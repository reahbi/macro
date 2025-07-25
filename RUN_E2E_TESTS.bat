@echo off
REM Run E2E tests

echo Running E2E tests...
venv311\Scripts\python.exe -m pytest tests\test_text_search_e2e.py -v --tb=short -k "test_save_load_complex_macro"

pause