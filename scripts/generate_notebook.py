"""
Generates the Agentry interactive Jupyter Walkthrough notebook.
"""

import json
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

nb = {
    "cells": [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Agentry: Real-Time Tabular In-Context Sentry for Autonomous AI Agents\n",
                "### Powered by TabPFN-3.5 Foundation Model & Local Edge SLM (Qwen 2.5)\n",
                "\n",
                "**Prior Labs TabPFN-3.5 Global Hackathon 2026 Submission**\n",
                "\n",
                "Agentry is an autonomous safety, cost, and reliability guardrail for multi-agent fleets. It monitors real-time tabular execution telemetry (token burn rates, repetition entropy, error streaks, tool latencies, and thought traces) and detects catastrophic failure modes (**Infinite Loops**, **Context / Cost Runaways**, and **Tool Hallucinations**) in <5ms without expensive LLM-as-a-judge overhead."
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Import Dependencies & Initialize Agentry"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import pandas as pd\n",
                "import numpy as np\n",
                "from pathlib import Path\n",
                "\n",
                "from agentry.telemetry import load_telemetry_data, AgentStepTelemetry\n",
                "from agentry.engine import TabPFNGuardrailEngine\n",
                "from agentry.agent import AgentrySentry\n",
                "from agentry.benchmark import GuardrailBenchmarkSuite\n",
                "\n",
                "print(\"Agentry modules loaded successfully!\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Load Real-World SWE-bench Agent Telemetry\n",
                "We evaluate on genuine agent execution traces streamed from `nebius/SWE-agent-trajectories`."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "df = load_telemetry_data()\n",
                "print(f\"Total telemetry steps: {len(df)}\")\n",
                "print(f\"Unique agent sessions: {df['session_id'].nunique()}\")\n",
                "print(\"\\nFailure Mode Distribution:\")\n",
                "print(df['failure_status'].value_counts())\n",
                "df[['session_id', 'step_index', 'tool_name', 'error_streak', 'repetition_score', 'accumulated_cost_usd', 'failure_status']].head(10)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Fit TabPFN-3.5 Guardrail Engine\n",
                "TabPFN utilizes In-Context Learning (ICL) directly across multimodal tabular features: sequential grouped session dynamics (`group_col`, `group_time_col`), numerical metrics, and raw thought traces."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "engine = TabPFNGuardrailEngine()\n",
                "engine.fit(df)\n",
                "print(f\"Engine fitted successfully. Cloud TabPFN active: {engine.is_cloud_tabpfn}\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 4. Real-Time Step Risk Evaluation & Sentry Intervention\n",
                "Simulate a live agent step and observe the real-time TabPFN risk probability, predicted failure mode, cost projection, and Sentry intervention."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "sentry = AgentrySentry(engine)\n",
                "\n",
                "# Test step: Repetitive tool loop with an error streak\n",
                "risky_step = AgentStepTelemetry(\n",
                "    session_id=\"demo_run_01\",\n",
                "    step_index=4,\n",
                "    agent_role=\"SWE-Coder\",\n",
                "    model_name=\"swe-agent-llama-70b\",\n",
                "    tool_name=\"bash\",\n",
                "    step_latency_ms=2400.0,\n",
                "    prompt_tokens=18500,\n",
                "    completion_tokens=2200,\n",
                "    total_tokens=20700,\n",
                "    tool_call_count=5,\n",
                "    error_streak=3,\n",
                "    repetition_score=0.82,\n",
                "    thought_length=140,\n",
                "    accumulated_cost_usd=0.062,\n",
                "    thought_trace=\"Executing git checkout again after syntax error...\",\n",
                "    failure_status=\"INFINITE_LOOP\",\n",
                "    is_failure=1,\n",
                "    final_cost_usd=0.45\n",
                ")\n",
                "\n",
                "decision = sentry.audit_step(risky_step)\n",
                "\n",
                "print(\"=== SENTRY AUDIT RESULT ===\")\n",
                "print(f\"Action:                  {decision.action}\")\n",
                "print(f\"Risk Level:              {decision.risk_level}\")\n",
                "print(f\"Failure Probability:     {decision.tabpfn_assessment.failure_probability * 100:.1f}%\")\n",
                "print(f\"Predicted Failure Mode:  {decision.tabpfn_assessment.predicted_failure_mode}\")\n",
                "print(f\"Projected Cost:          ${decision.tabpfn_assessment.projected_final_cost_usd:.4f}\")\n",
                "print(f\"Estimated Cost Saved:    ${decision.estimated_cost_saved_usd:.4f}\")\n",
                "print(f\"Sentry Explanation:      {decision.explanation}\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 5. Benchmark: TabPFN vs Classical ML Baselines\n",
                "Compare balanced accuracy, ROC-AUC, and cost estimation MAE across models in low-data regimes."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "suite = GuardrailBenchmarkSuite()\n",
                "results = suite.run_benchmark(train_samples=250, test_samples=400)\n",
                "\n",
                "records = [\n",
                "    {\n",
                "        \"Model\": r.model_name,\n",
                "        \"Train Samples\": r.sample_size,\n",
                "        \"Balanced Acc (%)\": round(r.classification_balanced_acc * 100, 2),\n",
                "        \"F1 Macro (%)\": round(r.classification_f1_macro * 100, 2),\n",
                "        \"ROC-AUC\": r.classification_roc_auc,\n",
                "        \"Cost MAE ($)\": r.regression_mae_usd,\n",
                "        \"Cost R2\": r.regression_r2,\n",
                "        \"Latency (ms)\": r.inference_latency_ms\n",
                "    }\n",
                "    for r in results\n",
                "]\n",
                "bench_df = pd.DataFrame(records)\n",
                "bench_df"
            ]
        }
    ],
    "metadata": {
        "language_info": {"name": "python", "version": "3.10"},
        "kernelspec": {"name": "python3", "display_name": "Python 3"}
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

out_dir = ROOT_DIR / "notebooks"
out_dir.mkdir(exist_ok=True)
out_file = out_dir / "agentry_walkthrough.ipynb"
with open(out_file, "w", encoding="utf-8") as f:
    json.dump(nb, f, indent=2)
print(f"Successfully generated {out_file}")
