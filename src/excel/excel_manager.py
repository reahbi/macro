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
        
        # Check for status column
        status_columns = ['상태', 'Status', '완료여부', '처리상태', 'status', 'STATUS']
        for col in status_columns:
            if col in df.columns:
                excel_data.set_status_column(col)
                break
        
        # If no status column found, create one
        if not excel_data.get_status_column():
            excel_data.set_status_column('처리상태')
            self.logger.info("Created new status column: 처리상태")
        
        self._current_data = excel_data
        return excel_data
    
    def save_file(self, file_path: Optional[str] = None) -> str:
        """Save current data back to Excel"""
        if not self._current_data:
            # Excel 데이터가 없으면 저장하지 않음 (standalone 모드)
            self.logger.info("No Excel data to save - skipping save operation")
            return ""
        
        save_path = file_path or self._current_file
        
        # Read all sheets to preserve
        with pd.ExcelFile(self._current_file) as xls:
            sheets = {}
            for sheet_name in xls.sheet_names:
                if sheet_name == self._current_data.sheet_name:
                    sheets[sheet_name] = self._current_data.dataframe
                else:
                    sheets[sheet_name] = pd.read_excel(xls, sheet_name)
        
        # Save all sheets
        with pd.ExcelWriter(save_path, engine='openpyxl') as writer:
            for sheet_name, df in sheets.items():
                df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        self.logger.info(f"Saved Excel file: {save_path}")
        return save_path
    
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
        
        self._current_data.update_row_status(row_index, status)
        
        if save_immediately:
            self.save_file()
    
    def get_pending_rows(self) -> List[int]:
        """Get list of row indices that need processing"""
        if not self._current_data:
            return []
        
        incomplete = self._current_data.get_incomplete_rows()
        return incomplete.index.tolist()