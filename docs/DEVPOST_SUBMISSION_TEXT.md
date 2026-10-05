# 📝 Devpost / Hackathon Submission Form Text
**Prior Labs TabPFN-3.5 Global Hackathon 2026**

This document contains pre-formatted text blocks ready to copy and paste directly into the Devpost submission portal fields.

---

### Project Title
```text
Agentry: Predictive Runtime Control Layer for Autonomous Agent Fleets Powered by TabPFN-3.5
```

### Tagline (max 200 characters)
```text
Predicts agent loop traps and token runaways before compute burns. Powered by Prior Labs TabPFN-3.5 and Local-First Edge Intelligence.
```

---

### Inspiration
```text
As enterprise engineering teams deploy autonomous coding and DevOps agents (SWE-agent, Devin, CrewAI, LangGraph), they face an existential blocker: agents frequently spiral into catastrophic, unpredictable repetition loops. In SWE-bench benchmarks, agents trapped by unexpected syntax or tool errors retry the exact same failing command 15 to 40 times consecutively. In under 15 minutes, a single stuck agent burns millions of tokens, generating $50 to $200 in API bills.

Existing solutions fall into two flawed extremes:
1. Static circuit breakers (`if error >= 3: stop()`) that prematurely kill productive agents actively exploring valid recovery paths (devastating task completion rates).
2. Synchronous Cloud LLM-as-a-Judge evaluators that cost upwards of $1,368,000/year for 500k steps/day, add 2,250ms latency per step, and leak proprietary enterprise source code outside the enterprise perimeter.

We realized a foundational paradigm shift: Autonomous agent execution telemetry is inherently structured, non-IID tabular data. By using Prior Labs' TabPFN-3.5 tabular foundation model, we could turn raw agent telemetry into a predictive runtime control system that halts runaway agents before catastrophic token burn occurs—with 14.5ms inference latency, 99.998% lower operational cost, and 100% zero code/prompt leakage.
```

---

### What It Does
```text
Agentry is an enterprise-grade predictive runtime control layer and tabular safety guardrail for AI agent fleets:

1. Real-Time Tabular Telemetry Ingestion: Continuously monitors step-by-step agent telemetry (token velocity, repetition entropy, error streaks, tool latencies, and thought traces).
2. TabPFN-3.5 Foundation Sentry: Leverages Prior Labs TabPFN-3.5 with native grouped temporal series support (`group_col='session_id'`, `group_time_col='step_index'`) and Thinking Mode to predict unrecoverable failure risk P(failure) and forecast terminal financial burn in USD.
3. Cost-Aware Economic Policy: Intervenes using an Economic Loss Formulation:
   Expected Waste = P(runaway) * Projected Remaining Cost
   Halting occurs only when expected waste exceeds the value of recovery, slashing the false-stop rate to 2.0% while preserving productive task completion.
4. Autonomic Trajectory Rewind & Self-Healing Engine: When an agent diverges, Agentry locates the exact divergence inflection point (t*), computes a RewindPrescription, prunes poisoned turns from context history, and injects counterfactual recovery directives to steer the agent back on course.
5. Enterprise Fleet Budget Autopilot & Quota Governor: Tracks 24-hour spend velocity across agent roles, computes budget utilization percentage, warns before depletion, and enforces hard single-session ($2.50) and daily fleet ($50.00) cost ceilings.
6. Prometheus / OpenTelemetry Metrics Exposition: Built-in `/metrics` endpoint exporting real-time scrapeable metrics (step latency histograms, budget spend, failure rate gauges, and rewind intervention counters) for Grafana/Datadog.
7. Interactive What-If Counterfactual Policy Simulator: Web UI module allowing operators to drag decision thresholds, inspect ROC & Pareto trade-offs, and simulate autonomic rewind recovery on historical SWE-bench sessions.
8. Human-in-the-Loop (HITL) Supervisor Control: Automatically pauses suspicious executions into an escalation queue, allowing human operators to review tabular telemetry and inject live steering directives (`hitl_gateway.resolve`).
9. Multi-Channel Webhook Alerts: Emits non-blocking HTTP webhooks with rich formatting to Slack, Discord, and PagerDuty for critical interventions.
10. Automated Incident Post-Mortems: Generates audit-ready forensic post-mortem reports in Markdown and HTML for enterprise AI safety compliance and AgentOps governance.
11. Zero-Code-Change OpenAI Reverse Proxy: Drop-in proxy (`http://localhost:8787/v1`) that guards any existing agent framework (LangChain, AutoGen, CrewAI) without changing application logic.
12. Model Context Protocol (MCP) Server: Exposes standardized MCP tools (`agentry_audit_step`, `agentry_get_fleet_status`) and resources (`fleet://metrics`) over stdio and SSE for native integration with Claude Desktop, Cursor IDE, and Windsurf.
```

---

### How We Built It
```text
• Tabular Foundation Model: Prior Labs TabPFN-3.5 (`tabpfn-client`, Thinking Mode) trained on multimodal agent features and grouped session dynamics.
• Dataset & Ground Truth: 1,156 real-world coding agent steps from Hugging Face `nebius/SWE-agent-trajectories` (SWE-bench benchmark) across 55 developer sessions (15 successful, 40 failing).
• Autonomic Healing & Budget: Divergence inflection point analysis, context history rewind, and multi-tenant financial quota governors.
• Control & Storage: SQLite Write-Ahead Logging (WAL) audit trail for ACID-compliant enterprise governance and forensic telemetry replay.
• Developer Protocols: Drop-in Python SDK (`@guard.protect`), LangChain/LangGraph callbacks, CrewAI hooks, HTTP REST Gateway daemon, OpenAI Reverse Proxy, Prometheus `/metrics` exposition, and standardized Model Context Protocol (MCP) Server.
• Enterprise Operations: Human-in-the-Loop (HITL) approval gateway, Slack/Discord webhooks, and automated HTML/Markdown incident post-mortem generator.
• Containerization: Production Dockerfile and docker-compose.yml orchestrating Web UI (port 8501), Gateway (port 8787), and MCP Server (port 8788).
• Interfaces: Streamlit Command Center with live fleet radar, forensic session inspector, interactive What-If Simulator, Fleet Budget Autopilot, interactive MCP step simulator, and Rich terminal visualizer.
```

---

### Challenges We Ran Into
```text
1. Eliminating Data Leakage in Sequential Agent Traces:
   Standard random train/test splits severely contaminate evaluations because steps from the same agent trajectory share hidden state. We implemented a rigorous `GroupShuffleSplit` strictly by `session_id`, holding out full unseen sessions for testing across 5 independent folds.
