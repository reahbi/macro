"""
Integration tests for Engine-Executor integration
Tests the interaction between ExecutionEngine and StepExecutor with real macro execution flows.
"""

import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock, call
from PyQt5.QtCore import QThread, pyqtSignal

from automation.engine import ExecutionEngine, ExecutionState, ExecutionResult
from automation.executor import StepExecutor
from core.macro_types import (
    Macro, MouseClickStep, KeyboardTypeStep, WaitTimeStep, ImageSearchStep, 
    TextSearchStep, IfConditionStep, ErrorHandling
)
from config.settings import Settings
from excel.excel_manager import ExcelManager


@pytest.mark.integration
class TestEngineExecutorBasicIntegration:
    """Test basic integration between ExecutionEngine and StepExecutor"""
    
    @pytest.fixture
    def mock_settings(self):
        """Create mock settings"""
        settings = Mock(spec=Settings)
        settings.get.return_value = 100  # Default delay
        return settings
    
    @pytest.fixture
    def execution_engine(self, mock_settings):
        """Create ExecutionEngine for testing"""
        with patch('automation.hotkey_listener.HotkeyListener'):
            with patch('logger.execution_logger.get_execution_logger'):
                engine = ExecutionEngine(mock_settings)
                return engine
    
    @pytest.fixture
    def step_executor(self, mock_settings):
        """Create StepExecutor for testing"""
        with patch('automation.executor.TextExtractor') as mock_text_extractor:
            # Mock the TextExtractor to avoid EasyOCR initialization
            mock_instance = Mock()
            mock_text_extractor.return_value = mock_instance
            
            executor = StepExecutor(mock_settings)
            return executor
    
    @pytest.fixture
    def simple_macro(self):
        """Create simple macro for testing"""
        macro = Macro(name="Engine Test Macro")
        macro.add_step(MouseClickStep(name="Test Click", x=100, y=200))
        macro.add_step(KeyboardTypeStep(name="Test Type", text="Hello World"))
        macro.add_step(WaitTimeStep(name="Test Wait", seconds=0.1))
        return macro
    
    def test_engine_executor_initialization(self, execution_engine, mock_settings):
        """Test that engine properly initializes with executor"""
        assert execution_engine.step_executor is not None
        assert isinstance(execution_engine.step_executor, StepExecutor)
        assert execution_engine.step_executor.settings == mock_settings
    
    def test_macro_validation_before_execution(self, execution_engine, simple_macro):
        """Test that engine validates macro before execution"""
        # Valid macro should pass
        execution_engine.set_macro(simple_macro)
        assert execution_engine.macro == simple_macro
        
        # Invalid macro should raise error
        invalid_macro = Macro(name="Invalid Macro")
        invalid_macro.add_step(WaitTimeStep(name="Invalid Wait", seconds=-1))  # Invalid
        
        with pytest.raises(ValueError, match="Macro validation failed"):
            execution_engine.set_macro(invalid_macro)
    
    @patch('pyautogui.click')
    @patch('pyautogui.typewrite')
    @patch('time.sleep')
    def test_step_execution_flow(self, mock_sleep, mock_typewrite, mock_click, 
                                execution_engine, simple_macro):
        """Test that engine properly executes steps through executor"""
        execution_engine.set_macro(simple_macro)
        
        # Mock execution state and logging
        with patch.object(execution_engine, '_set_state'):
            with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                with patch.object(execution_engine.execution_logger, 'log_row_start'):
                    with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                        with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                            with patch.object(execution_engine.execution_logger, 'close'):
                                
                                # Execute in standalone mode
                                result = execution_engine._execute_standalone()
                                
                                # Verify all steps were executed
                                mock_click.assert_called_once_with(x=100, y=200, clicks=1, interval=0.0, button='left')
                                mock_typewrite.assert_called_once_with("Hello World", interval=0.0)
                                mock_sleep.assert_called_once_with(0.1)
                                
                                # Verify successful result
                                assert result.success is True
                                assert result.error is None
    
    def test_variable_substitution_integration(self, execution_engine):
        """Test variable substitution between engine and executor"""
        # Create macro with variable substitution
        macro = Macro(name="Variable Test")
        macro.add_step(KeyboardTypeStep(
            name="Variable Type", 
            text="Hello {{name}}, you are {{age}} years old"
        ))
        
        execution_engine.set_macro(macro)
        
        # Mock Excel manager with variables
        mock_excel_manager = Mock()
        mock_excel_manager.get_mapped_data.return_value = {
            "name": "김철수",
            "age": "30"
        }
        execution_engine.excel_manager = mock_excel_manager
        
        # Mock pyautogui
        with patch('pyautogui.typewrite') as mock_typewrite:
            with patch.object(execution_engine, '_set_state'):
                with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                    with patch.object(execution_engine.execution_logger, 'log_row_start'):
                        with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                            with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                with patch.object(execution_engine.execution_logger, 'close'):
                                    
                                    # Execute for specific row
                                    result = execution_engine._execute_row(0)
                                    
                                    # Verify variable substitution occurred
                                    mock_typewrite.assert_called_once_with(
                                        "Hello 김철수, you are 30 years old", 
                                        interval=0.0
                                    )
                                    assert result.success is True


