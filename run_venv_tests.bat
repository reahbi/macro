@echo off
echo Running tests in venv311...
cd /d C:\mag\macro
call venv311\Scripts\activate.bat
python check_paddle_test.py
echo.
echo Running pytest tests...
python -m pytest tests\test_text_search_unit.py -v
python -m pytest tests\test_text_search_integration_fixed.py -v  
python -m pytest tests\test_text_search_e2e.py -v
pause