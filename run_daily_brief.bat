@echo off
cd /d "%~dp0"
echo --- Running Aevel HQ Daily Brief ---
python tools/navigation.py --send
if %errorlevel% neq 0 (
    echo [ERROR] Execution failed.
    pause
) else (
    echo [DONE] Execution complete.
    timeout /t 5
)
