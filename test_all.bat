@echo off
chcp 65001 >nul
echo ======================================================================
echo    AGENTRY: Complete Subsystem ^& Integration Test Suite
echo ======================================================================
echo.

echo [1/4] Running Environment Doctor Diagnostic...
.venv\Scripts\python.exe run.py doctor
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Doctor diagnostic failed!
    exit /b 1
)

echo.
echo [2/4] Running Core Agentry Pytest Suite (88 tests)...
.venv\Scripts\python.exe -m pytest tests/ -q
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Core unit tests failed!
    exit /b 1
)

echo.
echo [3/4] Running Real Project Build Arena Experiment...
.venv\Scripts\python.exe build_project_experiment.py
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] Project build experiment failed!
    exit /b 1
)

echo.
echo [4/4] Running NovaStore E-Commerce Integration Tests (10 tests)...
.venv\Scripts\python.exe -m pytest projects_arena\novastore\tests\test_store.py -q
if %ERRORLEVEL% NEQ 0 (
    echo [FAIL] NovaStore tests failed!
    exit /b 1
)

echo.
echo ======================================================================
echo  [ALL TESTS PASSED 100%%] System is completely verified and operational!
echo ======================================================================
pause
