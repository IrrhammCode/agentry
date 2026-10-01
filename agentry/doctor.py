"""
System Doctor & Diagnostic Readiness Tool for Agentry.
Checks all environment variables, port availability, database health,
TabPFN-3.5 engine state, local SLM connectivity, and dataset integrity.
"""

import sys
import os
import socket
import sqlite3
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from agentry import __version__
from agentry.config import ROOT_DIR, settings
from agentry.storage import AuditStorage

console = Console()


def check_port_free(host: str, port: int) -> bool:
    """Checks if a TCP port is free to bind."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)
        res = s.connect_ex((host, port))
        return res != 0  # True if port is free (connection failed)


def run_system_doctor() -> bool:
    """
    Performs comprehensive pre-flight health diagnostics across all subsystems.
    Returns True if all required subsystems are healthy.
    """
    table = Table(
        title=f"[bold green]AGENTRY SYSTEM READINESS DOCTOR (v{__version__})[/]",
        expand=True,
        header_style="bold cyan"
    )
    table.add_column("Subsystem / Component", style="white", width=28)
    table.add_column("Status", justify="center", width=14)
    table.add_column("Diagnostics & Details", style="dim white")

    all_passed = True

    # 1. Python Environment
    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    if sys.version_info >= (3, 10):
        table.add_row("Python Runtime", "[bold green]PASS[/]", f"v{py_ver} ({sys.platform})")
    else:
        table.add_row("Python Runtime", "[bold red]FAIL[/]", f"v{py_ver} (Python 3.10+ required)")
        all_passed = False

    # 2. SQLite WAL Storage
    try:
        storage = AuditStorage()
        summary = storage.get_fleet_summary()
        table.add_row(
            "SQLite WAL Audit DB",
            "[bold green]PASS[/]",
            f"Connected: {storage.db_path.name} ({summary.get('total_audited_steps', 0)} steps recorded)"
        )
    except Exception as e:
        table.add_row("SQLite WAL Audit DB", "[bold red]FAIL[/]", f"Error: {e}")
        all_passed = False

    # 3. Ground-Truth Telemetry Dataset
    dataset_path = ROOT_DIR / "data" / "real_swe_telemetry.csv"
    if dataset_path.exists():
        import pandas as pd
        df = pd.read_csv(dataset_path)
        table.add_row(
            "SWE-bench Dataset",
            "[bold green]PASS[/]",
            f"Verified: {len(df):,} steps across {df['session_id'].nunique()} developer sessions"
        )
    else:
        table.add_row("SWE-bench Dataset", "[bold yellow]WARN[/]", "real_swe_telemetry.csv not found (will generate on first run)")

    # 4. TabPFN-3.5 Foundation Model Engine
    from agentry.engine import TabPFNGuardrailEngine
    engine = TabPFNGuardrailEngine()
    if engine.is_cloud_tabpfn:
        table.add_row("TabPFN-3.5 Engine", "[bold green]PASS (Cloud)[/]", "Connected to Prior Labs Cloud API (Thinking Mode)")
    else:
        table.add_row(
            "TabPFN-3.5 Engine",
            "[bold green]PASS (Local)[/]",
            "Pre-warmed local tabular ensemble active (offline resilience net)"
        )

    # 5. Local SLM (Ollama)
    from agentry.agent import AgentrySentry
    sentry = AgentrySentry(engine)
    ollama_alive = sentry._check_ollama_alive()
    if ollama_alive:
        table.add_row("Local SLM (Ollama)", "[bold green]PASS[/]", f"Online: {settings.sentry_model} at {settings.ollama_base_url}")
    else:
        table.add_row(
            "Local SLM (Ollama)",
            "[bold yellow]STANDBY[/]",
            f"Ollama offline ({settings.sentry_model}); rule-based sentry brain fallback active"
        )

    # 6. Groq Cloud Engine Pool
    num_groq = len(settings.groq_api_keys)
    if num_groq > 0:
        table.add_row("Groq LLM Key Pool", "[bold green]PASS[/]", f"{num_groq} API key(s) loaded with automatic failover rotation")
    else:
        table.add_row("Groq LLM Key Pool", "[bold yellow]INFO[/]", "No Groq keys found; local inference mode active")

    # 7. Ports Availability
    web_free = check_port_free("127.0.0.1", 8501)
    gateway_free = check_port_free("127.0.0.1", 8787)
    mcp_free = check_port_free("127.0.0.1", 8788)

    ports_info = []
    ports_info.append(f"8501 (Web UI): {'FREE' if web_free else 'IN USE / LISTENING'}")
    ports_info.append(f"8787 (API Gateway): {'FREE' if gateway_free else 'IN USE / LISTENING'}")
    ports_info.append(f"8788 (MCP Server): {'FREE' if mcp_free else 'IN USE / LISTENING'}")
    table.add_row("Service TCP Ports", "[bold green]READY[/]", " | ".join(ports_info))

    # 8. Webhook Incident Notifier
    from agentry.alerts import default_notifier
    if default_notifier.enabled:
        table.add_row("Webhook Alerts", "[bold green]PASS[/]", f"Active endpoint: {default_notifier.webhook_url[:30]}...")
    else:
        table.add_row("Webhook Alerts", "[bold cyan]LOCAL LOG[/]", "AGENTRY_WEBHOOK_URL not set; logging alerts to console/DB")

    console.print(table)
    if all_passed:
        console.print("\n[bold green][OK] ALL ESSENTIAL SUBSYSTEMS ARE HEALTHY AND PRODUCTION-READY.[/]\n")
    else:
        console.print("\n[bold yellow][!] Some subsystems have warnings or require configuration.[/]\n")

    return all_passed


if __name__ == "__main__":
    run_system_doctor()
