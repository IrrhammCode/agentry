"""
Unit Tests for Agentry Model Context Protocol (MCP) Server.
"""

import pytest
import asyncio
from agentry.guard import AgentryGuard
from agentry.mcp_server import mcp, set_guard


@pytest.fixture(scope="module")
def shared_guard():
    guard = AgentryGuard(auto_fit=True, raise_on_kill=False)
    set_guard(guard)
    return guard


@pytest.mark.anyio
async def test_mcp_list_tools():
    """Verify that all Agentry tools are registered on the MCP server."""
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]
    assert "agentry_audit_step" in tool_names
    assert "agentry_get_fleet_status" in tool_names
    assert "agentry_inspect_session_history" in tool_names
    assert "agentry_reset_session" in tool_names


@pytest.mark.anyio
async def test_mcp_audit_step_nominal(shared_guard):
    """Test auditing a nominal agent step via MCP tool call."""
    args = {
        "session_id": "mcp_test_nominal_01",
        "step_index": 0,
        "tool_name": "read_file",
        "thought_trace": "Locating settings.py to verify configurations.",
        "error_streak": 0,
        "repetition_score": 0.10,
        "prompt_tokens": 1200,
        "completion_tokens": 100,
        "accumulated_cost_usd": 0.003
    }
    res = await mcp.call_tool("agentry_audit_step", args)
    assert not res.is_error
    data = res.structured_content
    # Depending on MCP version, structured_content or content contains the return
    if "result" in data:
        data = data["result"]
    assert data["action"] == "PASS"
    assert data["risk_level"] in ["NOMINAL", "MEDIUM"]
    assert data["session_id"] == "mcp_test_nominal_01"


@pytest.mark.anyio
async def test_mcp_audit_step_runaway_kill(shared_guard):
    """Test intercepting a severe infinite loop via MCP tool call."""
    args = {
        "session_id": "mcp_test_loop_01",
        "step_index": 5,
        "tool_name": "bash",
        "thought_trace": "Retrying python -c 'def broken(' for the 5th time...",
        "error_streak": 5,
        "repetition_score": 0.95,
        "prompt_tokens": 8000,
        "completion_tokens": 200,
        "accumulated_cost_usd": 0.08
    }
    res = await mcp.call_tool("agentry_audit_step", args)
    assert not res.is_error
    data = res.structured_content
    if "result" in data:
        data = data["result"]
    assert data["action"] == "KILL"
    assert data["risk_level"] == "CRITICAL"
    assert data["is_halted"] is True
    assert data["estimated_tokens_saved"] > 0


@pytest.mark.anyio
async def test_mcp_get_fleet_status(shared_guard):
    """Test retrieving fleet governance metrics via MCP tool call."""
    res = await mcp.call_tool("agentry_get_fleet_status", {})
    assert not res.is_error
    data = res.structured_content
    if "result" in data:
        data = data["result"]
    assert data["status"] == "healthy"
    assert data["total_audited_steps"] > 0
    assert "interventions" in data


@pytest.mark.anyio
async def test_mcp_inspect_and_reset_session(shared_guard):
    """Test inspecting session forensic history and resetting session state."""
    # 1. Inspect history
    res = await mcp.call_tool("agentry_inspect_session_history", {"session_id": "mcp_test_nominal_01"})
    assert not res.is_error
    data = res.structured_content
    if "result" in data:
        data = data["result"]
    assert data["session_id"] == "mcp_test_nominal_01"
    assert data["total_steps"] >= 1
    assert len(data["events"]) >= 1

    # 2. Reset session
    res_reset = await mcp.call_tool("agentry_reset_session", {"session_id": "mcp_test_nominal_01"})
    assert not res_reset.is_error
    reset_data = res_reset.structured_content
    if "result" in reset_data:
        reset_data = reset_data["result"]
    assert reset_data["status"] == "ok"


@pytest.mark.anyio
async def test_mcp_resources(shared_guard):
    """Test MCP resources registration and retrieval."""
    resources = await mcp.list_resources()
    uris = [str(r.uri) for r in resources]
    assert "fleet://metrics" in uris
    assert "fleet://recent-interventions" in uris

    # Read fleet metrics resource
    metric_content = await mcp.read_resource("fleet://metrics")
    assert metric_content is not None
    assert len(metric_content) > 0
    # read_resource returns list of content items (TextResourceContents or blob)
    text_content = metric_content[0].text if hasattr(metric_content[0], "text") else str(metric_content[0])
    assert "total_audited_steps" in text_content


