"""
Example 03: Programmatic Autonomic Trajectory Rewind & Context Healing.

Demonstrates how to invoke TrajectoryHealer directly to prune poisoned turns
from conversation history and inject TabPFN-generated steering directives.
"""

import sys
from pathlib import Path

# Ensure root directory is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from agentry.healing import trajectory_healer, TrajectoryHealer


def main():
    print("=" * 65)
    print("Agentry Autonomic Self-Healing & Trajectory Rewind")
    print("=" * 65)

    # Simulated poisoned conversation history from an agent trapped in a loop
    raw_messages = [
        {"role": "system", "content": "You are an autonomous coding agent."},
        {"role": "user", "content": "Fix the database deadlock in db/pool.py"},
        {"role": "assistant", "content": "I will inspect db/pool.py"},
        {"role": "tool", "content": "File content: pool size = 10, timeout = 30"},
        # Safe inflection checkpoint: Step 2
        {"role": "assistant", "content": "I will increase timeout to 60"},
        {"role": "tool", "content": "Saved changes to db/pool.py"},
        # Poisoned turns start here:
        {"role": "assistant", "content": "Running test... failed with deadlock error"},
        {"role": "tool", "content": "DeadlockDetectedError: thread 4"},
        {"role": "assistant", "content": "Retrying same change with timeout 90... failed"},
        {"role": "tool", "content": "DeadlockDetectedError: thread 4"},
        {"role": "assistant", "content": "Retrying same change with timeout 120... failed"},
        {"role": "tool", "content": "DeadlockDetectedError: thread 4"},
    ]

    print(f"[*] Initial poisoned message history length: {len(raw_messages)} messages")

    # Step 1: Diagnose and prescribe recovery
    prescription = trajectory_healer.diagnose_and_prescribe(
        session_id="db_deadlock_session_01",
        current_step=5,
        failed_tool="edit_file",
        error_streak=3,
        reason="Repeated DeadlockDetectedError and parameter oscillation"
    )

    print(f"\n[+] Healing Prescription:")
    print(f"    - Safe Checkpoint: Step {prescription.target_step}")
    print(f"    - Pruned Steps:    {prescription.pruned_steps_count} turns")
    print(f"    - Tokens Saved:    {prescription.estimated_tokens_saved:,} tokens")
    print(f"    - Cost Saved:      ${prescription.estimated_cost_saved_usd:.4f} USD")
    print(f"\n[+] Counterfactual Directive Injected:")
    print(f"    \"{prescription.counterfactual_directive}\"")

    # Step 2: Prune poisoned messages and inject corrective directive
    healed_messages = trajectory_healer.prune_conversation(
        messages=raw_messages,
        target_step=prescription.target_step,
        directive=prescription.counterfactual_directive
    )

    print(f"\n[*] Healed message history length: {len(healed_messages)} messages")
    print("[*] Last message in healed history (Corrective Steering Prompt):")
    print(f"    Role: {healed_messages[-1]['role']}")
    print(f"    Content: {healed_messages[-1]['content']}")

    print("\n[OK] Autonomic self-healing and trajectory rewind completed successfully.")


if __name__ == "__main__":
    main()
