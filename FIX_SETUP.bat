@echo off
echo ========================================
echo Fix Setup Issues
echo ========================================
echo.

REM 1. Kill all Python processes
echo [1/5] Terminating all Python processes...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 3 >nul

REM 2. Remove problematic virtual environments
echo [2/5] Removing problematic virtual environments...
if exist venv_auto (
    echo Removing venv_auto...
    attrib -r -h -s venv_auto\*.* /s
    rmdir /s /q venv_auto 2>nul
    if exist venv_auto (
        echo Failed to remove venv_auto. Trying alternative method...
        rd /s /q venv_auto
    )
)

REM 3. Clear pip cache
echo [3/5] Clearing pip cache...
rmdir /s /q %LOCALAPPDATA%\pip\cache 2>nul

REM 4. Create clean virtual environment with venv313
echo [4/5] Using existing venv313...
if not exist venv313 (
    echo Creating venv313...
    python -m venv venv313
)

REM 5. Activate and install minimal requirements
echo [5/5] Installing core packages...
call venv313\Scripts\activate.bat

REM Upgrade pip first
python -m pip install --upgrade pip

REM Install in specific order to avoid conflicts
pip install --no-cache-dir PyQt5==5.15.11
pip install --no-cache-dir pandas openpyxl
pip install --no-cache-dir pyautogui
pip install --no-cache-dir pillow
pip install --no-cache-dir pynput
pip install --no-cache-dir screeninfo mss
pip install --no-cache-dir cryptography chardet psutil
pip install --no-cache-dir "numpy>=2.0.0,<2.3.0"
pip install --no-cache-dir opencv-python==4.12.0.88

echo.
echo ========================================
echo Setup Fixed!
echo ========================================
echo.
echo To run the application:
echo 1. venv313\Scripts\activate
echo 2. python run_main.py
echo.
pause