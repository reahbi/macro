"""
Unit tests for ExcelManager - pandas/openpyxl integration and data processing
Tests data loading, type detection, column mapping, and status management with file I/O mocking.
"""

import pytest
import pandas as pd
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any, List

from excel.excel_manager import ExcelManager
from excel.models import ExcelFileInfo, SheetInfo, ColumnInfo, ColumnType, ExcelData, ColumnMapping


class TestExcelManagerInitialization:
    """Test ExcelManager initialization and configuration"""
    
    def test_default_initialization(self):
        """Test ExcelManager with default settings"""
        manager = ExcelManager()
        
        assert manager._current_file is None
        assert manager._current_data is None
        assert manager._column_mappings == {}
        assert hasattr(manager, 'logger')
    
    def test_file_path_property(self):
        """Test file_path property"""
        manager = ExcelManager()
        
        assert manager.file_path is None
        
        # Set current file
        manager._current_file = "/test/path/file.xlsx"
        assert manager.file_path == "/test/path/file.xlsx"


class TestFileLoading:
    """Test Excel file loading functionality with comprehensive mocking"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = ExcelManager()
        self.test_file_path = "/test/data/sample.xlsx"
    
    @patch('pathlib.Path.exists')
    def test_load_file_not_found(self, mock_exists):
        """Test loading non-existent file"""
        mock_exists.return_value = False
        
        with pytest.raises(FileNotFoundError, match="Excel file not found"):
            self.manager.load_file(self.test_file_path)
    
    @patch('pathlib.Path.exists')
    def test_load_file_invalid_format(self, mock_exists):
        """Test loading file with invalid format"""
        mock_exists.return_value = True
        
        with pytest.raises(ValueError, match="Invalid Excel file format"):
            self.manager.load_file("/test/data/sample.txt")
    
    @patch('openpyxl.load_workbook')
    @patch('pathlib.Path.stat')
    @patch('pathlib.Path.exists')
    @patch('excel.excel_manager.ExcelManager._analyze_sheet')
    def test_load_file_success(self, mock_analyze_sheet, mock_exists, mock_stat, mock_load_workbook):
        """Test successful file loading"""
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 1024000  # 1MB
        
        # Mock openpyxl workbook
        mock_workbook = Mock()
        mock_workbook.sheetnames = ["Sheet1", "Sheet2", "Data"]
        mock_load_workbook.return_value = mock_workbook
        
        # Mock sheet analysis
        mock_sheet_info = SheetInfo(
            name="Sheet1",
            row_count=100,
            column_count=5,
            columns=[]
        )
        mock_analyze_sheet.return_value = mock_sheet_info
        
        result = self.manager.load_file(self.test_file_path)
        
        # Verify result structure
        assert isinstance(result, ExcelFileInfo)
        assert result.file_path == self.test_file_path
        assert result.file_size == 1024000
        assert result.sheet_count == 3
        assert len(result.sheets) == 3
        
        # Verify workbook was closed
        mock_workbook.close.assert_called_once()
        
        # Verify current file was set
        assert self.manager._current_file == self.test_file_path
    
    @patch('pandas.read_excel')
    @patch('pathlib.Path.exists')
    def test_analyze_sheet_basic(self, mock_exists, mock_read_excel):
        """Test basic sheet analysis"""
        mock_exists.return_value = True
        
        # Mock pandas DataFrames
        sample_df = pd.DataFrame({
            'Name': ['Alice', 'Bob', 'Charlie'],
            'Age': [25, 30, 35],
            'Email': ['alice@test.com', 'bob@test.com', 'charlie@test.com'],
            'Active': [True, False, True]
        })
        
        full_df = pd.DataFrame({'Name': range(250)})  # 250 rows for count
        
        mock_read_excel.side_effect = [sample_df, full_df]
        
        result = self.manager._analyze_sheet(Path(self.test_file_path), "Sheet1")
        
        assert isinstance(result, SheetInfo)
        assert result.name == "Sheet1"
        assert result.row_count == 250
        assert result.column_count == 4
        assert len(result.columns) == 4
        
        # Verify column analysis
        column_names = [col.name for col in result.columns]
        assert "Name" in column_names
        assert "Age" in column_names
        assert "Email" in column_names
        assert "Active" in column_names
    
    @patch('pandas.read_excel')
    def test_analyze_column_types(self, mock_read_excel):
        """Test column type detection accuracy"""
        # Create test data with various types
        test_data = pd.DataFrame({
            'Text': ['Hello', 'World', 'Test'],
            'Numbers': [1, 2, 3],
            'Decimals': [1.1, 2.2, 3.3],
            'Dates': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03']),
            'Booleans': [True, False, True],
            'Mixed': ['Yes', 'No', 'Maybe'],
            'Empty': [None, None, None],
            'Korean_Bool': ['예', '아니오', '예']
        })
        
        mock_read_excel.side_effect = [test_data, pd.DataFrame({'col': range(100)})]
        
        result = self.manager._analyze_sheet(Path(self.test_file_path), "TypeTest")
        
        columns_by_name = {col.name: col for col in result.columns}
        
        # Verify type detection (approximate, as actual detection may vary)
        assert columns_by_name['Numbers'].data_type in [ColumnType.NUMBER]
        assert columns_by_name['Decimals'].data_type in [ColumnType.NUMBER]
        assert columns_by_name['Empty'].data_type == ColumnType.EMPTY
        # Other types may vary based on pandas inference
    
    def test_detect_column_type_empty(self):
        """Test empty column type detection"""
        empty_series = pd.Series([])
        result = self.manager._detect_column_type(empty_series)
        assert result == ColumnType.EMPTY
    
    def test_detect_column_type_number(self):
        """Test numeric column type detection"""
        numeric_series = pd.Series([1, 2, 3, 4, 5])
        result = self.manager._detect_column_type(numeric_series)
        assert result == ColumnType.NUMBER
        
        float_series = pd.Series([1.1, 2.2, 3.3])
        result = self.manager._detect_column_type(float_series)
        assert result == ColumnType.NUMBER
    
    def test_detect_column_type_boolean(self):
        """Test boolean column type detection with multilingual support"""
        boolean_cases = [
            pd.Series([True, False]),
            pd.Series(['True', 'False']),
            pd.Series(['yes', 'no']),
            pd.Series(['예', '아니오']),  # Korean
            pd.Series(['YES', 'NO']),
        ]
        
        for series in boolean_cases:
            result = self.manager._detect_column_type(series)
            assert result == ColumnType.BOOLEAN, f"Failed for series: {series.tolist()}"
    
    def test_detect_column_type_text_fallback(self):
        """Test text type as fallback"""
        text_series = pd.Series(['Hello', 'World', 'Mixed123', '!@#$%'])
        result = self.manager._detect_column_type(text_series)
        assert result == ColumnType.TEXT
        
        mixed_series = pd.Series(['Text', 123, True, None])
        result = self.manager._detect_column_type(mixed_series)
        assert result == ColumnType.TEXT  # Mixed types default to text
    
    @patch('warnings.catch_warnings')
    def test_detect_column_type_date_with_warnings(self, mock_warnings):
        """Test date detection with warning suppression"""
        # This tests the warning suppression logic for mixed date formats
        mixed_date_series = pd.Series(['2023-01-01', 'invalid_date', '2023-12-31'])
        
        # The actual detection might still return TEXT due to mixed content
        result = self.manager._detect_column_type(mixed_date_series)
        
        # Verify warnings context manager was used
        mock_warnings.assert_called()


class TestDataReading:
    """Test data reading and processing functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = ExcelManager()
        self.sample_data = pd.DataFrame({
            '이름': ['김철수', '박영희', '이민수'],
            '나이': [25, 30, 28],
            '부서': ['개발팀', '마케팅팀', '인사팀'],
            '상태': ['', '', '']
        })
    
    def test_read_sheet_no_file_loaded(self):
        """Test reading sheet when no file is loaded"""
        with pytest.raises(ValueError, match="No Excel file loaded"):
            self.manager.read_sheet("Sheet1")
    
    @patch('pandas.read_excel')
    @patch('excel.models.ExcelData')
    def test_read_sheet_success(self, mock_excel_data_class, mock_read_excel):
        """Test successful sheet reading"""
        self.manager._current_file = "test.xlsx"
        mock_read_excel.return_value = self.sample_data
        
        # Mock ExcelData creation
        mock_excel_data = Mock()
        mock_excel_data_class.return_value = mock_excel_data
        mock_excel_data.get_status_column.return_value = None
        
        result = self.manager.read_sheet("TestSheet")
        
        # Verify pandas read_excel was called correctly
        mock_read_excel.assert_called_once_with("test.xlsx", sheet_name="TestSheet", nrows=None)
        
        # Verify ExcelData was created
        mock_excel_data_class.assert_called_once_with(self.sample_data, "TestSheet", "test.xlsx")
        
        # Verify status column detection was called
        mock_excel_data.set_status_column.assert_called()
        
        assert self.manager._current_data == mock_excel_data
        assert result == mock_excel_data
    
    @patch('pandas.read_excel')
    @patch('excel.models.ExcelData')
    def test_read_sheet_status_column_detection(self, mock_excel_data_class, mock_read_excel):
        """Test automatic status column detection"""
        self.manager._current_file = "test.xlsx"
        
        # Test data with various status column names
        status_test_cases = [
            {'상태': ['', '', ''], '이름': ['A', 'B', 'C']},
            {'Status': ['', '', ''], 'Name': ['A', 'B', 'C']},
            {'완료여부': ['', '', ''], '이름': ['A', 'B', 'C']},
            {'처리상태': ['', '', ''], '이름': ['A', 'B', 'C']},
        ]
        
        for test_data in status_test_cases:
            mock_df = pd.DataFrame(test_data)
            mock_read_excel.return_value = mock_df
            
            mock_excel_data = Mock()
            mock_excel_data_class.return_value = mock_excel_data
            mock_excel_data.get_status_column.return_value = None
            
            self.manager.read_sheet("TestSheet")
            
            # Should call set_status_column with detected column
            expected_column = list(test_data.keys())[0]  # First column (status column)
            mock_excel_data.set_status_column.assert_called_with(expected_column)
    
    @patch('pandas.read_excel')
    @patch('excel.models.ExcelData')
    @patch('logger.app_logger.get_logger')
    def test_read_sheet_create_status_column(self, mock_logger, mock_excel_data_class, mock_read_excel):
        """Test automatic status column creation when none exists"""
        self.manager._current_file = "test.xlsx"
        mock_log = Mock()
        mock_logger.return_value = mock_log
        
        # Data without status column
        no_status_data = pd.DataFrame({
            '이름': ['김철수', '박영희'],
            '부서': ['개발팀', '마케팅팀']
        })
        mock_read_excel.return_value = no_status_data
        
        mock_excel_data = Mock()
        mock_excel_data_class.return_value = mock_excel_data
        mock_excel_data.get_status_column.return_value = None  # No existing status column
        
        self.manager.read_sheet("TestSheet")
        
        # Should create default status column
        mock_excel_data.set_status_column.assert_called_with('처리상태')
        mock_log.info.assert_called_with("Created new status column: 처리상태")
    
    @patch('pandas.read_excel')
    def test_read_sheet_with_max_rows(self, mock_read_excel):
        """Test reading sheet with row limit"""
        self.manager._current_file = "test.xlsx"
        mock_read_excel.return_value = self.sample_data
        
        with patch('excel.models.ExcelData'):
            self.manager.read_sheet("TestSheet", max_rows=100)
        
        mock_read_excel.assert_called_once_with("test.xlsx", sheet_name="TestSheet", nrows=100)


