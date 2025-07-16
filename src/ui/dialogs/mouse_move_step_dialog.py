"""
Mouse move step configuration dialog
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QSpinBox, QDoubleSpinBox, QDialogButtonBox,
    QFormLayout, QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt, QTimer
import pyautogui
from core.macro_types import MouseMoveStep
from ui.widgets.roi_selector import ROISelectorWidget
from utils.monitor_utils import get_monitor_name_for_position, get_monitor_info


class MouseMoveStepDialog(QDialog):
    """Dialog for configuring mouse move step"""
    
    def __init__(self, step: MouseMoveStep, parent=None):
        super().__init__(parent)
        self.step = step
        self.setWindowTitle("마우스 이동 설정")
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
        
        # Position group
        position_group = QGroupBox("이동 위치")
        position_layout = QVBoxLayout()
        
        # Position inputs
        coord_layout = QHBoxLayout()
        coord_layout.addWidget(QLabel("X:"))
        self.x_spin = QSpinBox()
        self.x_spin.setRange(-9999, 9999)  # 음수 좌표 허용 (듀얼 모니터)
        coord_layout.addWidget(self.x_spin)
        
        coord_layout.addWidget(QLabel("Y:"))
        self.y_spin = QSpinBox()
        self.y_spin.setRange(-9999, 9999)  # 음수 좌표 허용 (듀얼 모니터)
        coord_layout.addWidget(self.y_spin)
        
        coord_layout.addStretch()
        position_layout.addLayout(coord_layout)
        
        # Capture button
        self.capture_button = QPushButton("현재 마우스 위치 캡처 (F3)")
        self.capture_button.clicked.connect(self.capture_position)
        position_layout.addWidget(self.capture_button)
        
        # Set up F3 shortcut
        from PyQt5.QtWidgets import QShortcut
        from PyQt5.QtGui import QKeySequence
        self.capture_shortcut = QShortcut(QKeySequence("F3"), self)
        self.capture_shortcut.activated.connect(self.capture_position)
        
        # Select area button
        self.select_area_button = QPushButton("화면에서 선택...")
        self.select_area_button.clicked.connect(self.select_from_screen)
        position_layout.addWidget(self.select_area_button)
        
        position_group.setLayout(position_layout)
        layout.addWidget(position_group)
        
        # Help text for F3
        help_label = QLabel("💡 팁: F3 키를 누르면 현재 마우스 위치를 즉시 캡처합니다.")
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #0066cc; font-size: 12px; padding: 5px; background-color: #e6f2ff; border-radius: 3px;")
        layout.addWidget(help_label)
        
        # Monitor info
        self.add_monitor_info(layout)
        
        # Move options
        options_group = QGroupBox("이동 옵션")
        options_layout = QFormLayout()
        
        # Duration
        self.duration_spin = QDoubleSpinBox()
        self.duration_spin.setRange(0, 10.0)
        self.duration_spin.setSingleStep(0.1)
        self.duration_spin.setDecimals(1)
        self.duration_spin.setSuffix(" 초")
        self.duration_spin.setValue(0.0)
        options_layout.addRow("이동 시간:", self.duration_spin)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Help text
        help_label = QLabel("이동 시간을 0으로 설정하면 즉시 이동합니다.")
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(help_label)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def add_monitor_info(self, parent_layout):
        """Add monitor information display"""
        monitors = get_monitor_info()
        
        if len(monitors) > 1:
            monitor_group = QGroupBox("모니터 정보")
            monitor_layout = QVBoxLayout()
            
            info_text = f"감지된 모니터: {len(monitors)}개\n"
            for i, monitor in enumerate(monitors):
                name = "주 모니터" if monitor['is_primary'] else f"모니터 {i+1}"
                info_text += f"• {name}: {monitor['width']}x{monitor['height']} (위치: {monitor['x']}, {monitor['y']})\n"
            
            monitor_label = QLabel(info_text.strip())
            monitor_label.setStyleSheet("color: #666; font-size: 11px;")
            monitor_layout.addWidget(monitor_label)
            
            monitor_group.setLayout(monitor_layout)
            parent_layout.addWidget(monitor_group)
        
    def load_step_data(self):
        """Load data from step"""
        self.name_edit.setText(self.step.name)
        self.x_spin.setValue(self.step.x)
        self.y_spin.setValue(self.step.y)
        self.duration_spin.setValue(self.step.duration)
        
    def capture_position(self):
        """Capture current mouse position"""
        # Capture immediately when F3 is pressed
        x, y = pyautogui.position()
        self.x_spin.setValue(x)
        self.y_spin.setValue(y)
        
        # Get monitor name for the position
        monitor_name = get_monitor_name_for_position(x, y)
        
        # Flash the button to indicate capture with monitor info
        self.capture_button.setText(f"캡처됨! ({monitor_name}: {x}, {y})")
        QTimer.singleShot(1500, lambda: self.capture_button.setText("현재 마우스 위치 캡처 (F3)"))
        
        
    def select_from_screen(self):
        """Select position from screen"""
        self.hide()
        
        selector = ROISelectorWidget()
        # For now, just use capture position
        # TODO: Implement proper screen selection
        self.capture_position()
        return
        
        self.show()
        
        if result:
            x, y = result
            self.x_spin.setValue(x)
            self.y_spin.setValue(y)
            
    def get_step_data(self):
        """Get configured step data"""
        return {
            'name': self.name_edit.text(),
            'x': self.x_spin.value(),
            'y': self.y_spin.value(),
            'duration': self.duration_spin.value()
        }