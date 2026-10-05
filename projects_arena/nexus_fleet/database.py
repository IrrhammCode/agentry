"""
NexusFleet SQLite Database Manager
Production-grade SQLite database manager using standard library sqlite3 with:
- WAL mode (Write-Ahead Logging) enabled for high-concurrency read/write
- Foreign key constraints enforced
- Connection & transaction context managers
- Tables for 'nodes' and 'tasks'
- Schema initialization and idempotent seed data helpers
"""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Generator, Sequence

# Default database location relative to this file
DEFAULT_DB_PATH = Path(__file__).resolve().parent / "nexus_fleet.db"


def get_default_db_path() -> Path:
    """Return configured database path from environment or default location."""
    env_path = os.getenv("NEXUS_FLEET_DB_PATH")
    if env_path:
        return Path(env_path)
    return DEFAULT_DB_PATH


@contextmanager
def get_db_connection(
    db_path: str | Path | None = None,
    timeout: float = 30.0,
    enforce_foreign_keys: bool = True,
    enable_wal: bool = True,
) -> Generator[sqlite3.Connection, None, None]:
    """
    Context manager that yields an active SQLite connection configured with:
    - Row factory set to sqlite3.Row for dict-like access
    - Foreign keys enabled (PRAGMA foreign_keys = ON)
    - WAL journal mode enabled (PRAGMA journal_mode = WAL)
    - Busy timeout set to handle concurrent access
    - Automatic COMMIT on clean exit and ROLLBACK on exceptions
    """
    target = Path(db_path) if db_path and str(db_path) != ":memory:" else (db_path or get_default_db_path())
    
    # Ensure parent directory exists for file-based databases
    if isinstance(target, Path):
        target.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(target), timeout=timeout)
    conn.row_factory = sqlite3.Row
    
    try:
        # Enforce foreign key constraints
        if enforce_foreign_keys:
            conn.execute("PRAGMA foreign_keys = ON;")
        
        # Configure WAL mode & concurrency pragmas (not applicable for in-memory DB)
        if enable_wal and str(target) != ":memory:":
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
            conn.execute("PRAGMA busy_timeout = 5000;")
        
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


@contextmanager
def get_db_cursor(
    db_path: str | Path | None = None,
) -> Generator[sqlite3.Cursor, None, None]:
    """Context manager yielding a cursor from a managed connection."""
    with get_db_connection(db_path=db_path) as conn:
        cursor = conn.cursor()
        try:
            yield cursor
        finally:
            cursor.close()


def row_to_dict(row: sqlite3.Row | None) -> dict[str, Any] | None:
    """Helper to convert sqlite3.Row into a standard Python dictionary."""
    if row is None:
        return None
    return dict(row)


def rows_to_dicts(rows: Sequence[sqlite3.Row]) -> list[dict[str, Any]]:
    """Helper to convert a sequence of sqlite3.Row objects into dictionaries."""
    return [dict(r) for r in rows]


