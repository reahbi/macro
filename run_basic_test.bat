@echo off
cd /d "%~dp0"

echo Activating virtual environment...
if exist venv_auto (
    call venv_auto\Scripts\activate.bat
) else if exist venv313 (
    call venv313\Scripts\activate.bat
)

echo.
echo Running basic workflow test...
python -m pytest tests/test_workflow_basic.py -v

pause