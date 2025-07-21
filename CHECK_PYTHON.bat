@echo off
chcp 65001 >nul
cls
echo ========================================
echo Python 설치 상태 확인
echo ========================================
echo.

echo 1. 시스템 Python 확인:
echo ------------------------
python --version 2>nul
if errorlevel 1 (
    echo [오류] python 명령을 찾을 수 없습니다.
) else (
    echo [성공] Python이 설치되어 있습니다.
)

echo.
echo 2. Python3 명령 확인:
echo ------------------------
python3 --version 2>nul
if errorlevel 1 (
    echo [정보] python3 명령을 찾을 수 없습니다.
) else (
    echo [성공] python3 명령이 있습니다.
)

echo.
echo 3. py 런처 확인:
echo ------------------------
py --version 2>nul
if errorlevel 1 (
    echo [정보] py 런처를 찾을 수 없습니다.
) else (
    echo [성공] py 런처가 설치되어 있습니다.
    echo.
    echo 설치된 Python 버전들:
    py -0
)

echo.
echo 4. PATH 환경변수 확인:
echo ------------------------
echo %PATH% | findstr /i python >nul
if errorlevel 1 (
    echo [경고] PATH에 Python이 없습니다.
) else (
    echo [성공] PATH에 Python이 포함되어 있습니다.
)

echo.
echo 5. 현재 사용 가능한 Python:
echo ------------------------
where python 2>nul
if errorlevel 1 (
    echo [오류] Python 실행 파일을 찾을 수 없습니다.
)

echo.
pause