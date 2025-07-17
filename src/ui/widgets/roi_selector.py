"""
Region of Interest (ROI) selector widget with transparent overlay
"""

from typing import Optional, Tuple, Callable
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QDialog
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPixmap, QFont, QCursor, QPalette
import sys

class ROISelectorOverlay(QDialog):
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
        # Use flags that work well on Windows
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Dialog)
        self.setModal(True)
        
        # Make window transparent
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(1.0)
        
        # Cursor and mouse tracking
        self.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.StrongFocus)
        
        # Cover all screens
        self._setup_multi_monitor()
        
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
        print("DEBUG: ROI start_selection called")
        
        # Ensure window covers full screen
        desktop = QApplication.desktop()
        screen_rect = desktop.screenGeometry()
        self.setGeometry(screen_rect)
        
        # Show window using exec_ for modal dialog
        print(f"DEBUG: Showing ROI window at {screen_rect}")
        
        # Start with a slight delay to ensure proper display
        QTimer.singleShot(100, self._prepare_selection)
        
        # Show as modal dialog
        self.exec_()
        
    def _prepare_selection(self):
        """Prepare for selection after dialog is shown"""
        print("DEBUG: _prepare_selection called")
        self.raise_()
        self.activateWindow()
        self.grabMouse()
        self.grabKeyboard()
        self.update()
        
    def _grab_input(self):
        """Grab mouse and keyboard input after delay"""
        print("DEBUG: _grab_input called")
        try:
            self.grabMouse()
            self.grabKeyboard()
            self.setFocus()
            print("DEBUG: Input grabbed successfully")
        except Exception as e:
            print(f"DEBUG: Error grabbing input: {e}")
        
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
                region = (int(x), int(y), int(w), int(h))
                self.selectionComplete.emit(region)
            
            self.close()
            
    def keyPressEvent(self, event):
        """Handle key press"""
        if event.key() == Qt.Key_Escape:
            self.selecting = False
            self.selectionCancelled.emit()
            self.close()
            
    def paintEvent(self, event):
        """Paint overlay and selection"""
        print("DEBUG: paintEvent called")
        painter = QPainter(self)
        
        # Fill with semi-transparent color (reduced opacity for better visibility)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80))
        
        # If selecting, clear the selection area for better visibility
        if self.selecting or (self.start_point and self.end_point):
            # Calculate selection rectangle
            x = min(self.start_point.x(), self.end_point.x())
            y = min(self.start_point.y(), self.end_point.y())
            w = abs(self.end_point.x() - self.start_point.x())
            h = abs(self.end_point.y() - self.start_point.y())
            
            # Adjust to widget coordinates
            selection = QRect(x - self.x(), y - self.y(), w, h)
            
            # Clear the selection area (make it transparent)
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(selection, Qt.transparent)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            
            # Draw selection border
            painter.setPen(QPen(QColor(50, 150, 250), 3, Qt.SolidLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(selection)
        
        # Draw visible text
        painter.setPen(QColor(255, 255, 255))
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        painter.setFont(font)
        
        instructions = "마우스를 드래그하여 영역을 선택하세요. ESC로 취소"
        rect = self.rect()
        rect.setTop(50)
        painter.drawText(rect, Qt.AlignTop | Qt.AlignHCenter, instructions)
        
        if self.selecting or (self.start_point and self.end_point):
            
            # Draw dimensions text
            if w > 50 and h > 30:
                painter.setPen(QColor(255, 255, 255))
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
        painter.setBrush(QBrush(QColor(50, 150, 250)))
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
        print("DEBUG: ROI close() called")
        self.releaseMouse()
        self.releaseKeyboard()
        self.accept()  # Close the dialog properly

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
        self.info_label = QLabel("선택된 영역 없음")
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
        self.info_label.setText(f"영역: {region[0]}, {region[1]} - {region[2]}×{region[3]}")
        self.regionSelected.emit(region)
        
        # Capture and show preview
        self._update_preview()
        
    def _on_selection_cancelled(self):
        """Handle selection cancellation"""
        self.info_label.setText("선택 취소됨")
        
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
        
    def set_region(self, region: Optional[Tuple[int, int, int, int]]):
        """Set region programmatically"""
        self.current_region = region
        if region:
            self.info_label.setText(f"영역: {region[0]}, {region[1]} - {region[2]}×{region[3]}")
            self._update_preview()
        else:
            self.info_label.setText("선택된 영역 없음")
            self.preview_label.clear()
        
    def get_region(self) -> Optional[Tuple[int, int, int, int]]:
        """Get current region"""
        return self.current_region