"""
Unit and Integration Tests for Agentry Enterprise Capabilities:
1. Incident Post-Mortem Exporter (Markdown & HTML)
2. Real-Time Webhook Alerting (Slack, Discord, JSON)
3. Human-in-the-Loop (HITL) Web Approval Gateway
4. Zero-Code OpenAI-Compatible Reverse Proxy Middleware
5. Extended MCP Tools (Reports & HITL)
"""

import time
import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch

from agentry.report import generate_incident_report, export_incident_report_to_file
from agentry.alerts import WebhookNotifier
from agentry.hitl import HITLManager, HITLRequest
from agentry.proxy import OpenAIProxyHandler
from agentry.guard import AgentryGuard, SentryDecision
from agentry.storage import AuditStorage
from agentry.engine import StepRiskAssessment
from agentry.mcp_server import mcp, set_guard


def make_decision(
    session_id: str,
    step_index: int = 0,
    action: str = "PASS",
    risk_level: str = "NOMINAL",
    failure_probability: float = 0.05,
    predicted_failure_mode: str = "NORMAL",
    reason: str = "Normal step",
    reroute_instruction: str = None,
    tokens_saved: int = 0,
    cost_saved: float = 0.0,
    projected_final_cost_usd: float = 0.05
) -> SentryDecision:
    assessment = StepRiskAssessment(
        session_id=session_id,
        step_index=step_index,
        failure_probability=failure_probability,
        predicted_failure_mode=predicted_failure_mode,
        mode_probabilities={predicted_failure_mode: failure_probability},
        uncertainty_score=0.1,
        projected_final_cost_usd=projected_final_cost_usd,
        primary_risk_driver="repetition",
        is_cloud_tabpfn=False
    )
    return SentryDecision(
        session_id=session_id,
        step_index=step_index,
        action=action,
        risk_level=risk_level,
        confidence=0.9,
        reason=reason,
        reroute_instruction=reroute_instruction,
        estimated_tokens_saved=tokens_saved,
        estimated_cost_saved_usd=cost_saved,
        sentry_provider="agentry-local-sentry",
        tabpfn_assessment=assessment
    )


# ============================================================================
# 1. Incident Post-Mortem Exporter Tests
# ============================================================================

def test_incident_report_empty_session(tmp_path):
    storage = AuditStorage(db_path=tmp_path / "test_empty.db")
    md = generate_incident_report("non_existent_session", format="markdown", storage=storage)
    assert "No telemetry or audit events recorded" in md

    html = generate_incident_report("non_existent_session", format="html", storage=storage)
    assert "No telemetry or audit events recorded" in html


def test_incident_report_generation_markdown_and_html(tmp_path):
    storage = AuditStorage(db_path=tmp_path / "test_audit.db")

    # Record simulated audit decisions
    for i in range(3):
        action = "KILL" if i == 2 else "PASS"
        risk_level = "CRITICAL" if i == 2 else "NOMINAL"
        prob = 0.92 if i == 2 else 0.05
        mode = "INFINITE_LOOP" if i == 2 else "NORMAL"
        dec = make_decision(
            session_id="test_incident_session_01",
            step_index=i,
            action=action,
            risk_level=risk_level,
            failure_probability=prob,
            predicted_failure_mode=mode,
            reason=f"Step {i} test reason.",
            reroute_instruction="Break retry loop" if i == 2 else None,
            tokens_saved=12000 if i == 2 else 0,
            cost_saved=0.024 if i == 2 else 0.0,
            projected_final_cost_usd=0.15
        )
        storage.record_decision(dec)

    # 1. Test Markdown generation
    md_report = generate_incident_report("test_incident_session_01", format="markdown", storage=storage)
    assert "Agentry Enterprise Incident Post-Mortem Report" in md_report
    assert "test_incident_session_01" in md_report
    assert "CRITICAL: CIRCUIT-BREAKER TERMINATION (KILL)" in md_report
    assert "12,000 tokens" in md_report
    assert "$0.0240 USD" in md_report
    assert "Step 2 test reason." in md_report

    # 2. Test HTML generation
    html_report = generate_incident_report("test_incident_session_01", format="html", storage=storage)
    assert "<!DOCTYPE html>" in html_report
    assert "test_incident_session_01" in html_report
    assert "CRITICAL: CIRCUIT-BREAKER TERMINATION (KILL)" in html_report
    assert "<table>" in html_report

    # 3. Test File Export
    out_file = export_incident_report_to_file("test_incident_session_01", output_dir=tmp_path, format="markdown", storage=storage)
    assert out_file.exists()
    assert out_file.suffix == ".md"
    assert "test_incident_session_01" in out_file.read_text(encoding="utf-8")


