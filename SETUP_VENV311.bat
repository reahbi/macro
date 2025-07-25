@echo off
REM Setup Python 3.11 virtual environment for PaddleOCR compatibility

echo Creating Python 3.11 virtual environment for PaddleOCR...
echo =========================================================
echo.

REM Check if Python 3.11 is available using py launcher
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo Python 3.11 not found! 
    echo.
    echo PaddleOCR requires Python 3.8, 3.9, 3.10, or 3.11
    echo Please install Python 3.11 from https://www.python.org/downloads/
    echo.
    echo Current Python version:
    python --version
    echo.
    pause
    exit /b 1
)

echo Found Python 3.11!
py -3.11 --version

REM Remove existing venv311 if exists
if exist venv311 (
    echo Removing existing venv311...
    rmdir /s /q venv311
)

REM Create new virtual environment with Python 3.11
echo Creating new virtual environment with Python 3.11...
py -3.11 -m venv venv311

REM Activate virtual environment
call venv311\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Virtual environment setup complete!
echo To activate: call venv311\Scripts\activate.bat
echo To run app: python run_main.py
echo.
echo Note: PaddleOCR is now installed and will be used for text recognition.
pause