"""
Macro execution control widget
"""

from typing import Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QProgressBar, QTableWidget, QTableWidgetItem, QGroupBox,
    QTextEdit, QSplitter, QHeaderView, QCheckBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QColor, QBrush, QFont
from automation.engine import ExecutionEngine, ExecutionState, ExecutionResult
from excel.excel_manager import ExcelManager
from core.macro_types import Macro, MacroStep
from config.settings import Settings
from logger.app_logger import get_logger

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
    pauseRequested = pyqtSignal()
    stopRequested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QHBoxLayout()
        
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
        
    def set_running_state(self, is_running: bool, is_paused: bool = False):
        """Update button states"""
        self.start_btn.setEnabled(not is_running)
        self.pause_btn.setEnabled(is_running)
        self.stop_btn.setEnabled(is_running)
        
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
        self.control_widget.pauseRequested.connect(self.toggle_pause)
        self.control_widget.stopRequested.connect(self.stop_execution)
        
        # Engine signals
        self.engine.stateChanged.connect(self._on_state_changed)
        self.engine.progressUpdated.connect(self._on_progress_updated)
        self.engine.rowCompleted.connect(self._on_row_completed)
        self.engine.stepExecuting.connect(self._on_step_executing)
        self.engine.executionFinished.connect(self._on_execution_finished)
        self.engine.error.connect(self._on_error)
        
    def set_macro_and_excel(self, macro: Macro, excel_manager: ExcelManager):
        """Set macro and Excel manager"""
        self.current_macro = macro
        self.excel_manager = excel_manager
        
    def start_execution(self):
        """Start macro execution"""
        if not self.current_macro or not self.excel_manager:
            self.logger.warning("No macro or Excel data loaded")
            return
            
        # Reset statistics
        self.completed_count = 0
        self.failed_count = 0
        self.start_time = QTimer.currentTime()
        self.log_widget.setRowCount(0)
        
        # Configure engine
        self.engine.set_macro(self.current_macro, self.excel_manager)
        
        # Set target rows based on checkbox
        if self.incomplete_only_checkbox.isChecked():
            # Let engine use default (incomplete rows)
            self.engine.set_target_rows([])
        else:
            # Execute all rows
            total_rows = len(self.excel_manager._current_data.dataframe)
            self.engine.set_target_rows(list(range(total_rows)))
            
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
        
        if not is_running:
            self.timer.stop()
            
    def _on_progress_updated(self, current: int, total: int):
        """Handle progress update"""
        self.status_widget.update_progress(current, total)
        
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
        from dialogs.error_report_dialog import ErrorReportDialog
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
            elapsed = self.start_time.secsTo(QTimer.currentTime())
            total = self.completed_count + self.failed_count
            self.status_widget.update_statistics(
                total, self.completed_count, self.failed_count, elapsed
            )
            
    def show_log_viewer(self):
        """Show log viewer dialog"""
        from dialogs.log_viewer_dialog import LogViewerDialog
        from logger.execution_logger import get_execution_logger
        
        # Open with current log file if available
        log_file = get_execution_logger().get_current_log_file()
        dialog = LogViewerDialog(log_file=log_file, parent=self)
        dialog.show()  # Non-modal