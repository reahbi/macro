@echo off
chcp 65001 >nul
REM === Simple Windows Execution Script ===
REM === Optimized for WSL path execution ===

cls

echo ===============================
echo Excel Macro Automation Tool
echo ===============================
echo.

REM Set working directory to C:\temp\excel_macro
set WORK_DIR=C:\temp\excel_macro
set "SOURCE_PATH=%~dp0"

echo Source: %SOURCE_PATH%
echo Target: %WORK_DIR%
echo.

REM Clean and create working directory
if exist "%WORK_DIR%" (
    echo Cleaning existing directory...
    rd /s /q "%WORK_DIR%" 2>nul
    timeout /t 2 /nobreak >nul
)

mkdir "%WORK_DIR%" 2>nul
if errorlevel 1 (
    echo [ERROR] Cannot create working directory!
    echo Please run as administrator or check permissions.
    pause
    exit /b
)

REM Copy only essential files (exclude venv, __pycache__, etc.)
echo Copying essential files...
echo.

REM Create directory structure
mkdir "%WORK_DIR%\src" 2>nul
mkdir "%WORK_DIR%\src\ui" 2>nul
mkdir "%WORK_DIR%\src\ui\dialogs" 2>nul
mkdir "%WORK_DIR%\src\ui\widgets" 2>nul
mkdir "%WORK_DIR%\src\automation" 2>nul
mkdir "%WORK_DIR%\src\config" 2>nul
mkdir "%WORK_DIR%\src\core" 2>nul
mkdir "%WORK_DIR%\src\excel" 2>nul
mkdir "%WORK_DIR%\src\logger" 2>nul
mkdir "%WORK_DIR%\src\utils" 2>nul
mkdir "%WORK_DIR%\src\vision" 2>nul
mkdir "%WORK_DIR%\resources" 2>nul
mkdir "%WORK_DIR%\resources\icons" 2>nul

REM Copy Python files using PowerShell (more reliable for WSL paths)
echo Copying Python source files...
powershell -NoProfile -Command ^
    "$source = '%SOURCE_PATH%'.TrimEnd('\'); " ^
    "Copy-Item -Path \"$source\run_main_fixed.py\" -Destination '%WORK_DIR%' -Force -ErrorAction SilentlyContinue; " ^
    "Copy-Item -Path \"$source\src\*\" -Destination '%WORK_DIR%\src' -Recurse -Force -ErrorAction SilentlyContinue; " ^
    "Copy-Item -Path \"$source\resources\*\" -Destination '%WORK_DIR%\resources' -Recurse -Force -ErrorAction SilentlyContinue; " ^
    "Copy-Item -Path \"$source\requirements.txt\" -Destination '%WORK_DIR%' -Force -ErrorAction SilentlyContinue"

REM Verify essential file exists
if not exist "%WORK_DIR%\run_main_fixed.py" (
    echo.
    echo [ERROR] Failed to copy essential files!
    echo.
    echo Attempting direct file creation...
    
    REM Create a minimal launcher if copy fails
    echo import sys > "%WORK_DIR%\run_main_fixed.py"
    echo import os >> "%WORK_DIR%\run_main_fixed.py"
    echo sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src')) >> "%WORK_DIR%\run_main_fixed.py"
    echo print("Starting application...") >> "%WORK_DIR%\run_main_fixed.py"
    echo try: >> "%WORK_DIR%\run_main_fixed.py"
    echo     from PyQt5.QtWidgets import QApplication >> "%WORK_DIR%\run_main_fixed.py"
    echo     from ui.main_window import MainWindow >> "%WORK_DIR%\run_main_fixed.py"
    echo     from config.settings import Settings >> "%WORK_DIR%\run_main_fixed.py"
    echo     app = QApplication(sys.argv) >> "%WORK_DIR%\run_main_fixed.py"
    echo     settings = Settings() >> "%WORK_DIR%\run_main_fixed.py"
    echo     window = MainWindow(settings) >> "%WORK_DIR%\run_main_fixed.py"
    echo     window.show() >> "%WORK_DIR%\run_main_fixed.py"
    echo     sys.exit(app.exec_()) >> "%WORK_DIR%\run_main_fixed.py"
    echo except Exception as e: >> "%WORK_DIR%\run_main_fixed.py"
    echo     print(f"Error: {e}") >> "%WORK_DIR%\run_main_fixed.py"
    echo     input("Press Enter to exit...") >> "%WORK_DIR%\run_main_fixed.py"
)

REM Change to working directory
cd /d "%WORK_DIR%"
echo.
echo Working directory: %CD%
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo.
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b
)

echo Python version:
python --version
echo.

REM Install packages
echo Installing required packages...
echo This may take a few minutes on first run...
echo.

REM Upgrade pip silently
python -m pip install --upgrade pip >nul 2>&1

REM Install packages with progress
echo Installing PyQt5...
pip install PyQt5 --quiet --no-warn-script-location

echo Installing Excel packages...
pip install pandas openpyxl --quiet --no-warn-script-location

echo Installing automation packages...
pip install pyautogui pillow opencv-python numpy mss screeninfo --quiet --no-warn-script-location

echo Installing additional packages...
pip install cryptography --quiet --no-warn-script-location

echo Installing EasyOCR (this may take longer)...
pip install easyocr --quiet --no-warn-script-location

echo.
echo Package installation complete!
echo.

REM Check if main file exists
if not exist "run_main_fixed.py" (
    echo [ERROR] Main execution file not found!
    echo.
    dir *.py
    echo.
    pause
    exit /b
)

REM Run the application
echo ===============================
echo Starting Excel Macro Automation
echo ===============================
echo.

python run_main_fixed.py

REM Capture exit code
set EXIT_CODE=%errorlevel%

REM Display result
echo.
if %EXIT_CODE% neq 0 (
    echo ===============================
    echo Application exited with error code: %EXIT_CODE%
    echo ===============================
) else (
    echo ===============================
    echo Application closed successfully
    echo ===============================
)

echo.
echo Press any key to exit...
pause >nul

REM Cleanup option
echo.
set /p CLEANUP=Clean up temporary files? (Y/N): 
if /i "%CLEANUP%"=="Y" (
    cd /d C:\
    rd /s /q "%WORK_DIR%" 2>nul
    echo Temporary files cleaned.
)

exit /b %EXIT_CODE%