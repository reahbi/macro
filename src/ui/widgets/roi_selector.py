"""
Region of Interest (ROI) selector widget with transparent overlay
"""

from typing import Optional, Tuple, Callable, Dict
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QDialog
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPixmap, QFont, QCursor, QPalette
import sys
import mss
from datetime import datetime
import os
from pathlib import Path
from utils.coordinate_utils import get_converter

class ROISelectorOverlay(QDialog):
    """Transparent overlay for ROI selection"""
    
    # Signals
    selectionComplete = pyqtSignal(dict)  # {"region": (x, y, width, height), "monitor_info": {...}}
    selectionCancelled = pyqtSignal()
    
    def __init__(self, parent=None, monitor_bounds=None):
        super().__init__(parent)
        
        # Selection state
        self.selecting = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.selection_rect = QRect()
        self.monitor_bounds = monitor_bounds  # Restrict to specific monitor if provided
        
        # mss instance for consistent coordinate system
        self.sct = mss.mss()
        self.monitors = self.sct.monitors
        self.virtual_monitor = self.monitors[0]  # Combined virtual screen
        
        # Coordinate converter for DPI handling
        self.coord_converter = get_converter()
        
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
        
        # Setup monitor coverage
        if monitor_bounds:
            self._setup_single_monitor(monitor_bounds)
        else:
            self._setup_multi_monitor()
        
    def _setup_multi_monitor(self):
        """Setup to cover all monitors using mss coordinates"""
        # Use mss virtual monitor which covers all screens
        vm = self.virtual_monitor
        # mss uses absolute coordinates including negative values
        self.setGeometry(vm['left'], vm['top'], vm['width'], vm['height'])
        print(f"DEBUG: Multi-monitor setup: {vm}")
        
    def _setup_single_monitor(self, monitor_bounds):
        """Setup to cover a single monitor"""
        x = monitor_bounds['x']
        y = monitor_bounds['y']
        width = monitor_bounds['width']
        height = monitor_bounds['height']
        self.setGeometry(x, y, width, height)
        
    def start_selection(self):
        """Start ROI selection"""
        print("DEBUG: ROI start_selection called")
        
        # Setup monitor coverage is already done in __init__
        
        # Show window using exec_ for modal dialog
        print(f"DEBUG: Showing ROI window")
        
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
            end_point = event.globalPos()
            
            # If monitor bounds are set, constrain the end point
            if self.monitor_bounds:
                min_x = self.monitor_bounds['x']
                min_y = self.monitor_bounds['y']
                max_x = min_x + self.monitor_bounds['width']
                max_y = min_y + self.monitor_bounds['height']
                
                # Clamp the end point to monitor bounds
                end_point.setX(max(min_x, min(end_point.x(), max_x)))
                end_point.setY(max(min_y, min(end_point.y(), max_y)))
            
            self.end_point = end_point
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
                # Validate region
                region = (x, y, w, h)
                if not self.coord_converter.validate_region(region, self.monitor_bounds):
                    print(f"DEBUG: Invalid region selected: {region}")
                    self.selectionCancelled.emit()
                    self.close()
                    return
                
                # Find which monitor contains this region
                monitor_info = self._get_monitor_for_region(x, y, w, h)
                
                # Apply DPI scaling if needed
                dpi_scale = self.coord_converter.get_dpi_scale()
                
                # Create result with absolute coordinates only
                # (mss also uses absolute coordinates, no conversion needed)
                result = {
                    "region": (int(x), int(y), int(w), int(h)),  # Absolute coordinates
                    "monitor_info": monitor_info,
                    "dpi_scale": dpi_scale,
                    "timestamp": datetime.now().isoformat()
                }
                
                print(f"DEBUG: ROI selection complete with result: {result}")
                self.selectionComplete.emit(result)
                print(f"DEBUG: selectionComplete signal emitted")
                
                # Save preview screenshot for debugging
                self._save_preview(x, y, w, h)
            else:
                print(f"DEBUG: ROI selection too small: w={w}, h={h}")
            
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
                        
    def _get_monitor_for_region(self, x: int, y: int, w: int, h: int) -> Dict:
        """Find which monitor contains the center of the region"""
        center_x = x + w // 2
        center_y = y + h // 2
        
        # Check each monitor (skip index 0 which is the virtual monitor)
        for i, monitor in enumerate(self.monitors[1:], 1):
            if (monitor['left'] <= center_x < monitor['left'] + monitor['width'] and
                monitor['top'] <= center_y < monitor['top'] + monitor['height']):
                return {
                    "index": i,
                    "name": f"Monitor {i}",
                    "bounds": {
                        "left": monitor['left'],
                        "top": monitor['top'],
                        "width": monitor['width'],
                        "height": monitor['height']
                    },
                    "relative_region": (
                        x - monitor['left'],
                        y - monitor['top'],
                        w,
                        h
                    )
                }
        
        # Default to primary monitor if not found
        primary = self.monitors[1] if len(self.monitors) > 1 else self.virtual_monitor
        return {
            "index": 1,
            "name": "Primary Monitor",
            "bounds": {
                "left": primary['left'],
                "top": primary['top'],
                "width": primary['width'],
                "height": primary['height']
            },
            "relative_region": (x, y, w, h)
        }
    
    def _save_preview(self, x: int, y: int, w: int, h: int):
        """Save a preview screenshot of the selected region"""
        try:
            # Create debug directory if it doesn't exist
            debug_dir = Path("debug/roi_previews")
            debug_dir.mkdir(parents=True, exist_ok=True)
            
            # Capture the region
            monitor = {"left": x, "top": y, "width": w, "height": h}
            screenshot = self.sct.grab(monitor)
            
            # Save with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = debug_dir / f"roi_preview_{timestamp}.png"
            mss.tools.to_png(screenshot.rgb, screenshot.size, output=str(filename))
            
            print(f"DEBUG: ROI preview saved to {filename}")
            
        except Exception as e:
            print(f"DEBUG: Failed to save ROI preview: {e}")
    
    def close(self):
        """Clean up and close"""
        print("DEBUG: ROI close() called")
        self.releaseMouse()
        self.releaseKeyboard()
        if hasattr(self, 'sct'):
            self.sct.close()
        self.accept()  # Close the dialog properly

class ROISelectorWidget(QWidget):
    """Widget for ROI selection with preview"""
    
    regionSelected = pyqtSignal(tuple)  # (x, y, width, height) - for backward compatibility
    regionSelectedEx = pyqtSignal(dict)  # Extended info with monitor data
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_region: Optional[Tuple[int, int, int, int]] = None
        self.current_region_info: Optional[Dict] = None
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
        
    def _on_selection_complete(self, result: Dict):
        """Handle selection completion"""
        # Extract region for backward compatibility
        region = result["region"]
        self.current_region = region
        self.current_region_info = result
        
        # Update info with monitor details
        monitor_info = result.get("monitor_info", {})
        monitor_name = monitor_info.get("name", "Unknown")
        self.info_label.setText(
            f"영역: {region[0]}, {region[1]} - {region[2]}×{region[3]} "
            f"({monitor_name})"
        )
        
        # Emit both signals
        self.regionSelected.emit(region)  # Backward compatibility
        self.regionSelectedEx.emit(result)  # Extended info
        
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
    
    def get_region_info(self) -> Optional[Dict]:
        """Get extended region info with monitor data"""
        return self.current_region_info