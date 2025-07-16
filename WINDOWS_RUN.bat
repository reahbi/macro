@echo off
REM === Windows 실행 스크립트 ===

cls

echo ===============================
echo Excel Macro Automation Tool
echo ===============================
echo.

REM 현재 디렉토리로 이동
cd /d "%~dp0"
echo 작업 폴더: %CD%

REM Python 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo [오류] Python이 설치되지 않았습니다!
    echo.
    echo 1. https://python.org 에서 Python 다운로드
    echo 2. 설치 시 "Add Python to PATH" 체크
    echo.
    pause
    exit /b
)

echo Python 확인 완료
echo.

REM 필수 패키지 설치
echo 패키지 설치 중... (첫 실행 시 시간이 걸릴 수 있습니다)
echo.
echo 주요 패키지:
echo - PyQt5 (GUI 프레임워크)
echo - pandas, openpyxl (Excel 처리)
echo - pyautogui, opencv-python (화면 자동화)
echo - easyocr (텍스트 인식) - 설치에 시간이 걸릴 수 있습니다
echo.

python -m pip install --upgrade pip
pip install PyQt5 pandas openpyxl pyautogui pillow screeninfo cryptography opencv-python numpy mss

echo.
echo EasyOCR 설치 중... (첫 실행 시 모델 다운로드로 시간이 걸립니다)
pip install easyocr

if errorlevel 1 (
    echo.
    echo [경고] 일부 패키지 설치 실패. 수동 설치가 필요할 수 있습니다.
    echo.
)

REM 실행
echo.
echo 애플리케이션 시작 중...
echo ===============================
echo.

REM 파일 존재 확인
if not exist "run_main_fixed.py" (
    echo.
    echo [오류] run_main_fixed.py 파일을 찾을 수 없습니다!
    echo 현재 디렉토리: %CD%
    echo.
    pause
    exit /b
)

python run_main_fixed.py

REM 종료 시 일시정지 (오류 발생 여부와 관계없이)
if errorlevel 1 (
    echo.
    echo [오류] 프로그램 실행 중 오류가 발생했습니다.
    echo.
)

echo.
echo === 프로그램 종료 ===
echo 아무 키나 누르면 창이 닫힙니다...
pause >nul