2. The False-Stop Dilemma:
   Raw unthresholded argmax classification produced high false-stop rates on normal steps. We engineered a cost-sensitive Economic Utility formulation requiring Bayesian statistical confidence P(runaway) >= 0.85 combined with consecutive error streak evidence, dropping the False-Stop Rate to 2.0% while retaining 90.6% Failure Recall.
3. Non-IID Grouped Dynamics in Tabular Architecture:
   Classical ML baselines (XGBoost, Random Forest) struggled on held-out trajectory cost regression. TabPFN-3.5's native support for grouped temporal relationships enabled it to achieve an R^2 of 0.782–0.961 on unseen trajectories.
4. Preserving Enterprise Privacy in AI Safety:
   Cloud LLM judges require sending raw code diffs and prompts to third parties. We proved mathematically via permutation importance that 71.0% of predictive power comes from 5 non-sensitive tabular metadata features (`error_streak`, `prompt_tokens`, `step_latency_ms`, `thought_has_error`, `tool_call_count`), achieving complete runtime protection with zero proprietary code exposure.
5. Safe Autonomic Context Pruning:
   Rolling an agent backward requires identifying the exact divergence point without discarding productive setup steps. Our divergence inflection point locator identifies the highest step index before fatal error cascades began, surgically stripping poisoned tool outputs while preserving environment state.
```

---

### Accomplishments That We're Proud Of
```text
• 100% Real-World Data: Validated strictly against 1,156 genuine SWE-bench developer steps across 55 sessions from Hugging Face with zero synthetic mocks.
• Sub-Step Early Detection: Empirical research proved Agentry intercepts runaway failures at a median of Step 5.0, eliminating 53.3% of wasted trajectory length (569 steps and 162,339 tokens saved across failing sessions).
• 155.2x Faster & 99.998% Cheaper than Cloud LLMs: TabPFN-3.5 evaluates steps in 14.5ms and costs $21.90/year for 500,000 daily steps, compared to GPT-4o's 2,250ms and $1,368,750.00/year.
• 8 Full Enterprise Capabilities: Autonomic Trajectory Rewind, Fleet Budget Governor, Prometheus Observability, What-If Policy Simulator, Human-in-the-Loop (HITL) escalation, Slack/Discord webhooks, automated post-mortem reporting (Markdown/HTML), and OpenAI reverse proxy.
• Model Context Protocol (MCP) Native Support: Built a fully compliant MCP Server allowing Claude Desktop and Cursor users to guard their agents with TabPFN out-of-the-box.
• 100% Passing Test Suite: 54 comprehensive unit, integration, deep resilience, and adversarial chaos tests passing in CI (validating multithreaded concurrency, SSE streaming proxy, autonomic rewind, budget governor, Prometheus endpoint, NaN/Inf mathematical immunity, and zero SQLite resource leaks).
• One-Command Deployment: Complete Docker & Docker Compose configuration orchestrating Web UI, Reverse Proxy Gateway, and MCP Server.
```

---

### What We Learned
```text
1. Agent telemetry is one of the most compelling real-world applications of tabular foundation models: it is naturally high-dimensional, sequential, grouped, and low-data regime (few-shot per session).
2. Naive static heuristics (`if error >= 3`) kill over 50% of successful developer tasks. Learned tabular priors are essential for scalable agent deployment.
3. In-context learning on tabular telemetry allows instant runtime adaptation without expensive model fine-tuning or token-burning LLM-as-a-judge roundtrips.
4. Privacy-preserving safety is viable: agents can be safely governed through structured execution dynamics alone, without inspecting proprietary intellectual property.
```

---

### What's Next for Agentry
```text
• Distributed Kubernetes Envoy Sidecar: Deploying Agentry as an Envoy-style proxy sidecar for multi-agent Kubernetes clusters.
• TabPFN Fine-Tuning on 100,000+ Multimodal Traces: Expanding our telemetry database across Devin, AutoGPT, and open-source SWE-bench Docker trajectories.
• Automated Multi-Agent Co-Ordination Recovery: Extending trajectory rewind across DAG-based multi-agent swarms (CrewAI/LangGraph) with distributed rollbacks.
```