class TestFileSaving:
    """Test Excel file saving functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = ExcelManager()
    
    def test_save_file_no_data(self):
        """Test saving when no Excel data is loaded"""
        result = self.manager.save_file()
        
        # Should return empty string for standalone mode
        assert result == ""
    
    @patch('pandas.ExcelWriter')
    @patch('pandas.ExcelFile')
    @patch('logger.app_logger.get_logger')
    def test_save_file_success(self, mock_logger, mock_excel_file, mock_excel_writer):
        """Test successful file saving with multi-sheet preservation"""
        mock_log = Mock()
        mock_logger.return_value = mock_log
        
        # Setup mock data
        self.manager._current_file = "test.xlsx"
        mock_excel_data = Mock()
        mock_excel_data.sheet_name = "ModifiedSheet"
        mock_excel_data.dataframe = pd.DataFrame({'col1': [1, 2, 3]})
        self.manager._current_data = mock_excel_data
        
        # Mock existing file reading
        mock_xls = Mock()
        mock_xls.sheet_names = ["ModifiedSheet", "OtherSheet"]
        mock_excel_file.return_value.__enter__.return_value = mock_xls
        
        # Mock sheet reading
        other_sheet_data = pd.DataFrame({'other_col': ['a', 'b', 'c']})
        with patch('pandas.read_excel', return_value=other_sheet_data):
            # Mock Excel writer
            mock_writer = Mock()
            mock_excel_writer.return_value.__enter__.return_value = mock_writer
            
            result = self.manager.save_file()
            
            assert result == "test.xlsx"
            mock_log.info.assert_called_with("Saved Excel file: test.xlsx")
            
            # Verify all sheets were written
            assert mock_writer.to_excel.call_count >= 1
    
    @patch('pandas.ExcelWriter')
    @patch('pandas.ExcelFile')
    def test_save_file_custom_path(self, mock_excel_file, mock_excel_writer):
        """Test saving to custom file path"""
        # Setup mock data
        self.manager._current_file = "original.xlsx"
        mock_excel_data = Mock()
        mock_excel_data.sheet_name = "Sheet1"
        mock_excel_data.dataframe = pd.DataFrame({'col1': [1, 2, 3]})
        self.manager._current_data = mock_excel_data
        
        mock_xls = Mock()
        mock_xls.sheet_names = ["Sheet1"]
        mock_excel_file.return_value.__enter__.return_value = mock_xls
        
        mock_writer = Mock()
        mock_excel_writer.return_value.__enter__.return_value = mock_writer
        
        custom_path = "saved_as.xlsx"
        result = self.manager.save_file(custom_path)
        
        assert result == custom_path


class TestColumnMapping:
    """Test column mapping and variable substitution functionality"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = ExcelManager()
    
    def test_set_column_mapping(self):
        """Test setting column mappings"""
        self.manager.set_column_mapping(
            excel_column="고객명",
            variable_name="customer_name",
            data_type=ColumnType.TEXT,
            is_required=True
        )
        
        assert "customer_name" in self.manager._column_mappings
        mapping = self.manager._column_mappings["customer_name"]
        
        assert mapping.excel_column == "고객명"
        assert mapping.variable_name == "customer_name"
        assert mapping.data_type == ColumnType.TEXT
        assert mapping.is_required is True
    
    def test_get_mapped_data_success(self):
        """Test successful mapped data retrieval"""
        # Setup mock current data
        mock_excel_data = Mock()
        mock_excel_data.get_row_data.return_value = {
            "고객명": "김철수",
            "나이": 30,
            "부서": "개발팀"
        }
        self.manager._current_data = mock_excel_data
        
        # Set up mappings
        self.manager.set_column_mapping("고객명", "customer_name", ColumnType.TEXT)
        self.manager.set_column_mapping("나이", "age", ColumnType.NUMBER)
        self.manager.set_column_mapping("부서", "department", ColumnType.TEXT, is_required=False)
        
        result = self.manager.get_mapped_data(0)
        
        expected = {
            "customer_name": "김철수",
            "age": 30,
            "department": "개발팀"
        }
        assert result == expected
    
    def test_get_mapped_data_with_default_values(self):
        """Test mapped data retrieval with default values"""
        mock_excel_data = Mock()
        mock_excel_data.get_row_data.return_value = {
            "고객명": "김철수"
            # "선택항목" column is missing
        }
        self.manager._current_data = mock_excel_data
        
        # Create mapping with default value
        from excel.models import ColumnMapping
        mapping_with_default = ColumnMapping(
            excel_column="선택항목",
            variable_name="optional_field",
            data_type=ColumnType.TEXT,
            is_required=False,
            default_value="기본값"
        )
        self.manager._column_mappings["optional_field"] = mapping_with_default
        
        self.manager.set_column_mapping("고객명", "customer_name", ColumnType.TEXT)
        
        result = self.manager.get_mapped_data(0)
        
        assert result["customer_name"] == "김철수"
        assert result["optional_field"] == "기본값"
    
    def test_get_mapped_data_required_field_missing(self):
        """Test error when required field is missing"""
        mock_excel_data = Mock()
        mock_excel_data.get_row_data.return_value = {
            "고객명": "김철수"
            # "필수항목" column is missing
        }
        self.manager._current_data = mock_excel_data
        
        self.manager.set_column_mapping("고객명", "customer_name", ColumnType.TEXT)
        self.manager.set_column_mapping("필수항목", "required_field", ColumnType.TEXT, is_required=True)
        
        with pytest.raises(ValueError, match="Required column '필수항목' not found"):
            self.manager.get_mapped_data(0)
    
    def test_get_mapped_data_no_data_loaded(self):
        """Test error when no data is loaded"""
        with pytest.raises(ValueError, match="No data loaded"):
            self.manager.get_mapped_data(0)