class DatabaseManager:
    """Production database manager for NexusFleet."""

    def __init__(self, db_path: str | Path | None = None):
        self.db_path = Path(db_path) if db_path and str(db_path) != ":memory:" else (db_path or get_default_db_path())

    @contextmanager
    def connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager yielding an active connection."""
        with get_db_connection(db_path=self.db_path) as conn:
            yield conn

    @contextmanager
    def cursor(self) -> Generator[sqlite3.Cursor, None, None]:
        """Context manager yielding a cursor."""
        with get_db_cursor(db_path=self.db_path) as cur:
            yield cur

    def init_db(self) -> None:
        """Initialize database schema tables and indexes."""
        init_db(self.db_path)

    def seed_data(self) -> dict[str, int]:
        """Seed initial nodes and tasks."""
        return seed_data(self.db_path)

    def reset_db(self) -> None:
        """Reset database tables (drop & recreate)."""
        reset_db(self.db_path)


def init_db(db_path: str | Path | None = None) -> None:
    """
    Initialize SQLite schema for NexusFleet.
    Creates:
    - 'nodes' table: id, name, role, status, ip_address, created_at
    - 'tasks' table: id, node_id, title, command, risk_score, status, result, created_at
    - Indexes for optimal query performance
    """
    with get_db_connection(db_path=db_path) as conn:
        cursor = conn.cursor()
        
        # Create 'nodes' table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS nodes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                role TEXT NOT NULL,
                status TEXT NOT NULL,
                ip_address TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc'))
            );
            """
        )
        
        # Create 'tasks' table with foreign key reference to nodes(id)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                node_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                command TEXT NOT NULL,
                risk_score REAL NOT NULL,
                status TEXT NOT NULL,
                result TEXT,
                created_at TEXT NOT NULL DEFAULT (datetime('now', 'utc')),
                FOREIGN KEY (node_id) REFERENCES nodes (id) ON DELETE CASCADE
            );
            """
        )
        
        # Indexes for query optimization
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_nodes_status ON nodes (status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_node_id ON tasks (node_id);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tasks_risk_score ON tasks (risk_score);")


def reset_db(db_path: str | Path | None = None) -> None:
    """Drop and recreate all tables."""
    with get_db_connection(db_path=db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS tasks;")
        cursor.execute("DROP TABLE IF EXISTS nodes;")
    init_db(db_path=db_path)


# ---------------------------------------------------------------------------
# Seed Data
# ---------------------------------------------------------------------------

SEED_NODES = [
    {
        "name": "nexus-core-01",
        "role": "coordinator",
        "status": "online",
        "ip_address": "10.0.0.10",
    },
    {
        "name": "nexus-worker-01",
        "role": "worker",
        "status": "busy",
        "ip_address": "10.0.0.21",
    },
    {
        "name": "nexus-edge-01",
        "role": "gateway",
        "status": "idle",
        "ip_address": "10.0.0.32",
    },
]

SEED_TASKS = [
    {
        "node_name": "nexus-core-01",
        "title": "Fleet Consensus & Liveness Verification",
        "command": "nexusctl cluster verify --consensus-quorum 3 --timeout 15s",
        "risk_score": 0.12,
        "status": "completed",
        "result": "Consensus verified across all 3 nodes. Raft leader is nexus-core-01.",
    },
    {
        "node_name": "nexus-worker-01",
        "title": "Model Shard Rebalance & Cache Warm",
        "command": "python -m nexus.runtime.rebalance --target-tier hot --shards 8",
        "risk_score": 0.48,
        "status": "running",
        "result": None,
    },
    {
        "node_name": "nexus-worker-01",
        "title": "Distributed Stress Pipeline Benchmarking",
        "command": "pytest tests/stress/test_throughput.py -n 4 --benchmark-only",
        "risk_score": 0.65,
        "status": "pending",
        "result": None,
    },
    {
        "node_name": "nexus-edge-01",
        "title": "Edge Gateway Ingress ACL Sync",
        "command": "iptables-restore < /etc/nexus/edge_guardrails.v4",
        "risk_score": 0.89,
        "status": "failed",
        "result": "Syntax error in ruleset at line 37: unknown chain 'NEXUS_FILTER'",
    },
]


def seed_data(db_path: str | Path | None = None) -> dict[str, int]:
    """
    Populate database with initial seed data:
    - 3 nodes (nexus-core-01, nexus-worker-01, nexus-edge-01)
    - 4 tasks linked to the corresponding nodes
    
    Idempotent: skips seeding if records already exist.
    Returns:
        dict with counts of added nodes and tasks: {'nodes_added': int, 'tasks_added': int}
    """
    init_db(db_path=db_path)
    
    nodes_added = 0
    tasks_added = 0
    
    with get_db_connection(db_path=db_path) as conn:
        cursor = conn.cursor()
        
        # Check current count to preserve idempotency
        cursor.execute("SELECT COUNT(*) FROM nodes")
        existing_nodes = cursor.fetchone()[0]
        
        if existing_nodes == 0:
            for node in SEED_NODES:
                cursor.execute(
                    """
                    INSERT INTO nodes (name, role, status, ip_address)
                    VALUES (?, ?, ?, ?)
                    """,
                    (node["name"], node["role"], node["status"], node["ip_address"]),
                )
                nodes_added += 1
        
        # Map node names to their generated database IDs
        cursor.execute("SELECT id, name FROM nodes")
        node_map = {row["name"]: row["id"] for row in cursor.fetchall()}
        
        cursor.execute("SELECT COUNT(*) FROM tasks")
        existing_tasks = cursor.fetchone()[0]
        
        if existing_tasks == 0:
            for task in SEED_TASKS:
                node_id = node_map.get(task["node_name"])
                if node_id is None:
                    continue
                cursor.execute(
                    """
                    INSERT INTO tasks (node_id, title, command, risk_score, status, result)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        node_id,
                        task["title"],
                        task["command"],
                        task["risk_score"],
                        task["status"],
                        task["result"],
                    ),
                )
                tasks_added += 1
                
    return {"nodes_added": nodes_added, "tasks_added": tasks_added}


