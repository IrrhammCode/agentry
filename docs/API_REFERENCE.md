# 📡 Agentry REST API Reference Manual

> **Daemon Base URL:** `http://127.0.0.1:8000` (or configured host/port)  
> **Protocol:** HTTP/1.1 with JSON payloads & Server-Sent Events (SSE)  
> **CORS:** Enabled (`Access-Control-Allow-Origin: *`)

---

## 📑 Endpoints Overview

| Category | Endpoint | Method | Description |
| :--- | :--- | :--- | :--- |
| **System** | `/health` | `GET` | Health check & TabPFN engine readiness |
| **System** | `/metrics` | `GET` | Prometheus text exposition format metrics |
| **Audit** | `/v1/audit` | `POST` | Real-time TabPFN Bayesian audit for agent steps |
| **Fleet** | `/v1/fleet` | `GET` | Fleet aggregate governance metrics & capital saved |
| **Fleet** | `/v1/events` | `GET` | Paginated live stream of recorded audit steps |
| **HITL** | `/v1/approvals` | `GET` | List active Human-in-the-Loop escalation requests |
| **HITL** | `/v1/approvals/<id>` | `POST` | Resolve an escalation (`RESUME`, `REROUTE`, `ABORT`) |
| **DLP** | `/v1/dlp/redact` | `POST` | Scan & redact high-entropy secrets in-flight |
| **Sandbox**| `/v1/blast-radius/evaluate`| `POST` | Semantic command mutation hazard scoring |
| **Swarm** | `/v1/swarm/deadlock` | `POST` | Directed graph cyclic deadlock detector |
| **Healing**| `/v1/healing/rewind` | `POST` | Trajectory rewind & self-healing prescription |
| **Budget** | `/v1/budget` | `GET` | Fleet spend ceiling quota utilization |
| **Control**| `/v1/fleet/emergency-suspend`| `POST`| Global Kill Switch: freeze all running agent sessions |
| **Proxy**  | `/v1/chat/completions` | `POST` | Drop-in OpenAI reverse proxy with stream interception |

---

## 1. System Health & Readiness

### `GET /health`
Returns the status of the Sentry daemon and underlying Prior Labs TabPFN foundation model.

#### Response `200 OK`:
```json
{
  "status": "healthy",
  "service": "agentry-sentry-daemon",
  "version": "0.1.0",
  "tabpfn_engine_fitted": true,
  "tabpfn_cloud_mode": true,
  "local_slm_alive": false,
  "local_slm_model": "qwen2.5:3b"
}
```

---

## 2. Real-Time TabPFN Audit

### `POST /v1/audit`
Audits an arbitrary agent tool execution step using TabPFN tabular inference and semantic sentry rules.

#### Request Headers:
- `Content-Type: application/json`

#### Request Body:
```json
{
  "session_id": "swe_bench_task_402",
  "tool_name": "bash",
  "input_text": "DROP DATABASE production;",
  "output_text": "",
  "prompt_tokens": 1250,
  "completion_tokens": 42,
  "thought_trace": "Cleaning up obsolete test databases",
  "agent_role": "DevOps-Agent",
  "model_name": "llama-3.3-70b-versatile",
  "latency_ms": 25.0
}
```

#### Response `200 OK`:
```json
{
  "session_id": "swe_bench_task_402",
  "step_index": 0,
  "action": "KILL",
  "risk_level": "CRITICAL",
  "confidence": 1.0,
  "failure_probability": 1.0,
  "predicted_failure_mode": "COST_RUNAWAY",
  "projected_final_cost_usd": 0.50,
  "reason": "CRITICAL BLAST RADIUS VIOLATION: Irreversible database DROP mutation",
  "reroute_instruction": "DO NOT execute destructive commands.",
  "estimated_tokens_saved": 18000,
  "estimated_cost_saved_usd": 0.036,
  "sentry_provider": "blast-radius-evaluator"
}
```

---

## 3. Fleet Governance Metrics

### `GET /v1/fleet`
Returns global metrics computed directly from SQLite ACID audit storage.

#### Response `200 OK`:
```json
{
  "total_audited_steps": 1727,
  "unique_sessions": 52,
  "interventions": {
    "KILL": 81,
    "REROUTE": 39,
    "PAUSE": 18,
    "PASS": 1589
  },
  "total_tokens_saved": 2032200,
  "total_cost_saved_usd": 2.3579
}
```

---

## 4. Live Audit Events Feed

### `GET /v1/events`

#### Query Parameters:
- `limit` (integer, optional, default: `50`): Maximum events to return.

