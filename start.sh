#!/usr/bin/env bash
set -e

echo "======================================================================"
echo "   AGENTRY: Autonomous AI Fleet Sentry & Control Layer"
echo "   One-Click Quickstart Launcher (Sub-30-Second Startup)"
echo "======================================================================"

# 1. Virtual environment
if [ ! -d ".venv" ]; then
    echo "[*] Creating virtual environment (.venv)..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# 2. Python dependencies
echo "[*] Checking Python dependencies..."
pip install -q -r requirements.txt

# 3. Frontend dependencies
if [ -d "frontend" ] && command -v npm &> /dev/null; then
    if [ ! -d "frontend/node_modules" ]; then
        echo "[*] Installing frontend dependencies..."
        (cd frontend && npm install)
    fi
fi

# 4. Launch Daemon
echo "[*] Launching Agentry REST Daemon on port 8000..."
python run.py serve --port 8000 &
DAEMON_PID=$!

# 5. Launch Frontend
if [ -d "frontend" ]; then
    echo "[*] Launching Agentry Cockpit UI on port 3000..."
    (cd frontend && npm run dev) &
    FRONTEND_PID=$!
fi

echo ""
echo "======================================================================"
echo " [SUCCESS] All Agentry subsystems launched successfully!"
echo " • Web Cockpit UI:  http://localhost:3000"
echo " • Backend Daemon:  http://localhost:8000/health"
echo "======================================================================"

trap "kill $DAEMON_PID $FRONTEND_PID 2>/dev/null" EXIT
wait
