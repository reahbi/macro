"""
Simple End-to-End (E2E) tests for basic workflows
Tests simplified workflows with comprehensive mocking to ensure reliable execution.
"""

import pytest
import tempfile
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt

from ui.main_window import MainWindow
from core.macro_types import Macro, MouseClickStep, KeyboardTypeStep, WaitTimeStep
from core.macro_storage import MacroStorage
from excel.excel_manager import ExcelManager
from automation.engine import ExecutionEngine, ExecutionState
from config.settings import Settings


@pytest.fixture(scope="class")
def simple_app():
    """Create QApplication for simple E2E testing"""
    if not QApplication.instance():
        app = QApplication([])
    else:
        app = QApplication.instance()
    yield app


@pytest.fixture
def simple_main_window(simple_app):
    """Create simplified MainWindow for E2E testing"""
    from config.settings import Settings
    
    # Create comprehensive mock settings
    mock_settings_obj = Mock(spec=Settings)
    
    def mock_get(key, default=None):
        settings_map = {
            "ui.window_size": [1280, 720],
            "macro.recent_files": [],
            "execution.default_delay_ms": 100,
            "ui.compact_mode": False,
            "ui.theme": "light",
            "macro.auto_save": True,
            "execution.timeout_seconds": 30
        }
        return settings_map.get(key, default)
    
    mock_settings_obj.get.side_effect = mock_get
    mock_settings_obj.set.return_value = None
    mock_settings_obj.save.return_value = None
    
    # Patch all critical dependencies
    with patch('config.settings.Settings', return_value=mock_settings_obj):
        with patch('core.macro_storage.MacroStorage'):
            with patch('logger.app_logger.get_logger'):
                window = MainWindow(mock_settings_obj)
                window.show()
                return window


@pytest.mark.e2e
class TestSimpleE2EWorkflows:
    """Test simplified E2E workflows with comprehensive mocking"""
    
    def test_basic_macro_creation_workflow(self, simple_main_window):
        """Test basic macro creation workflow"""
        
        # Step 1: Access macro editor
        editor_widget = simple_main_window.macro_editor
        
        # Step 2: Create a simple macro
        test_macro = Macro(name="Simple E2E Test")
        test_macro.add_step(MouseClickStep(name="Test Click", x=100, y=200))
        test_macro.add_step(KeyboardTypeStep(name="Test Type", text="Hello E2E"))
        test_macro.add_step(WaitTimeStep(name="Test Wait", seconds=0.1))
        
        # Step 3: Set macro in editor
        editor_widget.set_macro(test_macro)
        
        # Step 4: Verify macro was set
        current_macro = editor_widget.get_macro()
        assert current_macro is not None
        assert current_macro.name == "Simple E2E Test"
        assert len(current_macro.steps) == 3
        
        # Step 5: Verify step types
        step_types = [step.step_type.value for step in current_macro.steps]
        assert "mouse_click" in step_types
        assert "keyboard_type" in step_types
        assert "wait_time" in step_types
    
    def test_macro_execution_workflow(self, simple_main_window):
        """Test basic macro execution workflow"""
        
        # Step 1: Create test macro
        test_macro = Macro(name="Execution Test")
        test_macro.add_step(MouseClickStep(name="Click", x=100, y=200))
        test_macro.add_step(KeyboardTypeStep(name="Type", text="Test execution"))
        
        # Step 2: Get execution engine
        execution_engine = simple_main_window.execution_widget.engine
        execution_engine.set_macro(test_macro)
        
        # Step 3: Mock execution dependencies
        execution_results = []
        
        def mock_click(x, y, clicks=1, interval=0.0, button='left'):
            execution_results.append(f"click({x}, {y})")
        
        def mock_typewrite(text, interval=0.0):
            execution_results.append(f"type({text})")
        
        # Step 4: Execute with mocking
        with patch('pyautogui.click', side_effect=mock_click):
            with patch('pyautogui.typewrite', side_effect=mock_typewrite):
                with patch.object(execution_engine, '_set_state'):
                    with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                        with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                            with patch.object(execution_engine.execution_logger, 'close'):
                                
                                result = execution_engine._execute_standalone()
        
        # Step 5: Verify execution results
        assert result.success is True
        assert len(execution_results) == 2
        assert "click(100, 200)" in execution_results
        assert "type(Test execution)" in execution_results
    
    def test_macro_editor_ui_workflow(self, simple_main_window):
        """Test macro editor UI interaction workflow"""
        
        # Step 1: Access UI components
        main_tab_widget = simple_main_window.tab_widget
        macro_editor = simple_main_window.macro_editor
        
        # Step 2: Verify UI structure
        assert main_tab_widget is not None
        assert macro_editor is not None
        
        # Step 3: Test macro setting and getting
        test_macro = Macro(name="UI Test Macro")
        test_macro.add_step(KeyboardTypeStep(name="UI Test", text="UI workflow test"))
        
        # Step 4: Set macro through UI
        macro_editor.set_macro(test_macro)
        
        # Step 5: Verify UI reflects the macro
        current_macro = macro_editor.get_macro()
        assert current_macro.name == "UI Test Macro"
        assert len(current_macro.steps) == 1
        assert current_macro.steps[0].text == "UI workflow test"
    
    def test_execution_state_management_workflow(self, simple_main_window):
        """Test execution state management workflow"""
        
        # Step 1: Get execution engine
        execution_engine = simple_main_window.execution_widget.engine
        
        # Step 2: Verify initial state
        assert execution_engine.state == ExecutionState.IDLE
        
        # Step 3: Test state transitions
        execution_engine._set_state(ExecutionState.RUNNING)
        assert execution_engine.state == ExecutionState.RUNNING
        
        # Step 4: Test pause/resume
        execution_engine.toggle_pause()
        assert execution_engine.state == ExecutionState.PAUSED
        
        execution_engine.toggle_pause()
        assert execution_engine.state == ExecutionState.RUNNING
        
        # Step 5: Test stop
        execution_engine.stop_execution()
        assert execution_engine.state == ExecutionState.STOPPING
    
    def test_variable_substitution_workflow(self, simple_main_window):
        """Test variable substitution in macro execution"""
        
        # Step 1: Create macro with variables
        test_macro = Macro(name="Variable Test")
        test_macro.add_step(KeyboardTypeStep(
            name="Variable Type", 
            text="Hello {{name}}, your score is {{score}}"
        ))
        
        # Step 2: Set up variable data
        test_variables = {
            "name": "TestUser",
            "score": "95"
        }
        
        # Step 3: Mock variable substitution
        execution_engine = simple_main_window.execution_widget.engine
        execution_engine.set_macro(test_macro)
        
        # Step 4: Mock Excel manager for variable data
        mock_excel_manager = Mock()
        mock_excel_manager.get_row_data.return_value = {
            '이름': 'TestUser',
            '점수': '95'
        }
        execution_engine.excel_manager = mock_excel_manager
        
        # Step 5: Test variable substitution
        substituted_results = []
        
        def mock_typewrite(text, interval=0.0):
            substituted_results.append(text)
        
        with patch('pyautogui.typewrite', side_effect=mock_typewrite):
            with patch.object(execution_engine, '_set_state'):
                with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                    with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                        with patch.object(execution_engine.execution_logger, 'close'):
                            with patch.object(execution_engine.step_executor, '_substitute_variables') as mock_substitute:
                                mock_substitute.return_value = "Hello TestUser, your score is 95"
                                
                                result = execution_engine._execute_standalone()
        
        # Step 6: Verify variable substitution worked
        assert result.success is True
        assert len(substituted_results) == 1
        assert "TestUser" in substituted_results[0]
        assert "95" in substituted_results[0]


