@echo off
chcp 65001 >nul
echo =====================================
echo 오류 수집 시스템 (Windows)
echo =====================================
echo.

REM 작업 디렉토리 설정
set WORK_DIR=C:\macro
if not exist "%WORK_DIR%" (
    echo [ERROR] %WORK_DIR% 디렉토리가 없습니다.
    echo RUN_ON_WINDOWS.bat을 먼저 실행하세요.
    pause
    exit /b 1
)

cd /d "%WORK_DIR%"

echo 최근 7일간의 오류를 수집합니다...
python -c "import sys; sys.path.insert(0, '.'); from src.utils.error_report_generator import collect_and_save_errors; count = collect_and_save_errors(7); print(f'\n총 {count}개의 오류가 수집되었습니다.')"

echo.
echo 수집된 오류 파일 위치:
echo %USERPROFILE%\.excel_macro_automation\collected_errors\
echo.

echo 최신 오류 요약:
python -c "import sys; sys.path.insert(0, '.'); from src.utils.error_report_generator import ErrorCollector; c = ErrorCollector(); errors = c.get_latest_errors(5); [print(f'{e[\"timestamp\"]}: {e[\"type\"]} - {e[\"message\"][:50]}...') for e in errors] if errors else print('수집된 오류가 없습니다.')"

echo.
echo 오류 파일을 탐색기에서 열기:
echo explorer "%USERPROFILE%\.excel_macro_automation\collected_errors"
echo.
pause