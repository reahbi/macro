"""
안정적인 ROI 선택기 - 즉시 종료 문제 해결 버전
"""

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QRect, QPoint, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QPixmap

class StableROISelector(QWidget):
    """안정적인 ROI 선택기"""
    
    selectionComplete = pyqtSignal(tuple)  # (x, y, width, height)
    selectionCancelled = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        print("DEBUG: StableROISelector __init__")
        
        self.selecting = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        self.overlay_visible = False
        
        # 전체 화면 설정
        self._setup_fullscreen()
        
    def _setup_fullscreen(self):
        """전체 화면 설정"""
        # 윈도우 플래그 설정 (WA_DeleteOnClose 없음)
        self.setWindowFlags(
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint |
            Qt.BypassWindowManagerHint
        )
        
        # 투명 배경
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        
        # 마우스 추적 활성화
        self.setMouseTracking(True)
        self.setCursor(Qt.CrossCursor)
        
        # 전체 화면 크기 설정
        desktop = QApplication.desktop()
        total_rect = QRect()
        for i in range(desktop.screenCount()):
            screen_rect = desktop.screenGeometry(i)
            total_rect = total_rect.united(screen_rect)
        self.setGeometry(total_rect)
        
        print(f"DEBUG: Screen geometry set to {total_rect}")
        
    def start_selection(self):
        """선택 시작"""
        print("DEBUG: StableROISelector start_selection")
        self.overlay_visible = True
        self.selecting = False
        self.start_point = QPoint()
        self.end_point = QPoint()
        
        # 윈도우 표시
        self.show()
        self.raise_()
        self.activateWindow()
        
        # 포커스 설정 (짧은 지연 후)
        QTimer.singleShot(50, self._setup_focus)
        
    def _setup_focus(self):
        """포커스 및 입력 설정"""
        print("DEBUG: Setting up focus")
        try:
            self.setFocus(Qt.OtherFocusReason)
            # grabMouse/grabKeyboard 대신 이벤트 필터 사용
            QApplication.instance().installEventFilter(self)
            print("DEBUG: Focus setup complete")
        except Exception as e:
            print(f"DEBUG: Focus setup error: {e}")
            
    def eventFilter(self, obj, event):
        """글로벌 이벤트 필터"""
        if not self.overlay_visible:
            return False
            
        # ESC 키 처리
        if event.type() == event.KeyPress and event.key() == Qt.Key_Escape:
            print("DEBUG: ESC pressed via event filter")
            self._cancel_selection()
            return True
            
        return False
        
    def mousePressEvent(self, event):
        """마우스 클릭"""
        if event.button() == Qt.LeftButton:
            print(f"DEBUG: Mouse press at {event.globalPos()}")
            self.selecting = True
            self.start_point = event.globalPos()
            self.end_point = self.start_point
            self.update()
            
    def mouseMoveEvent(self, event):
        """마우스 이동"""
        if self.selecting:
            self.end_point = event.globalPos()
            self.update()
            
    def mouseReleaseEvent(self, event):
        """마우스 놓기"""
        if event.button() == Qt.LeftButton and self.selecting:
            print(f"DEBUG: Mouse release at {event.globalPos()}")
            self.selecting = False
            
            # 선택 영역 계산
            x = min(self.start_point.x(), self.end_point.x())
            y = min(self.start_point.y(), self.end_point.y())
            w = abs(self.end_point.x() - self.start_point.x())
            h = abs(self.end_point.y() - self.start_point.y())
            
            if w > 5 and h > 5:
                region = (int(x), int(y), int(w), int(h))
                print(f"DEBUG: Selection complete: {region}")
                self._complete_selection(region)
            else:
                print("DEBUG: Selection too small")
                self._cancel_selection()
                
    def keyPressEvent(self, event):
        """키보드 이벤트"""
        if event.key() == Qt.Key_Escape:
            print("DEBUG: ESC pressed")
            self._cancel_selection()
            
    def paintEvent(self, event):
        """화면 그리기"""
        if not self.overlay_visible:
            return
            
        painter = QPainter(self)
        
        # 반투명 배경
        painter.fillRect(self.rect(), QColor(0, 0, 0, 80))
        
        # 선택 영역 그리기
        if self.selecting:
            # 전역 좌표를 위젯 좌표로 변환
            x = min(self.start_point.x(), self.end_point.x())
            y = min(self.start_point.y(), self.end_point.y())
            w = abs(self.end_point.x() - self.start_point.x())
            h = abs(self.end_point.y() - self.start_point.y())
            
            selection_rect = QRect(x, y, w, h)
            local_rect = self.mapFromGlobal(selection_rect.topLeft())
            selection = QRect(local_rect, selection_rect.size())
            
            # 선택 영역 내부를 투명하게
            painter.setCompositionMode(QPainter.CompositionMode_Clear)
            painter.fillRect(selection, Qt.transparent)
            painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
            
            # 테두리 그리기
            painter.setPen(QPen(QColor(50, 150, 250), 3, Qt.SolidLine))
            painter.setBrush(Qt.NoBrush)
            painter.drawRect(selection)
            
            # 크기 정보
            if w > 50 and h > 30:
                painter.setPen(QColor(255, 255, 255))
                text = f"{w} × {h}"
                text_rect = selection.adjusted(5, 5, -5, -5)
                painter.drawText(text_rect, Qt.AlignTop | Qt.AlignLeft, text)
                
        # 안내 텍스트
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(painter.font())
        instructions = "마우스를 드래그하여 영역을 선택하세요. ESC로 취소"
        painter.drawText(self.rect().adjusted(0, 50, 0, 0), 
                        Qt.AlignTop | Qt.AlignHCenter, instructions)
        
    def _complete_selection(self, region):
        """선택 완료"""
        self.overlay_visible = False
        QApplication.instance().removeEventFilter(self)
        self.selectionComplete.emit(region)
        self.hide()
        # deleteLater 호출하지 않음 (재사용 가능)
        
    def _cancel_selection(self):
        """선택 취소"""
        self.overlay_visible = False
        QApplication.instance().removeEventFilter(self)
        self.selectionCancelled.emit()
        self.hide()
        # deleteLater 호출하지 않음 (재사용 가능)