#### Response `200 OK`:
```json
{
  "total": 2,
  "events": [
    {
      "id": 1727,
      "session_id": "swe_bench_task_402",
      "step_index": 0,
      "timestamp": 1790931796.19,
      "action": "KILL",
      "risk_level": "CRITICAL",
      "failure_probability": 1.0,
      "predicted_failure_mode": "COST_RUNAWAY",
      "projected_final_cost_usd": 0.50,
      "confidence": 1.0,
      "reason": "CRITICAL BLAST RADIUS VIOLATION: Irreversible database DROP mutation",
      "reroute_instruction": "DO NOT execute destructive commands.",
      "estimated_tokens_saved": 18000,
      "estimated_cost_saved_usd": 0.036,
      "sentry_provider": "blast-radius-evaluator"
    }
  ]
}
```

---

## 5. Human-in-the-Loop (HITL) Gateway

### `GET /v1/approvals`
Lists pending or historical operator sign-off requests.

#### Query Parameters:
- `status` (string, optional): Filter by status (`PENDING`, `APPROVED_RESUME`, `REROUTED`, `REJECTED_ABORT`).

#### Response `200 OK`:
```json
{
  "total": 1,
  "requests": [
    {
      "request_id": "hitl_8941abc",
      "session_id": "devops_db_migration_prod",
      "step_index": 4,
      "tool_name": "bash: DROP TABLE audit_events_archive",
      "action": "PAUSE",
      "risk_level": "HIGH",
      "failure_probability": 0.88,
      "predicted_failure_mode": "COST_RUNAWAY",
      "reason": "Blast radius hazard: Irreversible schema mutation DROP TABLE",
      "created_at": 1790931900.0,
      "status": "PENDING"
    }
  ]
}
```

### `POST /v1/approvals/<request_id>`
Resolves a pending human sign-off request.

#### Request Body:
```json
{
  "action": "REROUTE",
  "comment": "Prevent table drop in production",
  "custom_directive": "Archive old rows to S3 cold storage bucket instead"
}
```

#### Allowed Actions:
- `RESUME`: Authorize execution to proceed within sandbox.
- `REROUTE`: Inject custom counterfactual prompt directive.
- `ABORT`: Terminate execution and roll back disk snapshots.

---

## 6. In-Flight DLP Secret Sanitizer

### `POST /v1/dlp/redact`
Redacts API keys, tokens, and database passwords from text in-flight before transmission.

#### Request Body:
```json
{
  "text": "Using AWS key AKIAIOSFODNN7EXAMPLE with postgres://admin:secret123@db.prod:5432/main"
}
```

#### Response `200 OK`:
```json
{
  "original_text": "Using AWS key AKIAIOSFODNN7EXAMPLE with postgres://admin:secret123@db.prod:5432/main",
  "masked_text": "Using AWS key [REDACTED_AWS_KEY_ID] with postgres://admin:[REDACTED_PASSWORD]@db.prod:5432/main",
  "redaction_count": 2,
  "detected_secrets": [
    { "type": "AWS_KEY_ID", "count": 1 },
    { "type": "DB_CONN_STRING", "count": 1 }
  ]
}
```

---

## 7. Semantic Blast Radius Evaluator

### `POST /v1/blast-radius/evaluate`

#### Request Body:
```json
{
  "tool_name": "bash",
  "command": "rm -rf / --no-preserve-root"
}
```

#### Response `200 OK`:
```json
{
  "score": 100.0,
  "score_raw": 1.0,
  "category": "CRITICAL",
  "is_blocked": true,
  "recommended_action": "KILL",
  "violation_reason": "Catastrophic recursive root/home deletion (rm -rf /)",
  "matched_pattern": "\\brm\\s+-[a-zA-Z]*r[a-zA-Z]*f*\\s+([/~*]|(\\.\\./){2,})"
}
```

---

## 8. Swarm Deadlock Detector

### `POST /v1/swarm/deadlock`

#### Request Body:
```json
{
  "session_id": "swarm_live",
  "transfers": [
    { "from_agent": "CoderAgent", "to_agent": "ReviewerAgent", "task": "Review PR" },
    { "from_agent": "ReviewerAgent", "to_agent": "CoderAgent", "task": "Fix linting" },
    { "from_agent": "CoderAgent", "to_agent": "ReviewerAgent", "task": "Review PR again" },
    { "from_agent": "ReviewerAgent", "to_agent": "CoderAgent", "task": "Fix linting again" }
  ]
}
```

#### Response `200 OK`:
```json
{
  "is_deadlocked": true,
  "cycle_agents": ["ReviewerAgent", "CoderAgent"],
  "cycle_length": 2,
  "recommendation": "Break ping-pong delegation between ReviewerAgent and CoderAgent. Enforce finalizer terminal turn."
}
```

---

## 9. Global Kill Switch

### `POST /v1/fleet/emergency-suspend`
Immediately freezes all running agent execution sessions across the daemon.

#### Request Body: `{}`

#### Response `200 OK`:
```json
{
  "status": "suspended",
  "halted_sessions": 4,
  "message": "Global kill switch engaged. 4 active session(s) halted."
}
```
