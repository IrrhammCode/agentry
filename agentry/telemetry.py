"""
Telemetry module for Agentry.
Defines agent telemetry schemas, feature extractors, and synthetic dataset generators.
"""

import random
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import pandas as pd
import numpy as np


@dataclass
class AgentStepTelemetry:
    """Telemetry captured from a single step of an AI Agent execution."""
    session_id: str
    step_index: int
    agent_role: str
    model_name: str
    tool_name: str
    step_latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    tool_call_count: int
    error_streak: int
    repetition_score: float
    thought_length: int
    accumulated_cost_usd: float
    thought_trace: str
    failure_status: str  # NORMAL, INFINITE_LOOP, TOOL_HALLUCINATION, COST_RUNAWAY
    is_failure: int = 0
    final_cost_usd: float = 0.0
    remaining_cost_usd: float = 0.0


# Failure modes categorized
FAILURE_MODES = ["NORMAL", "INFINITE_LOOP", "TOOL_HALLUCINATION", "COST_RUNAWAY"]
AGENT_ROLES = ["Coder", "Researcher", "Reviewer", "DevOps", "DataAnalyst"]
MODELS = ["qwen2.5:7b", "llama-3.3-70b", "gpt-4o-mini", "claude-3-5-haiku"]
TOOLS = ["bash", "read_file", "write_file", "grep_search", "web_search", "python_repl"]

# Thought trace templates for realistic agent traces
NORMAL_THOUGHTS = [
    "I will inspect the repository structure to locate where the database config is loaded.",
    "File found. Now reading the content of settings.py to verify connection string parameters.",
    "The parameter was missing. Writing unit tests to verify the expected connection behavior.",
    "Running test suite to verify the fix passes without breaking regressions.",
    "All unit tests passed. Generating git commit message and preparing summary for the user.",
    "Parsed the query requirements. Fetching data from API endpoint /v1/telemetry.",
    "Found 12 matching records. Filtering out null fields and aggregating by user_id.",
]

LOOP_THOUGHTS = [
    "Command failed with exit code 1. Let me try running npm install again with --force.",
    "Still failed with code 1. Re-running npm install with --legacy-peer-deps.",
    "Wait, still failing. Trying npm install again with --force and --ignore-scripts.",
    "Error persists. Let me re-run the exact same command to see if it was a transient network error.",
    "Command timed out. Retrying npm install once more...",
    "Error in compilation. Trying to delete node_modules and running npm install again.",
    "Re-executing npm install...",
]

HALLUCINATION_THOUGHTS = [
    "Invoking tool 'execute_quantum_algorithm' with parameters {'qubits': 64}...",
    "Tool error: Tool 'execute_quantum_algorithm' does not exist. Trying 'run_quantum_sim'...",
    "Tool error: Tool 'run_quantum_sim' not found. Let me call 'deepmind_tabpfn_api_direct'...",
    "Unrecognized tool 'deepmind_tabpfn_api_direct'. Maybe the flag --super-optimize will work on bash.",
    "bash: --super-optimize: command not found. Let me pass --magic-solve to git push.",
]

COST_RUNAWAY_THOUGHTS = [
    "Injecting entire 50,000 line log file into conversation context to analyze every single line.",
    "Context window is 85% full. Now reading all dependencies from site-packages into prompt...",
    "Appending 20MB trace dump to working memory. Token usage spiking rapidly.",
    "Re-generating full 30,000 token response without pagination or streaming.",
    "Recursive prompt expansion with all historical logs duplicated.",
]


