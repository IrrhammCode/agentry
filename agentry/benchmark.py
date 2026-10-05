"""
Benchmark Module for Agentry.
Evaluates TabPFN vs classical machine learning baselines (Random Forest, XGBoost, Logistic Regression, Rule-based)
on AI agent failure mode classification and cost runaway regression under strict Unseen Trajectory Group Splits.
"""

import time
import logging
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional
import numpy as np
import pandas as pd
from sklearn.model_selection import GroupShuffleSplit, train_test_split
from sklearn.metrics import (
    balanced_accuracy_score,
    f1_score,
    roc_auc_score,
    recall_score,
    precision_score,
    mean_absolute_error,
    mean_squared_error,
    r2_score,
)
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", module="sklearn")

try:
    import xgboost as xgb
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

from agentry.telemetry import load_telemetry_data
from agentry.engine import TabPFNGuardrailEngine

logger = logging.getLogger("agentry.benchmark")


@dataclass
class ModelBenchmarkResult:
    model_name: str
    sample_size: int
    test_sessions_count: int
    classification_balanced_acc: float
    classification_f1_macro: float
    classification_roc_auc: float
    failure_recall: float
    false_stop_rate: float  # False Positive Rate on normal steps (lower is better!)
    regression_mae_usd: float
    regression_rmse_usd: float
    regression_r2: float
    training_time_s: float
    inference_latency_ms: float


class HeuristicRuleBaseline:
    """
    Standard Engineering Heuristic Baseline (Circuit-Breaker):
    Halts if error_streak >= 3, repetition_score >= 0.75, or burn rate spikes.
    Illustrates why static if-else triggers suffer from high False-Stop rates.
    """

    def __init__(self, normal_idx: int, loop_idx: int, cost_idx: int):
        self.normal_idx = normal_idx
        self.loop_idx = loop_idx
        self.cost_idx = cost_idx

    def fit(self, X, y=None):
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        preds = np.full(len(X), self.normal_idx)
        # Rule triggers
        loop_trigger = (X["error_streak"] >= 3) | (X["repetition_score"] >= 0.75)
        cost_trigger = (X["accumulated_cost_usd"] >= 0.04) | (X["total_tokens"] >= 15000)

        preds[loop_trigger] = self.loop_idx
        preds[cost_trigger] = self.cost_idx
        return preds

    def predict_proba(self, X: pd.DataFrame, num_classes: int) -> np.ndarray:
        preds = self.predict(X)
        probs = np.full((len(X), num_classes), 0.05 / max(1, num_classes - 1))
        for i, p in enumerate(preds):
            probs[i, p] = 0.95
        return probs


class HeuristicCostRegressor:
    """Heuristic cost projection based on current cost + error accumulation."""

    def fit(self, X, y=None):
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        return X["accumulated_cost_usd"].values + (X["error_streak"].values * 0.005)


