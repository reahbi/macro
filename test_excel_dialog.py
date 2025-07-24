#!/usr/bin/env python3
"""
Excel 다이얼로그 테스트 스크립트
Excel 참조 작업 시 창이 꺼지는 문제를 디버깅하기 위한 스크립트
"""

import sys
import os
from pathlib import Path

# 프로젝트 경로 설정
project_root = Path(__file__).parent.absolute()
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import Qt, QTimer

def test_excel_repeat_dialog():
    """ExcelRepeatDialog 테스트"""
    print("\n=== Testing ExcelRepeatDialog ===")
    try:
        from ui.dialogs.excel_repeat_dialog import ExcelRepeatDialog
        
        dialog = ExcelRepeatDialog(total_rows=10, incomplete_rows=5)
        print("Dialog created successfully")
        
        # 다이얼로그 표시
        result = dialog.exec_()
        print(f"Dialog result: {result}")
        
        if result == dialog.Accepted:
            settings = dialog.get_settings()
            print(f"Settings: {settings}")
        
        print("ExcelRepeatDialog test completed successfully")
        return True
        
    except Exception as e:
        print(f"ERROR in ExcelRepeatDialog: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_quick_excel_dialog():
    """QuickExcelSetupDialog 테스트"""
    print("\n=== Testing QuickExcelSetupDialog ===")
    try:
        from ui.dialogs.excel_repeat_dialog import QuickExcelSetupDialog
        
        dialog = QuickExcelSetupDialog()
        print("Dialog created successfully")
        
        # 다이얼로그 표시
        result = dialog.exec_()
        print(f"Dialog result: {result}")
        
        print("QuickExcelSetupDialog test completed successfully")
        return True
        
    except Exception as e:
        print(f"ERROR in QuickExcelSetupDialog: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_sequential_dialogs():
    """순차적으로 두 다이얼로그 테스트"""
    print("\n=== Testing Sequential Dialogs ===")
    try:
        # 첫 번째 다이얼로그
        if not test_excel_repeat_dialog():
            return False
            
        # 잠시 대기
        QTimer.singleShot(100, lambda: None)
        
        # 두 번째 다이얼로그
        if not test_quick_excel_dialog():
            return False
            
        print("Sequential dialog test completed successfully")
        return True
        
    except Exception as e:
        print(f"ERROR in sequential test: {e}")
        import traceback
        traceback.print_exc()
        return False

class TestWindow(QMainWindow):
    """테스트를 위한 메인 윈도우"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel Dialog Test")
        self.setGeometry(100, 100, 400, 300)
        
        # 중앙 위젯
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 레이아웃
        layout = QVBoxLayout(central_widget)
        
        # 버튼들
        btn1 = QPushButton("Test ExcelRepeatDialog")
        btn1.clicked.connect(self.test_repeat_dialog)
        layout.addWidget(btn1)
        
        btn2 = QPushButton("Test QuickExcelSetupDialog")
        btn2.clicked.connect(self.test_quick_dialog)
        layout.addWidget(btn2)
        
        btn3 = QPushButton("Test Both Dialogs (Sequential)")
        btn3.clicked.connect(self.test_both_dialogs)
        layout.addWidget(btn3)
        
        btn4 = QPushButton("Test Drop Event Simulation")
        btn4.clicked.connect(self.test_drop_simulation)
        layout.addWidget(btn4)
        
    def test_repeat_dialog(self):
        """ExcelRepeatDialog 테스트"""
        test_excel_repeat_dialog()
        
    def test_quick_dialog(self):
        """QuickExcelSetupDialog 테스트"""
        test_quick_excel_dialog()
        
    def test_both_dialogs(self):
        """두 다이얼로그 순차 테스트"""
        test_sequential_dialogs()
        
    def test_drop_simulation(self):
        """드롭 이벤트 시뮬레이션"""
        print("\n=== Simulating Drop Event ===")
        try:
            from ui.widgets.macro_editor import MacroFlowWidget
            from core.macro_types import Macro
            
            # 위젯 생성
            flow_widget = MacroFlowWidget()
            flow_widget.show()
            
            # 시뮬레이션 메시지
            QMessageBox.information(
                self, 
                "Drop Simulation", 
                "Drop event would be simulated here.\n"
                "Check console output for debug messages."
            )
            
        except Exception as e:
            print(f"ERROR in drop simulation: {e}")
            import traceback
            traceback.print_exc()
    
    def closeEvent(self, event):
        """창 닫기 이벤트"""
        print("\nTestWindow closeEvent called")
        event.accept()

def main():
    """메인 함수"""
    print("Starting Excel Dialog Test Application")
    print("=" * 50)
    
    app = QApplication(sys.argv)
    app.setApplicationName("Excel Dialog Test")
    
    # 테스트 윈도우 생성
    window = TestWindow()
    window.show()
    
    print("\nTest window created. Click buttons to test dialogs.")
    print("Watch console output for debug messages.")
    print("=" * 50)
    
    # 이벤트 루프 실행
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()