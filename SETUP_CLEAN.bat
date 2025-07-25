@echo off
echo ========================================
echo Clean Setup for Excel Macro Automation
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found!
    echo Please install Python 3.x first.
    pause
    exit /b
)

echo Python found:
python --version
echo.

REM Kill any running Python processes
echo Terminating Python processes...
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 >nul

REM Remove old virtual environments
echo Removing old virtual environments...
if exist venv rmdir /s /q venv
if exist venv_auto rmdir /s /q venv_auto
if exist venv313 rmdir /s /q venv313
timeout /t 2 >nul

REM Create new virtual environment
echo Creating new virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment
    pause
    exit /b
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install packages in correct order
echo.
echo Installing packages...
echo.

echo [1/7] Installing PyQt5...
pip install PyQt5==5.15.11

echo.
echo [2/7] Installing data processing libraries...
pip install pandas openpyxl

echo.
echo [3/7] Installing automation tools...
pip install pyautogui pillow pynput

echo.
echo [4/7] Installing utilities...
pip install screeninfo mss cryptography chardet psutil

echo.
echo [5/7] Installing NumPy (compatible version)...
pip install "numpy>=2.0.0,<2.3.0"

echo.
echo [6/7] Installing OpenCV...
pip install opencv-python==4.12.0.88

echo.
echo [7/7] Installing PaddleOCR (optional, may take time)...
pip install paddlepaddle>=2.5.0 paddleocr>=2.7.0 || echo [Info] PaddleOCR installation skipped

echo.
echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo To run the application:
echo 1. venv\Scripts\activate
echo 2. python run_main.py
echo.
pause