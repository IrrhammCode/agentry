"""
Enterprise Incident Post-Mortem & Audit Report Generator for Agentry.
Produces audit-ready, forensic incident reports in Markdown and HTML
for AI safety compliance, AgentOps post-mortems, and engineering analysis.
"""

import time
import json
import html
from pathlib import Path
from typing import Dict, Any, List, Optional

from agentry import __version__
from agentry.storage import AuditStorage, DB_PATH
from agentry.config import ROOT_DIR


def generate_incident_report(session_id: str, format: str = "markdown", storage: Optional[AuditStorage] = None) -> str:
    """
    Generates a forensic post-mortem incident report for an agent session.
    Supported formats: 'markdown' or 'html'.
    """
    storage = storage or AuditStorage()
    events = storage.get_session_events(session_id)

    if not events:
        msg = f"No telemetry or audit events recorded for session '{session_id}'."
        if format.lower() == "html":
            return f"<html><body><h2>{msg}</h2></body></html>"
        return f"# Agentry Forensic Report: {session_id}\n\n> {msg}\n"

    last_event = events[-1]
    is_killed = any(e["action"] == "KILL" for e in events)
    is_rerouted = any(e["action"] == "REROUTE" for e in events)
    is_paused = any(e["action"] == "PAUSE" for e in events)

    if is_killed:
        incident_status = "CRITICAL: CIRCUIT-BREAKER TERMINATION (KILL)"
        status_color = "#EF4444"
    elif is_paused:
        incident_status = "WARNING: HUMAN INSPECTION ESCALATION (PAUSE)"
        status_color = "#F59E0B"
    elif is_rerouted:
        incident_status = "ELEVATED: STEERING DIRECTIVE INJECTED (REROUTE)"
        status_color = "#3B82F6"
    else:
        incident_status = "NOMINAL: CONVERGED WITHOUT CIRCUIT-BREAKER TRIPS"
        status_color = "#10B981"

    total_tokens_saved = sum(e.get("estimated_tokens_saved", 0) for e in events if e["action"] in ("KILL", "PAUSE"))
    total_cost_saved = sum(e.get("estimated_cost_saved_usd", 0.0) for e in events if e["action"] in ("KILL", "PAUSE"))
    terminal_cost = last_event.get("projected_final_cost_usd", 0.0)
    risk_prob = last_event.get("failure_probability", 0.0)
    failure_mode = last_event.get("predicted_failure_mode", "UNKNOWN")
    primary_reason = last_event.get("reason", "Nominal operational telemetry.")
    reroute_directive = last_event.get("reroute_instruction") or "N/A"
    sentry_provider = last_event.get("sentry_provider", "TabPFN-3.5 + Local Sentry")

    if format.lower() == "html":
        return _render_html_report(
            session_id=session_id,
            status=incident_status,
            status_color=status_color,
            events=events,
            last_event=last_event,
            tokens_saved=total_tokens_saved,
            cost_saved=total_cost_saved,
            terminal_cost=terminal_cost,
            risk_prob=risk_prob,
            failure_mode=failure_mode,
            primary_reason=primary_reason,
            reroute_directive=reroute_directive,
            sentry_provider=sentry_provider
        )

    return _render_markdown_report(
        session_id=session_id,
        status=incident_status,
        events=events,
        last_event=last_event,
        tokens_saved=total_tokens_saved,
        cost_saved=total_cost_saved,
        terminal_cost=terminal_cost,
        risk_prob=risk_prob,
        failure_mode=failure_mode,
        primary_reason=primary_reason,
        reroute_directive=reroute_directive,
        sentry_provider=sentry_provider
    )


