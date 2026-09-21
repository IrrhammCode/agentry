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
                "# Agentry: Predictive Runtime Control Layer for Autonomous Agent Fleets\n",
                "### Powered by Prior Labs TabPFN-3.5 Tabular Foundation Model & Edge Intelligence\n",
                "\n",
                "**Prior Labs TabPFN-3.5 Global Hackathon 2026 Submission**\n",
                "\n",
                "Agentry is a predictive runtime control layer for multi-agent fleets. It monitors real-time tabular execution telemetry (token velocities, repetition entropy, error streaks, tool latencies, and thought traces) and predicts unrecoverable failure cascades (**Infinite Loops**, **Context / Cost Runaways**, and **Tool Hallucinations**) before compute is incinerated."
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
                "from agentry.guard import AgentryGuard\n",
                "\n",
                "print(\"Agentry modules loaded successfully!\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Load Real-World SWE-bench Agent Telemetry\n",
                "We evaluate on genuine agent execution traces streamed from `nebius/SWE-agent-trajectories` (739 steps, 35 unique sessions)."
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
                "TabPFN utilizes In-Context Learning (ICL) directly across multimodal tabular features: sequential grouped session dynamics (`group_col='session_id'`, `group_time_col='step_index'`), numerical metrics, and raw thought traces."
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
                "## 4. Real-Time Step Risk Evaluation & Unified Economic Policy\n",
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
                "print(f\"Sentry Reason:           {decision.reason}\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 5. Rigorous Empirical Benchmark (Unseen Trajectory Group Split)\n",
                "Compare Failure Recall, False-Stop Rate (FPR), ROC-AUC, and Cost MAE across models on **unseen agent sessions**."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "suite = GuardrailBenchmarkSuite()\n",
                "results = suite.run_benchmark(group_split=True)\n",
                "\n",
                "records = [\n",
                "    {\n",
                "        \"Model Architecture\": r.model_name,\n",
                "        \"Unseen Test Sessions\": f\"{r.test_sessions_count} sessions\",\n",
                "        \"Balanced Acc (%)\": f\"{r.classification_balanced_acc * 100:.1f}%\",\n",
                "        \"F1 Macro (%)\": f\"{r.classification_f1_macro * 100:.1f}%\",\n",
                "        \"ROC-AUC\": f\"{r.classification_roc_auc:.3f}\",\n",
                "        \"Failure Recall\": f\"{r.failure_recall * 100:.1f}%\",\n",
                "        \"False-Stop Rate\": f\"{r.false_stop_rate * 100:.1f}%\",\n",
                "        \"Cost MAE ($)\": f\"${r.regression_mae_usd:.4f}\",\n",
                "        \"Cost R2\": f\"{r.regression_r2:.3f}\",\n",
                "        \"Inf Latency\": f\"{r.inference_latency_ms:.2f} ms\"\n",
                "    }\n",
                "    for r in results\n",
                "]\n",
                "bench_df = pd.DataFrame(records)\n",
                "bench_df"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 6. Equal-Success-Rate Fleet Runtime Experiment\n",
                "Evaluating the fundamental trade-off: **Preserving successful tasks vs Slashing token burn.**"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "from scripts.run_equal_success_experiment import run_fleet_simulation\n",
                "regimes, total_succ, total_fail = run_fleet_simulation()\n",
                "\n",
                "baseline_tokens = regimes['Unprotected Fleet (No Guard)']['total_tokens']\n",
                "fleet_records = []\n",
                "for name, stats in regimes.items():\n",
                "    succ_pct = (stats['completed_successes'] / max(1, total_succ)) * 100\n",
                "    reduc = ((baseline_tokens - stats['total_tokens']) / baseline_tokens) * 100\n",
                "    fleet_records.append({\n",
                "        'Strategy': name,\n",
                "        'Task Success Rate': f'{succ_pct:.1f}% ({stats[\"completed_successes\"]}/{total_succ})',\n",
                "        'False Kills': stats['false_kills'],\n",
                "        'Runaways Caught': f'{stats[\"runaways_interrupted\"]}/{total_fail}',\n",
                "        'Total Tokens': f'{stats[\"total_tokens\"]:,}',\n",
                "        'Fleet Cost': f'${stats[\"total_cost_usd\"]:.4f}',\n",
                "        'Compute Reduction': 'Baseline (0%)' if reduc == 0 else f'-{reduc:.1f}%'\n",
                "    })\n",
                "pd.DataFrame(fleet_records)"
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
