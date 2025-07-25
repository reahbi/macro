@echo off
echo Running PaddleOCR Tests...
echo ====================================

call venv311\Scripts\activate.bat

echo.
echo Checking PaddleOCR installation...
python -c "from paddleocr import PaddleOCR; print('PaddleOCR is installed successfully!')"

echo.
echo ====================================
echo Running Unit Tests
echo ====================================
python -m pytest tests\test_text_search_unit.py -v

echo.
echo ====================================
echo Running Integration Tests (Fixed)
echo ====================================
python -m pytest tests\test_text_search_integration_fixed.py -v

echo.
echo ====================================
echo Running E2E Tests
echo ====================================
python -m pytest tests\test_text_search_e2e.py -v

echo.
echo ====================================
echo SUMMARY
echo ====================================
python -m pytest tests\test_text_search_unit.py tests\test_text_search_integration_fixed.py tests\test_text_search_e2e.py -q

pause