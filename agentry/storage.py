"""
Persistent Telemetry & Audit Storage for Agentry.
Provides ACID-compliant SQLite WAL-mode audit logging for enterprise governance,
incident forensics, compliance reporting, and historical telemetry replay.
"""

import sqlite3
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional

from agentry.config import ROOT_DIR
from agentry.agent import SentryDecision

DB_PATH = ROOT_DIR / "data" / "agentry_audit.db"


class AuditStorage:
    """
    SQLite-backed audit storage for recording all Sentry decisions,
    TabPFN risk probabilities, and agent intervention events.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = Path(db_path) if db_path else DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path), timeout=10.0)
        conn.row_factory = sqlite3.Row
        # Enable Write-Ahead Logging (WAL) for high concurrency
        conn.execute("PRAGMA journal_mode=WAL;")
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    step_index INTEGER NOT NULL,
                    timestamp REAL NOT NULL,
                    action TEXT NOT NULL,
                    risk_level TEXT NOT NULL,
                    failure_probability REAL NOT NULL,
                    predicted_failure_mode TEXT NOT NULL,
                    projected_final_cost_usd REAL NOT NULL,
                    confidence REAL NOT NULL,
                    reason TEXT NOT NULL,
                    reroute_instruction TEXT,
                    estimated_tokens_saved INTEGER NOT NULL,
                    estimated_cost_saved_usd REAL NOT NULL,
                    sentry_provider TEXT NOT NULL
                );
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_session
                ON audit_events(session_id, step_index);
            """)

    def record_decision(self, decision: SentryDecision) -> int:
        """Persists a single SentryDecision to the audit database."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                INSERT INTO audit_events (
                    session_id,
                    step_index,
                    timestamp,
                    action,
                    risk_level,
                    failure_probability,
                    predicted_failure_mode,
                    projected_final_cost_usd,
                    confidence,
                    reason,
                    reroute_instruction,
                    estimated_tokens_saved,
                    estimated_cost_saved_usd,
                    sentry_provider
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                decision.session_id,
                decision.step_index,
                time.time(),
                decision.action,
                decision.risk_level,
                decision.tabpfn_assessment.failure_probability,
                decision.tabpfn_assessment.predicted_failure_mode,
                decision.tabpfn_assessment.projected_final_cost_usd,
                decision.confidence,
                decision.reason,
                decision.reroute_instruction or "",
                decision.estimated_tokens_saved,
                decision.estimated_cost_saved_usd,
                decision.sentry_provider
            ))
            return cursor.lastrowid

    def get_session_events(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieves all recorded audit events for a session ordered by step."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM audit_events WHERE session_id = ? ORDER BY step_index ASC",
                (session_id,)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_all_events(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieves most recent audit events across all sessions."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM audit_events ORDER BY id DESC LIMIT ?",
                (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_fleet_summary(self) -> Dict[str, Any]:
        """Calculates fleet-wide governance and intervention metrics."""
        with self._get_connection() as conn:
            total_steps = conn.execute("SELECT COUNT(*) FROM audit_events").fetchone()[0]
            kills = conn.execute("SELECT COUNT(*) FROM audit_events WHERE action = 'KILL'").fetchone()[0]
            reroutes = conn.execute("SELECT COUNT(*) FROM audit_events WHERE action = 'REROUTE'").fetchone()[0]
            pauses = conn.execute("SELECT COUNT(*) FROM audit_events WHERE action = 'PAUSE'").fetchone()[0]
            passes = conn.execute("SELECT COUNT(*) FROM audit_events WHERE action = 'PASS'").fetchone()[0]
            
            savings = conn.execute("""
                SELECT 
                    COALESCE(SUM(estimated_tokens_saved), 0),
                    COALESCE(SUM(estimated_cost_saved_usd), 0.0)
                FROM audit_events
            """).fetchone()
            
            unique_sessions = conn.execute("SELECT COUNT(DISTINCT session_id) FROM audit_events").fetchone()[0]

            return {
                "total_audited_steps": total_steps,
                "unique_sessions": unique_sessions,
                "interventions": {
                    "KILL": kills,
                    "REROUTE": reroutes,
                    "PAUSE": pauses,
                    "PASS": passes,
                },
                "total_tokens_saved": int(savings[0]),
                "total_cost_saved_usd": round(float(savings[1]), 4)
            }

    def clear(self):
        """Clears the audit database (used in testing)."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM audit_events;")
