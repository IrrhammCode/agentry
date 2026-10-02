import json
import threading
import urllib.request
import urllib.parse
from http.server import ThreadingHTTPServer
import pytest

from agentry.server import AgentryHTTPRequestHandler


@pytest.fixture(scope="module")
def live_server():
    """Spin up an in-process HTTP server on an ephemeral port for testing."""
    server = ThreadingHTTPServer(("127.0.0.1", 0), AgentryHTTPRequestHandler)
    host, port = server.server_address
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    base_url = f"http://{host}:{port}"
    yield base_url
    server.shutdown()
    server.server_close()


def http_get(url: str):
    req = urllib.request.Request(url, headers={"User-Agent": "AgentryTestClient"})
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode("utf-8")
        content_type = resp.headers.get("Content-Type", "")
        if "application/json" in content_type:
            return resp.status, json.loads(body)
        return resp.status, body


def http_post(url: str, data: dict):
    encoded = json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=encoded,
        headers={"Content-Type": "application/json", "User-Agent": "AgentryTestClient"}
    )
    with urllib.request.urlopen(req) as resp:
        body = resp.read().decode("utf-8")
        return resp.status, json.loads(body)


def test_health_check(live_server):
    status, body = http_get(f"{live_server}/health")
    assert status == 200
    assert body["status"] == "healthy"
    assert "version" in body
    assert "service" in body


def test_models_endpoint(live_server):
    status, body = http_get(f"{live_server}/v1/models")
    assert status == 200
    assert "data" in body
    model_ids = [m["id"] for m in body["data"]]
    assert "agentry-tabpfn-3.5" in model_ids


def test_prometheus_metrics(live_server):
    status, body = http_get(f"{live_server}/metrics")
    assert status == 200
    assert "agentry_audited_steps_total" in body


def test_fleet_and_budget(live_server):
    status, body = http_get(f"{live_server}/v1/fleet")
    assert status == 200
    assert isinstance(body, dict)

    status_b, body_b = http_get(f"{live_server}/v1/budget")
    assert status_b == 200
    assert "daily_budget_usd" in body_b


def test_dlp_redaction_endpoint(live_server):
    payload = {"text": "My AWS key is AKIAIOSFODNN7EXAMPLE and secret is sk-ant-api03-abcdef"}
    status, body = http_post(f"{live_server}/v1/dlp/redact", payload)
    assert status == 200
    assert "masked_text" in body
    assert "REDACTED" in body["masked_text"]
    assert body["redaction_count"] >= 1


def test_blast_radius_endpoint(live_server):
    payload = {"tool_name": "bash", "command": "rm -rf / --no-preserve-root"}
    status, body = http_post(f"{live_server}/v1/blast-radius/evaluate", payload)
    assert status == 200
    assert body["is_blocked"] is True
    assert body["score"] >= 80
    assert body["category"] == "CRITICAL"


def test_swarm_deadlock_endpoint(live_server):
    # Pass a 4-step ping pong cycle: A -> B -> A -> B
    transfers = [
        {"from_agent": "Agent_Planner", "to_agent": "Agent_Coder", "task": "Write route"},
        {"from_agent": "Agent_Coder", "to_agent": "Agent_Planner", "task": "Clarify specs"},
        {"from_agent": "Agent_Planner", "to_agent": "Agent_Coder", "task": "Here is the spec"},
        {"from_agent": "Agent_Coder", "to_agent": "Agent_Planner", "task": "Need more detail"},
    ]
    payload = {"session_id": "swarm_test_cycle", "transfers": transfers}
    status, body = http_post(f"{live_server}/v1/swarm/deadlock", payload)
    assert status == 200
    assert body["is_deadlocked"] is True
    assert body["cycle_length"] >= 2


def test_audit_endpoint(live_server):
    payload = {
        "session_id": "test_audit_api_session",
        "tool_name": "bash",
        "input_text": "cat /var/log/syslog",
        "prompt_tokens": 120,
        "completion_tokens": 45
    }
    status, body = http_post(f"{live_server}/v1/audit", payload)
    assert status == 200
    assert "action" in body
    assert "risk_level" in body
    assert body["session_id"] == "test_audit_api_session"


def test_emergency_suspend(live_server):
    status, body = http_post(f"{live_server}/v1/fleet/emergency-suspend", {})
    assert status == 200
    assert body["status"] == "suspended"
    assert "halted_sessions" in body
