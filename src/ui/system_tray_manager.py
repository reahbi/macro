"""
System tray manager for macro execution
"""

from typing import Optional
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtCore import QObject, pyqtSignal, QTimer
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QBrush, QColor
from config.settings import Settings
from logger.app_logger import get_logger


class SystemTrayManager(QObject):
    """Manages system tray icon and menu"""
    
    # Signals
    showMainWindow = pyqtSignal()
    hideMainWindow = pyqtSignal()
    startExecution = pyqtSignal()
    pauseExecution = pyqtSignal()
    stopExecution = pyqtSignal()
    showFloatingWidget = pyqtSignal()
    hideFloatingWidget = pyqtSignal()
    quitApplication = pyqtSignal()
    
    def __init__(self, settings: Settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.logger = get_logger(__name__)
        
        # Check if system tray is available
        if not QSystemTrayIcon.isSystemTrayAvailable():
            self.logger.warning("System tray is not available")
            self.tray_icon = None
            return
            
        # Create tray icon
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setToolTip("Excel Macro Automation")
        
        # Set icon
        self._update_icon("idle")
        
        # Create menu
        self._create_menu()
        
        # Connect signals
        self.tray_icon.activated.connect(self._on_tray_activated)
        
        # Animation timer for running state
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self._animate_icon)
        self.animation_frame = 0
        
        # Show tray icon if enabled in settings
        if self.settings.get("notification.system_tray.enabled", True):
            self.show()
            
    def _create_menu(self):
        """Create context menu for tray icon"""
        menu = QMenu()
        
        # Window control
        self.show_window_action = QAction("메인 창 보이기", self)
        self.show_window_action.triggered.connect(self.showMainWindow.emit)
        menu.addAction(self.show_window_action)
        
        self.hide_window_action = QAction("메인 창 숨기기", self)
        self.hide_window_action.triggered.connect(self.hideMainWindow.emit)
        self.hide_window_action.setVisible(False)
        menu.addAction(self.hide_window_action)
        
        menu.addSeparator()
        
        # Execution control
        self.start_action = QAction("실행 시작", self)
        self.start_action.triggered.connect(self.startExecution.emit)
        menu.addAction(self.start_action)
        
        self.pause_action = QAction("일시정지", self)
        self.pause_action.triggered.connect(self.pauseExecution.emit)
        self.pause_action.setEnabled(False)
        menu.addAction(self.pause_action)
        
        self.stop_action = QAction("정지", self)
        self.stop_action.triggered.connect(self.stopExecution.emit)
        self.stop_action.setEnabled(False)
        menu.addAction(self.stop_action)
        
        menu.addSeparator()
        
        # Floating widget control
        self.show_floating_action = QAction("상태 위젯 표시", self)
        self.show_floating_action.triggered.connect(self.showFloatingWidget.emit)
        menu.addAction(self.show_floating_action)
        
        self.hide_floating_action = QAction("상태 위젯 숨기기", self)
        self.hide_floating_action.triggered.connect(self.hideFloatingWidget.emit)
        self.hide_floating_action.setVisible(False)
        menu.addAction(self.hide_floating_action)
        
        menu.addSeparator()
        
        # Quit
        quit_action = QAction("종료", self)
        quit_action.triggered.connect(self.quitApplication.emit)
        menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(menu)
        
    def _create_icon(self, color: QColor, size: int = 16) -> QIcon:
        """Create a colored circle icon"""
        pixmap = QPixmap(size, size)
        pixmap.fill(QColor(0, 0, 0, 0))  # Transparent background
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Draw circle
        painter.setBrush(QBrush(color))
        painter.setPen(QColor(0, 0, 0, 0))
        painter.drawEllipse(1, 1, size-2, size-2)
        
        painter.end()
        
        return QIcon(pixmap)
        
    def _update_icon(self, state: str):
        """Update tray icon based on state"""
        if not self.tray_icon:
            return
            
        color_map = {
            "idle": QColor(128, 128, 128),      # Gray
            "running": QColor(76, 175, 80),     # Green
            "paused": QColor(255, 152, 0),      # Orange
            "error": QColor(244, 67, 54),       # Red
            "preparing": QColor(33, 150, 243)   # Blue
        }
        
        color = color_map.get(state, QColor(128, 128, 128))
        self.tray_icon.setIcon(self._create_icon(color))
        
    def _animate_icon(self):
        """Animate icon during execution"""
        if not self.tray_icon:
            return
            
        # Alternate between green and light green
        colors = [QColor(76, 175, 80), QColor(139, 195, 74)]
        self.tray_icon.setIcon(self._create_icon(colors[self.animation_frame % 2]))
        self.animation_frame += 1
        
    def _on_tray_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            # Toggle main window visibility
            if self.show_window_action.isVisible():
                self.showMainWindow.emit()
            else:
                self.hideMainWindow.emit()
                
    def show(self):
        """Show tray icon"""
        if self.tray_icon:
            self.tray_icon.show()
            
    def hide(self):
        """Hide tray icon"""
        if self.tray_icon:
            self.tray_icon.hide()
            
    def set_main_window_visible(self, visible: bool):
        """Update menu based on main window visibility"""
        if not self.tray_icon:
            return
            
        self.show_window_action.setVisible(not visible)
        self.hide_window_action.setVisible(visible)
        
    def set_floating_widget_visible(self, visible: bool):
        """Update menu based on floating widget visibility"""
        if not self.tray_icon:
            return
            
        self.show_floating_action.setVisible(not visible)
        self.hide_floating_action.setVisible(visible)
        
    def set_execution_state(self, state: str, is_running: bool = False):
        """Update tray based on execution state"""
        if not self.tray_icon:
            return
            
        # Update icon
        self._update_icon(state)
        
        # Update tooltip
        tooltip_map = {
            "idle": "Excel Macro Automation - 대기 중",
            "running": "Excel Macro Automation - 실행 중",
            "paused": "Excel Macro Automation - 일시정지",
            "error": "Excel Macro Automation - 오류",
            "preparing": "Excel Macro Automation - 준비 중"
        }
        
        self.tray_icon.setToolTip(tooltip_map.get(state, "Excel Macro Automation"))
        
        # Update menu actions
        self.start_action.setEnabled(not is_running)
        self.pause_action.setEnabled(is_running and state != "paused")
        self.stop_action.setEnabled(is_running)
        
        # Handle animation
        if state == "running":
            self.animation_timer.start(500)  # Animate every 500ms
        else:
            self.animation_timer.stop()
            
        # Update pause action text
        if state == "paused":
            self.pause_action.setText("재개")
        else:
            self.pause_action.setText("일시정지")
            
    def show_message(self, title: str, message: str, 
                    icon: QSystemTrayIcon.MessageIcon = QSystemTrayIcon.Information,
                    duration: int = 3000):
        """Show tray notification message"""
        if self.tray_icon and self.tray_icon.isVisible():
            self.tray_icon.showMessage(title, message, icon, duration)
            
    def set_progress(self, percentage: int, status_text: str = ""):
        """Update tooltip with progress information"""
        if not self.tray_icon:
            return
            
        tooltip = f"Excel Macro Automation - {percentage}% 완료"
        if status_text:
            tooltip += f"\n{status_text}"
            
        self.tray_icon.setToolTip(tooltip)