#!/usr/bin/env python3
"""
Integration tests for macro execution and pause/resume functionality
"""

import sys
import os
from pathlib import Path
import pytest
import tempfile
import time
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtTest import QTest

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_helpers import GUITestContext
from automation.engine import ExecutionEngine, ExecutionState
from excel.excel_manager import ExcelManager
from core.macro_types import (
    Macro, MacroStep, StepType, KeyboardTypeStep, 
    MouseClickStep, WaitTimeStep, IfConditionStep, MouseButton
)
from ui.widgets.execution_widget import ExecutionControlWidget
from config.settings import Settings


class TestMacroExecution:
    """Test macro execution and control functionality"""
    
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
    def simple_macro(self):
        """Create a simple test macro"""
        macro = Macro(name="테스트 실행 매크로")
        
        # Add a few simple steps
        wait_step = WaitTimeStep()
        wait_step.name = "시작 대기"
        wait_step.seconds = 0.1  # Short wait for testing
        macro.add_step(wait_step)
        
        type_step = KeyboardTypeStep()
        type_step.name = "텍스트 입력"
        type_step.text = "Hello {{name}}"
        macro.add_step(type_step)
        
        wait_step2 = WaitTimeStep()
        wait_step2.name = "종료 대기"
        wait_step2.seconds = 0.1
        macro.add_step(wait_step2)
        
        return macro
        
    @pytest.fixture
    def complex_macro(self):
        """Create a macro with conditional logic"""
        macro = Macro(name="복잡한 매크로")
        
        # Conditional step
        condition_step = IfConditionStep()
        condition_step.name = "조건 확인"
        condition_step.condition_type = "variable_equals"
        condition_step.condition_value = {
            "variable": "mode",
            "compare_value": "auto"
        }
        
        # True branch
        true_type = KeyboardTypeStep()
        true_type.name = "자동 모드"
        true_type.text = "자동 실행 중..."
        condition_step.true_steps = [true_type]
        
        # False branch
        false_type = KeyboardTypeStep()
        false_type.name = "수동 모드"
        false_type.text = "수동 실행 중..."
        condition_step.false_steps = [false_type]
        
        macro.add_step(condition_step)
        
        return macro
        
    @pytest.fixture
    def test_excel_manager(self):
        """Create test Excel manager with dummy data"""
        # Create temporary Excel file
        temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
        
        import pandas as pd
        data = pd.DataFrame({
            '이름': ['테스트1', '테스트2', '테스트3'],
            '상태': ['', '', ''],
            'Status': ['', '', '']
        })
        
        data.to_excel(temp_file.name, index=False)
        temp_file.close()
        
        manager = ExcelManager()
        manager.load_file(temp_file.name)
        manager.read_sheet('Sheet1')
        
        yield manager
        
        # Cleanup
        os.unlink(temp_file.name)
        
    def test_basic_execution(self, app, settings, simple_macro, test_excel_manager):
        """Test basic macro execution"""
        with GUITestContext(app) as ctx:
            engine = ExecutionEngine(settings)
            
            # Set macro and excel manager
            engine.set_macro(simple_macro, test_excel_manager)
            
            # Set variables
            engine.step_executor.set_variables({'name': '테스터'})
            
            # Track state changes
            state_changes = []
            
            def on_state_changed(state):
                state_changes.append(state)
                
            engine.stateChanged.connect(on_state_changed)
            
            # Start execution
            engine.start()
            
            # Wait for completion
            timeout = 2000
            start_time = time.time()
            while engine.state not in [ExecutionState.IDLE, ExecutionState.STOPPED]:
                if (time.time() - start_time) * 1000 > timeout:
                    engine.stop_execution()
                    break
                QTest.qWait(100)
                
            # Verify execution states
            assert ExecutionState.RUNNING in state_changes
            
    def test_pause_resume(self, app, settings, simple_macro, test_excel_manager):
        """Test pause and resume functionality"""
        with GUITestContext(app) as ctx:
            engine = ExecutionEngine(settings)
            
            # Set longer wait steps for pause testing
            simple_macro.steps[0].seconds = 0.5
            simple_macro.steps[2].seconds = 0.5
            
            engine.set_macro(simple_macro, test_excel_manager)
            
            # Track states
            states = []
            
            def on_state_changed(state):
                states.append(state)
                
            engine.stateChanged.connect(on_state_changed)
            
            # Start execution
            engine.start()
            
            # Pause after a short delay
            QTimer.singleShot(200, engine.toggle_pause)
            
            # Resume after another delay
            QTimer.singleShot(400, engine.toggle_pause)
            
            # Wait for completion
            timeout = 3000
            start_time = time.time()
            while engine.state not in [ExecutionState.IDLE, ExecutionState.STOPPED]:
                if (time.time() - start_time) * 1000 > timeout:
                    engine.stop_execution()
                    break
                QTest.qWait(100)
                
            # Verify states changed
            assert ExecutionState.RUNNING in states
            assert ExecutionState.PAUSED in states
            
    def test_stop_execution(self, app, settings, simple_macro, test_excel_manager):
        """Test stopping execution"""
        with GUITestContext(app) as ctx:
            engine = ExecutionEngine(settings)
            
            # Set longer wait for stop testing
            simple_macro.steps[0].seconds = 2.0
            
            engine.set_macro(simple_macro, test_excel_manager)
            
            # Track completion
            finished = False
            
            def on_finished():
                nonlocal finished
                finished = True
                
            engine.executionFinished.connect(on_finished)
            
            # Start execution
            engine.start()
            
            # Stop after a short delay
            QTimer.singleShot(200, engine.stop_execution)
            
            # Wait briefly
            QTest.qWait(500)
            
            # Verify stopped
            assert engine.state in [ExecutionState.STOPPED, ExecutionState.IDLE]
            assert finished  # Should emit finished signal
            
    def test_variable_substitution(self, app, settings, test_excel_manager):
        """Test variable substitution during execution"""
        with GUITestContext(app) as ctx:
            engine = ExecutionEngine(settings)
            
            # Create macro with variables
            macro = Macro(name="변수 테스트")
            
            type_step = KeyboardTypeStep()
            type_step.text = "이름: {{name}}, 나이: {{age}}"
            macro.add_step(type_step)
            
            engine.set_macro(macro, test_excel_manager)
            
            # Set variables
            engine.step_executor.set_variables({
                'name': '홍길동',
                'age': 25
            })
            
            # Execute
            engine.start()
            
            # Wait for completion
            timeout = 1000
            start_time = time.time()
            while engine.state not in [ExecutionState.IDLE, ExecutionState.STOPPED]:
                if (time.time() - start_time) * 1000 > timeout:
                    engine.stop_execution()
                    break
                QTest.qWait(100)
                
            # Execution should complete without errors
            
    def test_conditional_execution(self, app, settings, complex_macro, test_excel_manager):
        """Test conditional step execution"""
        with GUITestContext(app) as ctx:
            engine = ExecutionEngine(settings)
            
            # Test true branch
            engine.set_macro(complex_macro, test_excel_manager)
            engine.step_executor.set_variables({'mode': 'auto'})
            
            # Track executed steps
            executed_steps = []
            
            def on_step_executing(step, row_index):
                executed_steps.append(step.name)
                
            engine.stepExecuting.connect(on_step_executing)
            
            # Execute
            engine.start()
            
            # Wait for completion
            while engine.state not in [ExecutionState.IDLE, ExecutionState.STOPPED]:
                QTest.qWait(100)
                
            # Should have executed conditional branch
            # The exact steps depend on how the execution engine handles nested steps
            
    def test_error_handling(self, app, settings, test_excel_manager):
        """Test error handling during execution"""
        with GUITestContext(app) as ctx:
            engine = ExecutionEngine(settings)
            
            # Create macro with invalid step
            macro = Macro(name="에러 테스트")
            
            # Add a wait step (valid steps are needed for a macro)
            wait_step = WaitTimeStep()
            wait_step.seconds = 0.1
            macro.add_step(wait_step)
            
            engine.set_macro(macro, test_excel_manager)
            
            # Track errors
            errors = []
            
            def on_error(error_msg):
                errors.append(error_msg)
                
            engine.error.connect(on_error)
            
            # Execute
            engine.start()
            
            # Wait for completion
            timeout = 1000
            start_time = time.time()
            while engine.state not in [ExecutionState.IDLE, ExecutionState.STOPPED]:
                if (time.time() - start_time) * 1000 > timeout:
                    engine.stop_execution()
                    break
                QTest.qWait(100)
                
            # Should execute without major errors
            
    def test_execution_control_widget(self, app, settings, simple_macro, test_excel_manager):
        """Test execution control widget"""
        with GUITestContext(app) as ctx:
            control = ExecutionControlWidget()
            control.show()
            
            # Initialize with engine
            engine = ExecutionEngine(settings)
            engine.set_macro(simple_macro, test_excel_manager)
            control.set_engine(engine)
            
            # Verify initial state
            assert control.play_button.isEnabled()
            assert not control.pause_button.isEnabled()
            assert not control.stop_button.isEnabled()
            
            # Start execution
            control.play_button.click()
            QTest.qWait(100)
            
            # Verify running state
            assert not control.play_button.isEnabled()
            assert control.pause_button.isEnabled()
            assert control.stop_button.isEnabled()
            
            # Wait for completion or stop
            timeout = 2000
            start_time = time.time()
            while engine.state == ExecutionState.RUNNING:
                if (time.time() - start_time) * 1000 > timeout:
                    control.stop_button.click()
                    break
                QTest.qWait(100)
                
    def test_multiple_row_execution(self, app, settings, simple_macro, test_excel_manager):
        """Test executing multiple Excel rows"""
        with GUITestContext(app) as ctx:
            engine = ExecutionEngine(settings)
            engine.set_macro(simple_macro, test_excel_manager)
            
            # Set specific rows to execute
            engine.set_target_rows([0, 1, 2])
            
            # Track progress
            progress_updates = []
            
            def on_progress(current, total):
                progress_updates.append((current, total))
                
            engine.progressUpdated.connect(on_progress)
            
            # Execute
            engine.start()
            
            # Wait for completion
            timeout = 3000
            start_time = time.time()
            while engine.state not in [ExecutionState.IDLE, ExecutionState.STOPPED]:
                if (time.time() - start_time) * 1000 > timeout:
                    engine.stop_execution()
                    break
                QTest.qWait(100)
                
            # Should have progress updates
            assert len(progress_updates) > 0
            
    def test_hotkey_control(self, app, settings, simple_macro, test_excel_manager):
        """Test hotkey pause/stop control"""
        with GUITestContext(app) as ctx:
            engine = ExecutionEngine(settings)
            
            # Set longer execution for hotkey testing
            simple_macro.steps[0].seconds = 1.0
            
            engine.set_macro(simple_macro, test_excel_manager)
            
            # Start execution
            engine.start()
            
            # The hotkey listener should be active
            # In a real test we would simulate hotkey presses
            # For now just verify the engine can be controlled
            
            QTest.qWait(200)
            engine.toggle_pause()
            assert engine.state == ExecutionState.PAUSED
            
            engine.toggle_pause()
            QTest.qWait(100)
            
            engine.stop_execution()
            QTest.qWait(500)
            
            assert engine.state in [ExecutionState.STOPPED, ExecutionState.IDLE]


def run_tests():
    """Run tests standalone"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_tests()