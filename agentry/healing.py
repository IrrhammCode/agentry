"""
Autonomic Trajectory Rewind & Self-Healing Engine for Agentry.
Allows trapped or looping agents to roll back their execution state to the last
known healthy checkpoint, prune poisoned conversation context, and inject
TabPFN-guided counterfactual steering directives to achieve task completion.
"""

import time
import logging
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional

from agentry.storage import AuditStorage

logger = logging.getLogger("agentry.healing")


@dataclass
class RewindPrescription:
    """Actionable prescription for rolling back and self-healing an agent trajectory."""
    session_id: str
    current_step: int
    target_step: int
    pruned_steps_count: int
    trigger_reason: str
    failed_tool: str
    counterfactual_directive: str
    estimated_tokens_saved: int
    estimated_cost_saved_usd: float
    created_at: float = time.time()


class TrajectoryHealer:
    """
    Computes trajectory divergence inflection points and generates self-healing
    pruning recipes for autonomous agent recovery.
    """

    def __init__(self, storage: Optional[AuditStorage] = None):
        self.storage = storage or AuditStorage()

    def find_inflection_point(self, session_events: List[Dict[str, Any]]) -> int:
        """
        Scans historical steps in reverse to identify the divergence inflection point:
        the last known step where the agent had 0 error streak, nominal repetition,
        and was operating safely.
        """
        if not session_events:
            return 0

        # Traverse backwards from the step before current
        for event in reversed(session_events[:-1]):
            action = event.get("action", "PASS")
            risk_prob = float(event.get("failure_probability", 0.0))
            if action == "PASS" and risk_prob < 0.40:
                return max(0, int(event.get("step_index", 0)))

        # Fallback: rollback at least 3 steps or to step 0
        current_step = int(session_events[-1].get("step_index", len(session_events) - 1))
        return max(0, current_step - 3)

    def diagnose_and_prescribe(
        self,
        session_id: str,
        current_step: int,
        failed_tool: str = "tool",
        error_streak: int = 1,
        reason: str = "Repetitive failure loop detected",
        storage: Optional[AuditStorage] = None
    ) -> RewindPrescription:
        """
        Diagnoses an agent trajectory failure and synthesizes an actionable
        RewindPrescription with counterfactual steering directives.
        """
        store = storage or self.storage
        events = store.get_session_events(session_id)
        target_step = self.find_inflection_point(events)
        pruned_count = max(1, current_step - target_step)

        # Token savings: ~1,800 tokens per poisoned step pruned
        tokens_saved = pruned_count * 1800
        cost_saved = round((tokens_saved / 1000.0) * 0.002, 4)

        directive = (
            f"SYSTEM RECOVERY DIRECTIVE: Autonomic self-healing engaged. "
            f"Your trajectory diverged into an error loop at step {target_step + 1} "
            f"attempting '{failed_tool}' ({error_streak} consecutive errors). "
            f"We have rolled back your execution context to step {target_step}. "
            f"DO NOT repeat '{failed_tool}'. Adopt an alternative tool or strategy immediately."
        )

        prescription = RewindPrescription(
            session_id=session_id,
            current_step=current_step,
            target_step=target_step,
            pruned_steps_count=pruned_count,
            trigger_reason=reason,
            failed_tool=failed_tool,
            counterfactual_directive=directive,
            estimated_tokens_saved=tokens_saved,
            estimated_cost_saved_usd=cost_saved
        )
        logger.info(
            "Synthesized RewindPrescription for '%s': step %d -> %d (pruned %d steps, saved %d tokens)",
            session_id, current_step, target_step, pruned_count, tokens_saved
        )
        return prescription

    @staticmethod
    def prune_conversation(
        messages: List[Dict[str, Any]],
        target_step: int,
        directive: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Prunes poisoned turns from an OpenAI-compatible message history back
        to target_step and injects the counterfactual steering directive.
        """
        if not messages:
            return []

        # Always preserve system prompt (first message if system)
        has_system = messages[0].get("role") == "system"
        system_msg = [messages[0]] if has_system else []
        conversation_turns = messages[1:] if has_system else messages

        # Each user-assistant-tool exchange is roughly 2-3 messages
        keep_count = max(1, target_step * 2)
        pruned_turns = conversation_turns[:keep_count]

        result = list(system_msg) + list(pruned_turns)

        # Inject corrective directive as high-priority system steering message
        if directive:
            result.append({
                "role": "system",
                "content": directive
            })

        return result


# Global singleton healer instance
trajectory_healer = TrajectoryHealer()