@pytest.mark.integration
class TestErrorHandlingIntegration:
    """Test error handling integration between engine and executor"""
    
    @pytest.fixture
    def execution_engine(self, mock_settings):
        """Create ExecutionEngine for testing"""
        with patch('automation.hotkey_listener.HotkeyListener'):
            with patch('logger.execution_logger.get_execution_logger'):
                engine = ExecutionEngine(mock_settings)
                return engine
    
    def test_step_error_stop_strategy(self, execution_engine):
        """Test STOP error handling strategy"""
        # Create macro with step that will fail
        macro = Macro(name="Error Stop Test")
        macro.add_step(MouseClickStep(name="Good Click", x=100, y=200))
        failing_step = KeyboardTypeStep(name="Failing Type", text="test")
        failing_step.error_handling = ErrorHandling.STOP
        macro.add_step(failing_step)
        macro.add_step(MouseClickStep(name="Should Not Execute", x=300, y=400))
        
        execution_engine.set_macro(macro)
        
        # Mock successful first step and failing second step
        with patch('pyautogui.click') as mock_click:
            with patch('pyautogui.typewrite', side_effect=Exception("Keyboard error")):
                with patch.object(execution_engine, '_set_state'):
                    with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                        with patch.object(execution_engine.execution_logger, 'log_row_start'):
                            with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                                with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                    with patch.object(execution_engine.execution_logger, 'close'):
                                        
                                        result = execution_engine._execute_standalone()
                                        
                                        # First step should execute
                                        mock_click.assert_called_once()
                                        
                                        # Execution should stop after error
                                        assert result.success is False
                                        assert "Keyboard error" in result.error
    
    def test_step_error_continue_strategy(self, execution_engine):
        """Test CONTINUE error handling strategy"""
        # Create macro with failing step that should continue
        macro = Macro(name="Error Continue Test")
        macro.add_step(MouseClickStep(name="Good Click 1", x=100, y=200))
        failing_step = KeyboardTypeStep(name="Failing Type", text="test")
        failing_step.error_handling = ErrorHandling.CONTINUE
        macro.add_step(failing_step)
        macro.add_step(MouseClickStep(name="Good Click 2", x=300, y=400))
        
        execution_engine.set_macro(macro)
        
        # Mock steps: success, failure, success
        click_calls = []
        def mock_click(**kwargs):
            click_calls.append(kwargs)
        
        with patch('pyautogui.click', side_effect=mock_click):
            with patch('pyautogui.typewrite', side_effect=Exception("Keyboard error")):
                with patch.object(execution_engine, '_set_state'):
                    with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                        with patch.object(execution_engine.execution_logger, 'log_row_start'):
                            with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                                with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                    with patch.object(execution_engine.execution_logger, 'close'):
                                        
                                        result = execution_engine._execute_standalone()
                                        
                                        # Both click steps should execute despite middle failure
                                        assert len(click_calls) == 2
                                        assert click_calls[0]['x'] == 100
                                        assert click_calls[1]['x'] == 300
                                        
                                        # Overall execution should succeed
                                        assert result.success is True
    
    def test_step_error_retry_strategy(self, execution_engine):
        """Test RETRY error handling strategy"""
        # Create macro with retry step
        macro = Macro(name="Error Retry Test")
        retry_step = KeyboardTypeStep(name="Retry Type", text="test")
        retry_step.error_handling = ErrorHandling.RETRY
        retry_step.retry_count = 2
        macro.add_step(retry_step)
        
        execution_engine.set_macro(macro)
        
        # Mock typewrite to fail twice then succeed
        typewrite_calls = []
        def mock_typewrite_with_retries(text, **kwargs):
            typewrite_calls.append(text)
            if len(typewrite_calls) <= 2:  # Fail first 2 attempts
                raise Exception("Retry error")
            # Succeed on 3rd attempt
            return None
        
        with patch('pyautogui.typewrite', side_effect=mock_typewrite_with_retries):
            with patch('time.sleep'):  # Mock retry delay
                with patch.object(execution_engine, '_set_state'):
                    with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                        with patch.object(execution_engine.execution_logger, 'log_row_start'):
                            with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                                with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                    with patch.object(execution_engine.execution_logger, 'close'):
                                        
                                        result = execution_engine._execute_standalone()
                                        
                                        # Should have retried and eventually succeeded
                                        assert len(typewrite_calls) == 3
                                        assert result.success is True


