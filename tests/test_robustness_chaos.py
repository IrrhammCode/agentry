"""
Comprehensive Robustness, Adversarial & Chaos Test Suite for Agentry.
Validates system resilience under extreme real-world operating conditions:
- Adversarial inputs (None, NaN, Inf, non-numeric strings, massive string payloads)
- High-concurrency multithreaded stress testing (SQLite WAL concurrency)
- OpenAI Reverse Proxy tool-calling with null content & streaming SSE
- Circuit-breaker fail-fast verification
- Graceful TabPFN Cloud network failure fallback
- Model Context Protocol (MCP) parameter chaos
"""

import time
import math
import json
import threading
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import MagicMock, patch
import pytest

from agentry.guard import AgentryGuard, AgentHaltException, _safe_int, _safe_float
from agentry.telemetry import AgentStepTelemetry, load_telemetry_data
from agentry.engine import TabPFNGuardrailEngine
from agentry.agent import AgentrySentry
from agentry.storage import AuditStorage
from agentry.proxy import OpenAIProxyHandler
from agentry.mcp_server import audit_agent_step
from agentry.swe_telemetry import compute_string_overlap, is_error_output


@pytest.fixture(scope="module")
def shared_engine():
    """Module-scoped fitted engine for ultra-fast robustness tests."""
    df = load_telemetry_data()
    engine = TabPFNGuardrailEngine()
    engine.fit(df)
    return engine


def test_safe_converters_adversarial():
    """Validates that _safe_int and _safe_float never crash on bizarre inputs."""
    assert _safe_int(None, default=5) == 5
    assert _safe_int(float("nan"), default=10) == 10
    assert _safe_int(float("inf"), default=0) == 0
    assert _safe_int("invalid_string", default=42) == 42
    assert _safe_int("-50", default=0, min_val=0) == 0
    assert _safe_int(123.9) == 123

    assert _safe_float(None, default=1.5) == 1.5
    assert _safe_float(float("nan"), default=0.0) == 0.0
    assert _safe_float(float("inf"), default=0.0) == 0.0
    assert _safe_float("not_a_float", default=3.14) == 3.14
    assert _safe_float(-10.0, min_val=0.0) == 0.0
    assert _safe_float(1.5, max_val=1.0) == 1.0


def test_swe_telemetry_adversarial():
    """Validates string overlap and error detection on None and massive inputs."""
    assert compute_string_overlap(None, "hello") == 0.0
    assert compute_string_overlap("hello", None) == 0.0
    assert compute_string_overlap(None, None) == 0.0
    assert compute_string_overlap("", "") == 0.0

    # Massive string payload (stress regex tokenizer)
    huge_str = "word " * 50000
    assert compute_string_overlap(huge_str, "word") >= 0.0

    assert is_error_output(None) is False
    assert is_error_output("") is False
    assert is_error_output("Error: Command not found") is True


def test_guard_audit_adversarial_inputs(shared_engine, tmp_path):
    """Auditing with extreme, missing, and malformed inputs should execute cleanly."""
    db_path = tmp_path / "chaos_audit.db"
    storage = AuditStorage(db_path)
    guard = AgentryGuard(engine=shared_engine, storage=storage, auto_fit=False, raise_on_kill=False)

    # 1. All fields None or malformed
    decision = guard.audit(
        session_id=None,
        tool_name=None,
        input_text=None,
        output_text=None,
        prompt_tokens=float("nan"),
        completion_tokens=float("inf"),
        thought_trace=None,
        agent_role=None,
        model_name=None,
        latency_ms="extremely_slow"
    )
    assert decision is not None
    assert decision.action in ("PASS", "PAUSE", "REROUTE", "KILL")
    assert decision.tabpfn_assessment.failure_probability >= 0.0

    # 2. Huge diff payload
    massive_payload = "def test():\n    assert True\n" * 2000
    decision2 = guard.audit(
        session_id="stress_session_huge",
        tool_name="git_diff",
        input_text=massive_payload,
        output_text=massive_payload,
        thought_trace=massive_payload[:5000]
    )
    assert decision2 is not None


