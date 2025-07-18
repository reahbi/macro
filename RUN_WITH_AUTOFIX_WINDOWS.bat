@echo off
chcp 65001 >nul 2>&1
title Excel Macro Automation - 자동 오류 복구 모드
color 0A

cls
echo ============================================================
echo Excel Macro Automation - 자동 오류 복구 모드
echo ============================================================
echo.
echo 이 실행기는 다음 기능을 제공합니다:
echo - 시스템 자가 진단
echo - 오류 자동 감지 및 복구
echo - 환경 설정 자동 수정
echo.

REM Enable error handling
setlocal enabledelayedexpansion

REM Create and use C:\macro as working directory
set WORK_DIR=C:\macro
echo 작업 디렉토리: %WORK_DIR%
echo.

REM Clean existing directory
if exist "%WORK_DIR%" (
    echo 기존 파일 정리 중...
    rmdir /s /q "%WORK_DIR%" 2>nul
    timeout /t 2 /nobreak >nul
)

REM Create fresh directory
mkdir "%WORK_DIR%" 2>nul
if errorlevel 1 (
    echo [오류] %WORK_DIR% 디렉토리를 생성할 수 없습니다.
    echo 관리자 권한으로 실행하거나 권한을 확인하세요.
    echo.
    pause
    exit /b 1
)

REM Detect source path
set "SOURCE_PATH=%~dp0"
echo 소스 경로: %SOURCE_PATH%

REM Check if running from WSL path
echo %SOURCE_PATH% | find "\\wsl" >nul
if %errorlevel%==0 (
    echo WSL 경로에서 실행 감지됨
    set "WSL_PATH=\\wsl.localhost\Ubuntu-22.04\home\nosky\macro"
) else (
    echo 로컬 경로에서 실행 중
    set "WSL_PATH=%SOURCE_PATH%"
)

REM Use PowerShell to copy files
echo.
echo 애플리케이션 파일 복사 중...
powershell -Command "& {Try {Copy-Item -Path '%WSL_PATH%\*' -Destination '%WORK_DIR%' -Recurse -Force -ErrorAction Stop; Write-Host '복사 완료!'} Catch {Write-Host '복사 오류: ' $_.Exception.Message -ForegroundColor Red; exit 1}}"

if errorlevel 1 (
    echo.
    echo [오류] 복사 실패! 대체 방법 시도 중...
    xcopy "%WSL_PATH%\*.*" "%WORK_DIR%\" /E /I /Y /Q
)

REM Move to working directory
cd /d %WORK_DIR%
echo 현재 디렉토리: %CD%

REM Check Python
echo.
echo Python 설치 확인 중...
python --version 2>nul
if errorlevel 1 (
    echo [오류] Python이 설치되지 않았습니다!
    echo https://python.org 에서 Python을 설치하세요.
    echo 설치 시 "Add Python to PATH"를 체크하세요.
    pause
    exit /b 1
)

REM Set UTF-8 environment
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set QT_QPA_PLATFORM=windows

REM Run self diagnosis first
echo.
echo ============================================================
echo 시스템 자가 진단 실행 중...
echo ============================================================
python -c "import sys; sys.path.insert(0, '.'); from src.utils.self_diagnosis import run_diagnosis; run_diagnosis()"

if errorlevel 1 (
    echo.
    echo [경고] 자가 진단에서 문제를 발견했지만 계속 진행합니다...
    echo.
)

REM Install/upgrade packages
echo.
echo 필수 패키지 설치/업그레이드 중...
python -m pip install --upgrade pip
pip install PyQt5 pandas openpyxl pyautogui pillow opencv-python numpy mss screeninfo easyocr cryptography psutil

REM Create recovery runner if not exists
if not exist "run_with_recovery.py" (
    echo.
    echo run_with_recovery.py 생성 중...
    (
        echo from src.utils.error_recovery import get_recovery_manager
        echo from src.utils.self_diagnosis import SelfDiagnosis
        echo import sys
        echo import os
        echo.
        echo def main^(^):
        echo     # UTF-8 설정
        echo     os.environ['PYTHONUTF8'] = '1'
        echo     
        echo     # 자가 진단 실행
        echo     diagnosis = SelfDiagnosis^(^)
        echo     diagnosis.run_quick_diagnosis^(^)
        echo     
        echo     # 오류 복구 매니저 초기화
        echo     recovery = get_recovery_manager^(^)
        echo     
        echo     try:
        echo         # 메인 앱 실행
        echo         from run_main_fixed import main as app_main
        echo         app_main^(^)
        echo     except Exception as e:
        echo         print^(f"앱 실행 중 오류 발생: {e}"^)
        echo         # 오류 복구 시도
        echo         if recovery.try_recover^(e^):
        echo             print^("오류 복구 성공, 다시 시도합니다..."^)
        echo             try:
        echo                 app_main^(^)
        echo             except:
        echo                 print^("재시도 실패"^)
        echo                 raise
        echo         else:
        echo             raise
        echo.
        echo if __name__ == "__main__":
        echo     main^(^)
    ) > run_with_recovery.py
)

REM Run the application with error recovery
echo.
echo ============================================================
echo 애플리케이션을 자동 복구 모드로 시작합니다...
echo ============================================================
echo.

python run_with_recovery.py

set EXIT_CODE=%errorlevel%

echo.
echo ============================================================
if %EXIT_CODE%==0 (
    echo 애플리케이션이 정상적으로 종료되었습니다.
) else (
    echo 애플리케이션이 오류와 함께 종료되었습니다: %EXIT_CODE%
    echo.
    echo 오류 정보 수집 중...
    python -c "import sys; sys.path.insert(0, '.'); from src.utils.error_report_generator import collect_and_save_errors; count = collect_and_save_errors(1); print(f'{count}개의 오류가 수집되었습니다.')"
    echo.
    echo 수집된 오류 확인:
    echo %USERPROFILE%\.excel_macro_automation\collected_errors\
    echo.
    echo 다음을 시도해보세요:
    echo 1. DIAGNOSE_AND_FIX.bat 실행
    echo 2. 관리자 권한으로 재실행
    echo 3. COLLECT_ERRORS_WINDOWS.bat으로 오류 수집 후 분석
)
echo ============================================================

echo.
pause
endlocal
exit /b %EXIT_CODE%