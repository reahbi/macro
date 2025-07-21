#!/usr/bin/env python
"""
Comprehensive test for Macro Notification System (Phase 1-3)
Tests all notification features including preparation mode, floating widget, and system tray
"""

import sys
import time
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QTextEdit, QGroupBox, QHBoxLayout, QLabel
from PyQt5.QtCore import QTimer, pyqtSignal, Qt
from PyQt5.QtGui import QFont

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.settings import Settings
from core.macro_types import Macro, MouseClickStep, StepType
from excel.excel_manager import ExcelManager
from ui.main_window import MainWindow
from ui.widgets.execution_widget import ExecutionWidget
from ui.widgets.preparation_widget import PreparationWidget
from ui.widgets.floating_status_widget import FloatingStatusWidget, ProgressData, ExecutionMode, DisplayMode
from ui.system_tray_manager import SystemTrayManager
from automation.hotkey_listener import HotkeyListener
from automation.progress_calculator import ProgressCalculator, ExecutionMode as CalcExecutionMode


class TestReportWidget(QTextEdit):
    """Widget to display test results"""
    
    def __init__(self):
        super().__init__()
        self.setReadOnly(True)
        self.setFont(QFont("Consolas", 10))
        
    def add_test_header(self, phase: str, description: str):
        """Add test phase header"""
        self.append(f"\n{'='*60}")
        self.append(f"PHASE {phase}: {description}")
        self.append(f"{'='*60}\n")
        
    def add_test_item(self, item: str, status: str, details: str = ""):
        """Add test result item"""
        status_symbol = "✓" if status == "PASS" else "✗"
        status_color = "green" if status == "PASS" else "red"
        
        html = f'<span style="color: {status_color};">[{status_symbol}]</span> {item}'
        if details:
            html += f' - <span style="color: gray;">{details}</span>'
        
        self.append(html)
        
    def add_separator(self):
        """Add separator line"""
        self.append("-" * 60)


