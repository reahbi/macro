@echo off
chcp 65001 >nul
REM === Excel Macro Automation - C Drive Direct Run ===

cls

echo ===============================
echo Excel Macro Automation Tool
echo ===============================
echo.

REM Set current path
set "CURRENT_PATH=%~dp0"
echo Execution Path: %CURRENT_PATH%

REM Change to project directory
cd /d "%~dp0"
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to change to project directory!
    echo Path: %~dp0
    echo.
    pause
    exit /b
)

echo Current Directory: %CD%
echo.

:CHECK_PYTHON
REM Check Python
echo.
echo Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python is not installed!
    echo.
    echo 1. Download Python from https://python.org
    echo 2. Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b
)

python --version
echo.

REM Install required packages
echo Installing packages... (This may take time on first run)
echo.
echo Main packages:
echo - PyQt5 (GUI framework)
echo - pandas, openpyxl (Excel processing)
echo - pyautogui, opencv-python (Screen automation)
echo - easyocr (Text recognition) - May take time to install
echo.

REM Upgrade pip
python -m pip install --upgrade pip >nul 2>&1

REM Install base packages
echo Installing base packages...
pip install PyQt5 pandas openpyxl pyautogui pillow screeninfo cryptography opencv-python numpy mss --quiet --no-warn-script-location

REM Install EasyOCR separately
echo.
echo Installing EasyOCR... (Model download may take time on first run)
pip install easyocr --quiet --no-warn-script-location

if errorlevel 1 (
    echo.
    echo [WARNING] Some packages failed to install. Manual installation may be required.
    echo.
)

REM Check for execution file
echo.
echo Checking execution files...
if exist "run_main.py" (
    set "EXEC_FILE=run_main.py"
    echo Using primary launcher: run_main.py
) else if exist "run_main_fixed.py" (
    set "EXEC_FILE=run_main_fixed.py"
    echo Using fallback launcher: run_main_fixed.py
) else (
    echo.
    echo [ERROR] No execution file found!
    echo Looking for: run_main.py or run_main_fixed.py
    echo Current directory: %CD%
    echo.
    echo Directory contents:
    dir *.py
    echo.
    pause
    exit /b
)

REM Execute
echo.
echo ===============================
echo Starting application...
echo ===============================
echo.

python "%EXEC_FILE%"

REM Check execution result
set EXIT_CODE=%errorlevel%

REM Exit handling
echo.
if %EXIT_CODE% neq 0 (
    echo ===============================
    echo [ERROR] Application error occurred.
    echo Error code: %EXIT_CODE%
    echo ===============================
) else (
    echo ===============================
    echo Application terminated successfully.
    echo ===============================
)

echo.
echo Press any key to close...
pause >nul

REM No cleanup needed - running directly from project directory

exit /b %EXIT_CODE%