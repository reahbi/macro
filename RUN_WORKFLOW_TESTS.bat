@echo off
chcp 65001 >nul
cls
echo ========================================
echo Running Workflow Tests
echo ========================================
echo.

REM 프로젝트 디렉토리로 이동
cd /d "%~dp0"

REM 가상환경 확인 및 활성화
if exist venv_auto (
    echo 가상환경 활성화 중...
    call venv_auto\Scripts\activate.bat
) else if exist venv313 (
    echo 가상환경 활성화 중...
    call venv313\Scripts\activate.bat
) else (
    echo [오류] 가상환경이 없습니다!
    echo RUN_AUTO_VENV.bat을 먼저 실행하세요.
    pause
    exit /b 1
)

REM 테스트 실행
echo.
echo 워크플로우 테스트 시작...
echo.

python run_workflow_tests.py

echo.
pause