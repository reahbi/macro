"""
Main Excel integration widget
"""

from typing import Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QSplitter, QMessageBox,
    QProgressDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread
from ui.widgets.file_selector import FileSelectorWidget
from ui.widgets.sheet_mapper import SheetMapperWidget
from ui.widgets.data_preview import DataPreviewWidget
from excel.excel_manager import ExcelManager
from excel.models import ExcelFileInfo, ColumnMapping
from logger.app_logger import get_logger

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

class ExcelWidget(QWidget):
    """Main Excel integration widget"""
    
    dataReady = pyqtSignal(object)  # ExcelData
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger(__name__)
        self.excel_manager = ExcelManager()
        self.current_file_info: Optional[ExcelFileInfo] = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Create splitter for resizable sections
        splitter = QSplitter(Qt.Vertical)
        
        # File selector
        self.file_selector = FileSelectorWidget()
        self.file_selector.fileSelected.connect(self._on_file_selected)
        splitter.addWidget(self.file_selector)
        
        # Sheet mapper
        self.sheet_mapper = SheetMapperWidget()
        self.sheet_mapper.mappingComplete.connect(self._on_mapping_complete)
        splitter.addWidget(self.sheet_mapper)
        
        # Data preview
        self.data_preview = DataPreviewWidget()
        self.data_preview.rowSelected.connect(self._on_row_selected)
        splitter.addWidget(self.data_preview)
        
        # Set initial splitter sizes (30%, 30%, 40%)
        splitter.setSizes([300, 300, 400])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
        
    def _on_file_selected(self, file_path: str):
        """Handle file selection"""
        # Show progress dialog
        progress = QProgressDialog("엑셀 파일 로딩 중...", None, 0, 0, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.show()
        
        # Load file in thread
        self.load_thread = ExcelLoadThread(self.excel_manager, file_path)
        self.load_thread.fileLoaded.connect(lambda info: self._on_file_loaded(info, progress))
        self.load_thread.error.connect(lambda err: self._on_load_error(err, progress))
        self.load_thread.start()
        
    def _on_file_loaded(self, file_info: ExcelFileInfo, progress: QProgressDialog):
        """Handle successful file load"""
        progress.close()
        self.current_file_info = file_info
        self.sheet_mapper.set_file_info(file_info.sheets)
        self.logger.info(f"Loaded Excel file: {file_info.file_path}")
        
    def _on_load_error(self, error: str, progress: QProgressDialog):
        """Handle file load error"""
        progress.close()
        QMessageBox.critical(self, "파일 로드 오류", f"엑셀 파일을 불러올 수 없습니다:\n{error}")
        self.logger.error(f"Failed to load Excel file: {error}")
        
    def _on_mapping_complete(self, sheet_name: str, mappings: list):
        """Handle mapping completion"""
        try:
            # Read sheet data
            excel_data = self.excel_manager.read_sheet(sheet_name)
            
            # Apply mappings
            for mapping in mappings:
                self.excel_manager.set_column_mapping(
                    mapping.excel_column,
                    mapping.variable_name,
                    mapping.data_type,
                    mapping.is_required
                )
            
            # Load data in preview
            self.data_preview.load_excel_data(excel_data)
            
            # Emit signal that data is ready
            self.dataReady.emit(excel_data)
            
            self.logger.info(f"Loaded sheet '{sheet_name}' with {len(mappings)} mappings")
            
        except Exception as e:
            QMessageBox.critical(self, "데이터 로드 오류", f"시트 데이터를 불러올 수 없습니다:\n{str(e)}")
            self.logger.error(f"Failed to load sheet data: {e}")
            
    def _on_row_selected(self, row_index: int):
        """Handle row selection in preview"""
        self.logger.debug(f"Row {row_index} selected for execution")
        
    def get_excel_manager(self) -> ExcelManager:
        """Get Excel manager instance"""
        return self.excel_manager
        
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
                
    def set_compact_mode(self, is_compact: bool):
        """Apply compact mode to the Excel widget"""
        # Find the splitter
        splitter = self.findChild(QSplitter)
        
        if is_compact:
            # Reduce splitter sizes and spacing
            if splitter:
                splitter.setSizes([200, 200, 300])
                
            # Apply compact mode to child widgets
            if hasattr(self.file_selector, 'set_compact_mode'):
                self.file_selector.set_compact_mode(is_compact)
            if hasattr(self.sheet_mapper, 'set_compact_mode'):
                self.sheet_mapper.set_compact_mode(is_compact)
            if hasattr(self.data_preview, 'set_compact_mode'):
                self.data_preview.set_compact_mode(is_compact)
                
            # Reduce layout margins
            self.layout().setContentsMargins(5, 5, 5, 5)
            self.layout().setSpacing(5)
        else:
            # Reset to normal sizes
            if splitter:
                splitter.setSizes([300, 300, 400])
                
            # Reset child widgets
            if hasattr(self.file_selector, 'set_compact_mode'):
                self.file_selector.set_compact_mode(is_compact)
            if hasattr(self.sheet_mapper, 'set_compact_mode'):
                self.sheet_mapper.set_compact_mode(is_compact)
            if hasattr(self.data_preview, 'set_compact_mode'):
                self.data_preview.set_compact_mode(is_compact)
                
            # Reset layout margins
            self.layout().setContentsMargins(9, 9, 9, 9)
            self.layout().setSpacing(6)