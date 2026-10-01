"""
Zero-Code OpenAI-Compatible Reverse Proxy for Agentry.
Allows any autonomous AI agent (CrewAI, AutoGen, LangChain, OpenAI SDK)
to be governed in real-time simply by pointing base_url="http://localhost:8787/v1".
"""

import time
import json
import logging
from typing import Dict, Any, Optional, Tuple
import httpx

from agentry.guard import AgentryGuard, AgentHaltException, SentryDecision
from agentry.config import settings

logger = logging.getLogger("agentry.proxy")


class OpenAIProxyHandler:
    """
    Transparent proxy handler that intercepts /v1/chat/completions calls,
    records telemetry, queries TabPFN-3.5, and halts rogue agents.
    """

    def __init__(self, guard: Optional[AgentryGuard] = None, upstream_base_url: Optional[str] = None):
        self.guard = guard
        self.upstream_url = upstream_base_url or settings.groq_base_url

    def handle_chat_completion(
        self,
        request_body: Dict[str, Any],
        client_headers: Dict[str, str],
        guard: AgentryGuard
    ) -> Tuple[int, Dict[str, Any], Dict[str, str]]:
        """
        Handles a /v1/chat/completions request:
        1. Checks if session is already halted.
        2. Extracts input messages & prompt token estimates.
        3. Forwards request to upstream LLM (Groq, OpenAI, or Ollama).
        4. Audits completion with AgentryGuard.
        5. Returns response with X-Agentry governance headers, or circuit-breaker halt error.
        """
        # Extract or generate session_id from headers or request metadata
        session_id = (
            client_headers.get("x-session-id")
            or client_headers.get("x-agent-session")
            or request_body.get("user")
            or f"proxy_session_{hash(str(request_body.get('messages', []))) % 100000}"
        )

        state = guard.get_or_create_session(session_id)
        if state.is_halted:
            return 429, {
                "error": {
                    "message": f"AGENTRY SENTRY CIRCUIT BREAKER: Session '{session_id}' is permanently HALTED.",
                    "type": "circuit_breaker_kill",
                    "code": "SESSION_HALTED",
                    "reason": state.last_decision.reason if state.last_decision else "Runaway failure detected"
                }
            }, {"X-Agentry-Action": "KILL"}

        messages = request_body.get("messages", [])
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") in ("user", "system", "tool"):
                last_user_msg = str(m.get("content", ""))
                break

        # Forward request to upstream
        auth_header = client_headers.get("authorization", "")
        if not auth_header and settings.groq_api_keys:
            auth_header = f"Bearer {settings.groq_api_keys[0]}"

        upstream_target = f"{self.upstream_url}/chat/completions"
        headers_to_forward = {
            "Content-Type": "application/json",
            "Authorization": auth_header
        }

        t0 = time.time()
        try:
            with httpx.Client(timeout=45.0) as client:
                res = client.post(upstream_target, json=request_body, headers=headers_to_forward)
                latency_ms = (time.time() - t0) * 1000.0
                upstream_status = res.status_code
                response_data = res.json() if res.status_code == 200 else {}
        except Exception as exc:
            logger.error("Upstream proxy request failed: %s", exc)
            return 502, {"error": f"Upstream LLM gateway error: {str(exc)}"}, {"X-Agentry-Action": "ERROR"}

        if upstream_status != 200:
            return upstream_status, response_data, {}

        # Parse completion output & tokens
        choices = response_data.get("choices", [])
        completion_text = choices[0]["message"]["content"] if choices else ""
        usage = response_data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", len(str(messages)) // 4)
        completion_tokens = usage.get("completion_tokens", len(completion_text) // 4)
        tool_name = "llm_chat"

        # Check if tools were called
        first_choice = choices[0]["message"] if choices else {}
        if "tool_calls" in first_choice and first_choice["tool_calls"]:
            tool_name = first_choice["tool_calls"][0].get("function", {}).get("name", "tool")

        # Audit turn via TabPFN Sentry
        decision = guard.audit(
            session_id=session_id,
            tool_name=tool_name,
            input_text=last_user_msg[:200],
            output_text=completion_text[:200],
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            thought_trace=completion_text[:100],
            agent_role="Proxy-Agent",
            model_name=request_body.get("model", "unknown-model"),
            latency_ms=latency_ms
        )

        response_headers = {
            "X-Agentry-Action": decision.action,
            "X-Agentry-Risk-Level": decision.risk_level,
            "X-Agentry-Failure-Prob": f"{decision.tabpfn_assessment.failure_probability:.3f}",
            "X-Agentry-Failure-Mode": decision.tabpfn_assessment.predicted_failure_mode,
            "X-Agentry-Session-ID": session_id,
        }
        if decision.reroute_instruction:
            response_headers["X-Agentry-Reroute"] = decision.reroute_instruction

        # If KILL triggered, return circuit-breaker HTTP 429
        if decision.action == "KILL":
            return 429, {
                "error": {
                    "message": (
                        f"AGENTRY CIRCUIT BREAKER HALT: Agent '{session_id}' terminated at step {decision.step_index}.\n"
                        f"Reason: {decision.reason}\n"
                        f"Tokens Saved: ~{decision.estimated_tokens_saved:,} | Cost Saved: ~${decision.estimated_cost_saved_usd:.4f}"
                    ),
                    "type": "circuit_breaker_kill",
                    "code": "CIRCUIT_BREAKER_HALT",
                    "decision": {
                        "action": decision.action,
                        "risk_level": decision.risk_level,
                        "failure_probability": decision.tabpfn_assessment.failure_probability,
                        "predicted_failure_mode": decision.tabpfn_assessment.predicted_failure_mode,
                        "tokens_saved": decision.estimated_tokens_saved,
                        "cost_saved_usd": decision.estimated_cost_saved_usd
                    }
                }
            }, response_headers

        return 200, response_data, response_headers