@pytest.mark.integration
class TestAdvancedStepIntegration:
    """Test integration of advanced step types (conditions, loops, vision)"""
    
    @pytest.fixture
    def execution_engine(self, mock_settings):
        """Create ExecutionEngine for testing"""
        with patch('automation.hotkey_listener.HotkeyListener'):
            with patch('logger.execution_logger.get_execution_logger'):
                engine = ExecutionEngine(mock_settings)
                return engine
    
    def test_conditional_step_integration(self, execution_engine, mock_vision_systems):
        """Test conditional step execution integration"""
        # Create macro with conditional step
        macro = Macro(name="Conditional Test")
        
        condition_step = IfConditionStep(
            name="Image Condition",
            condition_type="image_exists",
            condition_value={"image_path": "button.png", "confidence": 0.9}
        )
        
        # Add steps to true branch
        true_step = MouseClickStep(name="True Click", x=100, y=200)
        condition_step.true_steps = [true_step]
        
        # Add steps to false branch
        false_step = KeyboardTypeStep(name="False Type", text="not found")
        condition_step.false_steps = [false_step]
        
        macro.add_step(condition_step)
        execution_engine.set_macro(macro)
        
        # Mock image matching to return True
        mock_vision_systems['image_matcher'].find_image.return_value.found = True
        
        with patch('pyautogui.click') as mock_click:
            with patch('pyautogui.typewrite') as mock_typewrite:
                with patch.object(execution_engine, '_set_state'):
                    with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                        with patch.object(execution_engine.execution_logger, 'log_row_start'):
                            with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                                with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                    with patch.object(execution_engine.execution_logger, 'close'):
                                        
                                        result = execution_engine._execute_standalone()
                                        
                                        # True branch should execute
                                        mock_click.assert_called_once_with(x=100, y=200, clicks=1, button='left')
                                        mock_typewrite.assert_not_called()
                                        
                                        assert result.success is True
    
    def test_image_search_integration(self, execution_engine, mock_vision_systems):
        """Test image search step integration"""
        # Create macro with image search
        macro = Macro(name="Image Search Test")
        image_step = ImageSearchStep(
            name="Find Button",
            image_path="search_button.png",
            confidence=0.8,
            click_after_find=True,
            click_offset=(10, 5)
        )
        macro.add_step(image_step)
        
        execution_engine.set_macro(macro)
        
        # Mock image matcher to find image at specific location
        from dataclasses import dataclass
        
        @dataclass
        class MockMatchResult:
            found: bool = True
            confidence: float = 0.85
            center: tuple = (200, 300)
        
        mock_vision_systems['image_matcher'].find_image.return_value = MockMatchResult()
        
        with patch('pyautogui.click') as mock_click:
            with patch.object(execution_engine, '_set_state'):
                with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                    with patch.object(execution_engine.execution_logger, 'log_row_start'):
                        with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                            with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                with patch.object(execution_engine.execution_logger, 'close'):
                                    
                                    result = execution_engine._execute_standalone()
                                    
                                    # Should click at found location plus offset
                                    mock_click.assert_called_once_with(x=210, y=305, clicks=1, button='left')
                                    assert result.success is True
    
    def test_text_search_integration(self, execution_engine, mock_vision_systems):
        """Test OCR text search step integration"""
        # Create macro with text search
        macro = Macro(name="Text Search Test")
        text_step = TextSearchStep(
            name="Find Text",
            search_text="Login",
            click_after_find=True,
            double_click=True
        )
        macro.add_step(text_step)
        
        execution_engine.set_macro(macro)
        
        # Mock text extractor to find text
        from dataclasses import dataclass
        
        @dataclass
        class MockTextResult:
            text: str = "Login"
            confidence: float = 0.9
            center: tuple = (150, 250)
        
        mock_vision_systems['text_extractor'].find_text.return_value = MockTextResult()
        
        with patch('pyautogui.doubleClick') as mock_double_click:
            with patch.object(execution_engine, '_set_state'):
                with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                    with patch.object(execution_engine.execution_logger, 'log_row_start'):
                        with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                            with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                with patch.object(execution_engine.execution_logger, 'close'):
                                    
                                    result = execution_engine._execute_standalone()
                                    
                                    # Should double-click at found text location
                                    mock_double_click.assert_called_once_with(x=150, y=250)
                                    assert result.success is True


