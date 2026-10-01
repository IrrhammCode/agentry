"""
Zero-Code OpenAI-Compatible Reverse Proxy for Agentry.
Allows any autonomous AI agent (CrewAI, AutoGen, LangChain, OpenAI SDK)
to be governed in real-time simply by pointing base_url="http://localhost:8787/v1".
"""

import time
import json
import logging
from typing import Dict, Any, Optional, Tuple, Iterator
import httpx

from agentry.guard import AgentryGuard, AgentHaltException, SentryDecision
from agentry.healing import trajectory_healer
from agentry.blast_radius import blast_radius_evaluator
from agentry.dlp import secret_redactor
from agentry.config import settings

logger = logging.getLogger("agentry.proxy")



class OpenAIProxyHandler:
    """
    Transparent proxy handler that intercepts /v1/chat/completions calls,
    records telemetry, queries TabPFN-3.5, and halts rogue agents.
    Supports both standard JSON requests and Server-Sent Events (SSE) streaming.
    """

    def __init__(self, guard: Optional[AgentryGuard] = None, upstream_base_url: Optional[str] = None):
        self.guard = guard
        self.upstream_url = upstream_base_url or settings.groq_base_url

    def _resolve_session_id(self, request_body: Dict[str, Any], client_headers: Dict[str, str]) -> str:
        return (
            client_headers.get("x-session-id")
            or client_headers.get("x-agent-session")
            or request_body.get("user")
            or f"proxy_session_{hash(str(request_body.get('messages', []))) % 100000}"
        )

    def _resolve_auth_header(self, client_headers: Dict[str, str]) -> str:
        auth_header = client_headers.get("authorization", "")
        if not auth_header and settings.groq_api_keys:
            auth_header = f"Bearer {settings.groq_api_keys[0]}"
        elif not auth_header and settings.openai_api_key:
            auth_header = f"Bearer {settings.openai_api_key}"
        return auth_header

    def handle_chat_completion(
        self,
        request_body: Dict[str, Any],
        client_headers: Dict[str, str],
        guard: Optional[AgentryGuard] = None
    ) -> Tuple[int, Dict[str, Any], Dict[str, str]]:
        """
        Handles a non-streaming /v1/chat/completions request:
        1. Checks if session is already halted.
        2. Extracts input messages & prompt token estimates.
        3. Forwards request to upstream LLM (Groq, OpenAI, or Ollama).
        4. Audits completion with AgentryGuard.
        5. Returns response with X-Agentry governance headers, or circuit-breaker halt error.
        """
        active_guard = guard or self.guard or AgentryGuard()
        session_id = self._resolve_session_id(request_body, client_headers)

        state = active_guard.get_or_create_session(session_id)
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
                last_user_msg = str(m.get("content") or "")
                break

        auth_header = self._resolve_auth_header(client_headers)
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

        # Parse completion output & tokens safely (handling tool calls where content is None)
        choices = response_data.get("choices", [])
        completion_msg = choices[0].get("message", {}) if (choices and isinstance(choices[0], dict)) else {}
        raw_content = completion_msg.get("content")
        completion_text = str(raw_content) if raw_content is not None else ""

        tool_name = "llm_chat"
        tool_calls = completion_msg.get("tool_calls", [])
        if tool_calls and isinstance(tool_calls, list):
            first_tool = tool_calls[0] if isinstance(tool_calls[0], dict) else {}
            func_info = first_tool.get("function", {}) if isinstance(first_tool, dict) else {}
            tool_name = str(func_info.get("name", "tool"))
            if not completion_text:
                args_snippet = str(func_info.get("arguments", ""))[:120]
                completion_text = f"call_{tool_name}({args_snippet})"

        usage = response_data.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens") if usage else None
        if prompt_tokens is None:
            prompt_tokens = max(100, len(str(messages)) // 4)

        completion_tokens = usage.get("completion_tokens") if usage else None
        if completion_tokens is None:
            completion_tokens = max(20, len(completion_text) // 4)

        # 1. Semantic Blast-Radius Interception on proposed tool call
        if tool_calls and isinstance(tool_calls, list):
            first_tool = tool_calls[0] if isinstance(tool_calls[0], dict) else {}
            func_info = first_tool.get("function", {}) if isinstance(first_tool, dict) else {}
            raw_args = str(func_info.get("arguments", ""))
            blast = blast_radius_evaluator.evaluate(tool_name, raw_args, session_id=session_id)
            if blast.is_critical:
                state.is_halted = True
                logger.critical(
                    "Proxy intercepted CRITICAL blast radius in tool call '%s' for session '%s': %s",
                    tool_name, session_id, blast.violation_reason
                )
                return 429, {
                    "error": {
                        "message": f"AGENTRY GATEWAY INTERCEPTION: Critical destructive blast radius blocked.\n{blast.violation_reason}",
                        "type": "circuit_breaker_kill",
                        "code": "CRITICAL_BLAST_RADIUS_BLOCKED",
                        "tool_name": tool_name,
                        "remediation": blast.remediation
                    }
                }, {
                    "X-Agentry-Action": "KILL",
                    "X-Agentry-Blast-Radius": "CRITICAL",
                    "X-Agentry-Session-ID": session_id
                }

        # 2. In-Flight DLP Secret Masking for completion and tool arguments
        masked_completion, secrets_count = secret_redactor.redact(completion_text)
        if secrets_count > 0:
            logger.info("Proxy DLP: Masked %d secret(s) in completion for session '%s'", secrets_count, session_id)
            if raw_content is not None:
                completion_msg["content"] = masked_completion

        # Audit turn via TabPFN Sentry
        decision = active_guard.audit(
            session_id=session_id,
            tool_name=tool_name,
            input_text=last_user_msg[:200],
            output_text=masked_completion[:200],
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            thought_trace=masked_completion[:100],
            agent_role="Proxy-Agent",
            model_name=str(request_body.get("model", "unknown-model")),
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

        # Closed-Loop Autonomic Self-Healing Rewind
        # If the agent is about to be terminated, attempt to prune poisoned context and heal transparently
        auto_rewind = (
            client_headers.get("x-agentry-auto-rewind", "true").lower() in ("true", "1", "yes")
            and bool(request_body.get("auto_rewind", True))
        )
        if decision.action == "KILL" and auto_rewind and getattr(state, "rewind_count", 0) < 2:
            try:
                prescription = trajectory_healer.diagnose_and_prescribe(
                    session_id=session_id,
                    current_step=decision.step_index,
                    failed_tool=tool_name,
                    error_streak=state.error_streak,
                    reason=decision.reason,
                    storage=active_guard.storage
                )
                pruned_msgs = trajectory_healer.prune_conversation(
                    messages=messages,
                    target_step=prescription.target_step,
                    directive=prescription.counterfactual_directive
                )
                retry_payload = dict(request_body)
                retry_payload["messages"] = pruned_msgs
                with httpx.Client(timeout=45.0) as retry_client:
                    retry_res = retry_client.post(upstream_target, json=retry_payload, headers=headers_to_forward)
                    if retry_res.status_code == 200:
                        state.is_halted = False
                        state.rewind_count = getattr(state, "rewind_count", 0) + 1
                        state.error_streak = 0
                        state.step_index = prescription.target_step + 1
                        healed_data = retry_res.json()
                        response_headers["X-Agentry-Action"] = "HEALED"
                        response_headers["X-Agentry-Auto-Healed"] = "true"
                        response_headers["X-Agentry-Rewound-Target"] = str(prescription.target_step)
                        response_headers["X-Agentry-Tokens-Saved"] = str(prescription.estimated_tokens_saved)
                        logger.info(
                            "Autonomous self-healing rewind succeeded for session '%s': pruned back to step %d",
                            session_id, prescription.target_step
                        )
                        return 200, healed_data, response_headers
            except Exception as heal_exc:
                logger.warning("Auto-rewind attempt failed: %s", heal_exc)

        # If KILL triggered and cannot be healed, return circuit-breaker HTTP 429
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

    def stream_chat_completion(
        self,
        request_body: Dict[str, Any],
        client_headers: Dict[str, str],
        guard: Optional[AgentryGuard] = None
    ) -> Iterator[bytes]:
        """
        Streams chat completion tokens from upstream LLM to client via SSE.
        Intercepts stream, tracks token generation & latency, and records audit telemetry.
        """
        active_guard = guard or self.guard or AgentryGuard()
        session_id = self._resolve_session_id(request_body, client_headers)
        state = active_guard.get_or_create_session(session_id)
        if state.is_halted:
            err_payload = {
                "error": {
                    "message": f"AGENTRY SENTRY CIRCUIT BREAKER: Session '{session_id}' is permanently HALTED.",
                    "type": "circuit_breaker_kill",
                    "code": "SESSION_HALTED"
                }
            }
            yield f"data: {json.dumps(err_payload)}\n\ndata: [DONE]\n\n".encode("utf-8")
            return

        messages = request_body.get("messages", [])
        last_user_msg = ""
        for m in reversed(messages):
            if m.get("role") in ("user", "system", "tool"):
                last_user_msg = str(m.get("content") or "")
                break

        auth_header = self._resolve_auth_header(client_headers)
        upstream_target = f"{self.upstream_url}/chat/completions"
        headers_to_forward = {
            "Content-Type": "application/json",
            "Authorization": auth_header
        }

        accumulated_text = []
        t0 = time.time()
        tool_name = "llm_chat"

        try:
            with httpx.Client(timeout=60.0) as client:
                with client.stream("POST", upstream_target, json=request_body, headers=headers_to_forward) as response:
                    if response.status_code != 200:
                        err_content = response.read()
                        yield err_content
                        return

                    for line in response.iter_lines():
                        if not line:
                            yield b"\n"
                            continue
                        yield f"{line}\n".encode("utf-8")
                        if line.startswith("data: ") and not "[DONE]" in line:
                            raw_chunk = line[6:].strip()
                            try:
                                chunk_json = json.loads(raw_chunk)
                                chs = chunk_json.get("choices", [])
                                if chs:
                                    delta = chs[0].get("delta", {})
                                    content_piece = delta.get("content")
                                    if content_piece:
                                        accumulated_text.append(content_piece)
                                    tool_calls = delta.get("tool_calls", [])
                                    if tool_calls:
                                        t_name = tool_calls[0].get("function", {}).get("name")
                                        if t_name:
                                            tool_name = str(t_name)
                            except Exception:
                                pass
        except Exception as exc:
            logger.error("Streaming proxy error: %s", exc)
            err_json = {"error": f"Upstream streaming error: {str(exc)}"}
            yield f"data: {json.dumps(err_json)}\n\ndata: [DONE]\n\n".encode("utf-8")
            return

        latency_ms = (time.time() - t0) * 1000.0
        full_completion = "".join(accumulated_text)
        prompt_tokens = max(100, len(str(messages)) // 4)
        comp_tokens = max(10, len(full_completion) // 4)

        try:
            active_guard.audit(
                session_id=session_id,
                tool_name=tool_name,
                input_text=last_user_msg[:200],
                output_text=full_completion[:200],
                prompt_tokens=prompt_tokens,
                completion_tokens=comp_tokens,
                thought_trace=full_completion[:100],
                agent_role="Proxy-Agent",
                model_name=str(request_body.get("model", "unknown-model")),
                latency_ms=latency_ms
            )
        except Exception as e:
            logger.debug("Failed recording streaming telemetry: %s", e)
