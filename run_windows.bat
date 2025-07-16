@echo off
echo === Excel Macro Automation Tool - Windows Runner ===
echo.

REM Handle UNC path issue by mapping to a temporary drive
if "%~d0"=="\\" (
    echo Detected UNC path. Creating temporary drive mapping...
    pushd "%~dp0"
) else (
    cd /d "%~dp0"
)

echo Working directory: %cd%
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Python is not installed or not in PATH!
    echo Please install Python from python.org
    pause
    exit /b 1
)

REM Check for virtual environment
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment!
        pause
        exit /b 1
    )
    call venv\Scripts\activate.bat
)

REM Install dependencies
echo.
echo Checking dependencies...
if exist "requirements.txt" (
    echo Installing requirements...
    python -m pip install --upgrade pip
    pip install -r requirements.txt
) else (
    echo Installing core packages...
    python -m pip install --upgrade pip
    pip install PyQt5 pandas openpyxl pyautogui pillow screeninfo cryptography opencv-python numpy mss easyocr
)

REM Set environment variables
set QT_AUTO_SCREEN_SCALE_FACTOR=1
set QT_ENABLE_HIGHDPI_SCALING=1
set PYTHONIOENCODING=utf-8

REM Run the application
echo.
echo Starting Excel Macro Automation Tool...
echo Note: Running in native Windows mode for better GUI compatibility
echo.

python run_main_fixed.py

REM Keep window open regardless of result
echo.
echo Program execution completed.
pause

REM Clean up temporary drive mapping if used
if "%~d0"=="\\" (
    popd
)