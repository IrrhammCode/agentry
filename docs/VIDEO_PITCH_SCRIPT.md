# 🎬 Agentry: Video Pitch Script & Storyboard (2 Minutes 30 Seconds)

**Target Event:** Prior Labs TabPFN-3.5 Global Hackathon (October 2026)  
**Tone:** Confident, fast-paced, high-tech, authoritative, engineering-first.  
**Recommended Recording Setup:** 1080p / 60fps screen recording (OBS Studio) with microphone audio.

---

## ⏱️ Video Structure Breakdown

| Time | Scene | Visual On-Screen | Audio / Spoken Topic |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:30** | **Scene 1: The Urgent Problem** | Code editor with an agent in an infinite bash loop + token bill climbing | The silent catastrophe of autonomous agent fleets: Infinite loops & runaway costs |
| **0:30 - 1:15** | **Scene 2: The Solution & TabPFN-3.5** | Agentry Architecture Diagram + Mermaid flow | Why TabPFN-3.5 is the secret weapon: sub-15ms tabular ICL, Thinking Mode, & 100% local privacy |
| **1:15 - 2:00** | **Scene 3: Live Action Demo** | Streamlit Command Center & Terminal CLI live execution | Live defense on real SWE-bench data: `KILL`, `REROUTE`, and forensic session inspection |
| **2:00 - 2:30** | **Scene 4: Benchmark & Impact** | Benchmark comparison table & GitHub repo | Outperforming classical ML, saving $1,000s in compute, and next steps |

---

## 📜 Complete Scene-by-Scene Script

### 🎬 Scene 1: The Urgent Hook (0:00 - 0:30)
**[Visual Cue]:**  
*Screen starts with a split view: on the left, a terminal running an AI coding agent repeatedly failing a test with `syntax error` and rerunning bash; on the right, an API cost dashboard spiraling up.*

**[Speaker / Voiceover]:**  
> *"Autonomous AI agents are building software, managing cloud infrastructure, and automating our digital world.*  
>  
> *But behind closed doors, every enterprise running agent fleets faces a silent, expensive nightmare: **catastrophic fleet casualties**.*  
>  
> *Agents get trapped in infinite retry loops, hallucinate non-existent tools, and blow past context windows — burning hundreds of dollars in API credits before human operators even notice.*  
>  
> *Existing guardrails try to solve this by calling yet another Cloud LLM. But that introduces a 2-second latency penalty, doubles your API bill, and leaks your proprietary code to third-party servers.*  
>  
> *What if there was a way to monitor agent health in milliseconds — with zero prompt leakage?"*

---

### 🎬 Scene 2: Introducing Agentry & TabPFN-3.5 (0:30 - 1:15)
**[Visual Cue]:**  
*Transition to the clean, modern Agentry Architecture Diagram from the README. Zoom into the TabPFN-3.5 engine and the local Ollama Qwen 2.5 badge.*

**[Speaker / Voiceover]:**  
> *"Meet **Agentry**: the autonomous tabular guardrail and real-time sentry for AI agent fleets.*  
>  
> *Our breakthrough insight is simple: **Agent execution telemetry is inherently tabular**.*  
> *Token velocity, repetition entropy, error streaks, latency, and thought length form a continuous tabular stream per session.*  
>  
> *Instead of slow LLM-as-a-judge, Agentry uses **Prior Labs' TabPFN-3.5 Foundation Model** as its core risk engine.*  
> *Using TabPFN's In-Context Learning with **Thinking Mode**, `group_col='session_id'`, and `group_time_col='step_index'`, Agentry performs multiclass failure classification and runaway cost regression in **under 15 milliseconds**.*  
>  
> *And for security? All semantic reasoning and intervention directives are dispatched to a **100% local SLM** — Qwen 2.5 running on edge GPU via Ollama. Your code, credentials, and internal prompts **never leave localhost**."*

---

### 🎬 Scene 3: Live Demo on Real SWE-bench Telemetry (1:15 - 2:00)
**[Visual Cue]:**  
*Switch screen to the **Streamlit Web Command Center** (`python run.py web`). Show the live radar, scrub across steps, and then run `python run.py demo` in the terminal to show real-time intervention.*

**[Speaker / Voiceover]:**  
> *"Let's see Agentry in action on **real-world data**. We evaluated Agentry on 739 real coding steps from the official SWE-bench trajectories on Hugging Face.*  
>  
> *(Point cursor at the Streamlit Radar Chart)*  
> *Here on the Agentry Command Center, we observe four concurrent agents. Notice Agent SWE-AnalogJ:*  
> *At step 0 and 1, execution is nominal. But by step 3, error streak begins to mount, and repetition entropy spikes.*  
>  
> *(Show Terminal CLI running `python run.py audit` or `python run.py demo`)*  
> *In less than 10 milliseconds, TabPFN-3.5 flags a 100% probability of **COST_RUNAWAY** and projects a 45-cent budget blowout.*  
>  
> *Immediately, our local Sentry triggers an autonomous **KILL intervention**!*  
> *In the unmonitored baseline, this agent looped blindly for **46 steps**, reaching an error streak of 13. Agentry killed it at step 3 — **saving 43 wasted steps and 85% of token expenses**."*

---

### 🎬 Scene 4: Empirical Benchmark & Conclusion (2:00 - 2:30)
**[Visual Cue]:**  
*Show the Empirical Benchmark Table on screen, highlighting TabPFN's 56.0% Balanced Accuracy and $0.0088 Cost MAE, then switch to the GitHub repository [IrrhammCode/agentry](https://github.com/IrrhammCode/agentry) showing the green CI badges and clean code.*

**[Speaker / Voiceover]:**  
> *"In our empirical benchmark against classical ML baselines on real agent telemetry, TabPFN achieves the highest balanced accuracy of **56.0%**, a macro F1 of **55.8%**, and predicts final costs with an astonishing Mean Absolute Error of **less than one cent ($0.0088)**.*  
>  
> *No manual feature engineering. No hyperparameter tuning. Just state-of-the-art tabular in-context learning.*  
>  
> *Agentry provides modern packaging, a 1-click Jupyter walkthrough notebook, and full zero-mock reproducibility.*  
>  
> *Check out our open-source repository at `github.com/IrrhammCode/agentry`. Protect your fleets, safeguard your budget, and build autonomous agents that never derail.*  
>  
> *Thank you, Prior Labs!"*

---

## 💡 Quick Tips for the Presenter (Catatan untuk Perekaman):

1. **Persiapan Layar Sebelum Rekam:**
   * Buka Terminal PowerShell di direktori `C:\Users\Irham\Documents\code\tabfpn`.
   * Jalankan `.\.venv\Scripts\python run.py web` di satu terminal (buka `http://localhost:8501` di browser).
   * Siapkan terminal kedua dengan font besar (Consolas 18pt) untuk menjalankan `.\.venv\Scripts\python run.py demo` dan `.\.venv\Scripts\python run.py audit`.
2. **Kualitas Audio:**
   * Berbicara dengan tempo santai tapi tegas (energetic).
   * Jangan terburu-buru di bagian demo: beri jeda 1 detik saat `KILL` muncul di terminal agar penonton bisa melihat tulisan merah `KILL` dan angka risiko `100.0%`.
3. **Screen Recording:**
   * Resolusi layar 1920x1080 disarankan untuk ketajaman teks terminal dan grafik Plotly.
