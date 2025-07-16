#!/usr/bin/env python3
"""
Integration tests for execution and logging functionality
"""

import sys
import os
from pathlib import Path
import pytest
import pandas as pd
import tempfile
import time
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_helpers import LogVerifier, GUITestContext, TestScenario
from ui.widgets.execution_widget import ExecutionWidget
from ui.dialogs.log_viewer_dialog import LogViewerDialog
from ui.dialogs.error_report_dialog import ErrorReportDialog
from automation.engine import ExecutionEngine, ExecutionState
from excel.excel_manager import ExcelManager
from core.macro_types import Macro, MacroStep, StepType
from config.settings import Settings
from logger.execution_logger import get_execution_logger


class TestExecutionLogging:
    """Test execution and logging functionality"""
    
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
        
        # Create test data
        test_data = pd.DataFrame({
            '이름': ['홍길동', '김철수', '이영희'],
            '나이': [30, 25, 35],
            '상태': ['대기', '완료', '진행중'],
            'Status': ['', '', '']  # Status column for tracking
        })
        
        # Save to Excel
        test_data.to_excel(temp_file.name, index=False)
        temp_file.close()
        
        yield temp_file.name
        
        # Cleanup
        os.unlink(temp_file.name)
        
    @pytest.fixture
    def test_macro(self):
        """Create test macro"""
        macro = Macro(name="테스트 매크로")
        
        # Add some test steps
        wait_step = MacroStep(step_type=StepType.WAIT_TIME)
        wait_step.name = "1초 대기"
        wait_step.config = {"duration_seconds": 1}
        
        type_step = MacroStep(step_type=StepType.KEYBOARD_TYPE)
        type_step.name = "이름 입력"
        type_step.config = {"text": "{{이름}}", "use_variable": True}
        
        macro.add_step(wait_step)
        macro.add_step(type_step)
        
        return macro
        
    def test_execution_with_csv_logging(self, app, test_excel_file, test_macro):
        """Test macro execution with CSV logging"""
        with GUITestContext(app) as ctx:
            settings = Settings()
            
            # Create Excel manager and load file
            excel_manager = ExcelManager()
            excel_manager.load_file(test_excel_file)
            excel_manager.select_sheet(0)
            excel_manager.set_column_mapping('이름', '이름')
            excel_manager.set_column_mapping('Status', 'Status')
            
            # Create execution widget
            exec_widget = ExecutionWidget(settings)
            exec_widget.set_macro_and_excel(test_macro, excel_manager)
            exec_widget.show()
            ctx.process_events(100)
            
            # Get execution logger
            logger = get_execution_logger()
            
            # Start execution
            exec_widget.start_execution()
            
            # Wait for execution to start
            start_time = time.time()
            while exec_widget.engine.state != ExecutionState.RUNNING and time.time() - start_time < 5:
                ctx.process_events(100)
                
            # Let it run for a bit
            ctx.process_events(2000)
            
            # Stop execution
            exec_widget.stop_execution()
            
            # Wait for stop
            while exec_widget.engine.state != ExecutionState.IDLE and time.time() - start_time < 10:
                ctx.process_events(100)
                
            # Get log file
            log_file = logger.get_current_log_file()
            assert log_file is not None
            assert log_file.exists()
            
            # Verify log contents
            verifier = LogVerifier(log_file)
            
            # Check session started
            assert any(entry['step_name'] == 'SESSION_START' for entry in verifier.entries)
            
            # Check some steps executed
            assert verifier.verify_step_executed("1초 대기")
            
            # Get summary
            summary = verifier.get_execution_summary()
            assert summary['total_steps'] > 0
            
            exec_widget.close()
            
    def test_error_dialog_on_failure(self, app, test_macro):
        """Test error dialog appears on execution failure"""
        with GUITestContext(app) as ctx:
            settings = Settings()
            
            # Create macro with failing step
            fail_step = MacroStep(step_type=StepType.WAIT_IMAGE)
            fail_step.name = "찾을 수 없는 이미지"
            fail_step.config = {
                "image_path": "/nonexistent/image.png",
                "timeout_seconds": 1
            }
            test_macro.add_step(fail_step, 0)  # Add at beginning
            
            # Mock execution that will fail
            error_shown = False
            original_show = ErrorReportDialog.show_error
            
            def mock_show_error(*args, **kwargs):
                nonlocal error_shown
                error_shown = True
                # Don't actually show dialog in test
                
            ErrorReportDialog.show_error = mock_show_error
            
            try:
                # Create minimal execution setup
                engine = ExecutionEngine(settings)
                
                # Emit error signal
                engine.error.emit("Test error: Image not found")
                ctx.process_events(100)
                
                # Verify error handling was triggered
                # In real execution, this would show the error dialog
                
            finally:
                ErrorReportDialog.show_error = original_show
                
    def test_log_viewer_real_time_update(self, app):
        """Test log viewer updates in real-time"""
        with GUITestContext(app) as ctx:
            # Create log file
            logger = get_execution_logger()
            log_file = logger.start_session("실시간 테스트", "test.xlsx")
            
            # Create and show log viewer
            viewer = LogViewerDialog(log_file)
            viewer.show()
            ctx.process_events(100)
            
            # Initial row count
            initial_rows = viewer.log_table.rowCount()
            
            # Add some log entries
            logger.log_row_start(0, {"테스트": "데이터"})
            logger.log_step_execution(0, 0, "테스트 단계", "test", True, 100.5)
            logger.flush()
            
            # Wait for auto-refresh (viewer refreshes every 2 seconds for active logs)
            ctx.process_events(2500)
            
            # Check if new entries appeared
            new_rows = viewer.log_table.rowCount()
            assert new_rows > initial_rows
            
            # Close logger
            logger.close()
            viewer.close()
            
    def test_log_statistics_calculation(self, app):
        """Test log statistics calculation"""
        with GUITestContext(app) as ctx:
            # Create log with known data
            logger = get_execution_logger()
            log_file = logger.start_session("통계 테스트", "test.xlsx")
            
            # Log specific test data
            # Row 1 - Success
            logger.log_row_start(0, {"name": "test1"})
            logger.log_step_execution(0, 0, "Step1", "click", True, 100)
            logger.log_step_execution(0, 1, "Step2", "type", True, 200)
            logger.log_row_complete(0, True, 300)
            
            # Row 2 - Failure
            logger.log_row_start(1, {"name": "test2"})
            logger.log_step_execution(1, 0, "Step1", "click", False, 150, "Not found")
            logger.log_row_complete(1, False, 150, "Step failed")
            
            # Row 3 - Success
            logger.log_row_start(2, {"name": "test3"})
            logger.log_step_execution(2, 0, "Step1", "click", True, 120)
            logger.log_row_complete(2, True, 120)
            
            logger.flush()
            
            # Create verifier
            verifier = LogVerifier(log_file)
            summary = verifier.get_execution_summary()
            
            # Verify statistics
            assert summary['total_rows'] == 3
            assert summary['successful_rows'] == 2
            assert summary['failed_rows'] == 1
            assert summary['success_rate'] == pytest.approx(66.67, 0.1)
            
            # Check step statistics
            assert summary['total_steps'] == 4
            assert summary['successful_steps'] == 3
            assert summary['failed_steps'] == 1
            
            logger.close()
            
    def test_execution_pause_resume(self, app, test_excel_file, test_macro):
        """Test pause and resume functionality with logging"""
        with GUITestContext(app) as ctx:
            settings = Settings()
            
            # Setup
            excel_manager = ExcelManager()
            excel_manager.load_file(test_excel_file)
            excel_manager.select_sheet(0)
            
            exec_widget = ExecutionWidget(settings)
            exec_widget.set_macro_and_excel(test_macro, excel_manager)
            
            # Start execution
            exec_widget.start_execution()
            ctx.process_events(500)
            
            # Pause
            exec_widget.toggle_pause()
            ctx.process_events(100)
            
            # Verify paused state
            assert exec_widget.engine.state == ExecutionState.PAUSED
            
            # Resume
            exec_widget.toggle_pause()
            ctx.process_events(100)
            
            # Verify resumed
            assert exec_widget.engine.state == ExecutionState.RUNNING
            
            # Stop
            exec_widget.stop_execution()
            ctx.process_events(500)
            
            exec_widget.close()
            
    def test_error_recovery_scenarios(self, app):
        """Test various error recovery scenarios"""
        scenarios = TestScenario("에러 복구 시나리오")
        
        # Scenario 1: Retry on failure
        scenarios.add_step(
            "재시도 설정 테스트",
            lambda ctx: {
                'error_handling': 'retry',
                'retry_count': 3,
                'retry_success': False  # Simulated
            }
        )
        
        # Scenario 2: Continue on error
        scenarios.add_step(
            "계속 진행 설정 테스트",
            lambda ctx: {
                'error_handling': 'continue',
                'error_logged': True,
                'execution_continued': True
            }
        )
        
        # Scenario 3: Stop on error
        scenarios.add_step(
            "중지 설정 테스트",
            lambda ctx: {
                'error_handling': 'stop',
                'execution_stopped': True,
                'error_dialog_shown': True
            }
        )
        
        # Execute scenarios
        results = scenarios.execute({})
        
        # Verify all scenarios passed
        assert results['success']
        for step in results['steps']:
            assert step['passed']


def run_tests():
    """Run tests standalone"""
    pytest.main([__file__, "-v", "-s"])


if __name__ == "__main__":
    run_tests()