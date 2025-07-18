@echo off
title 시스템 진단 및 자동 수정
color 0E

echo ============================================================
echo Excel Macro Automation - 시스템 진단 도구
echo ============================================================
echo.
echo 시스템을 진단하고 발견된 문제를 자동으로 수정합니다.
echo.

REM 가상환경 활성화
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM 필수 패키지 설치
echo chardet 패키지 확인 중...
pip show chardet >nul 2>&1
if %errorlevel% neq 0 (
    echo chardet 설치 중...
    pip install chardet
)

echo psutil 패키지 확인 중... (선택사항)
pip show psutil >nul 2>&1
if %errorlevel% neq 0 (
    echo psutil 설치 중...
    pip install psutil
)

echo.
echo ============================================================
echo 시스템 진단을 시작합니다...
echo ============================================================

REM 진단 실행
python -m utils.self_diagnosis

echo.
echo ============================================================
echo 진단이 완료되었습니다.
echo ============================================================
echo.
pause