"""
Keyboard hotkey step configuration dialog
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QDialogButtonBox, QFormLayout, QGroupBox,
    QListWidget, QListWidgetItem, QMessageBox
)
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QKeySequence
from core.macro_types import KeyboardHotkeyStep


class KeyCaptureButton(QPushButton):
    """Button that captures key combinations"""
    
    def __init__(self, text="클릭하고 키를 누르세요"):
        super().__init__(text)
        self.keys = []
        self.recording = False
        self.default_text = text
        
    def mousePressEvent(self, event):
        """Start recording on click"""
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            self.recording = True
            self.keys = []
            self.setText("키를 누르세요...")
            self.setFocus()
            
    def keyPressEvent(self, event):
        """Capture key press"""
        if not self.recording:
            return
            
        key = event.key()
        key_name = QKeySequence(key).toString()
        
        # Handle modifiers
        modifiers = event.modifiers()
        if modifiers & Qt.ControlModifier and 'ctrl' not in self.keys:
            self.keys.append('ctrl')
        if modifiers & Qt.AltModifier and 'alt' not in self.keys:
            self.keys.append('alt')
        if modifiers & Qt.ShiftModifier and 'shift' not in self.keys:
            self.keys.append('shift')
        if modifiers & Qt.MetaModifier and 'win' not in self.keys:
            self.keys.append('win')
            
        # Add regular key if not a modifier
        if key not in [Qt.Key_Control, Qt.Key_Alt, Qt.Key_Shift, Qt.Key_Meta] and key_name:
            self.keys.append(key_name.lower())
            
        self.update_display()
        
    def keyReleaseEvent(self, event):
        """Stop recording on key release"""
        if self.recording and self.keys:
            self.recording = False
            
    def focusOutEvent(self, event):
        """Stop recording when focus lost"""
        super().focusOutEvent(event)
        self.recording = False
        
    def update_display(self):
        """Update button text with captured keys"""
        if self.keys:
            self.setText(" + ".join(self.keys))
        else:
            self.setText(self.default_text)
            
    def get_keys(self):
        """Get captured keys"""
        return self.keys
        
    def set_keys(self, keys):
        """Set keys programmatically"""
        self.keys = keys
        self.update_display()


class KeyboardHotkeyStepDialog(QDialog):
    """Dialog for configuring keyboard hotkey step"""
    
    def __init__(self, step: KeyboardHotkeyStep, parent=None):
        super().__init__(parent)
        self.step = step
        self.setWindowTitle("단축키 설정")
        self.setModal(True)
        self.setMinimumWidth(400)
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
        
        # Hotkey capture
        hotkey_group = QGroupBox("단축키")
        hotkey_layout = QVBoxLayout()
        
        # Capture button
        self.capture_button = KeyCaptureButton()
        hotkey_layout.addWidget(self.capture_button)
        
        # Common hotkeys
        common_label = QLabel("일반적인 단축키:")
        common_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        hotkey_layout.addWidget(common_label)
        
        # Hotkey list
        self.hotkey_list = QListWidget()
        self.hotkey_list.setMaximumHeight(150)
        
        common_hotkeys = [
            ("복사", ["ctrl", "c"]),
            ("붙여넣기", ["ctrl", "v"]),
            ("잘라내기", ["ctrl", "x"]),
            ("실행 취소", ["ctrl", "z"]),
            ("다시 실행", ["ctrl", "y"]),
            ("모두 선택", ["ctrl", "a"]),
            ("저장", ["ctrl", "s"]),
            ("새로 만들기", ["ctrl", "n"]),
            ("열기", ["ctrl", "o"]),
            ("인쇄", ["ctrl", "p"]),
            ("찾기", ["ctrl", "f"]),
            ("탭 전환", ["alt", "tab"]),
            ("창 닫기", ["alt", "f4"]),
        ]
        
        for name, keys in common_hotkeys:
            item = QListWidgetItem(f"{name}: {' + '.join(keys)}")
            item.setData(Qt.UserRole, keys)
            self.hotkey_list.addItem(item)
            
        self.hotkey_list.itemDoubleClicked.connect(self.use_common_hotkey)
        hotkey_layout.addWidget(self.hotkey_list)
        
        hotkey_group.setLayout(hotkey_layout)
        layout.addWidget(hotkey_group)
        
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
        if self.step.keys:
            self.capture_button.set_keys(self.step.keys)
            
    def use_common_hotkey(self, item):
        """Use a common hotkey"""
        keys = item.data(Qt.UserRole)
        self.capture_button.set_keys(keys)
        
    def validate_and_accept(self):
        """Validate input and accept"""
        if not self.capture_button.get_keys():
            QMessageBox.warning(
                self, "경고",
                "단축키를 설정해주세요."
            )
            return
            
        self.accept()
        
    def get_step_data(self):
        """Get configured step data"""
        return {
            'name': self.name_edit.text(),
            'keys': self.capture_button.get_keys()
        }