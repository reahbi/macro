@echo off
cd /d "%~dp0"

if exist venv_auto (
    call venv_auto\Scripts\activate.bat
) else if exist venv313 (
    call venv313\Scripts\activate.bat
) else (
    echo No virtual environment found!
    exit /b 1
)

echo Running single test...
python -m pytest tests/e2e/test_healthcare_workflows.py::TestHealthcareCheckupWorkflow::test_checkup_workflow_execution -v -s

pause