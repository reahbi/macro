#!/usr/bin/env python3
"""
Integration tests for text input and variable binding functionality
"""

import sys
import os
from pathlib import Path
import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_helpers import GUITestContext
from core.macro_types import (
    MacroStep, StepType, KeyboardTypeStep, 
    Macro, IfConditionStep
)
from automation.executor import StepExecutor
from config.settings import Settings


class TestTextInputVariables:
    """Test text input and variable binding functionality"""
    
    @pytest.fixture
    def app(self):
        """Create QApplication for tests"""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app
        
    @pytest.fixture
    def test_variables(self):
        """Create test variables"""
        return {
            '이름': '홍길동',
            '이메일': 'test@example.com',
            '전화번호': '010-1234-5678',
            '주소': '서울시 강남구',
            '상태': '처리중'
        }
        
    def test_keyboard_type_step_creation(self, app):
        """Test creating keyboard type step"""
        with GUITestContext(app) as ctx:
            # Create keyboard type step
            step = KeyboardTypeStep()
            step.name = "텍스트 입력 테스트"
            step.text = "Hello World"
            
            # Verify configuration
            assert step.step_type == StepType.KEYBOARD_TYPE
            assert step.text == "Hello World"
            assert step.name == "텍스트 입력 테스트"
            
            # Test serialization
            step_dict = step.to_dict()
            assert step_dict['step_type'] == StepType.KEYBOARD_TYPE.value
            assert step_dict['text'] == "Hello World"
            
    def test_variable_substitution_simple(self, app, test_variables):
        """Test simple variable substitution"""
        with GUITestContext(app) as ctx:
            executor = StepExecutor(Settings())
            executor.set_variables(test_variables)
            
            # Test simple substitution
            text = "이름: {{이름}}"
            result = executor._substitute_variables(text)
            assert result == "이름: 홍길동"
            
            # Test multiple variables
            text = "{{이름}}님의 이메일은 {{이메일}}입니다"
            result = executor._substitute_variables(text)
            assert result == "홍길동님의 이메일은 test@example.com입니다"
            
    def test_variable_substitution_missing(self, app, test_variables):
        """Test behavior with missing variables"""
        with GUITestContext(app) as ctx:
            executor = StepExecutor(Settings())
            executor.set_variables(test_variables)
            
            # Missing variable should remain unchanged
            text = "{{없는변수}} 테스트"
            result = executor._substitute_variables(text)
            assert result == "{{없는변수}} 테스트"
            
    def test_variable_substitution_mixed(self, app, test_variables):
        """Test mixed text and variables"""
        with GUITestContext(app) as ctx:
            executor = StepExecutor(Settings())
            executor.set_variables(test_variables)
            
            # Complex mixed text
            text = """
            고객명: {{이름}}
            연락처: {{전화번호}}
            이메일: {{이메일}}
            주소: {{주소}}
            처리상태: {{상태}}
            """
            
            result = executor._substitute_variables(text)
            
            assert "고객명: 홍길동" in result
            assert "연락처: 010-1234-5678" in result
            assert "이메일: test@example.com" in result
            assert "주소: 서울시 강남구" in result
            assert "처리상태: 처리중" in result
            
    def test_special_keys(self, app):
        """Test special key configurations"""
        with GUITestContext(app) as ctx:
            # Test Tab key
            step = KeyboardTypeStep()
            step.text = "{{이름}}\t{{이메일}}"
            
            # Verify tab character
            assert '\t' in step.text
            
            # Test Enter key
            step2 = KeyboardTypeStep()
            step2.text = "첫 줄\n두 번째 줄"
            
            assert '\n' in step2.text
            
    def test_keyboard_step_with_delay(self, app):
        """Test keyboard typing with delay settings"""
        with GUITestContext(app) as ctx:
            step = KeyboardTypeStep()
            step.text = "천천히 입력"
            step.interval = 0.1  # 0.1 seconds between characters
            
            # Verify delay configuration
            assert step.interval == 0.1
            
            # Test serialization includes delay
            step_dict = step.to_dict()
            assert step_dict.get('interval') == 0.1
            
    def test_conditional_text_input(self, app, test_variables):
        """Test text input within conditional statements"""
        with GUITestContext(app) as ctx:
            # Create conditional step
            condition = IfConditionStep()
            condition.condition_type = "variable_equals"
            condition.variable_name = "상태"
            condition.compare_value = "처리중"
            
            # Add text input to true branch
            true_step = KeyboardTypeStep()
            true_step.text = "{{이름}}님 처리중입니다"
            condition.true_steps = [true_step]
            
            # Add text input to false branch
            false_step = KeyboardTypeStep()
            false_step.text = "{{이름}}님 대기중입니다"
            condition.false_steps = [false_step]
            
            # Verify structure
            assert len(condition.true_steps) == 1
            assert len(condition.false_steps) == 1
            assert condition.true_steps[0].text == "{{이름}}님 처리중입니다"
            assert condition.false_steps[0].text == "{{이름}}님 대기중입니다"
            
    def test_variable_in_macro_context(self, app, test_variables):
        """Test variables in full macro context"""
        with GUITestContext(app) as ctx:
            # Create macro with variables
            macro = Macro(name="변수 테스트 매크로")
            macro.variables = test_variables
            
            # Add steps with variables
            step1 = KeyboardTypeStep()
            step1.text = "고객명: {{이름}}"
            macro.add_step(step1)
            
            step2 = KeyboardTypeStep()
            step2.text = "이메일: {{이메일}}"
            macro.add_step(step2)
            
            # Verify macro structure
            assert len(macro.steps) == 2
            assert macro.variables['이름'] == '홍길동'
            assert macro.variables['이메일'] == 'test@example.com'
            
    def test_empty_and_whitespace_handling(self, app):
        """Test handling of empty and whitespace text"""
        with GUITestContext(app) as ctx:
            executor = StepExecutor(Settings())
            
            # Empty string
            executor.set_variables({})
            result = executor._substitute_variables("")
            assert result == ""
            
            # Only whitespace
            result = executor._substitute_variables("   ")
            assert result == "   "
            
            # Variable with empty value
            executor.set_variables({'empty': ''})
            result = executor._substitute_variables("Value: {{empty}}")
            assert result == "Value: "
            
    def test_nested_brackets(self, app):
        """Test handling of nested or malformed brackets"""
        with GUITestContext(app) as ctx:
            executor = StepExecutor(Settings())
            
            # Nested brackets
            executor.set_variables({'nested': 'value'})
            text = "{{{{nested}}}}"
            result = executor._substitute_variables(text)
            # Should handle gracefully
            assert "{{" in result or "value" in result
            
            # Unclosed brackets
            executor.set_variables({})
            text = "{{unclosed"
            result = executor._substitute_variables(text)
            assert result == "{{unclosed"
            
            # Extra closing brackets
            text = "extra}}"
            result = executor._substitute_variables(text)
            assert result == "extra}}"


def run_tests():
    """Run tests standalone"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_tests()