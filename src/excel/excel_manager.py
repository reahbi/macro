"""
Core Excel file management functionality
"""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple
import pandas as pd
import openpyxl
from logger.app_logger import get_logger
from excel.models import (
    ExcelFileInfo, SheetInfo, ColumnInfo, ColumnType, 
    ExcelData, ColumnMapping
)

class ExcelManager:
    """Manages Excel file operations"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self._current_file: Optional[str] = None
        self._current_data: Optional[ExcelData] = None
        self._column_mappings: Dict[str, ColumnMapping] = {}
        self.df: Optional[pd.DataFrame] = None  # For direct DataFrame access
        self.mappings: Dict[str, str] = {}  # For simple column mappings
    
    @property
    def file_path(self) -> Optional[str]:
        """Get current file path"""
        return self._current_file
        
    def load_file(self, file_path: str) -> ExcelFileInfo:
        """Load Excel file and return file information"""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Excel file not found: {file_path}")
        
        if not file_path.suffix.lower() in ['.xlsx', '.xls', '.xlsm']:
            raise ValueError(f"Invalid Excel file format: {file_path.suffix}")
        
        self.logger.info(f"Loading Excel file: {file_path}")
        
        # Get file info
        file_size = file_path.stat().st_size
        
        # Load workbook to get sheet names
        workbook = openpyxl.load_workbook(file_path, read_only=True, data_only=True)
        sheet_names = workbook.sheetnames
        workbook.close()
        
        # Analyze each sheet
        sheets = []
        for sheet_name in sheet_names:
            sheet_info = self._analyze_sheet(file_path, sheet_name)
            sheets.append(sheet_info)
        
        self._current_file = str(file_path)
        
        # Load first sheet into df for simple access
        if sheet_names:
            self.df = pd.read_excel(file_path, sheet_name=sheet_names[0])
        
        return ExcelFileInfo(
            file_path=str(file_path),
            file_size=file_size,
            sheet_count=len(sheets),
            sheets=sheets
        )
    
    def _analyze_sheet(self, file_path: Path, sheet_name: str) -> SheetInfo:
        """Analyze a specific sheet"""
        # Read first 1000 rows for analysis
        df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=1000)
        
        # Get full row count
        full_df = pd.read_excel(file_path, sheet_name=sheet_name, usecols=[0])
        row_count = len(full_df)
        
        # Analyze columns
        columns = []
        for idx, col in enumerate(df.columns):
            col_info = self._analyze_column(df[col], col, idx)
            columns.append(col_info)
        
        return SheetInfo(
            name=sheet_name,
            row_count=row_count,
            column_count=len(columns),
            columns=columns
        )
    
    def _analyze_column(self, series: pd.Series, name: str, index: int) -> ColumnInfo:
        """Analyze a single column"""
        # Get non-null values
        non_null = series.dropna()
        
        # Determine data type
        data_type = self._detect_column_type(non_null)
        
        # Get sample values
        sample_values = non_null.head(5).tolist()
        
        return ColumnInfo(
            name=str(name),
            index=index,
            data_type=data_type,
            sample_values=sample_values,
            null_count=series.isnull().sum(),
            unique_count=series.nunique()
        )
    
    def _detect_column_type(self, series: pd.Series) -> ColumnType:
        """Detect column data type"""
        if len(series) == 0:
            return ColumnType.EMPTY
        
        # Try to infer type
        try:
            pd.to_numeric(series)
            return ColumnType.NUMBER
        except (ValueError, TypeError):
            pass
        
        try:
            # Suppress warning for mixed date formats
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings('ignore', message='Could not infer format')
                pd.to_datetime(series, errors='coerce')
            return ColumnType.DATE
        except (ValueError, TypeError, AttributeError):
            pass
        
        # Check for boolean
        unique_values = series.unique()
        if len(unique_values) <= 2:
            bool_values = {True, False, 'True', 'False', 'true', 'false', 
                          'TRUE', 'FALSE', '예', '아니오', 'Yes', 'No'}
            if all(val in bool_values for val in unique_values):
                return ColumnType.BOOLEAN
        
        return ColumnType.TEXT
    
    def read_sheet(self, sheet_name: str, max_rows: Optional[int] = None) -> ExcelData:
        """Read data from a specific sheet"""
        if not self._current_file:
            raise ValueError("No Excel file loaded")
        
        self.logger.info(f"Reading sheet: {sheet_name}")
        
        # Read data
        df = pd.read_excel(self._current_file, sheet_name=sheet_name, nrows=max_rows)
        
        # Create ExcelData instance
        excel_data = ExcelData(df, sheet_name, self._current_file)
        
        # Check for status column - prioritize 매크로_상태
        status_columns = ['매크로_상태', '상태', 'Status', '완료여부', '처리상태', 'status', 'STATUS']
        found_status_column = None
        for col in status_columns:
            if col in df.columns:
                found_status_column = col
                break
        
        if found_status_column:
            # Analyze existing status values
            unique_values = df[found_status_column].unique()
            non_empty_values = [str(v) for v in unique_values if pd.notna(v) and str(v).strip()]
            
            self.logger.info(f"Found existing status column '{found_status_column}' with values: {non_empty_values}")
            
            # Check if we need user confirmation
            if non_empty_values and len(non_empty_values) > 0:
                # Store info for later dialog (to avoid circular imports)
                self._pending_status_column = found_status_column
                self._existing_status_values = non_empty_values
            else:
                # Empty column, just use it
                excel_data.set_status_column(found_status_column)
                self.logger.info(f"Using existing empty status column: {found_status_column}")
        else:
            # If no status column found, create one
            excel_data.set_status_column('매크로_상태')
            self.logger.info("Created new status column: 매크로_상태")
        
        self._current_data = excel_data
        return excel_data
        
    def confirm_status_column_usage(self, use_existing: bool):
        """Confirm whether to use existing status column"""
        if hasattr(self, '_pending_status_column') and self._current_data:
            if use_existing:
                self._current_data.set_status_column(self._pending_status_column)
                self.logger.info(f"Using existing status column: {self._pending_status_column}")
            else:
                # Create new column
                self._current_data.set_status_column('매크로_상태')
                self.logger.info("Created new status column: 매크로_상태")
            
            # Clean up
            delattr(self, '_pending_status_column')
            if hasattr(self, '_existing_status_values'):
                delattr(self, '_existing_status_values')
                
    def has_pending_status_column(self) -> bool:
        """Check if there's a pending status column decision"""
        return hasattr(self, '_pending_status_column')
        
    def get_pending_status_info(self) -> tuple:
        """Get pending status column info"""
        if hasattr(self, '_pending_status_column'):
            return self._pending_status_column, getattr(self, '_existing_status_values', [])
        return None, []
    
    def reload_current_file(self) -> None:
        """Reload current file from disk to get latest changes"""
        if not self._current_file or not self._current_data:
            raise ValueError("No file currently loaded")
            
        self.logger.info(f"Reloading Excel file: {self._current_file}")
        
        # Get current sheet name
        current_sheet = self._current_data.sheet_name
        
        # Read fresh data from file
        df = pd.read_excel(self._current_file, sheet_name=current_sheet)
        
        # Update current data with fresh DataFrame
        self._current_data.dataframe = df
        # row_count is a computed property, no need to set it explicitly
        
        self.logger.info(f"Reloaded {len(df)} rows from sheet '{current_sheet}'")
        
    def save_file(self, file_path: Optional[str] = None) -> str:
        """Save current data back to Excel"""
        if not self._current_data:
            # Excel 데이터가 없으면 저장하지 않음 (standalone 모드)
            self.logger.info("No Excel data to save - skipping save operation")
            return ""
        
        save_path = file_path or self._current_file
        
        # Check if file is accessible
        try:
            with open(save_path, 'a'):
                pass
        except IOError:
            self.logger.error(f"Cannot access file '{save_path}' - it may be open in another application!")
            return ""
        
        # Check if file is locked
        try:
            # Try to open file exclusively to check if it's locked
            with open(save_path, 'r+b') as f:
                pass
        except (IOError, OSError) as e:
            self.logger.error(f"Excel file may be locked by another process: {e}")
            # Continue anyway as openpyxl might handle it differently
        
        # Get file modification time before save
        import os
        import time
        mod_time_before = os.path.getmtime(save_path) if os.path.exists(save_path) else 0
        self.logger.info(f"File modification time before save: {time.ctime(mod_time_before)}")
        
        # Log current status column values before saving
        if self._current_data._status_column:
            status_values = self._current_data.dataframe[self._current_data._status_column].value_counts()
            self.logger.info(f"Status column '{self._current_data._status_column}' values before save: {status_values.to_dict()}")
        
        # Read all sheets to preserve
        with pd.ExcelFile(self._current_file) as xls:
            sheets = {}
            for sheet_name in xls.sheet_names:
                if sheet_name == self._current_data.sheet_name:
                    sheets[sheet_name] = self._current_data.dataframe
                    self.logger.debug(f"Using updated dataframe for sheet '{sheet_name}'")
                else:
                    sheets[sheet_name] = pd.read_excel(xls, sheet_name)
        
        # Save all sheets
        try:
            with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
                for sheet_name, df in sheets.items():
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    self.logger.debug(f"Written sheet '{sheet_name}' with {len(df)} rows")
            
            # Verify file was actually saved
            import time
            mod_time_after = os.path.getmtime(save_path)
            self.logger.info(f"File modification time after save: {time.ctime(mod_time_after)}")
            
            if mod_time_after <= mod_time_before:
                self.logger.warning("File modification time did not change after save!")
            
            # Log status column values after saving
            if self._current_data._status_column:
                status_values = self._current_data.dataframe[self._current_data._status_column].value_counts()
                self.logger.info(f"Status column '{self._current_data._status_column}' values after save: {status_values.to_dict()}")
            
            self.logger.info(f"Saved Excel file successfully: {save_path}")
            return save_path
        except Exception as e:
            self.logger.error(f"Failed to save Excel file: {e}", exc_info=True)
            raise
    
    def set_column_mapping(self, excel_column: str, variable_name: str, 
                          data_type: ColumnType, is_required: bool = True):
        """Set mapping between Excel column and variable"""
        mapping = ColumnMapping(
            excel_column=excel_column,
            variable_name=variable_name,
            data_type=data_type,
            is_required=is_required
        )
        self._column_mappings[variable_name] = mapping
    
    def get_mapped_data(self, row_index: int) -> Dict[str, Any]:
        """Get row data with variable mappings applied"""
        if not self._current_data:
            raise ValueError("No data loaded")
        
        row_data = self._current_data.get_row_data(row_index)
        mapped_data = {}
        
        for var_name, mapping in self._column_mappings.items():
            if mapping.excel_column in row_data:
                mapped_data[var_name] = row_data[mapping.excel_column]
            elif mapping.default_value is not None:
                mapped_data[var_name] = mapping.default_value
            elif mapping.is_required:
                raise ValueError(f"Required column '{mapping.excel_column}' not found")
        
        return mapped_data
    
    def update_row_status(self, row_index: int, status: str, save_immediately: bool = False):
        """Update status for a specific row"""
        if not self._current_data:
            raise ValueError("No data loaded")
        
        self.logger.info(f"ExcelManager.update_row_status called - row: {row_index}, status: '{status}', save_immediately: {save_immediately}")
        
        # Check if status column is configured
        if not self._current_data._status_column:
            self.logger.error(f"Status column not configured! Cannot update row {row_index}")
            return
            
        self._current_data.update_row_status(row_index, status)
        
        if save_immediately:
            self.logger.info(f"Saving file immediately after status update for row {row_index}")
            self.save_file()
    
    def update_all_rows_status(self, status: str, save_immediately: bool = False):
        """Update status for all rows"""
        if not self._current_data:
            raise ValueError("No data loaded")
        
        if self._current_data._status_column:
            self._current_data.dataframe[self._current_data._status_column] = status
        
        if save_immediately:
            self.save_file()
            
    def reset_all_status(self, save_immediately: bool = False):
        """Reset all rows to pending status"""
        from .models import MacroStatus
        if not self._current_data:
            raise ValueError("No data loaded")
            
        # Ensure status column exists
        if not self._current_data._status_column:
            self._current_data.set_status_column('매크로_상태')
            self.logger.info("Created status column: 매크로_상태")
            
        self.update_all_rows_status(MacroStatus.PENDING, save_immediately)
        
    def complete_all_status(self, save_immediately: bool = False):
        """Mark all rows as completed"""
        from .models import MacroStatus
        if not self._current_data:
            raise ValueError("No data loaded")
            
        # Ensure status column exists
        if not self._current_data._status_column:
            self._current_data.set_status_column('매크로_상태')
            self.logger.info("Created status column: 매크로_상태")
            
        self.update_all_rows_status(MacroStatus.COMPLETED, save_immediately)
    
    def get_pending_rows(self) -> List[int]:
        """Get list of row indices that need processing"""
        if not self._current_data:
            return []
        
        incomplete = self._current_data.get_incomplete_rows()
        return incomplete.index.tolist()
    
    def has_data(self) -> bool:
        """데이터가 로드되었는지 확인"""
        return self.df is not None and not self.df.empty
    
    def get_total_rows(self) -> int:
        """전체 행 수 반환"""
        return len(self.df) if self.df is not None else 0
    
    def get_headers(self) -> List[str]:
        """컬럼 헤더 목록 반환"""
        return list(self.df.columns) if self.df is not None else []
    
    def get_row_data(self, row_index: int) -> Dict[str, Any]:
        """특정 행의 데이터 반환"""
        if not self.has_data() or row_index >= self.get_total_rows():
            self.logger.warning(f"Invalid row index {row_index} or no data loaded")
            return {}
        
        # Use _current_data if available (new style)
        if self._current_data:
            row_data = self._current_data.get_row_data(row_index)
            self.logger.debug(f"Retrieved row {row_index} data: {list(row_data.keys())}")
            return row_data
        
        # Fallback to direct dataframe access (old style)
        row_data = self.df.iloc[row_index].to_dict()
        self.logger.debug(f"Retrieved row {row_index} data (legacy): {list(row_data.keys())}")
        return row_data
    
    def add_mapping(self, variable: str, column: str):
        """변수와 컬럼 매핑 추가"""
        self.mappings[variable] = column
    
    def set_active_sheet(self, sheet_name: str):
        """Set the active sheet for operations"""
        if not self._current_file:
            raise ValueError("No Excel file loaded")
        
        # Check if we already have this sheet loaded
        if self._current_data and self._current_data.sheet_name == sheet_name:
            self.logger.info(f"Sheet '{sheet_name}' is already active, skipping reload")
            return
        
        self.logger.info(f"Setting active sheet to: {sheet_name} (will reload data)")
        
        # Read the sheet data (this creates _current_data with status column)
        self.read_sheet(sheet_name)
        
        # Update the df property from _current_data, not re-reading from file
        if self._current_data:
            self.df = self._current_data.dataframe
            # Ensure status column exists
            if not self._current_data.get_status_column():
                self._current_data.set_status_column('매크로_상태')
                self.logger.info("Created default status column: 매크로_상태")
        else:
            # Fallback if _current_data is not set
            self.df = pd.read_excel(self._current_file, sheet_name=sheet_name)
            
        self.logger.info(f"Active sheet set to: {sheet_name} with {len(self.df.columns)} columns")
    
    def get_sheet_data(self) -> Optional[pd.DataFrame]:
        """Get the current sheet data as DataFrame"""
        if self._current_data:
            return self._current_data.dataframe
        return self.df