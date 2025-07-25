@echo off
REM Check imports in venv311

echo Activating venv311...
call venv311\Scripts\activate.bat

echo.
echo Checking imports...
python -c "import sys; print(f'Python: {sys.version}')"
python -c "import sys; print(f'Executable: {sys.executable}')"

echo.
echo Testing basic imports...
python -c "from vision.text_extractor_paddle import PaddleTextExtractor, TextResult; print('✓ PaddleTextExtractor imported')"
python -c "from core.macro_types import TextSearchStep; print('✓ TextSearchStep imported')"
python -c "from automation.executor import StepExecutor; print('✓ StepExecutor imported')"

echo.
pause