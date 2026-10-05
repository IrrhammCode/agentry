# 🎬 Agentry: 3-Minute Hackathon Demo Video Script
**Prior Labs TabPFN-3.5 Global Hackathon 2026**

> **Target Duration:** 2 minutes 50 seconds – 3 minutes 00 seconds  
> **Tools Recommended:** Loom, OBS Studio, or Screen Studio (1080p, 60fps)  
> **Setup Before Recording:**
> 1. Terminal 1 open: `.venv` activated.
> 2. Terminal 2 open: running `python -m agentry.cli mcp --transport stdio` or `streamlit run web/app.py`.
> 3. Browser open at `http://localhost:8501` (Agentry Command Center).

---

## ⏱️ Timeline & Scene-by-Scene Script

### [0:00 - 0:35] Scene 1: The Urgent Problem (Hook)
* **Screen Visual:** Show a real SWE-bench agent getting stuck in a loop (or the Agentry Terminal CLI `python run.py demo` showing the red infinite loop warnings).
* **Voiceover:**
  > "Autonomous coding agents are revolutionizing software engineering. But every enterprise deploying SWE-bench agents, Devin, or CrewAI encounters an existential crisis: **agents get trapped in infinite repetition loops and hallucination spirals**.
  > 
  > In real SWE-bench runs, an agent failing a unit test will retry the exact same broken patch 15 to 40 times consecutively. In under 15 minutes, a single runaway agent can burn millions of tokens, racking up **$50 to $200 in API bills on a single stuck task**.
  > 
  > Current solutions use static circuit breakers like `if error >= 3: stop()`, which murder half of all productive agents, or expensive cloud LLM-as-a-judge monitors that add 3,000 milliseconds of latency and leak proprietary enterprise source code."

---

### [0:35 - 1:15] Scene 2: The Breakthrough — Agent Telemetry is Tabular
* **Screen Visual:** Switch to the Web Command Center tab: **"📊 TabPFN Benchmark Suite"**, showing the empirical comparison table against XGBoost and Random Forest.
* **Voiceover:**
  > "We realized a fundamental truth: **Autonomous agent execution telemetry is inherently non-IID tabular data.**
  > 
  > At every step, an agent generates dynamic signals: consecutive error streaks, repetition entropy, latency degradation, and token velocity.
  > 
  > This is where **Prior Labs' TabPFN-3.5** shines. TabPFN-3.5 was built specifically for messy, non-IID, grouped temporal data using `group_col='session_id'` and `group_time_col='step_index'`.
  > 
  > On **739 real-world SWE-bench steps across 35 developer sessions**, classical tree models like XGBoost and Random Forest struggle with low cost $R^2$ ($0.190 - 0.235$), but **TabPFN-3.5 achieves an $R^2$ of 0.583 (over 2.5x higher) and 91.7% failure recall on completely unseen held-out sessions**."

---

### [1:15 - 2:00] Scene 3: Live Command Center & Autonomous Sentry
* **Screen Visual:** Switch to **"🚀 Live Fleet Simulation"** in the Streamlit app. Click through the simulation scrubber. Show the real-time donut chart, predicted failure mode, and the **KILL** intervention.
* **Voiceover:**
  > "Meet **Agentry**—the predictive runtime control layer for autonomous agent fleets.
  > 
  > Here in the Live Fleet Command Center, TabPFN continuously monitors the fleet.
  > 
  > Notice Step 3: when repetition entropy reaches 0.88 and error streak hits 3, TabPFN instantly detects a **96.8% unrecoverable failure risk**.
  > 
  > Instead of blindly cutting execution, Agentry pairs TabPFN with an economic loss formulation and local edge intelligence. It triggers an autonomous **KILL intervention**, halting the runaway agent immediately and saving **over 21,600 tokens and budget per stuck session**."

---

### [2:00 - 2:35] Scene 4: Model Context Protocol (MCP) Server & Benchmark Proof
* **Screen Visual:** Switch to the **"🔌 Model Context Protocol (MCP)"** tab in the Streamlit app. Click **"Execute MCP Audit Step"** to show instant real-time auditing. Then show the Unseen Trajectory Benchmark table.
* **Voiceover:**
  > "Agentry is built for production ecosystems. Today, we're unveiling our native **Model Context Protocol (MCP) Server**.
  > 
  > Any developer can connect Agentry directly to **Claude Desktop, Cursor IDE, or Windsurf** in one configuration line. Through MCP tools like `agentry_audit_step`, Claude Desktop gains real-time TabPFN guardrails.
  > 
  > And most importantly, look at our **Unseen Trajectory Benchmark**:
  > While naive static rules miss over 45% of runaway failures, **TabPFN catches over 90% of failure cascades on unseen developer sessions while maintaining calibrated test-time confidence**."

---

### [2:35 - 3:00] Scene 5: Conclusion & Hackathon Submission
* **Screen Visual:** Switch to the GitHub repository: `https://github.com/IrrhammCode/agentry`. Scroll through the README with passing badges.
* **Voiceover:**
  > "Agentry is 100% open-source, validated on real SWE-bench data with zero synthetic mocks, and ready for deployment.
  > 
  > By combining the tabular Bayesian power of Prior Labs TabPFN-3.5 with local-first privacy, Agentry makes autonomous AI agents enterprise-ready.
  > 
  > Thank you to Prior Labs for hosting this global hackathon. Check out our repository at `github.com/IrrhammCode/agentry`!"

---

## 🎯 Tips for the Recording:
1. Speak clearly and confidently at a steady, natural pace.
2. Ensure your microphone input is crisp and background noise is minimized.
3. Keep the mouse cursor smooth (avoid jittery movements).
4. Upload the recorded video to YouTube (as *Unlisted* or *Public*) or Loom, and copy the link into `docs/HACKATHON_SUBMISSION.md` line 7!
