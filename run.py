"""
Agentry main entrypoint script.
Run with:
    python run.py demo                  # Live terminal multi-agent fleet guardrail demo
    python run.py e2e                   # Live end-to-end closed-loop autonomic recovery simulation
    python run.py doctor                # Pre-flight environment & subsystem health diagnostic
    python run.py benchmark             # Run TabPFN benchmark vs classical ML baselines
    python run.py audit [session_id]    # Forensic audit on an agent session
    python run.py rewind [session_id]   # Autonomic trajectory rewind & self-healing prescription
    python run.py budget                # Inspect fleet budget quota & burn rate autopilot
    python run.py report [session_id]   # Export forensic incident post-mortem (MD/HTML)
    python run.py hitl list/resolve     # Manage Human-in-the-Loop approval queue
    python run.py serve                 # Start REST API, OpenAI reverse proxy & Prometheus metrics
    python run.py mcp                   # Launch Model Context Protocol (MCP) server
    python run.py web                   # Launch Streamlit web command center
"""

import sys
from pathlib import Path

# Ensure UTF-8 output encoding on Windows consoles
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Ensure root directory is on Python path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from agentry.cli import main

if __name__ == "__main__":
    main()
