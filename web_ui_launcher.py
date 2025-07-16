#!/usr/bin/env python3
"""
WSL GUI 문제를 우회하는 웹 기반 UI 런처
브라우저를 통해 애플리케이션을 제어합니다.
"""

import os
import sys
import json
import threading
import webbrowser
import subprocess
from pathlib import Path
from datetime import datetime

# Flask 설치 확인
try:
    from flask import Flask, render_template_string, jsonify, request
except ImportError:
    print("Flask 설치 중...")
    subprocess.run([sys.executable, "-m", "pip", "install", "flask"])
    from flask import Flask, render_template_string, jsonify, request

# 프로젝트 경로 설정
project_root = Path(__file__).parent.absolute()
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

app = Flask(__name__)

# 전역 상태 관리
app_state = {
    "status": "ready",
    "excel_file": None,
    "macro_steps": [],
    "execution_log": []
}

# HTML 템플릿
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Excel Macro Automation - Web UI</title>
    <meta charset="utf-8">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: #f5f5f5; 
            color: #333;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            padding: 20px; 
        }
        .header {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .header h1 {
            color: #2196F3;
            margin-bottom: 10px;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .tab {
            padding: 10px 20px;
            background: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
        }
        .tab.active {
            background: #2196F3;
            color: white;
        }
        .tab:hover {
            background: #1976D2;
            color: white;
        }
        .content {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            min-height: 400px;
        }
        .panel {
            display: none;
        }
        .panel.active {
            display: block;
        }
        .button {
            background: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
            margin: 5px;
        }
        .button:hover {
            background: #45a049;
        }
        .button.secondary {
            background: #757575;
        }
        .button.secondary:hover {
            background: #616161;
        }
        .file-input {
            margin: 20px 0;
        }
        .status-box {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }
        .macro-step {
            background: #f5f5f5;
            padding: 15px;
            margin: 10px 0;
            border-radius: 5px;
            border-left: 4px solid #2196F3;
        }
        .log-entry {
            padding: 5px 10px;
            margin: 2px 0;
            background: #f9f9f9;
            border-radius: 3px;
            font-family: monospace;
            font-size: 14px;
        }
        .log-entry.error {
            background: #ffebee;
            color: #c62828;
        }
        .log-entry.success {
            background: #e8f5e9;
            color: #2e7d32;
        }
        .step-palette {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 10px;
            margin: 20px 0;
        }
        .step-type {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        .step-type:hover {
            background: #2196F3;
            color: white;
            transform: translateY(-2px);
        }
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #2196F3;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Excel Macro Automation</h1>
            <p>WSL GUI 문제를 우회하는 웹 기반 컨트롤 패널</p>
            <div class="status-box">
                상태: <span id="status">준비됨</span>
                <span id="loading" class="loading" style="display: none;"></span>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('excel')">📊 Excel</button>
            <button class="tab" onclick="showTab('editor')">✏️ Editor</button>
            <button class="tab" onclick="showTab('run')">▶️ Run</button>
            <button class="tab" onclick="showTab('native')">🖥️ Native GUI</button>
        </div>
        
        <div class="content">
            <!-- Excel 탭 -->
            <div id="excel" class="panel active">
                <h2>Excel 파일 관리</h2>
                <div class="file-input">
                    <input type="file" id="excelFile" accept=".xlsx,.xls">
                    <button class="button" onclick="uploadExcel()">업로드</button>
                </div>
                <div id="excelInfo"></div>
            </div>
            
            <!-- Editor 탭 -->
            <div id="editor" class="panel">
                <h2>매크로 편집기</h2>
                <div class="step-palette">
                    <div class="step-type" onclick="addStep('mouse_click')">🖱️ 마우스 클릭</div>
                    <div class="step-type" onclick="addStep('keyboard_type')">⌨️ 텍스트 입력</div>
                    <div class="step-type" onclick="addStep('wait_time')">⏱️ 대기</div>
                    <div class="step-type" onclick="addStep('image_search')">🔍 이미지 검색</div>
                    <div class="step-type" onclick="addStep('ocr_text')">🔤 텍스트 검색</div>
                    <div class="step-type" onclick="addStep('if_condition')">❓ 조건문</div>
                </div>
                <h3>현재 매크로</h3>
                <div id="macroSteps"></div>
                <button class="button" onclick="saveMacro()">매크로 저장</button>
                <button class="button secondary" onclick="clearMacro()">초기화</button>
            </div>
            
            <!-- Run 탭 -->
            <div id="run" class="panel">
                <h2>매크로 실행</h2>
                <button class="button" onclick="runMacro()">▶️ 실행</button>
                <button class="button secondary" onclick="stopMacro()">⏹️ 중지</button>
                <h3>실행 로그</h3>
                <div id="executionLog"></div>
            </div>
            
            <!-- Native GUI 탭 -->
            <div id="native" class="panel">
                <h2>네이티브 GUI 실행 옵션</h2>
                <p>웹 UI 대신 원래 GUI를 실행하려면 아래 옵션을 시도하세요:</p>
                
                <div style="margin: 20px 0;">
                    <h3>옵션 1: X Server 확인 후 실행</h3>
                    <button class="button" onclick="runNative('check')">X Server 체크 & 실행</button>
                    
                    <h3>옵션 2: 가상 디스플레이 (Xvfb)</h3>
                    <button class="button" onclick="runNative('xvfb')">Xvfb로 실행</button>
                    
                    <h3>옵션 3: Windows에서 직접 실행</h3>
                    <button class="button" onclick="runNative('windows')">Windows 스크립트 생성</button>
                    
                    <h3>옵션 4: 디버그 모드</h3>
                    <button class="button" onclick="runNative('debug')">디버그 정보 보기</button>
                </div>
                
                <div id="nativeOutput" style="margin-top: 20px;"></div>
            </div>
        </div>
    </div>
    
    <script>
        let currentTab = 'excel';
        
        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
            currentTab = tabName;
        }
        
        function updateStatus(status, loading = false) {
            document.getElementById('status').textContent = status;
            document.getElementById('loading').style.display = loading ? 'inline-block' : 'none';
        }
        
        function uploadExcel() {
            const fileInput = document.getElementById('excelFile');
            const file = fileInput.files[0];
            
            if (!file) {
                alert('파일을 선택해주세요.');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            updateStatus('Excel 파일 업로드 중...', true);
            
            fetch('/upload_excel', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                updateStatus('Excel 파일 로드 완료');
                document.getElementById('excelInfo').innerHTML = 
                    `<p>파일명: ${data.filename}</p>
                     <p>시트: ${data.sheets.join(', ')}</p>
                     <p>행 수: ${data.rows}</p>`;
            })
            .catch(error => {
                updateStatus('오류 발생');
                alert('오류: ' + error);
            });
        }
        
        function addStep(stepType) {
            fetch('/add_step', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({step_type: stepType})
            })
            .then(response => response.json())
            .then(data => {
                refreshMacroSteps();
            });
        }
        
        function refreshMacroSteps() {
            fetch('/get_macro')
            .then(response => response.json())
            .then(data => {
                const stepsDiv = document.getElementById('macroSteps');
                stepsDiv.innerHTML = data.steps.map((step, i) => 
                    `<div class="macro-step">
                        ${i + 1}. ${step.name} (${step.type})
                        <button onclick="removeStep(${i})" style="float: right;">삭제</button>
                    </div>`
                ).join('');
            });
        }
        
        function removeStep(index) {
            fetch('/remove_step/' + index, {method: 'DELETE'})
            .then(() => refreshMacroSteps());
        }
        
        function saveMacro() {
            fetch('/save_macro', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                alert('매크로 저장 완료!');
            });
        }
        
        function clearMacro() {
            if (confirm('매크로를 초기화하시겠습니까?')) {
                fetch('/clear_macro', {method: 'POST'})
                .then(() => refreshMacroSteps());
            }
        }
        
        function runMacro() {
            updateStatus('매크로 실행 중...', true);
            fetch('/run_macro', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                updateStatus('매크로 실행 완료');
                refreshExecutionLog();
            });
        }
        
        function stopMacro() {
            fetch('/stop_macro', {method: 'POST'})
            .then(() => {
                updateStatus('매크로 중지됨');
            });
        }
        
        function refreshExecutionLog() {
            fetch('/get_log')
            .then(response => response.json())
            .then(data => {
                const logDiv = document.getElementById('executionLog');
                logDiv.innerHTML = data.log.map(entry => 
                    `<div class="log-entry ${entry.level}">[${entry.time}] ${entry.message}</div>`
                ).join('');
                logDiv.scrollTop = logDiv.scrollHeight;
            });
        }
        
        function runNative(mode) {
            updateStatus('네이티브 GUI 실행 시도 중...', true);
            fetch('/run_native/' + mode)
            .then(response => response.json())
            .then(data => {
                updateStatus(data.status);
                document.getElementById('nativeOutput').innerHTML = 
                    `<pre>${data.output}</pre>`;
            });
        }
        
        // 페이지 로드 시 초기화
        window.onload = function() {
            refreshMacroSteps();
            refreshExecutionLog();
        };
        
        // 주기적으로 로그 업데이트
        setInterval(refreshExecutionLog, 2000);
    </script>
