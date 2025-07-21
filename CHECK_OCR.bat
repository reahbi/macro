@echo off
chcp 65001 >nul
cls
echo ========================================
echo EasyOCR 설치 상태 확인
echo ========================================
echo.

REM Python 버전 확인
echo Python 버전:
python --version

REM 가상환경 확인
echo.
echo 가상환경 확인:
if exist venv_auto (
    echo ✓ venv_auto 발견
    call venv_auto\Scripts\activate.bat
) else if exist venv313 (
    echo ✓ venv313 발견
    call venv313\Scripts\activate.bat
) else if exist venv (
    echo ✓ venv 발견
    call venv\Scripts\activate.bat
) else (
    echo ✗ 가상환경 없음
)

REM 패키지 확인
echo.
echo ========================================
echo 설치된 패키지 확인:
echo ========================================
echo.

echo PyTorch 확인...
python -c "import torch; print(f'✓ PyTorch {torch.__version__} 설치됨')" 2>nul || echo ✗ PyTorch 미설치

echo.
echo EasyOCR 확인...
python -c "import easyocr; print('✓ EasyOCR 설치됨')" 2>nul || echo ✗ EasyOCR 미설치

echo.
echo OpenCV 확인...
python -c "import cv2; print(f'✓ OpenCV {cv2.__version__} 설치됨')" 2>nul || echo ✗ OpenCV 미설치

REM OCR 상태 파일 확인
echo.
echo ========================================
echo OCR 상태 파일 확인:
echo ========================================
if exist "%USERPROFILE%\.excel_macro\ocr\status.json" (
    echo ✓ OCR 상태 파일 존재
    type "%USERPROFILE%\.excel_macro\ocr\status.json"
) else (
    echo ✗ OCR 상태 파일 없음
)

echo.
echo ========================================
echo 권장 사항:
echo ========================================
echo.
echo OCR이 설치되지 않은 경우:
echo 1. INSTALL_OCR.bat 실행
echo 2. 또는 프로그램 실행 시 자동 설치
echo.
pause