@pytest.mark.anyio
async def test_mcp_evaluate_blast_radius(shared_guard):
    """Test evaluating blast radius via MCP tool call."""
    # Critical command
    res = await mcp.call_tool("agentry_evaluate_blast_radius", {
        "tool_name": "bash",
        "action_input": "rm -rf /"
    })
    assert not res.is_error
    data = res.structured_content
    if "result" in data:
        data = data["result"]
    assert data["is_critical"] is True
    assert data["severity"] == "CRITICAL"

    # Safe command
    res_safe = await mcp.call_tool("agentry_evaluate_blast_radius", {
        "tool_name": "bash",
        "action_input": "ls -la"
    })
    assert not res_safe.is_error
    data_safe = res_safe.structured_content
    if "result" in data_safe:
        data_safe = data_safe["result"]
    assert data_safe["is_critical"] is False
    assert data_safe["severity"] in ["NONE", "LOW"]


@pytest.mark.anyio
async def test_mcp_redact_secrets(shared_guard):
    """Test DLP secret masking via MCP tool call."""
    raw_prompt = "Export OPENAI_API_KEY=sk-abc123456789012345678901234567890123456789 to run tests"
    res = await mcp.call_tool("agentry_redact_secrets", {"text": raw_prompt})
    assert not res.is_error
    data = res.structured_content
    if "result" in data:
        data = data["result"]
    assert data["secrets_found_count"] >= 1
    assert "sk-abc123456789" not in data["redacted_text"]
    assert "[REDACTED_" in data["redacted_text"]


@pytest.mark.anyio
async def test_mcp_check_swarm_deadlock(shared_guard):
    """Test swarm deadlock watchdog via MCP tool call."""
    session = "mcp_swarm_test_01"
    # Hop 1: A -> B
    res1 = await mcp.call_tool("agentry_check_swarm_deadlock", {
        "session_id": session,
        "from_agent": "planner",
        "to_agent": "coder"
    })
    assert not res1.is_error

    # Hop 2: B -> A
    res2 = await mcp.call_tool("agentry_check_swarm_deadlock", {
        "session_id": session,
        "from_agent": "coder",
        "to_agent": "planner"
    })
    assert not res2.is_error

    # Hop 3: A -> B
    res3 = await mcp.call_tool("agentry_check_swarm_deadlock", {
        "session_id": session,
        "from_agent": "planner",
        "to_agent": "coder"
    })
    assert not res3.is_error

    # Hop 4: B -> A (cycle repeated 2 times)
    res4 = await mcp.call_tool("agentry_check_swarm_deadlock", {
        "session_id": session,
        "from_agent": "coder",
        "to_agent": "planner"
    })
    assert not res4.is_error
    data = res4.structured_content
    if "result" in data:
        data = data["result"]
    assert data["is_deadlocked"] is True
    assert data["deadlock_type"] == "PING_PONG"


@pytest.mark.anyio
async def test_mcp_rollback_filesystem(shared_guard, tmp_path):
    """Test physical checkpoint rollback via MCP tool call."""
    from agentry.checkpoint import physical_checkpointer
    test_session = "mcp_rollback_test"
    target_file = tmp_path / "mcp_test.txt"
    target_file.write_text("v1_original", encoding="utf-8")

    # Snapshot step 1 before mutation
    physical_checkpointer.snapshot(test_session, step_index=1, files=[target_file])

    # Mutate at step 1
    target_file.write_text("v2_poisoned", encoding="utf-8")

    # Call rollback tool to target_step 0
    res = await mcp.call_tool("agentry_rollback_filesystem", {
        "session_id": test_session,
        "target_step": 0
    })
    assert not res.is_error
    data = res.structured_content
    if "result" in data:
        data = data["result"]
    assert data["success"] is True
    assert target_file.read_text(encoding="utf-8") == "v1_original"



@pytest.mark.anyio
async def test_mcp_active_exemplars_resource(shared_guard):
    """Test reading active exemplars MCP resource."""
    resources = await mcp.list_resources()
    uris = [str(r.uri) for r in resources]
    assert "fleet://active-exemplars" in uris

    exemplar_content = await mcp.read_resource("fleet://active-exemplars")
    assert exemplar_content is not None
    text_content = exemplar_content[0].text if hasattr(exemplar_content[0], "text") else str(exemplar_content[0])
    assert "exemplars" in text_content