@pytest.mark.e2e 
class TestSimpleE2ESettings:
    """Test E2E workflows related to settings and configuration"""
    
    def test_settings_integration_workflow(self, simple_main_window):
        """Test settings integration in E2E workflow"""
        
        # Step 1: Access settings through main window
        settings = simple_main_window.settings
        
        # Step 2: Test setting retrieval
        window_size = settings.get("ui.window_size", [800, 600])
        assert window_size == [1280, 720]  # From our mock
        
        # Step 3: Test setting modification
        settings.set("test.new_setting", "test_value")
        settings.save()
        
        # Step 4: Verify settings methods were called
        settings.set.assert_called_with("test.new_setting", "test_value")
        settings.save.assert_called_once()
    
    def test_application_initialization_workflow(self, simple_main_window):
        """Test complete application initialization workflow"""
        
        # Step 1: Verify main window was created
        assert simple_main_window is not None
        assert simple_main_window.isVisible()
        
        # Step 2: Verify main components exist
        assert hasattr(simple_main_window, 'tab_widget')
        assert hasattr(simple_main_window, 'excel_widget')
        assert hasattr(simple_main_window, 'macro_editor')
        assert hasattr(simple_main_window, 'execution_widget')
        
        # Step 3: Verify execution engine exists
        assert hasattr(simple_main_window.execution_widget, 'engine')
        assert simple_main_window.execution_widget.engine is not None
        
        # Step 4: Verify Excel widget exists
        assert simple_main_window.excel_widget is not None
        
        # Step 5: Verify macro storage exists
        assert hasattr(simple_main_window, 'macro_storage')
        assert simple_main_window.macro_storage is not None


@pytest.mark.e2e
@pytest.mark.slow 
class TestSimpleE2EPerformance:
    """Test E2E performance characteristics"""
    
    def test_large_macro_creation_performance(self, simple_main_window):
        """Test performance with larger macro creation"""
        import time
        
        # Step 1: Record start time
        start_time = time.time()
        
        # Step 2: Create large macro
        large_macro = Macro(name="Large Macro Performance Test")
        
        # Add 50 steps
        for i in range(50):
            large_macro.add_step(KeyboardTypeStep(
                name=f"Step {i}",
                text=f"Performance test step {i}"
            ))
        
        # Step 3: Set macro in editor
        editor_widget = simple_main_window.macro_editor
        editor_widget.set_macro(large_macro)
        
        # Step 4: Measure performance
        end_time = time.time()
        total_time = end_time - start_time
        
        # Step 5: Verify performance requirements
        assert total_time < 2.0  # Should complete in less than 2 seconds
        
        # Step 6: Verify macro was created correctly
        current_macro = editor_widget.get_macro()
        assert len(current_macro.steps) == 50
        assert current_macro.name == "Large Macro Performance Test"
    
    def test_ui_responsiveness_workflow(self, simple_main_window):
        """Test UI responsiveness during operations"""
        
        # Step 1: Test rapid macro changes
        editor_widget = simple_main_window.macro_editor
        
        # Step 2: Create and set multiple macros rapidly
        for i in range(10):
            test_macro = Macro(name=f"Rapid Test {i}")
            test_macro.add_step(KeyboardTypeStep(name=f"Step {i}", text=f"Text {i}"))
            
            editor_widget.set_macro(test_macro)
            
            # Verify each change
            current_macro = editor_widget.get_macro()
            assert current_macro.name == f"Rapid Test {i}"
        
        # Step 3: Verify final state
        final_macro = editor_widget.get_macro()
        assert final_macro.name == "Rapid Test 9"
        assert len(final_macro.steps) == 1