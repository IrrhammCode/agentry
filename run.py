"""
Agentry main entrypoint script.
Run with:
    python run.py demo       # Live terminal multi-agent fleet guardrail demo
    python run.py benchmark  # Run TabPFN benchmark vs classical ML baselines
    python run.py audit      # Forensic audit on an agent session
    python run.py web        # Launch Streamlit web dashboard
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
