"""
Excel data models and types
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum
import pandas as pd

# Status values for macro execution
class MacroStatus:
    """Constants for macro execution status"""
    PENDING = ""          # Not processed (empty string)
    PROCESSING = "처리중"  # Currently processing
    COMPLETED = "완료"     # Successfully completed
    ERROR = "오류"        # Error occurred

class ColumnType(Enum):
    """Excel column data types"""
    TEXT = "text"
    NUMBER = "number"
    DATE = "date"
    BOOLEAN = "boolean"
    MIXED = "mixed"
    EMPTY = "empty"

@dataclass
class ColumnInfo:
    """Information about an Excel column"""
    name: str
    index: int
    data_type: ColumnType
    sample_values: List[Any]
    null_count: int
    unique_count: int

@dataclass
class SheetInfo:
    """Information about an Excel sheet"""
    name: str
    row_count: int
    column_count: int
    columns: List[ColumnInfo]

@dataclass
class ExcelFileInfo:
    """Information about an Excel file"""
    file_path: str
    file_size: int
    sheet_count: int
    sheets: List[SheetInfo]
    
@dataclass
class ColumnMapping:
    """Maps Excel columns to macro variables"""
    excel_column: str
    variable_name: str
    data_type: ColumnType
    is_required: bool = True
    default_value: Any = None

class ExcelData:
    """Container for Excel data with metadata"""
    
    def __init__(self, dataframe: pd.DataFrame, sheet_name: str, file_path: str):
        self.dataframe = dataframe
        self.sheet_name = sheet_name
        self.file_path = file_path
        # Set default status column to 매크로_상태 if it exists
        if "매크로_상태" in dataframe.columns:
            self._status_column = "매크로_상태"
        else:
            self._status_column = None
        
    @property
    def row_count(self) -> int:
        return len(self.dataframe)
    
    @property
    def column_count(self) -> int:
        return len(self.dataframe.columns)
    
    @property
    def columns(self) -> List[str]:
        return self.dataframe.columns.tolist()
    
    def get_status_column(self) -> Optional[str]:
        """Get the status column name"""
        return self._status_column
    
    def set_status_column(self, column_name: str):
        """Set the status column"""
        if column_name not in self.columns:
            self.dataframe[column_name] = ""
        self._status_column = column_name
    
    def update_row_status(self, row_index: int, status: str):
        """Update status for a specific row"""
        if self._status_column:
            self.dataframe.at[row_index, self._status_column] = status
    
    def get_incomplete_rows(self) -> pd.DataFrame:
        """Get rows that haven't been completed"""
        if not self._status_column:
            return self.dataframe
        
        return self.dataframe[
            (self.dataframe[self._status_column] != "완료") & 
            (self.dataframe[self._status_column] != "Completed")
        ]
    
    def get_row_data(self, row_index: int) -> Dict[str, Any]:
        """Get data for a specific row as dictionary"""
        return self.dataframe.iloc[row_index].to_dict()