"""
Loop step configuration dialog
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QDialogButtonBox, QFormLayout, QGroupBox,
    QComboBox, QSpinBox, QListWidget, QListWidgetItem,
    QAbstractItemView, QMessageBox, QTextEdit
)
from PyQt5.QtCore import Qt
from core.macro_types import LoopStep, MacroStep
from typing import List, Optional


class LoopStepDialog(QDialog):
    """Dialog for configuring loop step"""
    
    def __init__(self, step: LoopStep, available_steps: List[MacroStep], parent=None):
        super().__init__(parent)
        self.step = step
        self.available_steps = available_steps  # All steps in the macro
        self.setWindowTitle("반복문 설정")
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.init_ui()
        self.load_step_data()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Step name
        name_layout = QFormLayout()
        self.name_edit = QLineEdit()
        name_layout.addRow("단계 이름:", self.name_edit)
        layout.addLayout(name_layout)
        
        # Loop type group
        type_group = QGroupBox("반복 타입")
        type_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #2196F3;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #1976d2;
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        type_layout = QVBoxLayout()
        
        # Loop type selection
        type_form_layout = QFormLayout()
        self.type_combo = QComboBox()
        self.type_combo.addItems([
            "지정 횟수 반복",
            "이미지가 나타날 때까지",
            "각 엑셀 행에 대해"
        ])
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        type_form_layout.addRow("반복 방식:", self.type_combo)
        type_layout.addLayout(type_form_layout)
        
        # Count settings (for count type)
        self.count_widget = QWidget()
        count_layout = QHBoxLayout()
        count_layout.addWidget(QLabel("반복 횟수:"))
        self.count_spin = QSpinBox()
        self.count_spin.setMinimum(1)
        self.count_spin.setMaximum(9999)
        self.count_spin.setValue(5)
        count_layout.addWidget(self.count_spin)
        count_layout.addWidget(QLabel("회"))
        count_layout.addStretch()
        self.count_widget.setLayout(count_layout)
        type_layout.addWidget(self.count_widget)
        
        # Image settings (for while_image type)
        self.image_widget = QWidget()
        image_layout = QVBoxLayout()
        image_info = QLabel(
            "이미지가 화면에 나타날 때까지 반복합니다.\n"
            "이미지 검색 단계를 반복 대상에 포함시켜야 합니다."
        )
        image_info.setWordWrap(True)
        image_info.setStyleSheet("color: #666; background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        image_layout.addWidget(image_info)
        self.image_widget.setLayout(image_layout)
        self.image_widget.hide()
        type_layout.addWidget(self.image_widget)
        
        # Row settings (for for_each_row type)
        self.row_widget = QWidget()
        row_layout = QVBoxLayout()
        row_info = QLabel(
            "엑셀의 각 행에 대해 반복합니다.\n"
            "변수 치환을 사용하는 단계를 포함시켜 각 행의 데이터를 활용하세요."
        )
        row_info.setWordWrap(True)
        row_info.setStyleSheet("color: #666; background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        row_layout.addWidget(row_info)
        self.row_widget.setLayout(row_layout)
        self.row_widget.hide()
        type_layout.addWidget(self.row_widget)
        
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # Steps selection group
        steps_group = QGroupBox("반복할 단계 선택")
        steps_layout = QVBoxLayout()
        
        steps_info = QLabel("반복할 단계들을 선택하세요 (Ctrl+클릭으로 다중 선택)")
        steps_info.setStyleSheet("color: #666; font-size: 12px;")
        steps_layout.addWidget(steps_info)
        
        # Available steps list
        self.steps_list = QListWidget()
        self.steps_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self.steps_list.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 2px solid #2196F3;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                margin: 2px;
                border: 1px solid #e0e0e0;
                border-radius: 3px;
                background-color: #f5f5f5;
            }
            QListWidget::item:hover {
                background-color: #e3f2fd;
                border-color: #2196F3;
            }
            QListWidget::item:selected {
                background-color: #1976d2;
                color: white;
                border-color: #1565c0;
            }
        """)
        
        # Add available steps to list
        for step in self.available_steps:
            if step.step_id != self.step.step_id:  # Don't include self
                item = QListWidgetItem(f"{step.name} ({step.step_type.value})")
                item.setData(Qt.UserRole, step.step_id)
                self.steps_list.addItem(item)
                
        steps_layout.addWidget(self.steps_list)
        
        # Selected steps info
        self.selected_info = QLabel("선택된 단계: 0개")
        self.selected_info.setStyleSheet("font-weight: bold;")
        steps_layout.addWidget(self.selected_info)
        
        self.steps_list.itemSelectionChanged.connect(self.update_selected_info)
        
        steps_group.setLayout(steps_layout)
        layout.addWidget(steps_group)
        
        # Description
        desc_layout = QFormLayout()
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        self.description_edit.setPlaceholderText("반복문에 대한 설명 (선택사항)")
        desc_layout.addRow("설명:", self.description_edit)
        layout.addLayout(desc_layout)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        buttons.accepted.connect(self.validate_and_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def load_step_data(self):
        """Load data from step"""
        self.name_edit.setText(self.step.name)
        
        # Set loop type
        type_map = {
            "count": 0,
            "while_image": 1,
            "for_each_row": 2
        }
        self.type_combo.setCurrentIndex(type_map.get(self.step.loop_type, 0))
        
        # Set count
        self.count_spin.setValue(self.step.loop_count)
        
        # Select loop steps
        for i in range(self.steps_list.count()):
            item = self.steps_list.item(i)
            step_id = item.data(Qt.UserRole)
            if step_id in self.step.loop_steps:
                item.setSelected(True)
                
        # Set description
        if hasattr(self.step, 'description'):
            self.description_edit.setText(self.step.description)
            
        self.update_selected_info()
        
    def on_type_changed(self, index):
        """Handle loop type change"""
        # Show/hide appropriate widgets
        self.count_widget.setVisible(index == 0)
        self.image_widget.setVisible(index == 1)
        self.row_widget.setVisible(index == 2)
        
    def update_selected_info(self):
        """Update selected steps info"""
        selected_count = len(self.steps_list.selectedItems())
        self.selected_info.setText(f"선택된 단계: {selected_count}개")
        
    def validate_and_accept(self):
        """Validate input and accept"""
        # Check if any steps are selected
        if not self.steps_list.selectedItems():
            QMessageBox.warning(
                self, "경고",
                "반복할 단계를 최소 1개 이상 선택해주세요."
            )
            return
            
        # Check count for count type
        if self.type_combo.currentIndex() == 0 and self.count_spin.value() < 1:
            QMessageBox.warning(
                self, "경고",
                "반복 횟수는 1 이상이어야 합니다."
            )
            return
            
        self.accept()
        
    def get_step_data(self):
        """Get configured step data"""
        # Get loop type
        type_map = {
            0: "count",
            1: "while_image",
            2: "for_each_row"
        }
        loop_type = type_map[self.type_combo.currentIndex()]
        
        # Get selected step IDs
        loop_steps = []
        for item in self.steps_list.selectedItems():
            loop_steps.append(item.data(Qt.UserRole))
            
        return {
            'name': self.name_edit.text() or "반복문",
            'loop_type': loop_type,
            'loop_count': self.count_spin.value(),
            'loop_steps': loop_steps,
            'description': self.description_edit.toPlainText()
        }