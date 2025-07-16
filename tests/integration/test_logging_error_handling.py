#!/usr/bin/env python3
"""
Integration tests for execution logging and error handling
"""

import sys
import os
from pathlib import Path
import pytest
import tempfile
import csv
import time
from datetime import datetime
from PyQt5.QtWidgets import QApplication

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_helpers import GUITestContext
from logger.execution_logger import ExecutionLogger, get_execution_logger
from automation.engine import ExecutionResult
from config.settings import Settings


class TestExecutionLogging:
    """Test execution logging functionality"""
    
    @pytest.fixture
    def app(self):
        """Create QApplication for tests"""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app
        
    @pytest.fixture
    def settings(self):
        """Create test settings"""
        return Settings()
        
    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        
    @pytest.fixture
    def execution_logger(self, temp_log_dir):
        """Create execution logger with temp directory"""
        logger = ExecutionLogger(log_dir=Path(temp_log_dir))
        yield logger
        
    def test_start_session(self, app, execution_logger):
        """Test starting a logging session"""
        with GUITestContext(app) as ctx:
            # Start session
            log_file = execution_logger.start_session(
                macro_name="테스트 매크로",
                excel_file="test_data.xlsx"
            )
            
            # Verify log file created
            assert log_file is not None
            assert Path(log_file).exists()
            assert str(log_file).endswith('.csv')
            
            # Check file name format
            file_name = Path(log_file).name
            assert file_name.startswith("execution_")
            assert ".csv" in file_name
            
            # Close the session
            execution_logger.close()
            
    def test_log_row_execution(self, app, execution_logger):
        """Test logging row execution process"""
        with GUITestContext(app) as ctx:
            # Start session
            log_file = execution_logger.start_session(
                macro_name="테스트 매크로",
                excel_file="test_data.xlsx"
            )
            
            # Log row start
            execution_logger.log_row_start(
                row_index=0,
                row_data={'이름': '홍길동', '나이': 30}
            )
            
            # Log successful row completion
            execution_logger.log_row_complete(
                row_index=0,
                success=True,
                total_duration_ms=1500.5,
                error_message=""
            )
            
            # Log another row with failure
            execution_logger.log_row_start(
                row_index=1,
                row_data={'이름': '김철수', '나이': 25}
            )
            
            execution_logger.log_row_complete(
                row_index=1,
                success=False,
                total_duration_ms=500.0,
                error_message="클릭 위치를 찾을 수 없음"
            )
            
            # Force close to flush
            execution_logger.close()
            
            # Verify file has content
            assert Path(log_file).stat().st_size > 0
            
    def test_log_step_execution(self, app, execution_logger):
        """Test logging individual step execution"""
        with GUITestContext(app) as ctx:
            # Start session
            log_file = execution_logger.start_session(
                macro_name="테스트 매크로",
                excel_file="test_data.xlsx"
            )
            
            # Log row start
            execution_logger.log_row_start(0, {'test': 'data'})
            
            # Log step executions
            execution_logger.log_step_execution(
                row_index=0,
                step_index=0,
                step_name="마우스 클릭",
                step_type="mouse_click",
                success=True,
                duration_ms=100.0,
                error_message="",
                details=""
            )
            
            execution_logger.log_step_execution(
                row_index=0,
                step_index=1,
                step_name="텍스트 입력",
                step_type="keyboard_type",
                success=False,
                duration_ms=50.0,
                error_message="타임아웃",
                details="입력 실패"
            )
            
            # Complete row
            execution_logger.log_row_complete(0, False, 150.0, "일부 단계 실패")
            
            # Close session
            execution_logger.close()
            
            # Verify log file has content
            assert Path(log_file).stat().st_size > 0
            
    def test_session_end_logging(self, app, execution_logger):
        """Test session end summary logging"""
        with GUITestContext(app) as ctx:
            # Start session
            log_file = execution_logger.start_session(
                macro_name="테스트 매크로",
                excel_file="test_data.xlsx"
            )
            
            # Log some rows
            for i in range(5):
                execution_logger.log_row_start(i, {'index': i})
                execution_logger.log_row_complete(
                    row_index=i,
                    success=(i % 2 == 0),  # Alternate success/failure
                    total_duration_ms=1000.0,
                    error_message="" if i % 2 == 0 else "Test error"
                )
                
            # Log session end
            execution_logger.log_session_end(
                total_rows=5,
                successful_rows=3,
                failed_rows=2
            )
            
            # Close
            execution_logger.close()
            
            # Verify log file exists and has content
            assert Path(log_file).exists()
            assert Path(log_file).stat().st_size > 0
            
    def test_error_logging(self, app, execution_logger):
        """Test error logging functionality"""
        with GUITestContext(app) as ctx:
            # Start session
            log_file = execution_logger.start_session(
                macro_name="에러 테스트",
                excel_file="test.xlsx"
            )
            
            # Log various errors
            execution_logger.log_error(
                error_type="ImageNotFound",
                error_message="대상 이미지를 찾을 수 없습니다",
                details="image_path: /tmp/target.png"
            )
            
            execution_logger.log_error(
                error_type="TimeoutError",
                error_message="작업 시간 초과",
                details="timeout: 30s"
            )
            
            # Close
            execution_logger.close()
            
            # Verify errors were logged
            assert Path(log_file).stat().st_size > 0
            
    def test_concurrent_logging(self, app, temp_log_dir):
        """Test multiple logger instances"""
        with GUITestContext(app) as ctx:
            # Create multiple logger instances
            logger1 = ExecutionLogger(log_dir=Path(temp_log_dir))
            logger2 = ExecutionLogger(log_dir=Path(temp_log_dir))
            
            # Start sessions
            log_file1 = logger1.start_session("매크로1", "data1.xlsx")
            log_file2 = logger2.start_session("매크로2", "data2.xlsx")
            
            # Log to both
            logger1.log_row_start(0, {'data': 1})
            logger1.log_row_complete(0, True, 100, "")
            
            logger2.log_row_start(0, {'data': 2})
            logger2.log_row_complete(0, True, 200, "")
            
            # Close sessions
            logger1.close()
            logger2.close()
            
            # Both files should exist
            assert Path(log_file1).exists()
            assert Path(log_file2).exists()
            assert log_file1 != log_file2
            
    def test_get_execution_logger_singleton(self, app):
        """Test singleton logger instance"""
        with GUITestContext(app) as ctx:
            # Get logger instances
            logger1 = get_execution_logger()
            logger2 = get_execution_logger()
            
            # Should be the same instance
            assert logger1 is logger2
            
    def test_long_running_session(self, app, execution_logger):
        """Test logging over extended period"""
        with GUITestContext(app) as ctx:
            # Start session
            log_file = execution_logger.start_session(
                macro_name="장시간 테스트",
                excel_file="test.xlsx"
            )
            
            # Log many rows with small delays
            for i in range(10):
                execution_logger.log_row_start(i, {'index': i})
                
                # Log multiple steps
                for j in range(3):
                    execution_logger.log_step_execution(
                        row_index=i,
                        step_index=j,
                        step_name=f"단계 {j}",
                        step_type="wait_time",
                        success=True,
                        duration_ms=50.0,
                        error_message="",
                        details=""
                    )
                    
                execution_logger.log_row_complete(i, True, 150.0, "")
                
                # Small delay
                time.sleep(0.01)
                
            # Close
            execution_logger.close()
            
            # Should have logged all data
            assert Path(log_file).stat().st_size > 0
            
    def test_log_directory_creation(self, app):
        """Test automatic log directory creation"""
        with GUITestContext(app) as ctx:
            # Create logger with non-existent directory
            non_existent = Path("/tmp/test_macro_logs_" + str(time.time()))
            logger = ExecutionLogger(log_dir=non_existent)
            
            # Start session should create directory
            log_file = logger.start_session("테스트", "data.xlsx")
            
            # Directory should be created
            assert non_existent.exists()
            assert non_existent.is_dir()
            
            # Cleanup
            logger.close()
            import shutil
            shutil.rmtree(non_existent)
            
    def test_special_characters_in_data(self, app, execution_logger):
        """Test logging data with special characters"""
        with GUITestContext(app) as ctx:
            # Start session
            log_file = execution_logger.start_session(
                macro_name="특수문자 테스트",
                excel_file="test.xlsx"
            )
            
            # Log data with special characters
            execution_logger.log_row_start(
                row_index=0,
                row_data={
                    'name': '홍길동, "테스터"',
                    'description': 'Line1\nLine2\nLine3',
                    'note': 'Tab\there',
                    'path': 'C:\\Users\\Test\\File.txt'
                }
            )
            
            execution_logger.log_row_complete(0, True, 100, "")
            
            # Close
            execution_logger.close()
            
            # Should handle special characters properly
            assert Path(log_file).exists()
            
    def test_empty_session(self, app, execution_logger):
        """Test session with no data logged"""
        with GUITestContext(app) as ctx:
            # Start session
            log_file = execution_logger.start_session(
                macro_name="빈 세션",
                excel_file="empty.xlsx"
            )
            
            # Close immediately without logging
            execution_logger.close()
            
            # File should still exist (with headers at least)
            assert Path(log_file).exists()


def run_tests():
    """Run tests standalone"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_tests()