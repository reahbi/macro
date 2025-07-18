@echo off
title Excel Macro Automation - 자동 오류 복구 모드
color 0A

echo ============================================================
echo Excel Macro Automation - 자동 오류 복구 모드
echo ============================================================
echo.
echo 이 실행기는 다음 기능을 제공합니다:
echo - 시스템 자가 진단
echo - 오류 자동 감지 및 복구
echo - 환경 설정 자동 수정
echo.

REM 가상환경 활성화
if exist venv\Scripts\activate.bat (
    echo 가상환경을 활성화합니다...
    call venv\Scripts\activate.bat
) else (
    echo 가상환경이 없습니다. 시스템 Python을 사용합니다.
)

REM Python 실행
echo.
echo 프로그램을 시작합니다...
echo ============================================================
python run_with_recovery.py

REM 오류 코드 확인
if %errorlevel% neq 0 (
    echo.
    echo ============================================================
    echo 프로그램이 오류와 함께 종료되었습니다.
    echo.
    echo 다음을 시도해보세요:
    echo 1. python -m utils.self_diagnosis 실행
    echo 2. pip install -r requirements.txt 실행
    echo 3. 관리자 권한으로 다시 실행
    echo ============================================================
)

echo.
pause