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
from agentry.guard import AgentryGuard, SentryDecision, _safe_int, _safe_float
from agentry.telemetry import AgentStepTelemetry
from agentry.report import generate_incident_report, export_incident_report_to_file
from agentry.hitl import hitl_gateway
from agentry.healing import trajectory_healer
from agentry.budget import budget_governor
from agentry.blast_radius import blast_radius_evaluator
from agentry.dlp import secret_redactor
from agentry.swarm import swarm_deadlock_detector
from agentry.checkpoint import physical_checkpointer
from agentry.active_memory import active_exemplar_memory

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
    # Defensive input sanitization
    session_id = str(session_id or "default_session")
    step_index = _safe_int(step_index, default=0, min_val=0)
    tool_name = str(tool_name or "bash")
    thought_trace = str(thought_trace or "")
    prompt_tokens = _safe_int(prompt_tokens, default=0, min_val=0)
    completion_tokens = _safe_int(completion_tokens, default=0, min_val=0)
    error_streak = _safe_int(error_streak, default=0, min_val=0)
    repetition_score = _safe_float(repetition_score, default=0.0, min_val=0.0, max_val=1.0)
    accumulated_cost_usd = _safe_float(accumulated_cost_usd, default=0.0, min_val=0.0)
    step_latency_ms = _safe_float(step_latency_ms, default=0.0, min_val=0.0)

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
        final_cost_usd=accumulated_cost_usd,
        remaining_cost_usd=0.0
    )

    decision = guard.sentry.audit_step(step)

    # Persist event to SQLite WAL audit database safely
    try:
        guard.storage.record_decision(decision, source="mcp")
    except Exception as exc:
        logger.warning("MCP failed to record audit event to SQLite: %s", exc)

    # Trigger real-time webhook alert if configured
    try:
        if guard.notifier and decision.action in ("KILL", "PAUSE", "REROUTE"):
            guard.notifier.send_alert(decision, background=True)
    except Exception as exc:
        logger.debug("Failed sending webhook alert: %s", exc)

    # Enqueue for HITL review if PAUSE
    if decision.action == "PAUSE":
        try:
            hitl_gateway.create_escalation(decision, tool_name=tool_name)
        except Exception as exc:
            logger.debug("Failed enqueueing HITL escalation: %s", exc)

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


@mcp.tool(
    name="agentry_export_incident_report",
    description=(
        "Generates and exports an audit-ready, forensic incident post-mortem report "
        "for an agent session in Markdown or HTML format. Includes TabPFN risk telemetry, "
        "step chronological audit table, token/cost savings, and remediation recommendations."
    )
)
def export_incident_report(session_id: str, format: str = "markdown", save_to_disk: bool = True) -> Dict[str, Any]:
    """Generates an audit incident report for an agent session."""
    guard = get_guard()
    report_content = generate_incident_report(session_id, format=format, storage=guard.storage)
    file_path = None
    if save_to_disk:
        p = export_incident_report_to_file(session_id, format=format, storage=guard.storage)
        file_path = str(p)
    return {
        "session_id": session_id,
        "format": format,
        "file_path": file_path,
        "report_length": len(report_content),
        "report_content": report_content if len(report_content) < 15000 else report_content[:15000] + "\n...[truncated for MCP response]"
    }


@mcp.tool(
    name="agentry_list_hitl_approvals",
    description=(
        "Lists Human-in-the-Loop (HITL) escalation requests requiring operator intervention. "
        "Can filter by status ('PENDING', 'APPROVED_RESUME', 'REROUTED', 'REJECTED_ABORT', or 'ALL')."
    )
)
def list_hitl_approvals(status: str = "PENDING") -> Dict[str, Any]:
    """Lists HITL escalation requests."""
    filter_status = None if status.upper() == "ALL" else status
    requests = hitl_gateway.list_requests(status=filter_status)
    return {
        "status": "ok",
        "filter": status,
        "count": len(requests),
        "requests": requests
    }


