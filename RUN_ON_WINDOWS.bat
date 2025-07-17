@echo off
REM === Simplest Windows Runner for WSL Files ===

cls
echo ===============================
echo Excel Macro Automation Tool
echo ===============================
echo.

REM Create and use C:\macro as working directory
set WORK_DIR=C:\macro
echo Target directory: %WORK_DIR%
echo.

REM Clean existing directory
if exist "%WORK_DIR%" (
    echo Removing old files...
    rmdir /s /q "%WORK_DIR%" 2>nul
)

REM Create fresh directory
mkdir "%WORK_DIR%"

REM Use PowerShell to copy files (handles WSL paths better)
echo Copying application files...
echo Please wait...
echo.

powershell -Command "& {
    $source = '\\wsl.localhost\Ubuntu-22.04\home\nosky\macro'
    $dest = 'C:\macro'
    
    Write-Host 'Copying main files...'
    Copy-Item -Path $source\*.py -Destination $dest -Force
    Copy-Item -Path $source\*.txt -Destination $dest -Force
    
    Write-Host 'Copying source code...'
    Copy-Item -Path $source\src -Destination $dest -Recurse -Force
    
    Write-Host 'Copying resources...'
    if (Test-Path $source\resources) {
        Copy-Item -Path $source\resources -Destination $dest -Recurse -Force
    }
    
    Write-Host 'Copy complete!'
}"

REM Move to working directory
cd /d %WORK_DIR%

REM Check if copy was successful
if not exist "run_main_fixed.py" (
    echo.
    echo [ERROR] File copy failed!
    echo Please manually copy the project files to %WORK_DIR%
    echo.
    pause
    exit /b
)

REM Check Python
echo.
echo Checking Python installation...
python --version 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] Python not found!
    echo Please install Python from python.org
    echo.
    pause
    exit /b
)

REM Install packages if needed
echo.
echo Ensuring packages are installed...
pip install PyQt5 pandas openpyxl pyautogui pillow opencv-python numpy mss screeninfo easyocr cryptography --quiet

REM Run the application
echo.
echo ===============================
echo Starting application...
echo ===============================
echo.

python run_main_fixed.py

echo.
echo ===============================
echo Press any key to exit
echo ===============================
pause >nul