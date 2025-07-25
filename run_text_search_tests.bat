@echo off
REM Run text search tests in virtual environment

echo =====================================
echo Text Search Test Suite Runner
echo =====================================
echo.

REM Activate virtual environment
if exist venv311\Scripts\activate.bat (
    echo Activating venv311...
    call venv311\Scripts\activate.bat
) else (
    echo ERROR: venv311 not found!
    echo Please run SETUP_VENV311.bat first
    pause
    exit /b 1
)

echo.
echo Installing test dependencies...
python -m pip install pytest pytest-qt pytest-cov --quiet

echo.
echo =====================================
echo Running Unit Tests
echo =====================================
python -m pytest tests\test_text_search_unit.py -v --tb=short

echo.
echo =====================================
echo Running Integration Tests
echo =====================================
python -m pytest tests\test_text_search_integration.py -v --tb=short

echo.
echo =====================================
echo Running E2E Tests
echo =====================================
python -m pytest tests\test_text_search_e2e.py -v --tb=short

echo.
echo =====================================
echo Running All Tests with Coverage
echo =====================================
python -m pytest tests\test_text_search_*.py --cov=src\vision --cov=src\ui\dialogs --cov=src\automation --cov-report=term-missing --cov-report=html

echo.
echo Test execution completed!
echo Coverage report saved to htmlcov\index.html
echo.

pause