# ---------------------------------------------------------------------------
# Node CRUD Helpers
# ---------------------------------------------------------------------------

def get_nodes(db_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Retrieve all nodes ordered by ID."""
    with get_db_connection(db_path=db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM nodes ORDER BY id ASC")
        return rows_to_dicts(cursor.fetchall())


def get_node_by_id(node_id: int, db_path: str | Path | None = None) -> dict[str, Any] | None:
    """Retrieve a single node by its primary key."""
    with get_db_connection(db_path=db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM nodes WHERE id = ?", (node_id,))
        return row_to_dict(cursor.fetchone())


def get_node_by_name(name: str, db_path: str | Path | None = None) -> dict[str, Any] | None:
    """Retrieve a node by its unique name."""
    with get_db_connection(db_path=db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM nodes WHERE name = ?", (name,))
        return row_to_dict(cursor.fetchone())


def create_node(
    name: str,
    role: str,
    status: str,
    ip_address: str,
    db_path: str | Path | None = None,
) -> int:
    """Insert a new node record and return its primary key ID."""
    with get_db_connection(db_path=db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO nodes (name, role, status, ip_address)
            VALUES (?, ?, ?, ?)
            """,
            (name, role, status, ip_address),
        )
        return cursor.lastrowid  # type: ignore[return-value]


