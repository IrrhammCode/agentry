"""
Tests for Autonomic Trajectory Rewind, Fleet Budget Governor, and Prometheus Metrics.
Validates:
- TrajectoryHealer inflection point detection and conversation pruning
- FleetBudgetGovernor daily and session quota management
- Server Prometheus text exposition format (GET /metrics)
- Server Budget and Rewind REST endpoints (GET /v1/budget, POST /v1/healing/rewind)
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from agentry.healing import TrajectoryHealer, RewindPrescription, trajectory_healer
from agentry.budget import FleetBudgetGovernor, BudgetStatus, budget_governor
from agentry.storage import AuditStorage
from agentry.server import get_guard, AgentryHTTPRequestHandler
from agentry.agent import SentryDecision, StepRiskAssessment


def test_trajectory_healer_inflection_point(tmp_path):
    """Validates that TrajectoryHealer finds the correct healthy checkpoint."""
    storage = AuditStorage(tmp_path / "healing_test.db")
    healer = TrajectoryHealer(storage=storage)

    # Mock historical events: Steps 0, 1 were healthy, Step 2, 3 diverged
    mock_events = [
        {"session_id": "sess_heal_1", "step_index": 0, "action": "PASS", "failure_probability": 0.05, "error_streak": 0},
        {"session_id": "sess_heal_1", "step_index": 1, "action": "PASS", "failure_probability": 0.15, "error_streak": 0},
        {"session_id": "sess_heal_1", "step_index": 2, "action": "REROUTE", "failure_probability": 0.65, "error_streak": 1},
        {"session_id": "sess_heal_1", "step_index": 3, "action": "KILL", "failure_probability": 0.92, "error_streak": 2},
    ]

    target = healer.find_inflection_point(mock_events)
    # Step 1 was the last PASS step before the divergence
    assert target == 1


def test_trajectory_healer_diagnose_and_prescribe(tmp_path):
    """Validates prescription synthesis and counterfactual directive generation."""
    storage = AuditStorage(tmp_path / "prescribe_test.db")
    healer = TrajectoryHealer(storage=storage)

    prescription = healer.diagnose_and_prescribe(
        session_id="sess_loop_99",
        current_step=5,
        failed_tool="bash",
        error_streak=3,
        reason="Repeated command failure"
    )

    assert isinstance(prescription, RewindPrescription)
    assert prescription.session_id == "sess_loop_99"
    assert prescription.current_step == 5
    assert prescription.target_step <= 5
    assert prescription.pruned_steps_count >= 1
    assert "SYSTEM RECOVERY DIRECTIVE" in prescription.counterfactual_directive
    assert prescription.estimated_tokens_saved > 0
    assert prescription.estimated_cost_saved_usd > 0


def test_trajectory_healer_prune_messages():
    """Validates message list pruning and system directive injection."""
    messages = [
        {"role": "system", "content": "You are a coding assistant."},
        {"role": "user", "content": "Fix the bug in main.py"},
        {"role": "assistant", "content": "I will inspect the file."},
        {"role": "user", "content": "File contents..."},
        {"role": "assistant", "content": "Running broken command retry 1"},
        {"role": "user", "content": "Command failed error"},
        {"role": "assistant", "content": "Running broken command retry 2"},
    ]

    directive = "DO NOT repeat broken command. Inspect settings.py instead."
    pruned = TrajectoryHealer.prune_conversation(messages, target_step=1, directive=directive)

    assert len(pruned) < len(messages)
    # System prompt preserved
    assert pruned[0]["role"] == "system"
    # Recovery directive injected as final message
    assert pruned[-1]["role"] == "system"
    assert directive in pruned[-1]["content"]


def test_fleet_budget_governor_quotas(tmp_path):
    """Validates daily and session budget limit evaluation."""
    storage = AuditStorage(tmp_path / "budget_test.db")
    governor = FleetBudgetGovernor(
        daily_budget_usd=10.0,
        session_budget_usd=1.0,
        warning_threshold_pct=75.0,
        storage=storage
    )

    # 1. Nominal spend
    nominal_status = governor.check_session_budget("sess_norm", accumulated_cost=0.25)
    assert nominal_status.is_exceeded is False
    assert nominal_status.action_recommendation == "PROCEED"

    # 2. Warning spend
    warn_status = governor.check_session_budget("sess_warn", accumulated_cost=0.85)
    assert warn_status.is_warning is True
    assert warn_status.action_recommendation == "THROTTLE"

    # 3. Exceeded spend
    halt_status = governor.check_session_budget("sess_halt", accumulated_cost=1.20)
    assert halt_status.is_exceeded is True
    assert halt_status.action_recommendation == "HALT"


def test_server_prometheus_metrics_format():
    """Validates that GET /metrics emits valid Prometheus text exposition lines."""
    guard = get_guard()
    summary = guard.storage.get_fleet_summary()

    # Create handler mock
    handler = AgentryHTTPRequestHandler.__new__(AgentryHTTPRequestHandler)
    handler.path = "/metrics"
    sent_text = []

    def mock_send_plain_text(status_code, text):
        assert status_code == 200
        sent_text.append(text)

    handler._send_plain_text = mock_send_plain_text
    handler.do_GET()

    assert len(sent_text) == 1
    metrics_output = sent_text[0]
    assert "agentry_audited_steps_total" in metrics_output
    assert "agentry_unique_sessions_total" in metrics_output
    assert 'agentry_interventions_total{action="KILL"}' in metrics_output
    assert "agentry_fleet_budget_daily_usd" in metrics_output
    assert "agentry_fleet_spend_current_usd" in metrics_output


def test_server_budget_and_rewind_endpoints():
    """Validates GET /v1/budget and POST /v1/healing/rewind REST endpoints."""
    # 1. GET /v1/budget
    handler = AgentryHTTPRequestHandler.__new__(AgentryHTTPRequestHandler)
    handler.path = "/v1/budget"
    sent_json = []

    def mock_send_json(status_code, data, extra_headers=None):
        assert status_code == 200
        sent_json.append(data)

    handler._send_json = mock_send_json
    handler.do_GET()

    assert len(sent_json) == 1
    budget_data = sent_json[0]
    assert "daily_budget_usd" in budget_data
    assert "current_fleet_spend_usd" in budget_data
    assert "action_recommendation" in budget_data
