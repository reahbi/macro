"""
Preparation countdown widget for macro execution
"""

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, pyqtProperty, QRect
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush
import math


class CountdownWidget(QWidget):
    """Circular countdown display widget"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._progress = 100.0
        self._current_value = 5
        self.setFixedSize(200, 200)
        
    @pyqtProperty(float)
    def progress(self):
        return self._progress
        
    @progress.setter
    def progress(self, value):
        self._progress = value
        self.update()
        
    def set_value(self, value: int):
        """Set countdown value"""
        self._current_value = value
        self.update()
        
    def paintEvent(self, event):
        """Custom paint for circular countdown"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background circle
        painter.setPen(QPen(QColor(200, 200, 200), 8))
        painter.setBrush(QBrush(QColor(240, 240, 240)))
        painter.drawEllipse(10, 10, 180, 180)
        
        # Progress arc
        painter.setPen(QPen(QColor(33, 150, 243), 12))
        painter.setBrush(Qt.NoBrush)
        
        # Draw arc (16ths of a degree)
        start_angle = 90 * 16  # Start from top
        span_angle = -int(self._progress * 360 / 100) * 16  # Counter-clockwise
        painter.drawArc(20, 20, 160, 160, start_angle, span_angle)
        
        # Draw number
        painter.setPen(QPen(QColor(50, 50, 50)))
        font = QFont("Arial", 48, QFont.Bold)
        painter.setFont(font)
        
        text = str(self._current_value)
        rect = QRect(0, 0, 200, 200)
        painter.drawText(rect, Qt.AlignCenter, text)


class PreparationWidget(QWidget):
    """Preparation mode widget with countdown"""
    
    # Signals
    startNow = pyqtSignal()
    cancelled = pyqtSignal()
    countdownFinished = pyqtSignal()
    
    def __init__(self, parent=None, countdown_seconds=5):
        super().__init__(parent)
        self.countdown_seconds = countdown_seconds
        self.current_seconds = countdown_seconds
        
        # Window flags for floating
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Timer for countdown
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer)
        
        # Animation for progress
        self.progress_animation = QPropertyAnimation(self, b"windowOpacity")
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        # Main layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Container widget for styling
        container = QWidget()
        container.setObjectName("container")
        container.setStyleSheet("""
            #container {
                background-color: rgba(255, 255, 255, 240);
                border-radius: 15px;
                border: 2px solid #2196F3;
            }
        """)
        
        container_layout = QVBoxLayout()
        container_layout.setSpacing(20)
        
        # Title
        title_label = QLabel("매크로 준비 중...")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #1976D2;
            margin-bottom: 10px;
        """)
        container_layout.addWidget(title_label)
        
        # Countdown widget
        self.countdown_widget = CountdownWidget()
        container_layout.addWidget(self.countdown_widget, alignment=Qt.AlignCenter)
        
        # Info label
        info_label = QLabel("F5: 즉시 시작 | ESC: 취소")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setStyleSheet("""
            font-size: 14px;
            color: #666;
            margin-top: 10px;
        """)
        container_layout.addWidget(info_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        self.start_btn = QPushButton("즉시 시작 (F5)")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.start_btn.clicked.connect(self.start_now)
        button_layout.addWidget(self.start_btn)
        
        self.cancel_btn = QPushButton("취소 (ESC)")
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.cancel_btn.clicked.connect(self.cancel)
        button_layout.addWidget(self.cancel_btn)
        
        container_layout.addLayout(button_layout)
        container.setLayout(container_layout)
        
        layout.addWidget(container)
        self.setLayout(layout)
        
        # Set size
        self.setFixedSize(350, 400)
        
    def start_countdown(self):
        """Start countdown"""
        self.current_seconds = self.countdown_seconds
        self.countdown_widget.set_value(self.current_seconds)
        self.countdown_widget.progress = 100
        
        # Start timer
        self.timer.start(1000)  # 1 second intervals
        
        # Show widget
        self.show()
        self.raise_()
        self.activateWindow()
        
        # Center on screen
        self._center_on_screen()
        
    def _on_timer(self):
        """Handle timer tick"""
        self.current_seconds -= 1
        
        if self.current_seconds <= 0:
            # Countdown finished
            self.timer.stop()
            self.countdownFinished.emit()
            self.hide()
        else:
            # Update display
            self.countdown_widget.set_value(self.current_seconds)
            progress = (self.current_seconds / self.countdown_seconds) * 100
            self.countdown_widget.progress = progress
            
    def start_now(self):
        """Start immediately"""
        self.timer.stop()
        self.startNow.emit()
        self.hide()
        
    def cancel(self):
        """Cancel preparation"""
        self.timer.stop()
        self.cancelled.emit()
        self.hide()
        
    def keyPressEvent(self, event):
        """Handle key press"""
        if event.key() == Qt.Key_F5:
            self.start_now()
        elif event.key() == Qt.Key_Escape:
            self.cancel()
        else:
            super().keyPressEvent(event)
            
    def _center_on_screen(self):
        """Center widget on screen"""
        from PyQt5.QtWidgets import QApplication
        screen = QApplication.primaryScreen()
        screen_rect = screen.geometry()
        
        x = (screen_rect.width() - self.width()) // 2
        y = (screen_rect.height() - self.height()) // 2
        
        self.move(x, y)