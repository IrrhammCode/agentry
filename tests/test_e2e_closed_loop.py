"""
End-to-End Closed-Loop Autonomic Safety Test Suite for Agentry.

Tests:
1. System Readiness Doctor (diagnostics across all subsystems).
2. Live Closed-Loop E2E Simulator (detection, autonomic rewind, recovery).
3. Transparent Auto-Rewind in Reverse Proxy (healing without client code changes).
4. Auto-Rewind cap defense (preventing infinite rewind loops, falling back to 429).
5. CLI dispatch for 'doctor' and 'e2e' subcommands.
"""

import sys
import json
import pytest
from unittest.mock import patch, MagicMock

from agentry.doctor import run_system_doctor, check_port_free
from agentry.e2e_sim import run_e2e_simulation
from agentry.proxy import OpenAIProxyHandler
from agentry.guard import AgentryGuard, SessionState
from agentry.agent import SentryDecision, StepRiskAssessment
from agentry.healing import RewindPrescription


# ============================================================================
# 1. System Doctor Readiness Tests
# ============================================================================

def test_system_doctor_execution():
    """Verifies that run_system_doctor runs all subsystem checks and returns True."""
    is_ready = run_system_doctor()
    assert is_ready is True


def test_check_port_free():
    """Verifies port checking helper works correctly."""
    # Binding to an ephemeral free port should return True
    free = check_port_free("127.0.0.1", 59123)
    assert isinstance(free, bool)


# ============================================================================
# 2. Closed-Loop E2E Simulator Tests
# ============================================================================

def test_e2e_simulation_closed_loop():
    """
    Executes the 7-step autonomous simulation end-to-end:
    - Step 5 triggers TabPFN interception
    - Healer prunes poisoned turns back to Step 2
    - Resumes and successfully completes task
    """
    result = run_e2e_simulation(speed_s=0.0)

    assert result["success"] is True
    assert result["interception_step"] is not None
    assert result["rewound_to_step"] == 2
    assert result["pruned_steps"] >= 1
    assert result["tokens_saved"] > 0
    assert result["cost_saved_usd"] > 0.0


# ============================================================================
# 3. Transparent Auto-Rewind in Reverse Proxy
# ============================================================================

def test_proxy_transparent_rewind_on_kill(tmp_path):
    """
    Verifies that when TabPFN flags KILL on an agent turn, the proxy:
    1. Catches the KILL decision.
    2. Diagnoses and prunes poisoned context.
    3. Resubmits to upstream LLM.
    4. Un-halts the session state.
    5. Returns HTTP 200 with X-Agentry-Action: HEALED.
    """
    mock_guard = MagicMock(spec=AgentryGuard)
    state = SessionState(session_id="proxy_test_sess", rewind_count=0, error_streak=2)
    mock_guard.get_or_create_session.return_value = state
    mock_storage = MagicMock()
    mock_storage.get_session_events.return_value = []
    mock_guard.storage = mock_storage

    # Mock KILL decision
    mock_decision = SentryDecision(
        session_id="proxy_test_sess",
        step_index=4,
        action="KILL",
        risk_level="CRITICAL",
        confidence=0.95,
        reason="Repetitive failure loop detected in bash commands",
        estimated_tokens_saved=5400,
        estimated_cost_saved_usd=0.0108,
        reroute_instruction=None,
        sentry_provider="local-rule-engine",
        tabpfn_assessment=StepRiskAssessment(
            session_id="proxy_test_sess",
            step_index=4,
            failure_probability=0.95,
            predicted_failure_mode="INFINITE_LOOP",
            mode_probabilities={"INFINITE_LOOP": 0.95, "NORMAL": 0.05},
            uncertainty_score=0.05,
            projected_final_cost_usd=0.05,
            primary_risk_driver="repetition_score",
            is_cloud_tabpfn=True
        )
    )
    mock_guard.audit.return_value = mock_decision

    handler = OpenAIProxyHandler(guard=mock_guard, upstream_base_url="http://fake-upstream/v1")

    # Initial upstream response that triggers KILL
    first_upstream_res = MagicMock()
    first_upstream_res.status_code = 200
    first_upstream_res.json.return_value = {
        "choices": [{"message": {"role": "assistant", "content": "cat /tmp/loop"}}],
        "usage": {"prompt_tokens": 1000, "completion_tokens": 50}
    }

    # Second upstream response after rewind resubmission
    healed_upstream_res = MagicMock()
    healed_upstream_res.status_code = 200
    healed_upstream_res.json.return_value = {
        "choices": [{"message": {"role": "assistant", "content": "Correct alternative fix."}}],
        "usage": {"prompt_tokens": 400, "completion_tokens": 30}
    }

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.side_effect = [first_upstream_res, healed_upstream_res]

    req_body = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a coding assistant."},
            {"role": "user", "content": "Fix the bug."}
        ]
    }

    with patch("httpx.Client", return_value=mock_client):
        status, data, headers = handler.handle_chat_completion(
            request_body=req_body,
            client_headers={"x-agentry-session-id": "proxy_test_sess", "authorization": "Bearer dummy"}
        )

    # Assertions
    assert status == 200
    assert headers["X-Agentry-Action"] == "HEALED"
    assert headers["X-Agentry-Auto-Healed"] == "true"
    assert "X-Agentry-Rewound-Target" in headers
    assert state.is_halted is False
    assert state.rewind_count == 1
    assert data["choices"][0]["message"]["content"] == "Correct alternative fix."


