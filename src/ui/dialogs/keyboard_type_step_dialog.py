"""
Keyboard type step configuration dialog
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QSpinBox, QDialogButtonBox, QTextEdit,
    QFormLayout, QGroupBox, QCheckBox, QListWidget
)
from PyQt5.QtCore import Qt
from core.macro_types import KeyboardTypeStep


class KeyboardTypeStepDialog(QDialog):
    """Dialog for configuring keyboard type step"""
    
    def __init__(self, step: KeyboardTypeStep, excel_columns=None, parent=None):
        super().__init__(parent)
        self.step = step
        self.excel_columns = excel_columns or []
        self.setWindowTitle("텍스트 입력 설정")
        self.setModal(True)
        self.setMinimumWidth(500)
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
        
        # Text input
        text_group = QGroupBox("입력할 텍스트")
        text_layout = QVBoxLayout()
        
        # Text edit
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("입력할 텍스트를 작성하세요.\n변수는 {{변수명}} 형식으로 사용할 수 있습니다.")
        text_layout.addWidget(self.text_edit)
        
        # Variable help
        if self.excel_columns:
            help_layout = QHBoxLayout()
            help_layout.addWidget(QLabel("사용 가능한 Excel 열:"))
            
            # Variable list
            self.var_list = QListWidget()
            self.var_list.setMaximumHeight(100)
            for col in self.excel_columns:
                self.var_list.addItem(f"{{{{{col}}}}}")
            self.var_list.itemDoubleClicked.connect(self.insert_variable)
            help_layout.addWidget(self.var_list)
            
            text_layout.addLayout(help_layout)
        
        text_group.setLayout(text_layout)
        layout.addWidget(text_group)
        
        # Typing options
        options_group = QGroupBox("입력 옵션")
        options_layout = QFormLayout()
        
        # Typing interval
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(0, 1000)
        self.interval_spin.setSuffix(" ms")
        self.interval_spin.setValue(0)
        options_layout.addRow("키 입력 간격:", self.interval_spin)
        
        # Use variables checkbox
        self.use_variables_check = QCheckBox("변수 치환 사용")
        self.use_variables_check.setChecked(True)
        options_layout.addRow("", self.use_variables_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def load_step_data(self):
        """Load data from step"""
        self.name_edit.setText(self.step.name)
        self.text_edit.setPlainText(self.step.text)
        self.interval_spin.setValue(int(self.step.interval * 1000))
        self.use_variables_check.setChecked(self.step.use_variables)
        
    def insert_variable(self, item):
        """Insert variable at cursor position"""
        cursor = self.text_edit.textCursor()
        cursor.insertText(item.text())
        
    def get_step_data(self):
        """Get configured step data"""
        return {
            'name': self.name_edit.text(),
            'text': self.text_edit.toPlainText(),
            'interval': self.interval_spin.value() / 1000.0,
            'use_variables': self.use_variables_check.isChecked()
        }