# 🎬 Agentry: 3-Minute Hackathon Demo Video Script
**Prior Labs TabPFN-3.5 Global Hackathon 2026**

> **Target Duration:** 2 minutes 45 seconds – 3 minutes 00 seconds  
> **Recommended Screen Resolution:** 1080p, 60fps (Loom, OBS Studio, or Screen Studio)  
> **Pre-Recording Checklist:**
> 1. Terminal 1: `.venv` activated, ready to run `python run.py benchmark` or `python run.py demo`.
> 2. Terminal 2: Running backend daemon `python run.py serve --port 8000`.
> 3. Browser Tab 1: `http://localhost:3000` (Cyber-Sentry Web Console & Mission Control).
> 4. Browser Tab 2: `https://github.com/IrrhammCode/agentry` (GitHub repo).

---

## ⏱️ Timeline & Scene-by-Scene Script

### [0:00 - 0:30] Scene 1: The Urgent Problem (Hook)
* **Screen Visual:** Split screen showing an autonomous coding agent failing a unit test in loop and burning tokens, or the Terminal running `python run.py demo` showing rogue agents.
* **Click-Path:** Start on Terminal 1 or Mission Control (`http://localhost:3000`).
* **Spoken Script (Voiceover):**
  > "Autonomous coding agents are revolutionizing software engineering. But every team deploying SWE-bench agents, Devin, or LangGraph hits a painful wall: **agents get trapped in repetitive error spirals and catastrophic hallucination loops.**
  > 
  > In real SWE-bench benchmarks, an agent that fails a test often repeats the same flawed attempt 15 to 40 times. Within 15 minutes, a single stuck loop burns hundreds of thousands of tokens, racking up $50 to $200 in cloud bills on a single unresolved task.
  > 
  > Static rules like `if error >= 3: stop()` kill productive agents that are exploring valid recoveries, while synchronous Cloud LLM judges add thousands of milliseconds of latency and leak proprietary codebase IP."

---

### [0:30 - 1:15] Scene 2: The Breakthrough — Agent Telemetry is Tabular Non-IID Data
* **Screen Visual:** Switch to browser showing `data/benchmark_group_results.md` or Mission Control benchmark view.
* **Click-Path:** Scroll through the Unseen Trajectory Benchmark table.
* **Spoken Script (Voiceover):**
  > "We realized a fundamental breakthrough: **AI agent execution telemetry is inherently non-IID tabular data.**
  > 
  > Every step generates numerical telemetry: consecutive error streaks, repetition entropy, latency shifts, and token velocities grouped by session.
  > 
  > This is where **Prior Labs TabPFN-3.5** shines. TabPFN-3.5 was designed specifically for tabular foundation learning, with native temporal grouped support (`group_col='session_id'`, `group_time_col='step_index'`).
  > 
  > Evaluating on **1,156 genuine SWE-bench steps across 55 developer sessions** with strict `GroupShuffleSplit` on `session_id`—guaranteeing zero cross-step leakage—**TabPFN-3.5 achieves 91.7% failure recall on completely unseen held-out sessions**, outperforming tuned XGBoost and Random Forest with zero hyperparameter search."

---

### [1:15 - 1:55] Scene 3: Live Mission Control & Attack Simulator
* **Screen Visual:** Switch to `http://localhost:3000` (Agentry Mission Control / Attack Simulator).
* **Click-Path:** 
  1. Show the Attack Simulator with the default **TabPFN Runaway Loop & Error Spiral** preset.
  2. Click **"Run Sentry Scan"** or **"Test TabPFN Audit"** in Mission Control.
  3. Show the live TabPFN-3.5 probability output ($P(\text{failure}) = 94.6\%$, predicted mode `INFINITE_LOOP`, circuit breaker tripped).
  4. Switch to the `rm -rf /` preset to show the secondary defense layer: the Semantic Blast-Radius Interceptor halting the command before shell execution.
* **Spoken Script (Voiceover):**
  > "Here is **Agentry Mission Control**. Every agent action is scored by TabPFN-3.5 in real time before execution.
  > 
  > In our Attack Simulator, notice our default preset: an agent caught in a 5x crash loop. TabPFN evaluates the tabular telemetry in ~28 ms batch-amortized, detecting an unrecoverable failure pattern and tripping the circuit breaker before tokens drain.
  > 
  > Furthermore, Agentry enforces defense-in-depth: while TabPFN handles tabular failure and cost prediction, our secondary semantic blast-radius interceptor catches catastrophic mutations like `rm -rf /` or `DROP TABLE` before the shell runs, and our in-flight DLP redacts secrets."

---

### [1:55 - 2:30] Scene 4: Production Integration & Model Context Protocol (MCP)
* **Screen Visual:** Show the terminal running `python run.py mcp` and the SDK code snippet in `README.md`.
* **Click-Path:** Highlight the 2-line `@guard.protect` Python decorator and show MCP server initialization.
* **Spoken Script (Voiceover):**
  > "Agentry is built for production environments. You can integrate it into any agent framework in two lines of Python using our `@guard.protect` decorator.
  > 
  > We also provide an official **Model Context Protocol (MCP) Server** running over stdio and SSE. Any developer using **Claude Desktop, Cursor, or Windsurf** can plug Agentry in immediately.
  > 
  > When an agent diverges, Agentry doesn't just halt—it pinpoints the exact divergence step, captures an autonomic git checkpoint, and generates counterfactual steering instructions."

---

### [2:30 - 2:50] Scene 5: Conclusion & Hackathon Submission
* **Screen Visual:** Switch to GitHub repository `github.com/IrrhammCode/agentry`. Show the passing test suite and clean documentation.
* **Click-Path:** Scroll past the Apache-2.0 badge and reproducible benchmark logs.
* **Spoken Script (Voiceover):**
  > "Agentry is open-source under the Apache-2.0 license, backed by 89 passing tests, and completely reproducible via `python run.py benchmark` connecting to the official Prior Labs TabPFN Cloud API.
  > 
  > By pairing the Bayesian tabular intelligence of TabPFN-3.5 with local-first autonomic protection, Agentry makes autonomous AI agent fleets reliable and enterprise-ready.
  > 
  > Thank you to Prior Labs for hosting this hackathon. Check out Agentry on GitHub!"

---

## 🎯 Recording Best Practices:
1. **Pacing:** Speak at a steady, engaging pace (~135-145 words per minute).
2. **Audio:** Use a dedicated headset or USB condenser mic in a quiet room.
3. **Cursor:** Keep cursor movements purposeful; point directly to the metrics as you speak them.
4. **Link:** Upload video to YouTube (Unlisted or Public) or Loom, and paste the URL into your Devpost submission!
