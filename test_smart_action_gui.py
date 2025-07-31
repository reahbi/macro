"""
스마트 액션 GUI 테스트
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget
from PyQt5.QtCore import Qt

# 프로젝트 경로 추가
sys.path.insert(0, r'C:\mag\macro')

from src.ui.dialogs.smart_action_dialog import SmartActionDialog

class TestWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("스마트 액션 테스트")
        self.setGeometry(100, 100, 300, 200)
        
        # 중앙 위젯
        central = QWidget()
        self.setCentralWidget(central)
        
        layout = QVBoxLayout(central)
        
        # 테스트 버튼들
        btn1 = QPushButton("🎯 엑셀 데이터와 함께 열기")
        btn1.clicked.connect(self.open_with_excel)
        btn1.setStyleSheet("""
            QPushButton {
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                background-color: #28a745;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        layout.addWidget(btn1)
        
        btn2 = QPushButton("📄 엑셀 없이 열기")
        btn2.clicked.connect(self.open_without_excel)
        btn2.setStyleSheet("""
            QPushButton {
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
                background-color: #007bff;
                color: white;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        layout.addWidget(btn2)
        
    def open_with_excel(self):
        """엑셀 데이터와 함께 다이얼로그 열기"""
        excel_columns = ['고객명', '전화번호', '주소', '이메일', '상태']
        excel_data = [
            ["홍길동", "010-1234-5678", "서울시 강남구", "hong@email.com", "신규"],
            ["김철수", "010-2345-6789", "서울시 서초구", "kim@email.com", "기존"],
            ["이영희", "010-3456-7890", "서울시 송파구", "lee@email.com", "VIP"],
            ["박민수", "010-4567-8901", "서울시 강동구", "park@email.com", "신규"],
            ["정수진", "010-5678-9012", "서울시 강서구", "jung@email.com", "기존"],
        ]
        
        dialog = SmartActionDialog(self, excel_columns, excel_data)
        if dialog.exec_():
            actions = dialog.get_actions()
            print("\n=== 설정된 액션 ===")
            for i, action in enumerate(actions, 1):
                print(f"{i}. {action}")
                
    def open_without_excel(self):
        """엑셀 없이 다이얼로그 열기"""
        dialog = SmartActionDialog(self)
        if dialog.exec_():
            actions = dialog.get_actions()
            print("\n=== 설정된 액션 ===")
            for i, action in enumerate(actions, 1):
                print(f"{i}. {action}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec_())