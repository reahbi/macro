"""
Integrated Excel workflow widget combining data preview and editor
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
    QGroupBox, QTableWidget, QTableWidgetItem,
    QListWidget, QListWidgetItem, QPushButton,
    QLabel, QComboBox, QProgressBar, QToolBar,
    QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QBrush
from excel.excel_manager import ExcelManager
from core.macro_types import Macro, MacroStep, LoopStep
from automation.engine import ExecutionEngine, ExecutionState, ExecutionResult
from config.settings import Settings


class ExcelWorkflowWidget(QWidget):
    """Integrated widget for Excel workflow execution"""
    
    # Signals
    executionStarted = pyqtSignal()
    executionFinished = pyqtSignal()
    rowProcessed = pyqtSignal(int, bool, str)  # row_index, success, message
    
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.excel_manager = None
        self.macro = None
        self.execution_engine = None
        self.current_row = -1
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Toolbar
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # Main splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Excel data
        excel_widget = self.create_excel_widget()
        splitter.addWidget(excel_widget)
        
        # Right side - Workflow steps
        workflow_widget = self.create_workflow_widget()
        splitter.addWidget(workflow_widget)
        
        # Set splitter sizes (60% excel, 40% workflow)
        splitter.setSizes([600, 400])
        layout.addWidget(splitter)
        
        # Bottom - Execution status
        status_widget = self.create_status_widget()
        layout.addWidget(status_widget)
        
    def create_toolbar(self):
        """Create toolbar with actions"""
        toolbar = QToolBar()
        
        # File actions
        toolbar.addAction("📁 파일 열기", self.open_excel_file)
        toolbar.addAction("💾 워크플로우 저장", self.save_workflow)
        toolbar.addSeparator()
        
        # Execution actions
        self.start_action = toolbar.addAction("▶️ 실행", self.start_execution)
        self.pause_action = toolbar.addAction("⏸️ 일시정지", self.pause_execution)
        self.pause_action.setEnabled(False)
        self.stop_action = toolbar.addAction("⏹️ 중지", self.stop_execution)
        self.stop_action.setEnabled(False)
        toolbar.addSeparator()
        
        # View actions
        toolbar.addAction("🔍 전체 행 보기", self.show_all_rows)
        toolbar.addAction("❌ 실패한 행만", self.show_failed_rows)
        toolbar.addAction("✅ 완료된 행만", self.show_completed_rows)
        
        return toolbar
        
    def create_excel_widget(self):
        """Create Excel data preview widget"""
        group = QGroupBox("Excel 데이터")
        layout = QVBoxLayout()
        
        # Info bar
        info_layout = QHBoxLayout()
        self.file_label = QLabel("파일: 없음")
        info_layout.addWidget(self.file_label)
        
        self.sheet_combo = QComboBox()
        self.sheet_combo.currentTextChanged.connect(self.on_sheet_changed)
        info_layout.addWidget(self.sheet_combo)
        
        self.row_count_label = QLabel("행: 0")
        info_layout.addWidget(self.row_count_label)
        info_layout.addStretch()
        
        layout.addLayout(info_layout)
        
        # Data table
        self.data_table = QTableWidget()
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.data_table)
        
        group.setLayout(layout)
        return group
        
    def create_workflow_widget(self):
        """Create workflow steps widget"""
        group = QGroupBox("워크플로우 단계")
        layout = QVBoxLayout()
        
        # Steps list
        self.steps_list = QListWidget()
        self.steps_list.setAlternatingRowColors(True)
        layout.addWidget(self.steps_list)
        
        # Step info
        info_group = QGroupBox("현재 실행 중")
        info_layout = QVBoxLayout()
        
        self.current_step_label = QLabel("대기 중...")
        self.current_step_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        info_layout.addWidget(self.current_step_label)
        
        self.step_detail_label = QLabel("")
        self.step_detail_label.setWordWrap(True)
        info_layout.addWidget(self.step_detail_label)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        group.setLayout(layout)
        return group
        
    def create_status_widget(self):
        """Create execution status widget"""
        group = QGroupBox("실행 상태")
        layout = QVBoxLayout()
        
        # Progress bar
        progress_layout = QHBoxLayout()
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("0/0")
        progress_layout.addWidget(self.progress_label)
        
        layout.addLayout(progress_layout)
        
        # Statistics
        stats_layout = QHBoxLayout()
        
        self.total_label = QLabel("전체: 0")
        self.success_label = QLabel("성공: 0")
        self.success_label.setStyleSheet("color: green;")
        self.failed_label = QLabel("실패: 0")
        self.failed_label.setStyleSheet("color: red;")
        self.pending_label = QLabel("대기: 0")
        self.pending_label.setStyleSheet("color: orange;")
        
        stats_layout.addWidget(self.total_label)
        stats_layout.addWidget(self.success_label)
        stats_layout.addWidget(self.failed_label)
        stats_layout.addWidget(self.pending_label)
        stats_layout.addStretch()
        
        # Time info
        self.time_label = QLabel("경과 시간: 00:00:00")
        stats_layout.addWidget(self.time_label)
        
        layout.addLayout(stats_layout)
        
        group.setLayout(layout)
        return group
        
    def open_excel_file(self):
        """Open Excel file"""
        from PyQt5.QtWidgets import QFileDialog
        
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Excel 파일 열기",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*.*)"
        )
        
        if file_path:
            self.load_excel_file(file_path)
            
    def load_excel_file(self, file_path: str):
        """Load Excel file and update UI"""
        try:
            self.excel_manager = ExcelManager()
            file_info = self.excel_manager.load_file(file_path)
            
            if file_info:
                # Update UI
                import os
                self.file_label.setText(f"파일: {os.path.basename(file_path)}")
                
                # Update sheet combo
                self.sheet_combo.clear()
                self.sheet_combo.addItems(file_info.sheets)
                
        except Exception as e:
            QMessageBox.critical(self, "오류", f"파일 로드 실패: {str(e)}")
            
    def on_sheet_changed(self, sheet_name: str):
        """Handle sheet selection change"""
        if sheet_name and self.excel_manager:
            self.excel_manager.set_active_sheet(sheet_name)
            self.update_data_table()
            
    def update_data_table(self):
        """Update data table with Excel data"""
        if not self.excel_manager:
            return
            
        try:
            df = self.excel_manager.get_sheet_data()
            if df is not None:
                # Update row count
                self.row_count_label.setText(f"행: {len(df)}")
                
                # Update table
                self.data_table.setRowCount(len(df))
                self.data_table.setColumnCount(len(df.columns) + 1)  # +1 for status
                
                # Set headers
                headers = ["상태"] + df.columns.tolist()
                self.data_table.setHorizontalHeaderLabels(headers)
                
                # Populate data
                for row in range(len(df)):
                    # Status column
                    status_item = QTableWidgetItem("대기")
                    status_item.setBackground(QBrush(QColor(200, 200, 200)))
                    self.data_table.setItem(row, 0, status_item)
                    
                    # Data columns
                    for col in range(len(df.columns)):
                        value = df.iloc[row, col]
                        item = QTableWidgetItem(str(value))
                        self.data_table.setItem(row, col + 1, item)
                        
                # Resize columns
                self.data_table.resizeColumnsToContents()
                
                # Update statistics
                self.update_statistics()
                
        except Exception as e:
            print(f"Error updating data table: {e}")
            
    def update_statistics(self):
        """Update execution statistics"""
        if not self.data_table:
            return
            
        total = self.data_table.rowCount()
        success = 0
        failed = 0
        pending = 0
        
        for row in range(total):
            status_item = self.data_table.item(row, 0)
            if status_item:
                status = status_item.text()
                if status == "완료":
                    success += 1
                elif status == "실패":
                    failed += 1
                else:
                    pending += 1
                    
        self.total_label.setText(f"전체: {total}")
        self.success_label.setText(f"성공: {success}")
        self.failed_label.setText(f"실패: {failed}")
        self.pending_label.setText(f"대기: {pending}")
        
        # Update progress
        if total > 0:
            progress = ((success + failed) / total) * 100
            self.progress_bar.setValue(int(progress))
            self.progress_label.setText(f"{success + failed}/{total}")
            
    def set_macro(self, macro: Macro):
        """Set the macro to execute"""
        self.macro = macro
        self.update_steps_list()
        
    def update_steps_list(self):
        """Update workflow steps list"""
        self.steps_list.clear()
        
        if not self.macro:
            return
            
        # Find loop step
        for step in self.macro.steps:
            if isinstance(step, LoopStep) and step.loop_type == "excel_rows":
                # Show nested steps
                for i, nested_step in enumerate(step.steps):
                    item_text = f"{i+1}. {nested_step.name}"
                    self.steps_list.addItem(item_text)
                break
                
    def start_execution(self):
        """Start workflow execution"""
        if not self.excel_manager or not self.macro:
            QMessageBox.warning(self, "경고", "Excel 파일과 워크플로우를 먼저 설정하세요.")
            return
            
        # Create execution engine
        self.execution_engine = ExecutionEngine(self.settings)
        self.execution_engine.set_macro(self.macro, self.excel_manager)
        
        # Connect signals
        self.execution_engine.stateChanged.connect(self.on_state_changed)
        self.execution_engine.rowCompleted.connect(self.on_row_completed)
        self.execution_engine.stepExecuting.connect(self.on_step_executing)
        self.execution_engine.executionFinished.connect(self.on_execution_finished)
        
        # Update UI
        self.start_action.setEnabled(False)
        self.pause_action.setEnabled(True)
        self.stop_action.setEnabled(True)
        
        # Start timer for elapsed time
        self.start_time = QTimer()
        self.start_time.timeout.connect(self.update_elapsed_time)
        self.start_time.start(1000)  # Update every second
        self.elapsed_seconds = 0
        
        # Start execution
        self.execution_engine.start()
        self.executionStarted.emit()
        
    def pause_execution(self):
        """Pause/resume execution"""
        if self.execution_engine:
            self.execution_engine.toggle_pause()
            
    def stop_execution(self):
        """Stop execution"""
        if self.execution_engine:
            self.execution_engine.stop_execution()
            
    def on_state_changed(self, state: ExecutionState):
        """Handle execution state change"""
        if state == ExecutionState.PAUSED:
            self.pause_action.setText("▶️ 재개")
        elif state == ExecutionState.RUNNING:
            self.pause_action.setText("⏸️ 일시정지")
        elif state in [ExecutionState.IDLE, ExecutionState.STOPPED, ExecutionState.ERROR]:
            self.start_action.setEnabled(True)
            self.pause_action.setEnabled(False)
            self.stop_action.setEnabled(False)
            if self.start_time:
                self.start_time.stop()
                
    def on_row_completed(self, result: ExecutionResult):
        """Handle row completion"""
        row_index = result.row_index
        
        # Update table status
        if row_index < self.data_table.rowCount():
            status_item = self.data_table.item(row_index, 0)
            if status_item:
                if result.success:
                    status_item.setText("완료")
                    status_item.setBackground(QBrush(QColor(144, 238, 144)))  # Light green
                else:
                    status_item.setText("실패")
                    status_item.setBackground(QBrush(QColor(255, 182, 193)))  # Light red
                    status_item.setToolTip(result.error or "Unknown error")
                    
        # Highlight current row
        self.data_table.selectRow(row_index)
        
        # Update statistics
        self.update_statistics()
        
        # Emit signal
        self.rowProcessed.emit(row_index, result.success, result.error or "")
        
    def on_step_executing(self, step: MacroStep, row_index: int):
        """Handle step execution"""
        self.current_row = row_index
        self.current_step_label.setText(f"실행 중: {step.name}")
        
        # Update step details
        details = []
        if hasattr(step, 'search_text'):
            details.append(f"검색: {step.search_text}")
        if hasattr(step, 'text'):
            details.append(f"입력: {step.text}")
        if hasattr(step, 'x') and hasattr(step, 'y'):
            details.append(f"위치: ({step.x}, {step.y})")
            
        self.step_detail_label.setText("\n".join(details))
        
        # Highlight current step
        for i in range(self.steps_list.count()):
            item = self.steps_list.item(i)
            if item.text().startswith(f"{self.steps_list.currentRow() + 1}."):
                self.steps_list.setCurrentItem(item)
                break
                
    def on_execution_finished(self):
        """Handle execution completion"""
        self.current_step_label.setText("실행 완료")
        self.step_detail_label.setText("")
        
        # Show summary
        total = self.data_table.rowCount()
        success = int(self.success_label.text().split(": ")[1])
        failed = int(self.failed_label.text().split(": ")[1])
        
        QMessageBox.information(
            self,
            "실행 완료",
            f"워크플로우 실행이 완료되었습니다.\n\n"
            f"전체: {total}행\n"
            f"성공: {success}행\n"
            f"실패: {failed}행"
        )
        
        self.executionFinished.emit()
        
    def update_elapsed_time(self):
        """Update elapsed time display"""
        self.elapsed_seconds += 1
        hours = self.elapsed_seconds // 3600
        minutes = (self.elapsed_seconds % 3600) // 60
        seconds = self.elapsed_seconds % 60
        self.time_label.setText(f"경과 시간: {hours:02d}:{minutes:02d}:{seconds:02d}")
        
    def show_all_rows(self):
        """Show all rows"""
        for row in range(self.data_table.rowCount()):
            self.data_table.setRowHidden(row, False)
            
    def show_failed_rows(self):
        """Show only failed rows"""
        for row in range(self.data_table.rowCount()):
            status_item = self.data_table.item(row, 0)
            if status_item:
                self.data_table.setRowHidden(row, status_item.text() != "실패")
                
    def show_completed_rows(self):
        """Show only completed rows"""
        for row in range(self.data_table.rowCount()):
            status_item = self.data_table.item(row, 0)
            if status_item:
                self.data_table.setRowHidden(row, status_item.text() != "완료")
                
    def save_workflow(self):
        """Save current workflow"""
        if not self.macro:
            QMessageBox.warning(self, "경고", "저장할 워크플로우가 없습니다.")
            return
            
        from PyQt5.QtWidgets import QFileDialog
        from core.macro_storage import MacroStorage, MacroFormat
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "워크플로우 저장",
            "",
            "JSON Files (*.json);;Encrypted Files (*.emf);;All Files (*.*)"
        )
        
        if file_path:
            try:
                storage = MacroStorage()
                format_type = MacroFormat.ENCRYPTED if file_path.endswith('.emf') else MacroFormat.JSON
                success = storage.save_macro(self.macro, file_path, format_type)
                
                if success:
                    QMessageBox.information(self, "성공", "워크플로우가 저장되었습니다.")
                else:
                    QMessageBox.critical(self, "오류", "워크플로우 저장에 실패했습니다.")
            except Exception as e:
                QMessageBox.critical(self, "오류", f"저장 오류: {str(e)}")