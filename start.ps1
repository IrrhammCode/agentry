# Agentry PowerShell Quickstart Launcher
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   AGENTRY: Autonomous AI Fleet Sentry & Control Layer" -ForegroundColor Cyan
Write-Host "   One-Click Quickstart Launcher (Sub-30-Second Startup)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# 1. Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python is not installed or not in PATH! Please install Python 3.10+." -ForegroundColor Red
    exit 1
}

# 2. Check / Create Virtual Environment
if (-not (Test-Path ".venv")) {
    Write-Host "[*] Creating virtual environment (.venv)..." -ForegroundColor Yellow
    python -m venv .venv
}

# 3. Check Python Dependencies
Write-Host "[*] Checking Python dependencies..." -ForegroundColor Gray
& .\.venv\Scripts\pip.exe install -q -r requirements.txt

# 4. Check Frontend Dependencies
if (Get-Command npm -ErrorAction SilentlyContinue) {
    if (-not (Test-Path "frontend\node_modules")) {
        Write-Host "[*] Installing frontend dependencies (npm install)..." -ForegroundColor Yellow
        Push-Location frontend
        npm install
        Pop-Location
    }
}

# 5. Launch Agentry Backend Daemon
Write-Host "[*] Launching Agentry REST Daemon (Port 8000)..." -ForegroundColor Green
Start-Process -FilePath "cmd.exe" -ArgumentList "/k", ".\.venv\Scripts\python.exe run.py serve --port 8000"

# 6. Launch Frontend Dev Server
if (Test-Path "frontend") {
    Write-Host "[*] Launching Agentry Cockpit UI (Port 3000)..." -ForegroundColor Green
    Start-Process -FilePath "cmd.exe" -ArgumentList "/k", "cd frontend && npm.cmd run dev"
}

# 7. Launch NovaStore E-Commerce
if (Test-Path "projects_arena\novastore") {
    Write-Host "[*] Launching NovaStore E-Commerce (Port 5051)..." -ForegroundColor Green
    Start-Process -FilePath "cmd.exe" -ArgumentList "/k", ".\.venv\Scripts\python.exe -m uvicorn projects_arena.novastore.app:app --host 127.0.0.1 --port 5051"
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " [SUCCESS] All Agentry subsystems launched successfully!" -ForegroundColor Green
Write-Host " • Web Cockpit UI:  http://localhost:3000" -ForegroundColor White
Write-Host " • Backend Daemon:  http://localhost:8000/health" -ForegroundColor White
Write-Host " • NovaStore Demo:  http://127.0.0.1:5051" -ForegroundColor White
Write-Host "======================================================================" -ForegroundColor Cyan

Start-Sleep -Seconds 2
Start-Process "http://localhost:3000"