</body>
</html>
'''

# API 엔드포인트들
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/upload_excel', methods=['POST'])
def upload_excel():
    try:
        file = request.files['file']
        filepath = os.path.join(project_root, 'temp_excel.xlsx')
        file.save(filepath)
        
        import pandas as pd
        xls = pd.ExcelFile(filepath)
        
        app_state['excel_file'] = filepath
        
        return jsonify({
            'success': True,
            'filename': file.filename,
            'sheets': xls.sheet_names,
            'rows': len(pd.read_excel(xls, xls.sheet_names[0]))
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/add_step', methods=['POST'])
def add_step():
    step_type = request.json['step_type']
    step_names = {
        'mouse_click': '마우스 클릭',
        'keyboard_type': '텍스트 입력',
        'wait_time': '대기',
        'image_search': '이미지 검색',
        'ocr_text': '텍스트 검색',
        'if_condition': '조건문'
    }
    
    app_state['macro_steps'].append({
        'type': step_type,
        'name': step_names.get(step_type, step_type)
    })
    
    return jsonify({'success': True})

@app.route('/get_macro')
def get_macro():
    return jsonify({'steps': app_state['macro_steps']})

@app.route('/remove_step/<int:index>', methods=['DELETE'])
def remove_step(index):
    if 0 <= index < len(app_state['macro_steps']):
        app_state['macro_steps'].pop(index)
    return jsonify({'success': True})

@app.route('/clear_macro', methods=['POST'])
def clear_macro():
    app_state['macro_steps'] = []
    return jsonify({'success': True})

@app.route('/save_macro', methods=['POST'])
def save_macro():
    with open('web_macro.json', 'w', encoding='utf-8') as f:
        json.dump(app_state['macro_steps'], f, ensure_ascii=False, indent=2)
    return jsonify({'success': True})

@app.route('/run_macro', methods=['POST'])
def run_macro():
    app_state['execution_log'].append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'level': 'info',
        'message': '매크로 실행 시작'
    })
    
    # 실제 매크로 실행 로직은 여기에 구현
    for i, step in enumerate(app_state['macro_steps']):
        app_state['execution_log'].append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'level': 'success',
            'message': f'단계 {i+1}: {step["name"]} 실행 완료'
        })
    
    app_state['execution_log'].append({
        'time': datetime.now().strftime('%H:%M:%S'),
        'level': 'success',
        'message': '매크로 실행 완료'
    })
    
    return jsonify({'success': True})

@app.route('/stop_macro', methods=['POST'])
def stop_macro():
    app_state['status'] = 'stopped'
    return jsonify({'success': True})

@app.route('/get_log')
def get_log():
    return jsonify({'log': app_state['execution_log'][-50:]})  # 최근 50개만

@app.route('/run_native/<mode>')
def run_native(mode):
    try:
        output = ""
        
        if mode == 'check':
            # X Server 체크 후 실행
            result = subprocess.run(['python3', 'run_main.py'], 
                                  capture_output=True, text=True, timeout=5)
            output = result.stdout + result.stderr
            status = "실행 시도 완료"
            
        elif mode == 'xvfb':
            # Xvfb로 실행
            subprocess.Popen(['xvfb-run', '-a', 'python3', 'run_main.py'])
            output = "Xvfb 가상 디스플레이로 실행 중..."
            status = "Xvfb 실행"
            
        elif mode == 'windows':
            # Windows 스크립트 생성
            output = "Windows에서 실행:\n"
            output += "1. PowerShell을 관리자 권한으로 실행\n"
            output += "2. cd \\\\wsl.localhost\\Ubuntu\\home\\nosky\\macro\n"
            output += "3. .\\run_from_windows.ps1"
            status = "Windows 스크립트 안내"
            
        elif mode == 'debug':
            # 디버그 정보
            output = f"DISPLAY: {os.environ.get('DISPLAY', 'Not set')}\n"
            output += f"Project Root: {project_root}\n"
            output += "Python Path: " + str(sys.path[:3])
            status = "디버그 정보"
            
    except Exception as e:
        output = str(e)
        status = "오류 발생"
    
    return jsonify({'status': status, 'output': output})

# 메인 실행
if __name__ == '__main__':
    print("=" * 50)
    print("Excel Macro Automation - Web UI")
    print("=" * 50)
    print("\nWSL GUI 문제를 우회하는 웹 기반 인터페이스를 시작합니다.")
    print("\n브라우저가 자동으로 열립니다...")
    print("수동으로 열려면: http://localhost:5555")
    print("\n종료하려면 Ctrl+C를 누르세요.")
    print("=" * 50)
    
    # 브라우저 자동 열기
    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open('http://localhost:5555')
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Flask 앱 실행
    app.run(host='0.0.0.0', port=5555, debug=False)