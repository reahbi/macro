@echo off
chcp 65001 >nul
cls
echo ========================================
echo Python 3.13 환경 완전 초기화
echo ========================================
echo.
echo 이 스크립트는:
echo - 모든 가상환경 제거
echo - pip 캐시 정리  
echo - 깨끗한 Python 3.13 환경 재설정
echo.
echo 계속하시겠습니까? (Y/N)
choice /C YN /N
if errorlevel 2 exit /b 0

REM 프로젝트 디렉토리로 이동
cd /d "%~dp0"

REM 모든 가상환경 제거
echo.
echo 기존 가상환경 제거 중...
if exist venv rmdir /s /q venv
if exist venv312 rmdir /s /q venv312
if exist venv313 rmdir /s /q venv313
echo 가상환경 제거 완료!

REM pip 캐시 정리
echo.
echo pip 캐시 정리 중...
pip cache purge

REM Python 3.13 환경 설정 실행
echo.
echo ========================================
echo 새로운 Python 3.13 환경 설정 시작
echo ========================================
echo.
call SETUP_PY313_VENV.bat

echo.
echo ========================================
echo 초기화 완료!
echo ========================================
echo.
echo 프로그램 실행: RUN_PY313.bat
echo.
pause