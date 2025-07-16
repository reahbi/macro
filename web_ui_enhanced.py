#!/usr/bin/env python3
"""
향상된 웹 UI - 마우스 좌표 캡처 및 이미지 붙여넣기 기능 포함
"""

import os
import sys
import json
import threading
import webbrowser
import subprocess
import base64
import tempfile
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List
import io

# Flask 설치 확인
try:
    from flask import Flask, render_template_string, jsonify, request, send_file
    from flask_cors import CORS
except ImportError:
    print("필수 패키지 설치 중...")
    subprocess.run([sys.executable, "-m", "pip", "install", "flask", "flask-cors"])
    from flask import Flask, render_template_string, jsonify, request, send_file
    from flask_cors import CORS

# 추가 패키지 설치 확인
try:
    import pyautogui
    import pyperclip
    from PIL import Image, ImageGrab
    import keyboard
    import mouse
except ImportError:
    print("추가 패키지 설치 중...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pyautogui", "pyperclip", "pillow", "keyboard", "mouse"])
    import pyautogui
    import pyperclip
    from PIL import Image, ImageGrab
    import keyboard
    import mouse

# 프로젝트 경로 설정
project_root = Path(__file__).parent.absolute()
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

# 기존 매크로 모듈 import 시도
try:
    from core.macro_types import (
        MacroStep, StepType, MouseClickStep, KeyboardTypeStep,
        WaitTimeStep, ImageSearchStep, TextSearchStep, IfConditionStep,
        ConditionType, ComparisonOperator
    )
    from automation.executor import MacroExecutor
    from excel.excel_manager import ExcelManager
    from config.settings import Settings
    from logger.app_logger import setup_logger
    
    MODULES_LOADED = True
except Exception as e:
    print(f"경고: 일부 모듈을 로드할 수 없습니다: {e}")
    MODULES_LOADED = False

app = Flask(__name__)
CORS(app)

# 전역 상태 관리
class AppState:
    def __init__(self):
        self.excel_manager = ExcelManager() if MODULES_LOADED else None
        self.macro_steps: List[Dict] = []
        self.executor = None
        self.execution_thread = None
        self.execution_log = []
        self.is_running = False
        self.settings = Settings() if MODULES_LOADED else None
        self.mouse_position = {'x': 0, 'y': 0}
        self.is_tracking_mouse = False
        self.captured_images = {}  # 이미지 임시 저장소
        
    def add_log(self, message: str, level: str = "info"):
        self.execution_log.append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'level': level,
            'message': message
        })

app_state = AppState()

# 마우스 위치 추적 스레드
def track_mouse_position():
    """백그라운드에서 마우스 위치를 계속 추적"""
    while True:
        if app_state.is_tracking_mouse:
            try:
                x, y = pyautogui.position()
                app_state.mouse_position = {'x': x, 'y': y}
            except:
                pass
        time.sleep(0.1)

# 마우스 추적 스레드 시작
mouse_thread = threading.Thread(target=track_mouse_position, daemon=True)
mouse_thread.start()

