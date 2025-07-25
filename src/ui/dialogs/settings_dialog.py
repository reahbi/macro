"""
Settings dialog for Excel Macro Automation
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, 
    QPushButton, QDialogButtonBox, QLabel, QCheckBox,
    QSlider, QSpinBox, QComboBox, QGroupBox, QGridLayout,
    QWidget, QLineEdit, QFormLayout, QDoubleSpinBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from config.settings import Settings
from logger.app_logger import get_logger
from typing import Dict, Any


class SettingsDialog(QDialog):
    """Application settings dialog"""
    
    # Signal emitted when settings are changed
    settingsChanged = pyqtSignal()
    
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.logger = get_logger(__name__)
        
        # Store original settings to detect changes
        self.original_settings = {}
        self._store_original_settings()
        
        self.init_ui()
        self.load_settings()
        
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("설정")
        self.setMinimumSize(600, 500)
        
        # Main layout
        layout = QVBoxLayout(self)
        
        # Tab widget for different setting categories
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_general_tab()
        self.create_execution_tab()
        self.create_hotkeys_tab()
        self.create_notification_tab()
        
        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self.apply_settings)
        
        # Reset to defaults button
        reset_button = QPushButton("기본값으로 초기화")
        reset_button.clicked.connect(self.reset_to_defaults)
        button_box.addButton(reset_button, QDialogButtonBox.ResetRole)
        
        layout.addWidget(button_box)
        
    def create_general_tab(self):
        """Create general settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Language selection
        self.language_combo = QComboBox()
        self.language_combo.addItems(["한국어 (ko)", "English (en)"])
        layout.addRow("언어:", self.language_combo)
        
        # Theme selection
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])
        layout.addRow("테마:", self.theme_combo)
        
        # UI options
        ui_group = QGroupBox("UI 옵션")
        ui_layout = QVBoxLayout()
        
        self.show_tooltips = QCheckBox("도구 설명 표시")
        ui_layout.addWidget(self.show_tooltips)
        
        self.confirm_exit = QCheckBox("종료 시 확인")
        ui_layout.addWidget(self.confirm_exit)
        
        self.compact_mode = QCheckBox("컴팩트 모드")
        ui_layout.addWidget(self.compact_mode)
        
        ui_group.setLayout(ui_layout)
        layout.addRow(ui_group)
        
        self.tab_widget.addTab(widget, "일반")
        
    def create_execution_tab(self):
        """Create execution settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Default execution settings
        default_group = QGroupBox("기본 실행 설정")
        default_layout = QFormLayout()
        
        self.default_delay = QSpinBox()
        self.default_delay.setRange(0, 5000)
        self.default_delay.setSuffix(" ms")
        default_layout.addRow("기본 지연 시간:", self.default_delay)
        
        self.screenshot_quality = QSpinBox()
        self.screenshot_quality.setRange(1, 100)
        self.screenshot_quality.setSuffix(" %")
        default_layout.addRow("스크린샷 품질:", self.screenshot_quality)
        
        self.ocr_confidence = QDoubleSpinBox()
        self.ocr_confidence.setRange(0.1, 1.0)
        self.ocr_confidence.setSingleStep(0.1)
        default_layout.addRow("OCR 신뢰도 임계값:", self.ocr_confidence)
        
        default_group.setLayout(default_layout)
        layout.addWidget(default_group)
        
        # Human-like movement settings
        human_group = QGroupBox("사람처럼 자연스러운 마우스 움직임")
        human_layout = QVBoxLayout()
        
        # Enable checkbox
        self.human_movement_enabled = QCheckBox("자연스러운 마우스 움직임 사용")
        self.human_movement_enabled.setToolTip(
            "마우스가 즉시 이동하는 대신 사람처럼 자연스럽게 움직입니다."
        )
        human_layout.addWidget(self.human_movement_enabled)
        
        # Movement duration settings
        duration_layout = QGridLayout()
        
        duration_layout.addWidget(QLabel("이동 시간 범위:"), 0, 0)
        
        # Min duration
        duration_layout.addWidget(QLabel("최소:"), 1, 0)
        self.min_move_duration = QDoubleSpinBox()
        self.min_move_duration.setRange(0.1, 2.0)
        self.min_move_duration.setSingleStep(0.1)
        self.min_move_duration.setSuffix(" 초")
        duration_layout.addWidget(self.min_move_duration, 1, 1)
        
        # Max duration
        duration_layout.addWidget(QLabel("최대:"), 1, 2)
        self.max_move_duration = QDoubleSpinBox()
        self.max_move_duration.setRange(0.5, 5.0)
        self.max_move_duration.setSingleStep(0.1)
        self.max_move_duration.setSuffix(" 초")
        duration_layout.addWidget(self.max_move_duration, 1, 3)
        
        human_layout.addLayout(duration_layout)
        
        # Click delay settings
        click_layout = QGridLayout()
        
        click_layout.addWidget(QLabel("클릭 전 대기 시간:"), 0, 0)
        
        # Min click delay
        click_layout.addWidget(QLabel("최소:"), 1, 0)
        self.click_delay_min = QDoubleSpinBox()
        self.click_delay_min.setRange(0.05, 1.0)
        self.click_delay_min.setSingleStep(0.05)
        self.click_delay_min.setSuffix(" 초")
        click_layout.addWidget(self.click_delay_min, 1, 1)
        
        # Max click delay
        click_layout.addWidget(QLabel("최대:"), 1, 2)
        self.click_delay_max = QDoubleSpinBox()
        self.click_delay_max.setRange(0.1, 2.0)
        self.click_delay_max.setSingleStep(0.05)
        self.click_delay_max.setSuffix(" 초")
        click_layout.addWidget(self.click_delay_max, 1, 3)
        
        human_layout.addLayout(click_layout)
        
        # Connect enable checkbox to enable/disable controls
        self.human_movement_enabled.toggled.connect(self._on_human_movement_toggled)
        
        human_group.setLayout(human_layout)
        layout.addWidget(human_group)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "실행")
        
    def create_hotkeys_tab(self):
        """Create hotkeys settings tab"""
        widget = QWidget()
        layout = QFormLayout(widget)
        
        # Hotkey settings
        self.pause_hotkey = QLineEdit()
        self.pause_hotkey.setPlaceholderText("예: F9")
        layout.addRow("일시정지:", self.pause_hotkey)
        
        self.stop_hotkey = QLineEdit()
        self.stop_hotkey.setPlaceholderText("예: Escape")
        layout.addRow("중지:", self.stop_hotkey)
        
        self.start_hotkey = QLineEdit()
        self.start_hotkey.setPlaceholderText("예: F5")
        layout.addRow("시작:", self.start_hotkey)
        
        # Add note
        note = QLabel("참고: 단축키는 프로그램이 포커스되어 있지 않아도 작동합니다.")
        note.setWordWrap(True)
        note.setStyleSheet("color: gray;")
        layout.addRow(note)
        
        self.tab_widget.addTab(widget, "단축키")
        
    def create_notification_tab(self):
        """Create notification settings tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Preparation notification
        prep_group = QGroupBox("실행 준비 알림")
        prep_layout = QFormLayout()
        
        self.prep_enabled = QCheckBox("실행 준비 알림 사용")
        prep_layout.addRow(self.prep_enabled)
        
        self.countdown_seconds = QSpinBox()
        self.countdown_seconds.setRange(1, 30)
        self.countdown_seconds.setSuffix(" 초")
        prep_layout.addRow("카운트다운 시간:", self.countdown_seconds)
        
        self.minimize_window = QCheckBox("실행 시 창 최소화")
        prep_layout.addRow(self.minimize_window)
        
        self.show_countdown = QCheckBox("카운트다운 표시")
        prep_layout.addRow(self.show_countdown)
        
        prep_group.setLayout(prep_layout)
        layout.addWidget(prep_group)
        
        # Floating widget
        float_group = QGroupBox("플로팅 위젯")
        float_layout = QFormLayout()
        
        self.float_enabled = QCheckBox("플로팅 위젯 사용")
        float_layout.addRow(self.float_enabled)
        
        self.float_mode = QComboBox()
        self.float_mode.addItems(["최소", "일반", "상세"])
        float_layout.addRow("기본 모드:", self.float_mode)
        
        self.float_opacity = QSpinBox()
        self.float_opacity.setRange(10, 100)
        self.float_opacity.setSuffix(" %")
        float_layout.addRow("투명도:", self.float_opacity)
        
        float_group.setLayout(float_layout)
        layout.addWidget(float_group)
        
        # System tray
        tray_group = QGroupBox("시스템 트레이")
        tray_layout = QFormLayout()
        
        self.tray_enabled = QCheckBox("시스템 트레이 사용")
        tray_layout.addRow(self.tray_enabled)
        
        self.tray_notifications = QCheckBox("트레이 알림 표시")
        tray_layout.addRow(self.tray_notifications)
        
        tray_group.setLayout(tray_layout)
        layout.addWidget(tray_group)
        
        layout.addStretch()
        self.tab_widget.addTab(widget, "알림")
        
    def _on_human_movement_toggled(self, checked: bool):
        """Handle human movement checkbox toggle"""
        self.min_move_duration.setEnabled(checked)
        self.max_move_duration.setEnabled(checked)
        self.click_delay_min.setEnabled(checked)
        self.click_delay_max.setEnabled(checked)
        
    def _store_original_settings(self):
        """Store original settings for change detection"""
        self.original_settings = {
            "language": self.settings.get("language"),
            "theme": self.settings.get("theme"),
            "show_tooltips": self.settings.get("ui.show_tooltips"),
            "confirm_exit": self.settings.get("ui.confirm_exit"),
            "compact_mode": self.settings.get("ui.compact_mode"),
            "default_delay_ms": self.settings.get("execution.default_delay_ms"),
            "screenshot_quality": self.settings.get("execution.screenshot_quality"),
            "ocr_confidence_threshold": self.settings.get("execution.ocr_confidence_threshold"),
            "human_movement_enabled": self.settings.get("execution.human_like_movement.enabled"),
            "min_move_duration": self.settings.get("execution.human_like_movement.min_move_duration"),
            "max_move_duration": self.settings.get("execution.human_like_movement.max_move_duration"),
            "click_delay_min": self.settings.get("execution.human_like_movement.click_delay_min"),
            "click_delay_max": self.settings.get("execution.human_like_movement.click_delay_max"),
            "pause_hotkey": self.settings.get("hotkeys.pause"),
            "stop_hotkey": self.settings.get("hotkeys.stop"),
            "start_hotkey": self.settings.get("hotkeys.start"),
            "prep_enabled": self.settings.get("notification.preparation.enabled"),
            "countdown_seconds": self.settings.get("notification.preparation.countdown_seconds"),
            "minimize_window": self.settings.get("notification.preparation.minimize_window"),
            "show_countdown": self.settings.get("notification.preparation.show_countdown"),
            "float_enabled": self.settings.get("notification.floating_widget.enabled"),
            "float_mode": self.settings.get("notification.floating_widget.default_mode"),
            "float_opacity": self.settings.get("notification.floating_widget.opacity"),
            "tray_enabled": self.settings.get("notification.system_tray.enabled"),
            "tray_notifications": self.settings.get("notification.system_tray.show_notifications"),
        }
        
    def load_settings(self):
        """Load current settings into UI"""
        # General tab
        language = self.settings.get("language", "ko")
        self.language_combo.setCurrentText("한국어 (ko)" if language == "ko" else "English (en)")
        
        theme = self.settings.get("theme", "light")
        self.theme_combo.setCurrentText(theme.capitalize())
        
        self.show_tooltips.setChecked(self.settings.get("ui.show_tooltips", True))
        self.confirm_exit.setChecked(self.settings.get("ui.confirm_exit", True))
        self.compact_mode.setChecked(self.settings.get("ui.compact_mode", False))
        
        # Execution tab
        self.default_delay.setValue(self.settings.get("execution.default_delay_ms", 100))
        self.screenshot_quality.setValue(self.settings.get("execution.screenshot_quality", 95))
        self.ocr_confidence.setValue(self.settings.get("execution.ocr_confidence_threshold", 0.7))
        
        # Human-like movement
        human_enabled = self.settings.get("execution.human_like_movement.enabled", True)
        self.human_movement_enabled.setChecked(human_enabled)
        self.min_move_duration.setValue(self.settings.get("execution.human_like_movement.min_move_duration", 0.3))
        self.max_move_duration.setValue(self.settings.get("execution.human_like_movement.max_move_duration", 1.5))
        self.click_delay_min.setValue(self.settings.get("execution.human_like_movement.click_delay_min", 0.1))
        self.click_delay_max.setValue(self.settings.get("execution.human_like_movement.click_delay_max", 0.3))
        self._on_human_movement_toggled(human_enabled)
        
        # Hotkeys tab
        self.pause_hotkey.setText(self.settings.get("hotkeys.pause", "F9"))
        self.stop_hotkey.setText(self.settings.get("hotkeys.stop", "Escape"))
        self.start_hotkey.setText(self.settings.get("hotkeys.start", "F5"))
        
        # Notification tab
        self.prep_enabled.setChecked(self.settings.get("notification.preparation.enabled", True))
        self.countdown_seconds.setValue(self.settings.get("notification.preparation.countdown_seconds", 5))
        self.minimize_window.setChecked(self.settings.get("notification.preparation.minimize_window", True))
        self.show_countdown.setChecked(self.settings.get("notification.preparation.show_countdown", True))
        
        self.float_enabled.setChecked(self.settings.get("notification.floating_widget.enabled", True))
        float_mode = self.settings.get("notification.floating_widget.default_mode", "normal")
        mode_map = {"minimal": "최소", "normal": "일반", "detailed": "상세"}
        self.float_mode.setCurrentText(mode_map.get(float_mode, "일반"))
        self.float_opacity.setValue(int(self.settings.get("notification.floating_widget.opacity", 0.9) * 100))
        
        self.tray_enabled.setChecked(self.settings.get("notification.system_tray.enabled", True))
        self.tray_notifications.setChecked(self.settings.get("notification.system_tray.show_notifications", True))
        
    def save_settings(self):
        """Save settings from UI"""
        # General
        language = "ko" if "한국어" in self.language_combo.currentText() else "en"
        self.settings.set("language", language)
        self.settings.set("theme", self.theme_combo.currentText().lower())
        self.settings.set("ui.show_tooltips", self.show_tooltips.isChecked())
        self.settings.set("ui.confirm_exit", self.confirm_exit.isChecked())
        self.settings.set("ui.compact_mode", self.compact_mode.isChecked())
        
        # Execution
        self.settings.set("execution.default_delay_ms", self.default_delay.value())
        self.settings.set("execution.screenshot_quality", self.screenshot_quality.value())
        self.settings.set("execution.ocr_confidence_threshold", self.ocr_confidence.value())
        
        # Human-like movement
        self.settings.set("execution.human_like_movement.enabled", self.human_movement_enabled.isChecked())
        self.settings.set("execution.human_like_movement.min_move_duration", self.min_move_duration.value())
        self.settings.set("execution.human_like_movement.max_move_duration", self.max_move_duration.value())
        self.settings.set("execution.human_like_movement.click_delay_min", self.click_delay_min.value())
        self.settings.set("execution.human_like_movement.click_delay_max", self.click_delay_max.value())
        
        # Hotkeys
        self.settings.set("hotkeys.pause", self.pause_hotkey.text())
        self.settings.set("hotkeys.stop", self.stop_hotkey.text())
        self.settings.set("hotkeys.start", self.start_hotkey.text())
        
        # Notification
        self.settings.set("notification.preparation.enabled", self.prep_enabled.isChecked())
        self.settings.set("notification.preparation.countdown_seconds", self.countdown_seconds.value())
        self.settings.set("notification.preparation.minimize_window", self.minimize_window.isChecked())
        self.settings.set("notification.preparation.show_countdown", self.show_countdown.isChecked())
        
        self.settings.set("notification.floating_widget.enabled", self.float_enabled.isChecked())
        mode_map = {"최소": "minimal", "일반": "normal", "상세": "detailed"}
        self.settings.set("notification.floating_widget.default_mode", mode_map.get(self.float_mode.currentText(), "normal"))
        self.settings.set("notification.floating_widget.opacity", self.float_opacity.value() / 100.0)
        
        self.settings.set("notification.system_tray.enabled", self.tray_enabled.isChecked())
        self.settings.set("notification.system_tray.show_notifications", self.tray_notifications.isChecked())
        
        # Save to file
        self.settings.save()
        
        # Emit signal for settings change
        self.settingsChanged.emit()
        
        self.logger.info("Settings saved successfully")
        
    def apply_settings(self):
        """Apply settings without closing dialog"""
        self.save_settings()
        self._store_original_settings()  # Update original settings after apply
        
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings.reset_to_defaults()
        self.load_settings()
        self.logger.info("Settings reset to defaults")
        
    def accept(self):
        """Handle OK button"""
        self.save_settings()
        super().accept()
        
    def reject(self):
        """Handle Cancel button"""
        # Check if there are unsaved changes
        if self._has_unsaved_changes():
            # You could add a confirmation dialog here
            pass
        super().reject()
        
    def _has_unsaved_changes(self) -> bool:
        """Check if there are unsaved changes"""
        # Compare current UI values with original settings
        # This is a simplified check - you could make it more comprehensive
        return False  # For now, always allow cancel