def _render_markdown_report(
    session_id: str,
    status: str,
    events: List[Dict[str, Any]],
    last_event: Dict[str, Any],
    tokens_saved: int,
    cost_saved: float,
    terminal_cost: float,
    risk_prob: float,
    failure_mode: str,
    primary_reason: str,
    reroute_directive: str,
    sentry_provider: str
) -> str:
    timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(last_event.get("timestamp", time.time())))
    
    table_rows = []
    for e in events:
        action_badge = f"**{e['action']}**" if e["action"] != "PASS" else "PASS"
        table_rows.append(
            f"| {e['step_index']} | {action_badge} | {e['risk_level']} | {e['failure_probability']*100:.1f}% | "
            f"{e['predicted_failure_mode']} | ${e['projected_final_cost_usd']:.4f} | {e['reason'][:70]}... |"
        )
    table_content = "\n".join(table_rows)

    return f"""# 🛡️ Agentry Enterprise Incident Post-Mortem Report

**Incident Reference:** `INC-{session_id}`  
**Generated At:** {timestamp_str}  
**Platform Version:** Agentry v{__version__} (TabPFN-3.5 Tabular Control Plane)  
**Session Status:** `{status}`  

---

## 📋 1. Executive Summary

| Attribute | Forensic Value |
| :--- | :--- |
| **Monitored Session ID** | `{session_id}` |
| **Total Steps Audited** | **{len(events)} steps** |
| **TabPFN Calibrated Risk** | **{risk_prob * 100:.1f}%** |
| **Predicted Failure Mode** | **`{failure_mode}`** |
| **Autonomic Intervention** | **`{last_event['action']}`** |
| **Estimated Tokens Saved** | **{tokens_saved:,} tokens** |
| **Estimated Cost Saved** | **${cost_saved:.4f} USD** |
| **Projected Terminal Spend** | **${terminal_cost:.4f} USD** |
| **Sentry Audit Provider** | `{sentry_provider}` |

> **Key Forensic Finding:**  
> {primary_reason}

---

## 🔍 2. Corrective Steering & Remediation

- **Injected Directive:** `{reroute_directive}`
- **Root Cause Recommendation:**
  1. **Prompt Sanitization:** Add explicit stop criteria in system prompt to prevent identical retries on bash error exit codes.
  2. **Tool Boundary Hardening:** If hallucinated tools occurred, verify tool definitions and exclude non-existent command signatures from agent tool inventory.
  3. **Circuit-Breaker Enforcement:** Preserve Agentry TabPFN threshold $\\theta = 0.85$ with streak confirmation to halt runaway token burns before enterprise SLA breach.

---

## 📜 3. Chronological Step-by-Step Audit Trail

| Step | Sentry Action | Risk Level | Failure Risk | Mode Predicted | Projected Cost | Forensic Detail |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
{table_content}

---
*Report generated automatically by Prior Labs TabPFN-3.5 Agentry Governance Engine.*
"""


