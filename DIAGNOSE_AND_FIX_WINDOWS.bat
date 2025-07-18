@echo off
chcp 65001 >nul 2>&1
title 시스템 진단 및 자동 수정
color 0E

cls
echo ============================================================
echo 시스템 진단 및 자동 수정 도구
echo ============================================================
echo.
echo 이 도구는 다음을 수행합니다:
echo - Python 환경 검사
echo - 필수 패키지 검사 및 설치
echo - 파일 시스템 무결성 확인
echo - 인코딩 설정 수정
echo - 시스템 리소스 확인
echo.

REM 작업 디렉토리 설정
set WORK_DIR=C:\macro

REM WSL에서 직접 실행하는 경우 처리
if not exist "%WORK_DIR%" (
    echo [정보] %WORK_DIR%가 없습니다. 현재 위치에서 진단합니다.
    set "WORK_DIR=%~dp0"
)

cd /d "%WORK_DIR%"
echo 작업 디렉토리: %CD%
echo.

REM Python 확인
echo [1/5] Python 설치 확인...
python --version 2>nul
if errorlevel 1 (
    echo [오류] Python이 설치되지 않았습니다!
    echo.
    echo Python 설치 방법:
    echo 1. https://python.org 에서 다운로드
    echo 2. 설치 시 "Add Python to PATH" 체크
    echo 3. 설치 후 이 스크립트 재실행
    echo.
    pause
    exit /b 1
)
echo [확인] Python이 설치되어 있습니다.
echo.

REM UTF-8 환경 설정
echo [2/5] 환경 변수 설정 중...
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set QT_QPA_PLATFORM=windows
echo [확인] UTF-8 환경이 설정되었습니다.
echo.

REM 진단 스크립트 생성
echo [3/5] 진단 스크립트 생성 중...
(
    echo import sys
    echo import os
    echo sys.path.insert^(0, '.'
    echo.
    echo # UTF-8 설정
    echo os.environ['PYTHONUTF8'] = '1'
    echo.
    echo try:
    echo     from src.utils.self_diagnosis import SelfDiagnosis
    echo     diagnosis = SelfDiagnosis^(^)
    echo     result = diagnosis.run_full_diagnosis^(^)
    echo     
    echo     print^("\n진단 결과:"^)
    echo     print^(f"총 검사: {result['summary']['total']}"^)
    echo     print^(f"성공: {result['summary']['passed']}"^)
    echo     print^(f"실패: {result['summary']['failed']}"^)
    echo     print^(f"자동 수정: {result['summary']['fixes_applied']}"^)
    echo     
    echo     if result['summary']['failed'] ^> 0:
    echo         print^("\n실패한 검사:"^)
    echo         for category, checks in result['results'].items^(^):
    echo             for check in checks:
    echo                 if not check['passed']:
    echo                     print^(f"- [{category}] {check['name']}: {check.get^('error', 'Failed'^)}"^)
    echo     
    echo except ImportError as e:
    echo     print^(f"모듈 임포트 오류: {e}"^)
    echo     print^("필수 패키지를 설치합니다..."^)
    echo     import subprocess
    echo     subprocess.run^([sys.executable, "-m", "pip", "install", "--upgrade", "pip"]^)
    echo     subprocess.run^([sys.executable, "-m", "pip", "install", "PyQt5", "pandas", "openpyxl", "pyautogui", "pillow", "opencv-python", "numpy", "mss", "screeninfo", "easyocr", "cryptography", "psutil"]^)
    echo except Exception as e:
    echo     print^(f"진단 중 오류 발생: {e}"^)
    echo     import traceback
    echo     traceback.print_exc^(^)
) > diagnose_temp.py

REM 진단 실행
echo [4/5] 시스템 진단 실행 중...
echo ============================================================
python diagnose_temp.py
echo ============================================================
echo.

REM 진단 스크립트 삭제
del diagnose_temp.py 2>nul

REM 추가 패키지 설치 확인
echo [5/5] 필수 패키지 확인 및 설치...
echo.

REM pip 업그레이드
echo pip 업그레이드 중...
python -m pip install --upgrade pip

REM 필수 패키지 설치
echo.
echo 필수 패키지 설치 중...
pip install PyQt5 pandas openpyxl pyautogui pillow opencv-python numpy mss screeninfo easyocr cryptography psutil

echo.
echo ============================================================
echo 진단 및 수정 완료!
echo.
echo 다음 단계:
echo 1. RUN_WITH_AUTOFIX_WINDOWS.bat 실행하여 앱 시작
echo 2. 문제가 지속되면 COLLECT_ERRORS_WINDOWS.bat 실행
echo 3. 수집된 오류를 분석하여 추가 조치
echo ============================================================
echo.

REM 오류 디렉토리 생성
if not exist "%USERPROFILE%\.excel_macro_automation" (
    mkdir "%USERPROFILE%\.excel_macro_automation"
)
if not exist "%USERPROFILE%\.excel_macro_automation\logs" (
    mkdir "%USERPROFILE%\.excel_macro_automation\logs"
)
if not exist "%USERPROFILE%\.excel_macro_automation\collected_errors" (
    mkdir "%USERPROFILE%\.excel_macro_automation\collected_errors"
)

echo 로그 및 오류 수집 디렉토리가 준비되었습니다.
echo.

pause