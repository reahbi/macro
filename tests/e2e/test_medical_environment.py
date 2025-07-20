"""
E2E tests for medical environment requirements
Tests specific to healthcare/hospital use cases with large datasets and offline operation
"""

import pytest
import time
import pandas as pd
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QApplication

from ui.main_window import MainWindow
from core.macro_types import Macro, KeyboardTypeStep, MouseClickStep, WaitTimeStep, LoopStep
from excel.excel_manager import ExcelManager
from automation.engine import ExecutionEngine, ExecutionState
from config.settings import Settings


@pytest.mark.e2e
class TestMedicalEnvironmentLargeData:
    """Test large-scale patient data processing for medical environments"""
    
    @pytest.fixture
    def app(self):
        """Create QApplication for testing"""
        if not QApplication.instance():
            app = QApplication([])
        else:
            app = QApplication.instance()
        return app
    
    @pytest.fixture
    def mock_settings(self):
        """Create mock settings for medical environment"""
        mock_settings_obj = Mock(spec=Settings)
        
        def mock_get(key, default=None):
            settings_map = {
                "ui.window_size": [1920, 1080],
                "macro.recent_files": [],
                "execution.default_delay_ms": 50,  # Faster for testing
                "ui.compact_mode": False,
                "execution.batch_size": 100,  # Process 100 patients at a time
                "execution.memory_limit_mb": 500
            }
            return settings_map.get(key, default)
        
        mock_settings_obj.get.side_effect = mock_get
        mock_settings_obj.set.return_value = None
        mock_settings_obj.save.return_value = None
        
        return mock_settings_obj
    
    @pytest.fixture
    def large_patient_data(self):
        """Generate large patient dataset (100+ records)"""
        patient_count = 150
        
        data = {
            '환자번호': [f'P{str(i).zfill(6)}' for i in range(1, patient_count + 1)],
            '환자명': [f'환자{i}' for i in range(1, patient_count + 1)],
            '생년월일': ['1970-01-01'] * patient_count,
            '성별': ['M' if i % 2 == 0 else 'F' for i in range(patient_count)],
            '진료과': ['내과', '외과', '정형외과', '신경과', '소아과'] * (patient_count // 5),
            '진료일자': ['2025-01-20'] * patient_count,
            '검사항목': ['혈액검사', 'X-Ray', 'MRI', 'CT', '초음파'] * (patient_count // 5),
            '검사결과': ['정상', '이상', '재검필요', '정상', '정상'] * (patient_count // 5),
            '처리상태': [''] * patient_count,  # Empty status column
            '오류메시지': [''] * patient_count
        }
        
        return pd.DataFrame(data)
    
    def test_batch_patient_data_processing(self, app, mock_settings, large_patient_data):
        """Test processing 100+ patient records in batches"""
        
        # Create main window with settings
        with patch('config.settings.Settings', return_value=mock_settings):
            main_window = MainWindow(mock_settings)
        
        # Mock Excel manager with large dataset
        mock_excel_manager = Mock()
        
        def mock_get_row_data(row_index):
            if row_index < len(large_patient_data):
                return large_patient_data.iloc[row_index].to_dict()
            return {}
        
        def mock_get_mapped_data(row_index):
            row_data = mock_get_row_data(row_index)
            return {
                'patient_id': row_data.get('환자번호', ''),
                'patient_name': row_data.get('환자명', ''),
                'department': row_data.get('진료과', ''),
                'test_item': row_data.get('검사항목', ''),
                'test_result': row_data.get('검사결과', '')
            }
        
        mock_excel_manager.get_row_data.side_effect = mock_get_row_data
        mock_excel_manager.get_mapped_data.side_effect = mock_get_mapped_data
        mock_excel_manager.get_total_rows.return_value = len(large_patient_data)
        mock_excel_manager.has_data.return_value = True
        
        # Create medical data entry macro
        medical_macro = Macro(name="환자 데이터 일괄 입력")
        
        # Add steps for patient data entry
        medical_macro.add_step(KeyboardTypeStep(
            name="환자번호 입력",
            text="{{patient_id}}"
        ))
        medical_macro.add_step(WaitTimeStep(name="대기", seconds=0.01))  # Fast for testing
        medical_macro.add_step(KeyboardTypeStep(
            name="환자정보 입력",
            text="{{patient_name}} - {{department}}"
        ))
        medical_macro.add_step(KeyboardTypeStep(
            name="검사결과 입력",
            text="{{test_item}}: {{test_result}}"
        ))
        
        # Setup execution engine
        execution_engine = main_window.execution_widget.engine
        execution_engine.set_macro(medical_macro, mock_excel_manager)
        
        # Track execution metrics
        processed_count = 0
        start_time = time.time()
        memory_usage = []
        
        def track_execution(*args, **kwargs):
            nonlocal processed_count
            processed_count += 1
            # Simulate memory tracking
            import psutil
            import os
            process = psutil.Process(os.getpid())
            memory_usage.append(process.memory_info().rss / 1024 / 1024)  # MB
        
        # Execute with monitoring
        with patch('pyautogui.typewrite', side_effect=track_execution):
            with patch.object(execution_engine, '_set_state'):
                with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                    with patch.object(execution_engine.execution_logger, 'log_row_start'):
                        with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                            with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                with patch.object(execution_engine.execution_logger, 'close'):
                                    
                                    # Process first 100 patients
                                    for i in range(100):
                                        result = execution_engine._execute_row(i)
                                        assert result.success is True
        
        execution_time = time.time() - start_time
        
        # Verify performance requirements
        assert processed_count >= 300  # 3 typewrite steps per patient × 100 patients
        assert execution_time < 30  # Should complete 100 patients in < 30 seconds
        
        # Verify memory usage stayed under limit
        if memory_usage:
            max_memory = max(memory_usage)
            avg_memory = sum(memory_usage) / len(memory_usage)
            assert max_memory < 500  # Max 500MB as per PRD
            print(f"Memory usage - Max: {max_memory:.1f}MB, Avg: {avg_memory:.1f}MB")
    
    def test_offline_operation_simulation(self, app, mock_settings):
        """Test application works completely offline"""
        
        # Patch all network-related operations
        with patch('urllib.request.urlopen') as mock_urlopen:
            with patch('requests.get') as mock_requests:
                with patch('socket.socket') as mock_socket:
                    
                    # Make all network calls fail
                    mock_urlopen.side_effect = Exception("No internet connection")
                    mock_requests.side_effect = Exception("No internet connection")
                    mock_socket.side_effect = Exception("No internet connection")
                    
                    # Create main window - should work offline
                    with patch('config.settings.Settings', return_value=mock_settings):
                        main_window = MainWindow(mock_settings)
                        assert main_window is not None
                    
                    # Create and execute macro - should work offline
                    offline_macro = Macro(name="오프라인 테스트")
                    offline_macro.add_step(MouseClickStep(name="클릭", x=100, y=100))
                    offline_macro.add_step(KeyboardTypeStep(name="입력", text="오프라인 작동 확인"))
                    
                    # Verify macro can be saved/loaded locally
                    with tempfile.TemporaryDirectory() as temp_dir:
                        temp_path = Path(temp_dir) / "offline_macro.json"
                        
                        # Save macro
                        from core.macro_storage import MacroStorage
                        storage = MacroStorage(Path(temp_dir))
                        
                        with patch('pathlib.Path.write_text') as mock_write:
                            mock_write.return_value = None
                            result = storage.save_macro(offline_macro, str(temp_path))
                            assert result is True
                    
                    # Verify no network calls were attempted during operation
                    mock_urlopen.assert_not_called()
                    mock_requests.assert_not_called()
    
    def test_continuous_operation_stability(self, app, mock_settings):
        """Test 24-hour continuous operation stability"""
        
        with patch('config.settings.Settings', return_value=mock_settings):
            main_window = MainWindow(mock_settings)
        
        # Create repetitive task macro
        continuous_macro = Macro(name="연속 작업 테스트")
        continuous_macro.add_step(KeyboardTypeStep(name="데이터 입력", text="테스트 {{index}}"))
        continuous_macro.add_step(WaitTimeStep(name="대기", seconds=0.001))  # Very fast for testing
        
        execution_engine = main_window.execution_widget.engine
        execution_engine.set_macro(continuous_macro)
        
        # Simulate 1000 iterations (representing hours of operation)
        error_count = 0
        execution_times = []
        
        with patch('pyautogui.typewrite'):
            with patch.object(execution_engine, '_set_state'):
                for i in range(1000):
                    start = time.time()
                    
                    # Set variable for substitution
                    execution_engine.step_executor.set_variables({'index': str(i)})
                    
                    try:
                        result = execution_engine._execute_standalone()
                        if not result.success:
                            error_count += 1
                    except Exception:
                        error_count += 1
                    
                    execution_times.append(time.time() - start)
        
        # Verify stability metrics
        assert error_count < 10  # Less than 1% error rate
        assert max(execution_times) < 1.0  # No single execution > 1 second
        
        # Check for memory leaks (simplified check)
        import gc
        gc.collect()
        # In real scenario, would check actual memory usage over time


@pytest.mark.e2e
class TestMedicalSecurityCompliance:
    """Test security and compliance features for medical environments"""
    
    def test_sensitive_data_handling(self, temp_dir):
        """Test that sensitive patient data is handled securely"""
        
        # Create macro with sensitive data
        sensitive_macro = Macro(name="민감정보 처리")
        sensitive_macro.add_step(KeyboardTypeStep(
            name="주민번호 입력",
            text="{{patient_ssn}}",
            mask_in_logs=True  # Should mask in logs
        ))
        
        # Save macro with encryption
        from core.macro_storage import MacroStorage
        storage = MacroStorage(temp_dir)
        
        # Mock encryption to verify it's used
        with patch.object(storage.encryption_manager, 'encrypt') as mock_encrypt:
            mock_encrypt.return_value = b'encrypted_data'
            
            # Save with encryption
            from core.macro_types import MacroFormat
            result = storage.save_macro(
                sensitive_macro,
                format_type=MacroFormat.ENCRYPTED
            )
            
            # Verify encryption was used
            mock_encrypt.assert_called_once()
    
    def test_audit_trail_generation(self):
        """Test that all operations generate audit trails"""
        
        from logger.execution_logger import ExecutionLogger
        
        with tempfile.TemporaryDirectory() as log_dir:
            logger = ExecutionLogger(Path(log_dir))
            
            # Start session
            log_file = logger.start_session("의료_데이터_처리")
            assert log_file is not None
            
            # Log patient data processing
            logger.log_row_start(0, {'환자번호': 'P001', '환자명': '테스트'})
            logger.log_step_execution(
                step_name="환자정보 입력",
                success=True,
                duration=0.5,
                details={'action': 'typewrite', 'masked': True}
            )
            logger.log_row_complete(0, success=True, duration=1.0)
            
            logger.close()
            
            # Verify log file exists and contains audit trail
            log_path = Path(log_file)
            assert log_path.exists()
            
            # Check log doesn't contain sensitive data
            log_content = log_path.read_text(encoding='utf-8')
            assert 'P001' not in log_content  # Patient ID should be masked
            assert '테스트' not in log_content  # Patient name should be masked


@pytest.mark.e2e
@pytest.mark.slow
class TestPerformanceRequirements:
    """Test PRD performance requirements"""
    
    def test_response_time_under_300ms(self):
        """Test single step execution responds within 300ms"""
        
        simple_macro = Macro(name="응답시간 테스트")
        simple_macro.add_step(MouseClickStep(name="클릭", x=100, y=100))
        
        execution_times = []
        
        # Test 100 executions
        with patch('pyautogui.click'):
            from automation.step_executor import StepExecutor
            executor = StepExecutor()
            
            for _ in range(100):
                start = time.time()
                result = executor.execute_step(simple_macro.steps[0], {})
                execution_time = (time.time() - start) * 1000  # Convert to ms
                execution_times.append(execution_time)
                assert result['success'] is True
        
        # Verify performance
        avg_time = sum(execution_times) / len(execution_times)
        max_time = max(execution_times)
        
        assert avg_time < 300  # Average under 300ms
        assert max_time < 500  # Max under 500ms (allowing some variance)
        print(f"Response times - Avg: {avg_time:.1f}ms, Max: {max_time:.1f}ms")
    
    def test_cpu_usage_under_50_percent(self):
        """Test CPU usage stays under 50% during batch processing"""
        
        import psutil
        import threading
        
        # Create CPU-intensive macro
        intensive_macro = Macro(name="CPU 테스트")
        for i in range(10):
            intensive_macro.add_step(KeyboardTypeStep(name=f"입력{i}", text=f"데이터{i}"))
        
        cpu_usage_samples = []
        
        def monitor_cpu():
            """Monitor CPU usage in background"""
            while getattr(monitor_cpu, 'running', True):
                cpu_percent = psutil.cpu_percent(interval=0.1)
                cpu_usage_samples.append(cpu_percent)
                time.sleep(0.1)
        
        # Start CPU monitoring
        monitor_cpu.running = True
        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()
        
        # Execute macro
        with patch('pyautogui.typewrite'):
            from automation.step_executor import StepExecutor
            executor = StepExecutor()
            
            # Execute macro 50 times
            for _ in range(50):
                for step in intensive_macro.steps:
                    executor.execute_step(step, {})
        
        # Stop monitoring
        monitor_cpu.running = False
        monitor_thread.join()
        
        # Analyze CPU usage
        if cpu_usage_samples:
            avg_cpu = sum(cpu_usage_samples) / len(cpu_usage_samples)
            max_cpu = max(cpu_usage_samples)
            
            assert avg_cpu < 50  # Average CPU under 50%
            assert max_cpu < 80  # Max CPU under 80% (allowing spikes)
            print(f"CPU usage - Avg: {avg_cpu:.1f}%, Max: {max_cpu:.1f}%")