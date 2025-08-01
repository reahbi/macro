"""
좌표 변환 테스트 스크립트
다양한 DPI 스케일링 환경에서 Qt와 mss 간의 좌표 변환을 검증합니다.
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel, QTextEdit
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QCursor
import mss
from utils.coordinate_utils import get_converter
from ui.widgets.roi_selector import ROISelectorOverlay
import json


class CoordinateTestWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.coord_converter = get_converter()
        self.sct = mss.mss()
        
    def init_ui(self):
        self.setWindowTitle("좌표 변환 테스트")
        self.setGeometry(100, 100, 600, 800)
        
        layout = QVBoxLayout()
        
        # DPI 정보 표시
        self.dpi_label = QLabel()
        layout.addWidget(self.dpi_label)
        
        # 모니터 정보 표시
        self.monitor_label = QLabel()
        layout.addWidget(self.monitor_label)
        
        # 테스트 버튼들
        test_cursor_btn = QPushButton("현재 커서 위치 테스트")
        test_cursor_btn.clicked.connect(self.test_cursor_position)
        layout.addWidget(test_cursor_btn)
        
        test_roi_btn = QPushButton("ROI 선택 테스트")
        test_roi_btn.clicked.connect(self.test_roi_selection)
        layout.addWidget(test_roi_btn)
        
        test_conversion_btn = QPushButton("좌표 변환 테스트")
        test_conversion_btn.clicked.connect(self.test_coordinate_conversion)
        layout.addWidget(test_conversion_btn)
        
        test_capture_btn = QPushButton("캡처 검증 테스트")
        test_capture_btn.clicked.connect(self.test_capture_verification)
        layout.addWidget(test_capture_btn)
        
        # 결과 표시 영역
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)
        
        self.setLayout(layout)
        
        # 초기 정보 표시
        self.update_system_info()
        
    def update_system_info(self):
        """시스템 정보 업데이트"""
        dpi_scale = self.coord_converter.get_dpi_scale()
        self.dpi_label.setText(f"DPI Scale: {dpi_scale} ({int(dpi_scale * 100)}%)")
        
        # 모니터 정보
        monitor_info = []
        for i, monitor in enumerate(self.sct.monitors):
            if i == 0:
                monitor_info.append(f"Virtual Monitor: {monitor}")
            else:
                monitor_info.append(f"Monitor {i}: {monitor}")
        
        self.monitor_label.setText("모니터 정보:\n" + "\n".join(monitor_info))
        
    def log_result(self, message):
        """결과 로깅"""
        self.result_text.append(message)
        self.result_text.append("-" * 50)
        
    def test_cursor_position(self):
        """현재 커서 위치로 좌표 변환 테스트"""
        self.log_result("=== 커서 위치 테스트 ===")
        
        # Qt에서 커서 위치 가져오기
        qt_pos = QCursor.pos()
        qt_x, qt_y = qt_pos.x(), qt_pos.y()
        self.log_result(f"Qt 커서 위치 (논리적): ({qt_x}, {qt_y})")
        
        # Qt -> mss 변환
        mss_x, mss_y = self.coord_converter.qt_to_mss(qt_x, qt_y)
        self.log_result(f"변환된 mss 좌표 (물리적): ({mss_x}, {mss_y})")
        
        # mss -> Qt 역변환
        back_qt_x, back_qt_y = self.coord_converter.mss_to_qt(mss_x, mss_y)
        self.log_result(f"역변환된 Qt 좌표: ({back_qt_x}, {back_qt_y})")
        
        # 검증
        if qt_x == back_qt_x and qt_y == back_qt_y:
            self.log_result("✅ 좌표 변환 검증 성공!")
        else:
            self.log_result("❌ 좌표 변환 검증 실패!")
            
        # 어느 모니터에 있는지 확인
        monitor_info = self.coord_converter.get_monitor_at_point(mss_x, mss_y)
        if monitor_info:
            self.log_result(f"현재 모니터: Monitor {monitor_info['index']}")
            self.log_result(f"모니터 상대 좌표: ({monitor_info['relative_x']}, {monitor_info['relative_y']})")
            
    def test_roi_selection(self):
        """ROI 선택 테스트"""
        self.log_result("=== ROI 선택 테스트 ===")
        self.log_result("ROI를 선택하세요...")
        
        self.roi_selector = ROISelectorOverlay()
        self.roi_selector.selectionComplete.connect(self.on_roi_selected)
        self.roi_selector.selectionCancelled.connect(lambda: self.log_result("ROI 선택 취소됨"))
        self.roi_selector.start_selection()
        
    def on_roi_selected(self, result):
        """ROI 선택 완료 처리"""
        self.log_result("ROI 선택 완료!")
        self.log_result(f"결과: {json.dumps(result, indent=2, ensure_ascii=False)}")
        
        region = result.get("region")
        if region:
            x, y, w, h = region
            self.log_result(f"선택된 영역 (물리적 픽셀): x={x}, y={y}, width={w}, height={h}")
            
            # 논리적 좌표로 변환
            logical_x, logical_y = self.coord_converter.mss_to_qt(x, y)
            logical_w = int(w / self.coord_converter.get_dpi_scale())
            logical_h = int(h / self.coord_converter.get_dpi_scale())
            self.log_result(f"논리적 좌표: x={logical_x}, y={logical_y}, width={logical_w}, height={logical_h}")
            
    def test_coordinate_conversion(self):
        """다양한 좌표값으로 변환 테스트"""
        self.log_result("=== 좌표 변환 종합 테스트 ===")
        
        dpi_scale = self.coord_converter.get_dpi_scale()
        self.log_result(f"현재 DPI Scale: {dpi_scale}")
        
        # 테스트 케이스
        test_cases = [
            (0, 0),
            (100, 100),
            (500, 500),
            (1920, 1080),
            (-1920, 0),  # 다중 모니터 환경
        ]
        
        for qt_x, qt_y in test_cases:
            self.log_result(f"\n테스트 케이스: Qt({qt_x}, {qt_y})")
            
            # Qt -> mss
            mss_x, mss_y = self.coord_converter.qt_to_mss(qt_x, qt_y)
            self.log_result(f"  Qt -> mss: ({mss_x}, {mss_y})")
            
            # mss -> Qt
            back_qt_x, back_qt_y = self.coord_converter.mss_to_qt(mss_x, mss_y)
            self.log_result(f"  mss -> Qt: ({back_qt_x}, {back_qt_y})")
            
            # 검증
            if qt_x == back_qt_x and qt_y == back_qt_y:
                self.log_result("  ✅ 검증 성공")
            else:
                self.log_result(f"  ❌ 검증 실패: 예상({qt_x}, {qt_y}), 실제({back_qt_x}, {back_qt_y})")
                
    def test_capture_verification(self):
        """캡처 영역 검증 테스트"""
        self.log_result("=== 캡처 검증 테스트 ===")
        self.log_result("100x100 크기의 영역을 캡처합니다...")
        
        # 현재 윈도우의 중앙 좌표 계산
        window_rect = self.geometry()
        center_x = window_rect.x() + window_rect.width() // 2
        center_y = window_rect.y() + window_rect.height() // 2
        
        self.log_result(f"윈도우 중앙 (논리적): ({center_x}, {center_y})")
        
        # 물리적 좌표로 변환
        phys_x, phys_y = self.coord_converter.qt_to_mss(center_x - 50, center_y - 50)
        phys_w = int(100 * self.coord_converter.get_dpi_scale())
        phys_h = int(100 * self.coord_converter.get_dpi_scale())
        
        self.log_result(f"캡처 영역 (물리적): x={phys_x}, y={phys_y}, w={phys_w}, h={phys_h}")
        
        try:
            # 캡처
            monitor = {"left": phys_x, "top": phys_y, "width": phys_w, "height": phys_h}
            screenshot = self.sct.grab(monitor)
            
            # 캡처 성공 확인
            if screenshot:
                self.log_result(f"✅ 캡처 성공: {screenshot.size}")
                
                # 캡처된 이미지 저장 (선택적)
                from datetime import datetime
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"test_capture_{timestamp}.png"
                mss.tools.to_png(screenshot.rgb, screenshot.size, output=filename)
                self.log_result(f"캡처 이미지 저장됨: {filename}")
            else:
                self.log_result("❌ 캡처 실패")
                
        except Exception as e:
            self.log_result(f"❌ 캡처 중 오류 발생: {str(e)}")


def main():
    app = QApplication(sys.argv)
    
    # DPI awareness 설정
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps)
    
    widget = CoordinateTestWidget()
    widget.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()