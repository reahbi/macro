@echo off
REM Auto-detect and run with available virtual environment

echo Excel Macro Automation - Auto Virtual Environment Runner
echo ========================================================
echo.

REM Try venv313 first (Python 3.13)
if exist venv313\Scripts\activate.bat (
    echo Found venv313 virtual environment
    call venv313\Scripts\activate.bat
    goto run_app
)

REM Try venv_auto
if exist venv_auto\Scripts\activate.bat (
    echo Found venv_auto virtual environment
    call venv_auto\Scripts\activate.bat
    goto run_app
)

REM Try generic venv
if exist venv\Scripts\activate.bat (
    echo Found venv virtual environment
    call venv\Scripts\activate.bat
    goto run_app
)

REM No virtual environment found
echo ERROR: No virtual environment found!
echo.
echo Please run one of the following:
echo   - SETUP_VENV313.bat (for Python 3.13)
echo   - SETUP_CLEAN.bat (for clean setup)
echo   - INSTALL_DEPENDENCIES.bat (to install in current environment)
echo.
pause
exit /b 1

:run_app
echo.
echo Starting Excel Macro Automation...
echo.
python run_main.py

REM Check if the app exited with error
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)

REM Deactivate virtual environment
deactivate

pause