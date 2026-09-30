"""
Model Context Protocol (MCP) Server for Agentry.
Allows Claude Desktop, Cursor IDE, Windsurf, and custom agent fleets
to leverage TabPFN-3.5 runtime tabular guardrails directly over MCP.
"""

import sys
import json
import logging
from typing import Optional, Dict, Any, List
from pathlib import Path

# Ensure package root is in path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from mcp.server.mcpserver import MCPServer
from agentry import __version__
from agentry.guard import AgentryGuard, SentryDecision
from agentry.telemetry import AgentStepTelemetry

logger = logging.getLogger("agentry.mcp")

# Create MCP Server instance
mcp = MCPServer(
    name="agentry-sentry",
    version=__version__,
    description="Agentry: Predictive Runtime Control Layer for AI Agent Fleets powered by Prior Labs TabPFN-3.5"
)

# Global singleton guard instance
_guard: Optional[AgentryGuard] = None


def get_guard() -> AgentryGuard:
    """Lazily initializes and returns the AgentryGuard singleton."""
    global _guard
    if _guard is None:
        _guard = AgentryGuard(auto_fit=True, raise_on_kill=False)
    return _guard


def set_guard(guard: AgentryGuard) -> None:
    """Explicitly injects a pre-fitted guard instance."""
    global _guard
    _guard = guard


# ============================================================================
# MCP Tools
# ============================================================================

@mcp.tool(
    name="agentry_audit_step",
    description=(
        "Audits an autonomous AI agent execution step using the Prior Labs TabPFN-3.5 "
        "tabular foundation model. Returns real-time failure risk probability, "
        "predicted failure mode (INFINITE_LOOP, COST_RUNAWAY, TOOL_HALLUCINATION), "
        "projected terminal cost, and autonomic intervention (PASS, REROUTE, PAUSE, KILL)."
    )
)
def audit_agent_step(
    session_id: str,
    step_index: int = 0,
    tool_name: str = "bash",
    thought_trace: str = "",
    error_streak: int = 0,
    repetition_score: float = 0.0,
    prompt_tokens: int = 1000,
    completion_tokens: int = 150,
    accumulated_cost_usd: float = 0.005,
    step_latency_ms: float = 500.0
) -> Dict[str, Any]:
    """
    Audits an autonomous AI agent step in real-time.
    
    Args:
        session_id: Unique identifier for the agent session/task.
        step_index: Current 0-indexed step number in the trajectory.
        tool_name: Name of tool invoked (e.g., 'bash', 'read_file', 'edit_file').
        thought_trace: The agent's reasoning trace or proposed plan.
        error_streak: Number of consecutive failed tool execution attempts.
        repetition_score: Score from 0.0 to 1.0 measuring output repetition entropy.
        prompt_tokens: Total prompt tokens for this step.
        completion_tokens: Total completion tokens generated.
        accumulated_cost_usd: Total API expenditure incurred so far in USD.
        step_latency_ms: Milliseconds elapsed for this step.

    Returns:
        Structured audit decision with action (PASS/REROUTE/PAUSE/KILL), failure probability,
        predicted failure mode, reason, and estimated token savings.
    """
    guard = get_guard()
    total_tokens = prompt_tokens + completion_tokens

    step = AgentStepTelemetry(
        session_id=session_id,
        step_index=step_index,
        agent_role="MCP-Agent",
        model_name="mcp-client-model",
        tool_name=tool_name,
        thought_trace=thought_trace,
        step_latency_ms=step_latency_ms,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        tool_call_count=1,
        error_streak=error_streak,
        repetition_score=repetition_score,
        thought_length=len(thought_trace),
        accumulated_cost_usd=accumulated_cost_usd,
        failure_status="NORMAL",
        is_failure=0,
        final_cost_usd=accumulated_cost_usd
    )

    decision = guard.sentry.audit_step(step)

    # Persist event to SQLite WAL audit database
    guard.storage.record_decision(decision)

    return {
        "session_id": session_id,
        "step_index": step_index,
        "action": decision.action,
        "risk_level": decision.risk_level,
        "failure_probability": decision.tabpfn_assessment.failure_probability,
        "predicted_failure_mode": decision.tabpfn_assessment.predicted_failure_mode,
        "projected_final_cost_usd": decision.tabpfn_assessment.projected_final_cost_usd,
        "reason": decision.reason,
        "reroute_instruction": decision.reroute_instruction,
        "estimated_tokens_saved": decision.estimated_tokens_saved,
        "estimated_cost_saved_usd": decision.estimated_cost_saved_usd,
        "sentry_provider": decision.sentry_provider,
        "is_halted": decision.action == "KILL"
    }


