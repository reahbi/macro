#!/usr/bin/env python
"""
Real scenario simulation test for Macro Notification System
Simulates actual macro execution with all notification features
"""

import sys
import time
import random
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QProgressBar, QTextEdit, QGroupBox, QSpinBox
)
from PyQt5.QtCore import QTimer, QThread, pyqtSignal, Qt
from PyQt5.QtGui import QFont

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config.settings import Settings
from core.macro_types import (
    Macro, StepType, LoopStep, IfConditionStep,
    MouseClickStep, KeyboardTypeStep, ImageSearchStep, 
    OCRTextStep, WaitTimeStep
)
from ui.widgets.preparation_widget import PreparationWidget
from ui.widgets.floating_status_widget import FloatingStatusWidget, ProgressData, ExecutionMode
from ui.system_tray_manager import SystemTrayManager
from automation.progress_calculator import ProgressCalculator, ExecutionMode as CalcExecutionMode


class MacroSimulationThread(QThread):
    """Thread to simulate macro execution"""
    
    progressUpdated = pyqtSignal(ProgressData)
    statusChanged = pyqtSignal(str, str)  # status, icon
    stepExecuting = pyqtSignal(str, int)  # step_name, step_index
    executionFinished = pyqtSignal(int, int)  # success_count, fail_count
    
    def __init__(self, macro, total_rows=10):
        super().__init__()
        self.macro = macro
        self.total_rows = total_rows
        self.is_running = True
        self.is_paused = False
        self.progress_calculator = ProgressCalculator(CalcExecutionMode.EXCEL)
        
    def run(self):
        """Run simulated macro execution"""
        self.progress_calculator.initialize_macro(self.macro, self.total_rows)
        
        success_count = 0
        fail_count = 0
        start_time = time.time()
        
        for row_index in range(self.total_rows):
            if not self.is_running:
                break
                
            # Wait if paused
            while self.is_paused and self.is_running:
                time.sleep(0.1)
                
            self.progress_calculator.start_row(row_index, {"name": f"테스트_행_{row_index + 1}"})
            
            # Execute steps
            step_success = True
            for step_index, step in enumerate(self.macro.steps):
                if not self.is_running:
                    break
                    
                while self.is_paused and self.is_running:
                    time.sleep(0.1)
                    
                self.stepExecuting.emit(step.name, step_index)
                self.progress_calculator.start_step(step, step_index)
                
                # Simulate step execution
                time.sleep(random.uniform(0.1, 0.3))
                
                # Random failure (10% chance)
                if random.random() < 0.1:
                    step_success = False
                    
                self.progress_calculator.complete_step(step)
                
                # Calculate and emit progress
                progress_info = self.progress_calculator.calculate_progress()
                elapsed = time.time() - start_time
                
                progress_data = ProgressData(
                    mode=ExecutionMode.EXCEL,
                    percentage=progress_info.percentage,
                    current_row=row_index + 1,
                    total_rows=self.total_rows,
                    current_step=step_index + 1,
                    total_steps=len(self.macro.steps),
                    row_identifier=f"테스트_행_{row_index + 1}",
                    step_name=step.name,
                    elapsed_time=f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d}",
                    success_count=success_count,
                    failure_count=fail_count
                )
                
                self.progressUpdated.emit(progress_data)
                
            self.progress_calculator.complete_row(row_index)
            
            if step_success:
                success_count += 1
            else:
                fail_count += 1
                
        self.executionFinished.emit(success_count, fail_count)
        
    def pause(self):
        """Pause execution"""
        self.is_paused = True
        self.statusChanged.emit("일시정지", "⏸")
        
    def resume(self):
        """Resume execution"""
        self.is_paused = False
        self.statusChanged.emit("실행 중", "▶")
        
    def stop(self):
        """Stop execution"""
        self.is_running = False
        self.statusChanged.emit("정지됨", "⏹")


