"""
Deep resilience, fuzzing, and adversarial edge-case test suite for Agentry.
Tests system behavior under extreme conditions:
- NaN, Inf, None inputs across TabPFN engine evaluation
- Corrupted, missing, and non-dict message histories in autonomic rewind
- Multi-step spend aggregation accuracy and zero-division defenses in budget governor
- MCP new tools (agentry_prescribe_rewind, agentry_check_budget) & fleet://budget resource
- Guard halted session fast-path return without re-auditing
- Concurrency stress and thread safety
"""

import math
import time
import json
import pytest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor

from agentry.telemetry import AgentStepTelemetry, load_telemetry_data
from agentry.engine import TabPFNGuardrailEngine
from agentry.guard import AgentryGuard, AgentHaltException, _safe_int, _safe_float
from agentry.healing import TrajectoryHealer, RewindPrescription
from agentry.budget import FleetBudgetGovernor, BudgetStatus
from agentry.storage import AuditStorage
from agentry.mcp_server import (
    prescribe_trajectory_rewind,
    check_fleet_and_session_budget,
    fleet_budget_resource,
    get_fleet_status,
)


@pytest.fixture(scope="module")
def shared_engine():
    engine = TabPFNGuardrailEngine()
    data = load_telemetry_data()
    engine.fit(data)
    return engine


@pytest.fixture
def temp_storage(tmp_path):
    db_file = tmp_path / "deep_audit.db"
    return AuditStorage(db_file)


# ============================================================================
# 1. Engine NaN, Inf, and Type Chaos Resilience
# ============================================================================

def test_engine_nan_inf_adversarial_telemetry(shared_engine):
    """Verifies evaluate_step handles NaNs, Infs, and strings without crashing."""
    step = AgentStepTelemetry(
        session_id="chaos_session_nan",
        step_index=float("nan"),  # type: ignore
        agent_role=None,  # type: ignore
        model_name=None,  # type: ignore
        tool_name=None,  # type: ignore
        step_latency_ms=float("inf"),
        prompt_tokens=float("nan"),  # type: ignore
        completion_tokens=float("-inf"),  # type: ignore
        total_tokens=float("nan"),  # type: ignore
        tool_call_count=float("nan"),  # type: ignore
        error_streak=float("nan"),  # type: ignore
        repetition_score=float("nan"),
        thought_length=float("nan"),  # type: ignore
        accumulated_cost_usd=float("inf"),
        thought_trace=None,  # type: ignore
        failure_status="NORMAL",
        is_failure=0,
        final_cost_usd=0.0,
        remaining_cost_usd=0.0,
    )

    assessment = shared_engine.evaluate_step(step)
    assert assessment is not None
    assert 0.0 <= assessment.failure_probability <= 1.0
    assert assessment.predicted_failure_mode in shared_engine.mode_encoder.classes_
    assert assessment.session_id == "chaos_session_nan"
    assert assessment.step_index == 0


def test_engine_extreme_numeric_bounds(shared_engine):
    """Verifies evaluate_step clamps negative and extreme values safely."""
    step = AgentStepTelemetry(
        session_id="extreme_bounds",
        step_index=-50,
        agent_role="TestAgent",
        model_name="TestModel",
        tool_name="bash",
        step_latency_ms=-100.0,
        prompt_tokens=-999,
        completion_tokens=-50,
        total_tokens=-1049,
        tool_call_count=-1,
        error_streak=-3,
        repetition_score=9999.0,  # Should be clamped to 1.0
        thought_length=-10,
        accumulated_cost_usd=-5.0,
        thought_trace="Extreme test",
        failure_status="NORMAL",
        is_failure=0,
        final_cost_usd=0.0,
        remaining_cost_usd=0.0,
    )
    assessment = shared_engine.evaluate_step(step)
    assert assessment.failure_probability >= 0.0
    assert assessment.projected_final_cost_usd >= 0.0


# ============================================================================
# 2. Autonomic Trajectory Rewind & Healing Edge Cases
# ============================================================================

