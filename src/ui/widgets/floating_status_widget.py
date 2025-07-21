"""
Floating status widget for macro execution monitoring
"""

from typing import Optional, Tuple
from enum import Enum
from dataclasses import dataclass
from PyQt5.QtWidgets import QWidget, QLabel, QProgressBar, QVBoxLayout, QHBoxLayout, QPushButton, QMenu, QAction
from PyQt5.QtCore import Qt, QPoint, QTimer, pyqtSignal, QPropertyAnimation, QRect, QEasingCurve, QSettings
from PyQt5.QtGui import QPainter, QColor, QFont, QPalette, QLinearGradient, QMouseEvent


class DisplayMode(Enum):
    """Display modes for the widget"""
    MINIMAL = "minimal"
    NORMAL = "normal"
    DETAILED = "detailed"


class ExecutionMode(Enum):
    """Execution modes"""
    EXCEL = "excel"
    STANDALONE = "standalone"


@dataclass
class ProgressData:
    """Progress information"""
    mode: ExecutionMode
    percentage: float
    current_row: Optional[int] = None
    total_rows: Optional[int] = None
    current_step: Optional[int] = None
    total_steps: Optional[int] = None
    row_identifier: Optional[str] = None
    step_name: Optional[str] = None
    elapsed_time: Optional[str] = None
    success_count: Optional[int] = None
    failure_count: Optional[int] = None


