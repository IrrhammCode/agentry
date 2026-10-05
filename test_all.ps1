# Complete Subsystem & Integration Test Suite
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "   AGENTRY: Complete Subsystem & Integration Test Suite" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Running Environment Doctor Diagnostic..." -ForegroundColor Yellow
& .\.venv\Scripts\python.exe run.py doctor
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Doctor diagnostic failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/4] Running Core Agentry Pytest Suite (88 tests)..." -ForegroundColor Yellow
& .\.venv\Scripts\python.exe -m pytest tests/ -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Core unit tests failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[3/4] Running Real Project Build Arena Experiment..." -ForegroundColor Yellow
& .\.venv\Scripts\python.exe build_project_experiment.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "[FAIL] Project build experiment failed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host " [ALL TESTS PASSED 100%] System is completely verified and operational!" -ForegroundColor Green
Write-Host "======================================================================" -ForegroundColor Cyan