def _render_html_report(
    session_id: str,
    status: str,
    status_color: str,
    events: List[Dict[str, Any]],
    last_event: Dict[str, Any],
    tokens_saved: int,
    cost_saved: float,
    terminal_cost: float,
    risk_prob: float,
    failure_mode: str,
    primary_reason: str,
    reroute_directive: str,
    sentry_provider: str
) -> str:
    timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(last_event.get("timestamp", time.time())))
    clean_session = html.escape(str(session_id))
    clean_status = html.escape(str(status))
    clean_reason = html.escape(str(primary_reason))
    clean_directive = html.escape(str(reroute_directive))
    clean_provider = html.escape(str(sentry_provider))

    rows_html = ""
    for e in events:
        badge_class = "badge-pass"
        if e["action"] == "KILL":
            badge_class = "badge-kill"
        elif e["action"] == "REROUTE":
            badge_class = "badge-reroute"
        elif e["action"] == "PAUSE":
            badge_class = "badge-pause"

        esc_mode = html.escape(str(e.get("predicted_failure_mode", "")))
        esc_reason = html.escape(str(e.get("reason", "")))
        rows_html += f"""
        <tr>
            <td style="text-align:center;">{e['step_index']}</td>
            <td style="text-align:center;"><span class="badge {badge_class}">{e['action']}</span></td>
            <td style="text-align:center;">{e['risk_level']}</td>
            <td style="text-align:center;">{e['failure_probability']*100:.1f}%</td>
            <td style="text-align:center;"><code>{esc_mode}</code></td>
            <td style="text-align:right;">${e['projected_final_cost_usd']:.4f}</td>
            <td>{esc_reason}</td>
        </tr>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Agentry Post-Mortem Report: {clean_session}</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: #0F172A;
            color: #F8FAFC;
            margin: 0;
            padding: 30px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background-color: #1E293B;
            border: 1px solid #334155;
            border-radius: 12px;
            padding: 32px;
            box-shadow: 0 10px 25px rgba(0,0,0,0.5);
        }}
        h1 {{
            color: #38BDF8;
            margin-top: 0;
            border-bottom: 2px solid #334155;
            padding-bottom: 12px;
        }}
        .status-badge {{
            display: inline-block;
            background-color: {status_color};
            color: white;
            padding: 6px 14px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 0.95rem;
            margin-bottom: 20px;
        }}
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin: 24px 0;
        }}
        .kpi-card {{
            background-color: #0F172A;
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 16px;
            text-align: center;
        }}
        .kpi-value {{
            font-size: 1.6rem;
            font-weight: bold;
            color: #10B981;
        }}
        .kpi-label {{
            font-size: 0.8rem;
            color: #94A3B8;
            text-transform: uppercase;
            margin-top: 4px;
        }}
        .alert-box {{
            background-color: rgba(239, 68, 68, 0.1);
            border-left: 4px solid #EF4444;
            padding: 16px;
            border-radius: 4px;
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 0.9rem;
        }}
        th, td {{
            padding: 10px 12px;
            border-bottom: 1px solid #334155;
            text-align: left;
        }}
        th {{
            background-color: #0F172A;
            color: #94A3B8;
            font-weight: 600;
        }}
        .badge {{
            padding: 3px 8px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.75rem;
        }}
        .badge-pass {{ background-color: #10B981; color: white; }}
        .badge-kill {{ background-color: #EF4444; color: white; }}
        .badge-reroute {{ background-color: #F59E0B; color: black; }}
        .badge-pause {{ background-color: #6366F1; color: white; }}
        code {{
            background-color: #0F172A;
            padding: 2px 6px;
            border-radius: 4px;
            color: #38BDF8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🛡️ Agentry Forensic Incident Report</h1>
        <div class="status-badge">{clean_status}</div>
        <p><strong>Incident Reference:</strong> <code>INC-{clean_session}</code> | <strong>Timestamp:</strong> {timestamp_str} | <strong>Engine:</strong> {clean_provider}</p>

        <div class="kpi-grid">
            <div class="kpi-card">
                <div class="kpi-value">{tokens_saved:,}</div>
                <div class="kpi-label">Tokens Saved</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">${cost_saved:.4f}</div>
                <div class="kpi-label">Dollars Saved</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{risk_prob*100:.1f}%</div>
                <div class="kpi-label">TabPFN Risk Probability</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-value">{len(events)}</div>
                <div class="kpi-label">Steps Audited</div>
            </div>
        </div>

        <div class="alert-box">
            <h3 style="margin-top:0; color:#F8FAFC;">Forensic Summary</h3>
            <p style="margin-bottom:0;">{clean_reason}</p>
        </div>

        <h3>Steering Directive & Recommendations</h3>
        <p><strong>Injected Steering Directive:</strong> <code>{clean_directive}</code></p>

        <h3>Chronological Step Audit Trail</h3>
        <table>
            <thead>
                <tr>
                    <th style="text-align:center;">Step</th>
                    <th style="text-align:center;">Action</th>
                    <th style="text-align:center;">Risk Level</th>
                    <th style="text-align:center;">Risk Prob</th>
                    <th style="text-align:center;">Predicted Mode</th>
                    <th style="text-align:right;">Projected Cost</th>
                    <th>Reason / Detail</th>
                </tr>
            </thead>
            <tbody>
                {rows_html}
            </tbody>
        </table>
        
        <p style="text-align:center; color:#64748B; margin-top:30px; font-size:0.8rem;">
            Generated by Agentry v{__version__} &bull; Prior Labs TabPFN-3.5 Tabular Control Plane &bull; Enterprise AI Governance
        </p>
    </div>
</body>
</html>
"""


def export_incident_report_to_file(
    session_id: str,
    output_dir: Optional[Path] = None,
    format: str = "markdown",
    storage: Optional[AuditStorage] = None
) -> Path:
    """Exports the incident report to disk and returns the resolved file path."""
    target_dir = Path(output_dir) if output_dir else ROOT_DIR / "data" / "reports"
    target_dir.mkdir(parents=True, exist_ok=True)
    
    ext = "html" if format.lower() == "html" else "md"
    file_path = target_dir / f"incident_report_{session_id}.{ext}"
    
    content = generate_incident_report(session_id, format=format, storage=storage)
    file_path.write_text(content, encoding="utf-8")
    return file_path