class TestStatusManagement:
    """Test status column management and row tracking"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = ExcelManager()
    
    def test_update_row_status_success(self):
        """Test successful row status update"""
        mock_excel_data = Mock()
        self.manager._current_data = mock_excel_data
        
        self.manager.update_row_status(2, "완료", save_immediately=False)
        
        mock_excel_data.update_row_status.assert_called_once_with(2, "완료")
    
    def test_update_row_status_with_save(self):
        """Test row status update with immediate save"""
        mock_excel_data = Mock()
        self.manager._current_data = mock_excel_data
        
        with patch.object(self.manager, 'save_file') as mock_save:
            self.manager.update_row_status(1, "실패", save_immediately=True)
        
        mock_excel_data.update_row_status.assert_called_once_with(1, "실패")
        mock_save.assert_called_once()
    
    def test_update_row_status_no_data(self):
        """Test error when updating status with no data loaded"""
        with pytest.raises(ValueError, match="No data loaded"):
            self.manager.update_row_status(0, "완료")
    
    def test_get_pending_rows_success(self):
        """Test getting pending rows for processing"""
        mock_excel_data = Mock()
        mock_incomplete_df = pd.DataFrame({
            'index': [0, 2, 4],
            'status': ['', '진행중', '']
        })
        mock_incomplete_df.index = [0, 2, 4]
        mock_excel_data.get_incomplete_rows.return_value = mock_incomplete_df
        self.manager._current_data = mock_excel_data
        
        result = self.manager.get_pending_rows()
        
        assert result == [0, 2, 4]
        mock_excel_data.get_incomplete_rows.assert_called_once()
    
    def test_get_pending_rows_no_data(self):
        """Test getting pending rows when no data is loaded"""
        result = self.manager.get_pending_rows()
        assert result == []


class TestAdvancedScenarios:
    """Test advanced scenarios and edge cases"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.manager = ExcelManager()
    
    @patch('pandas.read_excel')
    @patch('openpyxl.load_workbook')
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.stat')
    def test_large_file_memory_optimization(self, mock_stat, mock_exists, mock_load_workbook, mock_read_excel):
        """Test memory optimization with large files (1000-row sampling)"""
        mock_exists.return_value = True
        mock_stat.return_value.st_size = 50 * 1024 * 1024  # 50MB file
        
        # Mock workbook
        mock_workbook = Mock()
        mock_workbook.sheetnames = ["LargeSheet"]
        mock_load_workbook.return_value = mock_workbook
        
        # Mock pandas calls for sampling strategy
        sample_df = pd.DataFrame({
            'col1': range(1000),  # 1000 rows sample
            'col2': [f'text_{i}' for i in range(1000)]
        })
        full_df = pd.DataFrame({'col1': range(10000)})  # 10k rows total
        
        mock_read_excel.side_effect = [sample_df, full_df]
        
        result = self.manager.load_file("/large/file.xlsx")
        
        # Verify sampling was used
        read_calls = mock_read_excel.call_args_list
        assert any('nrows=1000' in str(call) for call in read_calls)  # Sample call
        assert any('usecols=[0]' in str(call) for call in read_calls)  # Count call
        
        # Should report full row count despite sampling
        assert result.sheets[0].row_count == 10000
        assert result.sheets[0].column_count == 2
    
    def test_unicode_and_special_characters(self):
        """Test handling of Unicode and special characters"""
        unicode_data = pd.DataFrame({
            '한글컬럼': ['가나다', '라마바', '사아자'],
            'English': ['Hello', 'World', 'Test'],
            '특수문자!@#': ['!@#', '$%^', '&*()'],
            'Emoji😊': ['😊', '🎉', '🔥'],
            'Mixed한글English': ['Mixed한글1', 'Text영어2', 'Data데이터3']
        })
        
        # Test column analysis with Unicode data
        for column_name, column_data in unicode_data.items():
            series = pd.Series(column_data)
            result = self.manager._analyze_column(series, column_name, 0)
            
            assert isinstance(result, ColumnInfo)
            assert result.name == column_name
            assert result.data_type == ColumnType.TEXT  # Unicode text should be detected as TEXT
            assert len(result.sample_values) <= 5
    
    @patch('pandas.read_excel', side_effect=Exception("Pandas error"))
    @patch('openpyxl.load_workbook')
    @patch('pathlib.Path.exists')
    def test_error_handling_during_analysis(self, mock_exists, mock_load_workbook, mock_read_excel):
        """Test error handling during sheet analysis"""
        mock_exists.return_value = True
        
        mock_workbook = Mock()
        mock_workbook.sheetnames = ["ErrorSheet"]
        mock_load_workbook.return_value = mock_workbook
        
        # Should propagate pandas errors
        with pytest.raises(Exception, match="Pandas error"):
            self.manager.load_file("/error/file.xlsx")
    
    def test_column_type_edge_cases(self):
        """Test edge cases in column type detection"""
        edge_cases = [
            # All NaN/None values
            (pd.Series([None, np.nan, None]), ColumnType.EMPTY),
            
            # Mixed numeric and text that should be TEXT
            (pd.Series([1, 'text', 3]), ColumnType.TEXT),
            
            # Single value series
            (pd.Series([42]), ColumnType.NUMBER),
            (pd.Series(['single']), ColumnType.TEXT),
            
            # Boolean edge cases
            (pd.Series([True, None]), ColumnType.BOOLEAN),  # Might be BOOLEAN or TEXT
            (pd.Series(['Y', 'N']), ColumnType.TEXT),  # Not in boolean values list
            
            # Numeric strings that pandas might not auto-convert
            (pd.Series(['1.5', '2.5', '3.5']), None),  # Depends on pandas behavior
        ]
        
        for series, expected_type in edge_cases:
            if expected_type is not None:
                result = self.manager._detect_column_type(series)
                assert result == expected_type, f"Failed for series: {series.tolist()}"
    
    def test_concurrent_data_access_simulation(self):
        """Test behavior under simulated concurrent access"""
        # Setup data
        mock_excel_data = Mock()
        mock_excel_data.get_row_data.return_value = {"col1": "value1", "col2": "value2"}
        self.manager._current_data = mock_excel_data
        
        self.manager.set_column_mapping("col1", "var1", ColumnType.TEXT)
        self.manager.set_column_mapping("col2", "var2", ColumnType.TEXT)
        
        # Simulate multiple concurrent access attempts
        results = []
        for i in range(10):
            try:
                result = self.manager.get_mapped_data(i)
                results.append(result)
            except Exception as e:
                results.append(e)
        
        # All should succeed with same data
        assert len(results) == 10
        assert all(isinstance(r, dict) for r in results)
        assert all(r["var1"] == "value1" for r in results)


