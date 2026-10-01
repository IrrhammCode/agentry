"""
Autonomous Sentry Agent for Agentry.
Powered by Local LLM (Qwen 2.5 via Ollama) with TabPFN tabular signals.
Audits telemetry, explains anomalies, and executes autonomous interventions.
"""

import json
import logging
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional, List
import httpx

from agentry.config import settings
from agentry.telemetry import AgentStepTelemetry
from agentry.engine import TabPFNGuardrailEngine, StepRiskAssessment

logger = logging.getLogger("agentry.sentry")


@dataclass
class SentryDecision:
    """Actionable intervention decision by the Sentry Agent."""
    session_id: str
    step_index: int
    action: str  # KILL, PAUSE, REROUTE, PASS
    risk_level: str  # CRITICAL, HIGH, MEDIUM, NOMINAL
    confidence: float
    reason: str
    reroute_instruction: Optional[str]
    estimated_tokens_saved: int
    estimated_cost_saved_usd: float
    sentry_provider: str  # 'groq-llama-3.3-70b', 'ollama-qwen2.5:3b', or 'local-rule-engine'
    tabpfn_assessment: StepRiskAssessment


class GroqKeyRotator:
    """
    Round-robin API key pool with automatic failover across multiple Groq keys.
    Prevents rate limits (429) during heavy agent fleet monitoring.
    """

    def __init__(self, keys: List[str]):
        self.keys = [k.strip() for k in keys if k.strip()]
        self._index = 0

    def get_key(self) -> Optional[str]:
        if not self.keys:
            return None
        key = self.keys[self._index % len(self.keys)]
        self._index += 1
        return key


