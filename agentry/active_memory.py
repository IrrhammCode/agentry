"""
Active In-Context Learning Exemplar Buffer for TabPFN Guardrail.
Captures verified operational incidents, human operator resolutions (HITL),
and autonomic healing events in real-time.
Feeds these continuous dynamic exemplars into TabPFN's In-Context prompt buffer
allowing the foundation model to continuously adapt to enterprise-specific agent
behavior WITHOUT requiring slow offline model retraining.
"""

import json
import time
import logging
import threading
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

import pandas as pd
from agentry.config import ROOT_DIR

logger = logging.getLogger("agentry.active_memory")

EXEMPLARS_FILE = ROOT_DIR / "data" / "active_exemplars.jsonl"


@dataclass
class VerifiedIncidentExemplar:
    """A verified agent incident or resolution exemplar for In-Context Learning."""
    session_id: str
    step_index: int
    tool_name: str
    step_latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    tool_call_count: int
    error_streak: int
    repetition_score: float
    thought_length: int
    accumulated_cost_usd: float
    failure_status: str
    is_failure: int
    resolution_source: str  # 'HITL_OPERATOR', 'AUTONOMIC_REWIND', 'SENTRY_CORRECTION'
    timestamp: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if not d.get("timestamp"):
            d["timestamp"] = time.time()
        return d


class ActiveExemplarBuffer:
    """
    Thread-safe sliding window buffer of confirmed incident exemplars.
    Persists to JSONL and provides dynamic training slices for TabPFN.
    """

    def __init__(self, max_size: int = 500, storage_file: Optional[Path] = None):
        self.max_size = max_size
        self.storage_file = storage_file or EXEMPLARS_FILE
        self.storage_file.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.RLock()
        self._buffer: List[VerifiedIncidentExemplar] = []
        self._load_persisted_exemplars()

    def _load_persisted_exemplars(self):
        """Loads previously saved exemplars from disk."""
        if not self.storage_file.exists():
            return
        try:
            with open(self.storage_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        data = json.loads(line)
                        exemplar = VerifiedIncidentExemplar(**data)
                        self._buffer.append(exemplar)
            logger.info("Loaded %d active in-context exemplars from disk", len(self._buffer))
        except Exception as e:
            logger.warning("Failed to load active exemplars: %s", e)

    def record_exemplar(self, exemplar: VerifiedIncidentExemplar):
        """Adds a newly verified exemplar to the active buffer and disk."""
        with self._lock:
            self._buffer.append(exemplar)
            if len(self._buffer) > self.max_size:
                self._buffer.pop(0)

            # Append to file
            try:
                with open(self.storage_file, "a", encoding="utf-8") as f:
                    f.write(json.dumps(exemplar.to_dict()) + "\n")
            except Exception as e:
                logger.error("Failed to append exemplar to disk: %s", e)

        logger.info(
            "Recorded verified exemplar for session '%s' (status: %s, source: %s)",
            exemplar.session_id, exemplar.failure_status, exemplar.resolution_source
        )

    def get_exemplars_df(self) -> Optional[pd.DataFrame]:
        """Returns buffered exemplars as a DataFrame ready for TabPFN in-context augmentation."""
        with self._lock:
            if not self._buffer:
                return None
            return pd.DataFrame([e.to_dict() for e in self._buffer])

    def clear(self):
        """Clears the active exemplar buffer and storage file."""
        with self._lock:
            self._buffer.clear()
            if self.storage_file.exists():
                try:
                    self.storage_file.unlink()
                except Exception:
                    pass


# Global singleton instance
active_exemplar_memory = ActiveExemplarBuffer()