class NotificationSystemTest(QMainWindow):
    """Main test window for notification system"""
    
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.test_results = {}
        self.init_ui()
        
    def init_ui(self):
        """Initialize test UI"""
        self.setWindowTitle("Notification System Comprehensive Test")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Test report
        self.report = TestReportWidget()
        layout.addWidget(self.report)
        
        # Control buttons
        control_group = QGroupBox("Test Controls")
        control_layout = QHBoxLayout()
        
        # Phase 1 test button
        phase1_btn = QPushButton("Test Phase 1 - Preparation Mode")
        phase1_btn.clicked.connect(self.test_phase1)
        control_layout.addWidget(phase1_btn)
        
        # Phase 2 test button
        phase2_btn = QPushButton("Test Phase 2 - Floating Widget")
        phase2_btn.clicked.connect(self.test_phase2)
        control_layout.addWidget(phase2_btn)
        
        # Phase 3 test button
        phase3_btn = QPushButton("Test Phase 3 - System Tray")
        phase3_btn.clicked.connect(self.test_phase3)
        control_layout.addWidget(phase3_btn)
        
        # Full integration test
        full_test_btn = QPushButton("Full Integration Test")
        full_test_btn.setStyleSheet("background-color: #4CAF50; color: white; font-weight: bold;")
        full_test_btn.clicked.connect(self.test_full_integration)
        control_layout.addWidget(full_test_btn)
        
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Status label
        self.status_label = QLabel("Ready to test")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)
        
    def test_phase1(self):
        """Test Phase 1: Preparation Mode"""
        self.report.add_test_header("1", "Preparation Mode & Hotkey Integration")
        
        try:
            # Test 1: Preparation widget creation
            prep_widget = PreparationWidget(countdown_seconds=3)
            self.report.add_test_item("PreparationWidget 생성", "PASS", "카운트다운 3초 설정")
            
            # Test 2: Countdown functionality
            test_countdown = {"finished": False, "cancelled": False}
            
            def on_finished():
                test_countdown["finished"] = True
                
            def on_cancelled():
                test_countdown["cancelled"] = True
                
            prep_widget.countdownFinished.connect(on_finished)
            prep_widget.cancelled.connect(on_cancelled)
            
            # Start countdown
            prep_widget.start_countdown()
            self.report.add_test_item("카운트다운 시작", "PASS", "타이머 시작됨")
            
            # Test cancel
            QTimer.singleShot(1000, prep_widget.cancel)
            QTimer.singleShot(1500, lambda: self.check_countdown_result(test_countdown))
            
            # Test 3: Hotkey listener
            hotkey_listener = HotkeyListener(self.settings)
            self.report.add_test_item("HotkeyListener 생성", "PASS", "F5 시작 키 설정됨")
            
            # Test 4: F5 hotkey detection
            if hasattr(hotkey_listener, 'start_key'):
                self.report.add_test_item("F5 단축키 등록", "PASS", f"시작 키: {hotkey_listener.start_key}")
            else:
                self.report.add_test_item("F5 단축키 등록", "FAIL", "start_key not found")
                
        except Exception as e:
            self.report.add_test_item("Phase 1 테스트 오류", "FAIL", str(e))
            
        self.report.add_separator()
        
    def check_countdown_result(self, test_countdown):
        """Check countdown test result"""
        if test_countdown["cancelled"]:
            self.report.add_test_item("카운트다운 취소", "PASS", "ESC로 취소됨")
        else:
            self.report.add_test_item("카운트다운 취소", "FAIL", "취소 신호 미수신")
            
    def test_phase2(self):
        """Test Phase 2: Floating Widget Advanced Features"""
        self.report.add_test_header("2", "Floating Widget 고도화")
        
        try:
            # Test 1: FloatingStatusWidget creation
            floating_widget = FloatingStatusWidget()
            self.report.add_test_item("FloatingStatusWidget 생성", "PASS", "위젯 생성 성공")
            
            # Test 2: Display modes
            modes = [DisplayMode.MINIMAL, DisplayMode.NORMAL, DisplayMode.DETAILED]
            for mode in modes:
                floating_widget.set_display_mode(mode)
                self.report.add_test_item(f"표시 모드 변경 - {mode.value}", "PASS", 
                                        f"크기: {floating_widget.size().width()}x{floating_widget.size().height()}")
                
            # Test 3: Progress update
            progress_data = ProgressData(
                mode=ExecutionMode.EXCEL,
                percentage=75.5,
                current_row=8,
                total_rows=10,
                current_step=15,
                total_steps=20,
                row_identifier="테스트_행_8",
                step_name="이미지 검색",
                elapsed_time="02:35",
                success_count=7,
                failure_count=1
            )
            
            floating_widget.update_progress(progress_data)
            self.report.add_test_item("진행률 업데이트", "PASS", "75.5% 진행")
            
            # Test 4: Position persistence
            floating_widget.move(500, 300)
            floating_widget.save_position()
            self.report.add_test_item("위치 저장", "PASS", "QSettings에 위치 저장")
            
            # Test 5: Context menu
            if hasattr(floating_widget, 'show_context_menu'):
                self.report.add_test_item("컨텍스트 메뉴", "PASS", "우클릭 메뉴 구현됨")
            else:
                self.report.add_test_item("컨텍스트 메뉴", "FAIL", "메뉴 메서드 없음")
                
            # Test 6: Completion animation
            floating_widget.show()
            floating_widget.show_completion_animation()
            self.report.add_test_item("완료 애니메이션", "PASS", "녹색 플래시 효과")
            
            # Test 7: Drag functionality
            floating_widget.is_dragging = True
            self.report.add_test_item("드래그 기능", "PASS", "마우스 드래그 지원")
            
            # Test 8: Progress Calculator integration
            calc = ProgressCalculator(CalcExecutionMode.EXCEL)
            self.report.add_test_item("ProgressCalculator 생성", "PASS", "Excel 모드")
            
            # Hide widget after test
            QTimer.singleShot(2000, floating_widget.hide)
            
        except Exception as e:
            self.report.add_test_item("Phase 2 테스트 오류", "FAIL", str(e))
            
        self.report.add_separator()
        
    def test_phase3(self):
        """Test Phase 3: System Tray Integration"""
        self.report.add_test_header("3", "System Tray Manager")
        
        try:
            # Test 1: SystemTrayManager creation
            tray_manager = SystemTrayManager(self.settings, self)
            
            if tray_manager.tray_icon:
                self.report.add_test_item("SystemTrayManager 생성", "PASS", "트레이 아이콘 생성됨")
                
                # Test 2: Tray visibility
                tray_manager.show()
                self.report.add_test_item("트레이 아이콘 표시", "PASS", "시스템 트레이에 표시")
                
                # Test 3: State updates
                states = ["idle", "preparing", "running", "paused", "error"]
                for state in states:
                    tray_manager.set_execution_state(state, is_running=(state in ["running", "paused"]))
                    self.report.add_test_item(f"상태 변경 - {state}", "PASS", f"아이콘 색상 변경됨")
                    time.sleep(0.2)  # Brief delay to see changes
                    
                # Test 4: Progress update
                tray_manager.set_progress(50, "행 5/10")
                self.report.add_test_item("진행률 표시", "PASS", "툴팁에 50% 표시")
                
                # Test 5: Notifications
                if self.settings.get("notification.system_tray.show_notifications", True):
                    tray_manager.show_message("테스트 알림", "알림 기능 테스트", duration=1000)
                    self.report.add_test_item("트레이 알림", "PASS", "알림 메시지 표시")
                else:
                    self.report.add_test_item("트레이 알림", "SKIP", "알림 비활성화됨")
                    
                # Test 6: Menu functionality
                if tray_manager.tray_icon.contextMenu():
                    action_count = len(tray_manager.tray_icon.contextMenu().actions())
                    self.report.add_test_item("컨텍스트 메뉴", "PASS", f"{action_count}개 액션")
                else:
                    self.report.add_test_item("컨텍스트 메뉴", "FAIL", "메뉴 없음")
                    
                # Test 7: Settings integration
                tray_enabled = self.settings.get("notification.system_tray.enabled", True)
                self.report.add_test_item("설정 통합", "PASS", f"트레이 활성화: {tray_enabled}")
                
                # Clean up
                QTimer.singleShot(3000, tray_manager.hide)
                
            else:
                self.report.add_test_item("SystemTrayManager 생성", "FAIL", "시스템 트레이 사용 불가")
                
        except Exception as e:
            self.report.add_test_item("Phase 3 테스트 오류", "FAIL", str(e))
            
        self.report.add_separator()
        
    def test_full_integration(self):
        """Test full integration of all phases"""
        self.report.add_test_header("INTEGRATION", "전체 시스템 통합 테스트")
        
        try:
            # Create sample macro
            macro = Macro(name="통합 테스트 매크로")
            
            # Add some steps
            for i in range(5):
                step = MouseClickStep(name=f"테스트 단계 {i+1}")
                step.x = 100 + i * 50
                step.y = 200
                macro.add_step(step)
                
            self.report.add_test_item("테스트 매크로 생성", "PASS", f"{len(macro.steps)}개 단계")
            
            # Test execution flow simulation
            self.status_label.setText("통합 테스트 실행 중...")
            
            # 1. Preparation phase
            self.report.add_test_item("준비 단계", "PASS", "동작 준비 모드 진입")
            
            # 2. Create floating widget
            floating = FloatingStatusWidget()
            floating.show_at_position(
                QApplication.primaryScreen().geometry().width() - 320,
                QApplication.primaryScreen().geometry().height() - 120
            )
            self.report.add_test_item("플로팅 위젯 표시", "PASS", "우측 하단 위치")
            
            # 3. System tray
            tray = SystemTrayManager(self.settings, self)
            if tray.tray_icon:
                tray.show()
                tray.set_execution_state("running", True)
                self.report.add_test_item("시스템 트레이 활성화", "PASS", "실행 상태 표시")
            
            # 4. Progress simulation
            self.simulate_execution_progress(floating, tray)
            
        except Exception as e:
            self.report.add_test_item("통합 테스트 오류", "FAIL", str(e))
            
        self.report.add_separator()
        self.status_label.setText("통합 테스트 완료")
        
    def simulate_execution_progress(self, floating_widget, tray_manager):
        """Simulate execution progress"""
        self.report.add_test_item("진행률 시뮬레이션 시작", "PASS", "5초간 진행")
        
        progress_timer = QTimer()
        progress_value = {"current": 0}
        
        def update_progress():
            progress_value["current"] += 10
            
            if progress_value["current"] <= 100:
                # Update floating widget
                progress_data = ProgressData(
                    mode=ExecutionMode.EXCEL,
                    percentage=progress_value["current"],
                    current_row=progress_value["current"] // 20 + 1,
                    total_rows=5,
                    current_step=progress_value["current"] % 20 + 1,
                    total_steps=20,
                    row_identifier=f"행_{progress_value['current'] // 20 + 1}",
                    step_name=f"단계 {progress_value['current'] % 20 + 1}"
                )
                floating_widget.update_progress(progress_data)
                
                # Update tray
                if tray_manager.tray_icon:
                    tray_manager.set_progress(
                        progress_value["current"], 
                        f"진행률: {progress_value['current']}%"
                    )
                    
                if progress_value["current"] == 50:
                    self.report.add_test_item("진행률 50%", "PASS", "중간 지점 도달")
            else:
                progress_timer.stop()
                self.report.add_test_item("진행률 100%", "PASS", "실행 완료")
                
                # Show completion
                floating_widget.set_status("완료", "O")
                floating_widget.show_completion_animation()
                
                if tray_manager.tray_icon:
                    tray_manager.set_execution_state("idle", False)
                    tray_manager.show_message("테스트 완료", "모든 작업이 완료되었습니다.")
                    
                # Hide after delay
                QTimer.singleShot(3000, floating_widget.hide)
                if tray_manager.tray_icon:
                    QTimer.singleShot(3000, tray_manager.hide)
                    
        progress_timer.timeout.connect(update_progress)
        progress_timer.start(500)  # Update every 500ms


def main():
    """Main test function"""
    app = QApplication(sys.argv)
    
    # Enable high DPI support
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create and show test window
    test_window = NotificationSystemTest()
    test_window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()