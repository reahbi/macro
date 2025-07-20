@echo off
chcp 65001 >nul
REM === Simple Excel Macro Launcher ===

cls

echo ===============================
echo Excel Macro Automation
echo ===============================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Quick Python check
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found! Please install Python first.
    pause
    exit /b
)

echo Starting application...
echo.

REM Run the application
if exist "run_main.py" (
    python run_main.py
) else if exist "run_main_fixed.py" (
    python run_main_fixed.py
) else (
    echo [ERROR] No launcher found!
    echo Please ensure run_main.py exists.
    pause
    exit /b
)

echo.
echo Application closed.
pause