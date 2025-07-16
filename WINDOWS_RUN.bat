@echo off
REM === 가장 간단한 Windows 실행 스크립트 ===
REM 임시 폴더에 복사하여 UNC 경로 문제 해결

cls

echo ===============================
echo Excel Macro Automation Tool
echo ===============================
echo.

REM 로컬 임시 폴더 생성
set WORK_DIR=C:\temp\excel_macro
echo 작업 폴더: %WORK_DIR%

REM 기존 폴더 삭제
if exist "%WORK_DIR%" (
    echo 기존 폴더 정리 중...
    rd /s /q "%WORK_DIR%" 2>nul
)

REM 새 폴더 생성
mkdir "%WORK_DIR%"

REM 파일 복사
echo 파일 복사 중...
xcopy "%~dp0*" "%WORK_DIR%\" /E /I /Q /Y >nul

REM 작업 디렉토리로 이동
cd /d "%WORK_DIR%"

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

python run_main_fixed.py

REM 종료 시 일시정지 (오류 발생 여부와 관계없이)
echo.
echo === 프로그램 종료 ===
pause