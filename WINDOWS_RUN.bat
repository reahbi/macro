@echo off
REM === Windows 실행 스크립트 (WSL 및 로컬 경로 지원) ===

cls

echo ===============================
echo Excel Macro Automation Tool
echo ===============================
echo.

REM 현재 경로 확인
set "CURRENT_PATH=%~dp0"
echo 실행 경로: %CURRENT_PATH%

REM WSL 경로인지 확인 (\\wsl 포함 여부)
echo %CURRENT_PATH% | find "\\wsl" >nul
if %errorlevel%==0 (
    echo WSL 경로 감지됨. 로컬로 복사하여 실행합니다...
    goto :WSL_MODE
) else (
    echo 로컬 경로에서 실행합니다...
    goto :LOCAL_MODE
)

:WSL_MODE
REM === WSL 모드: 임시 폴더로 복사 후 실행 ===
set WORK_DIR=C:\temp\excel_macro
echo 작업 폴더: %WORK_DIR%

REM 기존 폴더 삭제
if exist "%WORK_DIR%" (
    echo 기존 폴더 정리 중...
    rd /s /q "%WORK_DIR%" 2>nul
    timeout /t 1 /nobreak >nul
)

REM 새 폴더 생성
mkdir "%WORK_DIR%" 2>nul
if errorlevel 1 (
    echo.
    echo [오류] 작업 폴더를 생성할 수 없습니다!
    echo 관리자 권한이 필요할 수 있습니다.
    echo.
    pause
    exit /b
)

REM 파일 복사
echo 파일 복사 중...
xcopy "%CURRENT_PATH%*" "%WORK_DIR%\" /E /I /Q /Y >nul 2>&1
if errorlevel 1 (
    echo.
    echo [오류] 파일 복사 실패!
    echo 원본 경로: %CURRENT_PATH%
    echo 대상 경로: %WORK_DIR%
    echo.
    pause
    exit /b
)

REM 작업 디렉토리로 이동
cd /d "%WORK_DIR%"
echo 현재 디렉토리: %CD%
goto :CHECK_PYTHON

:LOCAL_MODE
REM === 로컬 모드: 현재 위치에서 실행 ===
cd /d "%~dp0"
if errorlevel 1 (
    echo.
    echo [오류] 디렉토리 변경 실패!
    echo 경로: %~dp0
    echo.
    pause
    exit /b
)
echo 현재 디렉토리: %CD%

:CHECK_PYTHON
REM Python 확인
echo.
echo Python 확인 중...
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

python --version
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

REM pip 업그레이드
python -m pip install --upgrade pip >nul 2>&1

REM 기본 패키지 설치
echo 기본 패키지 설치 중...
pip install PyQt5 pandas openpyxl pyautogui pillow screeninfo cryptography opencv-python numpy mss --quiet --no-warn-script-location

REM EasyOCR 설치 (별도로 처리)
echo.
echo EasyOCR 설치 중... (첫 실행 시 모델 다운로드로 시간이 걸립니다)
pip install easyocr --quiet --no-warn-script-location

if errorlevel 1 (
    echo.
    echo [경고] 일부 패키지 설치 실패. 수동 설치가 필요할 수 있습니다.
    echo.
)

REM 파일 존재 확인
echo.
echo 실행 파일 확인 중...
if not exist "run_main_fixed.py" (
    echo.
    echo [오류] run_main_fixed.py 파일을 찾을 수 없습니다!
    echo 현재 디렉토리: %CD%
    echo.
    echo 디렉토리 내용:
    dir *.py
    echo.
    pause
    exit /b
)

REM 실행
echo.
echo ===============================
echo 애플리케이션 시작 중...
echo ===============================
echo.

python run_main_fixed.py

REM 실행 결과 확인
set EXIT_CODE=%errorlevel%

REM 종료 처리
echo.
if %EXIT_CODE% neq 0 (
    echo ===============================
    echo [오류] 프로그램 실행 중 오류가 발생했습니다.
    echo 오류 코드: %EXIT_CODE%
    echo ===============================
) else (
    echo ===============================
    echo 프로그램이 정상적으로 종료되었습니다.
    echo ===============================
)

echo.
echo 아무 키나 누르면 창이 닫힙니다...
pause >nul

REM WSL 모드인 경우 임시 폴더 정리 옵션
if defined WORK_DIR (
    echo.
    echo 임시 폴더를 정리하시겠습니까? (Y/N)
    set /p CLEANUP=선택: 
    if /i "%CLEANUP%"=="Y" (
        cd /d C:\
        rd /s /q "%WORK_DIR%" 2>nul
        echo 임시 폴더가 정리되었습니다.
    )
)

exit /b %EXIT_CODE%