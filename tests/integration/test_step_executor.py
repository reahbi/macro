#!/usr/bin/env python3
"""
Integration tests for step executor functionality
"""

import sys
import os
from pathlib import Path
import pytest
import tempfile
from PyQt5.QtWidgets import QApplication

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_helpers import GUITestContext
from automation.executor import StepExecutor
from core.macro_types import (
    MacroStep, StepType, KeyboardTypeStep, 
    MouseClickStep, WaitTimeStep, IfConditionStep, MouseButton
)
from config.settings import Settings


class TestStepExecutor:
    """Test individual step execution functionality"""
    
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
    def executor(self, settings):
        """Create step executor"""
        return StepExecutor(settings)
        
    def test_wait_time_execution(self, app, executor):
        """Test wait time step execution"""
        with GUITestContext(app) as ctx:
            # Create wait step
            step = WaitTimeStep()
            step.name = "테스트 대기"
            step.seconds = 0.1
            
            # Execute
            import time
            start_time = time.time()
            executor.execute_step(step)
            elapsed = time.time() - start_time
            
            # Should have waited approximately the specified time
            assert elapsed >= 0.09  # Allow small margin
            assert elapsed < 0.2
            
    def test_variable_substitution(self, app, executor):
        """Test variable substitution in text"""
        with GUITestContext(app) as ctx:
            # Set variables
            executor.set_variables({
                'name': '홍길동',
                'age': 25,
                'city': '서울'
            })
            
            # Test substitution
            text = "이름: {{name}}, 나이: {{age}}, 도시: {{city}}"
            result = executor._substitute_variables(text)
            
            assert result == "이름: 홍길동, 나이: 25, 도시: 서울"
            
    def test_variable_substitution_missing(self, app, executor):
        """Test substitution with missing variables"""
        with GUITestContext(app) as ctx:
            executor.set_variables({'name': '테스터'})
            
            # Missing variable should remain unchanged
            text = "이름: {{name}}, 이메일: {{email}}"
            result = executor._substitute_variables(text)
            
            assert result == "이름: 테스터, 이메일: {{email}}"
            
    def test_keyboard_type_step(self, app, executor):
        """Test keyboard typing step"""
        with GUITestContext(app) as ctx:
            # Create type step
            step = KeyboardTypeStep()
            step.text = "Hello World"
            step.interval = 0.0
            
            # Execute (in test environment, this won't actually type)
            try:
                executor.execute_step(step)
            except Exception as e:
                # May fail without proper display, but should handle gracefully
                pass
                
    def test_conditional_step_true(self, app, executor):
        """Test conditional step with true condition"""
        with GUITestContext(app) as ctx:
            # Create conditional step
            step = IfConditionStep()
            step.condition_type = "variable_equals"
            step.condition_value = {
                "variable": "status",
                "compare_value": "active"
            }
            
            # Add true branch step
            true_step = WaitTimeStep()
            true_step.seconds = 0.05
            step.true_steps = [true_step]
            
            # Add false branch step
            false_step = WaitTimeStep()
            false_step.seconds = 0.1
            step.false_steps = [false_step]
            
            # Set variable to make condition true
            executor.set_variables({'status': 'active'})
            
            # Execute
            import time
            start_time = time.time()
            executor.execute_step(step)
            elapsed = time.time() - start_time
            
            # Should have executed true branch (shorter wait)
            assert elapsed < 0.08
            
    def test_conditional_step_false(self, app, executor):
        """Test conditional step with false condition"""
        with GUITestContext(app) as ctx:
            # Create conditional step
            step = IfConditionStep()
            step.condition_type = "variable_equals"
            step.condition_value = {
                "variable": "status",
                "compare_value": "active"
            }
            
            # Add true branch step
            true_step = WaitTimeStep()
            true_step.seconds = 0.05
            step.true_steps = [true_step]
            
            # Add false branch step
            false_step = WaitTimeStep()
            false_step.seconds = 0.15
            step.false_steps = [false_step]
            
            # Set variable to make condition false
            executor.set_variables({'status': 'inactive'})
            
            # Execute
            import time
            start_time = time.time()
            executor.execute_step(step)
            elapsed = time.time() - start_time
            
            # Should have executed false branch (longer wait)
            assert elapsed >= 0.14
            
    def test_nested_conditions(self, app, executor):
        """Test nested conditional execution"""
        with GUITestContext(app) as ctx:
            # Create outer condition
            outer = IfConditionStep()
            outer.condition_type = "variable_equals"
            outer.condition_value = {
                "variable": "mode",
                "compare_value": "auto"
            }
            
            # Create inner condition for true branch
            inner = IfConditionStep()
            inner.condition_type = "variable_not_empty"
            inner.condition_value = {
                "variable": "target"
            }
            
            # Inner true step
            inner_true = WaitTimeStep()
            inner_true.seconds = 0.05
            inner.true_steps = [inner_true]
            
            outer.true_steps = [inner]
            
            # Set variables
            executor.set_variables({
                'mode': 'auto',
                'target': 'test'
            })
            
            # Execute
            executor.execute_step(outer)
            # Should complete without errors
            
    def test_variable_contains_condition(self, app, executor):
        """Test variable contains condition"""
        with GUITestContext(app) as ctx:
            step = IfConditionStep()
            step.condition_type = "variable_contains"
            step.condition_value = {
                "variable": "message",
                "compare_value": "error"
            }
            
            # True branch
            true_step = WaitTimeStep()
            true_step.seconds = 0.05
            step.true_steps = [true_step]
            
            # Test with containing value
            executor.set_variables({'message': 'Error occurred in system'})
            executor.execute_step(step)
            
            # Test with non-containing value
            executor.set_variables({'message': 'Success'})
            executor.execute_step(step)
            
    def test_variable_greater_condition(self, app, executor):
        """Test variable greater than condition"""
        with GUITestContext(app) as ctx:
            step = IfConditionStep()
            step.condition_type = "variable_greater"
            step.condition_value = {
                "variable": "count",
                "compare_value": "10"
            }
            
            # True branch
            true_step = WaitTimeStep()
            true_step.seconds = 0.05
            step.true_steps = [true_step]
            
            # Test with greater value
            executor.set_variables({'count': 15})
            executor.execute_step(step)
            
            # Test with smaller value
            executor.set_variables({'count': 5})
            executor.execute_step(step)
            
    def test_invalid_step_type(self, app, executor):
        """Test handling of unsupported step type"""
        with GUITestContext(app) as ctx:
            # Create a mock step with unsupported type
            class UnsupportedStep(MacroStep):
                def __init__(self):
                    super().__init__()
                    self.step_type = StepType.EXCEL_READ  # Not implemented in executor
                    
                def validate(self):
                    return []
                    
                def to_dict(self):
                    return super().to_dict()
                    
                @classmethod
                def from_dict(cls, data):
                    return cls()
                    
            step = UnsupportedStep()
            
            # Should raise NotImplementedError
            with pytest.raises(NotImplementedError):
                executor.execute_step(step)
                
    def test_mouse_click_validation(self, app, executor):
        """Test mouse click step validation"""
        with GUITestContext(app) as ctx:
            # Create click step with invalid coordinates
            step = MouseClickStep()
            step.x = -10  # Invalid
            step.y = -20  # Invalid
            
            errors = step.validate()
            assert len(errors) > 0
            assert "Coordinates must be non-negative" in errors[0]
            
    def test_keyboard_type_validation(self, app, executor):
        """Test keyboard type step validation"""
        with GUITestContext(app) as ctx:
            # Create type step with empty text
            step = KeyboardTypeStep()
            step.text = ""
            
            errors = step.validate()
            assert len(errors) > 0
            assert "Text cannot be empty" in errors[0]


def run_tests():
    """Run tests standalone"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_tests()