@pytest.mark.integration
class TestExecutionStateManagement:
    """Test execution state management and thread safety"""
    
    @pytest.fixture
    def execution_engine(self, mock_settings):
        """Create ExecutionEngine for testing"""
        with patch('automation.hotkey_listener.HotkeyListener'):
            with patch('logger.execution_logger.get_execution_logger'):
                engine = ExecutionEngine(mock_settings)
                return engine
    
    def test_state_transitions_during_execution(self, execution_engine):
        """Test proper state transitions during execution"""
        macro = Macro(name="State Test")
        macro.add_step(WaitTimeStep(name="Long Wait", seconds=0.1))
        
        execution_engine.set_macro(macro)
        
        state_changes = []
        def track_state_change(state):
            state_changes.append(state)
        
        execution_engine.stateChanged.connect(track_state_change)
        
        # Mock execution components
        with patch('time.sleep'):
            with patch.object(execution_engine, '_set_state', side_effect=execution_engine._set_state) as mock_set_state:
                with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                    with patch.object(execution_engine.execution_logger, 'log_row_start'):
                        with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                            with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                with patch.object(execution_engine.execution_logger, 'close'):
                                    
                                    result = execution_engine._execute_standalone()
                                    
                                    # Verify state was set to RUNNING and back to IDLE
                                    state_calls = [call[0][0] for call in mock_set_state.call_args_list]
                                    assert ExecutionState.RUNNING in state_calls
                                    assert ExecutionState.IDLE in state_calls
    
    def test_pause_resume_integration(self, execution_engine):
        """Test pause/resume functionality integration"""
        macro = Macro(name="Pause Test")
        macro.add_step(WaitTimeStep(name="Wait 1", seconds=0.1))
        macro.add_step(WaitTimeStep(name="Wait 2", seconds=0.1))
        
        execution_engine.set_macro(macro)
        
        # Test pause/resume state management
        assert execution_engine.state == ExecutionState.IDLE
        
        # Simulate running state
        execution_engine._set_state(ExecutionState.RUNNING)
        assert execution_engine.state == ExecutionState.RUNNING
        
        # Test pause
        execution_engine.toggle_pause()
        assert execution_engine.state == ExecutionState.PAUSED
        assert not execution_engine._pause_event.is_set()
        
        # Test resume
        execution_engine.toggle_pause()
        assert execution_engine.state == ExecutionState.RUNNING
        assert execution_engine._pause_event.is_set()
    
    def test_stop_execution_integration(self, execution_engine):
        """Test stop execution functionality"""
        macro = Macro(name="Stop Test")
        macro.add_step(WaitTimeStep(name="Long Wait", seconds=1.0))
        
        execution_engine.set_macro(macro)
        
        # Set to running state
        execution_engine._set_state(ExecutionState.RUNNING)
        
        # Test stop
        execution_engine.stop_execution()
        assert execution_engine.state == ExecutionState.STOPPING
        assert execution_engine._pause_event.is_set()  # Should resume if paused
    
    def test_thread_safety_during_execution(self, execution_engine):
        """Test thread safety of state management"""
        macro = Macro(name="Thread Safety Test")
        macro.add_step(WaitTimeStep(name="Wait", seconds=0.1))
        
        execution_engine.set_macro(macro)
        
        # Test concurrent state access
        states_accessed = []
        
        def access_state():
            for _ in range(10):
                state = execution_engine.state
                states_accessed.append(state)
                time.sleep(0.01)
        
        # Start multiple threads accessing state
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=access_state)
            threads.append(thread)
            thread.start()
        
        # Change state during concurrent access
        execution_engine._set_state(ExecutionState.RUNNING)
        execution_engine._set_state(ExecutionState.PAUSED)
        execution_engine._set_state(ExecutionState.IDLE)
        
        # Wait for threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no exceptions and states were accessed
        assert len(states_accessed) == 30  # 3 threads * 10 accesses each
        assert all(isinstance(state, ExecutionState) for state in states_accessed)


