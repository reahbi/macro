@echo off
REM Install pyperclip in all virtual environments

echo Installing pyperclip in all virtual environments...
echo ====================================================
echo.

REM Check venv311
if exist venv311\Scripts\activate.bat (
    echo Installing in venv311...
    call venv311\Scripts\activate.bat
    pip install pyperclip
    deactivate
    echo Done!
    echo.
)

REM Check venv_auto
if exist venv_auto\Scripts\activate.bat (
    echo Installing in venv_auto...
    call venv_auto\Scripts\activate.bat
    pip install pyperclip
    deactivate
    echo Done!
    echo.
)

REM Check venv
if exist venv\Scripts\activate.bat (
    echo Installing in venv...
    call venv\Scripts\activate.bat
    pip install pyperclip
    deactivate
    echo Done!
    echo.
)

REM Also try to install in system Python if no venv found
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo No Python installation found in PATH
) else (
    echo Installing in system Python...
    python -m pip install pyperclip
    echo Done!
)

echo.
echo pyperclip installation complete!
pause