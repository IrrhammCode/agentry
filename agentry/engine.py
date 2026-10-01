"""
TabPFN Guardrail Engine for Agentry.
Provides real-time failure classification and runaway cost regression using TabPFN-3.5.
Supports Thinking Mode, temporal grouping, and graceful fallback for offline evaluation.
"""

import os
import logging
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor
from sklearn.preprocessing import LabelEncoder

from agentry.config import settings
from agentry.telemetry import AgentStepTelemetry

logger = logging.getLogger("agentry.engine")


@dataclass
class StepRiskAssessment:
    """Risk and anomaly assessment produced by the TabPFN Guardrail Engine."""
    session_id: str
    step_index: int
    failure_probability: float
    predicted_failure_mode: str
    mode_probabilities: Dict[str, float]
    uncertainty_score: float
    projected_final_cost_usd: float
    primary_risk_driver: str
    is_cloud_tabpfn: bool


class TabPFNGuardrailEngine:
    """
    Core Tabular Foundation Model Guardrail Engine.
    Uses TabPFN-3.5 (via tabpfn-client) with group and time column awareness,
    with an offline ensemble fallback when API token is not yet configured.
    """

    FEATURE_COLS = [
        "step_latency_ms",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "tool_call_count",
        "error_streak",
        "repetition_score",
        "thought_length",
        "accumulated_cost_usd",
        "agent_role_cat",
        "tool_name_cat",
        "model_name_cat",
        "thought_has_retry",
        "thought_has_error",
        "thought_has_spill",
    ]

    # Raw multimodal columns passed to TabPFN-3.5 Cloud Foundation Model
    RAW_TABPFN_COLS = [
        "session_id",
        "step_index",
        "agent_role",
        "tool_name",
        "model_name",
        "step_latency_ms",
        "prompt_tokens",
        "completion_tokens",
        "total_tokens",
        "tool_call_count",
        "error_streak",
        "repetition_score",
        "thought_length",
        "accumulated_cost_usd",
        "thought_trace",
    ]

    def __init__(self, token: Optional[str] = None, use_thinking: Optional[bool] = None):
        self.token = token or settings.tabpfn_token
        self.use_thinking = use_thinking if use_thinking is not None else settings.tabpfn_use_thinking
        self.is_cloud_tabpfn = False
        self.classifier = None
        self.regressor = None
        self.role_encoder = LabelEncoder()
        self.tool_encoder = LabelEncoder()
        self.model_encoder = LabelEncoder()
        self.mode_encoder = LabelEncoder()
        self.is_fitted = False

        self._local_classifier = None
        self._local_regressor = None
        # Attempt to initialize TabPFN client
        self._init_tabpfn_client()

    def _init_tabpfn_client(self):
        """Attempts to connect to Prior Labs TabPFN-3.5 cloud API."""
        if not self.token or os.getenv("TABPFN_OFFLINE_MODE", "").lower() in ("1", "true", "yes"):
            logger.info("No TABPFN_TOKEN found or TABPFN_OFFLINE_MODE active. Engine will run in Local Emulated Fallback Mode.")
            return

        try:
            import tabpfn_client
            tabpfn_client.set_access_token(self.token)
            
            # Initialize TabPFN 3.5 Classifier & Regressor with Thinking Mode
            # Grouped temporal series in TabPFN-3.5 requires group_col + group_time_col
            self.classifier = tabpfn_client.TabPFNClassifier(
                thinking_mode=self.use_thinking,
                group_col="session_id",
                group_time_col="step_index",
                n_estimators=settings.tabpfn_n_estimators
            )
            self.regressor = tabpfn_client.TabPFNRegressor(
                thinking_mode=self.use_thinking,
                group_col="session_id",
                group_time_col="step_index",
                n_estimators=settings.tabpfn_n_estimators
            )
            self.is_cloud_tabpfn = True
            logger.info("Successfully initialized official TabPFN-3.5 Cloud Engine (Thinking Mode=%s)", self.use_thinking)
        except Exception as exc:
            logger.warning("Failed to initialize TabPFN Cloud Client: %s. Using local fallback.", exc)
            self.is_cloud_tabpfn = False

    def _extract_tabular_features(self, df: pd.DataFrame, fit: bool = False) -> pd.DataFrame:
        """Extracts engineered numerical & categorical features from telemetry rows."""
        processed = df.copy()

        # Fill NaNs defensively
        for col in ["agent_role", "tool_name", "model_name"]:
            if col in processed.columns:
                processed[col] = processed[col].fillna("unknown").astype(str)
            else:
                processed[col] = "unknown"

        for num_col in [
            "step_latency_ms", "prompt_tokens", "completion_tokens", "total_tokens",
            "tool_call_count", "error_streak", "repetition_score", "thought_length",
            "accumulated_cost_usd"
        ]:
            if num_col in processed.columns:
                processed[num_col] = pd.to_numeric(processed[num_col], errors="coerce").fillna(0.0)
            else:
                processed[num_col] = 0.0

        # Categorical encoding
        if fit:
            processed["agent_role_cat"] = self.role_encoder.fit_transform(processed["agent_role"])
            processed["tool_name_cat"] = self.tool_encoder.fit_transform(processed["tool_name"])
            processed["model_name_cat"] = self.model_encoder.fit_transform(processed["model_name"])
        else:
            # Handle unknown categories safely
            processed["agent_role_cat"] = processed["agent_role"].map(
                lambda s: self.role_encoder.transform([s])[0] if s in self.role_encoder.classes_ else 0
            )
            processed["tool_name_cat"] = processed["tool_name"].map(
                lambda s: self.tool_encoder.transform([s])[0] if s in self.tool_encoder.classes_ else 0
            )
            processed["model_name_cat"] = processed["model_name"].map(
                lambda s: self.model_encoder.transform([s])[0] if s in self.model_encoder.classes_ else 0
            )

        # NLP keyword telemetry signals
        thoughts = processed["thought_trace"].fillna("").astype(str).str.lower()
        processed["thought_has_retry"] = thoughts.apply(lambda t: 1 if any(k in t for k in ["retry", "re-run", "again", "failed"]) else 0)
        processed["thought_has_error"] = thoughts.apply(lambda t: 1 if any(k in t for k in ["error", "not found", "exit code", "unrecognized"]) else 0)
        processed["thought_has_spill"] = thoughts.apply(lambda t: 1 if any(k in t for k in ["context window", "spiking", "dump", "site-packages"]) else 0)

        return processed

    def fit(self, training_df: pd.DataFrame):
        """Fit the TabPFN engine and pre-warm offline fallback on historical agent telemetry."""
        # Preprocess features
        processed_df = self._extract_tabular_features(training_df, fit=True)
        self.mode_encoder.fit(training_df["failure_status"].fillna("NORMAL").astype(str))

        X = processed_df[self.FEATURE_COLS]
        y_class = self.mode_encoder.transform(training_df["failure_status"].fillna("NORMAL").astype(str))
        y_reg = pd.to_numeric(training_df["final_cost_usd"], errors="coerce").fillna(0.0).values

        # Pre-warm local fallback models (always available as instant, zero-latency safety net)
        self._local_classifier = HistGradientBoostingClassifier(random_state=42, max_iter=150)
        self._local_classifier.fit(X, y_class)

        self._local_regressor = HistGradientBoostingRegressor(random_state=42, max_iter=150)
        self._local_regressor.fit(X, y_reg)
        self.is_fitted = True

        if self.is_cloud_tabpfn:
            try:
                # TabPFN accepts raw multimodal DataFrame with group_col, group_time_col, and raw text
                X_tabpfn = training_df[self.RAW_TABPFN_COLS].copy()
                self.classifier.fit(X_tabpfn, y_class)
                self.regressor.fit(X_tabpfn, y_reg)
                logger.info("TabPFN-3.5 Cloud Engine fitted successfully on %d telemetry steps.", len(X_tabpfn))
                return
            except Exception as e:
                logger.warning("TabPFN Cloud fit error: %s. Falling back to local offline model.", e)
                self.is_cloud_tabpfn = False

        self.classifier = self._local_classifier
        self.regressor = self._local_regressor
        logger.info("Agentry Local Fallback Engine fitted on %d telemetry steps.", len(X))

    def evaluate_step(self, step: AgentStepTelemetry) -> StepRiskAssessment:
        """Evaluates telemetry from a single agent step and returns a StepRiskAssessment."""
        if not self.is_fitted:
            raise RuntimeError("TabPFNGuardrailEngine must be fitted before evaluating steps.")

        # Convert step to DataFrame
        row_dict = {
            "session_id": str(step.session_id or "default_session"),
            "step_index": int(step.step_index or 0),
            "agent_role": str(step.agent_role or "Agent"),
            "model_name": str(step.model_name or "default-model"),
            "tool_name": str(step.tool_name or "tool"),
            "step_latency_ms": max(0.0, float(step.step_latency_ms or 0.0)),
            "prompt_tokens": max(0, int(step.prompt_tokens or 0)),
            "completion_tokens": max(0, int(step.completion_tokens or 0)),
            "total_tokens": max(0, int(step.total_tokens or 0)),
            "tool_call_count": max(0, int(step.tool_call_count or 0)),
            "error_streak": max(0, int(step.error_streak or 0)),
            "repetition_score": min(1.0, max(0.0, float(step.repetition_score or 0.0))),
            "thought_length": max(0, int(step.thought_length or 0)),
            "accumulated_cost_usd": max(0.0, float(step.accumulated_cost_usd or 0.0)),
            "thought_trace": str(step.thought_trace or ""),
        }
        df_step = pd.DataFrame([row_dict])
        processed_step = self._extract_tabular_features(df_step, fit=False)

        # Probabilities & Prediction with automatic fallback on cloud failure
        probs = None
        pred_cost = None
        if self.is_cloud_tabpfn and self.classifier is not None and self.regressor is not None:
            try:
                X_cloud = df_step[self.RAW_TABPFN_COLS]
                probs = self.classifier.predict_proba(X_cloud)[0]
                pred_cost = float(self.regressor.predict(X_cloud)[0])
            except Exception as exc:
                logger.warning("TabPFN Cloud inference failure (%s). Switching to pre-warmed local model.", exc)
                self.is_cloud_tabpfn = False
                self.classifier = self._local_classifier
                self.regressor = self._local_regressor

        if probs is None or pred_cost is None:
            X_local = processed_step[self.FEATURE_COLS]
            probs = self.classifier.predict_proba(X_local)[0]
            pred_cost = float(self.regressor.predict(X_local)[0])

        classes = self.mode_encoder.classes_
        model_classes = getattr(self.classifier, "classes_", list(range(len(probs))))
        cls_map = {int(c_idx): float(p) for c_idx, p in zip(model_classes, probs)}

        mode_probs = {}
        for i, cls_name in enumerate(classes):
            mode_probs[cls_name] = float(round(cls_map.get(i, 0.0), 4))

        # Failure probability (sum of all non-NORMAL classes)
        normal_idx = list(classes).index("NORMAL") if "NORMAL" in classes else -1
        if normal_idx != -1:
            normal_p = cls_map.get(normal_idx, 0.0)
            failure_prob = round(float(np.clip(1.0 - normal_p, 0.0, 1.0)), 4)
        else:
            failure_prob = round(float(np.max(probs)), 4)

        pred_class_idx = int(model_classes[np.argmax(probs)])
        predicted_mode = str(classes[pred_class_idx]) if pred_class_idx < len(classes) else "NORMAL"

        # Prediction uncertainty (normalized Shannon entropy)
        entropy = -np.sum(probs * np.log(np.maximum(probs, 1e-12)))
        max_entropy = np.log(max(2, len(classes)))
        normalized_uncertainty = round(float(np.clip(entropy / max_entropy, 0.0, 1.0)), 3)

        # Regress final projected cost
        projected_cost = round(max(max(0.0, step.accumulated_cost_usd), pred_cost), 4)

        # Identify primary risk driver
        risk_driver = self._determine_primary_risk_driver(step, failure_prob, predicted_mode)

        return StepRiskAssessment(
            session_id=step.session_id,
            step_index=step.step_index,
            failure_probability=failure_prob,
            predicted_failure_mode=predicted_mode,
            mode_probabilities=mode_probs,
            uncertainty_score=normalized_uncertainty,
            projected_final_cost_usd=projected_cost,
            primary_risk_driver=risk_driver,
            is_cloud_tabpfn=self.is_cloud_tabpfn
        )

    def _determine_primary_risk_driver(self, step: AgentStepTelemetry, failure_prob: float, mode: str) -> str:
        """Explains the tabular root cause of the risk score."""
        if failure_prob < settings.risk_threshold_pause:
            return "Nominal operational parameters."

        drivers = []
        if step.repetition_score >= 0.70:
            drivers.append(f"High repetition score ({step.repetition_score:.2f})")
        if step.error_streak >= 3:
            drivers.append(f"Unbroken error streak ({step.error_streak} consecutive errors)")
        if step.step_latency_ms > 4000:
            drivers.append(f"High step latency ({step.step_latency_ms:.0f}ms)")
        if step.accumulated_cost_usd > settings.cost_threshold_warning_usd:
            drivers.append(f"High token cost burn (${step.accumulated_cost_usd:.4f})")
        if "retry" in step.thought_trace.lower() or "again" in step.thought_trace.lower():
            drivers.append("Thought trace indicates repetitive retries")
        if "not found" in step.thought_trace.lower() or "unrecognized" in step.thought_trace.lower():
            drivers.append("Thought trace indicates hallucinated tool/flag")

        if not drivers:
            drivers.append(f"Multivariate tabular anomaly detected ({mode})")

        return "; ".join(drivers)
