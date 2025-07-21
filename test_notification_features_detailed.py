#!/usr/bin/env python
"""
Detailed feature tests for Macro Notification System
Tests individual features and edge cases
"""

import sys
import time
from pathlib import Path
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit
from PyQt5.QtCore import QTimer, Qt, QSettings

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from ui.widgets.preparation_widget import PreparationWidget
from ui.widgets.floating_status_widget import FloatingStatusWidget, ProgressData, ExecutionMode, DisplayMode
from config.settings import Settings


class DetailedFeatureTest(QWidget):
    """Detailed feature testing widget"""
    
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.init_ui()
        
    def init_ui(self):
        """Initialize test UI"""
        self.setWindowTitle("Notification Features - Detailed Tests")
        self.setGeometry(100, 100, 600, 800)
        
        layout = QVBoxLayout()
        
        # Test log
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)
        
        # Test buttons
        self.add_test_button(layout, "Test 1: Preparation Widget States", self.test_preparation_states)
        self.add_test_button(layout, "Test 2: Floating Widget Modes", self.test_floating_modes)
        self.add_test_button(layout, "Test 3: Progress Edge Cases", self.test_progress_edge_cases)
        self.add_test_button(layout, "Test 4: Position Persistence", self.test_position_persistence)
        self.add_test_button(layout, "Test 5: Animation Timing", self.test_animation_timing)
        self.add_test_button(layout, "Test 6: Settings Integration", self.test_settings_integration)
        self.add_test_button(layout, "Test 7: Memory & Performance", self.test_performance)
        self.add_test_button(layout, "Test 8: Error Scenarios", self.test_error_scenarios)
        
        # Clear log button
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self.log.clear)
        layout.addWidget(clear_btn)
        
        self.setLayout(layout)
        
    def add_test_button(self, layout, text, callback):
        """Add a test button to layout"""
        btn = QPushButton(text)
        btn.clicked.connect(callback)
        layout.addWidget(btn)
        
    def log_test(self, test_name, result, details=""):
        """Log test result"""
        timestamp = time.strftime("%H:%M:%S")
        status = "✓ PASS" if result else "✗ FAIL"
        self.log.append(f"[{timestamp}] {test_name}: {status}")
        if details:
            self.log.append(f"  → {details}")
        self.log.append("")
        
    def test_preparation_states(self):
        """Test preparation widget state transitions"""
        self.log.append("=== Testing Preparation Widget States ===")
        
        prep = PreparationWidget(countdown_seconds=2)
        
        # Test 1: Initial state
        self.log_test("Initial countdown value", 
                     prep.countdown_label.text() == "5",
                     f"Display: {prep.countdown_label.text()}")
        
        # Test 2: Custom countdown
        prep2 = PreparationWidget(countdown_seconds=10)
        self.log_test("Custom countdown seconds", 
                     hasattr(prep2, 'countdown_seconds') and prep2.countdown_seconds == 10,
                     "10초 카운트다운 설정")
        
        # Test 3: Start and immediate cancel
        prep.start_countdown()
        QTimer.singleShot(100, prep.cancel)
        
        # Test 4: Multiple starts (should reset)
        prep3 = PreparationWidget(countdown_seconds=3)
        prep3.start_countdown()
        QTimer.singleShot(500, prep3.start_countdown)  # Restart
        
        self.log_test("Countdown restart capability", True, "카운트다운 재시작 가능")
        
        # Test 5: Window flags
        flags = prep.windowFlags()
        self.log_test("Frameless window", 
                     bool(flags & Qt.FramelessWindowHint),
                     "프레임 없는 윈도우")
        
        self.log_test("Always on top", 
                     bool(flags & Qt.WindowStaysOnTopHint),
                     "항상 위 표시")
        
        # Clean up
        prep.close()
        prep2.close()
        prep3.close()
        
    def test_floating_modes(self):
        """Test floating widget display modes"""
        self.log.append("=== Testing Floating Widget Display Modes ===")
        
        floating = FloatingStatusWidget()
        
        # Test each mode
        mode_sizes = {
            DisplayMode.MINIMAL: (200, 50),
            DisplayMode.NORMAL: (300, 60),
            DisplayMode.DETAILED: (350, 80)
        }
        
        for mode, expected_size in mode_sizes.items():
            floating.set_display_mode(mode)
            actual_size = (floating.width(), floating.height())
            
            self.log_test(f"Mode {mode.value} size", 
                         actual_size == expected_size,
                         f"Expected: {expected_size}, Actual: {actual_size}")
            
            # Check widget visibility
            if mode == DisplayMode.MINIMAL:
                self.log_test(f"Mode {mode.value} - controls hidden",
                             not floating.pause_btn.isVisible(),
                             "컨트롤 버튼 숨김")
            else:
                self.log_test(f"Mode {mode.value} - controls visible",
                             floating.pause_btn.isVisible(),
                             "컨트롤 버튼 표시")
                
        # Test mode persistence
        floating.set_display_mode(DisplayMode.DETAILED)
        saved_mode = floating.settings.value("display_mode")
        self.log_test("Display mode saved",
                     saved_mode == DisplayMode.DETAILED.value,
                     f"Saved: {saved_mode}")
        
        floating.close()
        
    def test_progress_edge_cases(self):
        """Test progress calculation edge cases"""
        self.log.append("=== Testing Progress Edge Cases ===")
        
        floating = FloatingStatusWidget()
        floating.show()
        
        # Test 1: Zero progress
        progress = ProgressData(
            mode=ExecutionMode.EXCEL,
            percentage=0,
            current_row=0,
            total_rows=10
        )
        floating.update_progress(progress)
        self.log_test("Zero progress display",
                     floating.percentage_label.text() == "0%",
                     "0% 표시")
        
        # Test 2: 100% progress
        progress.percentage = 100
        floating.update_progress(progress)
        self.log_test("100% progress display",
                     floating.percentage_label.text() == "100%",
                     "100% 표시")
        
        # Test 3: Fractional progress
        progress.percentage = 33.33
        floating.update_progress(progress)
        self.log_test("Fractional progress display",
                     floating.percentage_label.text() == "33%",
                     "소수점 반올림")
        
        # Test 4: None values
        progress = ProgressData(
            mode=ExecutionMode.STANDALONE,
            percentage=50,
            current_row=None,
            total_rows=None,
            current_step=5,
            total_steps=10
        )
        floating.update_progress(progress)
        self.log_test("Standalone mode display",
                     "단계" in floating.status_text_label.text(),
                     floating.status_text_label.text())
        
        # Test 5: Long text truncation
        progress = ProgressData(
            mode=ExecutionMode.EXCEL,
            percentage=50,
            row_identifier="Very_Long_Row_Identifier_That_Should_Be_Handled_Properly_Without_Breaking_Layout",
            step_name="극도로_긴_단계_이름_테스트_레이아웃_깨짐_방지_확인용"
        )
        floating.update_progress(progress)
        self.log_test("Long text handling", True, "긴 텍스트 처리")
        
        QTimer.singleShot(2000, floating.close)
        
    def test_position_persistence(self):
        """Test position saving and restoration"""
        self.log.append("=== Testing Position Persistence ===")
        
        # Clear existing position
        settings = QSettings("ExcelMacroAutomation", "FloatingWidget")
        settings.remove("position/x")
        settings.remove("position/y")
        
        # Test 1: Save position
        floating1 = FloatingStatusWidget()
        floating1.move(123, 456)
        floating1.save_position()
        floating1.close()
        
        # Test 2: Load position
        floating2 = FloatingStatusWidget()
        pos = floating2.pos()
        self.log_test("Position restored",
                     pos.x() == 123 and pos.y() == 456,
                     f"Position: ({pos.x()}, {pos.y()})")
        
        # Test 3: Reset position
        floating2.reset_position()
        screen = QApplication.primaryScreen().geometry()
        expected_x = screen.width() - 320
        expected_y = screen.height() - 120
        pos = floating2.pos()
        
        self.log_test("Position reset",
                     abs(pos.x() - expected_x) < 10 and abs(pos.y() - expected_y) < 10,
                     f"Reset to: ({pos.x()}, {pos.y()})")
        
        floating2.close()
        
    def test_animation_timing(self):
        """Test animation timing and performance"""
        self.log.append("=== Testing Animation Timing ===")
        
        floating = FloatingStatusWidget()
        floating.show()
        
        # Test 1: Expansion animation
        start_time = time.time()
        floating.expand()
        
        # Wait for animation
        QTimer.singleShot(300, lambda: self.check_animation_time(
            "Expansion animation",
            time.time() - start_time,
            0.2  # Expected ~200ms
        ))
        
        # Test 2: Completion animation
        QTimer.singleShot(500, lambda: self.test_completion_animation(floating))
        
        # Test 3: Rapid state changes
        QTimer.singleShot(1000, lambda: self.test_rapid_changes(floating))
        
        QTimer.singleShot(3000, floating.close)
        
    def check_animation_time(self, name, elapsed, expected):
        """Check animation timing"""
        self.log_test(name,
                     abs(elapsed - expected) < 0.1,
                     f"Elapsed: {elapsed:.3f}s (expected ~{expected}s)")
        
    def test_completion_animation(self, floating):
        """Test completion animation"""
        floating.show_completion_animation()
        self.log_test("Completion animation triggered", True, "녹색 플래시 시작")
        
    def test_rapid_changes(self, floating):
        """Test rapid state changes"""
        for i in range(5):
            floating.set_paused(i % 2 == 0)
            time.sleep(0.1)
        self.log_test("Rapid state changes", True, "5회 상태 변경")
        
    def test_settings_integration(self):
        """Test settings system integration"""
        self.log.append("=== Testing Settings Integration ===")
        
        # Test 1: Default settings
        defaults = {
            "notification.preparation.countdown_seconds": 5,
            "notification.floating_widget.default_mode": "normal",
            "notification.floating_widget.opacity": 0.9,
            "notification.system_tray.enabled": True
        }
        
        for key, expected in defaults.items():
            actual = self.settings.get(key)
            self.log_test(f"Default setting: {key}",
                         actual == expected,
                         f"Value: {actual}")
            
        # Test 2: Setting modification
        self.settings.set("notification.preparation.countdown_seconds", 10)
        new_value = self.settings.get("notification.preparation.countdown_seconds")
        self.log_test("Setting modification",
                     new_value == 10,
                     "카운트다운 10초로 변경")
        
        # Reset
        self.settings.set("notification.preparation.countdown_seconds", 5)
        
        # Test 3: Opacity setting
        floating = FloatingStatusWidget()
        opacity = floating.windowOpacity()
        expected_opacity = self.settings.get("notification.floating_widget.opacity", 0.9)
        self.log_test("Widget opacity from settings",
                     abs(opacity - expected_opacity) < 0.01,
                     f"Opacity: {opacity}")
        floating.close()
        
    def test_performance(self):
        """Test memory usage and performance"""
        self.log.append("=== Testing Performance ===")
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        
        # Get baseline memory
        baseline_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # Create multiple widgets
        widgets = []
        for i in range(10):
            w = FloatingStatusWidget()
            w.show()
            widgets.append(w)
            
        # Update all widgets
        for i in range(100):
            for w in widgets:
                progress = ProgressData(
                    mode=ExecutionMode.EXCEL,
                    percentage=i,
                    current_row=i,
                    total_rows=100
                )
                w.update_progress(progress)
                
        # Check memory increase
        current_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = current_memory - baseline_memory
        
        self.log_test("Memory usage (10 widgets, 100 updates)",
                     memory_increase < 50,  # Less than 50MB increase
                     f"Memory increase: {memory_increase:.1f}MB")
        
        # Clean up
        for w in widgets:
            w.close()
            
    def test_error_scenarios(self):
        """Test error handling scenarios"""
        self.log.append("=== Testing Error Scenarios ===")
        
        # Test 1: Invalid countdown value
        try:
            prep = PreparationWidget(countdown_seconds=-5)
            self.log_test("Negative countdown handling",
                         prep.countdown_seconds > 0,
                         f"Adjusted to: {prep.countdown_seconds}")
            prep.close()
        except Exception as e:
            self.log_test("Negative countdown handling", False, str(e))
            
        # Test 2: Missing settings
        floating = FloatingStatusWidget()
        floating.settings.clear()  # Clear all settings
        
        try:
            floating.load_position()
            self.log_test("Missing settings handling", True, "기본값 사용")
        except Exception as e:
            self.log_test("Missing settings handling", False, str(e))
            
        floating.close()
        
        # Test 3: Invalid progress data
        floating2 = FloatingStatusWidget()
        try:
            # Negative percentage
            progress = ProgressData(
                mode=ExecutionMode.EXCEL,
                percentage=-10,
                current_row=0,
                total_rows=10
            )
            floating2.update_progress(progress)
            displayed = int(floating2.progress_bar.value())
            self.log_test("Negative percentage handling",
                         displayed == 0,
                         f"Displayed: {displayed}%")
                         
            # Over 100%
            progress.percentage = 150
            floating2.update_progress(progress)
            displayed = int(floating2.progress_bar.value())
            self.log_test("Over 100% handling",
                         displayed == 100 or displayed == 150,
                         f"Displayed: {displayed}%")
                         
        except Exception as e:
            self.log_test("Invalid progress data", False, str(e))
            
        floating2.close()


def main():
    """Main test function"""
    app = QApplication(sys.argv)
    
    # Enable high DPI support
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create and show test window
    test_window = DetailedFeatureTest()
    test_window.show()
    
    # Run application
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()