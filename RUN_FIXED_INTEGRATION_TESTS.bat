@echo off
REM Run fixed integration tests

echo Running fixed integration tests...
venv311\Scripts\python.exe -m pytest tests\test_text_search_integration_fixed.py -v --tb=short

pause