@echo off
echo ====================================
echo Macro Fixer for Windows
echo ====================================
echo.

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found!
    echo.
)

REM Install chardet if not installed
echo Checking for required packages...
pip show chardet >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing chardet for encoding detection...
    pip install chardet
)

REM Run the fixer
echo.
echo Running macro fixer...
python fix_windows_macro.py %*

echo.
echo ====================================
echo Macro fixing completed!
echo ====================================
pause