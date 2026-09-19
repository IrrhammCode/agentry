"""
Tests for Agentry Drop-in SDK, Guardrails, and Middleware Integrations.
"""

import pytest
from agentry.guard import AgentryGuard, AgentHaltException, SessionState
from agentry.integrations import AgentryLangChainCallback, AgentryCrewHook


def test_guard_direct_audit():
    """Test direct programmatic auditing via AgentryGuard."""
    guard = AgentryGuard(raise_on_kill=False)
    
    # 1. Nominal step
    dec1 = guard.audit(
        session_id="test_direct_01",
        tool_name="read_file",
        input_text="view_file main.py",
        output_text="class MainApp: pass"
    )
    assert dec1.action == "PASS"
    assert dec1.risk_level in ["NOMINAL", "MEDIUM"]
    assert dec1.step_index == 0

    # 2. Progress step
    dec2 = guard.audit(
        session_id="test_direct_01",
        tool_name="bash",
        input_text="pytest tests/",
        output_text="1 passed in 0.5s"
    )
    assert dec2.step_index == 1
    assert dec2.action == "PASS"


def test_guard_decorator_nominal_and_kill():
    """Test @guard.protect decorator for tools and agent steps."""
    guard = AgentryGuard(raise_on_kill=True)

    @guard.protect(session_id="tool_session_01", tool_name="calculator")
    def add_numbers(a: int, b: int) -> int:
        return a + b

    # Nominal tool execution works seamlessly
    res = add_numbers(2, 3)
    assert res == 5
    state = guard.get_or_create_session("tool_session_01")
    assert state.step_index == 1

    # Now simulate an agent repeating an identical broken bash loop
    @guard.protect(session_id="loop_session_01", tool_name="bash")
    def run_broken_cmd(cmd: str) -> str:
        return "SyntaxError: unexpected EOF while parsing"

    # Run repeatedly until KILL intervention is raised
    with pytest.raises(AgentHaltException) as exc_info:
        for _ in range(6):
            run_broken_cmd("python -c 'def broken('")

    assert "AGENTRY SENTRY INTERVENTION: KILL" in str(exc_info.value)
    halt_state = guard.get_or_create_session("loop_session_01")
    assert halt_state.is_halted is True


def test_guard_context_manager():
    """Test 'with guard.step(...)' context manager."""
    guard = AgentryGuard(raise_on_kill=False)

    with guard.step(session_id="ctx_session_01", tool_name="git_clone") as m:
        # Simulate work
        output = "Cloning into 'repo'..."
        m.record_output(output)
        m.record_tokens(prompt=2000, completion=150)

    assert m.decision is not None
    assert m.decision.action == "PASS"
    assert m.decision.step_index == 0


def test_langchain_callback_integration():
    """Test LangChain / LangGraph callback handler."""
    guard = AgentryGuard(raise_on_kill=False)
    cb = AgentryLangChainCallback(session_id="lc_session_01", guard=guard)

    # Tool invocation sequence
    cb.on_tool_start({"name": "web_search"}, "latest AI news 2026")
    cb.on_tool_end("Found 5 articles on AI safety")

    state = guard.get_or_create_session("lc_session_01")
    assert state.step_index == 1
    assert state.tool_call_count == 1


def test_crewai_hook_integration():
    """Test CrewAI step hook integration."""
    guard = AgentryGuard(raise_on_kill=False)
    hook = AgentryCrewHook(session_id="crew_session_01", guard=guard)

    class MockStepOutput:
        tool = "code_interpreter"
        tool_input = "print(1 + 1)"
        thought = "Calculating answer"
        def __str__(self):
            return "2"

    decision = hook(MockStepOutput())
    assert decision is not None
    assert decision.action == "PASS"
    assert decision.step_index == 0
