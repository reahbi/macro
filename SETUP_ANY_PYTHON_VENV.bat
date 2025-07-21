@echo off
chcp 65001 >nul
cls
echo ========================================
echo Python 호환 가상환경 설정
echo (모든 Python 3.x 버전 지원)
echo ========================================
echo.

REM 프로젝트 디렉토리로 이동
cd /d "%~dp0"

REM Python 확인 - 여러 방법 시도
echo Python 확인 중...
set PYTHON_CMD=
set PYTHON_VERSION=

REM 1. python 명령 확인
python --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python
    for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
    goto python_found
)

REM 2. python3 명령 확인
python3 --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=python3
    for /f "tokens=2" %%i in ('python3 --version 2^>^&1') do set PYTHON_VERSION=%%i
    goto python_found
)

REM 3. py 런처 확인
py --version >nul 2>&1
if not errorlevel 1 (
    set PYTHON_CMD=py
    for /f "tokens=2" %%i in ('py --version 2^>^&1') do set PYTHON_VERSION=%%i
    goto python_found
)

REM Python을 찾을 수 없음
echo [오류] Python을 찾을 수 없습니다!
echo.
echo 해결 방법:
echo 1. Python 3.x를 설치하세요: https://www.python.org/downloads/
echo 2. 설치 시 "Add Python to PATH" 옵션을 체크하세요
echo 3. 설치 후 이 창을 닫고 다시 실행하세요
echo.
pause
exit /b 1

:python_found
echo.
echo Python 찾음: %PYTHON_CMD%
echo 버전: %PYTHON_VERSION%
echo.

REM 버전 확인 (3.x 이상인지)
echo %PYTHON_VERSION% | findstr /R "^3\." >nul
if errorlevel 1 (
    echo [오류] Python 3.x 이상이 필요합니다!
    echo 현재 버전: %PYTHON_VERSION%
    pause
    exit /b 1
)

REM 기존 가상환경 제거
if exist venv_auto (
    echo 기존 가상환경 제거 중...
    rmdir /s /q venv_auto
)

REM 새로운 가상환경 생성
echo.
echo 가상환경 생성 중...
%PYTHON_CMD% -m venv venv_auto
if errorlevel 1 (
    echo [오류] 가상환경 생성 실패!
    echo venv 모듈이 설치되어 있는지 확인하세요.
    pause
    exit /b 1
)

REM 가상환경 활성화
echo.
echo 가상환경 활성화 중...
call venv_auto\Scripts\activate.bat

REM pip 업그레이드
echo.
echo pip 업그레이드 중...
python -m pip install --upgrade pip

REM Python 버전에 따른 패키지 설치
echo.
echo ========================================
echo 호환 패키지 설치 시작
echo ========================================
echo.

REM 캐시 정리
echo 패키지 캐시 정리 중...
pip cache purge

REM 기본 패키지 설치 (모든 버전 호환)
echo.
echo [1/6] GUI 프레임워크 설치 중...
pip install PyQt5>=5.15.0

echo.
echo [2/6] 데이터 처리 라이브러리 설치 중...
pip install pandas openpyxl

echo.
echo [3/6] 자동화 도구 설치 중...
pip install pyautogui pillow pynput

echo.
echo [4/6] 유틸리티 설치 중...
pip install screeninfo mss cryptography chardet psutil

REM Python 버전별 numpy/opencv 설치
echo.
echo [5/6] 이미지 처리 라이브러리 설치 중...
echo Python %PYTHON_VERSION% 감지됨

REM Python 3.13 확인
echo %PYTHON_VERSION% | findstr "3.13" >nul
if not errorlevel 1 (
    echo Python 3.13용 호환 버전 설치...
    pip install numpy==2.3.0
    pip install opencv-python==4.12.0.88
    goto ocr_install
)

REM Python 3.12 확인
echo %PYTHON_VERSION% | findstr "3.12" >nul
if not errorlevel 1 (
    echo Python 3.12용 호환 버전 설치...
    pip install "numpy<2.0"
    pip install opencv-python
    goto ocr_install
)

REM 기타 버전 (3.11 이하)
echo 표준 버전 설치...
pip install numpy opencv-python

:ocr_install
echo.
echo [6/6] EasyOCR 설치 시도 중...
echo (선택사항 - 시간이 걸릴 수 있습니다)

REM EasyOCR 설치 시도
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install easyocr

if errorlevel 1 (
    echo.
    echo [정보] EasyOCR 설치 건너뜀
    echo 텍스트 인식 기능이 제한됩니다.
)

REM 설치 확인
echo.
echo ========================================
echo 설치 확인
echo ========================================
echo.

python -c "import sys; print(f'Python: {sys.version}')"
echo.
python -c "import numpy; print(f'NumPy: {numpy.__version__}')" 2>nul || echo NumPy: 설치 실패
python -c "import cv2; print(f'OpenCV: {cv2.__version__}')" 2>nul || echo OpenCV: 설치 실패
python -c "import PyQt5.QtCore; print(f'PyQt5: {PyQt5.QtCore.QT_VERSION_STR}')" 2>nul || echo PyQt5: 설치 실패
python -c "import pandas; print(f'Pandas: {pandas.__version__}')" 2>nul || echo Pandas: 설치 실패
python -c "import easyocr; print('EasyOCR: 설치됨')" 2>nul || echo EasyOCR: 미설치 (선택사항)

echo.
echo ========================================
echo 설정 완료!
echo ========================================
echo.
echo 실행 방법: RUN_AUTO_VENV.bat
echo.
pause