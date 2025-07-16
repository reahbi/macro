"""
Screenshot step configuration dialog
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QDialogButtonBox, QFormLayout, QGroupBox,
    QComboBox, QCheckBox, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from core.macro_types import ScreenshotStep
import os
from datetime import datetime


class ScreenshotStepDialog(QDialog):
    """Dialog for configuring screenshot step"""
    
    def __init__(self, step: ScreenshotStep, parent=None):
        super().__init__(parent)
        self.step = step
        self.setWindowTitle("화면 캡처 설정")
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
        
        # File settings group
        file_group = QGroupBox("파일 설정")
        file_layout = QVBoxLayout()
        
        # Filename pattern
        pattern_layout = QHBoxLayout()
        pattern_layout.addWidget(QLabel("파일명 패턴:"))
        self.filename_edit = QLineEdit()
        self.filename_edit.setPlaceholderText("예: screenshot_{timestamp}.png")
        pattern_layout.addWidget(self.filename_edit)
        file_layout.addLayout(pattern_layout)
        
        # Help text for filename patterns
        help_text = QLabel(
            "사용 가능한 변수:\n"
            "• {timestamp} - 현재 시간 (YYYYMMDD_HHMMSS)\n"
            "• {date} - 현재 날짜 (YYYYMMDD)\n"
            "• {time} - 현재 시간 (HHMMSS)\n"
            "• {index} - 순번 (자동 증가)"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #666; font-size: 11px; background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        file_layout.addWidget(help_text)
        
        # Save directory
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("저장 경로:"))
        self.directory_edit = QLineEdit()
        self.directory_edit.setPlaceholderText("기본: ./screenshots/")
        dir_layout.addWidget(self.directory_edit)
        
        self.browse_btn = QPushButton("찾아보기...")
        self.browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(self.browse_btn)
        file_layout.addLayout(dir_layout)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Capture options group
        options_group = QGroupBox("캡처 옵션")
        options_layout = QVBoxLayout()
        
        # Full screen or region
        self.full_screen_checkbox = QCheckBox("전체 화면 캡처")
        self.full_screen_checkbox.setChecked(True)
        self.full_screen_checkbox.toggled.connect(self.on_full_screen_toggled)
        options_layout.addWidget(self.full_screen_checkbox)
        
        # Region settings (disabled by default)
        region_layout = QHBoxLayout()
        region_layout.addWidget(QLabel("영역:"))
        
        self.x_edit = QLineEdit("0")
        self.x_edit.setMaximumWidth(80)
        self.x_edit.setEnabled(False)
        region_layout.addWidget(QLabel("X:"))
        region_layout.addWidget(self.x_edit)
        
        self.y_edit = QLineEdit("0")
        self.y_edit.setMaximumWidth(80)
        self.y_edit.setEnabled(False)
        region_layout.addWidget(QLabel("Y:"))
        region_layout.addWidget(self.y_edit)
        
        self.width_edit = QLineEdit("0")
        self.width_edit.setMaximumWidth(80)
        self.width_edit.setEnabled(False)
        region_layout.addWidget(QLabel("너비:"))
        region_layout.addWidget(self.width_edit)
        
        self.height_edit = QLineEdit("0")
        self.height_edit.setMaximumWidth(80)
        self.height_edit.setEnabled(False)
        region_layout.addWidget(QLabel("높이:"))
        region_layout.addWidget(self.height_edit)
        
        region_layout.addStretch()
        options_layout.addLayout(region_layout)
        
        # Select region button
        self.select_region_btn = QPushButton("화면에서 영역 선택...")
        self.select_region_btn.setEnabled(False)
        self.select_region_btn.clicked.connect(self.select_region)
        options_layout.addWidget(self.select_region_btn)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
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
        self.filename_edit.setText(self.step.filename_pattern)
        self.directory_edit.setText(self.step.save_directory)
        
        if self.step.region:
            self.full_screen_checkbox.setChecked(False)
            x, y, width, height = self.step.region
            self.x_edit.setText(str(x))
            self.y_edit.setText(str(y))
            self.width_edit.setText(str(width))
            self.height_edit.setText(str(height))
        else:
            self.full_screen_checkbox.setChecked(True)
            
    def on_full_screen_toggled(self, checked):
        """Handle full screen checkbox toggle"""
        self.x_edit.setEnabled(not checked)
        self.y_edit.setEnabled(not checked)
        self.width_edit.setEnabled(not checked)
        self.height_edit.setEnabled(not checked)
        self.select_region_btn.setEnabled(not checked)
        
    def browse_directory(self):
        """Browse for save directory"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "저장 경로 선택",
            self.directory_edit.text() or "./screenshots/"
        )
        if directory:
            self.directory_edit.setText(directory)
            
    def select_region(self):
        """Select region from screen"""
        # TODO: Implement screen region selection
        # For now, just show a message
        QMessageBox.information(
            self,
            "기능 구현 예정",
            "화면 영역 선택 기능은 추후 구현 예정입니다.\n수동으로 좌표를 입력해주세요."
        )
        
    def validate_and_accept(self):
        """Validate input and accept"""
        # Default filename if empty
        if not self.filename_edit.text():
            self.filename_edit.setText("screenshot_{timestamp}.png")
            
        # Default directory if empty
        if not self.directory_edit.text():
            self.directory_edit.setText("./screenshots/")
            
        # Validate region if not full screen
        if not self.full_screen_checkbox.isChecked():
            try:
                x = int(self.x_edit.text())
                y = int(self.y_edit.text())
                width = int(self.width_edit.text())
                height = int(self.height_edit.text())
                
                if width <= 0 or height <= 0:
                    raise ValueError("너비와 높이는 0보다 커야 합니다")
                    
            except ValueError as e:
                QMessageBox.warning(
                    self, "경고",
                    f"잘못된 영역 설정: {str(e)}"
                )
                return
                
        self.accept()
        
    def get_step_data(self):
        """Get configured step data"""
        region = None
        if not self.full_screen_checkbox.isChecked():
            region = (
                int(self.x_edit.text()),
                int(self.y_edit.text()),
                int(self.width_edit.text()),
                int(self.height_edit.text())
            )
            
        return {
            'name': self.name_edit.text() or "화면 캡처",
            'filename_pattern': self.filename_edit.text() or "screenshot_{timestamp}.png",
            'save_directory': self.directory_edit.text() or "./screenshots/",
            'region': region
        }