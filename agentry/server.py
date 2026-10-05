"""
Agentry REST API Gateway, Sidecar Daemon & Zero-Code OpenAI Proxy.
Allows multi-language agent fleets (Python, TypeScript, Go, Rust, cURL)
to interact with TabPFN-3.5 guardrails, export incident reports, manage HITL approvals,
and proxy OpenAI-compatible chat completions over standard HTTP.
"""

import json
import logging
import time
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs

from dataclasses import asdict
from agentry import __version__
from agentry.guard import AgentryGuard, SentryDecision, _safe_int, _safe_float
from agentry.storage import AuditStorage
from agentry.report import generate_incident_report
from agentry.hitl import hitl_gateway
from agentry.proxy import OpenAIProxyHandler
from agentry.budget import budget_governor
from agentry.healing import trajectory_healer
from agentry.config import settings

logger = logging.getLogger("agentry.server")

# Global singleton guard instance for the HTTP daemon
_guard_instance: Optional[AgentryGuard] = None
_proxy_handler: Optional[OpenAIProxyHandler] = None


def get_guard() -> AgentryGuard:
    global _guard_instance
    if _guard_instance is None:
        _guard_instance = AgentryGuard(auto_fit=True, raise_on_kill=False)
    return _guard_instance


def set_guard(guard: AgentryGuard) -> None:
    global _guard_instance
    _guard_instance = guard


def get_proxy_handler() -> OpenAIProxyHandler:
    global _proxy_handler
    if _proxy_handler is None:
        _proxy_handler = OpenAIProxyHandler()
    return _proxy_handler


class AgentryHTTPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request dispatcher for Agentry guardrail daemon and OpenAI proxy."""

    def _send_json(self, status_code: int, data: dict, extra_headers: Optional[Dict[str, str]] = None):
        body = json.dumps(data, indent=2, default=str).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization, X-Session-ID, X-Agent-Session")
        if extra_headers:
            for k, v in extra_headers.items():
                self.send_header(k, str(v))
        self.end_headers()
        self.wfile.write(body)

    def _send_html(self, status_code: int, html_content: str):
        body = html_content.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_plain_text(self, status_code: int, text_content: str):
        body = text_content.encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        """Handle CORS pre-flight requests."""
        self._send_json(200, {"status": "ok"})

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        query = parse_qs(parsed.query)
        guard = get_guard()

        # 1. Health check
        if path in ("", "/health", "/v1/health"):
            ollama_status = guard.sentry._check_ollama_alive()
            has_cloud_llm = bool(settings.groq_api_keys or os.getenv("GROQ_API_KEYS"))
            reasoning_provider = "local_ollama" if ollama_status else ("groq_cloud" if has_cloud_llm else "deterministic_rules")
            self._send_json(200, {
                "status": "healthy",
                "service": "agentry-sentry-daemon",
                "version": __version__,
                "tabpfn_engine_fitted": guard.engine.is_fitted,
                "tabpfn_cloud_mode": guard.engine.is_cloud_tabpfn,
                "reasoning_engine_alive": ollama_status or has_cloud_llm,
                "reasoning_provider": reasoning_provider,
                "local_slm_alive": ollama_status,
                "local_slm_model": guard.sentry.model,
                "cloud_llm_model": settings.groq_model,
            })
            return

        # 2. Prometheus Exposition Format: GET /metrics
        if path == "/metrics":
            summary = guard.storage.get_fleet_summary()
            budget = budget_governor.check_fleet_budget()
            interventions = summary.get("interventions", {})
            lines = [
                "# HELP agentry_audited_steps_total Total number of agent execution steps audited by TabPFN.",
                "# TYPE agentry_audited_steps_total counter",
                f"agentry_audited_steps_total {summary.get('total_audited_steps', 0)}",
                "",
                "# HELP agentry_unique_sessions_total Total number of unique agent sessions monitored.",
                "# TYPE agentry_unique_sessions_total counter",
                f"agentry_unique_sessions_total {summary.get('unique_sessions', 0)}",
                "",
                "# HELP agentry_interventions_total Total number of autonomic interventions by action type.",
                "# TYPE agentry_interventions_total counter",
                f'agentry_interventions_total{{action="KILL"}} {interventions.get("KILL", 0)}',
                f'agentry_interventions_total{{action="REROUTE"}} {interventions.get("REROUTE", 0)}',
                f'agentry_interventions_total{{action="PAUSE"}} {interventions.get("PAUSE", 0)}',
                f'agentry_interventions_total{{action="PASS"}} {interventions.get("PASS", 0)}',
                "",
                "# HELP agentry_tokens_saved_total Total estimated tokens saved by circuit breakers.",
                "# TYPE agentry_tokens_saved_total counter",
                f"agentry_tokens_saved_total {summary.get('total_tokens_saved', 0)}",
                "",
                "# HELP agentry_cost_saved_usd_total Total estimated API cost saved in USD.",
                "# TYPE agentry_cost_saved_usd_total counter",
                f"agentry_cost_saved_usd_total {summary.get('total_cost_saved_usd', 0.0):.4f}",
                "",
                "# HELP agentry_fleet_budget_daily_usd Daily configured budget ceiling in USD.",
                "# TYPE agentry_fleet_budget_daily_usd gauge",
                f"agentry_fleet_budget_daily_usd {budget.daily_budget_usd:.2f}",
                "",
                "# HELP agentry_fleet_spend_current_usd Current fleet expenditure in the last 24h in USD.",
                "# TYPE agentry_fleet_spend_current_usd gauge",
                f"agentry_fleet_spend_current_usd {budget.current_fleet_spend_usd:.4f}",
                "",
                "# HELP agentry_fleet_budget_utilization_ratio Ratio of daily budget consumed (0.0 to 1.0+).",
                "# TYPE agentry_fleet_budget_utilization_ratio gauge",
                f"agentry_fleet_budget_utilization_ratio {budget.utilization_pct / 100.0:.3f}",
                "",
                "# HELP agentry_tabpfn_cloud_mode 1 if TabPFN Cloud is active, 0 for local offline mode.",
                "# TYPE agentry_tabpfn_cloud_mode gauge",
                f"agentry_tabpfn_cloud_mode {1 if guard.engine.is_cloud_tabpfn else 0}",
                ""
            ]
            self._send_plain_text(200, "\n".join(lines))
            return

        # 3. OpenAI-Compatible Models Endpoint: GET /v1/models
        if path == "/v1/models":
            self._send_json(200, {
                "object": "list",
                "data": [
                    {"id": settings.groq_model, "object": "model", "owned_by": "agentry-proxy"},
                    {"id": settings.sentry_model, "object": "model", "owned_by": "agentry-local"},
                    {"id": "agentry-tabpfn-3.5", "object": "model", "owned_by": "prior-labs"},
                ]
            })
            return

        # 4. Fleet Summary & JSON Metrics: GET /v1/fleet or /v1/metrics
        if path in ("/v1/fleet", "/v1/metrics"):
            summary = guard.storage.get_fleet_summary()
            self._send_json(200, summary)
            return

        # 5. Fleet Budget Quota Status: GET /v1/budget
        if path == "/v1/budget":
            status = budget_governor.check_fleet_budget()
            self._send_json(200, asdict(status))
            return

        # 6. Human-in-the-Loop (HITL) Queue: GET /v1/approvals
        if path == "/v1/approvals":
            status_filter = query.get("status", [None])[0]
            requests = hitl_gateway.list_requests(status=status_filter)
            if not requests and status_filter in (None, "PENDING"):
                from agentry.agent import SentryDecision
                from agentry.engine import StepRiskAssessment
                demo_dec = SentryDecision(
                    session_id="devops_db_migration_prod",
                    step_index=4,
                    action="PAUSE",
                    risk_level="HIGH",
                    confidence=0.94,
                    reason="Blast radius hazard: Irreversible schema mutation DROP TABLE audit_events_archive. Snapshot t=4 frozen.",
                    reroute_instruction="Use non-destructive ALTER TABLE or archive rows to cold storage.",
                    estimated_tokens_saved=24000,
                    estimated_cost_saved_usd=0.048,
                    sentry_provider="blast-radius-evaluator",
                    tabpfn_assessment=StepRiskAssessment(
                        session_id="devops_db_migration_prod",
                        step_index=4,
                        failure_probability=0.88,
                        predicted_failure_mode="COST_RUNAWAY",
                        mode_probabilities={"COST_RUNAWAY": 0.88},
                        uncertainty_score=0.06,
                        projected_final_cost_usd=1.45,
                        primary_risk_driver="blast_radius",
                        is_cloud_tabpfn=False
                    )
                )
                hitl_gateway.create_escalation(demo_dec, tool_name="bash: DROP TABLE audit_events_archive")
                requests = hitl_gateway.list_requests(status=status_filter)
            self._send_json(200, {"total": len(requests), "requests": requests})
            return

        # 7. Audit events feed: GET /v1/events
        if path == "/v1/events":
            limit = _safe_int(query.get("limit", [50])[0], default=50, min_val=1)
            events = guard.storage.get_all_events(limit=limit)
            self._send_json(200, {"total": len(events), "events": events})
            return

        # 8. Incident Post-Mortem Report: GET /v1/reports/<session_id>
        if path.startswith("/v1/reports/"):
            session_id = path.replace("/v1/reports/", "")
            fmt = query.get("format", ["markdown"])[0].lower()
            report_text = generate_incident_report(session_id, format=fmt, storage=guard.storage)
            if fmt == "html":
                self._send_html(200, report_text)
            else:
                self._send_json(200, {"session_id": session_id, "report_markdown": report_text})
            return

        # 9. Session audit history: GET /v1/sessions/<session_id>
        if path.startswith("/v1/sessions/"):
            session_id = path.replace("/v1/sessions/", "")
            events = guard.storage.get_session_events(session_id)
            self._send_json(200, {
                "session_id": session_id,
                "total_steps": len(events),
                "events": events
            })
            return

        # 10. MCP Usage Breakdown: GET /v1/mcp/usage
        if path == "/v1/mcp/usage":
            usage = guard.storage.get_usage_by_source()
            self._send_json(200, usage)
            return

        # 11. Events by Source: GET /v1/events/<source>
        if path.startswith("/v1/events/"):
            source = path.replace("/v1/events/", "")
            limit = _safe_int(query.get("limit", [20])[0], default=20, min_val=1)
            events = guard.storage.get_events_by_source(source, limit=limit)
            self._send_json(200, {"source": source, "total": len(events), "events": events})
            return

        self._send_json(404, {"error": f"Endpoint not found: {self.path}"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        guard = get_guard()

        # Read JSON body safely
        content_length = _safe_int(self.headers.get("Content-Length", 0), default=0, min_val=0)
        post_data = self.rfile.read(content_length)
        try:
            payload = json.loads(post_data.decode("utf-8")) if post_data else {}
            if not isinstance(payload, dict):
                self._send_json(400, {"error": "JSON body must be an object"})
                return
        except Exception:
            self._send_json(400, {"error": "Invalid JSON body"})
            return

        # 1. Zero-Code OpenAI-Compatible Proxy: POST /v1/chat/completions
        if path == "/v1/chat/completions":
            proxy = get_proxy_handler()
            client_headers = {k.lower(): v for k, v in self.headers.items()}
            is_stream = bool(payload.get("stream", False))

            if is_stream:
                session_id = proxy._resolve_session_id(payload, client_headers)
                state = guard.get_or_create_session(session_id)
                if state.is_halted:
                    self._send_json(429, {
                        "error": {
                            "message": f"AGENTRY SENTRY CIRCUIT BREAKER: Session '{session_id}' is permanently HALTED.",
                            "type": "circuit_breaker_kill",
                            "code": "SESSION_HALTED"
                        }
                    }, extra_headers={"X-Agentry-Action": "KILL"})
                    return

                self.send_response(200)
                self.send_header("Content-Type", "text/event-stream; charset=utf-8")
                self.send_header("Cache-Control", "no-cache")
                self.send_header("Connection", "keep-alive")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()

                try:
                    for chunk in proxy.stream_chat_completion(payload, client_headers, guard):
                        self.wfile.write(chunk)
                        self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    logger.debug("Client disconnected during SSE stream.")
                return

            status_code, resp_data, extra_headers = proxy.handle_chat_completion(payload, client_headers, guard)
            self._send_json(status_code, resp_data, extra_headers=extra_headers)
            return

        # 2. Audit step endpoint: POST /v1/audit
        if path == "/v1/audit":
            session_id = str(payload.get("session_id") or f"session_{int(time.time())}")
            tool_name = str(payload.get("tool_name") or "tool")
            input_text = str(payload.get("input_text") or "")
            output_text = str(payload.get("output_text") or "")
            prompt_tokens = _safe_int(payload.get("prompt_tokens"), default=0, min_val=0)
            completion_tokens = _safe_int(payload.get("completion_tokens"), default=0, min_val=0)
            thought_trace = str(payload.get("thought_trace") or "")
            agent_role = str(payload.get("agent_role") or "Autonomous-Agent")
            model_name = str(payload.get("model_name") or "swe-agent-70b")
            latency_ms = _safe_float(payload.get("latency_ms"), default=850.0, min_val=0.0)

            decision = guard.audit(
                session_id=session_id,
                tool_name=tool_name,
                input_text=input_text,
                output_text=output_text,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                thought_trace=thought_trace,
                agent_role=agent_role,
                model_name=model_name,
                latency_ms=latency_ms
            )

            response = {
                "session_id": decision.session_id,
                "step_index": decision.step_index,
                "action": decision.action,
                "risk_level": decision.risk_level,
                "confidence": decision.confidence,
                "failure_probability": decision.tabpfn_assessment.failure_probability,
                "predicted_failure_mode": decision.tabpfn_assessment.predicted_failure_mode,
                "projected_final_cost_usd": decision.tabpfn_assessment.projected_final_cost_usd,
                "reason": decision.reason,
                "reroute_instruction": decision.reroute_instruction,
                "estimated_tokens_saved": decision.estimated_tokens_saved,
                "estimated_cost_saved_usd": decision.estimated_cost_saved_usd,
                "sentry_provider": decision.sentry_provider
            }
            self._send_json(200, response)
            return

        # 3. Resolve Human-in-the-Loop (HITL) Request: POST /v1/approvals/<request_id>
        if path.startswith("/v1/approvals/"):
            request_id = path.replace("/v1/approvals/", "")
            resolution = payload.get("action", "RESUME")
            comment = payload.get("comment")
            custom_directive = payload.get("custom_directive")
            resolved_req = hitl_gateway.resolve(
                request_id=request_id,
                resolution=resolution,
                comment=comment,
                custom_directive=custom_directive
            )
            if resolved_req:
                self._send_json(200, {"status": "ok", "request": json.loads(json.dumps(resolved_req.__dict__))})
            else:
                self._send_json(404, {"error": f"HITL request '{request_id}' not found."})
            return

        # 5. Trajectory Rewind & Self-Healing: POST /v1/healing/rewind
        if path == "/v1/healing/rewind":
            session_id = str(payload.get("session_id", "default_session"))
            current_step = _safe_int(payload.get("current_step", 1), default=1)
            failed_tool = str(payload.get("failed_tool", "tool"))
            error_streak = _safe_int(payload.get("error_streak", 1), default=1)
            reason = str(payload.get("reason", "Anomalous failure loop detected"))
            prescription = trajectory_healer.diagnose_and_prescribe(
                session_id=session_id,
                current_step=current_step,
                failed_tool=failed_tool,
                error_streak=error_streak,
                reason=reason,
                storage=guard.storage
            )
            self._send_json(200, asdict(prescription))
            return

        # 6. Session Budget Check: POST /v1/budget/check
        if path == "/v1/budget/check":
            session_id = str(payload.get("session_id", "default_session"))
            accumulated_cost = _safe_float(payload.get("accumulated_cost", 0.0), default=0.0)
            status = budget_governor.check_session_budget(session_id, accumulated_cost)
            self._send_json(200, asdict(status))
            return

        # 7. In-Flight DLP Sanitizer: POST /v1/dlp/redact
        if path == "/v1/dlp/redact":
            text = str(payload.get("text") or "")
            from agentry.dlp import secret_redactor
            res = secret_redactor.redact(text)
            self._send_json(200, {
                "original_text": text,
                "masked_text": res.masked_text,
                "redaction_count": res.redaction_count,
                "detected_secrets": res.detected_secrets
            })
            return

        # 8. Blast Radius Evaluation: POST /v1/blast-radius/evaluate
        if path == "/v1/blast-radius/evaluate":
            tool_name = str(payload.get("tool_name") or "bash")
            command = str(payload.get("command") or payload.get("input_text") or "")
            from agentry.blast_radius import blast_radius_evaluator
            assessment = blast_radius_evaluator.evaluate(tool_name, command)
            self._send_json(200, {
                "score": round(assessment.score * 100, 1),
                "score_raw": assessment.score,
                "category": assessment.category,
                "is_blocked": assessment.is_blocked,
                "recommended_action": assessment.recommended_action,
                "violation_reason": assessment.violation_reason,
                "matched_pattern": assessment.matched_pattern
            })
            return

        # 9. Swarm Deadlock Detector: POST /v1/swarm/deadlock
        if path == "/v1/swarm/deadlock":
            from agentry.swarm import SwarmDeadlockDetector
            detector = SwarmDeadlockDetector()
            session_id = payload.get("session_id", "swarm_session")
            transfers = payload.get("transfers", [])
            alert = None
            for tr in transfers:
                alert = detector.record_transfer(
                    session_id=session_id,
                    from_agent=tr.get("from_agent", ""),
                    to_agent=tr.get("to_agent", ""),
                    task_snippet=tr.get("task", "")
                )
            self._send_json(200, {
                "is_deadlocked": alert.is_deadlocked if alert else False,
                "cycle_agents": alert.cycle_agents if alert else [],
                "cycle_length": alert.cycle_length if alert else 0,
                "recommendation": alert.recommendation if alert else "Nominal agent delegation flow."
            })
            return

        # 10. Global Kill Switch Emergency Suspend: POST /v1/fleet/emergency-suspend
        if path == "/v1/fleet/emergency-suspend":
            with guard._lock:
                for session in guard._sessions.values():
                    session.is_halted = True
                halted_count = len(guard._sessions)
            self._send_json(200, {
                "status": "suspended",
                "halted_sessions": halted_count,
                "message": f"Global kill switch engaged. {halted_count} active session(s) halted."
            })
            return

        self._send_json(404, {"error": f"Endpoint not found: {self.path}"})

    def log_message(self, format, *args):
        return


def start_server(host: str = "127.0.0.1", port: int = 8787):
    """Starts the Agentry HTTP Sentry daemon, API Gateway & OpenAI Proxy."""
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, AgentryHTTPRequestHandler)
    print(f"🚀 Agentry HTTP Sentry Gateway & OpenAI Proxy running on http://{host}:{port}")
    print(f"   • Health Check:       http://{host}:{port}/health")
    print(f"   • OpenAI Proxy:       POST http://{host}:{port}/v1/chat/completions")
    print(f"   • Prometheus Metrics: http://{host}:{port}/metrics")
    print(f"   • Fleet Budget:       http://{host}:{port}/v1/budget")
    print(f"   • Trajectory Rewind:  POST http://{host}:{port}/v1/healing/rewind")
    print(f"   • Audit API:          POST http://{host}:{port}/v1/audit")
    print(f"   • HITL Approvals:     http://{host}:{port}/v1/approvals")
    print(f"   • Incident Reports:   http://{host}:{port}/v1/reports/<session_id>?format=html")
    print(f"   • Fleet Metrics:      http://{host}:{port}/v1/fleet")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Agentry Sentry Gateway...")
        httpd.server_close()


if __name__ == "__main__":
    start_server()
