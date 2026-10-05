"""
Unit and integration tests for NexusFleet SQLite Database Manager.
"""

import sqlite3
from pathlib import Path
import pytest

from projects_arena.nexus_fleet.database import (
    DatabaseManager,
    create_node,
    create_task,
    get_db_connection,
    get_node_by_id,
    get_node_by_name,
    get_nodes,
    get_task_by_id,
    get_tasks,
    get_tasks_by_node,
    init_db,
    inspect_db_state,
    reset_db,
    seed_data,
    update_node_status,
    update_task_status,
)


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Fixture to provide a clean temporary SQLite database path."""
    return tmp_path / "test_nexus_fleet.db"


def test_init_db_and_pragmas(temp_db_path: Path):
    """Verify table creation, WAL mode, and foreign keys."""
    init_db(temp_db_path)
    state = inspect_db_state(temp_db_path)
    
    assert state["journal_mode"].lower() == "wal"
    assert state["foreign_keys_enabled"] is True
    assert state["node_count"] == 0
    assert state["task_count"] == 0


def test_foreign_key_enforcement(temp_db_path: Path):
    """Verify that inserting a task with a non-existent node_id fails with IntegrityError."""
    init_db(temp_db_path)
    with pytest.raises(sqlite3.IntegrityError):
        create_task(
            node_id=99999,  # Non-existent node
            title="Invalid Task",
            command="echo 'invalid'",
            risk_score=0.5,
            status="pending",
            db_path=temp_db_path,
        )


def test_seed_data_count_and_idempotency(temp_db_path: Path):
    """Verify exactly 3 nodes and 4 tasks are seeded and operation is idempotent."""
    res1 = seed_data(temp_db_path)
    assert res1["nodes_added"] == 3
    assert res1["tasks_added"] == 4
    
    state1 = inspect_db_state(temp_db_path)
    assert state1["node_count"] == 3
    assert state1["task_count"] == 4

    nodes = get_nodes(temp_db_path)
    assert len(nodes) == 3
    assert {n["role"] for n in nodes} == {"coordinator", "worker", "gateway"}

    tasks = get_tasks(temp_db_path)
    assert len(tasks) == 4

    # Second call should not duplicate records
    res2 = seed_data(temp_db_path)
    assert res2["nodes_added"] == 0
    assert res2["tasks_added"] == 0

    state2 = inspect_db_state(temp_db_path)
    assert state2["node_count"] == 3
    assert state2["task_count"] == 4


def test_cascade_delete(temp_db_path: Path):
    """Verify that deleting a node cascades and removes its associated tasks."""
    seed_data(temp_db_path)
    
    worker = get_node_by_name("nexus-worker-01", temp_db_path)
    assert worker is not None
    worker_id = worker["id"]
    
    tasks_before = get_tasks_by_node(worker_id, temp_db_path)
    assert len(tasks_before) == 2

    # Delete worker node
    with get_db_connection(temp_db_path) as conn:
        conn.execute("DELETE FROM nodes WHERE id = ?", (worker_id,))

    # Tasks should be automatically cascade-deleted
    tasks_after = get_tasks_by_node(worker_id, temp_db_path)
    assert len(tasks_after) == 0


def test_transaction_rollback_on_error(temp_db_path: Path):
    """Verify that context manager rolls back on exception."""
    init_db(temp_db_path)
    
    try:
        with get_db_connection(temp_db_path) as conn:
            conn.execute(
                "INSERT INTO nodes (name, role, status, ip_address) VALUES (?, ?, ?, ?)",
                ("rollback-test", "test", "active", "1.1.1.1"),
            )
            raise RuntimeError("Forced simulation error")
    except RuntimeError:
        pass

    assert get_node_by_name("rollback-test", temp_db_path) is None


def test_crud_operations(temp_db_path: Path):
    """Verify basic CRUD helpers."""
    init_db(temp_db_path)
    
    # Create node
    node_id = create_node("node-alpha", "validator", "idle", "10.0.0.50", temp_db_path)
    assert node_id > 0
    node = get_node_by_id(node_id, temp_db_path)
    assert node["name"] == "node-alpha"
    assert node["status"] == "idle"

    # Update node status
    updated = update_node_status(node_id, "active", temp_db_path)
    assert updated is True
    assert get_node_by_id(node_id, temp_db_path)["status"] == "active"

    # Create task
    task_id = create_task(
        node_id=node_id,
        title="Check Health",
        command="ping -c 1 8.8.8.8",
        risk_score=0.1,
        status="pending",
        db_path=temp_db_path,
    )
    assert task_id > 0
    task = get_task_by_id(task_id, temp_db_path)
    assert task["title"] == "Check Health"
    assert task["status"] == "pending"

    # Update task status and result
    task_updated = update_task_status(task_id, "completed", "1 packet transmitted, 0 loss", temp_db_path)
    assert task_updated is True
    updated_task = get_task_by_id(task_id, temp_db_path)
    assert updated_task["status"] == "completed"
    assert "0 loss" in updated_task["result"]


def test_database_manager_class(temp_db_path: Path):
    """Verify the DatabaseManager object-oriented wrapper."""
    mgr = DatabaseManager(temp_db_path)
    mgr.init_db()
    counts = mgr.seed_data()
    assert counts["nodes_added"] == 3
    assert counts["tasks_added"] == 4

    mgr.reset_db()
    state = inspect_db_state(temp_db_path)
    assert state["node_count"] == 0
    assert state["task_count"] == 0
