"""
Simple ROI selector using screenshot approach
안정적인 스크린샷 기반 영역 선택기
"""

import os
import time
from typing import Optional, Tuple
from PyQt5.QtWidgets import QWidget, QLabel, QRubberBand, QApplication, QDesktopWidget
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor, QCursor, QFont
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
        self.selection_active = False
        
        # Setup window - 안정적인 플래그 조합
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint | 
            Qt.BypassWindowManagerHint
        )
        self.setCursor(Qt.CrossCursor)
        
        # 멀티 모니터 지원
        self._setup_geometry()
        
        # Instructions label
        self.label = QLabel(self)
        self.label.setText("🎯 마우스를 드래그하여 영역을 선택하세요 (ESC: 취소)")
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.label.setFont(font)
        self.label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 200);
                color: white;
                padding: 15px 20px;
                border-radius: 8px;
                border: 2px solid #0066cc;
            }
        """)
        self.label.adjustSize()
        
    def _setup_geometry(self):
        """멀티 모니터 지원을 위한 지오메트리 설정"""
        try:
            desktop = QApplication.desktop()
            
            # 모든 모니터를 포함하는 가상 데스크톱 영역
            virtual_geometry = desktop.virtualGeometry()
            
            print(f"DEBUG: Virtual desktop geometry: {virtual_geometry}")
            print(f"DEBUG: Screen count: {desktop.screenCount()}")
            
            # 각 모니터 정보 출력
            for i in range(desktop.screenCount()):
                screen_rect = desktop.screenGeometry(i)
                print(f"DEBUG: Monitor {i}: {screen_rect}")
            
            # 전체 가상 데스크톱을 커버하도록 설정
            self.setGeometry(virtual_geometry)
            
            # 각 모니터의 정보 저장
            self.monitors = []
            for i in range(desktop.screenCount()):
                self.monitors.append(desktop.screenGeometry(i))
            
        except Exception as e:
            print(f"DEBUG: Geometry setup error: {e}")
            # 기본값으로 primary 화면 사용
            self.setGeometry(desktop.screenGeometry(desktop.primaryScreen()))
        
    def start_selection(self):
        """영역 선택을 시작합니다"""
        print("DEBUG: SimpleROISelector start_selection called")
        self.selection_active = True
        
        try:
            # 즉시 스크린샷을 찍고 표시
            # 더 안정적인 타이밍을 위해 짧은 지연
            QTimer.singleShot(50, self._take_screenshot)
        except Exception as e:
            print(f"DEBUG: Start selection error: {e}")
            self._emit_cancelled()
            
    def _take_screenshot(self):
        """스크린샷을 찍고 선택기를 표시합니다"""
        try:
            print("DEBUG: Taking screenshot...")
            
            # WSL 환경 감지 및 대체 방법 시도
            screenshot = None
            
            # 방법 1: pyautogui 시도 (모든 모니터 캡처)
            try:
                # pyautogui는 기본적으로 모든 모니터를 캡처
                screenshot = pyautogui.screenshot()
                print(f"DEBUG: pyautogui screenshot successful, size: {screenshot.size}")
            except Exception as e:
                print(f"DEBUG: pyautogui failed: {e}")
                
                # 방법 2: mss 라이브러리 사용
                try:
                    import mss
                    with mss.mss() as sct:
                        # monitors[0]는 모든 모니터를 포함하는 가상 데스크톱
                        monitor = sct.monitors[0]
                        print(f"DEBUG: mss virtual monitor: {monitor}")
                        sct_img = sct.grab(monitor)
                        # mss 이미지를 PIL 이미지로 변환
                        from PIL import Image
                        screenshot = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
                        print(f"DEBUG: mss screenshot successful, size: {screenshot.size}")
                except Exception as mss_e:
                    print(f"DEBUG: mss failed: {mss_e}")
                    
                    # 방법 3: 더미 스크린샷 생성 (테스트용)
                    if not screenshot:
                        print("DEBUG: Creating dummy screenshot for testing")
                        from PIL import Image
                        # 가상 데스크톱 크기로 회색 이미지 생성
                        desktop = QApplication.desktop()
                        virtual_rect = desktop.virtualGeometry()
                        screenshot = Image.new('RGB', (virtual_rect.width(), virtual_rect.height()), color=(100, 100, 100))
            
            if not screenshot:
                raise Exception("스크린샷을 찍을 수 없습니다")
            
            # PIL Image를 QPixmap으로 변환
            import io
            buffer = io.BytesIO()
            screenshot.save(buffer, format='PNG')
            buffer.seek(0)
            
            self.screenshot_pixmap = QPixmap()
            success = self.screenshot_pixmap.loadFromData(buffer.read())
            
            if not success or self.screenshot_pixmap.isNull():
                raise Exception("스크린샷을 QPixmap으로 변환할 수 없습니다")
            
            print(f"DEBUG: Screenshot taken: {self.screenshot_pixmap.size()}")
            
            # 라벨 위치 조정 (중앙 상단)
            self.label.move(
                (self.width() - self.label.width()) // 2, 
                20
            )
            
            # 창 표시
            self.show()
            self.raise_()
            self.activateWindow()
            self.setFocus()
            
            # 전체 화면 모드로 설정 (멀티모니터 지원)
            self.showFullScreen()
            
            # 마우스 캡처
            self.setMouseTracking(True)
            self.grabMouse()
            self.grabKeyboard()
            
            print("DEBUG: SimpleROISelector window shown in fullscreen")
            
        except Exception as e:
            print(f"DEBUG: Screenshot error: {e}")
            import traceback
            traceback.print_exc()
            self._emit_cancelled()
            
    def paintEvent(self, event):
        """스크린샷을 배경으로 그리고 선택 영역을 표시합니다"""
        if not self.screenshot_pixmap:
            return
            
        painter = QPainter(self)
        
        # 스크린샷을 배경으로 그리기
        painter.drawPixmap(0, 0, self.screenshot_pixmap)
        
        # 약간 어둡게 처리 (가시성 향상)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 40))
        
        # 현재 선택 영역이 있다면 밝게 표시
        if self.rubber_band and self.rubber_band.isVisible():
            rubber_rect = self.rubber_band.geometry()
            
            # 선택 영역을 원본 밝기로 복원
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            painter.drawPixmap(rubber_rect, self.screenshot_pixmap, rubber_rect)
            
            # 선택 영역 테두리 그리기
            painter.setPen(QPen(QColor(50, 150, 250), 3, Qt.SolidLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(rubber_rect)
            
            # 크기 정보 표시
            if rubber_rect.width() > 50 and rubber_rect.height() > 30:
                painter.setPen(QColor(255, 255, 255))
                font = QFont()
                font.setPointSize(12)
                font.setBold(True)
                painter.setFont(font)
                
                size_text = f"{rubber_rect.width()} × {rubber_rect.height()}"
                text_rect = rubber_rect.adjusted(5, 5, -5, -5)
                painter.drawText(text_rect, Qt.AlignTop | Qt.AlignLeft, size_text)
            
    def mousePressEvent(self, event):
        """마우스 클릭 이벤트 처리"""
        if event.button() == Qt.LeftButton and self.selection_active:
            print(f"DEBUG: Mouse press at {event.pos()}")
            self.origin = event.pos()
            
            # RubberBand 생성 또는 재설정
            if not self.rubber_band:
                self.rubber_band = QRubberBand(QRubberBand.Rectangle, self)
                self.rubber_band.setStyleSheet("""
                    QRubberBand {
                        border: 3px solid rgb(50, 150, 250);
                        background-color: rgba(50, 150, 250, 20);
                    }
                """)
                
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()))
            self.rubber_band.show()
            self.update()  # 화면 새로고침
            
    def mouseMoveEvent(self, event):
        """마우스 이동 이벤트 처리"""
        if self.rubber_band and event.buttons() == Qt.LeftButton and self.selection_active:
            # 정규화된 사각형으로 설정 (드래그 방향 상관없이)
            rect = QRect(self.origin, event.pos()).normalized()
            self.rubber_band.setGeometry(rect)
            self.update()  # 화면 새로고침
            
    def mouseReleaseEvent(self, event):
        """마우스 놓기 이벤트 처리"""
        if event.button() == Qt.LeftButton and self.rubber_band and self.selection_active:
            rect = self.rubber_band.geometry()
            
            print(f"DEBUG: Mouse release, rect: {rect}")
            
            # 최소 크기 체크 (5x5 픽셀 이상)
            if rect.width() >= 5 and rect.height() >= 5:
                # 선택 영역을 정수 튜플로 변환하여 방출
                region = (int(rect.x()), int(rect.y()), int(rect.width()), int(rect.height()))
                print(f"DEBUG: Emitting selection: {region}")
                self._emit_complete(region)
            else:
                print("DEBUG: Selection too small, cancelling")
                self._emit_cancelled()
            
    def keyPressEvent(self, event):
        """키보드 이벤트 처리"""
        if event.key() == Qt.Key_Escape:
            print("DEBUG: ESC pressed, cancelling selection")
            self._emit_cancelled()
        super().keyPressEvent(event)
    
    def _emit_complete(self, region):
        """선택 완료 시그널 방출"""
        self.selection_active = False
        self.selectionComplete.emit(region)
        self._cleanup_and_close()
        
    def _emit_cancelled(self):
        """선택 취소 시그널 방출"""
        self.selection_active = False
        self.selectionCancelled.emit()
        self._cleanup_and_close()
        
    def _cleanup_and_close(self):
        """정리 작업 후 창 닫기"""
        try:
            # 마우스와 키보드 해제 (중요!)
            self.releaseMouse()
            self.releaseKeyboard()
            
            if self.rubber_band:
                self.rubber_band.hide()
                self.rubber_band.deleteLater()
                self.rubber_band = None
            
            self.hide()
            
            # 약간의 지연 후 완전히 삭제
            QTimer.singleShot(100, self.deleteLater)
            
        except Exception as e:
            print(f"DEBUG: Cleanup error: {e}")
            
    def closeEvent(self, event):
        """창 닫기 이벤트 처리"""
        print("DEBUG: SimpleROISelector closeEvent")
        self._cleanup_and_close()
        event.accept()