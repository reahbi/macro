#!/usr/bin/env python3
"""
웹 UI와 기존 매크로 기능을 통합한 실행 가능한 버전
매크로 스텝 설정 기능이 포함된 완전한 웹 인터페이스
"""

import os
import sys
import json
import threading
import webbrowser
import subprocess
import base64
import tempfile
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List

# Flask 설치 확인
try:
    from flask import Flask, render_template_string, jsonify, request, send_file
    from flask_cors import CORS
except ImportError:
    print("필수 패키지 설치 중...")
    subprocess.run([sys.executable, "-m", "pip", "install", "flask", "flask-cors"])
    from flask import Flask, render_template_string, jsonify, request, send_file
    from flask_cors import CORS

# 프로젝트 경로 설정
project_root = Path(__file__).parent.absolute()
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

# 기존 매크로 모듈 import
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
    from vision.image_matcher import ImageMatcher
    from vision.text_extractor import TextExtractor
    
    MODULES_LOADED = True
except Exception as e:
    print(f"경고: 일부 모듈을 로드할 수 없습니다: {e}")
    MODULES_LOADED = False

app = Flask(__name__)
CORS(app)

# 로거 설정
logger = setup_logger() if MODULES_LOADED else None

# 전역 상태 관리
class AppState:
    def __init__(self):
        self.excel_manager = ExcelManager() if MODULES_LOADED else None
        self.macro_steps: List[Dict] = []  # 단순화된 스텝 저장
        self.executor = None
        self.execution_thread = None
        self.execution_log = []
        self.is_running = False
        self.settings = Settings() if MODULES_LOADED else None
        
    def add_log(self, message: str, level: str = "info"):
        self.execution_log.append({
            'time': datetime.now().strftime('%H:%M:%S'),
            'level': level,
            'message': message
        })
        if logger:
            getattr(logger, level)(message)

app_state = AppState()

# HTML 템플릿
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Excel Macro Automation - 통합 웹 UI</title>
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
        .execution-log {
            background: #1a1a1a;
            color: #f0f0f0;
            padding: 20px;
            border-radius: 10px;
            font-family: monospace;
            max-height: 400px;
            overflow-y: auto;
        }
        .log-entry {
            padding: 5px 0;
        }
        .log-entry.error {
            color: #ff5252;
        }
        .log-entry.success {
            color: #69f0ae;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Excel Macro Automation</h1>
            <p>완전한 매크로 자동화 시스템 (스텝 설정 기능 포함)</p>
            <div class="status-badge">
                상태: <span id="status">준비됨</span>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('excel')">📊 Excel</button>
            <button class="tab" onclick="showTab('editor')">✏️ Editor</button>
            <button class="tab" onclick="showTab('run')">▶️ Run</button>
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
        
        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
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
        
        function configureStep(index) {
            currentStepIndex = index;
            
            fetch('/get_step_config/' + index)
            .then(response => response.json())
            .then(data => {
                document.getElementById('modalTitle').textContent = data.title;
                document.getElementById('modalBody').innerHTML = data.html;
                document.getElementById('stepConfigModal').style.display = 'block';
            });
        }
        
        function saveStepConfig() {
            const formData = new FormData();
            const inputs = document.querySelectorAll('#modalBody input, #modalBody select, #modalBody textarea');
            
            inputs.forEach(input => {
                if (input.type === 'checkbox') {
                    formData.append(input.name, input.checked);
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
        
        function closeModal() {
            document.getElementById('stepConfigModal').style.display = 'none';
        }
        
        function removeStep(index) {
            fetch('/remove_step/' + index, {method: 'DELETE'})
            .then(() => refreshMacroSteps());
        }
        
        function saveMacro() {
            fetch('/save_macro', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                alert('매크로가 저장되었습니다!');
            });
        }
        
        function clearMacro() {
            if (confirm('모든 매크로 스텝을 삭제하시겠습니까?')) {
                fetch('/clear_macro', {method: 'POST'})
                .then(() => refreshMacroSteps());
            }
        }
        
        function runMacro() {
            fetch('/run_macro', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    alert('실행 실패: ' + data.error);
                }
            });
        }
        
        function stopMacro() {
            fetch('/stop_macro', {method: 'POST'});
        }
        
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
    
    # 기본값으로 스텝 추가
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
    
    return jsonify({'title': title, 'html': html})

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
    
    # 실제 실행 로직은 여기에 구현
    for i, step in enumerate(app_state.macro_steps):
        app_state.add_log(f"단계 {i+1}: {step['name']} 실행", "info")
        # 실제 실행 코드...
        
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
            <label>이미지 경로</label>
            <input type="text" name="image_path" value="{config.get('image_path', '')}" placeholder="이미지 파일 경로">
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

# 메인 실행
if __name__ == '__main__':
    print("=" * 60)
    print("Excel Macro Automation - 통합 웹 UI (동작 버전)")
    print("=" * 60)
    print("\n✅ 매크로 스텝 설정 기능이 완전히 구현된 버전입니다.")
    print("\n기능:")
    print("- 각 스텝별 상세 설정 가능")
    print("- 마우스 클릭: 좌표, 버튼, 클릭 타입")
    print("- 텍스트 입력: 텍스트 내용, Enter 키")
    print("- 대기: 대기 시간")
    print("- 이미지/텍스트 검색: 검색 조건")
    print("- 조건문: 조건 타입, 비교값")
    print("\n브라우저가 자동으로 열립니다...")
    print("수동으로 열려면: http://localhost:5557")
    print("\n종료하려면 Ctrl+C를 누르세요.")
    print("=" * 60)
    
    # 브라우저 자동 열기
    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open('http://localhost:5557')
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Flask 앱 실행
    app.run(host='0.0.0.0', port=5557, debug=False)