@mcp.tool(
    name="agentry_resolve_hitl_approval",
    description=(
        "Resolves a pending Human-in-the-Loop (HITL) approval request. "
        "Applies resolution ('RESUME', 'REROUTE', 'ABORT'), optional operator comment, "
        "and optional steering directive."
    )
)
def resolve_hitl_approval(
    request_id: str,
    resolution: str = "RESUME",
    comment: str = "",
    custom_directive: str = ""
) -> Dict[str, Any]:
    """Resolves a pending HITL escalation request."""
    from dataclasses import asdict
    req = hitl_gateway.resolve(
        request_id=request_id,
        resolution=resolution,
        comment=comment or None,
        custom_directive=custom_directive or None
    )
    if not req:
        return {"status": "error", "message": f"HITL request '{request_id}' not found."}
    return {
        "status": "ok",
        "request_id": request_id,
        "resolution": req.status,
        "details": asdict(req)
    }


@mcp.tool(
    name="agentry_prescribe_rewind",
    description=(
        "Computes an autonomic self-healing RewindPrescription for a looping or stuck agent session. "
        "Locates the divergence inflection point (t*), computes poisoned turns to prune, "
        "and synthesizes counterfactual steering directives."
    )
)
def prescribe_trajectory_rewind(
    session_id: str,
    current_step: int = 1,
    failed_tool: str = "tool",
    error_streak: int = 1,
    reason: str = "Anomalous failure loop detected"
) -> Dict[str, Any]:
    """Computes trajectory rewind and recovery prescription."""
    from dataclasses import asdict
    guard = get_guard()
    c_step = _safe_int(current_step, default=1, min_val=0)
    e_streak = _safe_int(error_streak, default=1, min_val=0)
    prescription = trajectory_healer.diagnose_and_prescribe(
        session_id=str(session_id),
        current_step=c_step,
        failed_tool=str(failed_tool or "tool"),
        error_streak=e_streak,
        reason=str(reason or "Repetitive failure loop detected"),
        storage=guard.storage
    )
    return {
        "status": "ok",
        "prescription": asdict(prescription)
    }


@mcp.tool(
    name="agentry_check_budget",
    description=(
        "Checks current financial quota status across the agent fleet or for a specific session. "
        "Returns 24h spend, utilization %, remaining budget, and autonomic action recommendation (PROCEED, WARN, THROTTLE, HALT)."
    )
)
def check_fleet_and_session_budget(
    session_id: Optional[str] = None,
    accumulated_cost: float = 0.0
) -> Dict[str, Any]:
    """Queries budget governor for fleet and optional session quota."""
    from dataclasses import asdict
    fleet_status = budget_governor.check_fleet_budget()
    result: Dict[str, Any] = {
        "status": "ok",
        "fleet": asdict(fleet_status)
    }
    if session_id:
        s_cost = _safe_float(accumulated_cost, default=0.0, min_val=0.0)
        session_status = budget_governor.check_session_budget(session_id, s_cost)
        result["session"] = asdict(session_status)
    return result


@mcp.tool(
    name="agentry_evaluate_blast_radius",
    description=(
        "Evaluates the destructive blast radius of a proposed tool action (e.g. bash commands, "
        "SQL queries, file deletions) before execution. Detects critical hazards like unconstrained "
        "rm -rf, DROP DATABASE, mkfs, reverse shells, and unauthorized root mutations."
    )
)
def evaluate_blast_radius(
    tool_name: str,
    action_input: str,
    session_id: str = "default_session"
) -> Dict[str, Any]:
    """Evaluates semantic blast radius of an action."""
    from dataclasses import asdict
    assessment = blast_radius_evaluator.evaluate(
        tool_name=str(tool_name or ""),
        action_input=str(action_input or ""),
        session_id=str(session_id or "default_session")
    )
    return {
        "status": "ok",
        "tool_name": tool_name,
        "is_critical": assessment.is_critical,
        "severity": assessment.severity,
        "matched_rules": [assessment.matched_pattern] if assessment.matched_pattern else [],
        "remediation": assessment.remediation,
        "assessment": asdict(assessment)
    }


