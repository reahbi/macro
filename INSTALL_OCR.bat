@echo off
chcp 65001 >nul
cls
echo ========================================
echo EasyOCR 텍스트 인식 기능 설치
echo ========================================
echo.
echo 이 프로그램은 화면에서 텍스트를 찾는 기능을 위해
echo EasyOCR과 필요한 구성요소를 설치합니다.
echo.
echo 설치 내용:
echo - PyTorch (CPU 버전)
echo - EasyOCR
echo - 한국어/영어 인식 모델
echo.
echo 예상 시간: 5-10분 (인터넷 속도에 따라)
echo 필요 공간: 약 1GB
echo.
echo ========================================
echo.

REM 프로젝트 디렉토리로 이동
cd /d "%~dp0"

REM Python 확인
echo Python 확인 중...
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다!
    echo Python을 먼저 설치해주세요.
    pause
    exit /b 1
)

REM 가상환경 확인 및 활성화
if exist venv_auto (
    echo 가상환경 활성화 중...
    call venv_auto\Scripts\activate.bat
) else if exist venv313 (
    echo 가상환경 활성화 중...
    call venv313\Scripts\activate.bat
) else if exist venv (
    echo 가상환경 활성화 중...
    call venv\Scripts\activate.bat
) else (
    echo [경고] 가상환경이 없습니다.
    echo 시스템 Python을 사용합니다.
)

REM pip 업그레이드
echo.
echo pip 업그레이드 중...
python -m pip install --upgrade pip

REM PyTorch CPU 버전 설치
echo.
echo ========================================
echo [1/3] PyTorch CPU 버전 설치 중...
echo ========================================
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

if errorlevel 1 (
    echo [오류] PyTorch 설치 실패!
    echo 인터넷 연결을 확인하세요.
    pause
    exit /b 1
)

REM EasyOCR 설치
echo.
echo ========================================
echo [2/3] EasyOCR 설치 중...
echo ========================================
pip install easyocr

if errorlevel 1 (
    echo [오류] EasyOCR 설치 실패!
    pause
    exit /b 1
)

REM 추가 의존성 설치
echo.
echo ========================================
echo [3/3] 추가 구성요소 설치 중...
echo ========================================
pip install opencv-python-headless pillow scipy

REM 설치 확인
echo.
echo ========================================
echo 설치 확인 중...
echo ========================================
echo.

python -c "import torch; print(f'✓ PyTorch {torch.__version__} 설치됨')"
python -c "import easyocr; print('✓ EasyOCR 설치됨')"
python -c "import cv2; print(f'✓ OpenCV {cv2.__version__} 설치됨')"

REM OCR 테스트
echo.
echo ========================================
echo OCR 기능 테스트 중...
echo ========================================
echo.

python -c "
import easyocr
print('한국어/영어 모델 다운로드 중...')
print('(처음 실행 시 모델 다운로드로 시간이 걸립니다)')
reader = easyocr.Reader(['ko', 'en'], gpu=False)
print('✓ OCR 초기화 성공!')
print('✓ 텍스트 인식 기능 사용 가능!')
"

if errorlevel 1 (
    echo.
    echo [경고] OCR 초기화 중 문제가 발생했습니다.
    echo 프로그램 실행 시 자동으로 재시도됩니다.
) else (
    echo.
    echo ========================================
    echo ✓ EasyOCR 설치 완료!
    echo ========================================
    echo.
    echo 이제 Excel Macro에서 텍스트 찾기 기능을
    echo 사용할 수 있습니다.
)

REM 설치 완료 마커 생성
echo.
echo 설치 정보 저장 중...
mkdir "%USERPROFILE%\.excel_macro\ocr" 2>nul
echo {"status": "installed", "version": "1.0.0"} > "%USERPROFILE%\.excel_macro\ocr\status.json"

echo.
echo 설치가 완료되었습니다!
echo.
pause