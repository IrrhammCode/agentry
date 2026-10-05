# 📝 Devpost / Hackathon Submission Form Text
**Prior Labs TabPFN-3.5 Global Hackathon 2026**

This document contains pre-formatted text blocks ready to copy and paste directly into the Devpost submission portal fields.

---

### Project Title
```text
Agentry: Autonomous Tabular Guardrail & Sentry for AI Agent Fleets Powered by TabPFN-3.5
```

### Tagline (max 200 characters)
```text
Stops AI agent loops, cost runaways, and catastrophic shell mutations in real time using Prior Labs TabPFN-3.5 tabular Bayesian intelligence.
```

---

### Inspiration
```text
As engineering teams deploy autonomous coding and DevOps agents (SWE-bench, Devin, CrewAI, LangGraph), they face an existential blocker: agents frequently spiral into catastrophic, unpredictable repetition loops. In SWE-bench benchmarks, agents trapped by unexpected syntax or tool errors retry the exact same failing command 15 to 40 times consecutively. In under 15 minutes, a single stuck agent burns millions of tokens, generating $50 to $200 in API bills.

Existing solutions fall into two flawed extremes:
1. Static circuit breakers (`if error >= 3: stop()`) that prematurely kill productive agents actively exploring valid recovery paths (devastating task completion rates).
2. Synchronous Cloud LLM-as-a-Judge evaluators that add 2,000+ ms of latency per step, double API token bills, and leak proprietary enterprise source code outside the enterprise perimeter.

We realized a foundational paradigm shift: Autonomous agent execution telemetry is inherently structured, non-IID tabular data. By using Prior Labs' TabPFN-3.5 tabular foundation model, we turned raw agent telemetry into a predictive runtime sentry that halts runaway agents before catastrophic token burn occurs—with real-time Bayesian tabular inference, dramatically lower operational cost than LLM-as-a-judge, and zero internal code leakage.
```

---

### What It Does
```text
Agentry is an enterprise-grade predictive runtime control layer and tabular safety guardrail for AI agent fleets:

1. Primary Sentry (Prior Labs TabPFN-3.5): Telemetry steps (token velocity, repetition score, error streaks, tool latencies, and thought lengths) are evaluated by TabPFN-3.5 foundation models (`group_col='session_id'`, `group_time_col='step_index'`). It predicts failure probabilities across `INFINITE_LOOP`, `TOOL_HALLUCINATION`, and `COST_RUNAWAY`, while forecasting remaining token spend.
2. Pre-Execution Blast-Radius Hard Stop: Secondary regex interceptor that inspects catastrophic commands (`rm -rf /`, `DROP DATABASE`, raw disk writes) BEFORE execution occurs, acting as a deterministic safety backstop.
3. Cost-Aware Economic Policy: Intervenes using an Economic Loss Formulation:
   Expected Waste = P(runaway) * Projected Remaining Cost
   Halting occurs only when expected waste exceeds the value of recovery, preserving productive task exploration.
4. Autonomic Trajectory Rewind & Healing: When an agent diverges, Agentry pinpoints the divergence inflection point, rolls back the filesystem snapshot via git checkpoints, and injects counterfactual steering directives.
5. In-Flight DLP Sanitizer: Masks high-entropy credentials (OpenAI keys, GitHub tokens) before network egress.
6. Multi-Protocol Integration:
   - Python SDK: Drop-in `@guard.protect` decorator.
   - MCP Server: Standardized Model Context Protocol tools for Claude Desktop, Cursor, and Windsurf.
   - REST API Daemon: Fast HTTP gateway with Prometheus `/metrics` exposition.
7. Mission Control & Attack Simulator: Real-time web console with live fleet radar, forensic audit inspector, and interactive adversarial attack simulator.
```

---

