# 📖 Complete Guide: How to Use Agentry

> **Autonomous Tabular Guardrail & Sentry for AI Agent Fleets**  
> *Powered by Prior Labs TabPFN-3.5 Foundation Model & Local-First Intelligence*

---

## 📑 Table of Contents
1. [Overview](#1-overview)
2. [Prerequisites & Installation](#2-prerequisites--installation)
3. [Quick Pre-Flight Check](#3-quick-pre-flight-check)
4. [Integration Mode 1: Zero-Code OpenAI Reverse Proxy](#4-integration-mode-1-zero-code-openai-reverse-proxy)
5. [Integration Mode 2: Python SDK & Decorator Guard](#5-integration-mode-2-python-sdk--decorator-guard)
6. [Integration Mode 3: REST API Sidecar Daemon](#6-integration-mode-3-rest-api-sidecar-daemon)
7. [Integration Mode 4: Model Context Protocol (MCP) Server](#7-integration-mode-4-model-context-protocol-mcp-server)
8. [Integration Mode 5: Closed-Loop Trajectory Rewind & Healing](#8-integration-mode-5-closed-loop-trajectory-rewind--healing)
9. [Integration Mode 6: Human-in-the-Loop (HITL) War Room](#9-integration-mode-6-human-in-the-loop-hitl-war-room)
10. [Web Mission Control & Attack Simulator](#10-web-mission-control--attack-simulator)
11. [Configuration Reference (`.env`)](#11-configuration-reference-env)

---

## 1. Overview

Agentry protects autonomous AI agent fleets (SWE-bench coding agents, DevOps bots, autonomous researchers) from:
- **Infinite Retry Loops:** Agent repeats identical failing bash commands or unit test executions.
- **Catastrophic Blast Radius Mutations:** `rm -rf /`, `DROP TABLE`, filesystem formatting, or raw disk writes.
- **Runaway Token Burn:** Context window explosion and unconstrained compute consumption.
- **Credential & Secret Leaks:** Outbound API keys, database credentials, and auth tokens.
- **Swarm Deadlocks:** Multi-agent cyclic delegation ping-pong (Agent A ⇆ Agent B).

Unlike traditional guardrails that call heavy Cloud LLMs (costly, 2,000ms latency, leaks proprietary code), Agentry uses **Prior Labs TabPFN-3.5** to evaluate structured execution telemetry in **sub-20 milliseconds** with **zero prompt transmission**.

---

## 2. Prerequisites & Installation

### Requirements
- **OS:** Windows, macOS, or Linux
- **Python:** 3.10, 3.11, 3.12, or 3.14
- **Node.js:** v18+ (optional, for frontend Web Console)
- **Prior Labs TabPFN API Key** (optional for local TabPFN; recommended for TabPFN Cloud mode)

### Clone & Install
```bash
# Clone the repository
git clone https://github.com/IrrhammCode/agentry.git
cd agentry

# Create and activate virtual environment
python -m venv .venv

# Windows:
.venv\Scripts\activate

# Linux / macOS:
source .venv/bin/activate

# Install dependencies in editable mode
pip install -e .
```

### Environment Configuration
Create a `.env` file in the project root:
```env
# Prior Labs TabPFN Cloud Credentials
TABPFN_API_KEY=your_tabpfn_api_key_here
TABPFN_MODEL=tabpfn-3.5-classification
TABPFN_THINKING_MODE=true

# Local SLM Sentry (Ollama)
OLLAMA_BASE_URL=http://127.0.0.1:11434/v1
SENTRY_MODEL=qwen2.5:3b

# Fallback Groq API Keys (comma-separated for auto-rotation)
GROQ_API_KEYS=gsk_your_groq_key_here
GROQ_MODEL=llama-3.3-70b-versatile

# Budget Governor
DAILY_FLEET_BUDGET_USD=50.00
SESSION_MAX_COST_USD=5.00
```

---

## 3. Quick Pre-Flight Check

Run the built-in diagnostic doctor to verify all subsystems:
```bash
python run.py doctor
```
Expected output:
```text
✅ Python Environment: Python 3.14 (Compatible)
✅ Prior Labs TabPFN Engine: Fitted & Connected (Cloud Mode)
✅ SQLite Audit Storage: agentry_audit.db (ACID WAL Mode)
✅ DLP Regex Engine: 8 Patterns Compiled (AWS, OpenAI, DB URIs)
✅ Blast Radius Evaluator: Destructive Patterns Armed
✅ Trajectory Healer: File Snapshotting Enabled
```

---

## 4. Integration Mode 1: Zero-Code OpenAI Reverse Proxy

The simplest way to protect any agent written in **any programming language** (Python, TypeScript, Go, Rust, Ruby, PHP) without modifying agent code.

### Step 1: Start the Agentry Proxy Daemon
```bash
python run.py serve --port 8000
```

### Step 2: Point Your OpenAI Client to the Proxy
Simply redirect `base_url` to `http://127.0.0.1:8000/v1` and pass `X-Agent-Session`:

#### Python (OpenAI SDK):
```python
from openai import OpenAI

# Initialize client pointing to local Agentry proxy
client = OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="your-upstream-api-key",  # Forwarded securely to Groq / upstream
    default_headers={"X-Agent-Session": "swe_bench_task_402"}
)

# Chat completion request
response = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": "You are an autonomous DevOps engineer."},
        {"role": "user", "content": "Clean up temporary cache files."}
    ],
    stream=True  # SSE Streaming supported with real-time circuit breakers
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

#### TypeScript / Node.js:
```typescript
import OpenAI from 'openai';

const client = new OpenAI({
  baseURL: 'http://127.0.0.1:8000/v1',
  apiKey: process.env.OPENAI_API_KEY,
  defaultHeaders: {
    'X-Agent-Session': 'devops_swarm_worker_01',
  },
});

const res = await client.chat.completions.create({
  model: 'llama-3.3-70b-versatile',
  messages: [{ role: 'user', content: 'Run database migration' }],
});

console.log(res.choices[0].message.content);
```

#### cURL:
```bash
curl -X POST http://127.0.0.1:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Agent-Session: session_cli_01" \
  -d '{
    "model": "llama-3.3-70b-versatile",
    "messages": [{"role": "user", "content": "Execute refactoring"}]
  }'
```

---

## 5. Integration Mode 2: Python SDK & Decorator Guard

Use Python decorators to wrap and guard tool execution functions directly in your agent framework (LangChain, AutoGen, CrewAI, or bespoke agents).

### Basic Tool Protection (`@guard.protect`)
```python
from agentry.guard import AgentryGuard

guard = AgentryGuard(session_id="agent_worker_prod", auto_fit=True)

@guard.protect
def bash_execution_tool(command: str) -> str:
    """
    Agentry will:
    1. Check blast radius (halts `rm -rf /` or `DROP TABLE` before process spawns).
    2. Redact sensitive credentials in input/output in-flight.
    3. Feed metrics (token velocity, repetition, latency) to TabPFN.
    4. Automatically halt or pause if failure risk > 0.85.
    """
    import subprocess
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout or result.stderr

# Safe tool invocation:
output = bash_execution_tool("pytest tests/test_auth.py")

# Catastrophic tool invocation (Halts immediately with AgentHaltException):
# bash_execution_tool("rm -rf / --no-preserve-root")
```

### Context Manager Step Monitoring (`guard.step`)
```python
with guard.step(
    session_id="swe_agent_42",
    tool_name="file_editor",
    input_text="replace_line(14, 'bad_logic')",
    thought_trace="Attempting syntax fix"
) as step_ctx:
    # Perform your agent logic here
    result = edit_file("tokens.py", 14, "new_code")
    step_ctx.set_output(result)

# Sentry decision is automatically recorded to ACID SQLite database
print(f"Step verdict: {step_ctx.decision.action} (Risk: {step_ctx.decision.risk_level})")
```

---

## 6. Integration Mode 3: REST API Sidecar Daemon

For polyglot microservice environments, run the Agentry daemon as a sidecar container or background process:

```bash
python run.py serve --host 0.0.0.0 --port 8000
```

### Core API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/health` | Daemon status & TabPFN readiness |
| `GET` | `/v1/fleet` | Fleet governance metrics & dollars saved |
| `GET` | `/v1/events?limit=20` | Real-time audit stream across all sessions |
| `POST` | `/v1/audit` | Live TabPFN Bayesian audit for arbitrary tool calls |
| `GET` | `/v1/approvals` | Active Human-in-the-Loop (HITL) escalation queue |
| `POST` | `/v1/approvals/<id>` | Operator decision: `RESUME`, `REROUTE`, `ABORT` |
| `POST` | `/v1/dlp/redact` | In-flight secret scanner & redactor |
| `POST` | `/v1/blast-radius/evaluate` | Command hazard scoring (0 to 100) |
| `POST` | `/v1/swarm/deadlock` | Multi-agent directed graph cycle watchdog |
| `POST` | `/v1/healing/rewind` | Trajectory rewind & self-healing prescription |
| `POST` | `/v1/fleet/emergency-suspend`| Global kill switch to freeze all agents |

#### Example: Live TabPFN Audit via cURL
```bash
curl -X POST http://127.0.0.1:8000/v1/audit \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "agent_alpha",
    "tool_name": "bash",
    "input_text": "DROP DATABASE production;",
    "thought_trace": "Purging old records",
    "latency_ms": 14.8
  }'
```
Response:
```json
{
  "session_id": "agent_alpha",
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

## 7. Integration Mode 4: Model Context Protocol (MCP) Server

Connect Agentry to modern agent-enabled developer tools (Cursor IDE, Claude Desktop, Windsurf, or Antigravity):

### Launching the MCP Server
```bash
python run.py mcp --transport stdio
```

### Configuration for Claude Desktop or Cursor
Add the following to your `claude_desktop_config.json` or Cursor MCP settings:
```json
{
  "mcpServers": {
    "agentry-sentry": {
      "command": "python",
      "args": ["-m", "agentry.mcp_server", "--transport", "stdio"],
      "env": {
        "TABPFN_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Exposed MCP Tools
- `agentry_audit_step`: Audits a proposed tool call with TabPFN before execution.
- `agentry_dlp_sanitize`: Scans text for high-entropy secrets and redacts them.
- `agentry_blast_radius`: Assesses command hazard rating (0-100).
- `agentry_rewind_trajectory`: Rewinds code and generates counterfactual directions.
- `agentry_fleet_summary`: Reports fleet tokens saved and intervention statistics.

---

## 8. Integration Mode 5: Closed-Loop Trajectory Rewind & Healing

When an agent enters an infinite error loop (e.g. 5 repeated failing test runs):
1. **Automatic Pre-Edit Snapshots:** Before any file mutation (`edit_file`, `write_file`), Agentry automatically captures a snapshot in `.agentry/checkpoints/`.
2. **TabPFN Inflection Point Detection:** TabPFN detects failure repetition at step $N$.
3. **Autonomic Rewind:** Agentry reverts the filesystem to checkpoint step $N-k$ and prunes duplicate conversation turns.
4. **Counterfactual Prescription:** Injects a structured steering prompt:
   > *"DO NOT repeat previous tool call. Previous attempts failed with Exit 1. Consider alternative imports or inspect auth_test.py:42."*

Trigger a programmatic rewind:
```bash
python run.py rewind session_id_here
```

---

## 9. Integration Mode 6: Human-in-the-Loop (HITL) War Room

When an agent requests a sensitive production action (schema mutation, firewall modification, external data transfer), TabPFN transitions the action to `PAUSE`.

### CLI Management:
```bash
# List all pending operator escalations:
python run.py hitl list

# Approve and resume:
python run.py hitl resolve hitl_abc123 RESUME --comment "Approved schema change"

# Reject and rollback:
python run.py hitl resolve hitl_abc123 ABORT --comment "Destructive query rejected"

# Steer with custom directive:
python run.py hitl resolve hitl_abc123 REROUTE --directive "Archive rows to S3 cold storage instead"
```

---

## 10. Web Mission Control & Attack Simulator

Launch the Cyber-Sentry UI:
```bash
# Start backend daemon:
python run.py serve --port 8000

# Start frontend (port 3000):
cd frontend
npm run dev
```
Open **`http://localhost:3000`** in your browser:
- **Simulator (`#playground`):** Interactive adversarial sandbox testing TabPFN interception in real-time.
- **Mission Control (`/console`):** 3-stage governance console with live fleet telemetry, cost curves, and HITL authorization buttons.
- **Active Defense (`/defense`):** Interactive testbenches for DLP secret redaction, swarm deadlock cycle breaking, and blast radius scoring.

---

## 11. Configuration Reference (`.env`)

| Variable | Default | Purpose |
| :--- | :--- | :--- |
| `TABPFN_API_KEY` | None | Prior Labs cloud API authentication |
| `TABPFN_MODEL` | `tabpfn-3.5-classification` | Model variant |
| `TABPFN_THINKING_MODE` | `true` | Enables test-time Bayesian reasoning |
| `RISK_THRESHOLD_KILL` | `0.85` | TabPFN failure probability threshold to trigger KILL |
| `RISK_THRESHOLD_PAUSE` | `0.65` | Threshold to trigger Human-in-the-Loop PAUSE |
| `DAILY_FLEET_BUDGET_USD` | `50.00` | Daily spend ceiling across all fleet agents |
| `SESSION_MAX_COST_USD` | `5.00` | Max spend ceiling for any single agent session |
| `DB_PATH` | `data/agentry_audit.db` | SQLite ACID audit log destination |
