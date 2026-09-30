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


def test_groq_key_rotator():
    """Test 7-key round-robin rotation for Groq API keys."""
    from agentry.agent import GroqKeyRotator
    keys = [f"gsk_key_{i}" for i in range(1, 8)]
    rotator = GroqKeyRotator(keys)
    assert len(rotator.keys) == 7

    # Verify smooth round-robin cycling through all 7 keys
    sequence = [rotator.get_key() for _ in range(14)]
    assert sequence[:7] == keys
    assert sequence[7:14] == keys


@pytest.mark.anyio
async def test_guard_async_decorator():
    """Test @guard.protect on async coroutine tools."""
    guard = AgentryGuard(raise_on_kill=False)

    @guard.protect(session_id="async_session_01", tool_name="async_fetch")
    async def async_fetch_data(query: str) -> str:
        import asyncio
        await asyncio.sleep(0.01)
        return f"result for {query}"

    res = await async_fetch_data("AI safety papers")
    assert res == "result for AI safety papers"
    state = guard.get_or_create_session("async_session_01")
    assert state.step_index == 1
    assert state.tool_call_count == 1


def test_guard_multithreaded_concurrency():
    """Test thread-safety of AgentryGuard with concurrent worker threads."""
    import concurrent.futures
    guard = AgentryGuard(raise_on_kill=False)

    def worker(session_idx: int):
        sid = f"thread_sess_{session_idx}"
        for step in range(5):
            guard.audit(
                session_id=sid,
                tool_name="bash",
                input_text=f"step {step}",
                output_text="ok",
                prompt_tokens=500,
                completion_tokens=50
            )
        return guard.get_or_create_session(sid).step_index

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
        futures = [executor.submit(worker, i) for i in range(12)]
        results = [f.result() for f in futures]

    assert all(r == 5 for r in results)


def test_engine_robust_handling_unseen_and_nans():
    """Test that TabPFN Guardrail Engine handles NaNs and unseen categories defensively."""
    from agentry.engine import TabPFNGuardrailEngine
    from agentry.telemetry import AgentStepTelemetry, load_telemetry_data
    engine = TabPFNGuardrailEngine()
    engine.fit(load_telemetry_data())

    # Step with unknown roles, tools, and extreme values
    step = AgentStepTelemetry(
        session_id="wild_session_999",
        step_index=0,
        agent_role="BrandNewExoticRole",
        model_name="CompletelyNewLLM_v99",
        tool_name="QuantumDebugger",
        step_latency_ms=99999.0,
        prompt_tokens=0,
        completion_tokens=0,
        total_tokens=0,
        tool_call_count=0,
        error_streak=0,
        repetition_score=0.0,
        thought_length=0,
        accumulated_cost_usd=0.0,
        thought_trace="",
        failure_status="NORMAL",
        is_failure=0,
        final_cost_usd=0.0
    )

    assessment = engine.evaluate_step(step)
    assert assessment is not None
    assert 0.0 <= assessment.failure_probability <= 1.0
    assert assessment.predicted_failure_mode in ["NORMAL", "INFINITE_LOOP", "TOOL_HALLUCINATION", "COST_RUNAWAY"]
    assert assessment.projected_final_cost_usd >= 0.0

