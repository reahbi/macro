#!/usr/bin/env python3
"""
디버그 모드로 실행
"""

import sys
import os
from pathlib import Path

# 프로젝트 경로 설정
project_root = Path(__file__).parent.absolute()
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

# Windows IP 자동 감지
import subprocess
result = subprocess.run(['cat', '/etc/resolv.conf'], capture_output=True, text=True)
for line in result.stdout.split('\n'):
    if 'nameserver' in line:
        windows_ip = line.split()[1]
        break

# 여러 DISPLAY 설정 시도
display_options = [
    f"{windows_ip}:0.0",
    f"{windows_ip}:0",
    "localhost:0.0",
    "localhost:0",
    ":0.0",
    ":0"
]

print("=== GUI 실행 시도 ===")
print(f"Windows IP: {windows_ip}")

for display in display_options:
    print(f"\nDISPLAY={display} 시도 중...")
    os.environ['DISPLAY'] = display
    os.environ['LIBGL_ALWAYS_INDIRECT'] = '1'
    
    try:
        from PyQt5.QtWidgets import QApplication, QMessageBox
        from PyQt5.QtCore import Qt, QTimer
        
        # High DPI 설정
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        
        app = QApplication(sys.argv)
        
        # 간단한 메시지 박스 표시
        msg = QMessageBox()
        msg.setWindowTitle("연결 성공!")
        msg.setText(f"X Server 연결 성공!\nDISPLAY: {display}")
        msg.setIcon(QMessageBox.Information)
        msg.setStandardButtons(QMessageBox.Ok)
        
        # 3초 후 자동 닫기
        QTimer.singleShot(3000, msg.close)
        
        msg.show()
        
        print(f"✓ 성공! DISPLAY={display}")
        print("\n올바른 DISPLAY 설정을 찾았습니다.")
        print(f"다음 명령어로 실행하세요:")
        print(f"export DISPLAY={display}")
        print(f"source venv/bin/activate")
        print(f"python run_simple.py")
        
        app.exec_()
        break
        
    except Exception as e:
        print(f"✗ 실패: {e}")
        continue
else:
    print("\n모든 DISPLAY 설정이 실패했습니다.")
    print("\nVcXsrv 설정을 확인하세요:")
    print("1. VcXsrv가 실행 중인가?")
    print("2. 'Disable access control' 옵션이 체크되어 있는가?")
    print("3. Windows 방화벽이 차단하고 있지 않은가?")