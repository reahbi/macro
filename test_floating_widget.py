#!/usr/bin/env python
"""
Test script for FloatingStatusWidget Phase 2 enhancements
"""

import sys
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QLabel
from PyQt5.QtCore import QTimer

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ui.widgets.floating_status_widget import FloatingStatusWidget, ProgressData, ExecutionMode, DisplayMode

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.progress = 0
        
    def init_ui(self):
        self.setWindowTitle("FloatingStatusWidget Test")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        # Info label
        info_label = QLabel("FloatingStatusWidget 테스트\n\n"
                           "기능:\n"
                           "- 우클릭: 컨텍스트 메뉴 (표시 모드 변경)\n"
                           "- 드래그: 위치 이동 (자동 저장)\n"
                           "- 더블클릭: 확장/축소\n"
                           "- 마우스 오버: 자동 확장")
        layout.addWidget(info_label)
        
        # Create floating widget button
        create_btn = QPushButton("FloatingWidget 생성")
        create_btn.clicked.connect(self.create_floating_widget)
        layout.addWidget(create_btn)
        
        # Start progress button
        start_btn = QPushButton("진행률 시뮬레이션 시작")
        start_btn.clicked.connect(self.start_progress_simulation)
        layout.addWidget(start_btn)
        
        # Test completion animation
        complete_btn = QPushButton("완료 애니메이션 테스트")
        complete_btn.clicked.connect(self.test_completion_animation)
        layout.addWidget(complete_btn)
        
        self.setLayout(layout)
        
        # Create floating widget
        self.floating_widget = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        
    def create_floating_widget(self):
        if not self.floating_widget:
            self.floating_widget = FloatingStatusWidget()
            self.floating_widget.pauseClicked.connect(lambda: print("Pause clicked"))
            self.floating_widget.stopClicked.connect(lambda: print("Stop clicked"))
            
        # Position at bottom right
        screen = QApplication.primaryScreen().geometry()
        x = screen.width() - 320
        y = screen.height() - 120
        self.floating_widget.show_at_position(x, y)
        
    def start_progress_simulation(self):
        if not self.floating_widget:
            self.create_floating_widget()
            
        self.progress = 0
        self.floating_widget.set_status("매크로 실행 중...", "▶")
        self.timer.start(100)  # Update every 100ms
        
    def update_progress(self):
        self.progress += 1
        
        if self.progress <= 100:
            # Create progress data
            progress_data = ProgressData(
                mode=ExecutionMode.EXCEL,
                percentage=self.progress,
                current_row=self.progress // 10 + 1,
                total_rows=10,
                current_step=self.progress % 10 + 1,
                total_steps=10,
                row_identifier=f"테스트_{self.progress // 10 + 1}",
                step_name=f"단계 {self.progress % 10 + 1}",
                elapsed_time=f"{self.progress // 60:02d}:{self.progress % 60:02d}",
                success_count=self.progress // 10,
                failure_count=0
            )
            
            self.floating_widget.update_progress(progress_data)
        else:
            self.timer.stop()
            self.floating_widget.set_status("완료", "O")
            self.floating_widget.show_completion_animation()
            
    def test_completion_animation(self):
        if self.floating_widget:
            self.floating_widget.show_completion_animation()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())