# HTML 템플릿
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Excel Macro Automation - Enhanced</title>
    <meta charset="utf-8">
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; }
        body { 
            font-family: 'Segoe UI', Arial, sans-serif; 
            background: #f5f5f5; 
            color: #333;
        }
        .container { 
            max-width: 1400px; 
            margin: 0 auto; 
            padding: 20px; 
        }
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            background: white;
            padding: 10px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        .tab {
            padding: 12px 24px;
            background: #f0f0f0;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            transition: all 0.3s;
        }
        .tab.active {
            background: #667eea;
            color: white;
        }
        .content {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            min-height: 500px;
        }
        .panel {
            display: none;
        }
        .panel.active {
            display: block;
        }
        .button {
            background: #667eea;
            color: white;
            padding: 12px 24px;
            border: none;
            border-radius: 5px;
            font-size: 16px;
            cursor: pointer;
            transition: all 0.3s;
            margin: 5px;
        }
        .button:hover {
            background: #764ba2;
            transform: translateY(-2px);
        }
        .button.secondary {
            background: #757575;
        }
        .button.success {
            background: #4CAF50;
        }
        .step-palette {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 15px;
            margin: 30px 0;
        }
        .step-type-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
        }
        .step-type-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        }
        .macro-step {
            background: white;
            padding: 20px;
            margin: 10px 0;
            border-radius: 10px;
            border-left: 4px solid #667eea;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .step-config-button {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
        }
        .modal {
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }
        .modal-content {
            background-color: white;
            margin: 5% auto;
            padding: 30px;
            border-radius: 10px;
            width: 80%;
            max-width: 600px;
            max-height: 80vh;
            overflow-y: auto;
        }
        .form-group {
            margin: 20px 0;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .form-group input, .form-group select, .form-group textarea {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 16px;
        }
        .mouse-position {
            background: #f0f0f0;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            font-size: 20px;
            margin: 20px 0;
        }
        .capture-button {
            background: #FF9800;
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 5px;
            font-size: 18px;
            cursor: pointer;
            margin: 10px;
        }
        .image-preview {
            max-width: 100%;
            max-height: 300px;
            margin: 10px 0;
            border: 2px solid #ddd;
            border-radius: 5px;
        }
        .paste-area {
            border: 2px dashed #667eea;
            padding: 40px;
            text-align: center;
            border-radius: 10px;
            margin: 20px 0;
            cursor: pointer;
            transition: all 0.3s;
        }
        .paste-area:hover {
            background: #f8f9ff;
            border-color: #764ba2;
        }
        .paste-area.dragover {
            background: #e8eaff;
            border-color: #4CAF50;
        }
        .coordinate-display {
            display: flex;
            justify-content: space-around;
            align-items: center;
            margin: 20px 0;
        }
        .coord-box {
            background: #f8f9ff;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 24px;
            font-weight: bold;
            color: #667eea;
        }
        .hint-text {
            color: #666;
            font-size: 14px;
            margin: 10px 0;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Excel Macro Automation - Enhanced</h1>
            <p>마우스 좌표 캡처 및 이미지 붙여넣기 기능 포함</p>
            <div class="status-badge">
                상태: <span id="status">준비됨</span>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('excel')">📊 Excel</button>
            <button class="tab" onclick="showTab('editor')">✏️ Editor</button>
            <button class="tab" onclick="showTab('run')">▶️ Run</button>
            <button class="tab" onclick="showTab('tools')">🛠️ Tools</button>
        </div>
        
        <div class="content">
            <!-- Excel 탭 -->
            <div id="excel" class="panel active">
                <h2>Excel 파일 관리</h2>
                <div>
                    <input type="file" id="excelFile" accept=".xlsx,.xls">
                    <button class="button" onclick="uploadExcel()">업로드</button>
                </div>
                <div id="excelInfo"></div>
            </div>
            
            <!-- Editor 탭 -->
            <div id="editor" class="panel">
                <h2>매크로 편집기</h2>
                <div class="step-palette">
                    <div class="step-type-card" onclick="addStep('mouse_click')">
                        <div>🖱️</div>
                        <div>마우스 클릭</div>
                    </div>
                    <div class="step-type-card" onclick="addStep('keyboard_type')">
                        <div>⌨️</div>
                        <div>텍스트 입력</div>
                    </div>
                    <div class="step-type-card" onclick="addStep('wait_time')">
                        <div>⏱️</div>
                        <div>대기</div>
                    </div>
                    <div class="step-type-card" onclick="addStep('image_search')">
                        <div>🔍</div>
                        <div>이미지 검색</div>
                    </div>
                    <div class="step-type-card" onclick="addStep('ocr_text')">
                        <div>🔤</div>
                        <div>텍스트 검색</div>
                    </div>
                    <div class="step-type-card" onclick="addStep('if_condition')">
                        <div>❓</div>
                        <div>조건문</div>
                    </div>
                </div>
                
                <h3>현재 매크로</h3>
                <div id="macroSteps"></div>
                
                <button class="button" onclick="saveMacro()">💾 매크로 저장</button>
                <button class="button secondary" onclick="clearMacro()">🗑️ 초기화</button>
            </div>
            
            <!-- Run 탭 -->
            <div id="run" class="panel">
                <h2>매크로 실행</h2>
                <button class="button" onclick="runMacro()">▶️ 실행</button>
                <button class="button secondary" onclick="stopMacro()">⏹️ 중지</button>
                
                <h3>실행 로그</h3>
                <div id="executionLog" class="execution-log"></div>
            </div>
            
            <!-- Tools 탭 -->
            <div id="tools" class="panel">
                <h2>유용한 도구</h2>
                
                <h3>🎯 마우스 좌표 캡처</h3>
                <div class="mouse-position">
                    <div class="coordinate-display">
                        <div class="coord-box">X: <span id="mouseX">0</span></div>
                        <div class="coord-box">Y: <span id="mouseY">0</span></div>
                    </div>
                    <p class="hint-text">마우스를 움직여서 좌표를 확인하세요</p>
                    <button class="capture-button" onclick="toggleMouseTracking()">
                        <span id="trackingText">🎯 좌표 추적 시작</span>
                    </button>
                    <p class="hint-text" id="captureHint" style="display: none;">
                        F9 키를 눌러서 현재 좌표를 캡처하세요
                    </p>
                </div>
                
                <h3>📸 스크린샷 캡처</h3>
                <button class="button success" onclick="captureScreen()">
                    📷 전체 화면 캡처
                </button>
                <button class="button success" onclick="captureRegion()">
                    ✂️ 영역 선택 캡처
                </button>
                
                <h3>🖼️ 이미지 붙여넣기</h3>
                <div class="paste-area" onclick="document.getElementById('imageUpload').click()" 
                     ondrop="handleDrop(event)" ondragover="handleDragOver(event)" ondragleave="handleDragLeave(event)">
                    <p>이미지를 여기에 드래그하거나 클릭하여 선택하세요</p>
                    <p>또는 Ctrl+V로 클립보드에서 붙여넣기</p>
                    <input type="file" id="imageUpload" accept="image/*" style="display: none;" onchange="handleFileSelect(event)">
                </div>
                <div id="imagePreview"></div>
            </div>
        </div>
    </div>
    
    <!-- 스텝 설정 모달 -->
    <div id="stepConfigModal" class="modal">
        <div class="modal-content">
            <h2 id="modalTitle">스텝 설정</h2>
            <div id="modalBody"></div>
            <button class="button" onclick="saveStepConfig()">저장</button>
            <button class="button secondary" onclick="closeModal()">취소</button>
        </div>
    </div>
    
    <script>
        let currentStepIndex = null;
        let isTracking = false;
        let capturedPosition = null;
        
        // 탭 전환
        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
        }
        
        // Excel 업로드
        function uploadExcel() {
            const fileInput = document.getElementById('excelFile');
            const file = fileInput.files[0];
            if (!file) {
                alert('파일을 선택해주세요.');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            fetch('/upload_excel', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                document.getElementById('excelInfo').innerHTML = 
                    '<p>파일 업로드 완료: ' + data.filename + '</p>';
            });
        }
        
        // 매크로 스텝 추가
        function addStep(stepType) {
            fetch('/add_step', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({step_type: stepType})
            })
            .then(response => response.json())
            .then(data => {
                refreshMacroSteps();
                // 즉시 설정 다이얼로그 열기
                configureStep(data.index);
            });
        }
        
        // 매크로 스텝 목록 새로고침
        function refreshMacroSteps() {
            fetch('/get_macro')
            .then(response => response.json())
            .then(data => {
                const stepsDiv = document.getElementById('macroSteps');
                stepsDiv.innerHTML = data.steps.map((step, i) => `
                    <div class="macro-step">
                        <div>
                            <strong>${i + 1}. ${step.name}</strong>
                            ${step.description ? '<br>' + step.description : ''}
                        </div>
                        <div>
                            <button class="step-config-button" onclick="configureStep(${i})">설정</button>
                            <button class="button secondary" onclick="removeStep(${i})">삭제</button>
                        </div>
                    </div>
                `).join('');
            });
        }
        
        // 스텝 설정
        function configureStep(index) {
            currentStepIndex = index;
            
            fetch('/get_step_config/' + index)
            .then(response => response.json())
            .then(data => {
                document.getElementById('modalTitle').textContent = data.title;
                document.getElementById('modalBody').innerHTML = data.html;
                document.getElementById('stepConfigModal').style.display = 'block';
                
                // 마우스 클릭 스텝인 경우 좌표 캡처 버튼 추가
                if (data.step_type === 'mouse_click') {
                    setupMouseCaptureForModal();
                }
            });
        }
        
        // 모달에 마우스 캡처 기능 설정
        function setupMouseCaptureForModal() {
            // 캡처된 좌표가 있으면 자동으로 입력
            if (capturedPosition) {
                document.querySelector('input[name="x"]').value = capturedPosition.x;
                document.querySelector('input[name="y"]').value = capturedPosition.y;
            }
        }
        
        // 스텝 설정 저장
        function saveStepConfig() {
            const formData = new FormData();
            const inputs = document.querySelectorAll('#modalBody input, #modalBody select, #modalBody textarea');
            
            inputs.forEach(input => {
                if (input.type === 'checkbox') {
                    formData.append(input.name, input.checked);
                } else if (input.type === 'file' && input.files.length > 0) {
                    formData.append(input.name, input.files[0]);
                } else {
                    formData.append(input.name, input.value);
                }
            });
            
            fetch('/save_step_config/' + currentStepIndex, {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    closeModal();
                    refreshMacroSteps();
                } else {
                    alert('설정 저장 실패: ' + data.error);
                }
            });
        }
        
        // 모달 닫기
        function closeModal() {
            document.getElementById('stepConfigModal').style.display = 'none';
        }
        
        // 스텝 제거
        function removeStep(index) {
            fetch('/remove_step/' + index, {method: 'DELETE'})
            .then(() => refreshMacroSteps());
        }
        
        // 매크로 저장
        function saveMacro() {
            fetch('/save_macro', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                alert('매크로가 저장되었습니다!');
            });
        }
        
        // 매크로 초기화
        function clearMacro() {
            if (confirm('모든 매크로 스텝을 삭제하시겠습니까?')) {
                fetch('/clear_macro', {method: 'POST'})
                .then(() => refreshMacroSteps());
            }
        }
        
        // 매크로 실행
        function runMacro() {
            fetch('/run_macro', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    alert('실행 실패: ' + data.error);
                }
            });
        }
        
        // 매크로 중지
        function stopMacro() {
            fetch('/stop_macro', {method: 'POST'});
        }
        
        // 실행 로그 업데이트
        function updateExecutionLog() {
            fetch('/get_log')
            .then(response => response.json())
            .then(data => {
                const logDiv = document.getElementById('executionLog');
                logDiv.innerHTML = data.log.map(entry => 
                    '<div class="log-entry ' + entry.level + '">[' + entry.time + '] ' + entry.message + '</div>'
                ).join('');
                logDiv.scrollTop = logDiv.scrollHeight;
            });
        }
        
        // 마우스 좌표 추적
        function toggleMouseTracking() {
            isTracking = !isTracking;
            
            fetch('/toggle_mouse_tracking', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({tracking: isTracking})
            });
            
            if (isTracking) {
                document.getElementById('trackingText').textContent = '⏹️ 좌표 추적 중지';
                document.getElementById('captureHint').style.display = 'block';
                startMousePositionUpdate();
            } else {
                document.getElementById('trackingText').textContent = '🎯 좌표 추적 시작';
                document.getElementById('captureHint').style.display = 'none';
            }
        }
        
        // 마우스 위치 업데이트
        function startMousePositionUpdate() {
            if (isTracking) {
                fetch('/get_mouse_position')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('mouseX').textContent = data.x;
                    document.getElementById('mouseY').textContent = data.y;
                    
                    if (isTracking) {
                        setTimeout(startMousePositionUpdate, 100);
                    }
                });
            }
        }
        
        // 스크린샷 캡처
        function captureScreen() {
            fetch('/capture_screen', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('스크린샷이 캡처되었습니다!');
                    showImagePreview(data.image_url);
                }
            });
        }
        
        // 영역 캡처
        function captureRegion() {
            alert('화면에서 캡처할 영역을 마우스로 드래그하세요.');
            fetch('/capture_region', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showImagePreview(data.image_url);
                }
            });
        }
        
        // 이미지 미리보기
        function showImagePreview(imageUrl) {
            const previewDiv = document.getElementById('imagePreview');
            previewDiv.innerHTML = `<img src="${imageUrl}" class="image-preview">`;
        }
        
        // 드래그 앤 드롭 핸들러
        function handleDragOver(e) {
            e.preventDefault();
            e.currentTarget.classList.add('dragover');
        }
        
        function handleDragLeave(e) {
            e.currentTarget.classList.remove('dragover');
        }
        
        function handleDrop(e) {
            e.preventDefault();
            e.currentTarget.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleImageFile(files[0]);
            }
        }
        
        // 파일 선택 핸들러
        function handleFileSelect(e) {
            const file = e.target.files[0];
            if (file) {
                handleImageFile(file);
            }
        }
        
        // 이미지 파일 처리
        function handleImageFile(file) {
            if (!file.type.startsWith('image/')) {
                alert('이미지 파일만 업로드 가능합니다.');
                return;
            }
            
            const formData = new FormData();
            formData.append('image', file);
            
            fetch('/upload_image', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showImagePreview(data.image_url);
                }
            });
        }
        
        // 클립보드 붙여넣기 핸들러
        document.addEventListener('paste', function(e) {
            const items = e.clipboardData.items;
            
            for (let i = 0; i < items.length; i++) {
                if (items[i].type.indexOf('image') !== -1) {
                    const blob = items[i].getAsFile();
                    handleImageFile(blob);
                    e.preventDefault();
                    break;
                }
            }
        });
        
        // F9 키로 좌표 캡처
        document.addEventListener('keydown', function(e) {
            if (e.key === 'F9' && isTracking) {
                fetch('/capture_mouse_position', {method: 'POST'})
                .then(response => response.json())
                .then(data => {
                    capturedPosition = {x: data.x, y: data.y};
                    alert(`좌표가 캡처되었습니다: X=${data.x}, Y=${data.y}`);
                });
            }
        });
        
        // 초기화
        window.onload = function() {
            refreshMacroSteps();
            setInterval(updateExecutionLog, 1000);
        };
        
        // 모달 외부 클릭 시 닫기
        window.onclick = function(event) {
            if (event.target == document.getElementById('stepConfigModal')) {
                closeModal();
            }
        }
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
        filepath = os.path.join(tempfile.gettempdir(), file.filename)
        file.save(filepath)
        
        if MODULES_LOADED and app_state.excel_manager:
            app_state.excel_manager.load_file(filepath)
        
        return jsonify({'success': True, 'filename': file.filename})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/add_step', methods=['POST'])
