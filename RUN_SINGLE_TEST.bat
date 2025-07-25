@echo off
REM Run a single test file in venv311

echo Activating venv311...
call venv311\Scripts\activate.bat

echo.
echo Installing pytest...
pip install pytest pytest-mock

echo.
echo Running single test...
python -m pytest tests\test_text_search_unit.py::TestTextResult::test_text_result_creation -v -s

pause