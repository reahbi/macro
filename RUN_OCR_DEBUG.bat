@echo off
echo === Running OCR Debug Script ===
cd /d "%~dp0"

echo Using Python 3.11 virtual environment...
if exist venv311\Scripts\python.exe (
    echo Found venv311
    venv311\Scripts\python.exe test_ocr_debug.py
) else (
    echo venv311 not found, using direct Python
    python test_ocr_debug.py
)

pause