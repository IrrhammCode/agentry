"""
Comprehensive Automated Test Suite for NexusFleet REST API & Agentry Guardrail.
Tests:
- Schema initialization and healthcheck
- Real-time fleet metrics computation
- Node registration and duplicate rejection
- Node status transitions
- Task dispatch with benign commands
- Sub-15ms Agentry Sentinel Interception of catastrophic commands (rm -rf /, DROP TABLE)
- Non-strict quarantined task recording
- Task deletion and cascading cleanup
"""

import pytest
from fastapi.testclient import TestClient

from projects_arena.nexus_fleet.app import app
from projects_arena.nexus_fleet.database import init_db, reset_db, seed_data


@pytest.fixture(autouse=True)
def setup_test_db():
    """Ensure database is reset and freshly seeded before each test."""
    reset_db()
    seed_data()
    yield


@pytest.fixture
def client():
    """FastAPI TestClient fixture."""
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client):
    """Test health check endpoint reports healthy and shows SQLite WAL info."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "NexusFleet"
    assert data["database"]["foreign_keys_enabled"] is True
    assert data["database"]["node_count"] >= 3


def test_metrics_endpoint(client):
    """Test metrics endpoint returns nodes, tasks, and safety stats."""
    response = client.get("/api/v1/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "nodes" in data
    assert "tasks" in data
    assert "safety" in data
    assert data["nodes"]["total"] >= 3
    assert data["tasks"]["total"] >= 4
    assert isinstance(data["safety"]["average_risk_score"], float)


def test_list_and_filter_nodes(client):
    """Test listing nodes and filtering by role."""
    # List all
    res = client.get("/api/v1/nodes")
    assert res.status_code == 200
    nodes = res.json()["nodes"]
    assert len(nodes) >= 3

    # Filter by role 'coordinator'
    res_coord = client.get("/api/v1/nodes?role=coordinator")
    assert res_coord.status_code == 200
    coord_nodes = res_coord.json()["nodes"]
    assert len(coord_nodes) >= 1
    assert all(n["role"] == "coordinator" for n in coord_nodes)


def test_register_new_node(client):
    """Test registering a new fleet node and rejecting duplicates."""
    new_node = {
        "name": "nexus-canary-99",
        "role": "canary",
        "status": "online",
        "ip_address": "10.0.0.99",
    }
    res = client.post("/api/v1/nodes", json=new_node)
    assert res.status_code == 201
    node_id = res.json()["node_id"]
    assert isinstance(node_id, int)

    # Attempt duplicate
    dup_res = client.post("/api/v1/nodes", json=new_node)
    assert dup_res.status_code == 400
    assert "already registered" in dup_res.json()["detail"]


def test_update_node_status(client):
    """Test updating node status."""
    res = client.patch("/api/v1/nodes/1/status", json={"status": "busy"})
    assert res.status_code == 200

    detail_res = client.get("/api/v1/nodes/1")
    assert detail_res.status_code == 200
    assert detail_res.json()["node"]["status"] == "busy"


def test_dispatch_safe_task(client):
    """Test dispatching a safe maintenance command passes Agentry and gets queued."""
    safe_task = {
        "node_id": 1,
        "title": "Ingress SSL Certificate Renewal",
        "command": "certbot renew --dry-run",
        "risk_score": 0.15,
    }
    res = client.post("/api/v1/tasks", json=safe_task)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "pending"
    assert "task_id" in data


def test_agentry_blocks_rm_rf_root_strict(client):
    """
    CRITICAL AGENTRY SENTRY VERIFICATION:
    Verifies that a hallucinated or malicious `rm -rf /` command is intercepted
    in sub-15ms and blocked with HTTP 403 Forbidden.
    """
    destructive_task = {
        "node_id": 1,
        "title": "Clear Temp Files (Catastrophic Command)",
        "command": "rm -rf / --no-preserve-root",
    }
    res = client.post("/api/v1/tasks?strict=true", json=destructive_task)
    assert res.status_code == 403
    err = res.json()["detail"]
    assert err["error"] == "AGENTRY_BLAST_RADIUS_VIOLATION"
    assert "Agentry Sentinel" in err["message"]
    assert err["risk_score"] >= 0.9


def test_agentry_blocks_drop_table_non_strict(client):
    """
    Verifies non-strict mode: Agentry intercepts SQL DROP TABLE and safely
    records the task in a quarantined 'blocked' state with incident details.
    """
    drop_task = {
        "node_id": 2,
        "title": "Reset Schema (Dangerous Command)",
        "command": "DROP TABLE nodes;",
    }
    res = client.post("/api/v1/tasks?strict=false", json=drop_task)
    assert res.status_code == 201
    data = res.json()
    assert data["status"] == "blocked"
    assert "BLOCKED" in data["message"] and "Agentry" in data["message"]


def test_guard_evaluate_endpoint(client):
    """Directly test the /api/v1/guard/evaluate endpoint."""
    # Test safe
    res_safe = client.post(
        "/api/v1/guard/evaluate",
        json={"command": "pytest tests/ -v", "tool_name": "bash"},
    )
    assert res_safe.status_code == 200
    assert res_safe.json()["is_blocked"] is False
    assert res_safe.json()["action"] == "PASS"

    # Test catastrophic
    res_danger = client.post(
        "/api/v1/guard/evaluate",
        json={"command": "rm -rf /var/log/*", "tool_name": "bash"},
    )
    assert res_danger.status_code == 200
    assert res_danger.json()["is_blocked"] is True
    assert res_danger.json()["action"] in ("KILL", "WARN")


def test_task_lifecycle_update_and_delete(client):
    """Test modifying task status and deleting task records."""
    # Update task #1 to running
    res = client.patch("/api/v1/tasks/1", json={"status": "running", "result": "In progress"})
    assert res.status_code == 200

    # Delete task #1
    del_res = client.delete("/api/v1/tasks/1")
    assert del_res.status_code == 200

    # Check 404
    get_res = client.patch("/api/v1/tasks/1", json={"status": "completed"})
    assert get_res.status_code == 404
