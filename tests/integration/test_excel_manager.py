#!/usr/bin/env python3
"""
Integration tests for Excel data load and mapping functionality
"""

import sys
import os
from pathlib import Path
import pytest
import tempfile
import pandas as pd
from PyQt5.QtWidgets import QApplication

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_helpers import GUITestContext
from excel.excel_manager import ExcelManager
from excel.models import ColumnType, ColumnMapping
from config.settings import Settings


class TestExcelManager:
    """Test Excel data load and mapping functionality"""
    
    @pytest.fixture
    def app(self):
        """Create QApplication for tests"""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app
        
    @pytest.fixture
    def test_excel_file(self):
        """Create test Excel file"""
        # Create temporary Excel file
        temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        
        # Create test data with multiple sheets
        data1 = pd.DataFrame({
            '이름': ['홍길동', '김철수', '이영희', '박민수', '최지혜'],
            '나이': [30, 25, 35, 28, 32],
            '이메일': ['hong@test.com', 'kim@test.com', 'lee@test.com', 'park@test.com', 'choi@test.com'],
            '부서': ['개발팀', '마케팅팀', '개발팀', '영업팀', '개발팀'],
            '상태': ['활성', '활성', '비활성', '활성', '활성'],
            'Status': ['', '', '', '', '']  # Status column for tracking
        })
        
        data2 = pd.DataFrame({
            '제품명': ['노트북', '마우스', '키보드', '모니터'],
            '가격': [1200000, 35000, 80000, 450000],
            '재고': [15, 200, 150, 25],
            '카테고리': ['전자제품', '액세서리', '액세서리', '전자제품']
        })
        
        # Save to Excel with multiple sheets
        with pd.ExcelWriter(temp_file.name, engine='openpyxl') as writer:
            data1.to_excel(writer, sheet_name='직원목록', index=False)
            data2.to_excel(writer, sheet_name='제품목록', index=False)
            
        temp_file.close()
        yield temp_file.name
        
        # Cleanup
        os.unlink(temp_file.name)
        
    def test_load_excel_file(self, app, test_excel_file):
        """Test loading Excel file"""
        with GUITestContext(app) as ctx:
            manager = ExcelManager()
            
            # Load file
            file_info = manager.load_file(test_excel_file)
            
            # Verify file info
            assert file_info.file_path == test_excel_file
            assert file_info.sheet_count == 2
            assert len(file_info.sheets) == 2
            
            # Check sheet names
            sheet_names = [sheet.name for sheet in file_info.sheets]
            assert '직원목록' in sheet_names
            assert '제품목록' in sheet_names
            
    def test_analyze_sheet(self, app, test_excel_file):
        """Test sheet analysis"""
        with GUITestContext(app) as ctx:
            manager = ExcelManager()
            file_info = manager.load_file(test_excel_file)
            
            # Check employee sheet
            employee_sheet = next(s for s in file_info.sheets if s.name == '직원목록')
            assert employee_sheet.row_count == 5
            assert employee_sheet.column_count == 6
            
            # Check column names
            column_names = [col.name for col in employee_sheet.columns]
            assert '이름' in column_names
            assert '나이' in column_names
            assert '이메일' in column_names
            
    def test_column_type_detection(self, app, test_excel_file):
        """Test column type detection"""
        with GUITestContext(app) as ctx:
            manager = ExcelManager()
            file_info = manager.load_file(test_excel_file)
            
            employee_sheet = next(s for s in file_info.sheets if s.name == '직원목록')
            
            # Check column types
            name_col = next(c for c in employee_sheet.columns if c.name == '이름')
            assert name_col.data_type == ColumnType.TEXT
            
            age_col = next(c for c in employee_sheet.columns if c.name == '나이')
            assert age_col.data_type == ColumnType.NUMBER
            
            email_col = next(c for c in employee_sheet.columns if c.name == '이메일')
            assert email_col.data_type == ColumnType.TEXT
            
    def test_select_sheet(self, app, test_excel_file):
        """Test sheet selection"""
        with GUITestContext(app) as ctx:
            manager = ExcelManager()
            manager.load_file(test_excel_file)
            
            # Select sheet
            excel_data = manager.read_sheet('직원목록')
            
            # Verify data loaded
            assert excel_data is not None
            assert excel_data.sheet_name == '직원목록'
            assert len(excel_data.dataframe) == 5
            assert list(excel_data.dataframe.columns) == ['이름', '나이', '이메일', '부서', '상태', 'Status']
            
    def test_column_mapping(self, app, test_excel_file):
        """Test column mapping functionality"""
        with GUITestContext(app) as ctx:
            manager = ExcelManager()
            manager.load_file(test_excel_file)
            manager.read_sheet('직원목록')
            
            # Set column mappings
            manager.set_column_mapping('이름', 'name', ColumnType.TEXT, True)
            manager.set_column_mapping('이메일', 'email', ColumnType.TEXT, True)
            manager.set_column_mapping('Status', 'status', ColumnType.TEXT, False)
            
            # Get mappings (accessing internal attribute)
            mappings = manager._column_mappings
            assert len(mappings) == 3
            assert mappings['name'].excel_column == '이름'
            assert mappings['email'].excel_column == '이메일'
            assert mappings['status'].excel_column == 'Status'
            
    def test_get_row_data(self, app, test_excel_file):
        """Test getting row data with mappings"""
        with GUITestContext(app) as ctx:
            manager = ExcelManager()
            manager.load_file(test_excel_file)
            manager.read_sheet('직원목록')
            
            # Set mappings
            manager.set_column_mapping('이름', 'name', ColumnType.TEXT, True)
            manager.set_column_mapping('나이', 'age', ColumnType.NUMBER, True)
            manager.set_column_mapping('이메일', 'email', ColumnType.TEXT, True)
            
            # Get first row data
            row_data = manager.get_mapped_data(0)
            
            # Verify data
            assert row_data['name'] == '홍길동'
            assert row_data['age'] == 30
            assert row_data['email'] == 'hong@test.com'
            
    def test_update_status_column(self, app, test_excel_file):
        """Test updating status column"""
        with GUITestContext(app) as ctx:
            manager = ExcelManager()
            manager.load_file(test_excel_file)
            excel_data = manager.read_sheet('직원목록')
            
            # Update status using ExcelManager's update_row_status
            manager.update_row_status(0, 'Completed')
            
            # Verify update in the dataframe
            assert excel_data.dataframe.iloc[0][excel_data.get_status_column()] == 'Completed'
            
    def test_filter_incomplete_rows(self, app, test_excel_file):
        """Test filtering incomplete rows"""
        with GUITestContext(app) as ctx:
            manager = ExcelManager()
            manager.load_file(test_excel_file)
            manager.read_sheet('직원목록')
            
            # Update some rows
            manager.update_row_status(0, 'Completed')
            manager.update_row_status(2, 'Completed')
            
            # Get pending rows
            pending_indices = manager.get_pending_rows()
            
            # Should have 3 incomplete rows (1, 3, 4)
            assert len(pending_indices) == 3
            assert 1 in pending_indices
            assert 3 in pending_indices
            assert 4 in pending_indices
            
    def test_save_excel_file(self, app, test_excel_file):
        """Test saving Excel file with updates"""
        with GUITestContext(app) as ctx:
            manager = ExcelManager()
            manager.load_file(test_excel_file)
            excel_data = manager.read_sheet('직원목록')
            
            # Make updates
            manager.update_row_status(0, 'Processed')
            manager.update_row_status(1, 'Processed')
            
            # Save file (returns path, not boolean)
            saved_path = manager.save_file()
            assert saved_path == test_excel_file
            
            # Reload and verify
            manager2 = ExcelManager()
            manager2.load_file(test_excel_file)
            data2 = manager2.read_sheet('직원목록')
            
            # Check saved values
            status_col = data2.get_status_column()
            assert data2.dataframe.iloc[0][status_col] == 'Processed'
            assert data2.dataframe.iloc[1][status_col] == 'Processed'
            
    def test_multiple_sheet_handling(self, app, test_excel_file):
        """Test handling multiple sheets"""
        with GUITestContext(app) as ctx:
            manager = ExcelManager()
            file_info = manager.load_file(test_excel_file)
            
            # Load first sheet
            data1 = manager.read_sheet('직원목록')
            assert data1.sheet_name == '직원목록'
            assert len(data1.dataframe) == 5
            
            # Switch to second sheet
            data2 = manager.read_sheet('제품목록')
            assert data2.sheet_name == '제품목록'
            assert len(data2.dataframe) == 4
            
            # Column names should be different
            assert '제품명' in data2.dataframe.columns
            assert '가격' in data2.dataframe.columns
            
    def test_invalid_file_handling(self, app):
        """Test handling of invalid files"""
        with GUITestContext(app) as ctx:
            manager = ExcelManager()
            
            # Non-existent file
            with pytest.raises(FileNotFoundError):
                manager.load_file("/nonexistent/file.xlsx")
                
            # Invalid format
            temp_file = tempfile.NamedTemporaryFile(suffix='.txt', delete=False)
            temp_file.write(b"Not an Excel file")
            temp_file.close()
            
            with pytest.raises(ValueError):
                manager.load_file(temp_file.name)
                
            os.unlink(temp_file.name)
            
    def test_empty_excel_handling(self, app):
        """Test handling empty Excel files"""
        with GUITestContext(app) as ctx:
            # Create empty Excel file
            temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
            empty_df = pd.DataFrame()
            empty_df.to_excel(temp_file.name, index=False)
            temp_file.close()
            
            manager = ExcelManager()
            file_info = manager.load_file(temp_file.name)
            
            # Should handle gracefully
            assert file_info.sheet_count >= 1
            
            os.unlink(temp_file.name)


def run_tests():
    """Run tests standalone"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_tests()