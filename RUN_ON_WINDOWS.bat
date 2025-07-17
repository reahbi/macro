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

REM Check each package individually
python -c "import PyQt5" 2>nul || (
    echo Installing PyQt5...
    pip install PyQt5 --quiet --no-warn-script-location
)

python -c "import pandas" 2>nul || (
    echo Installing pandas and openpyxl...
    pip install pandas openpyxl --quiet --no-warn-script-location
)

python -c "import pyautogui" 2>nul || (
    echo Installing automation packages...
    pip install pyautogui pillow opencv-python numpy mss screeninfo --quiet --no-warn-script-location
)

python -c "import easyocr" 2>nul || (
    echo Installing EasyOCR (this may take a while)...
    pip install easyocr --quiet --no-warn-script-location
)

python -c "import cryptography" 2>nul || (
    echo Installing cryptography...
    pip install cryptography --quiet --no-warn-script-location
)

REM Run the application
echo.
echo ===============================
echo Starting application...
echo ===============================
echo.

python run_main_fixed.py

set EXIT_CODE=%errorlevel%

echo.
if %EXIT_CODE%==0 (
    echo ===============================
    echo Application closed successfully
    echo ===============================
) else (
    echo ===============================
    echo Application exited with error: %EXIT_CODE%
    echo ===============================
)

echo.
echo Press any key to exit...
pause >nul

endlocal
exit /b %EXIT_CODE%