@mcp.tool(
    name="agentry_get_fleet_status",
    description=(
        "Retrieves real-time enterprise fleet governance metrics from the local SQLite WAL audit trail. "
        "Shows total steps audited, unique sessions monitored, cumulative tokens and dollars saved, "
        "and breakdown of autonomic interventions (KILL, REROUTE, PAUSE, PASS)."
    )
)
def get_fleet_status() -> Dict[str, Any]:
    """Retrieves fleet-wide governance and cost-savings summary."""
    guard = get_guard()
    summary = guard.storage.get_fleet_summary()
    return {
        "status": "healthy",
        "service": "agentry-mcp-sentry",
        "version": __version__,
        "tabpfn_fitted": guard.engine.is_fitted,
        "tabpfn_cloud_mode": guard.engine.is_cloud_tabpfn,
        "total_audited_steps": summary.get("total_audited_steps", 0),
        "unique_sessions": summary.get("unique_sessions", 0),
        "unique_monitored_sessions": summary.get("unique_sessions", 0),
        "interventions": summary.get("interventions", {}),
        "total_tokens_saved": summary.get("total_tokens_saved", 0),
        "total_cost_saved_usd": summary.get("total_cost_saved_usd", 0.0)
    }


@mcp.tool(
    name="agentry_inspect_session_history",
    description="Fetches chronological audit logs, risk scores, and forensic decisions for a specific agent session."
)
def inspect_session_history(session_id: str) -> Dict[str, Any]:
    """Fetches audit trail for a single session."""
    guard = get_guard()
    events = guard.storage.get_session_events(session_id)
    return {
        "session_id": session_id,
        "total_steps": len(events),
        "events": events
    }


@mcp.tool(
    name="agentry_reset_session",
    description="Resets the in-memory guardrail state and step tracker for a specific agent session."
)
def reset_session(session_id: str) -> Dict[str, Any]:
    """Resets session tracking state."""
    guard = get_guard()
    guard.reset_session(session_id)
    return {
        "status": "ok",
        "message": f"Session '{session_id}' state reset successfully."
    }


# ============================================================================
# MCP Resources
# ============================================================================

@mcp.resource("fleet://metrics")
def fleet_metrics_resource() -> str:
    """Exposes live fleet audit metrics as an MCP resource."""
    guard = get_guard()
    summary = guard.storage.get_fleet_summary()
    return json.dumps(summary, indent=2)


@mcp.resource("fleet://recent-interventions")
def fleet_recent_interventions_resource() -> str:
    """Exposes the most recent audit records from SQLite WAL storage."""
    guard = get_guard()
    events = guard.storage.get_all_events(limit=20)
    return json.dumps(events, indent=2)


# ============================================================================
# Server Runner
# ============================================================================

def run_mcp_server(transport: str = "stdio", host: str = "127.0.0.1", port: int = 8788):
    """Starts the Agentry MCP Server."""
    logger.info("Starting Agentry MCP Server v%s using transport: %s", __version__, transport)
    if transport == "stdio":
        mcp.run(transport="stdio")
    elif transport == "sse":
        mcp.run(transport="sse", host=host, port=port)
    elif transport == "streamable-http":
        mcp.run(transport="streamable-http", host=host, port=port)
    else:
        raise ValueError(f"Unknown transport: {transport}. Choose 'stdio', 'sse', or 'streamable-http'.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Agentry MCP Server for Claude Desktop & Cursor")
    parser.add_argument("--transport", default="stdio", choices=["stdio", "sse", "streamable-http"], help="MCP transport mode")
    parser.add_argument("--host", default="127.0.0.1", help="Host for network transports")
    parser.add_argument("--port", type=int, default=8788, help="Port for network transports")
    args = parser.parse_args()

    run_mcp_server(transport=args.transport, host=args.host, port=args.port)
