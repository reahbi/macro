@echo off
REM Run with Python 3.11 directly (no virtual environment)
REM This is useful for testing or when venv is not set up

echo Excel Macro Automation - Python 3.11 Direct Runner
echo ==================================================
echo.

REM Check if Python 3.11 is available
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python 3.11 not found!
    echo.
    echo Please install Python 3.11 from:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

echo Using Python 3.11:
py -3.11 --version
echo.

echo Starting Excel Macro Automation...
echo.

REM Run with Python 3.11
py -3.11 run_main.py

REM Check if the app exited with error
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)

pause