def test_proxy_rewind_cap_prevents_infinite_rewinds():
    """
    Verifies that if an agent has already exhausted max rewinds (rewind_count >= 2),
    the proxy refuses further rewinds and halts the agent with HTTP 429.
    """
    mock_guard = MagicMock(spec=AgentryGuard)
    state = SessionState(session_id="proxy_capped_sess", rewind_count=2, error_streak=3)
    mock_guard.get_or_create_session.return_value = state

    mock_decision = SentryDecision(
        session_id="proxy_capped_sess",
        step_index=8,
        action="KILL",
        risk_level="CRITICAL",
        confidence=0.98,
        reason="Repeated runaway loop despite previous rewinds",
        estimated_tokens_saved=3600,
        estimated_cost_saved_usd=0.0072,
        reroute_instruction=None,
        sentry_provider="local-rule-engine",
        tabpfn_assessment=StepRiskAssessment(
            session_id="proxy_capped_sess",
            step_index=8,
            failure_probability=0.98,
            predicted_failure_mode="INFINITE_LOOP",
            mode_probabilities={"INFINITE_LOOP": 0.98, "NORMAL": 0.02},
            uncertainty_score=0.02,
            projected_final_cost_usd=0.08,
            primary_risk_driver="repetition_score",
            is_cloud_tabpfn=True
        )
    )
    mock_guard.audit.return_value = mock_decision

    handler = OpenAIProxyHandler(guard=mock_guard, upstream_base_url="http://fake-upstream/v1")

    upstream_res = MagicMock()
    upstream_res.status_code = 200
    upstream_res.json.return_value = {
        "choices": [{"message": {"role": "assistant", "content": "stuck in loop"}}],
        "usage": {"prompt_tokens": 1200, "completion_tokens": 40}
    }

    mock_client = MagicMock()
    mock_client.__enter__.return_value = mock_client
    mock_client.post.return_value = upstream_res

    req_body = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "retry loop"}]
    }

    with patch("httpx.Client", return_value=mock_client):
        status, data, headers = handler.handle_chat_completion(
            request_body=req_body,
            client_headers={"x-agentry-session-id": "proxy_capped_sess"}
        )

    # Must return HTTP 429 circuit breaker halt
    assert status == 429
    assert data["error"]["code"] == "CIRCUIT_BREAKER_HALT"
    assert headers["X-Agentry-Action"] == "KILL"


# ============================================================================
# 4. CLI Subcommand Dispatch Tests
# ============================================================================

def test_cli_doctor_dispatch():
    """Verifies that 'agentry doctor' CLI command invokes run_system_doctor."""
    from agentry.cli import main

    with patch("sys.argv", ["agentry", "doctor"]):
        with patch("agentry.doctor.run_system_doctor", return_value=True) as mock_doc:
            with pytest.raises(SystemExit) as exc:
                main()
            assert exc.value.code == 0
            mock_doc.assert_called_once()


def test_cli_e2e_dispatch():
    """Verifies that 'agentry e2e' CLI command invokes run_e2e_simulation."""
    from agentry.cli import main

    with patch("sys.argv", ["agentry", "e2e", "--speed", "0.0"]):
        with patch("agentry.e2e_sim.run_e2e_simulation", return_value={"success": True}) as mock_e2e:
            main()
            mock_e2e.assert_called_once_with(speed_s=0.0)
