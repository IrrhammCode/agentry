"""
Human-in-the-Loop (HITL) Approval Gateway for Agentry.
Allows human operators to inspect paused/high-risk agent executions,
review tabular forensic telemetry, and issue Resume, Reroute, or Abort decisions.
"""

import time
import uuid
import threading
import logging
from dataclasses import dataclass, asdict
from typing import Dict, Any, List, Optional

from agentry.agent import SentryDecision

logger = logging.getLogger("agentry.hitl")


@dataclass
class HITLRequest:
    request_id: str
    session_id: str
    step_index: int
    tool_name: str
    action: str  # "PAUSE", "REROUTE", "KILL"
    risk_level: str
    failure_probability: float
    predicted_failure_mode: str
    reason: str
    created_at: float
    status: str  # "PENDING", "APPROVED_RESUME", "REROUTED", "REJECTED_ABORT", "TIMED_OUT"
    operator_comment: Optional[str] = None
    custom_directive: Optional[str] = None
    resolved_at: Optional[float] = None


class HITLManager:
    """
    Thread-safe Human-in-the-Loop (HITL) Escalation Queue.
    Integrates with Streamlit dashboard, MCP server, and REST API daemon.
    """

    def __init__(self):
        self._requests: Dict[str, HITLRequest] = {}
        self._events: Dict[str, threading.Event] = {}
        self._lock = threading.RLock()

    def _prune_old_requests(self):
        """Prunes resolved requests older than 24 hours if queue size exceeds 1,000."""
        if len(self._requests) > 1000:
            cutoff = time.time() - 86400
            stale_keys = [
                k for k, v in self._requests.items()
                if v.status != "PENDING" and (v.resolved_at or v.created_at) < cutoff
            ]
            for k in stale_keys:
                self._requests.pop(k, None)
                self._events.pop(k, None)

    def create_escalation(self, decision: SentryDecision, tool_name: str = "tool") -> HITLRequest:
        """Enqueues an agent step for human review and creates a synchronization event."""
        with self._lock:
            self._prune_old_requests()
            req_id = f"hitl_{uuid.uuid4().hex[:8]}"
            req = HITLRequest(
                request_id=req_id,
                session_id=decision.session_id,
                step_index=decision.step_index,
                tool_name=tool_name,
                action=decision.action,
                risk_level=decision.risk_level,
                failure_probability=decision.tabpfn_assessment.failure_probability,
                predicted_failure_mode=decision.tabpfn_assessment.predicted_failure_mode,
                reason=decision.reason,
                created_at=time.time(),
                status="PENDING"
            )
            self._requests[req_id] = req
            self._events[req_id] = threading.Event()
            logger.info("Created HITL Escalation Request '%s' for session '%s' (Risk: %.1f%%)",
                        req_id, decision.session_id, req.failure_probability * 100)
            return req

    def list_requests(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Returns all escalation requests, optionally filtered by status (e.g. 'PENDING')."""
        with self._lock:
            results = []
            for r in sorted(self._requests.values(), key=lambda x: x.created_at, reverse=True):
                if status is None or r.status.upper() == status.upper():
                    results.append(asdict(r))
            return results

    def resolve(
        self,
        request_id: str,
        resolution: str,  # "RESUME", "REROUTE", "ABORT"
        comment: Optional[str] = None,
        custom_directive: Optional[str] = None
    ) -> Optional[HITLRequest]:
        """Resolves a pending request and unblocks waiting agent threads."""
        with self._lock:
            req = self._requests.get(request_id)
            if not req:
                logger.warning("HITL request '%s' not found for resolution", request_id)
                return None

            resolution_upper = resolution.upper()
            if resolution_upper == "RESUME":
                req.status = "APPROVED_RESUME"
            elif resolution_upper == "REROUTE":
                req.status = "REROUTED"
                req.custom_directive = custom_directive or "OPERATOR OVERRIDE: Change execution trajectory immediately."
            elif resolution_upper in ("ABORT", "KILL"):
                req.status = "REJECTED_ABORT"
            else:
                req.status = f"RESOLVED_{resolution_upper}"

            req.operator_comment = comment
            req.resolved_at = time.time()

            # Signal waiting event if present
            event = self._events.get(request_id)
            if event:
                event.set()

            logger.info("Resolved HITL request '%s' with outcome: %s", request_id, req.status)

            # Record human-verified incident into Active In-Context Memory for TabPFN adaptation
            try:
                from agentry.active_memory import active_exemplar_memory, VerifiedIncidentExemplar
                is_fail = 1 if req.status in ("REROUTED", "REJECTED_ABORT") else 0
                active_exemplar_memory.record_exemplar(VerifiedIncidentExemplar(
                    session_id=req.session_id,
                    step_index=req.step_index,
                    tool_name=req.tool_name,
                    step_latency_ms=850.0,
                    prompt_tokens=1500,
                    completion_tokens=250,
                    total_tokens=1750,
                    tool_call_count=req.step_index + 1,
                    error_streak=2 if is_fail else 0,
                    repetition_score=0.75 if is_fail else 0.1,
                    thought_length=100,
                    accumulated_cost_usd=0.015,
                    failure_status=req.predicted_failure_mode if is_fail else "NORMAL",
                    is_failure=is_fail,
                    resolution_source=f"HITL_{req.status}",
                    timestamp=time.time()
                ))
            except Exception as e:
                logger.debug("Non-fatal: failed to buffer active exemplar: %s", e)

            return req

    def wait_for_resolution(self, request_id: str, timeout_s: float = 30.0) -> HITLRequest:
        """Blocks until operator resolves the request or timeout expires."""
        event = self._events.get(request_id)
        if not event:
            with self._lock:
                return self._requests.get(request_id, HITLRequest(
                    request_id=request_id,
                    session_id="unknown",
                    step_index=0,
                    tool_name="unknown",
                    action="PAUSE",
                    risk_level="HIGH",
                    failure_probability=0.5,
                    predicted_failure_mode="UNKNOWN",
                    reason="Request expired",
                    created_at=time.time(),
                    status="TIMED_OUT"
                ))

        signaled = event.wait(timeout=timeout_s)
        with self._lock:
            req = self._requests[request_id]
            if not signaled and req.status == "PENDING":
                req.status = "TIMED_OUT"
                req.operator_comment = f"Timed out after {timeout_s}s awaiting operator input."
                req.resolved_at = time.time()
            return req

    def clear(self):
        """Clears all requests (used in tests)."""
        with self._lock:
            self._requests.clear()
            self._events.clear()


# Global singleton manager
hitl_gateway = HITLManager()