class FloatingStatusWidget(QWidget):
    """Floating widget to show macro execution status"""
    
    # Signals
    pauseClicked = pyqtSignal()
    stopClicked = pyqtSignal()
    expandToggled = pyqtSignal(bool)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Window setup
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.9)
        
        # State
        self.display_mode = DisplayMode.NORMAL
        self.is_expanded = False
        self.is_dragging = False
        self.drag_position = QPoint()
        
        # Settings for position persistence
        self.settings = QSettings("ExcelMacroAutomation", "FloatingWidget")
        
        # Animation
        self.expand_animation = QPropertyAnimation(self, b"geometry")
        self.expand_animation.setDuration(200)
        self.expand_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Opacity animation for smooth transitions
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(150)
        self.opacity_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Initialize UI
        self.init_ui()
        self.set_display_mode(DisplayMode.NORMAL)
        
        # Load saved position
        self.load_position()
        
        # Auto-hide timer (optional)
        self.auto_hide_timer = QTimer()
        self.auto_hide_timer.timeout.connect(self._check_auto_hide)
        
    def init_ui(self):
        """Initialize UI components"""
        # Main container
        self.container = QWidget()
        self.container.setObjectName("floatingContainer")
        
        # Apply stylesheet
        self.setStyleSheet("""
            #floatingContainer {
                background-color: rgba(255, 255, 255, 240);
                border-radius: 10px;
                border: 1px solid rgba(0, 0, 0, 50);
            }
            QLabel {
                color: #333;
            }
            QPushButton {
                background-color: transparent;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 3px 8px;
                color: #333;
            }
            QPushButton:hover {
                background-color: rgba(0, 0, 0, 10);
            }
            QProgressBar {
                border: 1px solid #ccc;
                border-radius: 3px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 2px;
            }
        """)
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(10, 8, 10, 8)
        container_layout.setSpacing(5)
        
        # Status line (always visible)
        status_layout = QHBoxLayout()
        status_layout.setSpacing(10)
        
        self.status_icon_label = QLabel("▶")
        self.status_icon_label.setFixedWidth(20)
        status_layout.addWidget(self.status_icon_label)
        
        self.status_text_label = QLabel("준비 중...")
        self.status_text_label.setMinimumWidth(150)
        status_layout.addWidget(self.status_text_label)
        
        self.percentage_label = QLabel("0%")
        self.percentage_label.setFixedWidth(40)
        self.percentage_label.setAlignment(Qt.AlignRight)
        status_layout.addWidget(self.percentage_label)
        
        status_layout.addStretch()
        container_layout.addLayout(status_layout)
        
        # Progress bar (always visible)
        self.progress_bar = QProgressBar()
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setTextVisible(False)
        container_layout.addWidget(self.progress_bar)
        
        # Details section (collapsible)
        self.details_widget = QWidget()
        details_layout = QVBoxLayout()
        details_layout.setContentsMargins(0, 5, 0, 0)
        details_layout.setSpacing(3)
        
        # Current step info
        self.step_info_label = QLabel("단계: -")
        self.step_info_label.setStyleSheet("font-size: 11px; color: #666;")
        details_layout.addWidget(self.step_info_label)
        
        # Time and stats
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        self.time_label = QLabel("시간: 00:00")
        self.time_label.setStyleSheet("font-size: 11px; color: #666;")
        stats_layout.addWidget(self.time_label)
        
        self.stats_label = QLabel("성공: 0 | 실패: 0")
        self.stats_label.setStyleSheet("font-size: 11px; color: #666;")
        stats_layout.addWidget(self.stats_label)
        
        stats_layout.addStretch()
        details_layout.addLayout(stats_layout)
        
        # Control buttons
        control_layout = QHBoxLayout()
        control_layout.setSpacing(5)
        
        self.pause_btn = QPushButton("⏸")
        self.pause_btn.setFixedSize(30, 24)
        self.pause_btn.clicked.connect(self.pauseClicked.emit)
        control_layout.addWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("⏹")
        self.stop_btn.setFixedSize(30, 24)
        self.stop_btn.clicked.connect(self.stopClicked.emit)
        control_layout.addWidget(self.stop_btn)
        
        control_layout.addStretch()
        details_layout.addLayout(control_layout)
        
        self.details_widget.setLayout(details_layout)
        self.details_widget.hide()
        container_layout.addWidget(self.details_widget)
        
        self.container.setLayout(container_layout)
        main_layout.addWidget(self.container)
        self.setLayout(main_layout)
        
        # Set initial size
        self.resize(300, 60)
        
    def set_display_mode(self, mode: DisplayMode):
        """Set display mode"""
        self.display_mode = mode
        
        # Save display mode preference
        self.settings.setValue("display_mode", mode.value)
        
        # Collapse first if expanded
        if self.is_expanded:
            self.collapse()
        
        if mode == DisplayMode.MINIMAL:
            self.resize(200, 50)
            self.step_info_label.hide()
            self.stats_label.hide()
            self.time_label.hide()
            self.pause_btn.hide()
            self.stop_btn.hide()
        elif mode == DisplayMode.NORMAL:
            self.resize(300, 60)
            self.step_info_label.show()
            self.stats_label.hide()
            self.time_label.show()
            self.pause_btn.show()
            self.stop_btn.show()
        elif mode == DisplayMode.DETAILED:
            self.resize(350, 80)
            self.step_info_label.show()
            self.stats_label.show()
            self.time_label.show()
            self.pause_btn.show()
            self.stop_btn.show()
            
    def update_progress(self, progress_data: ProgressData):
        """Update progress display"""
        # Update percentage
        self.progress_bar.setValue(int(progress_data.percentage))
        self.percentage_label.setText(f"{int(progress_data.percentage)}%")
        
        # Update status text based on mode
        if progress_data.mode == ExecutionMode.EXCEL:
            if progress_data.current_row and progress_data.total_rows:
                text = f"행 {progress_data.current_row}/{progress_data.total_rows}"
                if progress_data.row_identifier and self.display_mode != DisplayMode.MINIMAL:
                    text += f" - {progress_data.row_identifier}"
                self.status_text_label.setText(text)
        else:
            if progress_data.current_step and progress_data.total_steps:
                text = f"단계 {progress_data.current_step}/{progress_data.total_steps}"
                self.status_text_label.setText(text)
                
        # Update step info
        if progress_data.step_name:
            self.step_info_label.setText(f"현재: {progress_data.step_name}")
            
        # Update time
        if progress_data.elapsed_time:
            self.time_label.setText(f"시간: {progress_data.elapsed_time}")
            
        # Update stats
        if progress_data.success_count is not None and progress_data.failure_count is not None:
            self.stats_label.setText(f"성공: {progress_data.success_count} | 실패: {progress_data.failure_count}")
            
    def set_status(self, status: str, icon: str = "▶"):
        """Set status text and icon"""
        self.status_icon_label.setText(icon)
        self.status_text_label.setText(status)
        
    def set_paused(self, is_paused: bool):
        """Update UI for paused state"""
        if is_paused:
            self.status_icon_label.setText("⏸")
            self.pause_btn.setText("▶")
            self.progress_bar.setStyleSheet("""
                QProgressBar::chunk {
                    background-color: #FF9800;
                }
            """)
        else:
            self.status_icon_label.setText("▶")
            self.pause_btn.setText("⏸")
            self.progress_bar.setStyleSheet("""
                QProgressBar::chunk {
                    background-color: #4CAF50;
                }
            """)
            
    def set_error(self, has_error: bool):
        """Update UI for error state"""
        if has_error:
            self.status_icon_label.setText("⚠")
            self.progress_bar.setStyleSheet("""
                QProgressBar::chunk {
                    background-color: #f44336;
                }
            """)
            
    # Mouse handling for dragging
    def mousePressEvent(self, event: QMouseEvent):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
        elif event.button() == Qt.RightButton:
            self.show_context_menu(event.globalPos())
            event.accept()
            
    def mouseMoveEvent(self, event: QMouseEvent):
        """Handle mouse move"""
        if event.buttons() == Qt.LeftButton and self.is_dragging:
            self.move(event.globalPos() - self.drag_position)
            event.accept()
            
    def mouseReleaseEvent(self, event: QMouseEvent):
        """Handle mouse release"""
        self.is_dragging = False
        # Save position after dragging
        if event.button() == Qt.LeftButton:
            self.save_position()
        
    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """Toggle expanded state on double click"""
        self.toggle_expanded()
        
    def enterEvent(self, event):
        """Mouse entered widget"""
        if self.display_mode != DisplayMode.MINIMAL:
            self.expand()
            
    def leaveEvent(self, event):
        """Mouse left widget"""
        self.collapse()
        
    def toggle_expanded(self):
        """Toggle between expanded and collapsed state"""
        if self.is_expanded:
            self.collapse()
        else:
            self.expand()
            
    def expand(self):
        """Expand to show details"""
        if not self.is_expanded and self.display_mode != DisplayMode.MINIMAL:
            self.is_expanded = True
            self.details_widget.show()
            
            # Animate expansion
            current_rect = self.geometry()
            expanded_height = 60 if self.display_mode == DisplayMode.NORMAL else 120
            if self.display_mode == DisplayMode.DETAILED:
                expanded_height = 150
                
            expanded_rect = QRect(
                current_rect.x(),
                current_rect.y(),
                current_rect.width(),
                expanded_height
            )
            
            self.expand_animation.setStartValue(current_rect)
            self.expand_animation.setEndValue(expanded_rect)
            self.expand_animation.start()
            
            self.expandToggled.emit(True)
            
            # Add slight opacity change for visual feedback
            self.setWindowOpacity(1.0)
            
    def collapse(self):
        """Collapse to hide details"""
        if self.is_expanded:
            self.is_expanded = False
            
            # Animate collapse
            current_rect = self.geometry()
            collapsed_rect = QRect(
                current_rect.x(),
                current_rect.y(),
                current_rect.width(),
                60
            )
            
            self.expand_animation.setStartValue(current_rect)
            self.expand_animation.setEndValue(collapsed_rect)
            self.expand_animation.finished.connect(lambda: self.details_widget.hide())
            self.expand_animation.start()
            
            self.expandToggled.emit(False)
            
    def _check_auto_hide(self):
        """Check if widget should auto-hide"""
        # Implement auto-hide logic if needed
        pass
        
    def show_at_position(self, x: int, y: int):
        """Show widget at specific position"""
        self.move(x, y)
        self.show()
        self.raise_()
        self.activateWindow()
        
    def save_position(self):
        """Save current position to settings"""
        pos = self.pos()
        self.settings.setValue("position/x", pos.x())
        self.settings.setValue("position/y", pos.y())
        self.settings.setValue("display_mode", self.display_mode.value)
        
    def load_position(self):
        """Load saved position from settings"""
        # Load position
        x = self.settings.value("position/x", type=int)
        y = self.settings.value("position/y", type=int)
        
        if x is not None and y is not None:
            # Validate position is on screen
            from PyQt5.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            
            # Ensure widget is at least partially visible
            x = max(0, min(x, screen.width() - 50))
            y = max(0, min(y, screen.height() - 50))
            
            self.move(x, y)
        
        # Load display mode
        mode_value = self.settings.value("display_mode", DisplayMode.NORMAL.value)
        try:
            mode = DisplayMode(mode_value)
            self.set_display_mode(mode)
        except ValueError:
            pass  # Keep default mode
            
    def show_context_menu(self, pos):
        """Show context menu for display mode selection"""
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: white;
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 20px;
                color: #333;
            }
            QMenu::item:selected {
                background-color: #e0e0e0;
            }
            QMenu::separator {
                height: 1px;
                background-color: #ccc;
                margin: 5px 0;
            }
        """)
        
        # Display mode actions
        mode_group = QMenu("표시 모드", menu)
        
        minimal_action = QAction("최소화 모드", self)
        minimal_action.setCheckable(True)
        minimal_action.setChecked(self.display_mode == DisplayMode.MINIMAL)
        minimal_action.triggered.connect(lambda: self.set_display_mode(DisplayMode.MINIMAL))
        mode_group.addAction(minimal_action)
        
        normal_action = QAction("일반 모드", self)
        normal_action.setCheckable(True)
        normal_action.setChecked(self.display_mode == DisplayMode.NORMAL)
        normal_action.triggered.connect(lambda: self.set_display_mode(DisplayMode.NORMAL))
        mode_group.addAction(normal_action)
        
        detailed_action = QAction("상세 모드", self)
        detailed_action.setCheckable(True)
        detailed_action.setChecked(self.display_mode == DisplayMode.DETAILED)
        detailed_action.triggered.connect(lambda: self.set_display_mode(DisplayMode.DETAILED))
        mode_group.addAction(detailed_action)
        
        menu.addMenu(mode_group)
        
        # Position actions
        menu.addSeparator()
        
        reset_position_action = QAction("위치 초기화", self)
        reset_position_action.triggered.connect(self.reset_position)
        menu.addAction(reset_position_action)
        
        # Show menu
        menu.exec_(pos)
        
    def reset_position(self):
        """Reset widget to default position"""
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - 320
        y = screen.height() - 120
        self.move(x, y)
        self.save_position()
        
    def show_completion_animation(self):
        """Show a completion animation"""
        # Flash green background briefly
        original_style = self.container.styleSheet()
        completion_style = """
            #floatingContainer {
                background-color: rgba(76, 175, 80, 240);
                border-radius: 10px;
                border: 2px solid rgba(76, 175, 80, 255);
            }
        """
        
        self.container.setStyleSheet(completion_style)
        QTimer.singleShot(500, lambda: self.container.setStyleSheet(original_style))
        
        # Brief opacity animation
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.7)
        self.opacity_animation.setDuration(250)
        self.opacity_animation.finished.connect(
            lambda: self.opacity_animation.setDirection(QPropertyAnimation.Backward)
        )
        self.opacity_animation.start()