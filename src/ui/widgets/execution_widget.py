"""
Macro execution control widget
"""

from typing import Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QProgressBar, QTableWidget, QTableWidgetItem, QGroupBox,
    QTextEdit, QSplitter, QHeaderView, QCheckBox, QSystemTrayIcon
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QBrush, QFont
from automation.engine import ExecutionEngine, ExecutionState, ExecutionResult
from excel.excel_manager import ExcelManager
from core.macro_types import Macro, MacroStep
from config.settings import Settings
from logger.app_logger import get_logger
from ui.widgets.preparation_widget import PreparationWidget
from ui.widgets.floating_status_widget import FloatingStatusWidget, ProgressData, ExecutionMode, DisplayMode

class ExecutionStatusWidget(QWidget):
    """Widget showing execution status"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Status label
        self.status_label = QLabel("대기 중")
        self.status_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(14)
        font.setBold(True)
        self.status_label.setFont(font)
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        layout.addWidget(self.progress_bar)
        
        # Statistics
        stats_layout = QHBoxLayout()
        
        self.total_label = QLabel("전체: 0")
        stats_layout.addWidget(self.total_label)
        
        self.completed_label = QLabel("완료: 0")
        self.completed_label.setStyleSheet("color: green;")
        stats_layout.addWidget(self.completed_label)
        
        self.failed_label = QLabel("실패: 0")
        self.failed_label.setStyleSheet("color: red;")
        stats_layout.addWidget(self.failed_label)
        
        self.time_label = QLabel("소요시간: 0:00")
        stats_layout.addWidget(self.time_label)
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        self.setLayout(layout)
        
    def update_status(self, state: ExecutionState):
        """Update status display"""
        status_map = {
            ExecutionState.IDLE: ("대기 중", "#000000"),
            ExecutionState.RUNNING: ("실행 중", "#00aa00"),
            ExecutionState.PAUSED: ("일시정지", "#ff8800"),
            ExecutionState.STOPPING: ("정지 중...", "#aa0000"),
            ExecutionState.STOPPED: ("정지됨", "#aa0000"),
            ExecutionState.ERROR: ("오류", "#ff0000")
        }
        
        text, color = status_map.get(state, ("알 수 없음", "#000000"))
        self.status_label.setText(text)
        self.status_label.setStyleSheet(f"color: {color};")
        
    def update_progress(self, current: int, total: int):
        """Update progress bar"""
        self.progress_bar.setMaximum(total)
        self.progress_bar.setValue(current)
        self.progress_bar.setFormat(f"{current}/{total} ({current/total*100:.1f}%)")
        
    def update_statistics(self, total: int, completed: int, failed: int, elapsed_seconds: float):
        """Update statistics"""
        self.total_label.setText(f"전체: {total}")
        self.completed_label.setText(f"완료: {completed}")
        self.failed_label.setText(f"실패: {failed}")
        
        minutes = int(elapsed_seconds // 60)
        seconds = int(elapsed_seconds % 60)
        self.time_label.setText(f"소요시간: {minutes}:{seconds:02d}")

class ExecutionLogWidget(QTableWidget):
    """Widget showing execution log"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        # Set columns
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels(["시간", "행", "단계", "상태", "메시지"])
        
        # Configure table
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        
        self.setColumnWidth(1, 60)  # Row
        self.setColumnWidth(3, 80)  # Status
        
        # Style
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        
    def add_log_entry(self, timestamp: str, row: int, step_name: str, 
                      success: bool, message: str = ""):
        """Add log entry"""
        row_count = self.rowCount()
        self.insertRow(row_count)
        
        # Time
        self.setItem(row_count, 0, QTableWidgetItem(timestamp))
        
        # Row number
        row_item = QTableWidgetItem(str(row + 1))
        row_item.setTextAlignment(Qt.AlignCenter)
        self.setItem(row_count, 1, row_item)
        
        # Step name
        self.setItem(row_count, 2, QTableWidgetItem(step_name))
        
        # Status
        status_item = QTableWidgetItem("성공" if success else "실패")
        status_item.setTextAlignment(Qt.AlignCenter)
        if success:
            status_item.setForeground(QBrush(QColor(0, 150, 0)))
        else:
            status_item.setForeground(QBrush(QColor(200, 0, 0)))
        self.setItem(row_count, 3, status_item)
        
        # Message
        self.setItem(row_count, 4, QTableWidgetItem(message))
        
        # Auto scroll to bottom
        self.scrollToBottom()