def update_node_status(node_id: int, status: str, db_path: str | Path | None = None) -> bool:
    """Update node status. Returns True if row was updated."""
    with get_db_connection(db_path=db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE nodes SET status = ? WHERE id = ?", (status, node_id))
        return cursor.rowcount > 0


# ---------------------------------------------------------------------------
# Task CRUD Helpers
# ---------------------------------------------------------------------------

def get_tasks(db_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Retrieve all tasks ordered by ID."""
    with get_db_connection(db_path=db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks ORDER BY id ASC")
        return rows_to_dicts(cursor.fetchall())


def get_task_by_id(task_id: int, db_path: str | Path | None = None) -> dict[str, Any] | None:
    """Retrieve a single task by its primary key."""
    with get_db_connection(db_path=db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        return row_to_dict(cursor.fetchone())


def get_tasks_by_node(node_id: int, db_path: str | Path | None = None) -> list[dict[str, Any]]:
    """Retrieve all tasks associated with a specific node."""
    with get_db_connection(db_path=db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE node_id = ? ORDER BY id ASC", (node_id,))
        return rows_to_dicts(cursor.fetchall())


def create_task(
    node_id: int,
    title: str,
    command: str,
    risk_score: float,
    status: str,
    result: str | None = None,
    db_path: str | Path | None = None,
) -> int:
    """Insert a new task associated with an existing node."""
    with get_db_connection(db_path=db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO tasks (node_id, title, command, risk_score, status, result)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (node_id, title, command, risk_score, status, result),
        )
        return cursor.lastrowid  # type: ignore[return-value]


def update_task_status(
    task_id: int,
    status: str,
    result: str | None = None,
    db_path: str | Path | None = None,
) -> bool:
    """Update status and optionally result of an existing task."""
    with get_db_connection(db_path=db_path) as conn:
        cursor = conn.cursor()
        if result is not None:
            cursor.execute(
                "UPDATE tasks SET status = ?, result = ? WHERE id = ?",
                (status, result, task_id),
            )
        else:
            cursor.execute(
                "UPDATE tasks SET status = ? WHERE id = ?",
                (status, task_id),
            )
        return cursor.rowcount > 0


def delete_task(task_id: int, db_path: str | Path | None = None) -> bool:
    """Delete a task by its primary key ID. Returns True if row was deleted."""
    with get_db_connection(db_path=db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        return cursor.rowcount > 0


def update_task_fields(
    task_id: int,
    updates: dict[str, Any],
    db_path: str | Path | None = None,
) -> bool:
    """
    Dynamically update fields of a task (title, command, risk_score, status, result, node_id).
    Returns True if row was updated.
    """
    allowed_fields = {"title", "command", "risk_score", "status", "result", "node_id"}
    filtered_updates = {k: v for k, v in updates.items() if k in allowed_fields}
    if not filtered_updates:
        return False

    set_clause = ", ".join(f"{col} = ?" for col in filtered_updates.keys())
    values = list(filtered_updates.values()) + [task_id]

    with get_db_connection(db_path=db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(f"UPDATE tasks SET {set_clause} WHERE id = ?", values)
        return cursor.rowcount > 0


def delete_node(node_id: int, db_path: str | Path | None = None) -> bool:
    """Delete a node by its primary key ID (cascades to tasks). Returns True if row was deleted."""
    with get_db_connection(db_path=db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM nodes WHERE id = ?", (node_id,))
        return cursor.rowcount > 0


# ---------------------------------------------------------------------------
# Diagnostics & CLI Execution
# ---------------------------------------------------------------------------

def inspect_db_state(db_path: str | Path | None = None) -> dict[str, Any]:
    """Inspect SQLite pragmas and row counts."""
    with get_db_connection(db_path=db_path) as conn:
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA journal_mode;")
        journal_mode = cursor.fetchone()[0]
        
        cursor.execute("PRAGMA foreign_keys;")
        foreign_keys = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM nodes;")
        node_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tasks;")
        task_count = cursor.fetchone()[0]
        
        return {
            "journal_mode": journal_mode,
            "foreign_keys_enabled": bool(foreign_keys),
            "node_count": node_count,
            "task_count": task_count,
        }


if __name__ == "__main__":
    db_file = get_default_db_path()
    print(f"[*] Initializing NexusFleet database at: {db_file}")
    init_db()
    
    print("[*] Seeding initial data (3 nodes, 4 tasks)...")
    res = seed_data()
    print(f"[*] Seed result: {res}")
    
    state = inspect_db_state()
    print(f"[*] Database State: Journal Mode = {state['journal_mode']}, Foreign Keys = {state['foreign_keys_enabled']}")
    print(f"[*] Total Nodes: {state['node_count']}, Total Tasks: {state['task_count']}")
    
    print("\n[Nodes]:")
    for n in get_nodes():
        print(f"  - [{n['id']}] {n['name']} ({n['role']}) | Status: {n['status']} | IP: {n['ip_address']}")
        
    print("\n[Tasks]:")
    for t in get_tasks():
        print(f"  - [{t['id']}] Node #{t['node_id']} | Risk: {t['risk_score']} | Status: {t['status']} | Title: {t['title']}")
