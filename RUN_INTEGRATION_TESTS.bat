@echo off
REM Run integration tests with venv311

echo Running integration tests...
venv311\Scripts\python.exe run_integration_tests.py

pause