# ============================================================================
# 2. Real-Time Webhook Alerting Tests
# ============================================================================

def test_webhook_notifier_payload_formatting():
    notifier = WebhookNotifier(webhook_url="https://hooks.slack.com/services/T00/B00/X00")

    dec = make_decision(
        session_id="alert_test_sess",
        step_index=4,
        action="KILL",
        risk_level="CRITICAL",
        failure_probability=0.95,
        predicted_failure_mode="INFINITE_LOOP",
        reason="Severe infinite retry loop detected.",
        tokens_saved=50000,
        cost_saved=0.10,
        projected_final_cost_usd=0.50
    )

    # 1. Test Slack payload
    slack_payload = notifier._build_slack_payload(dec)
    assert "blocks" in slack_payload
    assert "KILL" in slack_payload["text"]

    # 2. Test Discord payload
    discord_payload = notifier._build_discord_payload(dec)
    assert "embeds" in discord_payload
    assert discord_payload["embeds"][0]["color"] == 0xEF4444  # Red for KILL

    # 3. Test Generic payload
    generic_payload = notifier._build_generic_payload(dec)
    assert generic_payload["event_type"] == "agentry.circuit_breaker.intervention"
    assert generic_payload["decision"]["action"] == "KILL"
    assert generic_payload["decision"]["session_id"] == "alert_test_sess"


def test_webhook_notifier_dispatch_mock():
    notifier = WebhookNotifier(webhook_url="https://discord.com/api/webhooks/123/abc")

    dec = make_decision(
        session_id="alert_dispatch_sess",
        step_index=2,
        action="PAUSE",
        risk_level="HIGH",
        failure_probability=0.72,
        predicted_failure_mode="TOOL_HALLUCINATION",
        reason="Repeated invalid tool invocations.",
        reroute_instruction="Verify tool names",
        tokens_saved=10000,
        cost_saved=0.02,
        projected_final_cost_usd=0.20
    )

    with patch("httpx.Client.post") as mock_post:
        mock_post.return_value = MagicMock(status_code=204)
        success = notifier._dispatch_sync(dec)
        assert success is True
        assert mock_post.called
        call_kwargs = mock_post.call_args[1]
        assert "embeds" in call_kwargs["json"]


# ============================================================================
# 3. Human-in-the-Loop (HITL) Gateway Tests
# ============================================================================

def test_hitl_lifecycle():
    hitl = HITLManager()

    dec = make_decision(
        session_id="hitl_test_session",
        step_index=3,
        action="PAUSE",
        risk_level="HIGH",
        failure_probability=0.78,
        predicted_failure_mode="COST_RUNAWAY",
        reason="Approaching budget runaway.",
        reroute_instruction="Prune context",
        tokens_saved=15000,
        cost_saved=0.03,
        projected_final_cost_usd=0.85
    )

    # 1. Create escalation
    req = hitl.create_escalation(dec, tool_name="bash")
    assert req.request_id.startswith("hitl_")
    assert req.status == "PENDING"
    assert req.session_id == "hitl_test_session"

    # 2. List requests
    pending = hitl.list_requests(status="PENDING")
    assert len(pending) == 1
    assert pending[0]["request_id"] == req.request_id

    # 3. Resolve with REROUTE
    updated = hitl.resolve(
        request_id=req.request_id,
        resolution="REROUTE",
        comment="Operator verified runaway tokens",
        custom_directive="Reduce search depth to 2"
    )
    assert updated is not None
    assert updated.status == "REROUTED"
    assert updated.custom_directive == "Reduce search depth to 2"
    assert updated.operator_comment == "Operator verified runaway tokens"

    # 4. Verify no longer pending
    pending_after = hitl.list_requests(status="PENDING")
    assert len(pending_after) == 0

    all_reqs = hitl.list_requests(status=None)
    assert len(all_reqs) == 1