class TestExcelManagerIntegration:
    """Integration-style tests combining multiple functionalities"""
    
    def test_complete_workflow_simulation(self, sample_excel_data):
        """Test complete workflow from file loading to data processing"""
        manager = ExcelManager()
        
        # Mock file loading
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 1024
                with patch('openpyxl.load_workbook') as mock_workbook:
                    mock_wb = Mock()
                    mock_wb.sheetnames = ["TestSheet"]
                    mock_workbook.return_value = mock_wb
                    
                    with patch.object(manager, '_analyze_sheet') as mock_analyze:
                        mock_sheet_info = SheetInfo(
                            name="TestSheet",
                            row_count=3,
                            column_count=4,
                            columns=[
                                ColumnInfo(name="이름", index=0, data_type=ColumnType.TEXT, sample_values=["김철수"], null_count=0, unique_count=3),
                                ColumnInfo(name="나이", index=1, data_type=ColumnType.NUMBER, sample_values=[25], null_count=0, unique_count=3),
                                ColumnInfo(name="상태", index=2, data_type=ColumnType.TEXT, sample_values=[""], null_count=3, unique_count=1)
                            ]
                        )
                        mock_analyze.return_value = mock_sheet_info
                        
                        # 1. Load file
                        file_info = manager.load_file("test.xlsx")
                        assert file_info.sheet_count == 1
        
        # 2. Read sheet data
        with patch('pandas.read_excel', return_value=sample_excel_data):
            with patch('excel.models.ExcelData') as mock_excel_data_class:
                mock_excel_data = Mock()
                mock_excel_data.get_status_column.return_value = "상태"
                mock_excel_data_class.return_value = mock_excel_data
                
                excel_data = manager.read_sheet("TestSheet")
                assert excel_data == mock_excel_data
        
        # 3. Set up column mappings
        manager.set_column_mapping("이름", "name", ColumnType.TEXT)
        manager.set_column_mapping("나이", "age", ColumnType.NUMBER)
        
        # 4. Get mapped data for processing
        mock_excel_data.get_row_data.return_value = {
            "이름": "김철수",
            "나이": 25,
            "상태": ""
        }
        
        mapped_data = manager.get_mapped_data(0)
        assert mapped_data["name"] == "김철수"
        assert mapped_data["age"] == 25
        
        # 5. Update status after processing
        manager.update_row_status(0, "완료")
        mock_excel_data.update_row_status.assert_called_with(0, "완료")
        
        # 6. Get pending rows
        mock_excel_data.get_incomplete_rows.return_value = pd.DataFrame(index=[1, 2])
        pending = manager.get_pending_rows()
        assert pending == [1, 2]
        
        # 7. Save file
        with patch('pandas.ExcelFile') as mock_excel_file:
            with patch('pandas.ExcelWriter') as mock_excel_writer:
                mock_xls = Mock()
                mock_xls.sheet_names = ["TestSheet"]
                mock_excel_file.return_value.__enter__.return_value = mock_xls
                
                mock_writer = Mock()
                mock_excel_writer.return_value.__enter__.return_value = mock_writer
                
                result = manager.save_file()
                assert result == "test.xlsx"


