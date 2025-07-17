@echo off
chcp 65001 >nul
REM === Windows Run Script (WSL and Local Path Support) ===

cls

echo ===============================
echo Excel Macro Automation Tool
echo ===============================
echo.

REM Check current path
set "CURRENT_PATH=%~dp0"
echo Execution Path: %CURRENT_PATH%

REM Check if WSL path (contains \\wsl)
echo %CURRENT_PATH% | find "\\wsl" >nul
if %errorlevel%==0 (
    echo WSL path detected. Copying to local folder...
    goto :WSL_MODE
) else (
    echo Running from local path...
    goto :LOCAL_MODE
)

:WSL_MODE
REM === WSL Mode: Copy to temp folder and run ===
set WORK_DIR=C:\temp\excel_macro
echo Working Directory: %WORK_DIR%

REM Delete existing folder
if exist "%WORK_DIR%" (
    echo Cleaning existing folder...
    rd /s /q "%WORK_DIR%" 2>nul
    timeout /t 1 /nobreak >nul
)

REM Create new folder
mkdir "%WORK_DIR%" 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] Cannot create working directory!
    echo Administrator privileges may be required.
    echo.
    pause
    exit /b
)

REM Copy files
echo Copying files from WSL...
echo This may take a moment...
REM Use robocopy for better UNC path support
robocopy "%CURRENT_PATH%." "%WORK_DIR%" /E /NFL /NDL /NJH /NJS /nc /ns /np
if errorlevel 8 (
    echo.
    echo [ERROR] File copy failed!
    echo Source: %CURRENT_PATH%
    echo Target: %WORK_DIR%
    echo.
    echo Trying alternative copy method...
    REM Try PowerShell as fallback
    powershell -Command "Copy-Item -Path '%CURRENT_PATH%*' -Destination '%WORK_DIR%' -Recurse -Force" 2>nul
    if errorlevel 1 (
        echo [ERROR] Alternative copy also failed!
        echo Please copy files manually to %WORK_DIR%
        pause
        exit /b
    )
)

REM Change to working directory
cd /d "%WORK_DIR%"
echo Current Directory: %CD%
goto :CHECK_PYTHON

:LOCAL_MODE
REM === Local Mode: Run from current location ===
cd /d "%~dp0"
if errorlevel 1 (
    echo.
    echo [ERROR] Failed to change directory!
    echo Path: %~dp0
    echo.
    pause
    exit /b
)
echo Current Directory: %CD%

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
echo Checking execution file...
if not exist "run_main_fixed.py" (
    echo.
    echo [ERROR] run_main_fixed.py not found!
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

python run_main_fixed.py

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

REM Cleanup option for WSL mode
if defined WORK_DIR (
    echo.
    echo Clean up temporary folder? (Y/N)
    set /p CLEANUP=Select: 
    if /i "%CLEANUP%"=="Y" (
        cd /d C:\
        rd /s /q "%WORK_DIR%" 2>nul
        echo Temporary folder cleaned.
    )
)

exit /b %EXIT_CODE%