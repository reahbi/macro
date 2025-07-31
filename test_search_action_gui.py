"""
SearchAndAction GUI 테스트 스크립트
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton, QHBoxLayout
from PyQt5.QtCore import Qt

# 프로젝트 경로 추가
sys.path.insert(0, r'C:\mag\macro')

from src.ui.dialogs.search_and_action_integrated import (
    SearchAndActionIntegratedWidget, 
    MacroStepSearchAndActionWidget
)

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🔍 검색하고 실행하기 GUI 테스트")
        self.setGeometry(100, 100, 600, 800)
        
        # 중앙 위젯
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        
        # 1. 메인 설정 위젯
        self.config_widget = SearchAndActionIntegratedWidget()
        # 샘플 엑셀 컬럼 설정
        self.config_widget.set_excel_columns(['고객명', '전화번호', '주소', '이메일', '상태'])
        layout.addWidget(self.config_widget)
        
        # 구분선
        line = QWidget()
        line.setFixedHeight(2)
        line.setStyleSheet("background-color: #ddd;")
        layout.addWidget(line)
        
        # 2. 매크로 스텝 위젯 (미리보기)
        preview_label = QPushButton("📋 매크로 에디터에서의 표시 예시:")
        preview_label.setStyleSheet("font-weight: bold; padding: 10px;")
        layout.addWidget(preview_label)
        
        # 샘플 스텝 데이터
        sample_step_data = {
            "search_type": "text",
            "search_target": "{{고객명}}",
            "success_action": "click",
            "failure_action": "skip_row"
        }
        
        self.step_widget = MacroStepSearchAndActionWidget(sample_step_data)
        self.step_widget.editRequested.connect(self.on_edit_requested)
        self.step_widget.deleteRequested.connect(self.on_delete_requested)
        layout.addWidget(self.step_widget)
        
        # 하단 버튼
        btn_layout = QHBoxLayout()
        
        get_config_btn = QPushButton("🔧 현재 설정 가져오기")
        get_config_btn.clicked.connect(self.get_current_config)
        get_config_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        
        btn_layout.addWidget(get_config_btn)
        layout.addLayout(btn_layout)
        
        # 여백 추가
        layout.addStretch()
        
    def on_edit_requested(self):
        print("편집 버튼 클릭됨!")
        
    def on_delete_requested(self):
        print("삭제 버튼 클릭됨!")
        
    def get_current_config(self):
        config = self.config_widget.get_configuration()
        print("\n=== 현재 설정 ===")
        print(f"검색 타입: {config['search_type']}")
        print(f"검색 대상: {config['search_target']}")
        print(f"검색 옵션: {config['search_options']}")
        print(f"성공 액션: {config['success_action']}")
        print(f"성공 파라미터: {config['success_params']}")
        print(f"실패 액션: {config['failure_action']}")
        print(f"실패 파라미터: {config['failure_params']}")
        print("================\n")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # 스타일 설정
    app.setStyle('Fusion')
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec_())