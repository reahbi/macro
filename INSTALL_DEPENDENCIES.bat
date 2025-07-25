@echo off
chcp 65001 >nul
REM === Excel Macro Dependencies Installer ===

cls

echo ===============================
echo Excel Macro Dependencies Setup
echo ===============================
echo.

REM Change to project directory
cd /d "%~dp0"

REM Check Python 3.11
echo Checking Python 3.11 installation...
py -3.11 --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python 3.11 is not installed!
    echo.
    echo PaddleOCR requires Python 3.8, 3.9, 3.10, or 3.11
    echo Please install Python 3.11 from: https://www.python.org/downloads/
    echo.
    echo Current Python version:
    python --version 2>nul
    echo.
    pause
    exit /b 1
)

echo Found Python 3.11:
py -3.11 --version
echo.

REM Check pip
echo Checking pip...
py -3.11 -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip not found!
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
py -3.11 -m pip install --upgrade pip

REM Check if requirements.txt exists
if exist "requirements.txt" (
    echo.
    echo Installing from requirements.txt...
    py -3.11 -m pip install -r requirements.txt
    
    if errorlevel 1 (
        echo.
        echo [WARNING] Some packages from requirements.txt failed to install.
        echo Trying individual package installation...
    ) else (
        echo.
        echo ✓ All dependencies installed successfully from requirements.txt!
        goto :SUCCESS
    )
)

REM Manual package installation
echo.
echo Installing core packages individually...
echo.

echo Installing GUI framework (PyQt5)...
py -3.11 -m pip install PyQt5>=5.15.0

echo Installing data processing libraries...
py -3.11 -m pip install pandas>=1.3.0 openpyxl>=3.0.0 numpy>=1.21.0

echo Installing automation libraries...
py -3.11 -m pip install pyautogui>=0.9.53 pillow>=8.3.0 opencv-python>=4.5.0

echo Installing screen capture...
py -3.11 -m pip install screeninfo>=0.8.0 mss>=6.1.0

echo Installing security...
py -3.11 -m pip install cryptography>=3.4.0

echo.
echo Installing OCR - PaddleOCR (This may take a while on first install)...
py -3.11 -m pip install paddlepaddle>=2.5.0 paddleocr>=2.7.0

echo.
echo Installing development tools (optional)...
py -3.11 -m pip install black>=21.0 flake8>=3.9.0

:SUCCESS
echo.
echo ===============================
echo Dependencies installation completed!
echo ===============================
echo.

REM Test import key packages
echo Testing package imports...
py -3.11 -c "import PyQt5; print('✓ PyQt5 OK')" 2>nul
py -3.11 -c "import pandas; print('✓ pandas OK')" 2>nul  
py -3.11 -c "import pyautogui; print('✓ pyautogui OK')" 2>nul
py -3.11 -c "import cv2; print('✓ opencv OK')" 2>nul
py -3.11 -c "import paddleocr; print('✓ PaddleOCR OK')" 2>nul

echo.
echo Ready to run Excel Macro Automation!
echo Use WINDOWS_RUN.bat or RUN_SIMPLE.bat to start the application.
echo.

pause