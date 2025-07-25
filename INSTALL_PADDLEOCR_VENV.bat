@echo off
REM Install PaddleOCR in venv311

echo Installing PaddleOCR in venv311...
echo =====================================

call venv311\Scripts\activate.bat

echo.
echo Python version:
python --version

echo.
echo Installing PaddleOCR dependencies...

REM Upgrade pip first
python -m pip install --upgrade pip

REM Install PaddlePaddle (CPU version)
echo.
echo Installing PaddlePaddle (CPU)...
pip install paddlepaddle>=2.5.0

REM Install PaddleOCR
echo.
echo Installing PaddleOCR...
pip install paddleocr>=2.7.0

REM Additional dependencies
echo.
echo Installing additional dependencies...
pip install opencv-python pillow numpy

echo.
echo Testing PaddleOCR installation...
python -c "from paddleocr import PaddleOCR; print('PaddleOCR imported successfully!')"

echo.
echo Installation complete!
pause