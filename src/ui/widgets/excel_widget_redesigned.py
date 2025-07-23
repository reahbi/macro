"""
Redesigned Excel integration widget with data-centric layout
"""

from typing import Optional, List, Dict, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QMessageBox,
    QProgressDialog, QPushButton, QLabel, QComboBox, QToolBar,
    QAction, QStatusBar, QFrame, QMenu
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QBrush, QColor
from ui.widgets.file_selector import FileSelectorWidget
from ui.widgets.sheet_mapper_simplified import SheetMapperWidget
from ui.widgets.data_preview import DataPreviewWidget
import pandas as pd
from excel.excel_manager import ExcelManager
from excel.models import ExcelFileInfo, ColumnMapping
from logger.app_logger import get_logger

class CompactToolbar(QToolBar):
    """Compact toolbar for Excel operations"""
    
    fileRequested = pyqtSignal()
    sheetChanged = pyqtSignal(str)
    mappingToggled = pyqtSignal()
    filterToggled = pyqtSignal()
    resetAllRequested = pyqtSignal()
    completeAllRequested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.sheets = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize toolbar UI"""
        self.setMovable(False)
        self.setFixedHeight(40)
        
        # File selection
        self.file_btn = QPushButton("📁 파일 선택")
        self.file_btn.clicked.connect(self.fileRequested.emit)
        self.addWidget(self.file_btn)
        
        self.file_label = QLabel("파일 없음")
        self.file_label.setMaximumWidth(300)
        self.addWidget(self.file_label)
        
        self.addSeparator()
        
        # Sheet selection
        self.addWidget(QLabel("시트:"))
        self.sheet_combo = QComboBox()
        self.sheet_combo.setMinimumWidth(150)
        self.sheet_combo.currentTextChanged.connect(self.sheetChanged.emit)
        self.sheet_combo.setEnabled(False)
        self.addWidget(self.sheet_combo)
        
        self.addSeparator()
        
        # Mapping toggle
        self.mapping_btn = QPushButton("⚙ 매핑 설정")
        self.mapping_btn.setCheckable(True)
        self.mapping_btn.toggled.connect(self.mappingToggled.emit)
        self.addWidget(self.mapping_btn)
        
        # Filter menu
        self.filter_btn = QPushButton("🔽 필터")
        filter_menu = QMenu()
        filter_menu.addAction("전체 보기")
        filter_menu.addAction("완료 항목 숨기기")
        filter_menu.addAction("오류 항목만")
        filter_menu.addAction("대기 항목만")
        self.filter_btn.setMenu(filter_menu)
        self.addWidget(self.filter_btn)
        
        self.addSeparator()
        
        # Batch status buttons
        self.reset_all_btn = QPushButton("⟲ 모든 행 미완료로")
        self.reset_all_btn.setToolTip("모든 행의 상태를 미완료로 변경합니다")
        self.reset_all_btn.clicked.connect(self.resetAllRequested.emit)
        self.addWidget(self.reset_all_btn)
        
        self.complete_all_btn = QPushButton("✓ 모든 행 완료로")
        self.complete_all_btn.setToolTip("모든 행의 상태를 완료로 변경합니다")
        self.complete_all_btn.clicked.connect(self.completeAllRequested.emit)
        self.addWidget(self.complete_all_btn)
        
    def set_file_info(self, file_path: str, sheets: List[str]):
        """Update file information"""
        import os
        self.current_file = file_path
        self.sheets = sheets
        
        # Update file label
        file_name = os.path.basename(file_path)
        self.file_label.setText(file_name)
        self.file_label.setToolTip(file_path)
        
        # Update sheet combo
        self.sheet_combo.setEnabled(True)
        self.sheet_combo.clear()
        self.sheet_combo.addItems(sheets)
        
class CollapsibleSidePanel(QFrame):
    """Collapsible side panel for mapping configuration"""
    
    mappingComplete = pyqtSignal(str, list)
    
    def __init__(self):
        super().__init__()
        self.is_collapsed = True
        self.sheet_mapper = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        self.setFrameStyle(QFrame.Box)
        self.setFixedWidth(0)  # Start collapsed
        
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("열 매핑 설정")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title)
        
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.clicked.connect(self.collapse)
        header_layout.addWidget(close_btn)
        
        layout.addLayout(header_layout)
        
        # Sheet mapper widget
        self.sheet_mapper = SheetMapperWidget()
        self.sheet_mapper.mappingComplete.connect(self.on_mapping_complete)
        layout.addWidget(self.sheet_mapper)
        
        self.setLayout(layout)
        
        # Animation
        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.InOutQuart)
        
    def toggle(self):
        """Toggle panel visibility"""
        if self.is_collapsed:
            self.expand()
        else:
            self.collapse()
            
    def expand(self):
        """Expand panel"""
        self.is_collapsed = False
        self.animation.setStartValue(0)
        self.animation.setEndValue(300)
        self.animation.start()
        
    def collapse(self):
        """Collapse panel"""
        self.is_collapsed = True
        self.animation.setStartValue(300)
        self.animation.setEndValue(0)
        self.animation.start()
        
    def on_mapping_complete(self, sheet_name: str, mappings: list):
        """Handle mapping completion"""
        self.mappingComplete.emit(sheet_name, mappings)
        self.collapse()
        
class EnhancedDataTable(DataPreviewWidget):
    """Enhanced data table with integrated status visualization"""
    
    statusChanged = pyqtSignal(int, str)  # row_index, new_status
    
    def __init__(self):
        super().__init__()
        self.status_columns = ["매크로_상태", "매크로_실행시간", "매크로_오류메시지"]
        # Override parent's status column search to only use our macro status columns
        self.macro_status_added = False
        self.status_col_idx = None
        from logger.app_logger import get_logger
        self.logger = get_logger(__name__)
        
        # Connect cell click to handle status toggle
        self.data_table.cellClicked.connect(self.on_cell_clicked)
        
    def load_excel_data(self, excel_data):
        """Override to add status columns if not present"""
        # Add status columns if not present
        df = excel_data.dataframe
        
        # Handle existing status columns
        if "상태" in df.columns and "매크로_상태" not in df.columns:
            # Rename existing "상태" to "매크로_상태" to preserve data
            df = df.rename(columns={"상태": "매크로_상태"})
            # Update the dataframe reference
            excel_data.dataframe = df
            self.logger.info("Renamed existing '상태' column to '매크로_상태'")
        elif "상태" in df.columns and "매크로_상태" in df.columns:
            # If both exist, drop the generic "상태" column
            df = df.drop(columns=["상태"])
            excel_data.dataframe = df
        
        # Check if status column already exists (from excel_manager)
        existing_status_col = excel_data.get_status_column()
        
        # If no status column is set, or it's not 매크로_상태, update it
        if existing_status_col != "매크로_상태":
            # Add our status columns if not present
            from excel.models import MacroStatus
            for col in self.status_columns:
                if col not in df.columns:
                    if col == "매크로_상태":
                        # Initialize with PENDING status
                        df[col] = MacroStatus.PENDING
                    elif col == "매크로_실행시간":
                        df[col] = ""
                    elif col == "매크로_오류메시지":
                        df[col] = ""
            
            # Update excel_data
            excel_data.dataframe = df
            self.macro_status_added = True
            
            # Update the ExcelData's status column reference to match what we're using
            excel_data.set_status_column("매크로_상태")
        else:
            # Status column already properly set
            self.logger.info(f"Using existing status column: {existing_status_col}")
            self.macro_status_added = True
        
        # Find the status column index
        columns = df.columns.tolist()
        for idx, col in enumerate(columns):
            if col == "매크로_상태":
                self.status_col_idx = idx
                break
        
        # Call parent method
        super().load_excel_data(excel_data)
        
    def update_row_status(self, row_index: int, status: str, error_msg: str = ""):
        """Update status for a specific row with visual feedback"""
        if not self.excel_data:
            return
            
        # Update data
        df = self.excel_data.dataframe
        df.at[row_index, "매크로_상태"] = status
        df.at[row_index, "매크로_실행시간"] = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
        if error_msg:
            df.at[row_index, "매크로_오류메시지"] = error_msg
            
        # Update visual display
        self._apply_filter()  # Refresh display
        
        # Apply row coloring based on status
        if status == "처리중":
            self.highlight_row(row_index, QColor(255, 255, 200))  # Light yellow
        elif status == "완료":
            self.highlight_row(row_index, QColor(200, 255, 200))  # Light green
        elif status == "오류":
            self.highlight_row(row_index, QColor(255, 200, 200))  # Light red
            
    def highlight_row(self, row_index: int, color: QColor):
        """Highlight a specific row with color"""
        # TODO: Implement row highlighting in the table
        pass
        
    def on_cell_clicked(self, row: int, column: int):
        """Handle cell click - toggle status if clicking on status column"""
        if self.status_col_idx is not None and column == self.status_col_idx:
            # Get current status
            current_status = self.data_table.item(row, column)
            if current_status:
                current_value = current_status.text()
                
                # Toggle between "미완료", "처리중", "완료", "오류"
                from excel.models import MacroStatus
                if current_value == MacroStatus.PENDING or current_value == "":
                    new_status = MacroStatus.PROCESSING
                elif current_value == MacroStatus.PROCESSING:
                    new_status = MacroStatus.COMPLETED
                elif current_value == MacroStatus.COMPLETED:
                    new_status = MacroStatus.ERROR
                else:  # ERROR or anything else
                    new_status = MacroStatus.PENDING
                
                # Update the cell
                current_status.setText(new_status)
                
                # Apply color based on status
                if new_status == MacroStatus.PROCESSING:
                    current_status.setBackground(QBrush(QColor(255, 255, 200)))  # Light yellow
                elif new_status == MacroStatus.COMPLETED:
                    current_status.setBackground(QBrush(QColor(200, 255, 200)))  # Light green
                elif new_status == MacroStatus.ERROR:
                    current_status.setBackground(QBrush(QColor(255, 200, 200)))  # Light red
                else:  # PENDING
                    current_status.setBackground(QBrush(QColor(255, 255, 255)))  # White
                
                # Calculate actual dataframe row index
                actual_row = self.current_page * self.rows_per_page + row
                if self.filtered_indices is not None and actual_row < len(self.filtered_indices):
                    df_row_index = self.filtered_indices[actual_row]
                else:
                    df_row_index = actual_row
                
                # Update the dataframe
                if self.excel_data and df_row_index < len(self.excel_data.dataframe):
                    self.excel_data.dataframe.at[df_row_index, "매크로_상태"] = new_status
                
                # Emit signal for status change
                self.statusChanged.emit(df_row_index, new_status)

class ProgressStatusBar(QStatusBar):
    """Status bar with progress information and execution controls"""
    
    executeRequested = pyqtSignal()
    pauseRequested = pyqtSignal()
    stopRequested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.total_rows = 0
        self.completed_rows = 0
        self.error_rows = 0
        self.init_ui()
        
    def init_ui(self):
        """Initialize status bar UI"""
        # Progress info
        self.progress_label = QLabel("대기 중")
        self.addWidget(self.progress_label)
        
        # Separator
        separator = QFrame()
        separator.setFrameStyle(QFrame.VLine)
        self.addWidget(separator)
        
        # Stats
        self.stats_label = QLabel("완료: 0 | 오류: 0")
        self.addWidget(self.stats_label)
        
        # Stretch
        self.addWidget(QWidget(), 1)
        
        # Execution controls
        self.execute_btn = QPushButton("▶ 실행")
        self.execute_btn.clicked.connect(self.executeRequested.emit)
        self.addPermanentWidget(self.execute_btn)
        
        self.pause_btn = QPushButton("⏸ 일시정지")
        self.pause_btn.clicked.connect(self.pauseRequested.emit)
        self.pause_btn.setVisible(False)
        self.addPermanentWidget(self.pause_btn)
        
        self.stop_btn = QPushButton("⏹ 중지")
        self.stop_btn.clicked.connect(self.stopRequested.emit)
        self.stop_btn.setVisible(False)
        self.addPermanentWidget(self.stop_btn)
        
    def set_total_rows(self, total: int):
        """Set total number of rows"""
        self.total_rows = total
        self.update_display()
        
    def update_progress(self, completed: int, errors: int):
        """Update progress information"""
        self.completed_rows = completed
        self.error_rows = errors
        self.update_display()
        
    def update_display(self):
        """Update display labels"""
        if self.total_rows > 0:
            percentage = (self.completed_rows / self.total_rows) * 100
            self.progress_label.setText(f"진행: {self.completed_rows}/{self.total_rows} ({percentage:.1f}%)")
        else:
            self.progress_label.setText("대기 중")
            
        self.stats_label.setText(f"완료: {self.completed_rows - self.error_rows} | 오류: {self.error_rows}")
        
    def set_running(self, is_running: bool):
        """Update button visibility based on running state"""
        self.execute_btn.setVisible(not is_running)
        self.pause_btn.setVisible(is_running)
        self.stop_btn.setVisible(is_running)

class ExcelLoadThread(QThread):
    """Thread for loading Excel files"""
    
    fileLoaded = pyqtSignal(ExcelFileInfo)
    error = pyqtSignal(str)
    
    def __init__(self, excel_manager: ExcelManager, file_path: str):
        super().__init__()
        self.excel_manager = excel_manager
        self.file_path = file_path
        
    def run(self):
        """Run Excel loading in thread"""
        try:
            file_info = self.excel_manager.load_file(self.file_path)
            self.fileLoaded.emit(file_info)
        except Exception as e:
            self.error.emit(str(e))

class ExcelWidgetRedesigned(QWidget):
    """Redesigned Excel integration widget with data-centric layout"""
    
    dataReady = pyqtSignal(object)  # ExcelData
    tabSwitchRequested = pyqtSignal(int)  # Request to switch to editor tab
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.excel_manager = ExcelManager()
        self.current_file_info: Optional[ExcelFileInfo] = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI with new layout"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Compact toolbar
        self.toolbar = CompactToolbar()
        self.toolbar.fileRequested.connect(self.select_file)
        self.toolbar.sheetChanged.connect(self.on_sheet_changed)
        self.toolbar.mappingToggled.connect(self.toggle_mapping_panel)
        self.toolbar.resetAllRequested.connect(self.reset_all_status)
        self.toolbar.completeAllRequested.connect(self.complete_all_status)
        main_layout.addWidget(self.toolbar)
        
        # Central area (side panel + data table)
        central_widget = QWidget()
        central_layout = QHBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.setSpacing(0)
        
        # Collapsible side panel
        self.side_panel = CollapsibleSidePanel()
        self.side_panel.mappingComplete.connect(self.on_mapping_complete)
        central_layout.addWidget(self.side_panel)
        
        # Enhanced data table (main area)
        self.data_table = EnhancedDataTable()
        self.data_table.rowSelected.connect(self.on_row_selected)
        self.data_table.statusChanged.connect(self.on_status_changed)
        central_layout.addWidget(self.data_table, 1)  # Stretch factor 1
        
        central_widget.setLayout(central_layout)
        main_layout.addWidget(central_widget, 1)  # Stretch factor 1
        
        # Progress status bar
        self.status_bar = ProgressStatusBar()
        self.status_bar.executeRequested.connect(self.execute_macro)
        self.status_bar.pauseRequested.connect(self.pause_execution)
        self.status_bar.stopRequested.connect(self.stop_execution)
        main_layout.addWidget(self.status_bar)
        
        self.setLayout(main_layout)
        
    def select_file(self):
        """Open file selection dialog"""
        from PyQt5.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Excel 파일 선택",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*.*)"
        )
        
        if file_path:
            self.load_file(file_path)
            
    def load_file(self, file_path: str):
        """Load Excel file"""
        # Show progress dialog
        progress = QProgressDialog("Excel 파일 로딩 중...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        # Load file in thread
        self.load_thread = ExcelLoadThread(self.excel_manager, file_path)
        self.load_thread.fileLoaded.connect(lambda info: self.on_file_loaded(info, progress))
        self.load_thread.error.connect(lambda err: self.on_load_error(err, progress))
        self.load_thread.start()
        
    def on_file_loaded(self, file_info: ExcelFileInfo, progress: QProgressDialog):
        """Handle successful file load"""
        progress.close()
        self.current_file_info = file_info
        
        # Update toolbar
        sheet_names = [sheet.name for sheet in file_info.sheets]
        self.toolbar.set_file_info(file_info.file_path, sheet_names)
        
        # Update side panel
        self.side_panel.sheet_mapper.set_file_info(file_info.sheets)
        
        self.logger.info(f"Loaded Excel file: {file_info.file_path}")
        
    def on_load_error(self, error: str, progress: QProgressDialog):
        """Handle file load error"""
        progress.close()
        QMessageBox.critical(self, "파일 로드 오류", f"Excel 파일을 불러올 수 없습니다:\n{error}")
        self.logger.error(f"Failed to load Excel file: {error}")
        
    def on_sheet_changed(self, sheet_name: str):
        """Handle sheet selection change"""
        self.logger.info(f"on_sheet_changed called with sheet: {sheet_name}")
        
        # Check if we're in the middle of execution - if so, don't reload
        from automation.engine import ExecutionEngine
        # Note: This is a temporary check - in production, we should properly track execution state
        
        if sheet_name and self.excel_manager._current_file:
            self.excel_manager.set_active_sheet(sheet_name)
            
            # Check if we need to confirm status column usage
            if self.excel_manager.has_pending_status_column():
                column_name, existing_values = self.excel_manager.get_pending_status_info()
                
                # Show confirmation dialog
                msg = f"기존 상태 컬럼 '{column_name}'이(가) 발견되었습니다.\n\n"
                msg += f"현재 값들: {', '.join(existing_values[:10])}"
                if len(existing_values) > 10:
                    msg += f" ... (총 {len(existing_values)}개)"
                msg += "\n\n이 컬럼을 상태 추적에 사용하시겠습니까?\n"
                msg += "(아니오를 선택하면 새 '처리상태' 컬럼이 생성됩니다)"
                
                reply = QMessageBox.question(
                    self, 
                    "상태 컬럼 확인",
                    msg,
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                use_existing = (reply == QMessageBox.Yes)
                self.excel_manager.confirm_status_column_usage(use_existing)
            
            excel_data = self.excel_manager._current_data
            if excel_data:
                self.data_table.load_excel_data(excel_data)
                self.status_bar.set_total_rows(excel_data.row_count)
                
    def toggle_mapping_panel(self):
        """Toggle mapping panel visibility"""
        self.side_panel.toggle()
        
    def on_mapping_complete(self, sheet_name: str, mappings: list):
        """Handle mapping completion"""
        try:
            # Apply mappings
            for mapping in mappings:
                self.excel_manager.set_column_mapping(
                    mapping.excel_column,
                    mapping.variable_name,
                    mapping.data_type,
                    mapping.is_required
                )
            
            # Emit signal that data is ready
            if self.excel_manager._current_data:
                self.dataReady.emit(self.excel_manager._current_data)
                
                # Request tab switch to editor
                self.tabSwitchRequested.emit(1)  # Editor tab index
                
                # Show success message
                QMessageBox.information(
                    self,
                    "매핑 완료",
                    "열 매핑이 완료되었습니다.\n에디터 탭으로 이동하여 매크로를 구성하세요."
                )
            
            self.logger.info(f"Applied {len(mappings)} column mappings")
            
        except Exception as e:
            QMessageBox.critical(self, "매핑 오류", f"매핑 적용 중 오류가 발생했습니다:\n{str(e)}")
            self.logger.error(f"Failed to apply mappings: {e}")
            
    def on_row_selected(self, row_index: int):
        """Handle row selection in preview"""
        self.logger.debug(f"Row {row_index} selected")
        
    def execute_macro(self):
        """Execute macro on Excel data"""
        # TODO: Implement macro execution
        self.status_bar.set_running(True)
        self.logger.info("Starting macro execution")
        
    def pause_execution(self):
        """Pause macro execution"""
        # TODO: Implement pause
        self.logger.info("Pausing macro execution")
        
    def stop_execution(self):
        """Stop macro execution"""
        # TODO: Implement stop
        self.status_bar.set_running(False)
        self.logger.info("Stopping macro execution")
        
    def get_excel_manager(self) -> ExcelManager:
        """Get Excel manager instance"""
        return self.excel_manager
        
    def has_data(self) -> bool:
        """Check if Excel data is loaded"""
        return hasattr(self.excel_manager, '_current_data') and self.excel_manager._current_data is not None
        
    def save_current_file(self):
        """Save current Excel file with updates"""
        if self.excel_manager._current_data:
            try:
                save_path = self.excel_manager.save_file()
                QMessageBox.information(self, "저장 완료", f"파일이 저장되었습니다:\n{save_path}")
                self.logger.info(f"Saved Excel file: {save_path}")
            except Exception as e:
                QMessageBox.critical(self, "저장 오류", f"파일 저장 중 오류가 발생했습니다:\n{str(e)}")
                self.logger.error(f"Failed to save Excel file: {e}")
                
    def reset_all_status(self):
        """Reset all rows to pending status"""
        self.logger.info("Reset all status button clicked")
        
        if not self.excel_manager._current_data:
            self.logger.warning("No Excel data loaded")
            QMessageBox.warning(self, "경고", "Excel 파일이 로드되지 않았습니다.")
            return
            
        # Get total row count
        total_rows = self.excel_manager._current_data.row_count
        status_column = self.excel_manager._current_data.get_status_column()
        
        self.logger.info(f"Total rows: {total_rows}, Status column: {status_column}")
        self.logger.info(f"Available columns: {self.excel_manager._current_data.columns}")
        
        if not status_column:
            self.logger.error("No status column found, creating one...")
            # Force creation of status column
            self.excel_manager._current_data.set_status_column('매크로_상태')
            status_column = self.excel_manager._current_data.get_status_column()
            self.logger.info(f"Created status column: {status_column}")
        
        # Confirm dialog
        reply = QMessageBox.question(
            self,
            "상태 초기화 확인",
            f"정말로 모든 {total_rows}개 행의 상태를 미완료로 변경하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.excel_manager.reset_all_status(save_immediately=True)
                # Refresh the data table
                self.data_table.load_excel_data(self.excel_manager._current_data)
                # Also refresh the sheet display
                if self.excel_manager._current_data:
                    self.on_sheet_changed(self.excel_manager._current_data.sheet_name)
                QMessageBox.information(self, "완료", "모든 행의 상태가 미완료로 변경되었습니다.")
                self.logger.info(f"Reset all {total_rows} rows to pending status")
            except Exception as e:
                self.logger.error(f"Failed to reset status: {e}")
                QMessageBox.critical(self, "오류", f"상태 변경 중 오류가 발생했습니다:\n{str(e)}")
                
    def complete_all_status(self):
        """Mark all rows as completed"""
        if not self.excel_manager._current_data:
            QMessageBox.warning(self, "경고", "Excel 파일이 로드되지 않았습니다.")
            return
            
        # Get total row count
        total_rows = self.excel_manager._current_data.row_count
        
        # Confirm dialog
        reply = QMessageBox.question(
            self,
            "상태 변경 확인",
            f"정말로 모든 {total_rows}개 행의 상태를 완료로 변경하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.excel_manager.complete_all_status(save_immediately=True)
                # Refresh the data table
                self.data_table.load_excel_data(self.excel_manager._current_data)
                QMessageBox.information(self, "완료", "모든 행의 상태가 완료로 변경되었습니다.")
                self.logger.info(f"Marked all {total_rows} rows as completed")
            except Exception as e:
                self.logger.error(f"Failed to complete status: {e}")
                QMessageBox.critical(self, "오류", f"상태 변경 중 오류가 발생했습니다:\n{str(e)}")
                
    def on_status_changed(self, row_index: int, new_status: str):
        """Handle individual status change from data table"""
        if not self.excel_manager._current_data:
            return
            
        try:
            # Update the Excel manager with the new status
            self.excel_manager.update_row_status(row_index, new_status)
            
            # Save immediately to persist the change
            self.excel_manager.save_file()
            
            self.logger.info(f"Updated row {row_index} status to: {new_status}")
        except Exception as e:
            self.logger.error(f"Failed to update row status: {e}")
            QMessageBox.critical(self, "오류", f"상태 업데이트 중 오류가 발생했습니다:\n{str(e)}")