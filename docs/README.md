# 📚 Agentry Documentation Hub

Welcome to the official documentation directory for **Agentry**—the autonomous tabular guardrail and sentry for AI agent fleets, powered by the **Prior Labs TabPFN-3.5** foundation model.

---

## 🗂️ Documentation Navigation

| Document | Description |
| :--- | :--- |
| [**📖 How to Use Agentry (`HOW_TO_USE.md`)**](./HOW_TO_USE.md) | **Start here!** Complete installation, integration guides (OpenAI Proxy, Python SDK, REST API daemon, MCP server), trajectory rewind, and Web Console walkthrough. |
| [**📡 REST API Reference (`API_REFERENCE.md`)**](./API_REFERENCE.md) | Full technical specification of all REST endpoints, JSON payload schemas, query parameters, and cURL examples. |
| [**💡 Innovation Ideas & Roadmap (`IDEAS_AND_ROADMAP.md`)**](./IDEAS_AND_ROADMAP.md) | Deep brainstormed concepts (*"Cari Ide"*): Tabular prompt injection fingerprinting, eBPF kernel sandboxing, red-team fuzzers, and hackathon presentation strategy. |
| [**🔬 Empirical Research Paper (`EMPIRICAL_RESEARCH_PAPER.md`)**](./EMPIRICAL_RESEARCH_PAPER.md) | Formal scientific evaluation of TabPFN-3.5 vs XGBoost, Random Forest, and LLM baselines across 1,725 SWE-bench agent execution steps. |
| [**🎬 Video Pitch Script (`VIDEO_PITCH_SCRIPT.md`)**](./VIDEO_PITCH_SCRIPT.md) | Step-by-step 3-minute hackathon pitch script with timestamped screen recordings and narration cues. |

---

## ⚡ Quick 30-Second Start

```bash
# 1. Start the Agentry Sentry Daemon & OpenAI Proxy
python run.py serve --port 8000

# 2. In another terminal, launch the modern Cyber-Sentry UI
cd frontend && npm run dev
```

Point any OpenAI-compatible client to:
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://127.0.0.1:8000/v1",
    api_key="upstream-key",
    default_headers={"X-Agent-Session": "swe_coder_01"}
)
```
Agentry will automatically redact credentials, evaluate telemetry in **14.8 milliseconds** with TabPFN, and halt destructive actions before execution.
