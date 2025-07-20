@echo off
REM Excel Macro Automation - Test Execution Pipeline
REM =============================================

echo.
echo Excel Macro Automation - Comprehensive Test Suite
echo =================================================
echo.

REM Set environment variables
set PYTHONPATH=%cd%\src;%PYTHONPATH%
set PYTEST_ARGS=-v --tb=short --disable-warnings

REM Create test results directory
if not exist "test_results" mkdir test_results

echo [Phase 1/4] Running Unit Tests...
echo ---------------------------------
pytest tests\unit %PYTEST_ARGS% --maxfail=5 --html=test_results\unit_tests.html --self-contained-html
if %ERRORLEVEL% NEQ 0 (
    echo Unit tests failed! Check test_results\unit_tests.html for details.
    goto :end
)

echo.
echo [Phase 2/4] Running Integration Tests...
echo ----------------------------------------
pytest tests\integration %PYTEST_ARGS% --maxfail=3 --html=test_results\integration_tests.html --self-contained-html
if %ERRORLEVEL% NEQ 0 (
    echo Integration tests failed! Check test_results\integration_tests.html for details.
    goto :end
)

echo.
echo [Phase 3/4] Running E2E Tests...
echo --------------------------------
pytest tests\e2e %PYTEST_ARGS% --maxfail=2 --html=test_results\e2e_tests.html --self-contained-html
if %ERRORLEVEL% NEQ 0 (
    echo E2E tests failed! Check test_results\e2e_tests.html for details.
    goto :end
)

echo.
echo [Phase 4/4] Generating Coverage Report...
echo -----------------------------------------
pytest --cov=src --cov-report=html:test_results\coverage --cov-report=term %PYTEST_ARGS%

echo.
echo ==========================================
echo Test execution completed successfully!
echo ==========================================
echo.
echo Reports available in test_results\:
echo - unit_tests.html
echo - integration_tests.html
echo - e2e_tests.html
echo - coverage\index.html
echo.

:end
pause