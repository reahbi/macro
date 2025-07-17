@echo off
chcp 65001 >nul
REM === Direct Windows Execution (No Copy) ===

cls

echo ===============================
echo Excel Macro Automation Tool
echo ===============================
echo Direct Execution Mode
echo ===============================
echo.

REM Store the original path
set "SCRIPT_DIR=%~dp0"
echo Script location: %SCRIPT_DIR%

REM Check if we're on a UNC path
if "%SCRIPT_DIR:~0,2%"=="\\" (
    echo.
    echo [INFO] Running from network/WSL path
    echo Mapping to temporary drive...
    
    REM Find an available drive letter
    for %%D in (Z Y X W V U T S R Q P) do (
        if not exist %%D:\ (
            echo Mapping %SCRIPT_DIR% to %%D:
            pushd "%SCRIPT_DIR%" 2>nul
            if not errorlevel 1 (
                set "MAPPED_DRIVE=%%D:"
                goto :mapped
            )
        )
    )
    
    echo [ERROR] Could not map network path to drive letter
    pause
    exit /b
    
    :mapped
    echo Successfully mapped to drive
) else (
    REM Local path, just change directory
    cd /d "%SCRIPT_DIR%"
)

echo.
echo Working directory: %CD%
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo.
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH"
    echo.
    pause
    goto :cleanup
)

echo Python version:
python --version
echo.

REM Quick package check and install
echo Checking required packages...
python -c "import PyQt5" 2>nul
if errorlevel 1 (
    echo Installing GUI framework...
    pip install PyQt5 --quiet
)

python -c "import pandas" 2>nul
if errorlevel 1 (
    echo Installing data processing packages...
    pip install pandas openpyxl --quiet
)

python -c "import pyautogui" 2>nul
if errorlevel 1 (
    echo Installing automation packages...
    pip install pyautogui pillow opencv-python numpy mss screeninfo --quiet
)

python -c "import easyocr" 2>nul
if errorlevel 1 (
    echo Installing OCR package (this may take a while)...
    pip install easyocr --quiet
)

echo.
echo All packages ready!
echo.

REM Check for main script
if not exist "run_main_fixed.py" (
    echo [ERROR] run_main_fixed.py not found!
    echo Current directory: %CD%
    echo.
    dir *.py
    echo.
    pause
    goto :cleanup
)

REM Run the application
echo ===============================
echo Starting application...
echo ===============================
echo.

python run_main_fixed.py

set EXIT_CODE=%errorlevel%

echo.
if %EXIT_CODE% neq 0 (
    echo ===============================
    echo [ERROR] Exit code: %EXIT_CODE%
    echo ===============================
) else (
    echo ===============================
    echo Application closed successfully
    echo ===============================
)

:cleanup
REM If we mapped a drive, unmap it
if defined MAPPED_DRIVE (
    echo.
    echo Unmapping temporary drive...
    popd
)

echo.
echo Press any key to exit...
pause >nul
exit /b %EXIT_CODE%