def test_multithreaded_concurrency_stress(shared_engine, tmp_path):
    """Validates high-concurrency threading across SQLite WAL without locks or race conditions."""
    db_path = tmp_path / "concurrent_stress.db"
    storage = AuditStorage(db_path)
    guard = AgentryGuard(engine=shared_engine, storage=storage, auto_fit=False, raise_on_kill=False)

    num_threads = 16
    steps_per_thread = 5

    def worker(worker_id: int):
        for i in range(steps_per_thread):
            # Interleave shared sessions and unique worker sessions
            sess = "shared_fleet_session" if (i % 2 == 0) else f"worker_session_{worker_id}"
            guard.audit(
                session_id=sess,
                tool_name="bash",
                input_text=f"echo step {i} from worker {worker_id}",
                output_text="ok",
                prompt_tokens=1000 + i * 100,
                completion_tokens=50 + i * 10,
                latency_ms=250.0
            )

    threads = [threading.Thread(target=worker, args=(w,)) for w in range(num_threads)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # Verify all records stored in SQLite WAL without data loss
    events = storage.get_all_events(limit=500)
    expected_total = num_threads * steps_per_thread
    assert len(events) == expected_total

    summary = storage.get_fleet_summary()
    assert summary["total_audited_steps"] == expected_total
    assert summary["unique_sessions"] == num_threads + 1  # each worker + shared session


def test_openai_proxy_tool_calling_null_content(shared_engine, tmp_path):
    """Validates OpenAI reverse proxy handles tool calls where message.content is null."""
    storage = AuditStorage(tmp_path / "proxy_tool.db")
    guard = AgentryGuard(engine=shared_engine, storage=storage, auto_fit=False, raise_on_kill=False)
    proxy = OpenAIProxyHandler(guard=guard)

    # Mock response from upstream LLM with tool_calls and content: None
    mock_upstream_response = {
        "id": "chatcmpl-mock-123",
        "object": "chat.completion",
        "created": int(time.time()),
        "model": "gpt-4o",
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": None,  # Standard OpenAI behavior during tool calls
                    "tool_calls": [
                        {
                            "id": "call_abc999",
                            "type": "function",
                            "function": {
                                "name": "bash",
                                "arguments": "{\"command\": \"cat /etc/hosts\"}"
                            }
                        }
                    ]
                },
                "finish_reason": "tool_calls"
            }
        ],
        "usage": {
            "prompt_tokens": 1250,
            "completion_tokens": 45,
            "total_tokens": 1295
        }
    }

    req_body = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "Check network hosts"}],
        "stream": False
    }
    client_headers = {"x-session-id": "proxy_tool_call_session"}

    with patch("httpx.Client.post") as mock_post:
        mock_resp = MagicMock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = mock_upstream_response
        mock_post.return_value = mock_resp

        status, data, headers = proxy.handle_chat_completion(req_body, client_headers, guard)

    assert status == 200
    assert "choices" in data
    assert headers.get("X-Agentry-Action") in ("PASS", "PAUSE", "REROUTE", "KILL")

    # Verify session telemetry was recorded with the tool name
    session_events = storage.get_session_events("proxy_tool_call_session")
    assert len(session_events) == 1


def test_openai_proxy_streaming_sse(shared_engine, tmp_path):
    """Validates OpenAI reverse proxy supports Server-Sent Events (SSE) streaming."""
    storage = AuditStorage(tmp_path / "proxy_stream.db")
    guard = AgentryGuard(engine=shared_engine, storage=storage, auto_fit=False, raise_on_kill=False)
    proxy = OpenAIProxyHandler(guard=guard)

    sse_lines = [
        b'data: {"id":"chatcmpl-s1","choices":[{"delta":{"role":"assistant","content":"Hello"}}]}',
        b'data: {"id":"chatcmpl-s1","choices":[{"delta":{"content":" world!"}}]}',
        b'data: [DONE]'
    ]

    req_body = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "Say hello"}],
        "stream": True
    }
    client_headers = {"x-session-id": "streaming_session_01"}

    with patch("httpx.Client.stream") as mock_stream_ctx:
        mock_stream_obj = MagicMock()
        mock_stream_obj.status_code = 200
        mock_stream_obj.iter_lines.return_value = [line.decode("utf-8") for line in sse_lines]
        mock_stream_ctx.return_value.__enter__.return_value = mock_stream_obj

        chunks = list(proxy.stream_chat_completion(req_body, client_headers, guard))

    assert len(chunks) >= 3
    combined = b"".join(chunks).decode("utf-8")
    assert "Hello" in combined
    assert "world!" in combined

    # Verify streaming turn was audited
    events = storage.get_session_events("streaming_session_01")
    assert len(events) == 1


