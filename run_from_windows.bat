@echo off
echo Excel Macro Automation - Windows 실행
echo =====================================
echo.

REM WSL 경로를 Windows 경로로 변환
set WSL_PATH=\\wsl.localhost\Ubuntu\home\nosky\macro

echo WSL 프로젝트 경로: %WSL_PATH%
echo.

REM Windows Python으로 실행
echo Python 버전 확인...
python --version

echo.
echo 필요한 패키지 설치 중...
cd /d %WSL_PATH%
python -m pip install PyQt5 pandas openpyxl pyautogui opencv-python numpy

echo.
echo 애플리케이션 실행...
set PYTHONPATH=%WSL_PATH%\src;%WSL_PATH%
python %WSL_PATH%\run_simple.py

pause