def test_hitl_sync_wait_resolution():
    hitl = HITLManager()

    dec = make_decision(
        session_id="sync_wait_session",
        step_index=1,
        action="PAUSE",
        risk_level="HIGH",
        failure_probability=0.75,
        predicted_failure_mode="INFINITE_LOOP",
        reason="Infinite loop pause.",
        tokens_saved=5000,
        cost_saved=0.01,
        projected_final_cost_usd=0.30
    )

    req = hitl.create_escalation(dec)

    import threading
    def background_resolver():
        time.sleep(0.1)
        hitl.resolve(req.request_id, resolution="RESUME", comment="Approved after audit")

    t = threading.Thread(target=background_resolver)
    t.start()

    resolved_req = hitl.wait_for_resolution(req.request_id, timeout_s=3.0)
    t.join()

    assert resolved_req.status == "APPROVED_RESUME"
    assert resolved_req.operator_comment == "Approved after audit"


# ============================================================================
# 4. OpenAI Reverse Proxy Middleware Tests
# ============================================================================

def test_proxy_chat_completion_circuit_breaker(tmp_path):
    guard = AgentryGuard(
        storage=AuditStorage(db_path=tmp_path / "proxy_test.db"),
        auto_fit=False,
        raise_on_kill=False
    )
    # Manually halt a session in the guard
    state = guard.get_or_create_session("halted_session_99")
    state.is_halted = True
    state.last_decision = make_decision(
        session_id="halted_session_99",
        step_index=5,
        action="KILL",
        risk_level="CRITICAL",
        failure_probability=0.98,
        predicted_failure_mode="INFINITE_LOOP",
        reason="Autonomous KILL triggered on infinite loop.",
        tokens_saved=20000,
        cost_saved=0.04,
        projected_final_cost_usd=0.50
    )

    proxy = OpenAIProxyHandler(guard=guard)
    status_code, body, headers = proxy.handle_chat_completion(
        request_body={
            "model": "gpt-4o",
            "messages": [{"role": "user", "content": "Keep running"}],
            "user": "halted_session_99"
        },
        client_headers={"x-session-id": "halted_session_99"},
        guard=guard
    )

    assert status_code == 429
    assert headers.get("X-Agentry-Action") == "KILL"
    assert body["error"]["code"] == "SESSION_HALTED"
    assert "CIRCUIT BREAKER" in body["error"]["message"]


def test_proxy_blocks_critical_blast_radius(tmp_path):
    """Test that the reverse proxy intercepts dangerous commands in tool_calls before execution."""
    guard = AgentryGuard(
        storage=AuditStorage(db_path=tmp_path / "proxy_blast.db"),
        auto_fit=False,
        raise_on_kill=False
    )
    proxy = OpenAIProxyHandler(guard=guard)

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "id": "chatcmpl-test-blast",
        "choices": [{
            "message": {
                "role": "assistant",
                "content": None,
                "tool_calls": [{
                    "id": "call_1",
                    "type": "function",
                    "function": {
                        "name": "bash",
                        "arguments": '{"command": "rm -rf /"}'
                    }
                }]
            }
        }],
        "usage": {"prompt_tokens": 100, "completion_tokens": 20}
    }

    with patch("httpx.Client.post", return_value=mock_resp):
        status, body, headers = proxy.handle_chat_completion(
            request_body={"model": "gpt-4o", "messages": [{"role": "user", "content": "Clean up"}]},
            client_headers={"x-session-id": "blast_proxy_session"},
            guard=guard
        )

    assert status == 429
    assert headers.get("X-Agentry-Action") == "KILL"
    assert headers.get("X-Agentry-Blast-Radius") == "CRITICAL"
    assert "Critical destructive blast radius blocked" in body["error"]["message"]


