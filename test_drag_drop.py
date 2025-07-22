"""
Test drag and drop functionality
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QMessageBox
from PyQt5.QtCore import Qt

from ui.widgets.variable_palette import VariablePalette
from ui.dialogs.keyboard_type_step_dialog import KeyboardTypeStepDialog
from excel.models import ColumnMapping, ColumnType
from core.macro_types import KeyboardTypeStep
import uuid


class TestWindow(QMainWindow):
    """Test window for drag and drop"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("드래그 앤 드롭 테스트")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        
        # Main layout
        layout = QHBoxLayout(central)
        
        # Left side - Variable palette
        self.variable_palette = VariablePalette()
        
        # Create test column mappings
        test_mappings = [
            ColumnMapping("환자번호", "환자번호", ColumnType.TEXT),
            ColumnMapping("이름", "이름", ColumnType.TEXT),
            ColumnMapping("혈압", "혈압", ColumnType.TEXT),
            ColumnMapping("혈당", "혈당", ColumnType.NUMBER),
            ColumnMapping("콜레스테롤", "콜레스테롤", ColumnType.NUMBER),
            ColumnMapping("판정", "판정", ColumnType.TEXT),
            ColumnMapping("검진일자", "검진일자", ColumnType.DATE)
        ]
        
        self.variable_palette.set_column_mappings(test_mappings)
        
        # Connect signals
        self.variable_palette.variableSelected.connect(self.on_variable_selected)
        self.variable_palette.variableDragged.connect(self.on_variable_dragged)
        
        layout.addWidget(self.variable_palette)
        
        # Right side - Test buttons
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Test keyboard dialog button
        test_keyboard_btn = QPushButton("키보드 입력 다이얼로그 테스트")
        test_keyboard_btn.clicked.connect(self.test_keyboard_dialog)
        right_layout.addWidget(test_keyboard_btn)
        
        # Add stretch
        right_layout.addStretch()
        
        # Info label
        self.info_label = QLabel("변수를 드래그하여 테스트하세요")
        self.info_label.setStyleSheet("padding: 10px; background-color: #f0f0f0;")
        right_layout.addWidget(self.info_label)
        
        layout.addWidget(right_widget)
        
        # Set stretch factors
        layout.setStretchFactor(self.variable_palette, 1)
        layout.setStretchFactor(right_widget, 3)
        
    def on_variable_selected(self, variable_name):
        """Handle variable selection"""
        self.info_label.setText(f"변수 클릭됨: {variable_name}")
        
    def on_variable_dragged(self, variable_name, column_type, excel_column):
        """Handle variable drag"""
        self.info_label.setText(
            f"드래그 시작: {variable_name}\n"
            f"타입: {column_type}\n"
            f"Excel 열: {excel_column}"
        )
        
    def test_keyboard_dialog(self):
        """Test keyboard type dialog with drag and drop"""
        # Create test step
        step = KeyboardTypeStep(
            step_id=str(uuid.uuid4()),
            name="테스트 텍스트 입력",
            text="안녕하세요 ${이름}님, 혈압은 ${혈압}입니다.",
            use_variables=True
        )
        
        # Excel columns for testing
        excel_columns = ["환자번호", "이름", "혈압", "혈당", "콜레스테롤", "판정"]
        
        # Show dialog
        dialog = KeyboardTypeStepDialog(step, excel_columns, self)
        if dialog.exec_():
            # Get result
            data = dialog.get_step_data()
            QMessageBox.information(
                self,
                "결과",
                f"이름: {data['name']}\n"
                f"텍스트: {data['text']}\n"
                f"변수 사용: {data['use_variables']}"
            )


def main():
    """Run test application"""
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show window
    window = TestWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    # Add missing import
    from PyQt5.QtWidgets import QLabel
    main()