@mcp.tool(
    name="agentry_redact_secrets",
    description=(
        "In-flight Data Loss Prevention (DLP) scanner. Detects and masks credentials, API keys "
        "(OpenAI, Anthropic, Groq, GitHub PAT, AWS, GCP), SSH private keys, and DB connection URIs."
    )
)
def redact_secrets(text: str) -> Dict[str, Any]:
    """Redacts high-risk secrets and credentials from prompts or tool outputs."""
    result = secret_redactor.redact(str(text or ""))
    return {
        "status": "ok",
        "redacted_text": result.masked_text,
        "secrets_found_count": result.redaction_count,
        "secret_types": [s["type"] for s in result.detected_secrets],
        "details": result.detected_secrets
    }


@mcp.tool(
    name="agentry_check_swarm_deadlock",
    description=(
        "Swarm coordination deadlock detector. Evaluates delegation handoffs between autonomous agents "
        "to prevent infinite ping-pong loops (A -> B -> A -> B) and multi-agent cyclic deadlocks."
    )
)
def check_swarm_deadlock(
    session_id: str,
    from_agent: str,
    to_agent: str,
    task_snippet: str = ""
) -> Dict[str, Any]:
    """Detects multi-agent circular delegation or deadlock."""
    from dataclasses import asdict
    sid = str(session_id or "default_session")
    report = swarm_deadlock_detector.record_delegation(
        session_id=sid,
        from_agent=str(from_agent or "agent_a"),
        to_agent=str(to_agent or "agent_b"),
        task_snippet=str(task_snippet or "")
    )
    if report is not None:
        return {
            "status": "ok",
            "is_deadlocked": report.is_deadlocked,
            "deadlock_type": "PING_PONG" if report.cycle_length == 2 else "CYCLIC_DEADLOCK",
            "cycle_path": report.cycle_agents,
            "hops_count": report.total_delegation_hops,
            "intervention": report.recommendation,
            "report": asdict(report)
        }
    hops = swarm_deadlock_detector.get_session_hops(sid)
    return {
        "status": "ok",
        "is_deadlocked": False,
        "deadlock_type": "NONE",
        "cycle_path": [],
        "hops_count": hops,
        "intervention": "PROCEED",
        "report": None
    }



@mcp.tool(
    name="agentry_rollback_filesystem",
    description=(
        "Autonomously rolls back physical filesystem mutations made by an autonomous agent during an incident. "
        "Restores modified files to their pre-incident state and deletes newly created poisoned files."
    )
)
def rollback_filesystem(
    session_id: str,
    target_step: int = 0
) -> Dict[str, Any]:
    """Rolls back filesystem to checkpoint before target_step."""
    res = physical_checkpointer.rollback(
        session_id=str(session_id),
        target_step=int(target_step)
    )
    return {
        "status": "ok" if res.success else "error",
        "session_id": session_id,
        "target_step": target_step,
        "success": res.success,
        "restored_files_count": len(res.restored_files),
        "deleted_files_count": len(res.deleted_files),
        "restored_files": res.restored_files,
        "deleted_files": res.deleted_files,
        "errors": res.errors
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


@mcp.resource("fleet://hitl-queue")
def fleet_hitl_queue_resource() -> str:
    """Exposes all pending HITL approval requests."""
    requests = hitl_gateway.list_requests(status="PENDING")
    return json.dumps(requests, indent=2)


@mcp.resource("fleet://budget")
def fleet_budget_resource() -> str:
    """Exposes real-time fleet financial budget and quota utilization."""
    from dataclasses import asdict
    status = budget_governor.check_fleet_budget()
    return json.dumps(asdict(status), indent=2)


@mcp.resource("fleet://active-exemplars")
def fleet_active_exemplars_resource() -> str:
    """Exposes buffered in-context incident exemplars for TabPFN calibration."""
    df = active_exemplar_memory.get_exemplars_df()
    if df is None or df.empty:
        return json.dumps({"count": 0, "exemplars": []})
    return json.dumps({"count": len(df), "exemplars": df.to_dict(orient="records")}, indent=2)



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