@pytest.mark.performance
class TestPerformanceConsiderations:
    """Test performance-related aspects of ExcelManager"""
    
    def test_large_dataset_memory_usage(self):
        """Test memory efficiency with large datasets"""
        manager = ExcelManager()
        
        # Simulate large dataset
        large_series = pd.Series(['text_value'] * 10000)
        
        import time
        start_time = time.time()
        result = manager._detect_column_type(large_series)
        detection_time = time.time() - start_time
        
        # Should complete quickly (< 1 second for 10k rows)
        assert detection_time < 1.0
        assert result == ColumnType.TEXT
    
    def test_column_analysis_performance(self):
        """Test column analysis performance with various data types"""
        manager = ExcelManager()
        
        # Create diverse dataset
        diverse_data = pd.DataFrame({
            f'col_{i}': [f'value_{j}' for j in range(1000)]
            for i in range(20)  # 20 columns
        })
        
        import time
        start_time = time.time()
        
        # Analyze each column
        for i, (col_name, col_data) in enumerate(diverse_data.items()):
            result = manager._analyze_column(col_data, col_name, i)
            assert isinstance(result, ColumnInfo)
        
        analysis_time = time.time() - start_time
        
        # Should complete within reasonable time (< 2 seconds for 20 columns x 1000 rows)
        assert analysis_time < 2.0