class RealScenarioTest(QMainWindow):
    """Main window for real scenario testing"""
    
    def __init__(self):
        super().__init__()
        self.settings = Settings()
        self.simulation_thread = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Real Scenario Simulation - Macro Notification System")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # Scenario controls
        control_group = QGroupBox("시나리오 설정")
        control_layout = QHBoxLayout()
        
        # Row count
        control_layout.addWidget(QLabel("실행할 행 수:"))
        self.row_count_spin = QSpinBox()
        self.row_count_spin.setRange(1, 100)
        self.row_count_spin.setValue(10)
        control_layout.addWidget(self.row_count_spin)
        
        # Step count
        control_layout.addWidget(QLabel("매크로 단계 수:"))
        self.step_count_spin = QSpinBox()
        self.step_count_spin.setRange(1, 50)
        self.step_count_spin.setValue(5)
        control_layout.addWidget(self.step_count_spin)
        
        control_layout.addStretch()
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)
        
        # Execution controls
        exec_group = QGroupBox("실행 제어")
        exec_layout = QHBoxLayout()
        
        # Prepare button
        self.prepare_btn = QPushButton("동작 준비")
        self.prepare_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
            }
        """)
        self.prepare_btn.clicked.connect(self.start_preparation)
        exec_layout.addWidget(self.prepare_btn)
        
        # Start button
        self.start_btn = QPushButton("바로 시작")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
            }
        """)
        self.start_btn.clicked.connect(self.start_execution_immediate)
        exec_layout.addWidget(self.start_btn)
        
        # Pause button
        self.pause_btn = QPushButton("일시정지")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.toggle_pause)
        exec_layout.addWidget(self.pause_btn)
        
        # Stop button
        self.stop_btn = QPushButton("정지")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self.stop_execution)
        exec_layout.addWidget(self.stop_btn)
        
        exec_layout.addStretch()
        exec_group.setLayout(exec_layout)
        layout.addWidget(exec_group)
        
        # Status display
        status_group = QGroupBox("실행 상태")
        status_layout = QVBoxLayout()
        
        # Progress bar
        self.progress_bar = QProgressBar()
        status_layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("대기 중")
        self.status_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(12)
        self.status_label.setFont(font)
        status_layout.addWidget(self.status_label)
        
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Log display
        log_group = QGroupBox("실행 로그")
        log_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        # Initialize notification components
        self.preparation_widget = None
        self.floating_widget = None
        self.tray_manager = SystemTrayManager(self.settings, self)
        
    def create_test_macro(self):
        """Create a test macro with specified steps"""
        macro = Macro(name="시나리오 테스트 매크로")
        
        step_count = self.step_count_spin.value()
        
        # Add various step types
        for i in range(step_count):
            step_type = random.choice([
                StepType.MOUSE_CLICK,
                StepType.KEYBOARD_TYPE,
                StepType.IMAGE_SEARCH,
                StepType.OCR_TEXT,
                StepType.WAIT_TIME
            ])
            
            # Create concrete step based on type
            if step_type == StepType.MOUSE_CLICK:
                step = MouseClickStep(name=f"클릭 단계 {i+1}")
                step.x = random.randint(100, 800)
                step.y = random.randint(100, 600)
            elif step_type == StepType.KEYBOARD_TYPE:
                step = KeyboardTypeStep(name=f"텍스트 입력 단계 {i+1}")
                step.text = f"테스트 텍스트 {i+1}"
            elif step_type == StepType.IMAGE_SEARCH:
                step = ImageSearchStep(name=f"이미지 검색 단계 {i+1}")
                step.image_path = "test_image.png"
            elif step_type == StepType.OCR_TEXT:
                step = OCRTextStep(name=f"OCR 검색 단계 {i+1}")
                step.search_text = f"텍스트 {i+1}"
            elif step_type == StepType.WAIT_TIME:
                step = WaitTimeStep(name=f"대기 단계 {i+1}")
                step.wait_time = random.uniform(0.5, 2.0)
                
            macro.add_step(step)
            
        # Add a loop step
        if step_count > 3:
            loop_step = LoopStep(name="반복 테스트")
            loop_step.loop_type = "fixed_count"
            loop_step.loop_count = 3
            
            # Add steps to loop
            for j in range(2):
                sub_step = MouseClickStep(name=f"반복 내부 단계 {j+1}")
                sub_step.x = 200 + j * 50
                sub_step.y = 300
                loop_step.add_step(sub_step)
                
            macro.add_step(loop_step)
            
        return macro
        
    def start_preparation(self):
        """Start preparation mode"""
        self.log_text.append("준비 모드 시작...")
        
        # Create preparation widget
        countdown = self.settings.get("notification.preparation.countdown_seconds", 5)
        self.preparation_widget = PreparationWidget(countdown_seconds=countdown)
        self.preparation_widget.startNow.connect(self.on_preparation_start_now)
        self.preparation_widget.cancelled.connect(self.on_preparation_cancelled)
        self.preparation_widget.countdownFinished.connect(self.on_preparation_finished)
        
        # Minimize main window
        self.showMinimized()
        
        # Start countdown
        self.preparation_widget.start_countdown()
        
        # Update tray
        if self.tray_manager:
            self.tray_manager.set_execution_state("preparing", False)
            self.tray_manager.show_message(
                "준비 모드",
                f"{countdown}초 후 매크로가 시작됩니다.",
                duration=2000
            )
            
    def on_preparation_start_now(self):
        """Handle immediate start from preparation"""
        self.log_text.append("F5 키로 즉시 시작")
        self.start_execution()
        
    def on_preparation_cancelled(self):
        """Handle preparation cancellation"""
        self.log_text.append("준비 모드 취소됨")
        self.showNormal()
        if self.tray_manager:
            self.tray_manager.set_execution_state("idle", False)
            
    def on_preparation_finished(self):
        """Handle preparation countdown finished"""
        self.log_text.append("카운트다운 완료")
        self.start_execution()
        
    def start_execution_immediate(self):
        """Start execution immediately without preparation"""
        self.log_text.append("즉시 실행 시작")
        self.start_execution()
        
    def start_execution(self):
        """Start macro execution"""
        # Show main window
        self.showNormal()
        
        # Create and show floating widget
        if not self.floating_widget:
            self.floating_widget = FloatingStatusWidget()
            self.floating_widget.pauseClicked.connect(self.toggle_pause)
            self.floating_widget.stopClicked.connect(self.stop_execution)
            
        # Position at bottom right
        screen = QApplication.primaryScreen().geometry()
        self.floating_widget.show_at_position(
            screen.width() - 320,
            screen.height() - 120
        )
        
        # Create test macro
        macro = self.create_test_macro()
        total_rows = self.row_count_spin.value()
        
        self.log_text.append(f"매크로 실행 시작: {len(macro.steps)}개 단계, {total_rows}개 행")
        
        # Create and start simulation thread
        self.simulation_thread = MacroSimulationThread(macro, total_rows)
        self.simulation_thread.progressUpdated.connect(self.on_progress_updated)
        self.simulation_thread.statusChanged.connect(self.on_status_changed)
        self.simulation_thread.stepExecuting.connect(self.on_step_executing)
        self.simulation_thread.executionFinished.connect(self.on_execution_finished)
        
        # Update UI
        self.prepare_btn.setEnabled(False)
        self.start_btn.setEnabled(False)
        self.pause_btn.setEnabled(True)
        self.stop_btn.setEnabled(True)
        
        # Update status
        self.status_label.setText("실행 중")
        self.floating_widget.set_status("매크로 실행 중...", "▶")
        
        # Update tray
        if self.tray_manager:
            self.tray_manager.set_execution_state("running", True)
            
        # Start thread
        self.simulation_thread.start()
        
    def toggle_pause(self):
        """Toggle pause state"""
        if self.simulation_thread and self.simulation_thread.isRunning():
            if self.simulation_thread.is_paused:
                self.simulation_thread.resume()
                self.pause_btn.setText("일시정지")
                self.log_text.append("실행 재개")
            else:
                self.simulation_thread.pause()
                self.pause_btn.setText("재개")
                self.log_text.append("일시정지")
                
            # Update floating widget
            if self.floating_widget:
                self.floating_widget.set_paused(self.simulation_thread.is_paused)
                
            # Update tray
            if self.tray_manager:
                state = "paused" if self.simulation_thread.is_paused else "running"
                self.tray_manager.set_execution_state(state, True)
                
    def stop_execution(self):
        """Stop execution"""
        if self.simulation_thread and self.simulation_thread.isRunning():
            self.simulation_thread.stop()
            self.log_text.append("실행 정지")
            
    def on_progress_updated(self, progress_data: ProgressData):
        """Handle progress update"""
        # Update progress bar
        self.progress_bar.setValue(int(progress_data.percentage))
        
        # Update floating widget
        if self.floating_widget:
            self.floating_widget.update_progress(progress_data)
            
        # Update tray
        if self.tray_manager:
            self.tray_manager.set_progress(
                int(progress_data.percentage),
                f"행 {progress_data.current_row}/{progress_data.total_rows}"
            )
            
    def on_status_changed(self, status: str, icon: str):
        """Handle status change"""
        self.status_label.setText(status)
        if self.floating_widget:
            self.floating_widget.set_status(status, icon)
            
    def on_step_executing(self, step_name: str, step_index: int):
        """Handle step execution"""
        self.log_text.append(f"  → 실행: {step_name}")
        
    def on_execution_finished(self, success_count: int, fail_count: int):
        """Handle execution finished"""
        self.log_text.append(f"\n실행 완료!")
        self.log_text.append(f"성공: {success_count}, 실패: {fail_count}")
        
        # Update UI
        self.prepare_btn.setEnabled(True)
        self.start_btn.setEnabled(True)
        self.pause_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.pause_btn.setText("일시정지")
        
        # Update status
        self.status_label.setText("완료")
        
        # Update floating widget
        if self.floating_widget:
            self.floating_widget.set_status("완료", "O")
            if fail_count == 0:
                self.floating_widget.show_completion_animation()
                
            # Hide after delay
            QTimer.singleShot(3000, self.floating_widget.hide)
            
        # Update tray
        if self.tray_manager:
            self.tray_manager.set_execution_state("idle", False)
            self.tray_manager.show_message(
                "매크로 완료",
                f"성공: {success_count}, 실패: {fail_count}",
                duration=3000
            )
            
        # Clean up thread
        self.simulation_thread = None


def main():
    """Main function"""
    app = QApplication(sys.argv)
    
    # Enable high DPI support
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create and show test window
    window = RealScenarioTest()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()