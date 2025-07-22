"""
Workflow mode selection dialog for choosing between Excel workflow and normal macro mode
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QWidget, QFrame, QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor

class WorkflowModeDialog(QDialog):
    """Dialog for selecting workflow mode at startup"""
    
    # Signals
    excel_mode_selected = pyqtSignal()
    normal_mode_selected = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("작업 모드 선택")
        self.setModal(True)
        self.setMinimumSize(600, 400)
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        # Main layout
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("작업 모드를 선택하세요")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Description
        desc = QLabel("Excel 파일의 데이터를 기반으로 반복 작업을 하시겠습니까?\n아니면 일반적인 매크로를 만드시겠습니까?")
        desc.setAlignment(Qt.AlignCenter)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Mode selection container
        mode_container = QHBoxLayout()
        mode_container.setSpacing(20)
        
        # Excel mode card
        excel_card = self.create_mode_card(
            "Excel 반복 작업",
            "📊",
            "Excel 데이터로\n반복 실행",
            "• Excel 파일의 각 행마다 자동 실행\n"
            "• 대량 데이터 처리에 최적\n"
            "• 병원, 사무실 업무 자동화",
            self.on_excel_mode_clicked
        )
        mode_container.addWidget(excel_card)
        
        # Normal mode card
        normal_card = self.create_mode_card(
            "일반 매크로",
            "🖱️",
            "단순 클릭/입력\n작업",
            "• 마우스와 키보드 동작 녹화\n"
            "• 단일 작업 자동화\n"
            "• 반복적인 클릭 작업",
            self.on_normal_mode_clicked
        )
        mode_container.addWidget(normal_card)
        
        layout.addLayout(mode_container)
        
        # Spacer
        layout.addStretch()
        
    def create_mode_card(self, title: str, icon: str, subtitle: str, 
                        description: str, click_handler) -> QWidget:
        """Create a mode selection card"""
        # Card container
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet("""
            QFrame {
                border: 2px solid #ddd;
                border-radius: 10px;
                background-color: #f9f9f9;
            }
            QFrame:hover {
                border: 2px solid #4CAF50;
                background-color: #f0f8f0;
            }
        """)
        card.setCursor(Qt.PointingHandCursor)
        card.setMinimumSize(250, 300)
        
        # Card layout
        card_layout = QVBoxLayout(card)
        card_layout.setSpacing(15)
        card_layout.setContentsMargins(20, 20, 20, 20)
        
        # Icon
        icon_label = QLabel(icon)
        icon_font = QFont()
        icon_font.setPointSize(48)
        icon_label.setFont(icon_font)
        icon_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(title)
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(title_label)
        
        # Subtitle
        subtitle_label = QLabel(subtitle)
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_label.setFont(subtitle_font)
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setWordWrap(True)
        card_layout.addWidget(subtitle_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignLeft)
        desc_label.setStyleSheet("color: #666;")
        card_layout.addWidget(desc_label)
        
        # Spacer
        card_layout.addStretch()
        
        # Button
        button = QPushButton("선택")
        button.setMinimumHeight(40)
        button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        button.clicked.connect(click_handler)
        card_layout.addWidget(button)
        
        # Make entire card clickable
        card.mousePressEvent = lambda event: click_handler()
        
        return card
        
    def on_excel_mode_clicked(self):
        """Handle Excel mode selection"""
        self.excel_mode_selected.emit()
        self.accept()
        
    def on_normal_mode_clicked(self):
        """Handle normal mode selection"""
        self.normal_mode_selected.emit()
        self.accept()