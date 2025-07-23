@echo off
REM Setup Python 3.13 virtual environment

echo Creating Python 3.13 virtual environment...

REM Check if Python 3.13 is available
python --version | findstr "3.13" >nul
if errorlevel 1 (
    echo Python 3.13 not found! Please install Python 3.13 first.
    pause
    exit /b 1
)

REM Remove existing venv313 if exists
if exist venv313 (
    echo Removing existing venv313...
    rmdir /s /q venv313
)

REM Create new virtual environment
echo Creating new virtual environment...
python -m venv venv313

REM Activate virtual environment
call venv313\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo Virtual environment setup complete!
echo To activate: call venv313\Scripts\activate.bat
echo To run app: python run_main.py
pause