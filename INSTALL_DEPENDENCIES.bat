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

REM Check Python
echo Checking Python installation...
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [ERROR] Python is not installed or not in PATH!
    echo.
    echo Please install Python from: https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

python --version
echo Python found!
echo.

REM Check pip
echo Checking pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip not found!
    pause
    exit /b 1
)

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Check if requirements.txt exists
if exist "requirements.txt" (
    echo.
    echo Installing from requirements.txt...
    python -m pip install -r requirements.txt
    
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
python -m pip install PyQt5>=5.15.0

echo Installing data processing libraries...
python -m pip install pandas>=1.3.0 openpyxl>=3.0.0 numpy>=1.21.0

echo Installing automation libraries...
python -m pip install pyautogui>=0.9.53 pillow>=8.3.0 opencv-python>=4.5.0

echo Installing screen capture...
python -m pip install screeninfo>=0.8.0 mss>=6.1.0

echo Installing security...
python -m pip install cryptography>=3.4.0

echo.
echo Installing OCR (This may take a while on first install)...
python -m pip install easyocr>=1.7.0

echo.
echo Installing testing frameworks (optional)...
python -m pip install pytest>=6.2.0 pytest-qt>=4.0.0

echo.
echo Installing development tools (optional)...
python -m pip install black>=21.0 flake8>=3.9.0

:SUCCESS
echo.
echo ===============================
echo Dependencies installation completed!
echo ===============================
echo.

REM Test import key packages
echo Testing package imports...
python -c "import PyQt5; print('✓ PyQt5 OK')" 2>nul
python -c "import pandas; print('✓ pandas OK')" 2>nul  
python -c "import pyautogui; print('✓ pyautogui OK')" 2>nul
python -c "import cv2; print('✓ opencv OK')" 2>nul

echo.
echo Ready to run Excel Macro Automation!
echo Use WINDOWS_RUN.bat or RUN_SIMPLE.bat to start the application.
echo.

pause