class ExecutionControlWidget(QWidget):
    """Execution control buttons"""
    
    startRequested = pyqtSignal()
    prepareRequested = pyqtSignal()  # 동작 준비 신호 추가
    pauseRequested = pyqtSignal()
    stopRequested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QHBoxLayout()
        
        # Prepare button (동작 준비)
        self.prepare_btn = QPushButton("동작 준비")
        self.prepare_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        self.prepare_btn.clicked.connect(self.prepareRequested.emit)
        layout.addWidget(self.prepare_btn)
        
        # Start button
        self.start_btn = QPushButton("▶ 시작")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.start_btn.clicked.connect(self.startRequested.emit)
        layout.addWidget(self.start_btn)
        
        # Pause button
        self.pause_btn = QPushButton("⏸ 일시정지")
        self.pause_btn.setEnabled(False)
        self.pause_btn.clicked.connect(self.pauseRequested.emit)
        layout.addWidget(self.pause_btn)
        
        # Stop button
        self.stop_btn = QPushButton("⏹ 정지")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet("""
            QPushButton:enabled {
                background-color: #f44336;
                color: white;
            }
        """)
        self.stop_btn.clicked.connect(self.stopRequested.emit)
        layout.addWidget(self.stop_btn)
        
        layout.addStretch()
        
        # Hotkey info
        hotkey_label = QLabel("단축키: F9(일시정지), ESC(정지)")
        hotkey_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(hotkey_label)
        
        self.setLayout(layout)
        
    def set_running_state(self, is_running: bool, is_paused: bool = False, is_preparing: bool = False):
        """Update button states"""
        self.prepare_btn.setEnabled(not is_running and not is_preparing)
        self.start_btn.setEnabled(not is_running and not is_preparing)
        self.pause_btn.setEnabled(is_running)
        self.stop_btn.setEnabled(is_running or is_preparing)
        
        if is_paused:
            self.pause_btn.setText("▶ 재개")
        else:
            self.pause_btn.setText("⏸ 일시정지")