def test_healing_adversarial_events_and_none_fields(temp_storage):
    """Verifies TrajectoryHealer handles corrupted event dictionaries."""
    healer = TrajectoryHealer(temp_storage)

    # Empty list
    assert healer.find_inflection_point([]) == 0

    # Events with None fields and non-dict entries
    corrupted_events = [
        "not_a_dict",
        None,
        {"step_index": None, "failure_probability": None, "action": None},
        {"step_index": "2", "failure_probability": "0.15", "action": "PASS"},
        {"step_index": 3, "failure_probability": 0.85, "action": "KILL"},
    ]
    inflection = healer.find_inflection_point(corrupted_events)  # type: ignore
    assert inflection == 2

    # All failing events fallback to max(0, current_step - 3)
    all_failing = [
        {"step_index": 5, "failure_probability": 0.90, "action": "KILL"},
        {"step_index": 6, "failure_probability": 0.95, "action": "KILL"},
    ]
    inflection_fallback = healer.find_inflection_point(all_failing)
    assert inflection_fallback == max(0, 6 - 3)


def test_healing_diagnose_and_prescribe_boundary(temp_storage):
    """Verifies diagnose_and_prescribe when target_step is bounded."""
    healer = TrajectoryHealer(temp_storage)
    prescription = healer.diagnose_and_prescribe(
        session_id="unseen_session_boundary",
        current_step=0,  # Step 0 failure
        failed_tool="rm_rf",
        error_streak=1,
    )
    assert prescription.session_id == "unseen_session_boundary"
    assert prescription.current_step == 0
    assert prescription.target_step == 0
    assert prescription.pruned_steps_count >= 1
    assert "DO NOT repeat 'rm_rf'" in prescription.counterfactual_directive


def test_healing_prune_conversation_chaos():
    """Verifies prune_conversation with non-dict items and edge target steps."""
    # 1. Non-dict elements
    corrupted_messages = ["string_msg", None, {"role": "system", "content": "System directive"}, {"role": "user", "content": "Initial prompt"}]
    pruned = TrajectoryHealer.prune_conversation(corrupted_messages, target_step=0)  # type: ignore
    assert len(pruned) >= 2
    assert pruned[0]["role"] == "system"

    # 2. Target step 0 preserves system and initial turn
    messages = [
        {"role": "system", "content": "You are a coding assistant."},
        {"role": "user", "content": "Fix bug in app.py"},
        {"role": "assistant", "content": "Let me run bash."},
        {"role": "tool", "content": "SyntaxError"},
        {"role": "assistant", "content": "Let me retry bash."},
        {"role": "tool", "content": "SyntaxError"},
    ]
    pruned_step_0 = TrajectoryHealer.prune_conversation(
        messages,
        target_step=0,
        directive="SYSTEM: Do not use bash again."
    )
    assert pruned_step_0[0]["content"] == "You are a coding assistant."
    assert pruned_step_0[-1]["content"] == "SYSTEM: Do not use bash again."
    assert len(pruned_step_0) < len(messages)


# ============================================================================
# 3. Fleet Budget Autopilot Multi-Session Aggregation & Robustness
# ============================================================================

def test_budget_governor_grouped_session_spend_aggregation(temp_storage, shared_engine):
    """
    Verifies that multi-step sessions sum MAX projected cost per session,
    not naively summing every step.
    """
    guard = AgentryGuard(engine=shared_engine, storage=temp_storage, raise_on_kill=False)
    governor = FleetBudgetGovernor(daily_budget_usd=10.0, storage=temp_storage)

    # Record 5 steps for session_A (projected cost ~$0.05 each)
    for i in range(5):
        guard.audit(session_id="session_A", tool_name="bash", input_text=f"cmd_{i}", output_text="ok")

    # Record 5 steps for session_B (projected cost ~$0.05 each)
    for i in range(5):
        guard.audit(session_id="session_B", tool_name="bash", input_text=f"cmd_{i}", output_text="ok")

    status = governor.check_fleet_budget()
    assert not status.is_exceeded
    # Spend should be sum of 2 sessions, not 10 steps!
    assert status.current_fleet_spend_usd < 0.50
    assert status.action_recommendation == "PROCEED"


