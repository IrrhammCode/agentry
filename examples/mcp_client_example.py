"""
Agentry MCP Client Example.
Demonstrates interacting with Agentry's Model Context Protocol (MCP) server
to audit agent steps and monitor fleet safety in real-time.
"""

import asyncio
from agentry.mcp_server import mcp, audit_agent_step, get_fleet_status, inspect_session_history


async def main():
    print("=== Agentry MCP Server Integration Demo ===\n")

    # 1. List all available MCP Tools
    tools = await mcp.list_tools()
    print(f"Registered MCP Tools ({len(tools)}):")
    for t in tools:
        print(f"  • {t.name}: {t.description[:60]}...")
    print()

    # 2. Simulate Step 0: Nominal Agent Execution
    print("[1] Auditing Nominal Agent Step (Reading Config)...")
    res_nominal = audit_agent_step(
        session_id="session_mcp_demo_01",
        step_index=0,
        tool_name="read_file",
        thought_trace="Opening settings.py to verify database URL.",
        error_streak=0,
        repetition_score=0.08,
        prompt_tokens=1500,
        completion_tokens=80,
        accumulated_cost_usd=0.003
    )
    print(f"  -> Decision: {res_nominal['action']} (Risk: {res_nominal['risk_level']}, Prob: {res_nominal['failure_probability']:.1%})")
    print(f"  -> Reason: {res_nominal['reason']}\n")

    # 3. Simulate Step 5: Infinite Loop Anomaly
    print("[2] Auditing Runaway Loop Step (5th Consecutive Failure)...")
    res_loop = audit_agent_step(
        session_id="session_mcp_demo_01",
        step_index=5,
        tool_name="bash",
        thought_trace="Retrying broken command 'pip install invalid-package' for the 5th time...",
        error_streak=5,
        repetition_score=0.96,
        prompt_tokens=8500,
        completion_tokens=150,
        accumulated_cost_usd=0.075
    )
    print(f"  -> Decision: {res_loop['action']} (Risk: {res_loop['risk_level']}, Mode: {res_loop['predicted_failure_mode']})")
    print(f"  -> Action Taken: {'HALTED (KILL)' if res_loop['is_halted'] else 'PROCEED'}")
    print(f"  -> Tokens Saved: ~{res_loop['estimated_tokens_saved']:,} | Cost Saved: ~${res_loop['estimated_cost_saved_usd']:.4f}")
    print(f"  -> Reason: {res_loop['reason']}\n")

    # 4. Query Fleet Governance Summary
    print("[3] Fetching Enterprise Fleet Status...")
    status = get_fleet_status()
    print(f"  • Total Steps Audited: {status['total_audited_steps']}")
    print(f"  • Unique Sessions: {status['unique_sessions']}")
    print(f"  • Total Tokens Saved: ~{status['total_tokens_saved']:,}")
    print(f"  • Total Dollars Saved: ~${status['total_cost_saved_usd']:.4f}")
    print(f"  • Interventions: {status['interventions']}\n")

    # 5. Inspect Session Audit Trail
    print("[4] Inspecting Session History...")
    history = inspect_session_history("session_mcp_demo_01")
    print(f"  • Session: {history['session_id']}")
    print(f"  • Recorded Steps: {history['total_steps']}")
    for ev in history["events"][-2:]:
        print(f"    - Step {ev['step_index']}: {ev['action']} | Risk: {ev['risk_level']} ({ev['failure_probability']:.1%})")

    print("\n=== Demo Complete ===")


if __name__ == "__main__":
    asyncio.run(main())
