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
    PENDING = "미완료"      # Not processed
    PROCESSING = "처리중"  # Currently processing
    COMPLETED = "완료"     # Successfully completed
    ERROR = "오류"        # Error occurred
    
    # Status value mappings for normalization
    COMPLETED_VALUES = {"완료", "Completed", "Complete", "Done", "Y", "O", "1", "TRUE", "True", "true", "○", "●"}
    PENDING_VALUES = {"미완료", "Pending", "N", "X", "0", "FALSE", "False", "false", "", None, "×"}
    ERROR_VALUES = {"오류", "Error", "Failed", "실패", "E"}

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
            # Initialize new status column with PENDING status
            self.dataframe[column_name] = MacroStatus.PENDING
        else:
            # Normalize existing status values
            self._normalize_status_values(column_name)
        self._status_column = column_name
        
    def _normalize_status_values(self, column_name: str):
        """Normalize existing status column values"""
        import numpy as np
        
        # Handle different data types safely
        try:
            # Create a copy to avoid modifying original if error occurs
            col_copy = self.dataframe[column_name].copy()
            
            # Convert to string type, handling various data types
            if col_copy.dtype == np.dtype('object'):
                # Already object type, just convert to string
                col_copy = col_copy.astype(str)
            elif np.issubdtype(col_copy.dtype, np.number):
                # Numeric type - convert to string
                col_copy = col_copy.astype(str)
            elif np.issubdtype(col_copy.dtype, np.datetime64):
                # Datetime type - convert to string
                col_copy = col_copy.dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                # Other types - try generic conversion
                col_copy = col_copy.astype(str)
                
        except Exception as e:
            # If conversion fails, initialize column with PENDING
            import logging
            logging.warning(f"Failed to convert status column '{column_name}' to string: {e}")
            self.dataframe[column_name] = MacroStatus.PENDING
            return
        
        # Apply normalization
        def normalize_value(val):
            val_str = str(val).strip() if val is not None else ""
            
            # Check for completed values
            if val_str in MacroStatus.COMPLETED_VALUES:
                return MacroStatus.COMPLETED
            # Check for error values
            elif val_str in MacroStatus.ERROR_VALUES:
                return MacroStatus.ERROR
            # Check for pending values (including empty)
            elif val_str in MacroStatus.PENDING_VALUES or val_str == "nan" or val_str == "":
                return MacroStatus.PENDING
            # Keep original value if not recognized
            else:
                return val_str
                
        self.dataframe[column_name] = col_copy.apply(normalize_value)
    
    def update_row_status(self, row_index: int, status: str):
        """Update status for a specific row"""
        import logging
        logger = logging.getLogger(__name__)
        
        if self._status_column:
            # Log current value before update
            current_value = self.dataframe.at[row_index, self._status_column]
            logger.debug(f"Updating row {row_index} status: '{current_value}' -> '{status}' in column '{self._status_column}'")
            
            # Update the status
            self.dataframe.at[row_index, self._status_column] = status
            
            # Verify the update
            new_value = self.dataframe.at[row_index, self._status_column]
            logger.debug(f"Row {row_index} status after update: '{new_value}'")
            
            if new_value != status:
                logger.error(f"Status update failed! Expected '{status}' but got '{new_value}'")
        else:
            logger.warning(f"Cannot update row {row_index} status - no status column configured")
    
    def get_incomplete_rows(self) -> pd.DataFrame:
        """Get rows that haven't been completed"""
        if not self._status_column:
            return self.dataframe
        
        # Include rows with PENDING status or empty status
        return self.dataframe[
            (self.dataframe[self._status_column] != MacroStatus.COMPLETED) & 
            (self.dataframe[self._status_column] != "Completed") &
            (self.dataframe[self._status_column] != "Complete") &
            (self.dataframe[self._status_column] != "Done")
        ]
    
    def get_row_data(self, row_index: int) -> Dict[str, Any]:
        """Get data for a specific row as dictionary"""
        return self.dataframe.iloc[row_index].to_dict()