class GuardrailBenchmarkSuite:
    """
    Benchmark suite comparing TabPFN against standard baselines on agent telemetry
    under rigorous Unseen Trajectory Group Splits (Zero Step-Leakage).
    """

    def __init__(self, data_path: Optional[str] = None):
        self.df = load_telemetry_data(data_path)

    def run_benchmark(
        self,
        train_samples: int = 150,
        test_samples: int = 400,
        group_split: bool = True
    ) -> List[ModelBenchmarkResult]:
        """
        Runs benchmark comparison on agent telemetry.
        If group_split=True, uses GroupShuffleSplit by 'session_id' ensuring
        the test set contains 100% unseen agent trajectories (no data leakage).
        """
        engine = TabPFNGuardrailEngine()
        processed_df = engine._extract_tabular_features(self.df, fit=True)
        engine.mode_encoder.fit(self.df["failure_status"].astype(str))

        feature_cols = engine.FEATURE_COLS
        X = processed_df[feature_cols].copy()
        y_class = engine.mode_encoder.transform(self.df["failure_status"].astype(str))
        y_reg = self.df["final_cost_usd"].values
        num_classes = len(engine.mode_encoder.classes_)

        # Identify normal class index
        class_list = list(engine.mode_encoder.classes_)
        normal_idx = class_list.index("NORMAL") if "NORMAL" in class_list else 0
        loop_idx = class_list.index("INFINITE_LOOP") if "INFINITE_LOOP" in class_list else 1
        cost_idx = class_list.index("COST_RUNAWAY") if "COST_RUNAWAY" in class_list else 2

        test_sessions_count = 0
        if group_split and "session_id" in self.df.columns and self.df["session_id"].nunique() > 2:
            # Rigorous Group Split: Entire sessions partitioned into Train vs Test
            gss = GroupShuffleSplit(n_splits=1, test_size=0.30, random_state=42)
            train_idx, test_idx = next(gss.split(X, y_class, groups=self.df["session_id"]))
            X_train, X_test = X.iloc[train_idx], X.iloc[test_idx]
            y_train_cls, y_test_cls = y_class[train_idx], y_class[test_idx]
            y_train_reg, y_test_reg = y_reg[train_idx], y_reg[test_idx]
            test_sessions_count = int(self.df.iloc[test_idx]["session_id"].nunique())
        else:
            # Fallback stratified split if session_id is unavailable
            X_train, X_test, y_train_cls, y_test_cls, y_train_reg, y_test_reg = train_test_split(
                X, y_class, y_reg,
                train_size=min(train_samples, int(len(X) * 0.7)),
                test_size=min(test_samples, int(len(X) * 0.3)),
                stratify=y_class,
                random_state=42
            )
            test_sessions_count = 1

        results: List[ModelBenchmarkResult] = []

        # 1. Baseline 1: Heuristic Rule-Based Circuit Breaker (if-else static thresholds)
        rule_cls = HeuristicRuleBaseline(normal_idx, loop_idx, cost_idx)
        rule_reg = HeuristicCostRegressor()
        results.append(self._evaluate_model_pair(
            "Heuristic Rule Baseline",
            rule_cls, rule_reg,
            X_train, y_train_cls, y_train_reg,
            X_test, y_test_cls, y_test_reg,
            normal_idx=normal_idx,
            num_classes=num_classes,
            test_sessions_count=test_sessions_count,
            is_heuristic=True
        ))

        # 2. Classical Baseline 2: Logistic Regression & Ridge
        lr_cls = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000, random_state=42))
        ridge_reg = make_pipeline(StandardScaler(), Ridge(random_state=42))
        results.append(self._evaluate_model_pair(
            "Logistic Reg / Ridge",
            lr_cls, ridge_reg,
            X_train, y_train_cls, y_train_reg,
            X_test, y_test_cls, y_test_reg,
            normal_idx=normal_idx,
            num_classes=num_classes,
            test_sessions_count=test_sessions_count
        ))

        # 3. Classical Baseline 3: Random Forest (100 trees)
        rf_cls = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
        rf_reg = RandomForestRegressor(n_estimators=100, max_depth=8, random_state=42)
        results.append(self._evaluate_model_pair(
            "Random Forest (100 trees)",
            rf_cls, rf_reg,
            X_train, y_train_cls, y_train_reg,
            X_test, y_test_cls, y_test_reg,
            normal_idx=normal_idx,
            num_classes=num_classes,
            test_sessions_count=test_sessions_count
        ))

        # 4. Classical Baseline 4: XGBoost (Gradient Boosted Trees)
        if HAS_XGB:
            xgb_cls = xgb.XGBClassifier(
                n_estimators=100, max_depth=6, learning_rate=0.1,
                random_state=42, eval_metric="mlogloss"
            )
            xgb_reg = xgb.XGBRegressor(
                n_estimators=100, max_depth=6, learning_rate=0.1,
                random_state=42
            )
            results.append(self._evaluate_model_pair(
                "XGBoost (100 estimators)",
                xgb_cls, xgb_reg,
                X_train, y_train_cls, y_train_reg,
                X_test, y_test_cls, y_test_reg,
                normal_idx=normal_idx,
                num_classes=num_classes,
                test_sessions_count=test_sessions_count
            ))

        # 5. Agentry TabPFN Engine (Prior Labs Foundation Model)
        train_slice_df = self.df.iloc[X_train.index]
        t0 = time.time()
        engine.fit(train_slice_df)
        train_time = round(time.time() - t0, 3)
        tabpfn_name = "TabPFN-3.5 (Prior Labs)" if engine.is_cloud_tabpfn else "scikit-learn fallback (HistGradientBoosting), not TabPFN"

        t_inf0 = time.time()
        if engine.is_cloud_tabpfn:
            test_slice_df = self.df.iloc[X_test.index]
            X_test_input = test_slice_df[engine.RAW_TABPFN_COLS]
        else:
            X_test_input = X_test
        cls_probs = engine.classifier.predict_proba(X_test_input)
        cls_preds = np.argmax(cls_probs, axis=1)
        reg_preds = engine.regressor.predict(X_test_input)
        inf_latency = round(((time.time() - t_inf0) / len(X_test)) * 1000, 2)

        bal_acc = round(float(balanced_accuracy_score(y_test_cls, cls_preds)), 4)
        f1_mac = round(float(f1_score(y_test_cls, cls_preds, average="macro")), 4)
        try:
            auc = round(float(roc_auc_score(y_test_cls, cls_probs, multi_class="ovr")), 4)
        except Exception:
            auc = float('nan')

        mae = round(float(mean_absolute_error(y_test_reg, reg_preds)), 4)
        rmse = round(float(np.sqrt(mean_squared_error(y_test_reg, reg_preds))), 4)
        r2 = round(float(r2_score(y_test_reg, reg_preds)), 4)

        # False-Stop Rate (FPR on Normal productive steps)
        is_normal_gt = (y_test_cls == normal_idx)
        is_halt_pred = (cls_preds != normal_idx)
        false_stops = np.sum(is_normal_gt & is_halt_pred)
        total_normals = max(1, np.sum(is_normal_gt))
        false_stop_rate = round(float(false_stops / total_normals), 4)

        # Failure Recall (Detection rate of real loops/runaways)
        is_failure_gt = (y_test_cls != normal_idx)
        caught_failures = np.sum(is_failure_gt & is_halt_pred)
        total_failures = max(1, np.sum(is_failure_gt))
        fail_recall = round(float(caught_failures / total_failures), 4)

        results.append(ModelBenchmarkResult(
            model_name=tabpfn_name,
            sample_size=len(X_train),
            test_sessions_count=test_sessions_count,
            classification_balanced_acc=bal_acc,
            classification_f1_macro=f1_mac,
            classification_roc_auc=auc,
            failure_recall=fail_recall,
            false_stop_rate=false_stop_rate,
            regression_mae_usd=mae,
            regression_rmse_usd=rmse,
            regression_r2=r2,
            training_time_s=train_time,
            inference_latency_ms=inf_latency
        ))

        return results

    def _evaluate_model_pair(
        self,
        name: str,
        cls_model,
        reg_model,
        X_train, y_train_cls, y_train_reg,
        X_test, y_test_cls, y_test_reg,
        normal_idx: int = 0,
        num_classes: int = 4,
        test_sessions_count: int = 0,
        is_heuristic: bool = False
    ) -> ModelBenchmarkResult:
        t0 = time.time()
        cls_model.fit(X_train, y_train_cls)
        reg_model.fit(X_train, y_train_reg)
        train_time = round(time.time() - t0, 3)

        t_inf0 = time.time()
        cls_preds = cls_model.predict(X_test)
        reg_preds = reg_model.predict(X_test)
        inf_latency = round(((time.time() - t_inf0) / len(X_test)) * 1000, 2)

        bal_acc = round(float(balanced_accuracy_score(y_test_cls, cls_preds)), 4)
        f1_mac = round(float(f1_score(y_test_cls, cls_preds, average="macro", zero_division=0)), 4)

        try:
            if is_heuristic:
                cls_probs = cls_model.predict_proba(X_test, num_classes)
            else:
                cls_probs = cls_model.predict_proba(X_test)
            auc = round(float(roc_auc_score(y_test_cls, cls_probs, multi_class="ovr")), 4)
        except Exception:
            auc = float('nan')

        mae = round(float(mean_absolute_error(y_test_reg, reg_preds)), 4)
        rmse = round(float(np.sqrt(mean_squared_error(y_test_reg, reg_preds))), 4)
        r2 = round(float(r2_score(y_test_reg, reg_preds)), 4)

        # False-Stop Rate (FPR on Normal productive steps)
        is_normal_gt = (y_test_cls == normal_idx)
        is_halt_pred = (cls_preds != normal_idx)
        false_stops = np.sum(is_normal_gt & is_halt_pred)
        total_normals = max(1, np.sum(is_normal_gt))
        false_stop_rate = round(float(false_stops / total_normals), 4)

        # Failure Recall (Detection rate of real loops/runaways)
        is_failure_gt = (y_test_cls != normal_idx)
        caught_failures = np.sum(is_failure_gt & is_halt_pred)
        total_failures = max(1, np.sum(is_failure_gt))
        fail_recall = round(float(caught_failures / total_failures), 4)

        return ModelBenchmarkResult(
            model_name=name,
            sample_size=len(X_train),
            test_sessions_count=test_sessions_count,
            classification_balanced_acc=bal_acc,
            classification_f1_macro=f1_mac,
            classification_roc_auc=auc,
            failure_recall=fail_recall,
            false_stop_rate=false_stop_rate,
            regression_mae_usd=mae,
            regression_rmse_usd=rmse,
            regression_r2=r2,
            training_time_s=train_time,
            inference_latency_ms=inf_latency
        )


