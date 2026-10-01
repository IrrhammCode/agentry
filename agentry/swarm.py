"""
Multi-Agent Swarm Deadlock & Ping-Pong Loop Detector for Agentry.
Models fleet interaction as a directed delegation graph across collaborating agents
(e.g., in CrewAI, AutoGen, or LangGraph multi-agent teams).
Detects circular delegation cycles (Ping-Pong loops A -> B -> A -> B, and N-agent cyclic deadlocks)
that burn excessive API budget without achieving forward progress.
"""

import time
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional, Set

logger = logging.getLogger("agentry.swarm")


@dataclass
class SwarmDeadlockAlert:
    """Alert raised when multi-agent collaboration enters an unproductive cycle."""
    is_deadlocked: bool
    session_id: str
    cycle_agents: List[str]
    cycle_length: int
    cycle_repeat_count: int
    total_delegation_hops: int
    recommendation: str
    timestamp: float = field(default_factory=time.time)


class SwarmDeadlockDetector:
    """
    Tracks agent-to-agent delegation chains within a collaborative session.
    Detects directed graph cycles using sequence repetition analysis.
    """

    def __init__(self, cycle_repeat_threshold: int = 2):
        self.cycle_repeat_threshold = cycle_repeat_threshold
        # session_id -> List[Tuple[from_agent, to_agent, timestamp, task_snippet]]
        self._delegation_history: Dict[str, List[Tuple[str, str, float, str]]] = {}

    def record_transfer(
        self,
        session_id: str,
        from_agent: str,
        to_agent: str,
        task_snippet: str = ""
    ) -> Optional[SwarmDeadlockAlert]:
        """
        Records a delegation transfer from one agent to another and evaluates
        whether the fleet has entered a circular deadlock.
        """
        from_ag = (from_agent or "agent").strip()
        to_ag = (to_agent or "agent").strip()
        now = time.time()

        if session_id not in self._delegation_history:
            self._delegation_history[session_id] = []

        history = self._delegation_history[session_id]
        history.append((from_ag, to_ag, now, str(task_snippet)[:150]))

        # We need at least 4 hops to detect a repeating cycle (e.g. A->B->A->B)
        if len(history) < 4:
            return None

        # Build list of agent transitions
        agents_sequence: List[str] = [h[0] for h in history] + [history[-1][1]]

        # Search for repeating sub-cycles of length 2 to 5
        for cycle_len in range(2, min(6, len(agents_sequence) // 2 + 1)):
            recent_pattern = agents_sequence[-cycle_len:]
            # Check if recent_pattern repeated cycle_repeat_threshold times
            needed_hops = cycle_len * self.cycle_repeat_threshold
            if len(agents_sequence) >= needed_hops:
                window = agents_sequence[-needed_hops:]
                expected = recent_pattern * self.cycle_repeat_threshold
                if window == expected:
                    # Circular deadlock confirmed!
                    alert = SwarmDeadlockAlert(
                        is_deadlocked=True,
                        session_id=session_id,
                        cycle_agents=recent_pattern,
                        cycle_length=cycle_len,
                        cycle_repeat_count=self.cycle_repeat_threshold,
                        total_delegation_hops=len(history),
                        recommendation=(
                            f"SWARM DEADLOCK INTERCEPTION: Circular delegation cycle detected "
                            f"({' -> '.join(recent_pattern)} -> {recent_pattern[0]}). "
                            f"Halted ping-pong loop after {len(history)} total delegations."
                        )
                    )
                    logger.critical(
                        "Swarm deadlock detected in session '%s': %s (cycle length: %d)",
                        session_id, " -> ".join(recent_pattern), cycle_len
                    )
                    return alert

        return None

    def get_session_hops(self, session_id: str) -> int:
        """Returns total delegation hops recorded for session."""
        return len(self._delegation_history.get(session_id, []))

    # Alias for API uniformity
    record_delegation = record_transfer

    def reset_session(self, session_id: str):
        """Clears delegation tracking for a completed session."""
        if session_id in self._delegation_history:
            del self._delegation_history[session_id]



# Global singleton instance
swarm_detector = SwarmDeadlockDetector()
swarm_deadlock_detector = swarm_detector

