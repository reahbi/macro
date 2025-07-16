#!/bin/bash
# WSL GUI 설정 스크립트

echo "=== WSL GUI 환경 설정 ==="

# 1. Windows IP 자동 감지
WINDOWS_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2; exit;}')
echo "Windows IP: $WINDOWS_IP"

# 2. DISPLAY 환경 변수 설정
export DISPLAY=$WINDOWS_IP:0.0
export LIBGL_ALWAYS_INDIRECT=1

echo "DISPLAY 설정: $DISPLAY"

# 3. .bashrc에 영구 설정 추가 (이미 없는 경우만)
if ! grep -q "export DISPLAY=" ~/.bashrc; then
    echo "" >> ~/.bashrc
    echo "# WSL GUI Support" >> ~/.bashrc
    echo "export DISPLAY=\$(cat /etc/resolv.conf | grep nameserver | awk '{print \$2; exit;}'):0.0" >> ~/.bashrc
    echo "export LIBGL_ALWAYS_INDIRECT=1" >> ~/.bashrc
    echo "✓ ~/.bashrc에 DISPLAY 설정이 추가되었습니다."
else
    echo "✓ ~/.bashrc에 이미 DISPLAY 설정이 있습니다."
fi

# 4. 필요한 패키지 확인
echo ""
echo "필요한 패키지 확인 중..."

# PyQt5 확인
if python3 -c "import PyQt5" 2>/dev/null; then
    echo "✓ PyQt5가 설치되어 있습니다."
else
    echo "✗ PyQt5가 설치되지 않았습니다."
fi

# 5. X Server 연결 테스트
echo ""
echo "X Server 연결 테스트..."
if command -v xeyes &> /dev/null; then
    timeout 2 xeyes 2>/dev/null &
    XEYES_PID=$!
    sleep 1
    if kill -0 $XEYES_PID 2>/dev/null; then
        echo "✓ X Server 연결 성공! (xeyes가 표시되어야 합니다)"
        kill $XEYES_PID 2>/dev/null
    else
        echo "✗ X Server 연결 실패"
        echo ""
        echo "다음을 확인하세요:"
        echo "1. Windows에서 VcXsrv가 실행 중인가?"
        echo "2. VcXsrv 설정에서 'Disable access control'이 체크되어 있는가?"
        echo "3. Windows 방화벽이 VcXsrv를 차단하고 있지 않은가?"
    fi
fi

echo ""
echo "설정이 완료되었습니다."
echo "새 터미널을 열거나 다음 명령을 실행하세요:"
echo "source ~/.bashrc"