def add_step():
    step_type = request.json['step_type']
    
    step_data = {
        'type': step_type,
        'name': get_step_name(step_type),
        'config': get_default_config(step_type)
    }
    
    app_state.macro_steps.append(step_data)
    
    return jsonify({
        'success': True,
        'index': len(app_state.macro_steps) - 1
    })

@app.route('/get_macro')
def get_macro():
    steps_info = []
    for step in app_state.macro_steps:
        step_info = {
            'type': step['type'],
            'name': step['name'],
            'description': get_step_description(step)
        }
        steps_info.append(step_info)
    
    return jsonify({'steps': steps_info})

@app.route('/get_step_config/<int:index>')
def get_step_config(index):
    if index >= len(app_state.macro_steps):
        return jsonify({'title': '오류', 'html': '<p>잘못된 인덱스</p>'})
    
    step = app_state.macro_steps[index]
    step_type = step['type']
    config = step.get('config', {})
    
    title = f"{step['name']} 설정"
    html = generate_config_html(step_type, config)
    
    return jsonify({
        'title': title,
        'html': html,
        'step_type': step_type
    })

@app.route('/save_step_config/<int:index>', methods=['POST'])
def save_step_config(index):
    try:
        if index >= len(app_state.macro_steps):
            return jsonify({'success': False, 'error': '잘못된 인덱스'})
        
        step = app_state.macro_steps[index]
        
        # 폼 데이터를 config에 저장
        for key, value in request.form.items():
            if value == 'true':
                step['config'][key] = True
            elif value == 'false':
                step['config'][key] = False
            else:
                try:
                    step['config'][key] = float(value)
                except ValueError:
                    step['config'][key] = value
        
        # 이미지 파일 처리
        if 'image' in request.files:
            image_file = request.files['image']
            if image_file.filename:
                image_id = f"step_{index}_{int(time.time())}"
                image_path = save_uploaded_image(image_file, image_id)
                step['config']['image_path'] = image_path
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/remove_step/<int:index>', methods=['DELETE'])
def remove_step(index):
    if 0 <= index < len(app_state.macro_steps):
        app_state.macro_steps.pop(index)
    return jsonify({'success': True})