class TelemetrySimulator:
    """Generates synthetic agent fleet telemetry for training and evaluating TabPFN."""

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        np.random.seed(seed)

    def generate_session(self, session_id: Optional[str] = None, forced_mode: Optional[str] = None) -> List[AgentStepTelemetry]:
        """Generate telemetry for a single agent task session."""
        if not session_id:
            session_id = f"sess_{uuid.uuid4().hex[:8]}"

        mode = forced_mode if forced_mode else self.rng.choices(
            FAILURE_MODES, weights=[0.60, 0.18, 0.12, 0.10], k=1
        )[0]

        agent_role = self.rng.choice(AGENT_ROLES)
        model_name = self.rng.choice(MODELS)
        max_steps = self.rng.randint(6, 18) if mode == "NORMAL" else self.rng.randint(10, 25)

        session_steps: List[AgentStepTelemetry] = []
        accumulated_prompt = self.rng.randint(800, 2000)
        accumulated_comp = self.rng.randint(150, 400)
        error_streak = 0
        tool_call_count = 0
        cost_per_1k_tokens = 0.003 if "70b" in model_name else 0.0006

        for step in range(max_steps):
            is_step_failing = False
            tool_name = self.rng.choice(TOOLS)

            if mode == "NORMAL":
                # Healthy agent progression
                tool_call_count += 1
                error_streak = 0 if self.rng.random() > 0.15 else 1
                repetition_score = round(self.rng.uniform(0.05, 0.35), 3)
                latency = round(self.rng.uniform(600, 2200), 1)
                accumulated_prompt += self.rng.randint(300, 900)
                accumulated_comp += self.rng.randint(80, 250)
                thought = self.rng.choice(NORMAL_THOUGHTS)

            elif mode == "INFINITE_LOOP":
                # Starts diverging after step 3
                if step >= 3:
                    is_step_failing = True
                    tool_call_count += 1
                    error_streak += 1
                    repetition_score = round(min(0.98, 0.50 + 0.07 * (step - 2) + self.rng.uniform(-0.05, 0.05)), 3)
                    latency = round(self.rng.uniform(1800, 6000), 1)
                    accumulated_prompt += self.rng.randint(1200, 2800)
                    accumulated_comp += self.rng.randint(200, 450)
                    tool_name = "bash" if self.rng.random() > 0.3 else "read_file"
                    thought = self.rng.choice(LOOP_THOUGHTS)
                else:
                    repetition_score = round(self.rng.uniform(0.15, 0.35), 3)
                    latency = round(self.rng.uniform(800, 2000), 1)
                    thought = self.rng.choice(NORMAL_THOUGHTS)

            elif mode == "TOOL_HALLUCINATION":
                if step >= 2:
                    is_step_failing = True
                    tool_call_count += 1
                    error_streak = min(8, error_streak + 1)
                    repetition_score = round(self.rng.uniform(0.40, 0.75), 3)
                    latency = round(self.rng.uniform(400, 1500), 1)
                    accumulated_prompt += self.rng.randint(600, 1500)
                    accumulated_comp += self.rng.randint(100, 300)
                    tool_name = self.rng.choice(["ghost_tool_exec", "eval_unsupported", "quantum_sim", "magic_deploy"])
                    thought = self.rng.choice(HALLUCINATION_THOUGHTS)
                else:
                    repetition_score = round(self.rng.uniform(0.10, 0.30), 3)
                    latency = round(self.rng.uniform(700, 1800), 1)
                    thought = self.rng.choice(NORMAL_THOUGHTS)

            elif mode == "COST_RUNAWAY":
                if step >= 2:
                    is_step_failing = True
                    tool_call_count += 1
                    error_streak = self.rng.randint(0, 2)
                    repetition_score = round(self.rng.uniform(0.30, 0.65), 3)
                    latency = round(self.rng.uniform(3500, 12000), 1)
                    # Quadratic or massive token inflation
                    accumulated_prompt += int(3000 * (1.5 ** (step - 1)))
                    accumulated_comp += self.rng.randint(1000, 3500)
                    thought = self.rng.choice(COST_RUNAWAY_THOUGHTS)
                else:
                    repetition_score = round(self.rng.uniform(0.10, 0.25), 3)
                    latency = round(self.rng.uniform(900, 2200), 1)
                    thought = self.rng.choice(NORMAL_THOUGHTS)

            total_tokens = accumulated_prompt + accumulated_comp
            accumulated_cost = round((total_tokens / 1000.0) * cost_per_1k_tokens, 5)

            session_steps.append(
                AgentStepTelemetry(
                    session_id=session_id,
                    step_index=step,
                    agent_role=agent_role,
                    model_name=model_name,
                    tool_name=tool_name,
                    step_latency_ms=latency,
                    prompt_tokens=accumulated_prompt,
                    completion_tokens=accumulated_comp,
                    total_tokens=total_tokens,
                    tool_call_count=tool_call_count,
                    error_streak=error_streak,
                    repetition_score=repetition_score,
                    thought_length=len(thought),
                    accumulated_cost_usd=accumulated_cost,
                    thought_trace=thought,
                    failure_status=mode if is_step_failing else "NORMAL",
                    is_failure=1 if is_step_failing else 0,
                    final_cost_usd=0.0  # Will be populated after session finishes
                )
            )

        # Populate final cost for all steps in the session
        final_cost = session_steps[-1].accumulated_cost_usd
        if mode == "COST_RUNAWAY":
            final_cost = max(final_cost, round(self.rng.uniform(0.60, 2.80), 4))
        for item in session_steps:
            item.final_cost_usd = final_cost

        return session_steps

    def generate_fleet_dataset(self, num_sessions: int = 150) -> pd.DataFrame:
        """Generate a complete multi-agent fleet dataset."""
        all_records = []
        for _ in range(num_sessions):
            session_telemetry = self.generate_session()
            all_records.extend([asdict(step) for step in session_telemetry])
        return pd.DataFrame(all_records)


def load_telemetry_data(csv_path: Optional[Path] = None, generate_if_missing: bool = True) -> pd.DataFrame:
    """Load agent telemetry DataFrame from CSV or generate if missing."""
    from agentry.config import settings

    target_path = Path(csv_path) if csv_path else settings.default_dataset_path
    if target_path.exists():
        return pd.read_csv(target_path)

    if generate_if_missing:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        simulator = TelemetrySimulator(seed=42)
        df = simulator.generate_fleet_dataset(num_sessions=200)
        df.to_csv(target_path, index=False)
        return df

    raise FileNotFoundError(f"Telemetry dataset not found at {target_path}")
