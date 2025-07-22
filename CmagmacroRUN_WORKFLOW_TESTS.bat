@echo off
echo Running Workflow Tests...
echo.

REM Set UTF-8 encoding for proper Korean text display
set PYTHONIOENCODING=utf-8
chcp 65001 > nul

REM Check if virtual environment is active
if "%VIRTUAL_ENV%"=="" (
    echo WARNING: No virtual environment detected\!
    echo It's recommended to run tests in a virtual environment.
    echo.
)

REM Run the workflow tests with UTF-8 support
python -X utf8 run_workflow_tests.py

echo.
echo Test execution completed.
pause
