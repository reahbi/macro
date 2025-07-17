"""
Region of Interest (ROI) selector widget with transparent overlay
(수정된 버전)
"""

from typing import Optional, Tuple
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout, QDialog
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPixmap, QFont
import sys

class ROISelectorOverlay(QDialog):
    """Transparent overlay for ROI selection"""
    
    selectionComplete = pyqtSignal(tuple)
    selectionCancelled = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        print("DEBUG: ROISelectorOverlay __init__ called")
        
        self.selecting = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        
        # --- 수정된 부분 1: 윈도우 플래그 및 속성 ---
        # Qt.Tool 플래그를 추가하여 작업 표시줄에 나타나지 않도록 하고,
        # WA_DeleteOnClose는 제거하여 즉시 종료 문제를 방지합니다.
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # self.setAttribute(Qt.WA_DeleteOnClose) # 즉시 종료 문제로 인해 제거
        
        self.setCursor(Qt.CrossCursor)
        self.setMouseTracking(True)
        
        self._setup_multi_monitor()
        
    def _setup_multi_monitor(self):
        desktop = QApplication.desktop()
        total_rect = QRect()
        for i in range(desktop.screenCount()):
            screen_rect = desktop.screenGeometry(i)
            total_rect = total_rect.united(screen_rect)
        self.setGeometry(total_rect)
        
    def start_selection(self):
        """ROI 선택을 비동기(non-modal) 방식으로 시작합니다."""
        print("DEBUG: ROI start_selection called")
        
        # 창을 먼저 표시하고 활성화
        self.show()
        self.activateWindow()
        self.raise_()
        
        # 짧은 지연 후 마우스와 키보드를 캡처
        QTimer.singleShot(100, self._grab_input)
    
    def _grab_input(self):
        """입력 장치를 캡처합니다."""
        print("DEBUG: Grabbing mouse and keyboard")
        try:
            self.grabMouse()
            self.grabKeyboard()
            self.setFocus()
        except Exception as e:
            print(f"DEBUG: Error grabbing input: {e}")
            self.selectionCancelled.emit()
            self.hide()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.selecting = True
            self.start_point = event.globalPos()
            self.end_point = self.start_point
            self.update()
            
    def mouseMoveEvent(self, event):
        if self.selecting:
            self.end_point = event.globalPos()
            self.update()
            
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.selecting:
            self.selecting = False
            
            x = min(self.start_point.x(), self.end_point.x())
            y = min(self.start_point.y(), self.end_point.y())
            w = abs(self.end_point.x() - self.start_point.x())
            h = abs(self.end_point.y() - self.start_point.y())
            
            if w > 5 and h > 5:
                region = (int(x), int(y), int(w), int(h))
                self.selectionComplete.emit(region)
            else:
                # 너무 작게 드래그하면 취소로 간주
                self.selectionCancelled.emit()
            
            # --- 수정된 부분 2: hide() 호출로 변경 ---
            # 선택이 끝나면 창을 숨깁니다.
            self.hide()
            self.releaseMouse()
            self.releaseKeyboard()
            
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.selecting = False
            self.selectionCancelled.emit()
            # --- 수정된 부분 3: hide() 호출로 변경 ---
            self.hide()
            self.releaseMouse()
            self.releaseKeyboard()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80))
        
        if self.selecting:
            x = min(self.start_point.x(), self.end_point.x())
            y = min(self.start_point.y(), self.end_point.y())
            w = abs(self.end_point.x() - self.start_point.x())
            h = abs(self.end_point.y() - self.start_point.y())
            selection_rect = QRect(x, y, w, h)
            
            # 전역 좌표를 위젯의 로컬 좌표로 변환
            local_selection_rect = self.mapFromGlobal(selection_rect.topLeft())
            selection = QRect(local_selection_rect, selection_rect.size())

            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(selection, Qt.transparent)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            
            painter.setPen(QPen(QColor(50, 150, 250), 3, Qt.SolidLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(selection)
            
            self._draw_handles(painter, selection)

            # 크기 정보 텍스트 그리기
            if w > 50 and h > 30:
                painter.setPen(QColor(255, 255, 255))
                font = QFont()
                font.setPointSize(12)
                font.setBold(True)
                painter.setFont(font)
                text = f"{w} × {h}"
                text_rect = selection.adjusted(5, 5, -5, -5)
                painter.drawText(text_rect, Qt.AlignTop | Qt.AlignLeft, text)

        # 안내 텍스트 그리기
        painter.setPen(QColor(255, 255, 255))
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        painter.setFont(font)
        instructions = "마우스를 드래그하여 영역을 선택하세요. ESC로 취소"
        painter.drawText(self.rect().adjusted(0, 50, 0, 0), Qt.AlignTop | Qt.AlignHCenter, instructions)

    def _draw_handles(self, painter: QPainter, rect: QRect):
        handle_size = 8
        painter.setBrush(QBrush(QColor(50, 150, 250)))
        painter.setPen(Qt.NoPen)
        # 핸들 그리는 로직
        painter.drawRect(rect.topLeft().x() - handle_size//2, rect.topLeft().y() - handle_size//2, handle_size, handle_size)
        painter.drawRect(rect.topRight().x() - handle_size//2, rect.topRight().y() - handle_size//2, handle_size, handle_size)
        painter.drawRect(rect.bottomLeft().x() - handle_size//2, rect.bottomLeft().y() - handle_size//2, handle_size, handle_size)
        painter.drawRect(rect.bottomRight().x() - handle_size//2, rect.bottomRight().y() - handle_size//2, handle_size, handle_size)

    # --- 추가된 부분: closeEvent ---
    def closeEvent(self, event):
        """창이 닫힐 때 마우스와 키보드 입력을 반드시 해제합니다."""
        print("DEBUG: ROI closeEvent called")
        self.releaseMouse()
        self.releaseKeyboard()
        event.accept()

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
            
        im_data = pil_image.tobytes("raw", "RGBA" if pil_image.mode == "RGBA" else "RGB")
        
        if pil_image.mode == "RGBA":
            qimage = QImage(im_data, pil_image.width, pil_image.height, QImage.Format_RGBA8888)
        else:
            qimage = QImage(im_data, pil_image.width, pil_image.height, QImage.Format_RGB888)
            
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