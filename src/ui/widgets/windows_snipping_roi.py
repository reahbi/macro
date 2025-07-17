"""
Windows Snipping Tool 스타일 ROI 선택기
Windows 환경에 최적화된 안정적인 영역 선택 위젯
"""

from PyQt5.QtWidgets import QWidget, QApplication, QRubberBand
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPixmap, QCursor, QFont


class WindowsSnippingROI(QWidget):
    """Windows Snipping Tool처럼 작동하는 ROI 선택기"""
    
    # 시그널 정의
    selectionComplete = pyqtSignal(tuple)  # (x, y, width, height)
    selectionCancelled = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        print("DEBUG: WindowsSnippingROI __init__")
        
        # 선택 상태
        self.selecting = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.screenshot = None
        self.rubber_band = None
        
        # 윈도우 설정
        self._setup_window()
        
    def _setup_window(self):
        """윈도우 속성 설정"""
        # Windows에 최적화된 플래그
        self.setWindowFlags(
            Qt.FramelessWindowHint |      # 프레임 없음
            Qt.WindowStaysOnTopHint |     # 항상 위
            Qt.Tool |                     # 작업 표시줄에 표시 안함
            Qt.NoDropShadowWindowHint     # 그림자 없음
        )
        
        # 투명 배경 설정
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WA_ShowWithoutActivating, False)
        
        # 마우스 추적 활성화
        self.setMouseTracking(True)
        self.setCursor(Qt.CrossCursor)
        
    def start_selection(self):
        """영역 선택 시작"""
        print("DEBUG: WindowsSnippingROI start_selection")
        
        try:
            # 1. 먼저 스크린샷 찍기
            self._take_screenshot()
            
            # 2. 전체 화면 크기로 설정
            self._setup_fullscreen()
            
            # 3. 윈도우 표시
            self.showFullScreen()
            self.raise_()
            self.activateWindow()
            
            # 4. 포커스 설정 (약간의 지연 후)
            QTimer.singleShot(50, self._ensure_focus)
            
        except Exception as e:
            print(f"ERROR: Failed to start selection: {e}")
            self.selectionCancelled.emit()
            self.close()
            
    def _take_screenshot(self):
        """전체 화면 스크린샷 찍기"""
        print("DEBUG: Taking screenshot")
        
        # QApplication의 primaryScreen 사용
        screen = QApplication.primaryScreen()
        if screen:
            self.screenshot = screen.grabWindow(0)
            print(f"DEBUG: Screenshot size: {self.screenshot.size()}")
        else:
            raise Exception("No primary screen found")
            
    def _setup_fullscreen(self):
        """전체 화면 설정"""
        desktop = QApplication.desktop()
        if desktop:
            # 모든 화면을 포함하는 영역 계산
            total_rect = QRect()
            for i in range(desktop.screenCount()):
                screen_rect = desktop.screenGeometry(i)
                total_rect = total_rect.united(screen_rect)
            
            self.setGeometry(total_rect)
            print(f"DEBUG: Total screen area: {total_rect}")
        else:
            # 기본값 사용
            self.setGeometry(0, 0, 1920, 1080)
            
    def _ensure_focus(self):
        """포커스 확실히 가져오기"""
        print("DEBUG: Ensuring focus")
        self.setFocus(Qt.OtherFocusReason)
        self.grabKeyboard()  # 키보드 입력 캡처
        
    def mousePressEvent(self, event):
        """마우스 클릭 이벤트"""
        if event.button() == Qt.LeftButton:
            print(f"DEBUG: Mouse press at {event.pos()}")
            self.selecting = True
            self.start_point = event.pos()
            self.end_point = event.pos()
            
            # QRubberBand 생성
            if not self.rubber_band:
                self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
                self.rubber_band.setStyleSheet("""
                    QRubberBand {
                        border: 2px solid #0078D4;
                        background-color: rgba(0, 120, 212, 30);
                    }
                """)
            
            self.rubber_band.setGeometry(QRect(self.start_point, self.end_point))
            self.rubber_band.show()
            
    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트"""
        if self.selecting and event.buttons() == Qt.LeftButton:
            self.end_point = event.pos()
            # 정규화된 사각형으로 설정
            rect = QRect(self.start_point, self.end_point).normalized()
            self.rubber_band.setGeometry(rect)
            self.update()  # 화면 업데이트
            
    def mouseReleaseEvent(self, event):
        """마우스 놓기 이벤트"""
        if event.button() == Qt.LeftButton and self.selecting:
            print(f"DEBUG: Mouse release at {event.pos()}")
            self.selecting = False
            
            # 선택 영역 계산
            rect = QRect(self.start_point, self.end_point).normalized()
            
            # 최소 크기 체크
            if rect.width() > 5 and rect.height() > 5:
                region = (rect.x(), rect.y(), rect.width(), rect.height())
                print(f"DEBUG: Selection complete: {region}")
                self._complete_selection(region)
            else:
                print("DEBUG: Selection too small, cancelling")
                self._cancel_selection()
                
    def keyPressEvent(self, event):
        """키보드 이벤트"""
        if event.key() == Qt.Key_Escape:
            print("DEBUG: ESC pressed, cancelling")
            self._cancel_selection()
        elif event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            # Enter 키로도 현재 선택 확정
            if self.rubber_band and self.rubber_band.isVisible():
                rect = self.rubber_band.geometry()
                if rect.width() > 5 and rect.height() > 5:
                    region = (rect.x(), rect.y(), rect.width(), rect.height())
                    self._complete_selection(region)
                    
    def paintEvent(self, event):
        """화면 그리기"""
        if not self.screenshot:
            return
            
        painter = QPainter(self)
        
        # 1. 스크린샷 그리기
        painter.drawPixmap(0, 0, self.screenshot)
        
        # 2. 전체 화면에 반투명 어두운 오버레이
        painter.fillRect(self.rect(), QColor(0, 0, 0, 120))
        
        # 3. 선택 영역은 밝게 (원본 스크린샷 보이도록)
        if self.rubber_band and self.rubber_band.isVisible():
            rect = self.rubber_band.geometry()
            
            # 선택 영역의 스크린샷 부분을 다시 그리기
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.drawPixmap(rect, self.screenshot, rect)
            
            # 선택 영역 테두리
            painter.setPen(QPen(QColor(0, 120, 212), 2, Qt.SolidLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(rect)
            
            # 크기 정보 표시
            if rect.width() > 50 and rect.height() > 30:
                painter.setPen(QColor(255, 255, 255))
                font = QFont("Segoe UI", 10)
                painter.setFont(font)
                
                size_text = f"{rect.width()} × {rect.height()}"
                info_rect = rect.adjusted(5, 5, -5, -5)
                
                # 배경 박스
                text_rect = painter.fontMetrics().boundingRect(size_text)
                bg_rect = text_rect.adjusted(-5, -2, 5, 2)
                bg_rect.moveTopLeft(info_rect.topLeft())
                
                painter.fillRect(bg_rect, QColor(0, 0, 0, 180))
                painter.drawText(info_rect, Qt.AlignTop | Qt.AlignLeft, size_text)
                
        # 4. 도움말 텍스트
        painter.setPen(QColor(255, 255, 255))
        font = QFont("Segoe UI", 12)
        painter.setFont(font)
        
        help_text = "마우스를 드래그하여 영역을 선택하세요. ESC: 취소"
        text_rect = painter.fontMetrics().boundingRect(help_text)
        
        # 중앙 상단에 표시
        x = (self.width() - text_rect.width()) // 2
        y = 30
        
        # 배경 박스
        bg_rect = text_rect.adjusted(-20, -10, 20, 10)
        bg_rect.moveTopLeft(QPoint(x - 20, y - 10))
        
        painter.fillRect(bg_rect, QColor(0, 0, 0, 200))
        painter.drawText(x, y + text_rect.height() - 10, help_text)
        
    def _complete_selection(self, region):
        """선택 완료"""
        print(f"DEBUG: Completing selection: {region}")
        
        # 키보드 해제
        self.releaseKeyboard()
        
        # 시그널 발생
        self.selectionComplete.emit(region)
        
        # 창 닫기
        self.hide()
        
        # 약간의 지연 후 정리
        QTimer.singleShot(100, self._cleanup)
        
    def _cancel_selection(self):
        """선택 취소"""
        print("DEBUG: Cancelling selection")
        
        # 키보드 해제
        self.releaseKeyboard()
        
        # 시그널 발생
        self.selectionCancelled.emit()
        
        # 창 닫기
        self.hide()
        
        # 약간의 지연 후 정리
        QTimer.singleShot(100, self._cleanup)
        
    def _cleanup(self):
        """리소스 정리"""
        print("DEBUG: Cleaning up WindowsSnippingROI")
        
        # Rubber band 정리
        if self.rubber_band:
            self.rubber_band.hide()
            self.rubber_band.deleteLater()
            self.rubber_band = None
            
        # 스크린샷 정리
        self.screenshot = None
        
        # 위젯 삭제
        self.deleteLater()
        
    def closeEvent(self, event):
        """창 닫기 이벤트"""
        print("DEBUG: WindowsSnippingROI closeEvent")
        self._cleanup()
        event.accept()