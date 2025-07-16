#!/bin/bash
# Excel Macro Automation 실행 스크립트

echo "Excel Macro Automation GUI 시작..."
echo "=================================="

# 가상환경 활성화
source venv/bin/activate

# 환경 변수 설정
export DISPLAY=${DISPLAY:-:0}
export QT_QPA_PLATFORM=xcb
export QT_DEBUG_PLUGINS=0

# Python 경로 출력
echo "Python 경로: $(which python)"
echo "Python 버전: $(python --version)"
echo ""

# GUI 실행
echo "GUI를 실행합니다..."
python run_main.py

echo "=================================="
echo "프로그램이 종료되었습니다."