#!/bin/bash
# Windows + WSL2 환경 실행 스크립트

echo "Windows + WSL2 환경에서 Excel Macro Automation 실행"
echo "=================================================="

# Windows IP 주소 가져오기
WINDOWS_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
export DISPLAY=$WINDOWS_IP:0.0
export LIBGL_ALWAYS_INDIRECT=1

echo "Windows IP: $WINDOWS_IP"
echo "DISPLAY 설정: $DISPLAY"
echo ""

# X Server 연결 테스트
echo "X Server 연결 테스트 중..."
if command -v xset &> /dev/null; then
    if xset q &>/dev/null; then
        echo "✓ X Server 연결 성공!"
    else
        echo "✗ X Server에 연결할 수 없습니다."
        echo ""
        echo "다음을 확인하세요:"
        echo "1. Windows에서 VcXsrv 또는 MobaXterm이 실행 중인가?"
        echo "2. VcXsrv 설정에서 'Disable access control'이 체크되어 있는가?"
        echo "3. Windows 방화벽이 X Server를 차단하고 있지 않은가?"
        echo ""
        echo "VcXsrv 다운로드: https://sourceforge.net/projects/vcxsrv/"
        exit 1
    fi
else
    echo "xset이 설치되지 않았습니다. X Server 테스트를 건너뜁니다."
fi

echo ""
echo "가상환경 활성화..."
source venv/bin/activate

echo "Python 경로: $(which python)"
echo "Python 버전: $(python --version)"
echo ""

# 애플리케이션 실행
echo "애플리케이션을 실행합니다..."
python run_simple.py