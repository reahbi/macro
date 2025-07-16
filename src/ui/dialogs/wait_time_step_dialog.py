"""
Wait time step configuration dialog
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QLabel, QLineEdit, 
    QDoubleSpinBox, QDialogButtonBox, QFormLayout
)
from PyQt5.QtCore import Qt
from core.macro_types import WaitTimeStep


class WaitTimeStepDialog(QDialog):
    """Dialog for configuring wait time step"""
    
    def __init__(self, step: WaitTimeStep, parent=None):
        super().__init__(parent)
        self.step = step
        self.setWindowTitle("대기 시간 설정")
        self.setModal(True)
        self.setFixedWidth(300)
        self.init_ui()
        self.load_step_data()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Form layout
        form_layout = QFormLayout()
        
        # Step name
        self.name_edit = QLineEdit()
        form_layout.addRow("단계 이름:", self.name_edit)
        
        # Wait time
        self.seconds_spin = QDoubleSpinBox()
        self.seconds_spin.setRange(0.1, 3600.0)
        self.seconds_spin.setSingleStep(0.5)
        self.seconds_spin.setDecimals(1)
        self.seconds_spin.setSuffix(" 초")
        self.seconds_spin.setValue(1.0)
        form_layout.addRow("대기 시간:", self.seconds_spin)
        
        layout.addLayout(form_layout)
        
        # Help text
        help_label = QLabel("지정된 시간 동안 실행을 일시 정지합니다.")
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(help_label)
        
        layout.addStretch()
        
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
        self.seconds_spin.setValue(self.step.seconds)
        
    def get_step_data(self):
        """Get configured step data"""
        return {
            'name': self.name_edit.text(),
            'seconds': self.seconds_spin.value()
        }