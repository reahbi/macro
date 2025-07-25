@echo off
REM Run all tests with PaddleOCR installed

echo Running all text search tests with PaddleOCR...
echo ================================================

call venv311\Scripts\activate.bat

echo.
echo Verifying PaddleOCR installation...
python -c "from paddleocr import PaddleOCR; print('PaddleOCR version:', PaddleOCR.__module__)"

echo.
echo =====================================
echo 1. Running Unit Tests
echo =====================================
python -m pytest tests\test_text_search_unit.py -v --tb=short

echo.
echo =====================================
echo 2. Running Integration Tests (Fixed)
echo =====================================
python -m pytest tests\test_text_search_integration_fixed.py -v --tb=short

echo.
echo =====================================
echo 3. Running E2E Tests
echo =====================================
python -m pytest tests\test_text_search_e2e.py -v --tb=short

echo.
echo =====================================
echo Test Summary
echo =====================================
python -m pytest tests\test_text_search_*.py tests\test_text_search_integration_fixed.py --tb=no -q

pause