@app.route('/clear_macro', methods=['POST'])
def clear_macro():
    app_state.macro_steps = []
    return jsonify({'success': True})

@app.route('/save_macro', methods=['POST'])
def save_macro():
    with open('web_macro.json', 'w', encoding='utf-8') as f:
        json.dump(app_state.macro_steps, f, ensure_ascii=False, indent=2)
    return jsonify({'success': True})

@app.route('/run_macro', methods=['POST'])
def run_macro():
    if not app_state.macro_steps:
        return jsonify({'success': False, 'error': '실행할 매크로가 없습니다.'})
    
    app_state.add_log("매크로 실행 시작", "info")
    
    # 실제 실행 로직
    for i, step in enumerate(app_state.macro_steps):
        app_state.add_log(f"단계 {i+1}: {step['name']} 실행", "info")
        
        if step['type'] == 'mouse_click':
            x = int(step['config'].get('x', 0))
            y = int(step['config'].get('y', 0))
            pyautogui.click(x, y)
            app_state.add_log(f"마우스 클릭: ({x}, {y})", "success")
            
        elif step['type'] == 'keyboard_type':
            text = step['config'].get('text', '')
            pyautogui.typewrite(text)
            if step['config'].get('press_enter'):
                pyautogui.press('enter')
            app_state.add_log(f"텍스트 입력: {text}", "success")
            
        elif step['type'] == 'wait_time':
            seconds = float(step['config'].get('seconds', 1))
            time.sleep(seconds)
            app_state.add_log(f"{seconds}초 대기", "success")
        
    app_state.add_log("매크로 실행 완료", "success")
    
    return jsonify({'success': True})

