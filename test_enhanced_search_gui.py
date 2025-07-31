"""
향상된 검색 GUI 테스트
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import Qt

# 프로젝트 경로 추가
sys.path.insert(0, r'C:\mag\macro')

from src.ui.dialogs.enhanced_search_dialog import EnhancedSearchDialog

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("향상된 검색 테스트")
        self.setGeometry(100, 100, 400, 300)
        
        # 중앙 위젯
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        layout.setSpacing(20)
        
        # 헤더
        header = QPushButton("🔍 향상된 검색 다이얼로그 테스트")
        header.setStyleSheet("""
            QPushButton {
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
            }
        """)
        header.setEnabled(False)
        layout.addWidget(header)
        
        # 이미지 검색 테스트
        img_btn = QPushButton("🖼️ 이미지 검색 + 액션")
        img_btn.setStyleSheet("""
            QPushButton {
                padding: 15px;
                font-size: 14px;
                background-color: #2ecc71;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        img_btn.clicked.connect(self.open_image_search)
        layout.addWidget(img_btn)
        
        # 텍스트 검색 테스트
        text_btn = QPushButton("📝 텍스트 검색 + 액션")
        text_btn.setStyleSheet("""
            QPushButton {
                padding: 15px;
                font-size: 14px;
                background-color: #e74c3c;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        text_btn.clicked.connect(self.open_text_search)
        layout.addWidget(text_btn)
        
        # 엑셀 연동 테스트
        excel_btn = QPushButton("📊 엑셀 변수와 함께 테스트")
        excel_btn.setStyleSheet("""
            QPushButton {
                padding: 15px;
                font-size: 14px;
                background-color: #9b59b6;
                color: white;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        excel_btn.clicked.connect(self.open_with_excel)
        layout.addWidget(excel_btn)
        
        layout.addStretch()
        
    def open_image_search(self):
        """이미지 검색 다이얼로그 열기"""
        dialog = EnhancedSearchDialog(self, search_type="image")
        if dialog.exec_():
            config = dialog.get_configuration()
            self.show_result(config)
            
    def open_text_search(self):
        """텍스트 검색 다이얼로그 열기"""
        dialog = EnhancedSearchDialog(self, search_type="text")
        if dialog.exec_():
            config = dialog.get_configuration()
            self.show_result(config)
            
    def open_with_excel(self):
        """엑셀 변수와 함께 열기"""
        excel_columns = ['고객명', '전화번호', '주소', '이메일', '상태', '담당자']
        dialog = EnhancedSearchDialog(self, search_type="text", excel_columns=excel_columns)
        if dialog.exec_():
            config = dialog.get_configuration()
            self.show_result(config)
            
    def show_result(self, config):
        """결과 표시"""
        msg = "=== 설정 결과 ===\n\n"
        
        # 검색 타입
        msg += f"검색 타입: {config['search_type']}\n"
        
        # 검색 설정
        if config['search_type'] == 'image':
            msg += f"이미지: {config['search_config'].get('image_path', '')}\n"
            msg += f"일치율: {config['search_config'].get('confidence', 0.8) * 100}%\n"
        else:
            msg += f"텍스트: {config['search_config'].get('text', '')}\n"
            msg += f"정확히 일치: {config['search_config'].get('exact_match', False)}\n"
            
        # 성공 액션
        msg += f"\n✅ 찾았을 때: {config['success_action']['type']}\n"
        if 'text' in config['success_action']:
            msg += f"  입력: {config['success_action']['text']}\n"
            
        # 실패 액션
        msg += f"\n❌ 못 찾았을 때: {config['failure_action']['type']}\n"
        if 'count' in config['failure_action']:
            msg += f"  재시도: {config['failure_action']['count']}회\n"
            
        QMessageBox.information(self, "설정 결과", msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec_())