@echo off
echo Running PaddleOCR tests...
venv311\Scripts\python.exe test_with_paddleocr.py > paddleocr_test_output.txt 2>&1
type paddleocr_test_output.txt
pause