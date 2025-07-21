@echo off
chcp 65001 >nul
cls
echo ========================================
echo Python 3.13 호환 가상환경 설정
echo ========================================
echo.

REM 프로젝트 디렉토리로 이동
cd /d "%~dp0"

REM Python 확인
echo Python 버전 확인 중...

REM 먼저 python 명령이 있는지 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다!
    echo.
    echo Python을 먼저 설치해주세요:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Python 버전 표시
echo.
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo 현재 Python 버전: %PYTHON_VERSION%

REM Python 3.13 확인 (선택사항)
echo %PYTHON_VERSION% | findstr "3.13" >nul
if errorlevel 1 (
    echo.
    echo [주의] Python 3.13이 아닙니다.
    echo 최적의 호환성을 위해 Python 3.13을 권장합니다.
    echo.
    echo 현재 버전으로 계속하시겠습니까? (Y/N)
    choice /C YN /N
    if errorlevel 2 exit /b 0
)

REM 기존 가상환경 제거
if exist venv313 (
    echo.
    echo 기존 가상환경 제거 중...
    rmdir /s /q venv313
)

REM 새로운 가상환경 생성
echo.
echo Python 3.13 가상환경 생성 중...
python -m venv venv313
if errorlevel 1 (
    echo [오류] 가상환경 생성 실패!
    pause
    exit /b 1
)

REM 가상환경 활성화
echo.
echo 가상환경 활성화 중...
call venv313\Scripts\activate.bat

REM pip 업그레이드
echo.
echo pip 업그레이드 중...
python -m pip install --upgrade pip

REM 호환 패키지 설치
echo.
echo ========================================
echo Python 3.13 호환 패키지 설치
echo ========================================
echo.

REM 캐시 정리 (이전 버전 충돌 방지)
echo 패키지 캐시 정리 중...
pip cache purge

REM numpy와 opencv 이전 버전 제거
pip uninstall -y numpy opencv-python opencv-python-headless 2>nul

REM 핵심 패키지 개별 설치
echo.
echo [1/7] GUI 프레임워크 설치 중...
pip install PyQt5>=5.15.0

echo.
echo [2/7] 데이터 처리 라이브러리 설치 중...
pip install pandas>=2.0.0 openpyxl>=3.0.0

echo.
echo [3/7] NumPy 2.3.0 설치 중 (Python 3.13 호환)...
pip install numpy==2.3.0

echo.
echo [4/7] OpenCV 4.12.0.88 설치 중 (NumPy 2.x 호환)...
pip install opencv-python==4.12.0.88

echo.
echo [5/7] 자동화 도구 설치 중...
pip install pyautogui>=0.9.53 pillow>=10.0.0 pynput>=1.7.0

echo.
echo [6/7] 추가 유틸리티 설치 중...
pip install screeninfo>=0.8.0 mss>=9.0.0 cryptography>=41.0.0 chardet>=5.0.0 psutil>=5.9.0

echo.
echo [7/7] EasyOCR 설치 시도 중...
echo (설치에 시간이 걸릴 수 있습니다)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install easyocr>=1.7.0

if errorlevel 1 (
    echo.
    echo [경고] EasyOCR 설치 실패. 텍스트 인식 기능이 제한됩니다.
    echo 기본 기능은 정상 작동합니다.
) else (
    echo.
    echo [성공] EasyOCR 설치 완료!
)

REM 설치 확인
echo.
echo ========================================
echo 설치된 패키지 확인
echo ========================================
echo.

python -c "import numpy; print(f'NumPy: {numpy.__version__}')"
python -c "import cv2; print(f'OpenCV: {cv2.__version__}')"
python -c "import PyQt5.QtCore; print(f'PyQt5: {PyQt5.QtCore.QT_VERSION_STR}')"
python -c "import pandas; print(f'Pandas: {pandas.__version__}')"

echo.
python -c "import easyocr; print('EasyOCR: 설치됨')" 2>nul
if errorlevel 1 (
    echo EasyOCR: 설치되지 않음 (텍스트 인식 기능 제한)
)

echo.
echo ========================================
echo 설정 완료!
echo ========================================
echo.
echo 프로그램 실행: RUN_PY313.bat
echo.
pause