def test_circuit_breaker_halt_blocks_proxy(shared_engine, tmp_path):
    """Validates that a killed session is immediately blocked on future proxy requests."""
    storage = AuditStorage(tmp_path / "halt_proxy.db")
    guard = AgentryGuard(engine=shared_engine, storage=storage, auto_fit=False, raise_on_kill=False)
    proxy = OpenAIProxyHandler(guard=guard)

    session_id = "permanently_halted_sess"
    state = guard.get_or_create_session(session_id)
    state.is_halted = True

    # 1. Non-streaming call blocked with 429
    status, data, headers = proxy.handle_chat_completion(
        {"model": "gpt-4o", "messages": [{"role": "user", "content": "Run"}]},
        {"x-session-id": session_id},
        guard
    )
    assert status == 429
    assert data["error"]["code"] == "SESSION_HALTED"
    assert headers.get("X-Agentry-Action") == "KILL"

    # 2. Streaming call yields error without calling upstream
    stream_chunks = list(proxy.stream_chat_completion(
        {"model": "gpt-4o", "messages": [{"role": "user", "content": "Run"}], "stream": True},
        {"x-session-id": session_id},
        guard
    ))
    stream_text = b"".join(stream_chunks).decode("utf-8")
    assert "SESSION_HALTED" in stream_text


def test_tabpfn_cloud_outage_fallback(shared_engine):
    """Simulates a cloud TabPFN network failure and asserts instant fallback to local pre-warmed models."""
    engine = TabPFNGuardrailEngine()
    # Distinct cloud client mock that throws network errors
    cloud_classifier = MagicMock()
    cloud_classifier.predict_proba.side_effect = ConnectionError("TabPFN Cloud 504 Timeout")
    cloud_regressor = MagicMock()
    cloud_regressor.predict.side_effect = ConnectionError("TabPFN Cloud 504 Timeout")

    engine.classifier = cloud_classifier
    engine.regressor = cloud_regressor
    engine._local_classifier = shared_engine._local_classifier
    engine._local_regressor = shared_engine._local_regressor
    engine.mode_encoder = shared_engine.mode_encoder
    engine.role_encoder = shared_engine.role_encoder
    engine.tool_encoder = shared_engine.tool_encoder
    engine.model_encoder = shared_engine.model_encoder
    engine.is_fitted = True
    engine.is_cloud_tabpfn = True

    step = AgentStepTelemetry(
        session_id="cloud_outage_test",
        step_index=2,
        agent_role="DevOps",
        model_name="llama-70b",
        tool_name="bash",
        step_latency_ms=900.0,
        prompt_tokens=2000,
        completion_tokens=100,
        total_tokens=2100,
        tool_call_count=1,
        error_streak=0,
        repetition_score=0.1,
        thought_length=50,
        accumulated_cost_usd=0.005,
        thought_trace="Deploying container...",
        failure_status="NORMAL"
    )
    assessment = engine.evaluate_step(step)

    # Engine must have caught the error, fallen back to local model, and returned assessment
    assert assessment is not None
    assert assessment.is_cloud_tabpfn is False
    assert assessment.failure_probability >= 0.0


def test_mcp_server_chaos_params(shared_engine):
    """Tests Model Context Protocol audit tool against malformed inputs."""
    res = audit_agent_step(
        session_id="mcp_chaos_session",
        step_index=-5,
        tool_name="bash",
        thought_trace=None,
        error_streak=-10,
        repetition_score=float("nan"),
        prompt_tokens="invalid",
        completion_tokens=-20,
        accumulated_cost_usd=float("inf"),
        step_latency_ms="fast"
    )
    assert res is not None
    assert res["session_id"] == "mcp_chaos_session"
    assert res["action"] in ("PASS", "PAUSE", "REROUTE", "KILL")
    assert res["failure_probability"] >= 0.0
    assert res["step_index"] >= 0
