"""
Agentry Guard: Drop-in SDK & Middleware for Autonomous AI Agents.
Provides decorators, context managers, and framework callbacks
for intercepting agent tool executions, detecting infinite loops,
and preventing runaway token costs via TabPFN-3.5 and Local SLM.
"""

import time
import re
import functools
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Callable, Union

from agentry.config import ROOT_DIR, settings
from agentry.telemetry import AgentStepTelemetry, load_telemetry_data
from agentry.engine import TabPFNGuardrailEngine
from agentry.agent import AgentrySentry, SentryDecision
from agentry.swe_telemetry import compute_string_overlap, is_error_output

logger = logging.getLogger("agentry.guard")


class AgentHaltException(Exception):
    """
    Exception raised when Agentry Sentry triggers a KILL intervention
    to halt an agent before catastrophic cost or loop runaway occurs.
    """

    def __init__(self, decision: SentryDecision):
        self.decision = decision
        self.message = (
            f"[AGENTRY SENTRY INTERVENTION: {decision.action}]\n"
            f"• Session: {decision.session_id} (Step {decision.step_index})\n"
            f"• Risk: {decision.risk_level} ({decision.tabpfn_assessment.failure_probability * 100:.1f}%)\n"
            f"• Mode: {decision.tabpfn_assessment.predicted_failure_mode}\n"
            f"• Reason: {decision.reason}\n"
            f"• Tokens Saved: ~{decision.estimated_tokens_saved:,} | Cost Saved: ~${decision.estimated_cost_saved_usd:.4f}"
        )
        super().__init__(self.message)


@dataclass
class SessionState:
    """Internal state tracked per monitored agent session."""
    session_id: str
    step_index: int = 0
    accumulated_prompt_tokens: int = 1500
    accumulated_comp_tokens: int = 0
    accumulated_cost_usd: float = 0.0
    error_streak: int = 0
    tool_call_count: int = 0
    recent_inputs: List[str] = field(default_factory=list)
    is_halted: bool = False
    last_decision: Optional[SentryDecision] = None


class StepContext:
    """Context manager for monitoring an agent turn or tool execution."""

    def __init__(
        self,
        guard: "AgentryGuard",
        session_id: str,
        tool_name: str,
        input_text: str = "",
        thought_trace: str = "",
        agent_role: str = "Autonomous-Agent",
        model_name: str = "swe-agent-70b"
    ):
        self.guard = guard
        self.session_id = session_id
        self.tool_name = tool_name
        self.input_text = input_text
        self.thought_trace = thought_trace
        self.agent_role = agent_role
        self.model_name = model_name
        self.start_time: float = 0.0
        self.output_text: str = ""
        self.prompt_tokens: int = 0
        self.completion_tokens: int = 0
        self.decision: Optional[SentryDecision] = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def record_output(self, output: Any):
        """Record the tool execution output or response string."""
        self.output_text = str(output)

    def record_tokens(self, prompt: int = 0, completion: int = 0):
        """Record exact token counts if returned by the LLM provider."""
        self.prompt_tokens = prompt
        self.completion_tokens = completion

    def __exit__(self, exc_type, exc_val, exc_tb):
        latency_ms = (time.time() - self.start_time) * 1000.0
        if exc_type is not None:
            # Exception occurred during execution
            err_msg = f"{exc_type.__name__}: {str(exc_val)}"
            self.output_text = err_msg if not self.output_text else f"{self.output_text}\n{err_msg}"

        self.decision = self.guard.audit(
            session_id=self.session_id,
            tool_name=self.tool_name,
            input_text=self.input_text,
            output_text=self.output_text,
            prompt_tokens=self.prompt_tokens,
            completion_tokens=self.completion_tokens,
            thought_trace=self.thought_trace,
            agent_role=self.agent_role,
            model_name=self.model_name,
            latency_ms=latency_ms
        )
        # If an unhandled exception occurred other than AgentHaltException, let it propagate
        return False


