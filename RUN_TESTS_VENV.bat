@echo off
REM Run tests in venv311

echo Activating venv311...
call venv311\Scripts\activate.bat

echo.
echo Python version:
python --version

echo.
echo Installing test dependencies...
pip install pytest pytest-qt pytest-mock pytest-cov

echo.
echo =====================================
echo Running Unit Tests
echo =====================================
python -m pytest tests\test_text_search_unit.py -v -x --tb=short

if errorlevel 1 (
    echo Unit tests failed!
    pause
    exit /b 1
)

echo.
echo =====================================
echo Running Integration Tests
echo =====================================
python -m pytest tests\test_text_search_integration.py -v -x --tb=short

if errorlevel 1 (
    echo Integration tests failed!
    pause
    exit /b 1
)

echo.
echo =====================================
echo Running E2E Tests
echo =====================================
python -m pytest tests\test_text_search_e2e.py -v -x --tb=short

if errorlevel 1 (
    echo E2E tests failed!
    pause
    exit /b 1
)

echo.
echo All tests passed!
pause