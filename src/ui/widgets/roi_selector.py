"""
Region of Interest (ROI) selector widget with transparent overlay
"""

from typing import Optional, Tuple, Callable
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPixmap, QFont, QCursor
import sys

class ROISelectorOverlay(QWidget):
    """Transparent overlay for ROI selection"""
    
    # Signals
    selectionComplete = pyqtSignal(tuple)  # (x, y, width, height)
    selectionCancelled = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Selection state
        self.selecting = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.selection_rect = QRect()
        
        # UI setup
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setCursor(Qt.CrossCursor)
        
        # Cover all screens
        self._setup_multi_monitor()
        
        # Styling
        self.overlay_color = QColor(0, 0, 0, 100)  # Semi-transparent black
        self.selection_color = QColor(50, 150, 250, 100)  # Semi-transparent blue
        self.border_color = QColor(50, 150, 250, 255)  # Solid blue
        self.text_color = QColor(255, 255, 255, 255)  # White
        
    def _setup_multi_monitor(self):
        """Setup to cover all monitors"""
        # Get combined screen geometry
        desktop = QApplication.desktop()
        total_rect = QRect()
        
        for i in range(desktop.screenCount()):
            screen_rect = desktop.screenGeometry(i)
            total_rect = total_rect.united(screen_rect)
            
        self.setGeometry(total_rect)
        
    def start_selection(self):
        """Start ROI selection"""
        self.show()
        self.raise_()
        self.activateWindow()
        self.grabMouse()
        self.grabKeyboard()
        
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.LeftButton:
            self.selecting = True
            self.start_point = event.globalPos()
            self.end_point = self.start_point
            self.update()
            
    def mouseMoveEvent(self, event):
        """Handle mouse move"""
        if self.selecting:
            self.end_point = event.globalPos()
            self.update()
            
    def mouseReleaseEvent(self, event):
        """Handle mouse release"""
        if event.button() == Qt.LeftButton and self.selecting:
            self.selecting = False
            self.end_point = event.globalPos()
            
            # Calculate selection rectangle
            x = min(self.start_point.x(), self.end_point.x())
            y = min(self.start_point.y(), self.end_point.y())
            w = abs(self.end_point.x() - self.start_point.x())
            h = abs(self.end_point.y() - self.start_point.y())
            
            # Emit result if selection is valid
            if w > 5 and h > 5:
                self.selectionComplete.emit((x, y, w, h))
            
            self.close()
            
    def keyPressEvent(self, event):
        """Handle key press"""
        if event.key() == Qt.Key_Escape:
            self.selecting = False
            self.selectionCancelled.emit()
            self.close()
            
    def paintEvent(self, event):
        """Paint overlay and selection"""
        painter = QPainter(self)
        
        # Draw semi-transparent overlay
        painter.fillRect(self.rect(), self.overlay_color)
        
        if self.selecting or (self.start_point and self.end_point):
            # Calculate selection rectangle
            x = min(self.start_point.x(), self.end_point.x())
            y = min(self.start_point.y(), self.end_point.y())
            w = abs(self.end_point.x() - self.start_point.x())
            h = abs(self.end_point.y() - self.start_point.y())
            
            # Adjust to widget coordinates
            selection = QRect(x - self.x(), y - self.y(), w, h)
            
            # Clear selection area (make it transparent)
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(selection, Qt.transparent)
            
            # Draw selection border
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.setPen(QPen(self.border_color, 2, Qt.SolidLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(selection)
            
            # Draw dimensions text
            if w > 50 and h > 30:
                painter.setPen(self.text_color)
                font = QFont()
                font.setPointSize(12)
                font.setBold(True)
                painter.setFont(font)
                
                text = f"{w} × {h}"
                text_rect = selection.adjusted(5, 5, -5, -5)
                painter.drawText(text_rect, Qt.AlignTop | Qt.AlignLeft, text)
                
            # Draw corner handles
            self._draw_handles(painter, selection)
            
    def _draw_handles(self, painter: QPainter, rect: QRect):
        """Draw resize handles at corners"""
        handle_size = 8
        painter.setBrush(QBrush(self.border_color))
        painter.setPen(Qt.NoPen)
        
        # Top-left
        painter.drawRect(rect.x() - handle_size//2, 
                        rect.y() - handle_size//2,
                        handle_size, handle_size)
        
        # Top-right
        painter.drawRect(rect.x() + rect.width() - handle_size//2,
                        rect.y() - handle_size//2,
                        handle_size, handle_size)
        
        # Bottom-left
        painter.drawRect(rect.x() - handle_size//2,
                        rect.y() + rect.height() - handle_size//2,
                        handle_size, handle_size)
        
        # Bottom-right
        painter.drawRect(rect.x() + rect.width() - handle_size//2,
                        rect.y() + rect.height() - handle_size//2,
                        handle_size, handle_size)
                        
    def close(self):
        """Clean up and close"""
        self.releaseMouse()
        self.releaseKeyboard()
        super().close()

class ROISelectorWidget(QWidget):
    """Widget for ROI selection with preview"""
    
    regionSelected = pyqtSignal(tuple)  # (x, y, width, height)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_region: Optional[Tuple[int, int, int, int]] = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Preview label
        self.preview_label = QLabel()
        self.preview_label.setMinimumSize(200, 150)
        self.preview_label.setMaximumSize(400, 300)
        self.preview_label.setScaledContents(True)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px solid #ccc;
                background-color: #f0f0f0;
            }
        """)
        self.preview_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.preview_label)
        
        # Info label
        self.info_label = QLabel("No region selected")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)
        
        self.setLayout(layout)
        
    def start_selection(self):
        """Start ROI selection"""
        self.selector = ROISelectorOverlay()
        self.selector.selectionComplete.connect(self._on_selection_complete)
        self.selector.selectionCancelled.connect(self._on_selection_cancelled)
        self.selector.start_selection()
        
    def _on_selection_complete(self, region: Tuple[int, int, int, int]):
        """Handle selection completion"""
        self.current_region = region
        self.info_label.setText(f"Region: {region[0]}, {region[1]} - {region[2]}×{region[3]}")
        self.regionSelected.emit(region)
        
        # Capture and show preview
        self._update_preview()
        
    def _on_selection_cancelled(self):
        """Handle selection cancellation"""
        self.info_label.setText("Selection cancelled")
        
    def _update_preview(self):
        """Update preview of selected region"""
        if not self.current_region:
            return
            
        try:
            # Capture the selected region
            import mss
            import numpy as np
            from PIL import Image
            
            with mss.mss() as sct:
                monitor = {
                    "left": self.current_region[0],
                    "top": self.current_region[1],
                    "width": self.current_region[2],
                    "height": self.current_region[3]
                }
                
                screenshot = sct.grab(monitor)
                img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                
                # Convert to QPixmap
                qpixmap = QPixmap.fromImage(self._pil_to_qimage(img))
                self.preview_label.setPixmap(qpixmap)
                
        except Exception as e:
            self.info_label.setText(f"Preview error: {str(e)}")
            
    def _pil_to_qimage(self, pil_image):
        """Convert PIL image to QImage"""
        from PyQt5.QtGui import QImage
        
        if pil_image.mode == "RGB":
            r, g, b = pil_image.split()
            pil_image = Image.merge("RGB", (b, g, r))
        elif pil_image.mode == "RGBA":
            r, g, b, a = pil_image.split()
            pil_image = Image.merge("RGBA", (b, g, r, a))
            
        width, height = pil_image.size
        data = pil_image.tobytes("raw", pil_image.mode)
        
        if pil_image.mode == "RGB":
            qimage = QImage(data, width, height, QImage.Format_RGB888)
        elif pil_image.mode == "RGBA":
            qimage = QImage(data, width, height, QImage.Format_RGBA8888)
            
        return qimage
        
    def set_region(self, region: Tuple[int, int, int, int]):
        """Set region programmatically"""
        self.current_region = region
        self.info_label.setText(f"Region: {region[0]}, {region[1]} - {region[2]}×{region[3]}")
        self._update_preview()
        
    def get_region(self) -> Optional[Tuple[int, int, int, int]]:
        """Get current region"""
        return self.current_region