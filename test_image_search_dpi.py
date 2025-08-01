"""
이미지 검색 DPI 스케일링 테스트 스크립트
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QTextEdit, QLabel
from PyQt5.QtCore import Qt
from ui.dialogs.image_step_dialog import ImageSearchStepDialog
from core.macro_types import ImageSearchStep
import json


class TestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("이미지 검색 DPI 테스트")
        self.setGeometry(100, 100, 600, 400)
        
        layout = QVBoxLayout()
        
        # 테스트 버튼들
        test_new_btn = QPushButton("새 이미지 검색 단계 만들기")
        test_new_btn.clicked.connect(self.test_new_step)
        layout.addWidget(test_new_btn)
        
        test_load_btn = QPushButton("기존 단계 로드 테스트")
        test_load_btn.clicked.connect(self.test_load_step)
        layout.addWidget(test_load_btn)
        
        # 결과 표시
        layout.addWidget(QLabel("결과:"))
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)
        
        self.setLayout(layout)
        
    def log(self, message):
        """결과 로깅"""
        self.result_text.append(message)
        self.result_text.append("-" * 50)
        
    def test_new_step(self):
        """새 이미지 검색 단계 생성 테스트"""
        self.log("=== 새 이미지 검색 단계 테스트 ===")
        
        # 새 단계 생성
        step = ImageSearchStep()
        
        # 다이얼로그 열기
        dialog = ImageSearchStepDialog(step=step, parent=self)
        
        if dialog.exec_():
            # 결과 확인
            step_data = dialog.get_step_data()
            
            self.log("단계 데이터:")
            self.log(json.dumps(step_data, indent=2, ensure_ascii=False))
            
            # 특히 monitor_info 확인
            if 'monitor_info' in step_data:
                self.log("✅ monitor_info가 올바르게 저장됨")
                self.log(f"monitor_info: {step_data['monitor_info']}")
            else:
                self.log("❌ monitor_info가 없음!")
                
            # region 확인
            if 'region' in step_data and step_data['region']:
                self.log(f"✅ region: {step_data['region']}")
            else:
                self.log("❌ region이 없음!")
                
    def test_load_step(self):
        """기존 단계 로드 테스트"""
        self.log("=== 기존 단계 로드 테스트 ===")
        
        # 테스트 데이터 생성
        test_data = {
            "step_type": "image_search",
            "name": "테스트 이미지 검색",
            "image_path": "",
            "confidence": 0.9,
            "region": [100, 200, 300, 400],
            "monitor_info": {
                "index": 1,
                "name": "Monitor 1",
                "bounds": {
                    "left": 0,
                    "top": 0,
                    "width": 1920,
                    "height": 1080
                }
            },
            "click_on_found": True,
            "double_click": False
        }
        
        # 단계 생성
        step = ImageSearchStep.from_dict(test_data)
        
        self.log("로드된 단계 정보:")
        self.log(f"Name: {step.name}")
        self.log(f"Region: {step.region}")
        self.log(f"Monitor Info: {step.monitor_info}")
        
        # 다이얼로그에서 로드 테스트
        dialog = ImageSearchStepDialog(step=step, parent=self)
        
        # monitor_info가 올바르게 로드되었는지 확인
        if hasattr(dialog, 'monitor_info') and dialog.monitor_info:
            self.log("✅ 다이얼로그에 monitor_info가 올바르게 로드됨")
        else:
            self.log("❌ 다이얼로그에 monitor_info가 로드되지 않음")
            
        dialog.show()
        dialog.close()
        
        # 저장/로드 사이클 테스트
        self.log("\n저장/로드 사이클 테스트:")
        saved_data = step.to_dict()
        
        if 'monitor_info' in saved_data:
            self.log("✅ to_dict()에 monitor_info 포함됨")
        else:
            self.log("❌ to_dict()에 monitor_info 누락됨")
            
        # 다시 로드
        reloaded_step = ImageSearchStep.from_dict(saved_data)
        if reloaded_step.monitor_info:
            self.log("✅ 재로드 후 monitor_info 유지됨")
        else:
            self.log("❌ 재로드 후 monitor_info 손실됨")


def main():
    app = QApplication(sys.argv)
    
    # DPI awareness 설정
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    widget = TestWidget()
    widget.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()