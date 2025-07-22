@echo off
REM Simple run script for Excel Macro Automation

REM Activate virtual environment
if exist venv313\Scripts\activate.bat (
    call venv313\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo No virtual environment found!
    echo Please run SETUP_CLEAN.bat or FIX_SETUP.bat first.
    pause
    exit /b
)

REM Run the application
python run_main.py

pause