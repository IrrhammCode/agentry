@echo off
chcp 65001 >nul
echo ======================================================================
echo    AGENTRY: Autonomous AI Fleet Sentry ^& Control Layer
echo    One-Click Quickstart Launcher (Sub-30-Second Startup)
echo ======================================================================
echo.

:: 1. Check Python
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in PATH! Please install Python 3.10+.
    pause
    exit /b 1
)

:: 2. Check / Create Virtual Environment
if not exist ".venv" (
    echo [*] Creating virtual environment (.venv)...
    python -m venv .venv
)

:: 3. Install Python Dependencies
echo [*] Checking Python dependencies...
.venv\Scripts\pip.exe install -q -r requirements.txt

:: 4. Check Frontend Dependencies
where npm >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    if not exist "frontend\node_modules" (
        echo [*] Installing frontend npm dependencies...
        pushd frontend
        call npm.cmd install
        popd
    )
) else (
    echo [WARN] npm not found. Frontend dev server might need manual launch.
)

:: 5. Launch Agentry Backend Daemon
echo [*] Launching Agentry REST Daemon on http://localhost:8000 ...
start "Agentry Daemon (Port 8000)" cmd /k ".venv\Scripts\python.exe run.py serve --port 8000"

:: 6. Launch Frontend Dev Server
if exist "frontend" (
    echo [*] Launching Agentry Cockpit UI on http://localhost:3000 ...
    start "Agentry Frontend (Port 3000)" cmd /k "cd frontend && npm.cmd run dev"
)

:: 7. Launch General Project (NovaStore)
if exist "projects_arena\novastore" (
    echo [*] Launching NovaStore E-Commerce on http://127.0.0.1:5051 ...
    start "NovaStore App (Port 5051)" cmd /k ".venv\Scripts\python.exe -m uvicorn projects_arena.novastore.app:app --host 127.0.0.1 --port 5051"
)

echo.
echo ======================================================================
echo  [SUCCESS] All Agentry subsystems launched successfully!
echo.
echo  • Web Cockpit UI:  http://localhost:3000
echo  • Backend Daemon:  http://localhost:8000/health
echo  • NovaStore Demo:  http://127.0.0.1:5051
echo ======================================================================
echo.
timeout /t 3 >nul
start http://localhost:3000
pause