class AgentryGuard:
    """
    The Agentry Drop-in SDK & Guardrail Middleware.
    
    Usage Examples:
    
    1. Decorator:
        guard = AgentryGuard()
        
        @guard.protect(session_id="task_101", tool_name="bash")
        def run_bash(cmd: str):
            ...
            
    2. Context Manager:
        with guard.step(session_id="task_101", tool_name="python_repl") as m:
            res = execute_code(...)
            m.record_output(res)
            
    3. Direct Audit:
        decision = guard.audit(session_id="task_101", tool_name="bash", input_text="ls", output_text="...")
    """

    def __init__(
        self,
        engine: Optional[TabPFNGuardrailEngine] = None,
        sentry: Optional[AgentrySentry] = None,
        auto_fit: bool = True,
        raise_on_kill: bool = True,
        cost_per_1k_tokens: float = 0.002
    ):
        self.engine = engine or TabPFNGuardrailEngine()
        if auto_fit and not self.engine.is_fitted:
            real_csv = ROOT_DIR / "data" / "real_swe_telemetry.csv"
            training_data = load_telemetry_data(str(real_csv) if real_csv.exists() else None)
            self.engine.fit(training_data)

        self.sentry = sentry or AgentrySentry(self.engine)
        self.raise_on_kill = raise_on_kill
        self.cost_per_1k = cost_per_1k_tokens
        self._sessions: Dict[str, SessionState] = {}

    def get_or_create_session(self, session_id: str) -> SessionState:
        """Retrieves or creates tracked state for a session."""
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionState(session_id=session_id)
        return self._sessions[session_id]

    def reset_session(self, session_id: str):
        """Resets tracking for a specific session."""
        if session_id in self._sessions:
            del self._sessions[session_id]

    def step(
        self,
        session_id: str,
        tool_name: str,
        input_text: str = "",
        thought_trace: str = "",
        agent_role: str = "Autonomous-Agent",
        model_name: str = "swe-agent-70b"
    ) -> StepContext:
        """Context manager to monitor a single tool or execution step."""
        return StepContext(
            guard=self,
            session_id=session_id,
            tool_name=tool_name,
            input_text=input_text,
            thought_trace=thought_trace,
            agent_role=agent_role,
            model_name=model_name
        )

    def protect(
        self,
        session_id: Optional[str] = None,
        tool_name: Optional[str] = None,
        session_id_getter: Optional[Callable[..., str]] = None,
        thought_getter: Optional[Callable[..., str]] = None,
        agent_role: str = "Autonomous-Agent",
        model_name: str = "swe-agent-70b"
    ):
        """
        Python function/method decorator to monitor and guard tool executions.
        
        Example:
            @guard.protect(session_id="agent_1")
            def bash_tool(command: str) -> str:
                return run(command)
        """
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Resolve session_id
                resolved_session_id = session_id
                if session_id_getter is not None:
                    resolved_session_id = session_id_getter(*args, **kwargs)
                elif resolved_session_id is None:
                    resolved_session_id = getattr(args[0], "session_id", "default_session") if args else "default_session"

                # Resolve tool_name
                resolved_tool = tool_name or func.__name__

                # Resolve input snippet
                input_snippet = str(args) if args else str(kwargs)
                thought = thought_getter(*args, **kwargs) if thought_getter else ""

                t0 = time.time()
                error_occurred = False
                output_str = ""
                result = None

                try:
                    result = func(*args, **kwargs)
                    output_str = str(result)
                    return result
                except Exception as exc:
                    error_occurred = True
                    output_str = f"{type(exc).__name__}: {str(exc)}"
                    raise exc
                finally:
                    latency = (time.time() - t0) * 1000.0
                    self.audit(
                        session_id=resolved_session_id,
                        tool_name=resolved_tool,
                        input_text=input_snippet,
                        output_text=output_str,
                        thought_trace=thought,
                        agent_role=agent_role,
                        model_name=model_name,
                        latency_ms=latency
                    )
            return wrapper
        return decorator

    def audit(
        self,
        session_id: str,
        tool_name: str,
        input_text: str = "",
        output_text: str = "",
        prompt_tokens: int = 0,
        completion_tokens: int = 0,
        thought_trace: str = "",
        agent_role: str = "Autonomous-Agent",
        model_name: str = "swe-agent-70b",
        latency_ms: Optional[float] = None
    ) -> SentryDecision:
        """
        Audits a step in real-time, updates session telemetry,
        and triggers autonomous interventions if risk thresholds are breached.
        """
        state = self.get_or_create_session(session_id)
        if state.is_halted:
            logger.warning("Attempted execution on halted session: %s", session_id)
            if self.raise_on_kill and state.last_decision:
                raise AgentHaltException(state.last_decision)

        # 1. Update token metrics
        comp_est = completion_tokens if completion_tokens > 0 else max(30, len(output_text) // 4)
        prompt_est = prompt_tokens if prompt_tokens > 0 else max(100, len(input_text) // 6)

        state.accumulated_comp_tokens += comp_est
        state.accumulated_prompt_tokens += prompt_est
        total_tokens = state.accumulated_prompt_tokens + state.accumulated_comp_tokens
        state.accumulated_cost_usd = round((total_tokens / 1000.0) * self.cost_per_1k, 5)
        state.tool_call_count += 1

        # 2. Check for tool failure / errors
        if is_error_output(output_text):
            state.error_streak += 1
        else:
            state.error_streak = max(0, state.error_streak - 1)

        # 3. Compute repetition score against recent turns
        input_snippet = input_text.replace("\n", " ")[:150]
        if state.recent_inputs:
            repetition = max(compute_string_overlap(input_snippet, prev) for prev in state.recent_inputs[-4:])
        else:
            repetition = 0.05
        state.recent_inputs.append(input_snippet)

        # 4. Latency
        step_latency = latency_ms if latency_ms is not None else 850.0

        # 5. Assemble tabular telemetry
        telemetry = AgentStepTelemetry(
            session_id=session_id,
            step_index=state.step_index,
            agent_role=agent_role,
            model_name=model_name,
            tool_name=tool_name,
            step_latency_ms=round(step_latency, 1),
            prompt_tokens=state.accumulated_prompt_tokens,
            completion_tokens=state.accumulated_comp_tokens,
            total_tokens=total_tokens,
            tool_call_count=state.tool_call_count,
            error_streak=state.error_streak,
            repetition_score=round(repetition, 3),
            thought_length=len(thought_trace),
            accumulated_cost_usd=state.accumulated_cost_usd,
            thought_trace=thought_trace or input_snippet[:100],
            failure_status="NORMAL",
            is_failure=0,
            final_cost_usd=0.0
        )

        # 6. Audit via Sentry & TabPFN
        decision = self.sentry.audit_step(telemetry)
        state.last_decision = decision
        state.step_index += 1

        # 7. Execute Halt if required
        if decision.action == "KILL":
            state.is_halted = True
            logger.error("Agentry Sentry TRIGGERED KILL on session '%s' at step %d: %s", session_id, telemetry.step_index, decision.reason)
            if self.raise_on_kill:
                raise AgentHaltException(decision)

        return decision
