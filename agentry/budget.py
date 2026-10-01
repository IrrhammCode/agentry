"""
Fleet Budget Autopilot & Quota Governor for Agentry.
Enforces multi-agent financial governance, dynamic quota allocation,
burn-rate velocity monitoring, and bill-shock prevention using TabPFN cost forecasts.
"""

import time
import logging
from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

from agentry.config import settings
from agentry.storage import AuditStorage

logger = logging.getLogger("agentry.budget")


@dataclass
class BudgetStatus:
    """Real-time financial quota and burn rate status."""
    is_exceeded: bool
    is_warning: bool
    daily_budget_usd: float
    session_budget_usd: float
    current_fleet_spend_usd: float
    projected_day_end_spend_usd: float
    remaining_daily_budget_usd: float
    utilization_pct: float
    action_recommendation: str  # "PROCEED", "WARN", "THROTTLE", "HALT"
    reason: str


class FleetBudgetGovernor:
    """
    Fleet-wide financial control layer.
    Monitors aggregate token expenditure across all agent sessions,
    compares against configured budgets, and recommends autonomic throttling
    or hard halting before budget overruns occur.
    """

    def __init__(
        self,
        daily_budget_usd: Optional[float] = None,
        session_budget_usd: Optional[float] = None,
        warning_threshold_pct: float = 80.0,
        storage: Optional[AuditStorage] = None
    ):
        self.daily_budget_usd = daily_budget_usd or float(settings.cost_threshold_kill_usd * 20.0)  # Default: $50.00
        self.session_budget_usd = session_budget_usd or float(settings.cost_threshold_kill_usd)    # Default: $2.50
        self.warning_threshold_pct = warning_threshold_pct
        self.storage = storage or AuditStorage()

    def check_fleet_budget(self, active_session_projected_delta: float = 0.0) -> BudgetStatus:
        """
        Evaluates current fleet expenditure against daily budget quotas.
        Integrates TabPFN terminal cost projections across active sessions.
        """
        summary = self.storage.get_fleet_summary()
        current_spend = summary.get("total_cost_saved_usd", 0.0)  # Total spend tracked

        # Query actual current spend from SQLite database
        try:
            with self.storage._get_connection() as conn:
                row = conn.execute("""
                    SELECT COALESCE(SUM(projected_final_cost_usd), 0.0)
                    FROM audit_events
                    WHERE timestamp >= ?
                """, (time.time() - 86400,)).fetchone()
                current_spend = float(row[0]) if row else 0.0
        except Exception as e:
            logger.debug("Failed querying daily fleet spend: %s", e)

        projected_total = current_spend + max(0.0, active_session_projected_delta)
        remaining = max(0.0, self.daily_budget_usd - current_spend)
        utilization = (current_spend / max(0.001, self.daily_budget_usd)) * 100.0

        is_exceeded = current_spend >= self.daily_budget_usd
        is_warning = utilization >= self.warning_threshold_pct

        if is_exceeded:
            rec = "HALT"
            reason = f"Daily fleet budget of ${self.daily_budget_usd:.2f} USD completely exhausted (${current_spend:.2f} spent)."
        elif is_warning:
            rec = "WARN" if utilization < 95.0 else "THROTTLE"
            reason = f"Fleet spend reached {utilization:.1f}% of daily ceiling (${current_spend:.2f}/${self.daily_budget_usd:.2f} USD)."
        else:
            rec = "PROCEED"
            reason = f"Budget nominal. Utilization at {utilization:.1f}% (${remaining:.2f} USD remaining)."

        return BudgetStatus(
            is_exceeded=is_exceeded,
            is_warning=is_warning,
            daily_budget_usd=self.daily_budget_usd,
            session_budget_usd=self.session_budget_usd,
            current_fleet_spend_usd=round(current_spend, 4),
            projected_day_end_spend_usd=round(projected_total, 4),
            remaining_daily_budget_usd=round(remaining, 4),
            utilization_pct=round(utilization, 1),
            action_recommendation=rec,
            reason=reason
        )

    def check_session_budget(self, session_id: str, accumulated_cost: float) -> BudgetStatus:
        """Evaluates an individual agent session against single-task quota."""
        utilization = (accumulated_cost / max(0.001, self.session_budget_usd)) * 100.0
        is_exceeded = accumulated_cost >= self.session_budget_usd
        is_warning = utilization >= self.warning_threshold_pct

        if is_exceeded:
            rec = "HALT"
            reason = f"Session '{session_id}' exceeded budget cap of ${self.session_budget_usd:.2f} USD (spent ${accumulated_cost:.4f})."
        elif is_warning:
            rec = "THROTTLE"
            reason = f"Session '{session_id}' at {utilization:.1f}% of cost budget."
        else:
            rec = "PROCEED"
            reason = f"Session cost nominal (${accumulated_cost:.4f}/${self.session_budget_usd:.2f})."

        return BudgetStatus(
            is_exceeded=is_exceeded,
            is_warning=is_warning,
            daily_budget_usd=self.daily_budget_usd,
            session_budget_usd=self.session_budget_usd,
            current_fleet_spend_usd=round(accumulated_cost, 4),
            projected_day_end_spend_usd=round(accumulated_cost, 4),
            remaining_daily_budget_usd=round(max(0.0, self.session_budget_usd - accumulated_cost), 4),
            utilization_pct=round(utilization, 1),
            action_recommendation=rec,
            reason=reason
        )


# Global singleton governor
budget_governor = FleetBudgetGovernor()
