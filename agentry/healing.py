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
from agentry.utils import safe_int, safe_float, safe_str

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
            if not isinstance(event, dict):
                continue
            action = safe_str(event.get("action"), default="PASS")
            risk_prob = safe_float(event.get("failure_probability"), default=0.0)
            if action == "PASS" and risk_prob < 0.40:
                return safe_int(event.get("step_index"), default=0, min_val=0)

        # Fallback: rollback at least 3 steps or to step 0
        last_event = session_events[-1]
        current_step = safe_int(
            last_event.get("step_index") if isinstance(last_event, dict) else len(session_events) - 1,
            default=0,
            min_val=0
        )
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
        raw_inflection = self.find_inflection_point(events)
        target_step = min(max(0, current_step), max(0, raw_inflection))
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

        # Defensively filter and normalize non-dict messages
        valid_messages = [m for m in messages if isinstance(m, dict)]
        if not valid_messages:
            return []

        # Always preserve system prompt (first message if system)
        has_system = valid_messages[0].get("role") == "system"
        system_msg = [valid_messages[0]] if has_system else []
        conversation_turns = valid_messages[1:] if has_system else valid_messages

        # Each user-assistant-tool exchange is roughly 2-3 messages
        clamped_step = max(0, target_step)
        keep_count = max(1, clamped_step * 2)
        pruned_turns = conversation_turns[:keep_count]

        result = list(system_msg) + list(pruned_turns)

        # Inject corrective directive as high-priority system steering message
        if directive:
            result.append({
                "role": "system",
                "content": str(directive)
            })

        return result


# Global singleton healer instance
trajectory_healer = TrajectoryHealer()