def test_proxy_redacts_secrets_in_completion(tmp_path):
    """Test that the reverse proxy automatically masks API credentials in completions."""
    guard = AgentryGuard(
        storage=AuditStorage(db_path=tmp_path / "proxy_dlp.db"),
        auto_fit=True,
        raise_on_kill=False
    )

    proxy = OpenAIProxyHandler(guard=guard)

    secret_key = "sk-proj-1234567890123456789012345678901234567890"
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "id": "chatcmpl-test-dlp",
        "choices": [{
            "message": {
                "role": "assistant",
                "content": f"Here is your new key: {secret_key}"
            }
        }],
        "usage": {"prompt_tokens": 100, "completion_tokens": 20}
    }

    with patch("httpx.Client.post", return_value=mock_resp):
        status, body, headers = proxy.handle_chat_completion(
            request_body={"model": "gpt-4o", "messages": [{"role": "user", "content": "Fetch key"}]},
            client_headers={"x-session-id": "dlp_proxy_session"},
            guard=guard
        )

    assert status == 200
    returned_content = body["choices"][0]["message"]["content"]
    assert secret_key not in returned_content
    assert "[REDACTED_" in returned_content


# ============================================================================
# 5. Extended MCP Tools Tests
# ============================================================================


@pytest.mark.anyio
async def test_mcp_extended_tools_registration():
    """Verify that report and HITL tools are exposed on the MCP server."""
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]
    assert "agentry_export_incident_report" in tool_names
    assert "agentry_list_hitl_approvals" in tool_names
    assert "agentry_resolve_hitl_approval" in tool_names


@pytest.mark.anyio
async def test_mcp_hitl_and_report_tools():
    """Test calling agentry_list_hitl_approvals and agentry_resolve_hitl_approval over MCP."""
    from agentry.hitl import hitl_gateway

    dec = make_decision(
        session_id="mcp_hitl_sess",
        step_index=2,
        action="PAUSE",
        risk_level="HIGH",
        failure_probability=0.70,
        predicted_failure_mode="TOOL_HALLUCINATION",
        reason="Tool hallucination detected.",
        reroute_instruction="Verify tool signature",
        tokens_saved=5000,
        cost_saved=0.01,
        projected_final_cost_usd=0.20
    )
    req = hitl_gateway.create_escalation(dec, tool_name="unknown_tool")

    # 1. Call list over MCP
    res_list = await mcp.call_tool("agentry_list_hitl_approvals", {"status": "PENDING"})
    assert not res_list.is_error
    data_list = res_list.structured_content
    if "result" in data_list:
        data_list = data_list["result"]
    assert data_list["count"] >= 1

    # 2. Call resolve over MCP
    res_resolve = await mcp.call_tool("agentry_resolve_hitl_approval", {
        "request_id": req.request_id,
        "resolution": "RESUME",
        "comment": "Resolved via MCP client"
    })
    assert not res_resolve.is_error
    data_resolve = res_resolve.structured_content
    if "result" in data_resolve:
        data_resolve = data_resolve["result"]
    assert data_resolve["status"] == "ok"
    assert data_resolve["resolution"] == "APPROVED_RESUME"

    # 3. Call export incident report over MCP
    res_rep = await mcp.call_tool("agentry_export_incident_report", {
        "session_id": "mcp_hitl_sess",
        "format": "markdown",
        "save_to_disk": False
    })
    assert not res_rep.is_error
    data_rep = res_rep.structured_content
    if "result" in data_rep:
        data_rep = data_rep["result"]
    assert data_rep["session_id"] == "mcp_hitl_sess"
    assert "report_content" in data_rep


def test_proxy_security_spoofed_x_forwarded_for_rejected(tmp_path):
    """External requests spoofing X-Forwarded-For: 127.0.0.1 must be rejected if unauthenticated."""
    guard = AgentryGuard(
        storage=AuditStorage(db_path=tmp_path / "proxy_sec.db"),
        auto_fit=False,
        raise_on_kill=False
    )
    # Using an external upstream URL to ensure authentication is enforced
    proxy = OpenAIProxyHandler(guard=guard, upstream_base_url="https://api.groq.com/openai/v1")

    # Client has external socket address 198.51.100.42 but sends spoofed X-Forwarded-For
    headers = {
        "remote-addr": "198.51.100.42",
        "x-forwarded-for": "127.0.0.1",
        "x-session-id": "spoof_attempt_session"
    }

    status, body, _ = proxy.handle_chat_completion(
        request_body={"model": "gpt-4o", "messages": [{"role": "user", "content": "hello"}]},
        client_headers=headers,
        guard=guard
    )

    assert status == 401
    assert body["error"]["code"] == "MISSING_AUTH_HEADER"