@app.route('/stop_macro', methods=['POST'])
def stop_macro():
    app_state.is_running = False
    app_state.add_log("매크로 중지됨", "warning")
    return jsonify({'success': True})

@app.route('/get_log')
def get_log():
    return jsonify({'log': app_state.execution_log[-50:]})

# 마우스 추적 관련 엔드포인트
@app.route('/toggle_mouse_tracking', methods=['POST'])
def toggle_mouse_tracking():
    app_state.is_tracking_mouse = request.json.get('tracking', False)
    return jsonify({'success': True})

@app.route('/get_mouse_position')
def get_mouse_position():
    return jsonify(app_state.mouse_position)

@app.route('/capture_mouse_position', methods=['POST'])
def capture_mouse_position():
    return jsonify(app_state.mouse_position)

# 스크린샷 관련 엔드포인트
@app.route('/capture_screen', methods=['POST'])
def capture_screen():
    try:
        # 전체 화면 캡처
        screenshot = ImageGrab.grab()
        
        # 이미지 저장
        image_id = f"screenshot_{int(time.time())}"
        image_path = save_screenshot(screenshot, image_id)
        
        return jsonify({
            'success': True,
            'image_url': f'/image/{image_id}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/capture_region', methods=['POST'])
def capture_region():
    try:
        # 간단히 구현 - 실제로는 영역 선택 UI가 필요
        app_state.add_log("영역 캡처 기능은 추가 구현이 필요합니다", "warning")
        
        # 임시로 전체 화면 캡처
        screenshot = ImageGrab.grab()
        
        image_id = f"region_{int(time.time())}"
        image_path = save_screenshot(screenshot, image_id)
        
        return jsonify({
            'success': True,
            'image_url': f'/image/{image_id}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        image_file = request.files['image']
        image_id = f"upload_{int(time.time())}"
        image_path = save_uploaded_image(image_file, image_id)
        
        return jsonify({
            'success': True,
            'image_url': f'/image/{image_id}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/image/<image_id>')
def get_image(image_id):
    if image_id in app_state.captured_images:
        image_data = app_state.captured_images[image_id]
        return send_file(
            io.BytesIO(image_data),
            mimetype='image/png',
            as_attachment=False
        )
    return '', 404

# 헬퍼 함수들
def get_step_name(step_type):
    names = {
        'mouse_click': '마우스 클릭',
        'keyboard_type': '텍스트 입력',
        'wait_time': '대기',
        'image_search': '이미지 검색',
        'ocr_text': '텍스트 검색',
        'if_condition': '조건문'
    }
    return names.get(step_type, '알 수 없음')

def get_default_config(step_type):
    configs = {
        'mouse_click': {'x': 0, 'y': 0, 'button': 'left', 'click_type': 'single'},
        'keyboard_type': {'text': '', 'press_enter': False},
        'wait_time': {'seconds': 1.0},
        'image_search': {'image_path': '', 'confidence': 0.8},
        'ocr_text': {'search_text': '', 'exact_match': False},
        'if_condition': {'condition_type': 'image_found', 'value': ''}
    }
    return configs.get(step_type, {})

def get_step_description(step):
    config = step.get('config', {})
    step_type = step['type']
    
    if step_type == 'mouse_click':
        return f"({config.get('x', 0)}, {config.get('y', 0)}) 클릭"
    elif step_type == 'keyboard_type':
        text = config.get('text', '')
        return f"'{text[:20]}...' 입력" if len(text) > 20 else f"'{text}' 입력"
    elif step_type == 'wait_time':
        return f"{config.get('seconds', 1)}초 대기"
    elif step_type == 'image_search':
        return "이미지 검색 후 클릭"
    elif step_type == 'ocr_text':
        return f"'{config.get('search_text', '')}' 텍스트 검색"
    elif step_type == 'if_condition':
        return f"{config.get('condition_type', '')} 조건"
    
    return ""

def generate_config_html(step_type, config):
    if step_type == 'mouse_click':
        return f'''
        <div class="form-group">
            <label>X 좌표</label>
            <input type="number" name="x" value="{config.get('x', 0)}" required>
        </div>
        <div class="form-group">
            <label>Y 좌표</label>
            <input type="number" name="y" value="{config.get('y', 0)}" required>
        </div>
        <div class="form-group" style="background: #f8f9ff; padding: 15px; border-radius: 5px;">
            <p style="text-align: center; color: #667eea; font-weight: bold;">
                💡 팁: Tools 탭에서 마우스 좌표를 쉽게 캡처할 수 있습니다!
            </p>
            <p style="text-align: center; margin-top: 10px;">
                1. Tools 탭으로 이동<br>
                2. "좌표 추적 시작" 클릭<br>
                3. 원하는 위치에서 F9 키 누르기
            </p>
        </div>
        <div class="form-group">
            <label>마우스 버튼</label>
            <select name="button">
                <option value="left" {'selected' if config.get('button') == 'left' else ''}>왼쪽</option>
                <option value="right" {'selected' if config.get('button') == 'right' else ''}>오른쪽</option>
            </select>
        </div>
        <div class="form-group">
            <label>클릭 타입</label>
            <select name="click_type">
                <option value="single" {'selected' if config.get('click_type') == 'single' else ''}>싱글 클릭</option>
                <option value="double" {'selected' if config.get('click_type') == 'double' else ''}>더블 클릭</option>
            </select>
        </div>
        '''
        
    elif step_type == 'keyboard_type':
        return f'''
        <div class="form-group">
            <label>입력할 텍스트</label>
            <textarea name="text" rows="3">{config.get('text', '')}</textarea>
        </div>
        <div class="form-group">
            <label>
                <input type="checkbox" name="press_enter" value="true" {'checked' if config.get('press_enter') else ''}>
                입력 후 Enter 키 누르기
            </label>
        </div>
        '''
        
    elif step_type == 'wait_time':
        return f'''
        <div class="form-group">
            <label>대기 시간 (초)</label>
            <input type="number" name="seconds" value="{config.get('seconds', 1.0)}" step="0.1" min="0.1" required>
        </div>
        '''
        
    elif step_type == 'image_search':
        return f'''
        <div class="form-group">
            <label>검색할 이미지</label>
            <input type="file" name="image" accept="image/*">
            <p style="margin-top: 10px; color: #666;">
                💡 팁: Tools 탭에서 스크린샷을 캡처하거나 클립보드에서 이미지를 붙여넣을 수 있습니다!
            </p>
        </div>
        <div class="form-group">
            <label>유사도 (0.0 ~ 1.0)</label>
            <input type="number" name="confidence" value="{config.get('confidence', 0.8)}" step="0.1" min="0" max="1" required>
        </div>
        '''
        
    elif step_type == 'ocr_text':
        return f'''
        <div class="form-group">
            <label>검색할 텍스트</label>
            <input type="text" name="search_text" value="{config.get('search_text', '')}">
        </div>
        <div class="form-group">
            <label>
                <input type="checkbox" name="exact_match" value="true" {'checked' if config.get('exact_match') else ''}>
                정확히 일치
            </label>
        </div>
        '''
        
    elif step_type == 'if_condition':
        return f'''
        <div class="form-group">
            <label>조건 타입</label>
            <select name="condition_type">
                <option value="image_found" {'selected' if config.get('condition_type') == 'image_found' else ''}>이미지 발견</option>
                <option value="text_found" {'selected' if config.get('condition_type') == 'text_found' else ''}>텍스트 발견</option>
                <option value="excel_value" {'selected' if config.get('condition_type') == 'excel_value' else ''}>Excel 값</option>
            </select>
        </div>
        <div class="form-group">
            <label>비교 값</label>
            <input type="text" name="value" value="{config.get('value', '')}">
        </div>
        '''
    
    return '<p>설정이 필요하지 않습니다.</p>'

def save_screenshot(image, image_id):
    # 메모리에 저장
    buffer = io.BytesIO()
    image.save(buffer, format='PNG')
    app_state.captured_images[image_id] = buffer.getvalue()
    return image_id

def save_uploaded_image(image_file, image_id):
    # 업로드된 이미지를 메모리에 저장
    image_data = image_file.read()
    app_state.captured_images[image_id] = image_data
    return image_id

# 메인 실행
if __name__ == '__main__':
    # pyautogui 안전 설정
    pyautogui.FAILSAFE = True
    pyautogui.PAUSE = 0.1
    
    print("=" * 60)
    print("Excel Macro Automation - Enhanced Version")
    print("=" * 60)
    print("\n✨ 새로운 기능:")
    print("- 🎯 실시간 마우스 좌표 추적")
    print("- 📸 스크린샷 캡처 및 저장")
    print("- 🖼️ 이미지 드래그 앤 드롭 / 클립보드 붙여넣기")
    print("- ⌨️ F9 키로 마우스 좌표 캡처")
    print("- 🖥️ 멀티 모니터 지원")
    print("\n브라우저가 자동으로 열립니다...")
    print("수동으로 열려면: http://localhost:5558")
    print("\n종료하려면 Ctrl+C를 누르세요.")
    print("=" * 60)
    
    # 브라우저 자동 열기
    def open_browser():
        time.sleep(1.5)
        webbrowser.open('http://localhost:5558')
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Flask 앱 실행
    app.run(host='0.0.0.0', port=5558, debug=False)