@pytest.mark.integration
class TestLoggingIntegration:
    """Test integration with execution logging system"""
    
    @pytest.fixture
    def execution_engine(self, mock_settings):
        """Create ExecutionEngine for testing"""
        with patch('automation.hotkey_listener.HotkeyListener'):
            mock_logger = Mock()
            with patch('logger.execution_logger.get_execution_logger', return_value=mock_logger):
                engine = ExecutionEngine(mock_settings)
                engine.execution_logger = mock_logger
                return engine
    
    def test_execution_logging_flow(self, execution_engine):
        """Test complete execution logging flow"""
        macro = Macro(name="Logging Test")
        macro.add_step(MouseClickStep(name="Log Click", x=100, y=200))
        macro.add_step(KeyboardTypeStep(name="Log Type", text="test"))
        
        execution_engine.set_macro(macro)
        
        # Mock all step executions
        with patch('pyautogui.click'):
            with patch('pyautogui.typewrite'):
                with patch.object(execution_engine, '_set_state'):
                    result = execution_engine._execute_standalone()
                    
                    # Verify logging calls
                    logger = execution_engine.execution_logger
                    
                    # Session should be started
                    logger.start_session.assert_called_once_with(macro.name, "Unknown")
                    
                    # Row execution should be logged
                    logger.log_row_start.assert_called_once_with(0, {})
                    logger.log_row_complete.assert_called_once()
                    
                    # Step executions should be logged
                    assert logger.log_step_execution.call_count == 2
                    
                    # Session should be closed
                    logger.close.assert_called_once()
    
    def test_error_logging_integration(self, execution_engine):
        """Test error logging integration"""
        macro = Macro(name="Error Logging Test")
        macro.add_step(KeyboardTypeStep(name="Failing Step", text="test"))
        
        execution_engine.set_macro(macro)
        
        # Mock step to fail
        with patch('pyautogui.typewrite', side_effect=Exception("Test error")):
            with patch.object(execution_engine, '_set_state'):
                result = execution_engine._execute_standalone()
                
                # Verify error was logged
                logger = execution_engine.execution_logger
                
                # Row should be marked as failed
                logger.log_row_complete.assert_called_once()
                call_args = logger.log_row_complete.call_args
                assert call_args[0][1] is False  # success=False
                assert "Test error" in call_args[0][3]  # error message
                
                # Step should be logged as failed
                step_log_calls = logger.log_step_execution.call_args_list
                assert len(step_log_calls) == 1
                step_call = step_log_calls[0]
                assert step_call[0][4] is False  # success=False
                assert "Test error" in step_call[0][6]  # error message


