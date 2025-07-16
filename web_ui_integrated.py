#!/usr/bin/env python3
"""
웹 UI와 기존 매크로 기능을 통합한 완전한 버전
실제 매크로 실행이 가능한 웹 인터페이스
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
        self.macro_steps: List[MacroStep] = []
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
    <title>Excel Macro Automation - Integrated Web UI</title>
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
        .header h1 {
            margin-bottom: 10px;
            font-size: 2.5em;
        }
        .status-badge {
            display: inline-block;
            padding: 5px 15px;
            background: rgba(255,255,255,0.2);
            border-radius: 20px;
            margin-top: 10px;
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
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .tab.active {
            background: #667eea;
            color: white;
        }
        .tab:hover {
            background: #764ba2;
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
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .button:hover {
            background: #764ba2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }
        .button.secondary {
            background: #757575;
        }
        .button.secondary:hover {
            background: #616161;
        }
        .button.danger {
            background: #f44336;
        }
        .button.danger:hover {
            background: #d32f2f;
        }
        .file-upload-area {
            border: 2px dashed #667eea;
            padding: 40px;
            text-align: center;
            border-radius: 10px;
            margin: 20px 0;
            transition: all 0.3s;
        }
        .file-upload-area:hover {
            background: #f8f9ff;
            border-color: #764ba2;
        }
        .excel-info {
            background: #f8f9ff;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
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
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        .step-type-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(0,0,0,0.2);
        }
        .step-type-card .icon {
            font-size: 2em;
            margin-bottom: 10px;
        }
        .macro-steps-container {
            background: #f8f9ff;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
            max-height: 400px;
            overflow-y: auto;
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
            transition: all 0.3s;
        }
        .macro-step:hover {
            transform: translateX(5px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .step-actions {
            display: flex;
            gap: 10px;
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
        .step-config-button:hover {
            background: #45a049;
        }
        .execution-log {
            background: #1a1a1a;
            color: #f0f0f0;
            padding: 20px;
            border-radius: 10px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
            max-height: 400px;
            overflow-y: auto;
            margin: 20px 0;
        }
        .log-entry {
            padding: 5px 0;
            border-bottom: 1px solid #333;
        }
        .log-entry.error {
            color: #ff5252;
        }
        .log-entry.success {
            color: #69f0ae;
        }
        .log-entry.warning {
            color: #ffd740;
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
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .close {
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }
        .close:hover {
            color: #000;
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
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-left: 10px;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .screenshot-preview {
            max-width: 100%;
            border: 1px solid #ddd;
            border-radius: 5px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Excel Macro Automation</h1>
            <p>완전히 통합된 웹 기반 매크로 자동화 시스템</p>
            <div class="status-badge">
                상태: <span id="status">준비됨</span>
                <span id="loading" class="loading" style="display: none;"></span>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="showTab('excel')">
                <span>📊</span> Excel
            </button>
            <button class="tab" onclick="showTab('editor')">
                <span>✏️</span> Editor
            </button>
            <button class="tab" onclick="showTab('run')">
                <span>▶️</span> Run
            </button>
            <button class="tab" onclick="showTab('settings')">
                <span>⚙️</span> Settings
            </button>
        </div>
        
        <div class="content">
            <!-- Excel 탭 -->
            <div id="excel" class="panel active">
                <h2>Excel 파일 관리</h2>
                <div class="file-upload-area">
                    <p>Excel 파일을 드래그하거나 클릭하여 업로드</p>
                    <input type="file" id="excelFile" accept=".xlsx,.xls" style="display: none;">
                    <button class="button" onclick="document.getElementById('excelFile').click()">
                        파일 선택
                    </button>
                </div>
                <div id="excelInfo" class="excel-info" style="display: none;">
                    <h3>로드된 Excel 파일</h3>
                    <div id="excelDetails"></div>
                    <div id="sheetSelector" style="margin-top: 20px;"></div>
                    <div id="dataPreview" style="margin-top: 20px;"></div>
                </div>
            </div>
            
            <!-- Editor 탭 -->
            <div id="editor" class="panel">
                <h2>매크로 편집기</h2>
                <div class="step-palette">
                    <div class="step-type-card" onclick="addStep('mouse_click')">
                        <div class="icon">🖱️</div>
                        <div>마우스 클릭</div>
                    </div>
                    <div class="step-type-card" onclick="addStep('keyboard_type')">
                        <div class="icon">⌨️</div>
                        <div>텍스트 입력</div>
                    </div>
                    <div class="step-type-card" onclick="addStep('wait_time')">
                        <div class="icon">⏱️</div>
                        <div>대기</div>
                    </div>
                    <div class="step-type-card" onclick="addStep('image_search')">
                        <div class="icon">🔍</div>
                        <div>이미지 검색</div>
                    </div>
                    <div class="step-type-card" onclick="addStep('ocr_text')">
                        <div class="icon">🔤</div>
                        <div>텍스트 검색</div>
                    </div>
                    <div class="step-type-card" onclick="addStep('if_condition')">
                        <div class="icon">❓</div>
                        <div>조건문</div>
                    </div>
                </div>
                
                <h3>현재 매크로</h3>
                <div id="macroSteps" class="macro-steps-container"></div>
                
                <div style="margin-top: 20px;">
                    <button class="button" onclick="saveMacro()">
                        <span>💾</span> 매크로 저장
                    </button>
                    <button class="button" onclick="loadMacro()">
                        <span>📁</span> 매크로 불러오기
                    </button>
                    <button class="button secondary" onclick="clearMacro()">
                        <span>🗑️</span> 초기화
                    </button>
                </div>
            </div>
            
            <!-- Run 탭 -->
            <div id="run" class="panel">
                <h2>매크로 실행</h2>
                <div style="margin: 20px 0;">
                    <button class="button" onclick="runMacro()" id="runButton">
                        <span>▶️</span> 실행
                    </button>
                    <button class="button danger" onclick="stopMacro()" id="stopButton" disabled>
                        <span>⏹️</span> 중지
                    </button>
                    <button class="button secondary" onclick="clearLog()">
                        <span>🧹</span> 로그 지우기
                    </button>
                </div>
                
                <h3>실행 로그</h3>
                <div id="executionLog" class="execution-log"></div>
                
                <div id="screenshotArea" style="margin-top: 20px; display: none;">
                    <h3>실행 스크린샷</h3>
                    <img id="screenshotImage" class="screenshot-preview">
                </div>
            </div>
            
            <!-- Settings 탭 -->
            <div id="settings" class="panel">
                <h2>설정</h2>
                <div class="form-group">
                    <label>실행 속도 (초)</label>
                    <input type="number" id="executionSpeed" value="1.0" step="0.1" min="0.1">
                </div>
                <div class="form-group">
                    <label>스크린샷 캡처</label>
                    <select id="screenshotCapture">
                        <option value="on_error">에러 발생 시만</option>
                        <option value="always">항상</option>
                        <option value="never">사용 안 함</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>로그 레벨</label>
                    <select id="logLevel">
                        <option value="info">정보</option>
                        <option value="debug">디버그</option>
                        <option value="error">에러만</option>
                    </select>
                </div>
                <button class="button" onclick="saveSettings()">
                    <span>💾</span> 설정 저장
                </button>
            </div>
        </div>
    </div>
    
    <!-- 스텝 설정 모달 -->
    <div id="stepConfigModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <h2 id="modalTitle">스텝 설정</h2>
            <div id="modalBody"></div>
            <div style="margin-top: 20px;">
                <button class="button" onclick="saveStepConfig()">저장</button>
                <button class="button secondary" onclick="closeModal()">취소</button>
            </div>
        </div>
    </div>
    
    <script>
        let currentTab = 'excel';
        let currentStepIndex = null;
        let macroSteps = [];
        
        // 탭 전환
        function showTab(tabName) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById(tabName).classList.add('active');
            currentTab = tabName;
        }
        
        // 상태 업데이트
        function updateStatus(status, loading = false) {
            document.getElementById('status').textContent = status;
            document.getElementById('loading').style.display = loading ? 'inline-block' : 'none';
        }
        
        // Excel 파일 업로드
        document.getElementById('excelFile').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (!file) return;
            
            const formData = new FormData();
            formData.append('file', file);
            
            updateStatus('Excel 파일 업로드 중...', true);
            
            fetch('/api/upload_excel', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateStatus('Excel 파일 로드 완료');
                    showExcelInfo(data);
                } else {
                    throw new Error(data.error);
                }
            })
            .catch(error => {
                updateStatus('오류 발생');
                alert('Excel 파일 로드 실패: ' + error.message);
            });
        });
        
        // Excel 정보 표시
        function showExcelInfo(data) {
            document.getElementById('excelInfo').style.display = 'block';
            document.getElementById('excelDetails').innerHTML = `
                <p><strong>파일명:</strong> ${data.filename}</p>
                <p><strong>시트:</strong> ${data.sheets.join(', ')}</p>
                <p><strong>데이터 행:</strong> ${data.total_rows}</p>
            `;
            
            // 시트 선택기
            const sheetSelector = document.getElementById('sheetSelector');
            sheetSelector.innerHTML = '<label>활성 시트: </label>' +
                '<select id="activeSheet" onchange="changeSheet()">' +
                data.sheets.map(sheet => 
                    `<option value="${sheet}" ${sheet === data.active_sheet ? 'selected' : ''}>${sheet}</option>`
                ).join('') +
                '</select>';
            
            // 데이터 미리보기
            if (data.preview) {
                showDataPreview(data.preview);
            }
        }
        
        // 데이터 미리보기 표시
        function showDataPreview(preview) {
            const previewDiv = document.getElementById('dataPreview');
            previewDiv.innerHTML = '<h4>데이터 미리보기 (처음 5행)</h4>' +
                '<table style="width: 100%; border-collapse: collapse;">' +
                '<thead><tr>' +
                preview.columns.map(col => `<th style="border: 1px solid #ddd; padding: 8px;">${col}</th>`).join('') +
                '</tr></thead><tbody>' +
                preview.data.map(row => 
                    '<tr>' + row.map(cell => `<td style="border: 1px solid #ddd; padding: 8px;">${cell || ''}</td>`).join('') + '</tr>'
                ).join('') +
                '</tbody></table>';
        }
        
        // 시트 변경
        function changeSheet() {
            const sheet = document.getElementById('activeSheet').value;
            fetch('/api/change_sheet', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({sheet: sheet})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success && data.preview) {
                    showDataPreview(data.preview);
                }
            });
        }
        
        // 매크로 스텝 추가
        function addStep(stepType) {
            fetch('/api/add_step', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({step_type: stepType})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    refreshMacroSteps();
                    // 즉시 설정 다이얼로그 열기
                    configureStep(data.index);
                }
            });
        }
        
        // 매크로 스텝 목록 새로고침
        function refreshMacroSteps() {
            fetch('/api/get_macro')
            .then(response => response.json())
            .then(data => {
                macroSteps = data.steps;
                const stepsDiv = document.getElementById('macroSteps');
                
                if (data.steps.length === 0) {
                    stepsDiv.innerHTML = '<p style="text-align: center; color: #999;">매크로 스텝이 없습니다. 위에서 추가해주세요.</p>';
                } else {
                    stepsDiv.innerHTML = data.steps.map((step, i) => 
                        `<div class="macro-step">
                            <div>
                                <strong>${i + 1}. ${step.name}</strong>
                                ${step.description ? `<br><small>${step.description}</small>` : ''}
                            </div>
                            <div class="step-actions">
                                <button class="step-config-button" onclick="configureStep(${i})">설정</button>
                                <button class="button secondary" style="padding: 8px 16px;" onclick="removeStep(${i})">삭제</button>
                            </div>
                        </div>`
                    ).join('');
                }
            });
        }
        
        // 스텝 설정
        function configureStep(index) {
            currentStepIndex = index;
            const step = macroSteps[index];
            
            document.getElementById('modalTitle').textContent = `${step.name} 설정`;
            
            fetch(`/api/get_step_config/${index}`)
            .then(response => response.json())
            .then(data => {
                document.getElementById('modalBody').innerHTML = data.html;
                document.getElementById('stepConfigModal').style.display = 'block';
            });
        }
        
        // 스텝 설정 저장
        function saveStepConfig() {
            const formData = new FormData();
            const inputs = document.querySelectorAll('#modalBody input, #modalBody select, #modalBody textarea');
            
            inputs.forEach(input => {
                if (input.type === 'file' && input.files.length > 0) {
                    formData.append(input.name, input.files[0]);
                } else {
                    formData.append(input.name, input.value);
                }
            });
            
            fetch(`/api/save_step_config/${currentStepIndex}`, {
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
            currentStepIndex = null;
        }
        
        // 스텝 제거
        function removeStep(index) {
            if (confirm('이 스텝을 삭제하시겠습니까?')) {
                fetch(`/api/remove_step/${index}`, {method: 'DELETE'})
                .then(() => refreshMacroSteps());
            }
        }
        
        // 매크로 저장
        function saveMacro() {
            const name = prompt('매크로 이름을 입력하세요:');
            if (!name) return;
            
            fetch('/api/save_macro', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({name: name})
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('매크로가 저장되었습니다!');
                }
            });
        }
        
        // 매크로 불러오기
        function loadMacro() {
            fetch('/api/list_macros')
            .then(response => response.json())
            .then(data => {
                if (data.macros.length === 0) {
                    alert('저장된 매크로가 없습니다.');
                    return;
                }
                
                const selected = prompt('불러올 매크로를 선택하세요:\\n' + 
                    data.macros.map((m, i) => `${i+1}. ${m}`).join('\\n'));
                
                if (selected && parseInt(selected) > 0 && parseInt(selected) <= data.macros.length) {
                    const macroName = data.macros[parseInt(selected) - 1];
                    
                    fetch(`/api/load_macro/${macroName}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            refreshMacroSteps();
                            alert('매크로를 불러왔습니다!');
                        }
                    });
                }
            });
        }
        
        // 매크로 초기화
        function clearMacro() {
            if (confirm('모든 매크로 스텝을 삭제하시겠습니까?')) {
                fetch('/api/clear_macro', {method: 'POST'})
                .then(() => refreshMacroSteps());
            }
        }
        
        // 매크로 실행
        function runMacro() {
            updateStatus('매크로 실행 중...', true);
            document.getElementById('runButton').disabled = true;
            document.getElementById('stopButton').disabled = false;
            
            fetch('/api/run_macro', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    throw new Error(data.error);
                }
            })
            .catch(error => {
                updateStatus('실행 오류');
                alert('매크로 실행 실패: ' + error.message);
                document.getElementById('runButton').disabled = false;
                document.getElementById('stopButton').disabled = true;
            });
        }
        
        // 매크로 중지
        function stopMacro() {
            fetch('/api/stop_macro', {method: 'POST'})
            .then(() => {
                updateStatus('매크로 중지됨');
                document.getElementById('runButton').disabled = false;
                document.getElementById('stopButton').disabled = true;
            });
        }
        
        // 로그 지우기
        function clearLog() {
            document.getElementById('executionLog').innerHTML = '';
            document.getElementById('screenshotArea').style.display = 'none';
        }
        
        // 실행 로그 업데이트
        function updateExecutionLog() {
            fetch('/api/get_log')
            .then(response => response.json())
            .then(data => {
                const logDiv = document.getElementById('executionLog');
                const shouldScroll = logDiv.scrollTop + logDiv.clientHeight >= logDiv.scrollHeight - 10;
                
                logDiv.innerHTML = data.log.map(entry => 
                    `<div class="log-entry ${entry.level}">[${entry.time}] ${entry.message}</div>`
                ).join('');
                
                if (shouldScroll) {
                    logDiv.scrollTop = logDiv.scrollHeight;
                }
                
                // 상태 업데이트
                if (data.is_running) {
                    updateStatus('실행 중...', true);
                } else {
                    updateStatus('준비됨');
                    document.getElementById('runButton').disabled = false;
                    document.getElementById('stopButton').disabled = true;
                }
                
                // 스크린샷 표시
                if (data.screenshot) {
                    document.getElementById('screenshotArea').style.display = 'block';
                    document.getElementById('screenshotImage').src = 'data:image/png;base64,' + data.screenshot;
                }
            });
        }
        
        // 설정 저장
        function saveSettings() {
            const settings = {
                execution_speed: parseFloat(document.getElementById('executionSpeed').value),
                screenshot_capture: document.getElementById('screenshotCapture').value,
                log_level: document.getElementById('logLevel').value
            };
            
            fetch('/api/save_settings', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(settings)
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('설정이 저장되었습니다!');
                }
            });
        }
        
        // 페이지 로드 시 초기화
        window.onload = function() {
            refreshMacroSteps();
            
            // 주기적으로 로그 업데이트
            setInterval(updateExecutionLog, 1000);
            
            // 드래그 앤 드롭 지원
            const uploadArea = document.querySelector('.file-upload-area');
            uploadArea.addEventListener('dragover', (e) => {
                e.preventDefault();
                uploadArea.style.background = '#f0f0ff';
            });
            
            uploadArea.addEventListener('dragleave', () => {
                uploadArea.style.background = '';
            });
            
            uploadArea.addEventListener('drop', (e) => {
                e.preventDefault();
                uploadArea.style.background = '';
                
                const files = e.dataTransfer.files;
                if (files.length > 0 && (files[0].name.endsWith('.xlsx') || files[0].name.endsWith('.xls'))) {
                    document.getElementById('excelFile').files = files;
                    document.getElementById('excelFile').dispatchEvent(new Event('change'));
                }
            });
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

@app.route('/api/upload_excel', methods=['POST'])
def upload_excel():
    try:
        if not MODULES_LOADED:
            return jsonify({'success': False, 'error': '모듈이 로드되지 않았습니다.'})
            
        file = request.files['file']
        filepath = os.path.join(tempfile.gettempdir(), file.filename)
        file.save(filepath)
        
        success = app_state.excel_manager.load_file(filepath)
        if not success:
            return jsonify({'success': False, 'error': 'Excel 파일을 로드할 수 없습니다.'})
        
        sheets = app_state.excel_manager.get_sheet_names()
        active_sheet = app_state.excel_manager.current_sheet
        total_rows = len(app_state.excel_manager.get_all_data())
        
        # 데이터 미리보기
        preview_data = app_state.excel_manager.get_data_preview(rows=5)
        columns = app_state.excel_manager.get_column_headers()
        
        return jsonify({
            'success': True,
            'filename': file.filename,
            'sheets': sheets,
            'active_sheet': active_sheet,
            'total_rows': total_rows,
            'preview': {
                'columns': columns,
                'data': preview_data
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/change_sheet', methods=['POST'])
def change_sheet():
    try:
        if not MODULES_LOADED:
            return jsonify({'success': False, 'error': '모듈이 로드되지 않았습니다.'})
            
        sheet_name = request.json['sheet']
        app_state.excel_manager.select_sheet(sheet_name)
        
        preview_data = app_state.excel_manager.get_data_preview(rows=5)
        columns = app_state.excel_manager.get_column_headers()
        
        return jsonify({
            'success': True,
            'preview': {
                'columns': columns,
                'data': preview_data
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/add_step', methods=['POST'])
def add_step():
    try:
        if not MODULES_LOADED:
            return jsonify({'success': False, 'error': '모듈이 로드되지 않았습니다.'})
            
        step_type = request.json['step_type']
        
        # 기본 스텝 생성
        if step_type == 'mouse_click':
            step = MouseClickStep()
        elif step_type == 'keyboard_type':
            step = KeyboardTypeStep()
        elif step_type == 'wait_time':
            step = WaitTimeStep()
        elif step_type == 'image_search':
            step = ImageSearchStep()
        elif step_type == 'ocr_text':
            step = TextSearchStep()
        elif step_type == 'if_condition':
            step = IfConditionStep()
        else:
            return jsonify({'success': False, 'error': '알 수 없는 스텝 타입'})
        
        app_state.macro_steps.append(step)
        
        return jsonify({
            'success': True,
            'index': len(app_state.macro_steps) - 1
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/get_macro')
def get_macro():
    try:
        steps_info = []
        for i, step in enumerate(app_state.macro_steps):
            step_info = {
                'type': step.step_type.value,
                'name': get_step_display_name(step),
                'description': get_step_description(step)
            }
            steps_info.append(step_info)
        
        return jsonify({'steps': steps_info})
    except Exception as e:
        return jsonify({'steps': []})

@app.route('/api/get_step_config/<int:index>')
def get_step_config(index):
    try:
        if not MODULES_LOADED or index >= len(app_state.macro_steps):
            return jsonify({'html': '<p>설정을 불러올 수 없습니다.</p>'})
        
        step = app_state.macro_steps[index]
        html = generate_step_config_html(step)
        
        return jsonify({'html': html})
    except Exception as e:
        return jsonify({'html': f'<p>오류: {str(e)}</p>'})

@app.route('/api/save_step_config/<int:index>', methods=['POST'])
def save_step_config(index):
    try:
        if not MODULES_LOADED or index >= len(app_state.macro_steps):
            return jsonify({'success': False, 'error': '잘못된 인덱스'})
        
        step = app_state.macro_steps[index]
        
        # 스텝 타입에 따라 설정 저장
        if isinstance(step, MouseClickStep):
            step.x = int(request.form.get('x', 0))
            step.y = int(request.form.get('y', 0))
            step.button = request.form.get('button', 'left')
            step.click_type = request.form.get('click_type', 'single')
            
        elif isinstance(step, KeyboardTypeStep):
            step.text = request.form.get('text', '')
            step.excel_column = request.form.get('excel_column') or None
            step.press_enter = request.form.get('press_enter') == 'true'
            
        elif isinstance(step, WaitTimeStep):
            step.seconds = float(request.form.get('seconds', 1.0))
            
        elif isinstance(step, ImageSearchStep):
            if 'image' in request.files:
                image_file = request.files['image']
                if image_file.filename:
                    image_path = os.path.join(tempfile.gettempdir(), f"macro_image_{index}.png")
                    image_file.save(image_path)
                    step.image_path = image_path
            step.confidence = float(request.form.get('confidence', 0.8))
            step.region = None  # TODO: 영역 설정 구현
            
        elif isinstance(step, TextSearchStep):
            step.search_text = request.form.get('search_text', '')
            step.excel_column = request.form.get('excel_column') or None
            step.exact_match = request.form.get('exact_match') == 'true'
            step.confidence_threshold = float(request.form.get('confidence_threshold', 0.5))
            
        elif isinstance(step, IfConditionStep):
            step.condition_type = ConditionType(request.form.get('condition_type', 'image_found'))
            step.comparison_operator = ComparisonOperator(request.form.get('comparison_operator', 'equals'))
            step.value = request.form.get('value', '')
            step.excel_column = request.form.get('excel_column') or None
        
        app_state.add_log(f"스텝 {index + 1} 설정 저장됨", "info")
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/remove_step/<int:index>', methods=['DELETE'])
def remove_step(index):
    try:
        if 0 <= index < len(app_state.macro_steps):
            app_state.macro_steps.pop(index)
        return jsonify({'success': True})
    except:
        return jsonify({'success': False})

@app.route('/api/clear_macro', methods=['POST'])
def clear_macro():
    app_state.macro_steps = []
    return jsonify({'success': True})

@app.route('/api/save_macro', methods=['POST'])
def save_macro():
    try:
        name = request.json['name']
        macro_file = os.path.join(project_root, 'macros', f'{name}.json')
        
        os.makedirs(os.path.dirname(macro_file), exist_ok=True)
        
        # MacroStep 객체를 직렬화 가능한 형태로 변환
        steps_data = []
        for step in app_state.macro_steps:
            step_dict = {
                'type': step.step_type.value,
                'data': {}
            }
            
            if isinstance(step, MouseClickStep):
                step_dict['data'] = {
                    'x': step.x, 'y': step.y,
                    'button': step.button, 'click_type': step.click_type
                }
            elif isinstance(step, KeyboardTypeStep):
                step_dict['data'] = {
                    'text': step.text, 'excel_column': step.excel_column,
                    'press_enter': step.press_enter
                }
            elif isinstance(step, WaitTimeStep):
                step_dict['data'] = {'seconds': step.seconds}
            elif isinstance(step, ImageSearchStep):
                step_dict['data'] = {
                    'image_path': step.image_path,
                    'confidence': step.confidence
                }
            elif isinstance(step, TextSearchStep):
                step_dict['data'] = {
                    'search_text': step.search_text,
                    'excel_column': step.excel_column,
                    'exact_match': step.exact_match,
                    'confidence_threshold': step.confidence_threshold
                }
            elif isinstance(step, IfConditionStep):
                step_dict['data'] = {
                    'condition_type': step.condition_type.value,
                    'comparison_operator': step.comparison_operator.value,
                    'value': step.value,
                    'excel_column': step.excel_column
                }
            
            steps_data.append(step_dict)
        
        with open(macro_file, 'w', encoding='utf-8') as f:
            json.dump(steps_data, f, ensure_ascii=False, indent=2)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/list_macros')
def list_macros():
    try:
        macro_dir = os.path.join(project_root, 'macros')
        if not os.path.exists(macro_dir):
            return jsonify({'macros': []})
        
        macros = [f[:-5] for f in os.listdir(macro_dir) if f.endswith('.json')]
        return jsonify({'macros': macros})
    except:
        return jsonify({'macros': []})

@app.route('/api/load_macro/<name>')
def load_macro(name):
    try:
        macro_file = os.path.join(project_root, 'macros', f'{name}.json')
        
        with open(macro_file, 'r', encoding='utf-8') as f:
            steps_data = json.load(f)
        
        app_state.macro_steps = []
        
        for step_data in steps_data:
            step_type = step_data['type']
            data = step_data['data']
            
            if step_type == 'mouse_click':
                step = MouseClickStep(**data)
            elif step_type == 'keyboard_type':
                step = KeyboardTypeStep(**data)
            elif step_type == 'wait_time':
                step = WaitTimeStep(**data)
            elif step_type == 'image_search':
                step = ImageSearchStep(**data)
            elif step_type == 'ocr_text':
                step = TextSearchStep(**data)
            elif step_type == 'if_condition':
                data['condition_type'] = ConditionType(data['condition_type'])
                data['comparison_operator'] = ComparisonOperator(data['comparison_operator'])
                step = IfConditionStep(**data)
            else:
                continue
            
            app_state.macro_steps.append(step)
        
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/run_macro', methods=['POST'])
def run_macro():
    try:
        if not MODULES_LOADED:
            return jsonify({'success': False, 'error': '모듈이 로드되지 않았습니다.'})
        
        if app_state.is_running:
            return jsonify({'success': False, 'error': '이미 실행 중입니다.'})
        
        if not app_state.macro_steps:
            return jsonify({'success': False, 'error': '실행할 매크로가 없습니다.'})
        
        # 실행 스레드 시작
        def run_macro_thread():
            try:
                app_state.is_running = True
                app_state.add_log("매크로 실행 시작", "info")
                
                # MacroExecutor 생성 및 실행
                app_state.executor = MacroExecutor(
                    macro_steps=app_state.macro_steps,
                    excel_manager=app_state.excel_manager,
                    settings=app_state.settings
                )
                
                # 로그 콜백 설정
                def log_callback(message, level="info"):
                    app_state.add_log(message, level)
                
                app_state.executor.log_callback = log_callback
                
                # 실행
                success = app_state.executor.execute()
                
                if success:
                    app_state.add_log("매크로 실행 완료", "success")
                else:
                    app_state.add_log("매크로 실행 실패", "error")
                    
            except Exception as e:
                app_state.add_log(f"실행 오류: {str(e)}", "error")
            finally:
                app_state.is_running = False
        
        app_state.execution_thread = threading.Thread(target=run_macro_thread)
        app_state.execution_thread.start()
        
        return jsonify({'success': True})
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/stop_macro', methods=['POST'])
def stop_macro():
    try:
        if app_state.executor:
            app_state.executor.stop()
        app_state.is_running = False
        app_state.add_log("매크로 중지됨", "warning")
        return jsonify({'success': True})
    except:
        return jsonify({'success': False})

@app.route('/api/get_log')
def get_log():
    # 최근 로그 50개만 반환
    recent_logs = app_state.execution_log[-50:]
    
    # 실행 중 스크린샷 확인
    screenshot = None
    if app_state.executor and hasattr(app_state.executor, 'last_screenshot'):
        # 스크린샷을 base64로 인코딩
        screenshot = base64.b64encode(app_state.executor.last_screenshot).decode()
    
    return jsonify({
        'log': recent_logs,
        'is_running': app_state.is_running,
        'screenshot': screenshot
    })

@app.route('/api/save_settings', methods=['POST'])
def save_settings():
    try:
        settings = request.json
        # TODO: 설정 저장 구현
        return jsonify({'success': True})
    except:
        return jsonify({'success': False})

# 헬퍼 함수들
def get_step_display_name(step):
    names = {
        StepType.MOUSE_CLICK: "마우스 클릭",
        StepType.KEYBOARD_TYPE: "텍스트 입력",
        StepType.WAIT_TIME: "대기",
        StepType.IMAGE_SEARCH: "이미지 검색",
        StepType.OCR_TEXT: "텍스트 검색",
        StepType.IF_CONDITION: "조건문"
    }
    return names.get(step.step_type, "알 수 없음")

def get_step_description(step):
    if isinstance(step, MouseClickStep):
        return f"({step.x}, {step.y}) 위치 클릭"
    elif isinstance(step, KeyboardTypeStep):
        if step.excel_column:
            return f"Excel {step.excel_column}열 데이터 입력"
        return f"'{step.text}' 입력"
    elif isinstance(step, WaitTimeStep):
        return f"{step.seconds}초 대기"
    elif isinstance(step, ImageSearchStep):
        return "이미지 검색 후 클릭"
    elif isinstance(step, TextSearchStep):
        if step.excel_column:
            return f"Excel {step.excel_column}열 텍스트 검색"
        return f"'{step.search_text}' 검색"
    elif isinstance(step, IfConditionStep):
        return f"{step.condition_type.value} 조건"
    return ""

def generate_step_config_html(step):
    """각 스텝 타입에 맞는 설정 HTML 생성"""
    
    if isinstance(step, MouseClickStep):
        return f'''
        <div class="form-group">
            <label>X 좌표</label>
            <input type="number" name="x" value="{step.x}" required>
        </div>
        <div class="form-group">
            <label>Y 좌표</label>
            <input type="number" name="y" value="{step.y}" required>
        </div>
        <div class="form-group">
            <label>마우스 버튼</label>
            <select name="button">
                <option value="left" {'selected' if step.button == 'left' else ''}>왼쪽</option>
                <option value="right" {'selected' if step.button == 'right' else ''}>오른쪽</option>
            </select>
        </div>
        <div class="form-group">
            <label>클릭 타입</label>
            <select name="click_type">
                <option value="single" {"selected" if step.click_type == "single" else ""}>싱글 클릭</option>
                <option value="double" {"selected" if step.click_type == "double" else ""}>더블 클릭</option>
            </select>
        </div>
        '''
        
    elif isinstance(step, KeyboardTypeStep):
        # Excel 컬럼 옵션 생성
        excel_options = '<option value="">직접 입력</option>'
        if app_state.excel_manager and app_state.excel_manager.df is not None:
            columns = app_state.excel_manager.get_column_headers()
            for col in columns:
                selected = 'selected' if step.excel_column == col else ''
                excel_options += f'<option value="{col}" {selected}>{col}</option>'
        
        return f'''
        <div class="form-group">
            <label>입력 방식</label>
            <select name="excel_column" onchange="toggleTextInput(this)">
                {excel_options}
            </select>
        </div>
        <div class="form-group" id="textInputGroup">
            <label>입력할 텍스트</label>
            <textarea name="text" rows="3">{step.text or ""}</textarea>
        </div>
        <div class="form-group">
            <label>
                <input type="checkbox" name="press_enter" value="true" {"checked" if step.press_enter else ""}>
                입력 후 Enter 키 누르기
            </label>
        </div>
        <script>
        function toggleTextInput(select) {
            document.getElementById('textInputGroup').style.display = 
                select.value === '' ? 'block' : 'none';
        }
        toggleTextInput(document.querySelector('[name="excel_column"]'));
        </script>
        '''
        
    elif isinstance(step, WaitTimeStep):
        return f'''
        <div class="form-group">
            <label>대기 시간 (초)</label>
            <input type="number" name="seconds" value="{step.seconds}" step="0.1" min="0.1" required>
        </div>
        '''
        
    elif isinstance(step, ImageSearchStep):
        return f'''
        <div class="form-group">
            <label>검색할 이미지</label>
            <input type="file" name="image" accept="image/*" {"required" if not step.image_path else ""}>
            {f'<p>현재 이미지: {os.path.basename(step.image_path)}</p>' if step.image_path else ''}
        </div>
        <div class="form-group">
            <label>유사도 (0.0 ~ 1.0)</label>
            <input type="number" name="confidence" value="{step.confidence}" step="0.1" min="0" max="1" required>
        </div>
        '''
        
    elif isinstance(step, TextSearchStep):
        # Excel 컬럼 옵션 생성
        excel_options = '<option value="">직접 입력</option>'
        if app_state.excel_manager and app_state.excel_manager.df is not None:
            columns = app_state.excel_manager.get_column_headers()
            for col in columns:
                selected = 'selected' if step.excel_column == col else ''
                excel_options += f'<option value="{col}" {selected}>{col}</option>'
        
        return f'''
        <div class="form-group">
            <label>텍스트 소스</label>
            <select name="excel_column" onchange="toggleSearchText(this)">
                {excel_options}
            </select>
        </div>
        <div class="form-group" id="searchTextGroup">
            <label>검색할 텍스트</label>
            <input type="text" name="search_text" value="{step.search_text or ""}">
        </div>
        <div class="form-group">
            <label>
                <input type="checkbox" name="exact_match" value="true" {"checked" if step.exact_match else ""}>
                정확히 일치
            </label>
        </div>
        <div class="form-group">
            <label>신뢰도 임계값 (0.0 ~ 1.0)</label>
            <input type="number" name="confidence_threshold" value="{step.confidence_threshold}" step="0.1" min="0" max="1" required>
        </div>
        <script>
        function toggleSearchText(select) {
            document.getElementById('searchTextGroup').style.display = 
                select.value === '' ? 'block' : 'none';
        }
        toggleSearchText(document.querySelector('[name="excel_column"]'));
        </script>
        '''
        
    elif isinstance(step, IfConditionStep):
        # Excel 컬럼 옵션 생성
        excel_options = '<option value="">없음</option>'
        if app_state.excel_manager and app_state.excel_manager.df is not None:
            columns = app_state.excel_manager.get_column_headers()
            for col in columns:
                selected = 'selected' if step.excel_column == col else ''
                excel_options += f'<option value="{col}" {selected}>{col}</option>'
        
        return f'''
        <div class="form-group">
            <label>조건 타입</label>
            <select name="condition_type">
                <option value="image_found" {"selected" if step.condition_type == ConditionType.IMAGE_FOUND else ""}>이미지 발견</option>
                <option value="text_found" {"selected" if step.condition_type == ConditionType.TEXT_FOUND else ""}>텍스트 발견</option>
                <option value="excel_value" {"selected" if step.condition_type == ConditionType.EXCEL_VALUE else ""}>Excel 값</option>
                <option value="variable" {"selected" if step.condition_type == ConditionType.VARIABLE else ""}>변수</option>
            </select>
        </div>
        <div class="form-group">
            <label>비교 연산자</label>
            <select name="comparison_operator">
                <option value="equals" {"selected" if step.comparison_operator == ComparisonOperator.EQUALS else ""}>=</option>
                <option value="not_equals" {"selected" if step.comparison_operator == ComparisonOperator.NOT_EQUALS else ""}>!=</option>
                <option value="greater_than" {"selected" if step.comparison_operator == ComparisonOperator.GREATER_THAN else ""}>></option>
                <option value="less_than" {"selected" if step.comparison_operator == ComparisonOperator.LESS_THAN else ""}><</option>
                <option value="contains" {"selected" if step.comparison_operator == ComparisonOperator.CONTAINS else ""}>포함</option>
                <option value="exists" {"selected" if step.comparison_operator == ComparisonOperator.EXISTS else ""}>존재</option>
            </select>
        </div>
        <div class="form-group">
            <label>비교 값</label>
            <input type="text" name="value" value="{step.value or ""}">
        </div>
        <div class="form-group">
            <label>Excel 컬럼 (선택사항)</label>
            <select name="excel_column">
                {excel_options}
            </select>
        </div>
        '''
        
    return '<p>설정이 필요하지 않습니다.</p>'

# 메인 실행
if __name__ == '__main__':
    print("=" * 60)
    print("Excel Macro Automation - 통합 웹 UI")
    print("=" * 60)
    print("\n기존 매크로 기능과 완전히 통합된 웹 인터페이스입니다.")
    print("\n기능:")
    print("- Excel 파일 로드 및 데이터 미리보기")
    print("- 드래그 앤 드롭 매크로 편집")
    print("- 각 스텝별 상세 설정")
    print("- 실시간 실행 모니터링")
    print("- 매크로 저장/불러오기")
    print("\n브라우저가 자동으로 열립니다...")
    print("수동으로 열려면: http://localhost:5556")
    print("\n종료하려면 Ctrl+C를 누르세요.")
    print("=" * 60)
    
    # 브라우저 자동 열기
    def open_browser():
        import time
        time.sleep(1.5)
        webbrowser.open('http://localhost:5556')
    
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    # Flask 앱 실행
    app.run(host='0.0.0.0', port=5556, debug=False)