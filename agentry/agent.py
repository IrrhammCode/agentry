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
    sentry_provider: str  # 'ollama-qwen2.5:7b' or 'local-rule-engine'
    tabpfn_assessment: StepRiskAssessment


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

        # Determine Sentry Action
        cost_runaway_critical = (
            step.accumulated_cost_usd >= settings.cost_threshold_kill_usd
            or (predicted_mode == "COST_RUNAWAY" and risk_prob >= 0.75 and projected_cost >= settings.cost_threshold_warning_usd)
        )
        loop_critical = (
            (predicted_mode == "INFINITE_LOOP" and risk_prob >= settings.risk_threshold_kill and step.error_streak >= 3)
            or (step.repetition_score >= settings.repetition_score_kill and step.error_streak >= 3)
            or step.error_streak >= settings.error_streak_kill
        )

        if cost_runaway_critical or loop_critical or (risk_prob >= settings.risk_threshold_kill and step.error_streak >= 3):
            action = "KILL"
            risk_level = "CRITICAL"
        elif risk_prob >= settings.risk_threshold_pause or (step.error_streak >= 2 and predicted_mode != "NORMAL"):
            if predicted_mode in ["TOOL_HALLUCINATION", "INFINITE_LOOP"] and step.error_streak <= 2:
                action = "REROUTE"
                risk_level = "HIGH"
            elif risk_prob >= settings.risk_threshold_kill:
                action = "KILL"
                risk_level = "CRITICAL"
            else:
                action = "PAUSE"
                risk_level = "HIGH"
        elif risk_prob >= 0.35:
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
        """Queries local Ollama instance if alive, or uses deterministic sentry intelligence."""
        if self._check_ollama_alive():
            ollama_result = self._query_ollama(step, assessment, action)
            if ollama_result:
                return ollama_result[0], ollama_result[1], f"ollama-{self.model}"

        # Deterministic Sentry Brain
        return self._rule_based_sentry_brain(step, assessment, action)

    def _query_ollama(
        self,
        step: AgentStepTelemetry,
        assessment: StepRiskAssessment,
        action: str
    ) -> Optional[Tuple[str, Optional[str]]]:
        """Tries to query local Ollama LLM endpoint with a short timeout."""
        try:
            prompt = f"""You are Agentry, an autonomous AI Sentry safeguarding an agent fleet.
A monitored agent '{step.agent_role}' running '{step.model_name}' produced telemetry:
- Step: {step.step_index}
- Tool: {step.tool_name}
- Error Streak: {step.error_streak}
- Repetition Score: {step.repetition_score:.2f}
- Accumulated Cost: ${step.accumulated_cost_usd:.4f}
- Thought: "{step.thought_trace}"

TabPFN-3.5 Tabular Assessment:
- Failure Risk Probability: {assessment.failure_probability:.1%}
- Failure Mode: {assessment.predicted_failure_mode}
- Driver: {assessment.primary_risk_driver}
- Projected Cost: ${assessment.projected_final_cost_usd:.4f}

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
                    content = data["choices"][0]["message"]["content"].strip()
                    if content.startswith("```"):
                        content = content.split("```")[1]
                        if content.startswith("json"):
                            content = content[4:]
                    content = content.strip()
                    parsed = json.loads(content)
                    return parsed.get("reason", ""), parsed.get("reroute_instruction")
        except Exception:
            # Local Ollama not available or timed out
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
            reason = (
                f"Autonomous termination triggered. TabPFN detected {mode} with {prob:.1%} probability. "
                f"Root cause: {driver}. Terminating immediately to halt cost runaway."
            )
        elif action == "REROUTE":
            reason = (
                f"Autonomous reroute engaged. TabPFN flagged early-stage {mode} ({prob:.1%}). "
                f"Injecting corrective telemetry steering directive."
            )
            if mode == "INFINITE_LOOP":
                reroute = (
                    f"STOP RETRYING: You have repeated tool '{step.tool_name}' {step.error_streak} times. "
                    f"Read the error log carefully or switch strategies immediately."
                )
            elif mode == "TOOL_HALLUCINATION":
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
