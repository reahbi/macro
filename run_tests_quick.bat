@echo off
REM Quick test runner for development
REM =================================

echo Running quick test suite...
echo.

set PYTHONPATH=%cd%\src;%PYTHONPATH%

REM Run only E2E tests (most stable)
echo [E2E Tests]
pytest tests\e2e -v --tb=short --disable-warnings
echo.

REM Quick summary
echo Test run completed!
pause