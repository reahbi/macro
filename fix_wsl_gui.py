#!/usr/bin/env python3
"""
WSL GUI 문제 해결을 위한 종합 진단 및 수정 스크립트
"""

import os
import sys
import subprocess
import platform

print("=== WSL GUI 문제 해결 스크립트 ===\n")

# 1. 시스템 정보 확인
print("1. 시스템 정보:")
print(f"   - Python: {sys.version}")
print(f"   - Platform: {platform.platform()}")
print(f"   - WSL 버전: ", end="")
try:
    wsl_version = subprocess.check_output(['wsl.exe', '-l', '-v'], text=True, stderr=subprocess.DEVNULL)
    print("WSL2" if "2" in wsl_version else "WSL1")
except:
    print("확인 불가")

# 2. 모든 가능한 DISPLAY 설정 시도
print("\n2. DISPLAY 설정 테스트:")

# Windows IP 가져오기
windows_ip = subprocess.check_output("cat /etc/resolv.conf | grep nameserver | awk '{print $2}'", shell=True, text=True).strip()

display_options = [
    f"{windows_ip}:0.0",
    f"{windows_ip}:0",
    "localhost:0.0",
    "localhost:0",
    ":0.0",
    ":0",
    ":1",
    "host.docker.internal:0.0"  # Docker Desktop 사용 시
]

# 3. Qt 환경 변수 설정
print("\n3. Qt 환경 변수 최적화:")
qt_settings = {
    'QT_QPA_PLATFORM': 'xcb',
    'QT_XCB_GL_INTEGRATION': 'none',
    'LIBGL_ALWAYS_INDIRECT': '1',
    'LIBGL_ALWAYS_SOFTWARE': '1',
    'QT_QUICK_BACKEND': 'software',
    'QT_AUTO_SCREEN_SCALE_FACTOR': '0',
    'QT_SCALE_FACTOR': '1',
    'GDK_SCALE': '1',
    'GDK_DPI_SCALE': '1'
}

for key, value in qt_settings.items():
    os.environ[key] = value
    print(f"   - {key}={value}")

# 4. 필요한 패키지 확인
print("\n4. 필요한 시스템 패키지 확인:")
required_packages = [
    'libxcb-xinerama0',
    'libxcb-icccm4',
    'libxcb-image0',
    'libxcb-keysyms1',
    'libxcb-randr0',
    'libxcb-render-util0',
    'libxcb-shape0',
    'libxcb-xfixes0',
    'libxkbcommon-x11-0',
    'libgl1-mesa-glx',
    'libglu1-mesa',
    'libegl1-mesa',
    'libxrandr2',
    'libxss1',
    'libxcursor1',
    'libxcomposite1',
    'libasound2',
    'libxi6',
    'libxtst6'
]

missing_packages = []
for pkg in required_packages:
    result = subprocess.run(['dpkg', '-l', pkg], capture_output=True, text=True)
    if result.returncode != 0:
        missing_packages.append(pkg)
        print(f"   ✗ {pkg} - 미설치")
    else:
        print(f"   ✓ {pkg} - 설치됨")

if missing_packages:
    print(f"\n   설치 필요: sudo apt-get install {' '.join(missing_packages)}")

# 5. PyQt5 플랫폼 플러그인 확인
print("\n5. PyQt5 플랫폼 플러그인 확인:")
try:
    from PyQt5.QtCore import QCoreApplication
    app = QCoreApplication.instance()
    if app is None:
        app = QCoreApplication(sys.argv)
    
    from PyQt5.QtGui import QGuiApplication
    available_platforms = QGuiApplication.platformName()
    print(f"   - 현재 플랫폼: {available_platforms}")
    
    # 플러그인 경로 확인
    from PyQt5.QtCore import QLibraryInfo
    plugin_path = QLibraryInfo.location(QLibraryInfo.PluginsPath)
    print(f"   - 플러그인 경로: {plugin_path}")
    
    platforms_dir = os.path.join(plugin_path, 'platforms')
    if os.path.exists(platforms_dir):
        print(f"   - 사용 가능한 플랫폼:")
        for f in os.listdir(platforms_dir):
            print(f"     • {f}")
except Exception as e:
    print(f"   ✗ PyQt5 플러그인 확인 실패: {e}")

# 6. 실행 스크립트 생성
print("\n6. 최적화된 실행 스크립트 생성:")

script_content = f'''#!/bin/bash
# WSL GUI 최적화 실행 스크립트

echo "WSL GUI 실행 준비..."

# Windows IP 자동 감지
export DISPLAY=$(cat /etc/resolv.conf | grep nameserver | awk '{{print $2; exit;}}'):0.0

# Qt 최적화 설정
export QT_QPA_PLATFORM=xcb
export QT_XCB_GL_INTEGRATION=none
export LIBGL_ALWAYS_INDIRECT=1
export LIBGL_ALWAYS_SOFTWARE=1
export QT_QUICK_BACKEND=software
export QT_AUTO_SCREEN_SCALE_FACTOR=0
export QT_SCALE_FACTOR=1

# Mesa 소프트웨어 렌더링 강제
export MESA_GL_VERSION_OVERRIDE=3.3
export MESA_GLSL_VERSION_OVERRIDE=330

# 디버그 정보
export QT_DEBUG_PLUGINS=1
export QT_LOGGING_RULES="qt.qpa.xcb*=true"

echo "DISPLAY: $DISPLAY"
echo "QT_QPA_PLATFORM: $QT_QPA_PLATFORM"

# 가상환경 활성화
source venv/bin/activate

# 실행
python run_simple.py 2>&1 | tee gui_debug.log
'''

with open('run_wsl_optimized.sh', 'w') as f:
    f.write(script_content)
os.chmod('run_wsl_optimized.sh', 0o755)
print("   ✓ run_wsl_optimized.sh 생성 완료")

# 7. 대안 솔루션
print("\n7. 추가 해결 방법:")
print("   A. WSLg 사용 (Windows 11):")
print("      - PowerShell 관리자: wsl --update")
print("      - WSL 재시작: wsl --shutdown")
print("      - DISPLAY=:0 으로 설정")
print("\n   B. VcXsrv 대신 X410 사용:")
print("      - Microsoft Store에서 X410 구매/설치")
print("      - WSL2 모드로 실행")
print("\n   C. MobaXterm 사용:")
print("      - 내장 X Server 자동 실행")
print("      - WSL 세션 직접 지원")

# 8. 간단한 테스트
print("\n8. GUI 테스트:")
for display in display_options[:3]:  # 처음 3개만 테스트
    print(f"\n   DISPLAY={display} 테스트 중...")
    os.environ['DISPLAY'] = display
    
    try:
        from PyQt5.QtWidgets import QApplication, QWidget
        from PyQt5.QtCore import QTimer
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 테스트 창
        test_window = QWidget()
        test_window.setWindowTitle(f"테스트 - DISPLAY={display}")
        test_window.resize(300, 100)
        
        # 1초 후 자동 종료
        QTimer.singleShot(1000, app.quit)
        
        test_window.show()
        print(f"   ✓ 창 생성 성공! 이 설정을 사용하세요: DISPLAY={display}")
        break
        
    except Exception as e:
        print(f"   ✗ 실패: {str(e)[:50]}...")
        continue

print("\n완료! './run_wsl_optimized.sh' 실행해보세요.")