def format_benchmark_markdown(results: List[ModelBenchmarkResult]) -> str:
    """Formats benchmark results as a clean, publication-ready markdown table."""
    headers = [
        "Model Architecture",
        "Unseen Test Sessions",
        "Balanced Acc",
        "F1 Macro",
        "ROC-AUC",
        "Failure Recall",
        "False-Stop Rate (FPR)",
        "Cost MAE ($)",
        "Cost R²",
        "Inference Latency"
    ]
    rows = []
    for r in results:
        auc_str = "N/A" if np.isnan(r.classification_roc_auc) else f"{r.classification_roc_auc:.3f}"
        rows.append([
            f"**{r.model_name}**",
            f"{r.test_sessions_count} sessions",
            f"{r.classification_balanced_acc * 100:.1f}%",
            f"{r.classification_f1_macro * 100:.1f}%",
            auc_str,
            f"{r.failure_recall * 100:.1f}%",
            f"**{r.false_stop_rate * 100:.1f}%**" if r.false_stop_rate < 0.10 else f"{r.false_stop_rate * 100:.1f}%",
            f"${r.regression_mae_usd:.4f}",
            f"{r.regression_r2:.3f}",
            f"{r.inference_latency_ms:.2f} ms"
        ])

    table = "| " + " | ".join(headers) + " |\n"
    table += "| " + " | ".join(["---"] * len(headers)) + " |\n"
    for row in rows:
        table += "| " + " | ".join(row) + " |\n"
    return table