### How We Built It
```text
• Tabular Foundation Model: Prior Labs TabPFN-3.5 (`tabpfn-client`) using in-context Bayesian inference and temporal grouped session structures. Includes an offline scikit-learn fallback (HistGradientBoosting) when operating in air-gapped environments without API tokens.
• Dataset & Ground Truth: 1,156 genuine coding agent steps across 55 developer sessions from Hugging Face `nebius/SWE-agent-trajectories` (SWE-bench benchmark).
• Strict Group Evaluation: Zero step-leakage evaluation using `GroupShuffleSplit` on `session_id`, holding out 17 complete unseen sessions for testing.
• Autonomic Recovery: Divergence inflection point locator, git state checkpointing, and counterfactual steering.
• Infrastructure & Protocols: FastAPI REST daemon, Model Context Protocol (MCP) server over stdio/SSE, SQLite WAL forensic audit storage, Prometheus metrics exporter, and Docker Compose orchestration.
• Frontend Console: Modern React + Vite + Tailwind CSS cyber-sentry mission control with live attack simulator and telemetry tickers.
```

---

### Challenges We Ran Into
```text
1. Eliminating Data Leakage in Sequential Agent Traces:
   Standard random train/test splits severely contaminate evaluations because steps from the same agent trajectory share hidden state. We implemented a rigorous `GroupShuffleSplit` strictly by `session_id`, testing on completely unseen agent sessions across independent folds.
2. The False-Stop Dilemma:
   Naive static rules (`if error >= 3`) catch only 54.4% of runaway failures while causing a 17.4% False-Stop Rate on productive agents. We engineered a cost-sensitive Economic Utility formulation requiring Bayesian statistical confidence P(runaway) combined with consecutive error streak evidence.
3. Defense-in-Depth Pipeline Separation:
   Balancing statistical tabular forecasting with deterministic safety required establishing clean pipeline boundaries: TabPFN-3.5 scores telemetry and financial risk, while semantic blast-radius interceptors act as pre-execution hard stops for destructive mutations.
4. Preserving Enterprise Privacy:
   Cloud LLM monitors require sending raw code diffs and proprietary prompts to third parties. We demonstrated that predictive runtime safety is driven by structured tabular metadata features without exposing private repository code.
```

---

### Accomplishments That We're Proud Of
```text
• Empirical Superiority on Unseen Trajectories: On 17 held-out SWE-bench sessions, TabPFN-3.5 achieves 91.7% Failure Recall, 60.1% Balanced Accuracy, and 58.7% Macro F1, outperforming tuned XGBoost (82.2% recall, 55.9% balanced acc) and Random Forest without hyperparameter search.
• Fast & Economical: ~28 ms per row batch-amortized inference in our benchmark, avoiding expensive 2,000+ ms LLM-as-a-judge roundtrips.
• Production Ecosystem Support: Standardized Model Context Protocol (MCP) server for Claude Desktop and Cursor, plus drop-in Python decorator `@guard.protect`.
• 100% Green Test Suite: 89 passing unit, resilience, and adversarial tests in CI.
• Open-Source & Reproducible: Released under Apache-2.0 license with reproducible benchmark scripts (`python run.py benchmark`).
```

---

### What We Learned
```text
1. Agent telemetry is one of the most natural, high-impact real-world applications of tabular foundation models: high-dimensional, sequential, grouped, and low-data regime (few-shot per session).
2. Naive static heuristics kill over 45% of productive recovery paths. Learned tabular priors are essential for reliable autonomous agent operations.
3. In-context learning on tabular telemetry allows instant runtime adaptation without hours of offline fine-tuning or token-burning LLM-as-a-judge calls.
```

---

### What's Next for Agentry
```text
• Envoy Sidecar Architecture: Deploying Agentry as a lightweight sidecar container for Kubernetes agent clusters.
• Expanded Fleet Datasets: Incorporating multi-agent telemetry traces from Devin, AutoGPT, and SWE-bench Docker environments.
• Multi-Agent DAG Rollbacks: Extending autonomic rewind across distributed DAG agent networks (CrewAI/LangGraph).
```
