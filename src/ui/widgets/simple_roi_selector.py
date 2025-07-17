"""
Simple ROI selector using screenshot approach
"""

import os
import time
from typing import Optional, Tuple
from PyQt5.QtWidgets import QWidget, QLabel, QRubberBand
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QCursor
import pyautogui


class SimpleROISelector(QWidget):
    """Simple ROI selector that uses screenshot approach"""
    
    selectionComplete = pyqtSignal(tuple)  # (x, y, width, height)
    selectionCancelled = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Selection state
        self.origin = QPoint()
        self.rubber_band = None
        self.screenshot_pixmap = None
        
        # Setup window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setWindowState(Qt.WindowFullScreen)
        self.setCursor(Qt.CrossCursor)
        
        # Instructions label
        self.label = QLabel(self)
        self.label.setText("드래그하여 영역을 선택하세요. ESC: 취소")
        self.label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
            }
        """)
        self.label.adjustSize()
        self.label.move(10, 10)
        
    def start_selection(self):
        """Start ROI selection"""
        # Take screenshot first
        try:
            # Hide any windows
            QTimer.singleShot(100, self._take_screenshot)
        except Exception as e:
            print(f"Screenshot error: {e}")
            self.selectionCancelled.emit()
            self.close()
            
    def _take_screenshot(self):
        """Take screenshot and show selector"""
        try:
            # Take screenshot using pyautogui
            screenshot = pyautogui.screenshot()
            
            # Convert to QPixmap
            import io
            from PIL import Image
            
            # Save to bytes
            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Load as QPixmap
            self.screenshot_pixmap = QPixmap()
            self.screenshot_pixmap.loadFromData(buffer.read())
            
            # Set window size to screen size
            self.resize(self.screenshot_pixmap.size())
            
            # Show window
            self.show()
            self.raise_()
            self.activateWindow()
            
        except Exception as e:
            print(f"Screenshot error: {e}")
            self.selectionCancelled.emit()
            self.close()
            
    def paintEvent(self, event):
        """Paint screenshot as background"""
        if self.screenshot_pixmap:
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self.screenshot_pixmap)
            
            # Darken the screenshot slightly (reduced from 50 to 30 for better visibility)
            painter.fillRect(self.rect(), QColor(0, 0, 0, 30))
            
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            
            if not self.rubber_band:
                self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
                self.rubber_band.setStyleSheet("""
                    QRubberBand {
                        border: 2px solid rgb(50, 150, 250);
                        background-color: rgba(50, 150, 250, 30);
                    }
                """)
                
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()))
            self.rubber_band.show()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move"""
        if self.rubber_band and event.buttons() == Qt.LeftButton:
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton and self.rubber_band:
            rect = self.rubber_band.geometry()
            
            if rect.width() > 5 and rect.height() > 5:
                # Emit the selection - ensure all values are integers
                region = (int(rect.x()), int(rect.y()), int(rect.width()), int(rect.height()))
                self.selectionComplete.emit(region)
            
            self.close()
            
    def keyPressEvent(self, event):
        """Handle key press"""
        if event.key() == Qt.Key_Escape:
            self.selectionCancelled.emit()
            self.close()
            
    def close(self):
        """Clean up and close"""
        if self.rubber_band:
            self.rubber_band.hide()
        super().close()