class AgentrySentry:
    """
    Autonomous Guardrail & Sentry Agent.
    Monitors live agent telemetry, queries TabPFN for tabular risk, and acts
    as an intelligent Sentry to prevent cost blowups and infinite loops.
    """

    def __init__(self, engine: Optional[TabPFNGuardrailEngine] = None):
        self.engine = engine or TabPFNGuardrailEngine()
        self.ollama_url = settings.ollama_base_url
        self.model = settings.sentry_model
        self.groq_rotator = GroqKeyRotator(settings.groq_api_keys)

        # Cache Ollama availability
        self._ollama_available: Optional[bool] = None
        self._last_ollama_check: float = 0.0

    def _check_ollama_alive(self) -> bool:
        """Fast probe to check if Ollama server and configured model are alive without blocking."""
        import time
        now = time.time()
        if self._ollama_available is not None and (now - self._last_ollama_check) < 15.0:
            return self._ollama_available

        self._last_ollama_check = now
        try:
            # Quick probe to check if model is installed
            base_url = self.ollama_url.replace("/v1", "")
            with httpx.Client(timeout=2.0) as client:
                res = client.get(f"{base_url}/api/tags")
                if res.status_code == 200:
                    models = [m.get("name", "") for m in res.json().get("models", [])]
                    # Check if requested model or base name is installed
                    self._ollama_available = any(self.model in m or m.startswith(self.model.split(":")[0]) for m in models)
                else:
                    self._ollama_available = False
        except Exception:
            self._ollama_available = False
        return self._ollama_available

    def audit_step(self, step: AgentStepTelemetry) -> SentryDecision:
        """
        Audit a single step of an agent in real-time.
        Evaluates tabular telemetry via TabPFN-3.5 and invokes Sentry brain for intervention.
        """
        assessment = self.engine.evaluate_step(step)
        risk_prob = assessment.failure_probability
        predicted_mode = assessment.predicted_failure_mode
        projected_cost = assessment.projected_final_cost_usd

        # Unified Economic Loss Formulation
        # Expected Loss = P(runaway) * expected_remaining_cost
        expected_remaining_cost = max(0.0, projected_cost - step.accumulated_cost_usd)
        expected_loss = risk_prob * expected_remaining_cost

        # Determine Sentry Action based on Economic Risk & Operational Evidence
        cost_runaway_critical = (
            step.accumulated_cost_usd >= settings.cost_threshold_kill_usd
            or (predicted_mode == "COST_RUNAWAY" and risk_prob >= 0.80 and step.accumulated_cost_usd >= 0.05 and step.error_streak >= 1)
        )
        loop_critical = (
            (predicted_mode == "INFINITE_LOOP" and risk_prob >= settings.risk_threshold_kill and step.error_streak >= 2)
            or (step.repetition_score >= settings.repetition_score_kill and step.error_streak >= 3)
            or step.error_streak >= settings.error_streak_kill
        )

        thought_lower = str(step.thought_trace or "").lower()
        tool_name_lower = str(step.tool_name or "").lower()
        is_hallucination = (
            predicted_mode == "TOOL_HALLUCINATION"
            or (step.error_streak >= 1 and ("unrecognized" in thought_lower or "not found" in thought_lower or "magic" in tool_name_lower))
        )

        # Autonomous KILL requires statistical certainty AND operational failure evidence
        # Never kill an agent with 0 errors and nominal spend (preserves task completion)
        if cost_runaway_critical or loop_critical or (risk_prob >= settings.risk_threshold_kill and step.error_streak >= 3):
            action = "KILL"
            risk_level = "CRITICAL"
        elif is_hallucination:
            action = "REROUTE"
            risk_level = "HIGH"
        elif step.repetition_score >= 0.65 and step.error_streak >= 1:
            action = "REROUTE"
            risk_level = "HIGH"
        elif risk_prob >= settings.risk_threshold_pause or (step.error_streak >= 2 and predicted_mode != "NORMAL"):
            if predicted_mode in ["TOOL_HALLUCINATION", "INFINITE_LOOP"] and step.error_streak <= 2:
                action = "REROUTE"
                risk_level = "HIGH"
            elif risk_prob >= settings.risk_threshold_kill and step.error_streak >= 2:
                action = "KILL"
                risk_level = "CRITICAL"
            else:
                action = "PAUSE"
                risk_level = "HIGH"
        elif risk_prob >= 0.35 or step.error_streak >= 1:
            action = "PASS"
            risk_level = "MEDIUM"
        else:
            action = "PASS"
            risk_level = "NOMINAL"

        # Calculate estimated savings if intervening
        if action in ["KILL", "PAUSE"]:
            remaining_steps = max(0, 15 - step.step_index)
            tokens_saved = remaining_steps * 1800
            cost_saved = round(max(0.0, projected_cost - step.accumulated_cost_usd), 4)
            if cost_saved <= 0:
                cost_saved = round((tokens_saved / 1000.0) * 0.002, 4)
        else:
            tokens_saved = 0
            cost_saved = 0.0

        # Generate intelligent reasoning using Ollama local LLM, or fallback to rule brain
        llm_explanation, reroute_inst, provider = self._generate_sentry_reasoning(step, assessment, action)

        return SentryDecision(
            session_id=step.session_id,
            step_index=step.step_index,
            action=action,
            risk_level=risk_level,
            confidence=round(max(risk_prob, 1.0 - risk_prob), 3),
            reason=llm_explanation,
            reroute_instruction=reroute_inst,
            estimated_tokens_saved=tokens_saved,
            estimated_cost_saved_usd=cost_saved,
            sentry_provider=provider,
            tabpfn_assessment=assessment,
        )

    def _generate_sentry_reasoning(
        self,
        step: AgentStepTelemetry,
        assessment: StepRiskAssessment,
        action: str
    ) -> Tuple[str, Optional[str], str]:
        """
        Generates Sentry forensic reasoning.
        Priority:
        1. Groq Cloud Engine (if keys provided and preferred/auto).
        2. Local Ollama SLM (Zero-leakage local privacy).
        3. Deterministic Sentry Brain Fallback.
        """
        provider_pref = settings.sentry_provider

        # Fast-path nominal steps: no external LLM query needed for safe/nominal executions
        if action == "PASS" and assessment.failure_probability < 0.5:
            return self._rule_based_sentry_brain(step, assessment, action)

        # 1. Groq Ultra-Fast Cloud Engine (with multi-key rotation)
        if provider_pref in ("groq", "auto") and self.groq_rotator.keys:
            groq_result = self._query_groq(step, assessment, action)
            if groq_result:
                return groq_result[0], groq_result[1], f"groq-{settings.groq_model}"

        # 2. Local Ollama SLM (Zero-leakage local privacy)
        if provider_pref in ("ollama", "auto") and self._check_ollama_alive():
            ollama_result = self._query_ollama(step, assessment, action)
            if ollama_result:
                return ollama_result[0], ollama_result[1], f"ollama-{self.model}"

        # 3. Deterministic Sentry Brain Fallback
        return self._rule_based_sentry_brain(step, assessment, action)

    def _query_groq(
        self,
        step: AgentStepTelemetry,
        assessment: StepRiskAssessment,
        action: str
    ) -> Optional[Tuple[str, Optional[str]]]:
        """Queries Groq API with automatic key rotation across available keys."""
        if not self.groq_rotator.keys:
            return None

        rep_val = round(step.repetition_score, 2)
        cost_val = round(step.accumulated_cost_usd, 4)
        prob_val = round(assessment.failure_probability * 100, 1)
        proj_val = round(assessment.projected_final_cost_usd, 4)

        prompt = f"""You are Agentry, an autonomous AI Sentry safeguarding an agent fleet.
A monitored agent '{step.agent_role}' running '{step.model_name}' produced telemetry:
- Step: {step.step_index}
- Tool: {step.tool_name}
- Error Streak: {step.error_streak}
- Repetition Score: {rep_val}
- Accumulated Cost: ${cost_val}
- Thought: "{step.thought_trace}"

TabPFN-3.5 Tabular Assessment:
- Failure Risk Probability: {prob_val}%
- Failure Mode: {assessment.predicted_failure_mode}
- Driver: {assessment.primary_risk_driver}
- Projected Cost: ${proj_val}

Recommended Action: {action}

Respond strictly in JSON with two keys:
"reason": "A 1-2 sentence concise forensic summary explaining the decision and TabPFN metrics",
"reroute_instruction": "A corrective directive for the agent if action is REROUTE, else null"
"""
        max_attempts = min(len(self.groq_rotator.keys) * 2, 8)
        for attempt in range(max_attempts):
            api_key = self.groq_rotator.get_key()
            if not api_key:
                break
            try:
                with httpx.Client(timeout=6.0) as client:
                    res = client.post(
                        f"{settings.groq_base_url}/chat/completions",
                        headers={
                            "Authorization": f"Bearer {api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": settings.groq_model,
                            "messages": [
                                {"role": "system", "content": "You are Agentry, an autonomous AI Sentry. Output valid JSON only."},
                                {"role": "user", "content": prompt}
                            ],
                            "response_format": {"type": "json_object"},
                            "temperature": 0.2,
                            "max_tokens": 350
                        }
                    )
                    if res.status_code == 200:
                        data = res.json()
                        content = data["choices"][0]["message"]["content"]
                        parsed = self._extract_json_response(content)
                        if parsed:
                            return parsed.get("reason", ""), parsed.get("reroute_instruction")
                    elif res.status_code in (429, 401):
                        masked = f"{api_key[:6]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
                        logger.warning("Groq key %s returned %d. Rotating key (attempt %d/%d)...",
                                       masked, res.status_code, attempt + 1, max_attempts)
                        continue
            except Exception as e:
                logger.debug("Groq query attempt %d failed: %s", attempt + 1, e)
                continue
        return None

    def _query_ollama(
        self,
        step: AgentStepTelemetry,
        assessment: StepRiskAssessment,
        action: str
    ) -> Optional[Tuple[str, Optional[str]]]:
        rep_val = round(step.repetition_score, 2)
        cost_val = round(step.accumulated_cost_usd, 4)
        prob_val = round(assessment.failure_probability * 100, 1)
        proj_val = round(assessment.projected_final_cost_usd, 4)

        try:
            prompt = f"""You are Agentry, an autonomous AI Sentry safeguarding an agent fleet.
A monitored agent '{step.agent_role}' running '{step.model_name}' produced telemetry:
- Step: {step.step_index}
- Tool: {step.tool_name}
- Error Streak: {step.error_streak}
- Repetition Score: {rep_val}
- Accumulated Cost: ${cost_val}
- Thought: "{step.thought_trace}"

TabPFN-3.5 Tabular Assessment:
- Failure Risk Probability: {prob_val}%
- Failure Mode: {assessment.predicted_failure_mode}
- Driver: {assessment.primary_risk_driver}
- Projected Cost: ${proj_val}

Recommended Action: {action}

Respond strictly in JSON with two keys:
"reason": "A 1-2 sentence concise forensic summary explaining the decision and TabPFN metrics",
"reroute_instruction": "A corrective directive for the agent if action is REROUTE, else null"
"""
            with httpx.Client(timeout=12.0) as client:
                res = client.post(
                    f"{self.ollama_url}/chat/completions",
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": "You are Agentry, an autonomous AI Sentry. Output valid JSON only."},
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.2,
                    }
                )
                if res.status_code == 200:
                    data = res.json()
                    content = data["choices"][0]["message"]["content"]
                    parsed = self._extract_json_response(content)
                    if parsed:
                        return parsed.get("reason", ""), parsed.get("reroute_instruction")
        except Exception:
            # Local Ollama not available or timed out
            pass
        return None

    @staticmethod
    def _extract_json_response(content: str) -> Optional[Dict[str, Any]]:
        """Robustly extracts JSON dictionary from LLM response text."""
        import re
        if not content:
            return None
        clean = content.strip()
        try:
            return json.loads(clean)
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}", clean)
            if match:
                try:
                    return json.loads(match.group(0))
                except json.JSONDecodeError:
                    pass
        return None

    def _rule_based_sentry_brain(
        self,
        step: AgentStepTelemetry,
        assessment: StepRiskAssessment,
        action: str
    ) -> Tuple[str, Optional[str], str]:
        """High-precision local rule engine ensuring instant, reliable evaluations."""
        mode = assessment.predicted_failure_mode
        prob = assessment.failure_probability
        driver = assessment.primary_risk_driver

        reroute = None
        if action == "KILL":
            if step.error_streak >= settings.error_streak_kill or step.repetition_score >= settings.repetition_score_kill:
                reason = (
                    f"Autonomous termination triggered. Repetitive failure loop detected (streak {step.error_streak}, "
                    f"repetition {step.repetition_score:.2f}). Terminating immediately to halt cost runaway."
                )
            elif step.accumulated_cost_usd >= settings.cost_threshold_kill_usd or (mode == "COST_RUNAWAY" and prob >= 0.70):
                reason = (
                    f"Autonomous termination triggered. Runaway token expenditure detected (${step.accumulated_cost_usd:.4f}). "
                    f"Terminating immediately to prevent further budget breach."
                )
            else:
                reason = (
                    f"Autonomous termination triggered. TabPFN detected {mode} with {prob:.1%} probability. "
                    f"Root cause: {driver}. Terminating immediately to halt cost runaway."
                )
        elif action == "REROUTE":
            reason = (
                f"Autonomous reroute engaged. TabPFN/Sentry flagged anomalous {mode} ({prob:.1%}). "
                f"Injecting corrective telemetry steering directive."
            )
            thought_low = str(step.thought_trace or "").lower()
            tool_low = str(step.tool_name or "").lower()
            if mode == "INFINITE_LOOP" or step.repetition_score >= 0.65:
                reroute = (
                    f"STOP RETRYING: You have repeated tool '{step.tool_name}' {step.error_streak} times. "
                    f"Read the error log carefully or switch strategies immediately."
                )
            elif mode == "TOOL_HALLUCINATION" or "not found" in thought_low or "unrecognized" in thought_low or "magic" in tool_low:
                reroute = (
                    f"INVALID TOOL: Tool '{step.tool_name}' does not exist in your environment. "
                    f"Use only available tools: [bash, read_file, write_file, grep_search]."
                )
            else:
                reroute = "CHECKPOINT: Summarize current findings and request user clarification before proceeding."
        elif action == "PAUSE":
            reason = (
                f"Agent execution paused for human inspection. TabPFN tabular risk elevated to {prob:.1%} "
                f"({driver}). Escalated to operator review."
            )
        else:
            reason = f"Telemetry nominal. TabPFN healthy confidence {1.0 - prob:.1%}. Agent authorized to proceed."

        return reason, reroute, "agentry-local-sentry"
