@echo off
echo ====================================
echo Installation Validator
echo ====================================
echo.

REM Activate virtual environment if exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment not found!
    echo.
)

REM Run validator
python validate_installation.py

echo.
pause