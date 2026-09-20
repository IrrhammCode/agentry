"""
Agentry REST API Gateway & Sidecar Daemon.
Allows multi-language agent fleets (Python, TypeScript, Go, Rust, cURL)
to interact with the TabPFN-3.5 guardrail engine over standard HTTP.
"""

import json
import logging
import time
from http.server import HTTPServer, ThreadingHTTPServer, BaseHTTPRequestHandler
from typing import Optional
from urllib.parse import urlparse, parse_qs

from agentry import __version__
from agentry.guard import AgentryGuard, SentryDecision
from agentry.storage import AuditStorage

logger = logging.getLogger("agentry.server")

# Global singleton guard instance for the HTTP daemon
_guard_instance: Optional[AgentryGuard] = None


def get_guard() -> AgentryGuard:
    global _guard_instance
    if _guard_instance is None:
        _guard_instance = AgentryGuard(auto_fit=True, raise_on_kill=False)
    return _guard_instance


def set_guard(guard: AgentryGuard) -> None:
    global _guard_instance
    _guard_instance = guard


class AgentryHTTPRequestHandler(BaseHTTPRequestHandler):
    """HTTP request dispatcher for Agentry guardrail daemon."""

    def _send_json(self, status_code: int, data: dict):
        body = json.dumps(data, indent=2).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        """Handle CORS pre-flight requests."""
        self._send_json(200, {"status": "ok"})

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        guard = get_guard()

        # 1. Health check
        if path == "" or path == "/health" or path == "/v1/health":
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

        # 2. Fleet Summary & Metrics
        if path == "/v1/fleet" or path == "/v1/metrics":
            summary = guard.storage.get_fleet_summary()
            self._send_json(200, summary)
            return

        # 3. Session audit history: /v1/sessions/<session_id>
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

        # 1. Audit step endpoint
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

        # 2. Reset session endpoint: /v1/sessions/<session_id>/reset
        if path.startswith("/v1/sessions/") and path.endswith("/reset"):
            parts = path.split("/")
            session_id = parts[3]
            guard.reset_session(session_id)
            self._send_json(200, {"status": "ok", "message": f"Session '{session_id}' reset successfully"})
            return

        self._send_json(404, {"error": f"Endpoint not found: {self.path}"})

    def log_message(self, format, *args):
        # Override to suppress default HTTP server access logs to stderr
        return


def start_server(host: str = "127.0.0.1", port: int = 8787):
    """Starts the Agentry HTTP Sentry daemon."""
    server_address = (host, port)
    httpd = HTTPServer(server_address, AgentryHTTPRequestHandler)
    print(f"🚀 Agentry HTTP Sentry Gateway running on http://{host}:{port}")
    print(f"   • Health Check: http://{host}:{port}/health")
    print(f"   • Audit API:    POST http://{host}:{port}/v1/audit")
    print(f"   • Fleet Stats:  http://{host}:{port}/v1/fleet")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Agentry Sentry Gateway...")
        httpd.server_close()


if __name__ == "__main__":
    start_server()
