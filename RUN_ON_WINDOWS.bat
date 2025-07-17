@echo off
chcp 65001 >nul 2>&1
REM === Simplest Windows Runner for WSL Files ===

cls
echo ===============================
echo Excel Macro Automation Tool
echo ===============================
echo.

REM Enable error handling
setlocal enabledelayedexpansion

REM Create and use C:\macro as working directory
set WORK_DIR=C:\macro
echo Target directory: %WORK_DIR%
echo.

REM Clean existing directory
if exist "%WORK_DIR%" (
    echo Removing old files...
    rmdir /s /q "%WORK_DIR%" 2>nul
    timeout /t 2 /nobreak >nul
)

REM Create fresh directory
mkdir "%WORK_DIR%" 2>nul
if errorlevel 1 (
    echo [ERROR] Cannot create directory %WORK_DIR%
    echo Please check permissions or run as administrator
    echo.
    pause
    exit /b 1
)

REM Detect source path
set "SOURCE_PATH=%~dp0"
echo Source path: %SOURCE_PATH%

REM Check if running from WSL path
echo %SOURCE_PATH% | find "\\wsl" >nul
if %errorlevel%==0 (
    echo Running from WSL path detected
    set "WSL_PATH=\\wsl.localhost\Ubuntu-22.04\home\nosky\macro"
) else (
    echo Running from local path
    set "WSL_PATH=%SOURCE_PATH%"
)

REM Use PowerShell to copy files (handles WSL paths better)
echo.
echo Copying application files...
echo Please wait...
echo.

REM Create a PowerShell script for better error handling
echo $ErrorActionPreference = 'Stop' > "%TEMP%\copy_files.ps1"
echo try { >> "%TEMP%\copy_files.ps1"
echo     $source = '%WSL_PATH%' >> "%TEMP%\copy_files.ps1"
echo     $dest = '%WORK_DIR%' >> "%TEMP%\copy_files.ps1"
echo     Write-Host 'Source: ' $source >> "%TEMP%\copy_files.ps1"
echo     Write-Host 'Destination: ' $dest >> "%TEMP%\copy_files.ps1"
echo     Write-Host '' >> "%TEMP%\copy_files.ps1"
echo     if (-not (Test-Path $source)) { >> "%TEMP%\copy_files.ps1"
echo         throw "Source path not found: $source" >> "%TEMP%\copy_files.ps1"
echo     } >> "%TEMP%\copy_files.ps1"
echo     Write-Host 'Copying Python files...' >> "%TEMP%\copy_files.ps1"
echo     Get-ChildItem -Path "$source\*.py" -ErrorAction SilentlyContinue ^| Copy-Item -Destination $dest -Force >> "%TEMP%\copy_files.ps1"
echo     Get-ChildItem -Path "$source\*.txt" -ErrorAction SilentlyContinue ^| Copy-Item -Destination $dest -Force >> "%TEMP%\copy_files.ps1"
echo     Write-Host 'Copying source code directory...' >> "%TEMP%\copy_files.ps1"
echo     if (Test-Path "$source\src") { >> "%TEMP%\copy_files.ps1"
echo         Copy-Item -Path "$source\src" -Destination $dest -Recurse -Force >> "%TEMP%\copy_files.ps1"
echo     } >> "%TEMP%\copy_files.ps1"
echo     Write-Host 'Copying resources directory...' >> "%TEMP%\copy_files.ps1"
echo     if (Test-Path "$source\resources") { >> "%TEMP%\copy_files.ps1"
echo         Copy-Item -Path "$source\resources" -Destination $dest -Recurse -Force >> "%TEMP%\copy_files.ps1"
echo     } >> "%TEMP%\copy_files.ps1"
echo     Write-Host 'Copy complete!' >> "%TEMP%\copy_files.ps1"
echo } catch { >> "%TEMP%\copy_files.ps1"
echo     Write-Host "ERROR: $_" -ForegroundColor Red >> "%TEMP%\copy_files.ps1"
echo     exit 1 >> "%TEMP%\copy_files.ps1"
echo } >> "%TEMP%\copy_files.ps1"

REM Execute PowerShell script
powershell -ExecutionPolicy Bypass -File "%TEMP%\copy_files.ps1"
if errorlevel 1 (
    echo.
    echo [ERROR] PowerShell copy failed!
    echo Trying alternative copy method...
    echo.
    
    REM Try direct copy as fallback
    xcopy "%SOURCE_PATH%*.py" "%WORK_DIR%\" /Y >nul 2>&1
    xcopy "%SOURCE_PATH%*.txt" "%WORK_DIR%\" /Y >nul 2>&1
    xcopy "%SOURCE_PATH%src" "%WORK_DIR%\src\" /E /I /Y >nul 2>&1
    xcopy "%SOURCE_PATH%resources" "%WORK_DIR%\resources\" /E /I /Y >nul 2>&1
)

REM Clean up temp PowerShell script
del "%TEMP%\copy_files.ps1" 2>nul

REM Move to working directory
cd /d %WORK_DIR%
echo.
echo Current directory: %CD%

REM Check if copy was successful
if not exist "run_main_fixed.py" (
    echo.
    echo [ERROR] Essential files not found!
    echo.
    echo Checking what was copied:
    dir /b
    echo.
    echo Please ensure the source directory contains:
    echo - run_main_fixed.py
    echo - src\ directory
    echo - resources\ directory
    echo.
    pause
    exit /b 1
)

REM Check Python
echo.
echo Checking Python installation...
python --version 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] Python not found!
    echo.
    echo Please install Python from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

python --version
echo.

REM Install packages if needed
echo Checking and installing required packages...
echo This may take a few minutes on first run...
echo.

REM Upgrade pip first
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install all packages at once for simplicity
echo Installing required packages...
echo - PyQt5 (GUI framework)
echo - pandas, openpyxl (Excel processing)  
echo - pyautogui (automation)
echo - easyocr (text recognition)
echo.

pip install PyQt5 pandas openpyxl pyautogui pillow opencv-python numpy mss screeninfo easyocr cryptography

if errorlevel 1 (
    echo.
    echo [WARNING] Some packages may have failed to install
    echo Continuing anyway...
    echo.
)

REM Run the application
echo.
echo ===============================
echo Starting application...
echo ===============================
echo.

REM Check if we can import basic modules
echo Testing Python environment...
python -c "import sys; print(f'Python path: {sys.executable}')" 2>&1
if errorlevel 1 (
    echo [ERROR] Python environment issue detected
    pause
    exit /b 1
)

echo Running application...
echo.

REM Run with explicit error output
python run_main_fixed.py 2>&1

set EXIT_CODE=%errorlevel%

echo.
echo ===============================
if %EXIT_CODE%==0 (
    echo Application closed successfully
) else (
    echo Application exited with error: %EXIT_CODE%
    echo.
    echo Common issues:
    echo - Missing packages: Run 'pip install -r requirements.txt'
    echo - Import errors: Check if all source files were copied
    echo - Permission issues: Try running as administrator
)
echo ===============================

echo.
echo Press any key to exit...
pause >nul

endlocal
exit /b %EXIT_CODE%