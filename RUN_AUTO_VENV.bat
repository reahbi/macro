@echo off
chcp 65001 >nul
cls
echo ========================================
echo Excel Macro Automation 실행
echo ========================================
echo.

REM 프로젝트 디렉토리로 이동
cd /d "%~dp0"

REM 가상환경 확인
if not exist venv_auto (
    echo [알림] 가상환경이 없습니다.
    echo.
    echo 자동 설정을 시작합니다...
    echo.
    call SETUP_ANY_PYTHON_VENV.bat
    
    if errorlevel 1 (
        echo [오류] 환경 설정 실패!
        pause
        exit /b 1
    )
    cls
    echo ========================================
    echo Excel Macro Automation 실행
    echo ========================================
    echo.
)

REM 가상환경 활성화
echo 가상환경 활성화 중...
call venv_auto\Scripts\activate.bat

REM Python 버전 표시
echo.
python --version

REM 빠른 호환성 검사
echo.
echo 모듈 확인 중...
python -c "import PyQt5; print('✓ GUI 모듈 정상')" 2>nul || goto module_error
python -c "import pandas; print('✓ Excel 처리 모듈 정상')" 2>nul || goto module_error
python -c "import pyautogui; print('✓ 자동화 모듈 정상')" 2>nul || goto module_error

REM numpy/opencv는 선택사항으로 처리
python -c "import numpy, cv2; print('✓ 이미지 처리 모듈 정상')" 2>nul || echo ✗ 이미지 처리 모듈 제한 (일부 기능 제한)

REM EasyOCR 확인
python -c "import easyocr; print('✓ OCR 모듈 정상')" 2>nul || echo ✗ OCR 모듈 없음 (텍스트 인식 불가)

REM 프로그램 실행
echo.
echo ========================================
echo 프로그램 시작...
echo ========================================
echo.

python run_main.py

if errorlevel 1 (
    echo.
    echo [오류] 프로그램 실행 중 문제가 발생했습니다.
    echo.
    echo 오류 해결 방법:
    echo 1. 위의 오류 메시지를 확인하세요
    echo 2. SETUP_ANY_PYTHON_VENV.bat을 다시 실행하세요
    echo 3. logs 폴더의 로그 파일을 확인하세요
) else (
    echo.
    echo 프로그램이 정상 종료되었습니다.
)
goto end

:module_error
echo.
echo [오류] 필수 모듈이 설치되지 않았습니다!
echo.
echo SETUP_ANY_PYTHON_VENV.bat을 실행하여
echo 환경을 다시 설정해주세요.

:end
echo.
pause