@pytest.mark.integration
@pytest.mark.slow
class TestPerformanceIntegration:
    """Test performance aspects of engine-executor integration"""
    
    @pytest.fixture
    def execution_engine(self, mock_settings):
        """Create ExecutionEngine for testing"""
        with patch('automation.hotkey_listener.HotkeyListener'):
            with patch('logger.execution_logger.get_execution_logger'):
                engine = ExecutionEngine(mock_settings)
                return engine
    
    def test_large_macro_execution_performance(self, execution_engine):
        """Test performance with large macros"""
        import time
        
        # Create large macro
        large_macro = Macro(name="Large Performance Test")
        for i in range(50):  # 50 steps
            if i % 2 == 0:
                step = MouseClickStep(name=f"Click {i}", x=i*10, y=i*10)
            else:
                step = WaitTimeStep(name=f"Wait {i}", seconds=0.001)  # Very short wait
            large_macro.add_step(step)
        
        execution_engine.set_macro(large_macro)
        
        # Mock all operations to be instant
        with patch('pyautogui.click'):
            with patch('time.sleep'):
                with patch.object(execution_engine, '_set_state'):
                    with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                        with patch.object(execution_engine.execution_logger, 'log_row_start'):
                            with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                                with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                    with patch.object(execution_engine.execution_logger, 'close'):
                                        
                                        start_time = time.time()
                                        result = execution_engine._execute_standalone()
                                        execution_time = time.time() - start_time
                                        
                                        # Should complete within reasonable time (< 1 second)
                                        assert execution_time < 1.0, f"Large macro execution too slow: {execution_time:.3f}s"
                                        assert result.success is True
    
    def test_concurrent_execution_attempts(self, execution_engine):
        """Test handling of concurrent execution attempts"""
        macro = Macro(name="Concurrent Test")
        macro.add_step(WaitTimeStep(name="Wait", seconds=0.1))
        
        execution_engine.set_macro(macro)
        
        # Try to set macro while in different states
        execution_engine._set_state(ExecutionState.RUNNING)
        
        with pytest.raises(RuntimeError, match="Cannot set macro while execution is active"):
            execution_engine.set_macro(macro)
        
        # Reset to idle
        execution_engine._set_state(ExecutionState.IDLE)
        
        # Should work now
        execution_engine.set_macro(macro)
        assert execution_engine.macro == macro
    
    def test_memory_usage_during_execution(self, execution_engine):
        """Test memory efficiency during execution"""
        # Create macro with variable substitution
        macro = Macro(name="Memory Test")
        for i in range(20):
            step = KeyboardTypeStep(
                name=f"Type {i}",
                text=f"Variable text {{var_{i}}} with content {i}"
            )
            macro.add_step(step)
        
        execution_engine.set_macro(macro)
        
        # Mock Excel manager with large variable data
        mock_excel_manager = Mock()
        large_data = {f"var_{i}": f"Large content string {i} " * 100 for i in range(20)}
        mock_excel_manager.get_mapped_data.return_value = large_data
        execution_engine.excel_manager = mock_excel_manager
        
        # Execute and verify no memory issues
        with patch('pyautogui.typewrite'):
            with patch.object(execution_engine, '_set_state'):
                with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                    with patch.object(execution_engine.execution_logger, 'log_row_start'):
                        with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                            with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                with patch.object(execution_engine.execution_logger, 'close'):
                                    
                                    result = execution_engine._execute_row(0)
                                    
                                    # Should complete successfully without memory issues
                                    assert result.success is True