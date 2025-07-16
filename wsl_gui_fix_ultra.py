#!/usr/bin/env python3
"""
WSL GUI 표시를 위한 혁신적인 해결책
다중 접근법을 동시에 시도하여 가장 효과적인 방법을 찾습니다.
"""

import sys
import os
import subprocess
import time
import threading
from pathlib import Path

# 프로젝트 경로 설정
project_root = Path(__file__).parent.absolute()
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

print("=== WSL GUI Ultra Fix ===\n")

# 1. 환경 변수 최적화
def setup_environment():
    """모든 가능한 환경 변수 설정"""
    
    # Windows IP 자동 감지
    try:
        windows_ip = subprocess.check_output(
            "cat /etc/resolv.conf | grep nameserver | awk '{print $2}'", 
            shell=True, text=True
        ).strip()
    except:
        windows_ip = "172.25.144.1"  # 기본값
    
    env_vars = {
        # Display 설정 - 여러 옵션 시도
        'DISPLAY': f'{windows_ip}:0.0',
        
        # Qt 최적화
        'QT_QPA_PLATFORM': 'xcb',
        'QT_XCB_GL_INTEGRATION': 'none',
        'QT_QUICK_BACKEND': 'software',
        'QT_AUTO_SCREEN_SCALE_FACTOR': '0',
        'QT_SCALE_FACTOR': '1',
        'QT_SCREEN_SCALE_FACTORS': '1',
        'QT_DEVICE_PIXEL_RATIO': '1',
        
        # OpenGL 소프트웨어 렌더링
        'LIBGL_ALWAYS_INDIRECT': '1',
        'LIBGL_ALWAYS_SOFTWARE': '1',
        'MESA_GL_VERSION_OVERRIDE': '3.3',
        'MESA_GLSL_VERSION_OVERRIDE': '330',
        
        # X11 최적화
        'X11_NO_MITSHM': '1',
        '_X11_NO_MITSHM': '1',
        
        # 추가 디버그
        'QT_DEBUG_PLUGINS': '1',
        'QT_LOGGING_RULES': 'qt.qpa.xcb*=true',
        
        # GTK 호환성
        'GDK_BACKEND': 'x11',
        'CLUTTER_BACKEND': 'x11',
        
        # 경로 설정
        'PYTHONPATH': f"{project_root}:{src_path}"
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
        
    print(f"Display: {os.environ['DISPLAY']}")
    print(f"Qt Platform: {os.environ['QT_QPA_PLATFORM']}")
    print()

# 2. X Server 연결 테스트
def test_x_connection():
    """X Server 연결 테스트"""
    print("X Server 연결 테스트...")
    
    try:
        result = subprocess.run(['xset', 'q'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✓ X Server 연결 성공!\n")
            return True
        else:
            print("✗ X Server 연결 실패\n")
            return False
    except:
        print("✗ xset 명령 실행 실패\n")
        return False

# 3. 간단한 Qt 테스트
def test_simple_qt():
    """최소한의 Qt 창 테스트"""
    print("간단한 Qt 테스트...")
    
    try:
        from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout
        from PyQt5.QtCore import Qt, QTimer
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        # 테스트 창
        test_window = QWidget()
        test_window.setWindowTitle("WSL GUI Test")
        test_window.setFixedSize(400, 200)
        
        layout = QVBoxLayout()
        label = QLabel("GUI가 표시되면 성공입니다!")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 20px; padding: 20px;")
        layout.addWidget(label)
        test_window.setLayout(layout)
        
        # 중앙에 표시
        test_window.setWindowFlags(Qt.WindowStaysOnTopHint)
        test_window.show()
        test_window.raise_()
        test_window.activateWindow()
        
        # 2초 후 자동 종료
        QTimer.singleShot(2000, app.quit)
        
        print("✓ Qt 테스트 창 생성 성공!")
        print("  (2초 후 자동 종료)")
        
        app.exec_()
        return True
        
    except Exception as e:
        print(f"✗ Qt 테스트 실패: {e}")
        return False

# 4. 대체 실행 방법
def run_with_xvfb():
    """Xvfb를 사용한 가상 디스플레이 실행"""
    print("\nXvfb 가상 디스플레이 시도...")
    
    try:
        # Xvfb 설치 확인
        result = subprocess.run(['which', 'xvfb-run'], capture_output=True)
        if result.returncode != 0:
            print("Xvfb 설치 중...")
            subprocess.run(['sudo', 'apt-get', 'install', '-y', 'xvfb'], 
                         input='121312\n', text=True)
        
        # Xvfb로 실행
        cmd = ['xvfb-run', '-a', '-s', '-screen 0 1280x720x24', 
               'python3', 'run_main.py']
        print(f"실행: {' '.join(cmd)}")
        subprocess.run(cmd)
        return True
        
    except Exception as e:
        print(f"✗ Xvfb 실행 실패: {e}")
        return False

# 5. VNC 서버 접근법
def setup_vnc_approach():
    """VNC 서버를 통한 GUI 표시"""
    print("\nVNC 서버 접근법 안내:")
    print("1. WSL에 VNC 서버 설치:")
    print("   sudo apt-get install tightvncserver")
    print("\n2. VNC 서버 시작:")
    print("   vncserver :1 -geometry 1280x720 -depth 24")
    print("\n3. Windows에서 VNC 뷰어로 연결:")
    print("   localhost:5901")
    print("\n4. VNC 세션에서 애플리케이션 실행:")
    print("   DISPLAY=:1 python run_main.py")

# 6. 웹 기반 UI 접근법
def create_web_launcher():
    """웹 기반 실행기 생성"""
    web_launcher = """#!/usr/bin/env python3
'''웹 기반 GUI 런처'''
import subprocess
import webbrowser
import time
from flask import Flask, render_template_string
import threading

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Excel Macro Automation - Web Launcher</title>
    <style>
        body { font-family: Arial; padding: 20px; background: #f0f0f0; }
        .container { max-width: 600px; margin: auto; background: white; 
                    padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        button { background: #4CAF50; color: white; padding: 15px 30px; 
                border: none; border-radius: 5px; font-size: 16px; cursor: pointer; }
        button:hover { background: #45a049; }
        .status { margin-top: 20px; padding: 10px; background: #e8f5e9; 
                 border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Excel Macro Automation</h1>
        <p>WSL GUI를 Windows에서 실행하기 위한 웹 런처입니다.</p>
        
        <h3>실행 옵션:</h3>
        <button onclick="runApp('native')">네이티브 실행 (X Server)</button>
        <button onclick="runApp('xvfb')">가상 디스플레이 실행</button>
        <button onclick="runApp('debug')">디버그 모드</button>
        
        <div class="status" id="status">
            준비됨
        </div>
    </div>
    
    <script>
        function runApp(mode) {
            document.getElementById('status').innerHTML = '실행 중...';
            fetch('/run/' + mode)
                .then(response => response.text())
                .then(data => {
                    document.getElementById('status').innerHTML = data;
                });
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/run/<mode>')
def run_app(mode):
    try:
        if mode == 'native':
            subprocess.Popen(['python3', 'run_main.py'])
            return '네이티브 모드로 실행되었습니다.'
        elif mode == 'xvfb':
            subprocess.Popen(['xvfb-run', '-a', 'python3', 'run_main.py'])
            return '가상 디스플레이에서 실행되었습니다.'
        elif mode == 'debug':
            subprocess.Popen(['python3', 'wsl_gui_fix_ultra.py'])
            return '디버그 모드로 실행되었습니다.'
    except Exception as e:
        return f'오류: {e}'

if __name__ == '__main__':
    # 브라우저 자동 열기
    def open_browser():
        time.sleep(1)
        webbrowser.open('http://localhost:5000')
    
    threading.Thread(target=open_browser).start()
    app.run(host='0.0.0.0', port=5000, debug=False)
"""
    
    with open('web_launcher.py', 'w') as f:
        f.write(web_launcher)
    
    print("\n✓ 웹 런처 생성 완료: web_launcher.py")
    print("실행: python3 web_launcher.py")

# 7. Windows 네이티브 실행 접근법
def create_windows_native_runner():
    """Windows에서 직접 실행하는 스크립트"""
    powershell_script = """# PowerShell script to run WSL GUI app from Windows
$wslPath = "\\\\wsl.localhost\\Ubuntu\\home\\nosky\\macro"
$pythonExe = "python"

# Check if Python is installed in Windows
try {
    $pythonVersion = & $pythonExe --version 2>$null
    Write-Host "Python found: $pythonVersion"
} catch {
    Write-Host "Python not found. Installing Python..."
    Start-Process "https://www.python.org/downloads/"
    exit
}

# Install required packages
Write-Host "Installing required packages..."
& $pythonExe -m pip install PyQt5 pandas openpyxl pyautogui opencv-python numpy easyocr

# Set environment variables
$env:PYTHONPATH = "$wslPath\\src;$wslPath"

# Run the application
Write-Host "Starting application..."
Set-Location $wslPath
& $pythonExe run_main.py
"""
    
    with open('run_from_windows.ps1', 'w') as f:
        f.write(powershell_script)
    
    print("\n✓ Windows PowerShell 스크립트 생성: run_from_windows.ps1")
    print("Windows PowerShell에서 실행: .\\run_from_windows.ps1")

# 메인 실행
def main():
    # 1. 환경 설정
    setup_environment()
    
    # 2. X Server 연결 테스트
    if test_x_connection():
        # 3. 간단한 Qt 테스트
        if test_simple_qt():
            print("\n✓ Qt 테스트 성공! 메인 애플리케이션 실행...")
            
            # Import 경로 수정
            exec(open('run_main.py').read())
        else:
            print("\n대체 방법 시도...")
            
            # 4. Xvfb 시도
            if not run_with_xvfb():
                # 5. 다른 대안 제시
                setup_vnc_approach()
                create_web_launcher()
                create_windows_native_runner()
                
                print("\n=== 권장 해결책 ===")
                print("1. 웹 런처 사용: python3 web_launcher.py")
                print("2. Windows에서 직접 실행: PowerShell에서 .\\run_from_windows.ps1")
                print("3. VNC 서버 사용 (위 안내 참조)")
    else:
        print("\nX Server 연결 실패. 대체 방법 생성 중...")
        create_web_launcher()
        create_windows_native_runner()
        
        print("\n=== X Server 없이 실행하는 방법 ===")
        print("1. 웹 런처: python3 web_launcher.py")
        print("2. Windows 네이티브: PowerShell에서 .\\run_from_windows.ps1")

if __name__ == "__main__":
    main()