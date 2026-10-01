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

from agentry import __version__
from agentry.guard import AgentryGuard, SentryDecision
from agentry.storage import AuditStorage
from agentry.report import generate_incident_report
from agentry.hitl import hitl_gateway
from agentry.proxy import OpenAIProxyHandler
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
        body = json.dumps(data, indent=2).encode("utf-8")
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
            self._send_json(200, {
                "status": "healthy",
                "service": "agentry-sentry-daemon",
                "version": __version__,
                "tabpfn_engine_fitted": guard.engine.is_fitted,
                "tabpfn_cloud_mode": guard.engine.is_cloud_tabpfn,
                "local_slm_alive": ollama_status,
                "local_slm_model": guard.sentry.model
            })
            return

        # 2. OpenAI-Compatible Models Endpoint: GET /v1/models
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

        # 3. Fleet Summary & Metrics
        if path in ("/v1/fleet", "/v1/metrics"):
            summary = guard.storage.get_fleet_summary()
            self._send_json(200, summary)
            return

        # 4. Human-in-the-Loop (HITL) Queue: GET /v1/approvals
        if path == "/v1/approvals":
            status_filter = query.get("status", [None])[0]
            requests = hitl_gateway.list_requests(status=status_filter)
            self._send_json(200, {"total": len(requests), "requests": requests})
            return

        # 5. Incident Post-Mortem Report: GET /v1/reports/<session_id>
        if path.startswith("/v1/reports/"):
            session_id = path.replace("/v1/reports/", "")
            fmt = query.get("format", ["markdown"])[0].lower()
            report_text = generate_incident_report(session_id, format=fmt, storage=guard.storage)
            if fmt == "html":
                self._send_html(200, report_text)
            else:
                self._send_json(200, {"session_id": session_id, "report_markdown": report_text})
            return

        # 6. Session audit history: GET /v1/sessions/<session_id>
        if path.startswith("/v1/sessions/"):
            session_id = path.replace("/v1/sessions/", "")
            events = guard.storage.get_session_events(session_id)
            self._send_json(200, {
                "session_id": session_id,
                "total_steps": len(events),
                "events": events
            })
            return

        self._send_json(404, {"error": f"Endpoint not found: {self.path}"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        guard = get_guard()

        # Read JSON body
        content_length = int(self.headers.get("Content-Length", 0))
        post_data = self.rfile.read(content_length)
        try:
            payload = json.loads(post_data.decode("utf-8")) if post_data else {}
        except Exception:
            self._send_json(400, {"error": "Invalid JSON body"})
            return

        # 1. Zero-Code OpenAI-Compatible Proxy: POST /v1/chat/completions
        if path == "/v1/chat/completions":
            proxy = get_proxy_handler()
            client_headers = {k.lower(): v for k, v in self.headers.items()}
            status_code, resp_data, extra_headers = proxy.handle_chat_completion(payload, client_headers, guard)
            self._send_json(status_code, resp_data, extra_headers=extra_headers)
            return

        # 2. Audit step endpoint: POST /v1/audit
        if path == "/v1/audit":
            session_id = payload.get("session_id", f"session_{int(time.time())}")
            tool_name = payload.get("tool_name", "tool")
            input_text = payload.get("input_text", "")
            output_text = payload.get("output_text", "")
            prompt_tokens = int(payload.get("prompt_tokens", 0))
            completion_tokens = int(payload.get("completion_tokens", 0))
            thought_trace = payload.get("thought_trace", "")
            agent_role = payload.get("agent_role", "Autonomous-Agent")
            model_name = payload.get("model_name", "swe-agent-70b")
            latency_ms = payload.get("latency_ms")

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
                latency_ms=float(latency_ms) if latency_ms is not None else None
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

        # 4. Reset session endpoint: POST /v1/sessions/<session_id>/reset
        if path.startswith("/v1/sessions/") and path.endswith("/reset"):
            parts = path.split("/")
            session_id = parts[3]
            guard.reset_session(session_id)
            self._send_json(200, {"status": "ok", "message": f"Session '{session_id}' reset successfully"})
            return

        self._send_json(404, {"error": f"Endpoint not found: {self.path}"})

    def log_message(self, format, *args):
        return


def start_server(host: str = "127.0.0.1", port: int = 8787):
    """Starts the Agentry HTTP Sentry daemon, API Gateway & OpenAI Proxy."""
    server_address = (host, port)
    httpd = ThreadingHTTPServer(server_address, AgentryHTTPRequestHandler)
    print(f"🚀 Agentry HTTP Sentry Gateway & OpenAI Proxy running on http://{host}:{port}")
    print(f"   • Health Check:     http://{host}:{port}/health")
    print(f"   • OpenAI Proxy:     POST http://{host}:{port}/v1/chat/completions")
    print(f"   • Audit API:        POST http://{host}:{port}/v1/audit")
    print(f"   • HITL Approvals:   http://{host}:{port}/v1/approvals")
    print(f"   • Incident Reports: http://{host}:{port}/v1/reports/<session_id>?format=html")
    print(f"   • Fleet Metrics:    http://{host}:{port}/v1/fleet")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Agentry Sentry Gateway...")
        httpd.server_close()


if __name__ == "__main__":
    start_server()