class ExecutionWidget(QWidget):
    """Complete execution widget"""
    
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.logger = get_logger(__name__)
        
        # Execution engine
        self.engine = ExecutionEngine(settings)
        self.current_macro: Optional[Macro] = None
        self.excel_manager: Optional[ExcelManager] = None
        
        # Statistics
        self.start_time = None
        self.completed_count = 0
        self.failed_count = 0
        
        # Timer for elapsed time
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_elapsed_time)
        
        # Preparation widget
        self.preparation_widget = None
        self.is_preparing = False
        
        # Floating status widget
        self.floating_widget = None
        
        self.init_ui()
        self.connect_signals()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Control buttons
        self.control_widget = ExecutionControlWidget()
        layout.addWidget(self.control_widget)
        
        # Status display
        status_group = QGroupBox("실행 상태")
        status_layout = QVBoxLayout()
        self.status_widget = ExecutionStatusWidget()
        status_layout.addWidget(self.status_widget)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Options
        options_layout = QHBoxLayout()
        self.incomplete_only_checkbox = QCheckBox("미완료 항목만 실행")
        self.incomplete_only_checkbox.setChecked(True)
        options_layout.addWidget(self.incomplete_only_checkbox)
        options_layout.addStretch()
        layout.addLayout(options_layout)
        
        # Log display
        log_group = QGroupBox("실행 로그")
        log_layout = QVBoxLayout()
        
        # Log toolbar
        log_toolbar_layout = QHBoxLayout()
        log_toolbar_layout.addStretch()
        
        view_logs_btn = QPushButton("CSV 로그 보기")
        view_logs_btn.clicked.connect(self.show_log_viewer)
        log_toolbar_layout.addWidget(view_logs_btn)
        
        log_layout.addLayout(log_toolbar_layout)
        
        self.log_widget = ExecutionLogWidget()
        log_layout.addWidget(self.log_widget)
        log_group.setLayout(log_layout)
        layout.addWidget(log_group)
        
        self.setLayout(layout)
        
    def connect_signals(self):
        """Connect signals"""
        # Control signals
        self.control_widget.startRequested.connect(self.start_execution)
        self.control_widget.prepareRequested.connect(self.prepare_execution)
        self.control_widget.pauseRequested.connect(self.toggle_pause)
        self.control_widget.stopRequested.connect(self.stop_execution)
        
        # Engine signals
        self.engine.stateChanged.connect(self._on_state_changed)
        self.engine.progressUpdated.connect(self._on_progress_updated)
        self.engine.progressInfoUpdated.connect(self._on_progress_info_updated)
        self.engine.rowCompleted.connect(self._on_row_completed)
        self.engine.stepExecuting.connect(self._on_step_executing)
        self.engine.executionFinished.connect(self._on_execution_finished)
        self.engine.error.connect(self._on_error)
        
    def set_macro_and_excel(self, macro: Macro, excel_manager: Optional[ExcelManager] = None):
        """Set macro and Excel manager"""
        self.current_macro = macro
        self.excel_manager = excel_manager
        
        # Show/hide Excel-specific controls
        self.incomplete_only_checkbox.setVisible(excel_manager is not None)
        
    def prepare_execution(self):
        """Enter preparation mode"""
        if not self.current_macro:
            self.logger.warning("No macro loaded")
            return
            
        # Set preparing state
        self.is_preparing = True
        self.control_widget.set_running_state(False, False, True)
        
        # Get countdown seconds from settings
        countdown_seconds = self.settings.get("notification.preparation.countdown_seconds", 5)
        
        # Create preparation widget if not exists
        if not self.preparation_widget:
            self.preparation_widget = PreparationWidget(countdown_seconds=countdown_seconds)
            self.preparation_widget.startNow.connect(self._on_preparation_start_now)
            self.preparation_widget.cancelled.connect(self._on_preparation_cancelled)
            self.preparation_widget.countdownFinished.connect(self._on_preparation_finished)
            
        # Connect hotkey listener for F5 during preparation
        if hasattr(self.engine, 'hotkey_listener'):
            self.engine.hotkey_listener.startPressed.connect(self._on_hotkey_start_pressed)
        
        # Minimize main window
        main_window = self.window()
        if main_window:
            main_window.showMinimized()
        
        # Start countdown
        self.preparation_widget.start_countdown()
        
    def _on_preparation_start_now(self):
        """Handle immediate start from preparation"""
        self.is_preparing = False
        self.start_execution()
        
    def _on_preparation_cancelled(self):
        """Handle preparation cancellation"""
        self.is_preparing = False
        self.control_widget.set_running_state(False, False, False)
        
        # Restore main window
        main_window = self.window()
        if main_window:
            main_window.showNormal()
            
    def _on_preparation_finished(self):
        """Handle preparation countdown finished"""
        self.is_preparing = False
        self.start_execution()
        
    def _on_hotkey_start_pressed(self):
        """Handle F5 hotkey press"""
        if self.is_preparing and self.preparation_widget and self.preparation_widget.isVisible():
            self.preparation_widget.start_now()
    
    def start_execution(self):
        """Start macro execution"""
        if not self.current_macro:
            self.logger.warning("No macro loaded")
            return
            
        # Reset statistics
        self.completed_count = 0
        self.failed_count = 0
        from PyQt5.QtCore import QTime
        self.start_time = QTime.currentTime()
        self.log_widget.setRowCount(0)
        
        # Create and show floating widget
        if not self.floating_widget:
            self.floating_widget = FloatingStatusWidget()
            self.floating_widget.pauseClicked.connect(self.toggle_pause)
            self.floating_widget.stopClicked.connect(self.stop_execution)
            
            # Position at bottom right of screen
            from PyQt5.QtWidgets import QApplication
            screen = QApplication.primaryScreen().geometry()
            x = screen.width() - 320
            y = screen.height() - 120
            self.floating_widget.show_at_position(x, y)
        else:
            self.floating_widget.show()
            
        # Set initial status
        self.floating_widget.set_status("매크로 시작 중...", "▶")
        
        # Configure engine
        self.engine.set_macro(self.current_macro, self.excel_manager)
        
        # Set target rows based on Excel availability
        if self.excel_manager:
            if self.incomplete_only_checkbox.isChecked():
                # Let engine use default (incomplete rows)
                self.engine.set_target_rows([])
            else:
                # Execute all rows
                total_rows = len(self.excel_manager._current_data.dataframe)
                self.engine.set_target_rows(list(range(total_rows)))
        else:
            # No Excel - standalone mode
            self.engine.set_target_rows([])
            
        # Start execution
        self.engine.start()
        self.timer.start(1000)  # Update every second
        
    def toggle_pause(self):
        """Toggle pause state"""
        self.engine.toggle_pause()
        
    def stop_execution(self):
        """Stop execution"""
        self.engine.stop_execution()
        
    def _on_state_changed(self, state: ExecutionState):
        """Handle state change"""
        self.status_widget.update_status(state)
        
        is_running = state in [ExecutionState.RUNNING, ExecutionState.PAUSED]
        is_paused = state == ExecutionState.PAUSED
        self.control_widget.set_running_state(is_running, is_paused)
        
        # Update floating widget
        if self.floating_widget:
            if state == ExecutionState.RUNNING:
                self.floating_widget.set_status("실행 중", "▶")
                self.floating_widget.set_paused(False)
            elif state == ExecutionState.PAUSED:
                self.floating_widget.set_status("일시정지", "⏸")
                self.floating_widget.set_paused(True)
            elif state == ExecutionState.IDLE:
                self.floating_widget.set_status("완료", "O")
                # Show completion animation if no errors
                if self.failed_count == 0:
                    self.floating_widget.show_completion_animation()
            elif state == ExecutionState.ERROR:
                self.floating_widget.set_status("오류", "X")
                self.floating_widget.set_error(True)
                
        # Update system tray
        self._update_system_tray(state)
        
        if not is_running:
            self.timer.stop()
            # Hide floating widget after completion
            if self.floating_widget and state == ExecutionState.IDLE:
                QTimer.singleShot(3000, lambda: self.floating_widget.hide() if self.floating_widget else None)
            
    def _on_progress_updated(self, current: int, total: int):
        """Handle progress update"""
        self.status_widget.update_progress(current, total)
        
        # Update floating widget
        if self.floating_widget:
            # Determine execution mode
            mode = ExecutionMode.EXCEL if self.excel_manager else ExecutionMode.STANDALONE
            
            # Calculate percentage
            percentage = (current / total * 100) if total > 0 else 0
            
            # Create progress data
            progress_data = ProgressData(
                mode=mode,
                percentage=percentage,
                current_row=current if mode == ExecutionMode.EXCEL else None,
                total_rows=total if mode == ExecutionMode.EXCEL else None,
                current_step=current if mode == ExecutionMode.STANDALONE else None,
                total_steps=total if mode == ExecutionMode.STANDALONE else None
            )
            
            self.floating_widget.update_progress(progress_data)
            
        # Update system tray progress
        self._update_tray_progress(current, total)
            
    def _on_progress_info_updated(self, progress_info):
        """Handle detailed progress information update"""
        if self.floating_widget:
            # Convert ProgressInfo to ProgressData for floating widget
            from automation.progress_calculator import ExecutionMode as CalcExecutionMode
            
            # Get display text from progress calculator
            if hasattr(self.engine, 'progress_calculator') and self.engine.progress_calculator:
                display_text = self.engine.progress_calculator.get_display_text(
                    progress_info, 
                    include_identifier=True, 
                    include_step=True
                )
            else:
                display_text = ""
            
            # Create progress data
            progress_data = ProgressData(
                mode=ExecutionMode.EXCEL if progress_info.mode == CalcExecutionMode.EXCEL else ExecutionMode.STANDALONE,
                percentage=progress_info.percentage,
                current_row=progress_info.current_row,
                total_rows=progress_info.total_rows,
                current_step=progress_info.current_step_index,
                total_steps=progress_info.total_steps,
                row_identifier=progress_info.row_identifier,
                step_name=progress_info.current_step_name
            )
            
            # Update floating widget
            self.floating_widget.update_progress(progress_data)
            
            # Update status with detailed text
            if progress_info.in_loop:
                loop_text = f" (반복 {progress_info.loop_iteration}/{progress_info.loop_total})"
                self.floating_widget.set_status(display_text + loop_text, "▶")
        
    def _on_row_completed(self, result: ExecutionResult):
        """Handle row completion"""
        if result.success:
            self.completed_count += 1
        else:
            self.failed_count += 1
            
        # Add to log
        import time
        timestamp = time.strftime("%H:%M:%S", time.localtime(result.timestamp))
        self.log_widget.add_log_entry(
            timestamp,
            result.row_index,
            "행 완료",
            result.success,
            result.error or f"소요시간: {result.duration_ms:.0f}ms"
        )
        
    def _on_step_executing(self, step: MacroStep, row_index: int):
        """Handle step execution"""
        # Could add detailed step logging here if needed
        pass
        
    def _on_execution_finished(self):
        """Handle execution finished"""
        self.logger.info("Execution finished")
        self.timer.stop()
        
    def _on_error(self, error_msg: str):
        """Handle execution error"""
        self.logger.error(f"Execution error: {error_msg}")
        
        # Show error dialog
        from ui.dialogs.error_report_dialog import ErrorReportDialog
        from logger.execution_logger import get_execution_logger
        
        log_file = get_execution_logger().get_current_log_file()
        ErrorReportDialog.show_error(
            "Execution Error",
            error_msg,
            log_file=log_file,
            parent=self
        )
        
    def _update_elapsed_time(self):
        """Update elapsed time display"""
        if self.start_time:
            from PyQt5.QtCore import QTime
            elapsed = self.start_time.secsTo(QTime.currentTime())
            total = self.completed_count + self.failed_count
            self.status_widget.update_statistics(
                total, self.completed_count, self.failed_count, elapsed
            )
            
            # Update floating widget time and stats
            if self.floating_widget:
                minutes = elapsed // 60
                seconds = elapsed % 60
                elapsed_str = f"{minutes:02d}:{seconds:02d}"
                
                # Get current progress data and update with time/stats
                mode = ExecutionMode.EXCEL if self.excel_manager else ExecutionMode.STANDALONE
                current_progress = self.floating_widget.progress_bar.value()
                
                progress_data = ProgressData(
                    mode=mode,
                    percentage=current_progress,
                    elapsed_time=elapsed_str,
                    success_count=self.completed_count,
                    failure_count=self.failed_count
                )
                
                self.floating_widget.update_progress(progress_data)
            
    def show_log_viewer(self):
        """Show log viewer dialog"""
        from ui.dialogs.log_viewer_dialog import LogViewerDialog
        from logger.execution_logger import get_execution_logger
        
        # Open with current log file if available
        log_file = get_execution_logger().get_current_log_file()
        dialog = LogViewerDialog(log_file=log_file, parent=self)
        dialog.show()  # Non-modal
        
    def set_compact_mode(self, is_compact: bool):
        """Apply compact mode to the execution widget"""
        if is_compact:
            # Reduce spacing in main layout
            self.layout().setSpacing(5)
            self.layout().setContentsMargins(5, 5, 5, 5)
            
            # Adjust group boxes
            for group_box in self.findChildren(QGroupBox):
                group_box.setContentsMargins(5, 15, 5, 5)
                
            # Set compact height for log table rows
            self.log_widget.verticalHeader().setDefaultSectionSize(22)
        else:
            # Reset to normal spacing
            self.layout().setSpacing(10)
            self.layout().setContentsMargins(10, 10, 10, 10)
            
            # Reset group boxes
            for group_box in self.findChildren(QGroupBox):
                group_box.setContentsMargins(9, 20, 9, 9)
                
            # Reset log table row height
            self.log_widget.verticalHeader().setDefaultSectionSize(30)
            
    def _update_system_tray(self, state: ExecutionState):
        """Update system tray based on execution state"""
        # Get main window's tray manager
        main_window = self.window()
        if hasattr(main_window, 'tray_manager') and main_window.tray_manager:
            tray_manager = main_window.tray_manager
            
            # Map execution state to tray state
            state_map = {
                ExecutionState.IDLE: "idle",
                ExecutionState.RUNNING: "running",
                ExecutionState.PAUSED: "paused",
                ExecutionState.ERROR: "error",
                ExecutionState.STOPPING: "running",
                ExecutionState.STOPPED: "idle"
            }
            
            tray_state = state_map.get(state, "idle")
            is_running = state in [ExecutionState.RUNNING, ExecutionState.PAUSED]
            
            # Update tray icon and menu
            tray_manager.set_execution_state(tray_state, is_running)
            
            # Update floating widget visibility in tray menu
            if self.floating_widget:
                tray_manager.set_floating_widget_visible(self.floating_widget.isVisible())
                
            # Show tray notifications
            if self.settings.get("notification.system_tray.show_notifications", True):
                if state == ExecutionState.RUNNING and self.is_preparing:
                    tray_manager.show_message(
                        "매크로 실행",
                        f"{self.current_macro.name} 매크로 실행을 시작합니다.",
                        duration=2000
                    )
                elif state == ExecutionState.IDLE and self.completed_count + self.failed_count > 0:
                    tray_manager.show_message(
                        "매크로 완료",
                        f"완료: {self.completed_count}, 실패: {self.failed_count}",
                        duration=3000
                    )
                elif state == ExecutionState.ERROR:
                    tray_manager.show_message(
                        "매크로 오류",
                        "매크로 실행 중 오류가 발생했습니다.",
                        QSystemTrayIcon.Critical,
                        duration=5000
                    )
                    
    def _update_tray_progress(self, current: int, total: int):
        """Update system tray with progress"""
        main_window = self.window()
        if hasattr(main_window, 'tray_manager') and main_window.tray_manager:
            percentage = int((current / total * 100)) if total > 0 else 0
            
            if self.excel_manager:
                status_text = f"행 {current}/{total}"
            else:
                status_text = f"단계 {current}/{total}"
                
            main_window.tray_manager.set_progress(percentage, status_text)