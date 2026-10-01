"""
Real-Time Webhook Alerting for Agentry.
Dispatches instant incident alerts to Slack, Discord, or generic Webhooks
when autonomous circuit breakers trip (KILL, PAUSE, REROUTE).
"""

import os
import time
import json
import logging
import threading
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any
import httpx

from agentry.agent import SentryDecision
from agentry.config import settings

logger = logging.getLogger("agentry.alerts")


@dataclass
class WebhookAlertPayload:
    event_type: str  # "circuit_breaker_kill", "human_escalation_pause", "steering_reroute"
    session_id: str
    step_index: int
    action: str
    risk_level: str
    failure_probability: float
    predicted_failure_mode: str
    reason: str
    reroute_instruction: Optional[str]
    tokens_saved: int
    cost_saved_usd: float
    timestamp: float = time.time()


class WebhookNotifier:
    """
    Non-blocking webhook dispatcher for enterprise AI Agent incident alerting.
    Auto-detects Slack, Discord, or generic Webhook endpoints.
    """

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url or os.getenv("AGENTRY_WEBHOOK_URL", os.getenv("SLACK_WEBHOOK_URL", ""))
        self.enabled = bool(self.webhook_url.strip())

    def send_alert(self, decision: SentryDecision, background: bool = True):
        """
        Dispatches an incident alert for a SentryDecision.
        By default runs in a detached daemon thread to prevent latency overhead on agent tool turns.
        """
        if not self.enabled or decision.action not in ("KILL", "PAUSE", "REROUTE"):
            return

        event_type = {
            "KILL": "circuit_breaker_kill",
            "PAUSE": "human_escalation_pause",
            "REROUTE": "steering_reroute"
        }.get(decision.action, "circuit_breaker_alert")

        payload = WebhookAlertPayload(
            event_type=event_type,
            session_id=decision.session_id,
            step_index=decision.step_index,
            action=decision.action,
            risk_level=decision.risk_level,
            failure_probability=decision.tabpfn_assessment.failure_probability,
            predicted_failure_mode=decision.tabpfn_assessment.predicted_failure_mode,
            reason=decision.reason,
            reroute_instruction=decision.reroute_instruction,
            tokens_saved=decision.estimated_tokens_saved,
            cost_saved_usd=decision.estimated_cost_saved_usd
        )

        if background:
            t = threading.Thread(target=self._dispatch_sync, args=(payload,), daemon=True)
            t.start()
        else:
            self._dispatch_sync(payload)

    def _to_payload(self, item: Any) -> WebhookAlertPayload:
        if isinstance(item, WebhookAlertPayload):
            return item
        if isinstance(item, SentryDecision):
            event_type = {
                "KILL": "circuit_breaker_kill",
                "PAUSE": "human_escalation_pause",
                "REROUTE": "steering_reroute"
            }.get(item.action, "circuit_breaker_alert")
            return WebhookAlertPayload(
                event_type=event_type,
                session_id=item.session_id,
                step_index=item.step_index,
                action=item.action,
                risk_level=item.risk_level,
                failure_probability=item.tabpfn_assessment.failure_probability,
                predicted_failure_mode=item.tabpfn_assessment.predicted_failure_mode,
                reason=item.reason,
                reroute_instruction=item.reroute_instruction,
                tokens_saved=item.estimated_tokens_saved,
                cost_saved_usd=item.estimated_cost_saved_usd,
                timestamp=time.time()
            )
        raise TypeError(f"Expected WebhookAlertPayload or SentryDecision, got {type(item)}")

    def _dispatch_sync(self, alert: Any):
        """Executes the HTTP POST request to the webhook URL."""
        if not self.webhook_url:
            return

        payload = self._to_payload(alert)
        url = self.webhook_url.lower()
        if "slack.com" in url:
            body = self._build_slack_payload(payload)
        elif "discord.com" in url:
            body = self._build_discord_payload(payload)
        else:
            body = self._build_generic_payload(payload)

        try:
            with httpx.Client(timeout=4.0) as client:
                res = client.post(self.webhook_url, json=body)
                if res.status_code >= 400:
                    logger.warning("Webhook alert failed with HTTP %d: %s", res.status_code, res.text[:100])
                return True
        except Exception as exc:
            logger.warning("Webhook alert dispatch error: %s", exc)
            return False

    def _build_slack_payload(self, alert: Any) -> Dict[str, Any]:
        """Constructs rich Slack Block Kit message."""
        p = self._to_payload(alert)
        emoji = "🛑" if p.action == "KILL" else ("⚠️" if p.action == "PAUSE" else "🔄")
        header = f"{emoji} [Agentry Alert] Agent {p.action} Intervention Triggered"
        
        fields = [
            {"type": "mrkdwn", "text": f"*Session:*\n`{p.session_id}` (Step {p.step_index})"},
            {"type": "mrkdwn", "text": f"*Failure Mode:*\n`{p.predicted_failure_mode}` ({p.failure_probability*100:.1f}%)"},
            {"type": "mrkdwn", "text": f"*Tokens Saved:*\n~{p.tokens_saved:,}"},
            {"type": "mrkdwn", "text": f"*Budget Saved:*\n~${p.cost_saved_usd:.4f} USD"},
        ]

        blocks = [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": header, "emoji": True}
            },
            {
                "type": "section",
                "fields": fields
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Forensic Reason:*\n{p.reason}"}
            }
        ]
        if p.reroute_instruction:
            blocks.append({
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Steering Directive:*\n`{p.reroute_instruction}`"}
            })

        return {"text": header, "blocks": blocks}

    def _build_discord_payload(self, alert: Any) -> Dict[str, Any]:
        """Constructs rich Discord Embed."""
        p = self._to_payload(alert)
        color = 0xEF4444 if p.action == "KILL" else (0xF59E0B if p.action == "PAUSE" else 0x3B82F6)
        embed = {
            "title": f"🛡️ Agentry Alert: {p.action} on `{p.session_id}`",
            "description": p.reason,
            "color": color,
            "fields": [
                {"name": "Step Index", "value": str(p.step_index), "inline": True},
                {"name": "Predicted Mode", "value": p.predicted_failure_mode, "inline": True},
                {"name": "TabPFN Risk", "value": f"{p.failure_probability*100:.1f}%", "inline": True},
                {"name": "Tokens Saved", "value": f"{p.tokens_saved:,}", "inline": True},
                {"name": "Cost Saved", "value": f"${p.cost_saved_usd:.4f}", "inline": True},
            ],
            "footer": {"text": "Agentry Prior Labs TabPFN-3.5 Governance"}
        }
        if p.reroute_instruction:
            embed["fields"].append({"name": "Steering Directive", "value": p.reroute_instruction, "inline": False})
        return {"embeds": [embed]}

    def _build_generic_payload(self, alert: Any) -> Dict[str, Any]:
        """Constructs standardized JSON webhook payload."""
        p = self._to_payload(alert)
        return {
            "event_type": "agentry.circuit_breaker.intervention",
            "timestamp": time.time(),
            "decision": asdict(p)
        }


# Global notifier singleton
default_notifier = WebhookNotifier()
