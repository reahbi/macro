@echo off
chcp 65001 >nul
cls
echo ========================================
echo Excel Macro Automation 실행
echo (Python 3.13 호환 환경)
echo ========================================
echo.

REM 프로젝트 디렉토리로 이동
cd /d "%~dp0"

REM 가상환경 확인
if not exist venv313 (
    echo [알림] Python 3.13 가상환경이 없습니다.
    echo.
    echo 환경 설정을 시작하시겠습니까? (Y/N)
    choice /C YN /N
    if errorlevel 2 (
        echo 실행을 취소합니다.
        pause
        exit /b 0
    )
    
    echo.
    echo SETUP_PY313_VENV.bat 실행 중...
    call SETUP_PY313_VENV.bat
    
    if errorlevel 1 (
        echo [오류] 환경 설정 실패!
        pause
        exit /b 1
    )
    cls
    echo ========================================
    echo Excel Macro Automation 실행
    echo (Python 3.13 호환 환경)
    echo ========================================
    echo.
)

REM 가상환경 활성화
echo 가상환경 활성화 중...
call venv313\Scripts\activate.bat

REM Python 버전 확인
echo.
echo 실행 환경:
python --version
echo.

REM 호환성 빠른 검사
echo 호환성 검사 중...
python -c "import numpy; import cv2; print(f'[OK] NumPy {numpy.__version__}')" 2>nul
if errorlevel 1 (
    echo [경고] NumPy/OpenCV 호환성 문제 감지
    echo.
    echo 환경을 재설정하시겠습니까? (Y/N)
    choice /C YN /N
    if errorlevel 2 goto skip_reinstall
    
    echo.
    echo 패키지 재설치 중...
    pip uninstall -y numpy opencv-python opencv-python-headless
    pip install numpy==2.3.0
    pip install opencv-python==4.12.0.88
)
:skip_reinstall

python -c "import PyQt5" 2>nul
if errorlevel 1 (
    echo [오류] PyQt5가 설치되지 않았습니다!
    echo 환경 설정을 다시 실행해주세요.
    pause
    exit /b 1
)

REM EasyOCR 확인 (선택사항)
python -c "import easyocr" 2>nul
if errorlevel 1 (
    echo [X] EasyOCR 없음 (텍스트 인식 기능 제한)
) else (
    echo [OK] EasyOCR 사용 가능
)

REM 프로그램 실행
echo.
echo ========================================
echo 프로그램 시작...
echo ========================================
echo.

python run_main.py

REM 실행 결과 처리
if errorlevel 1 (
    echo.
    echo ========================================
    echo [오류] 프로그램 실행 중 문제 발생
    echo ========================================
    echo.
    echo 가능한 해결 방법:
    echo 1. SETUP_PY313_VENV.bat 재실행
    echo 2. 오류 메시지 확인
    echo 3. logs 폴더의 로그 파일 확인
    echo.
) else (
    echo.
    echo 프로그램이 정상 종료되었습니다.
)

pause