def test_budget_governor_zero_and_negative_budgets(temp_storage):
    """Verifies governor handles zero or negative configured budgets without division by zero."""
    governor = FleetBudgetGovernor(daily_budget_usd=0.0, session_budget_usd=-5.0, storage=temp_storage)
    assert governor.daily_budget_usd >= 0.01
    assert governor.session_budget_usd >= 0.01

    fleet_status = governor.check_fleet_budget(active_session_projected_delta=float("nan"))
    assert fleet_status.utilization_pct >= 0.0

    session_status = governor.check_session_budget("sess_test", accumulated_cost=float("inf"))
    assert session_status.is_exceeded
    assert session_status.action_recommendation == "HALT"


# ============================================================================
# 4. Guard Halted Session Fast-Path & Concurrency
# ============================================================================

def test_guard_halted_session_fast_path(shared_engine, temp_storage):
    """Verifies that an already halted session returns last_decision immediately if raise_on_kill=False."""
    guard = AgentryGuard(engine=shared_engine, storage=temp_storage, raise_on_kill=False)

    # Force HALT
    state = guard.get_or_create_session("halt_fast_test")
    state.is_halted = True
    # Audit while halted
    decision1 = guard.audit(session_id="halt_fast_test", tool_name="bash", input_text="fatal loop", output_text="Error: stuck")
    assert state.is_halted

    # Calling audit again should return last decision without incrementing step_index
    step_before = state.step_index
    decision2 = guard.audit(session_id="halt_fast_test", tool_name="bash", input_text="retry", output_text="Error: stuck")
    assert decision2 == decision1
    assert state.step_index == step_before


def test_guard_high_concurrency_stress(shared_engine, temp_storage):
    """Tests 50 concurrent threads auditing steps across independent sessions."""
    guard = AgentryGuard(engine=shared_engine, storage=temp_storage, raise_on_kill=False)

    def worker(worker_id: int):
        session_id = f"concurrent_worker_{worker_id % 5}"
        for s in range(4):
            dec = guard.audit(
                session_id=session_id,
                tool_name="bash",
                input_text=f"step_{s}",
                output_text="ok nominal",
                prompt_tokens=150,
                completion_tokens=40
            )
            assert dec.action in ("PASS", "REROUTE", "PAUSE", "KILL")

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(worker, i) for i in range(30)]
        for f in futures:
            f.result()

    summary = temp_storage.get_fleet_summary()
    assert summary["total_audited_steps"] == 120


# ============================================================================
# 5. MCP New Tools & Resources
# ============================================================================

def test_mcp_prescribe_rewind_tool(temp_storage, shared_engine):
    """Verifies MCP tool agentry_prescribe_rewind executes and returns prescription."""
    from agentry.mcp_server import set_guard
    guard = AgentryGuard(engine=shared_engine, storage=temp_storage, raise_on_kill=False)
    set_guard(guard)

    # Seed events
    guard.audit(session_id="mcp_rewind_test", tool_name="bash", input_text="start", output_text="ok")
    guard.audit(session_id="mcp_rewind_test", tool_name="edit", input_text="edit", output_text="Error: not found")

    res = prescribe_trajectory_rewind(
        session_id="mcp_rewind_test",
        current_step=2,
        failed_tool="edit",
        error_streak=2,
        reason="Repeated edit error"
    )
    assert res["status"] == "ok"
    assert "prescription" in res
    assert res["prescription"]["failed_tool"] == "edit"
    assert res["prescription"]["pruned_steps_count"] >= 1


def test_mcp_check_budget_tool_and_resource(temp_storage, shared_engine):
    """Verifies MCP tool agentry_check_budget and fleet://budget resource."""
    from agentry.mcp_server import set_guard
    guard = AgentryGuard(engine=shared_engine, storage=temp_storage, raise_on_kill=False)
    set_guard(guard)

    res = check_fleet_and_session_budget(session_id="mcp_budget_test", accumulated_cost=0.45)
    assert res["status"] == "ok"
    assert "fleet" in res
    assert "session" in res
    assert res["session"]["current_fleet_spend_usd"] == 0.45

    # Check resource fleet://budget
    raw_json = fleet_budget_resource()
    parsed = json.loads(raw_json)
    assert "daily_budget_usd" in parsed
    assert "utilization_pct" in parsed
