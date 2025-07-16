#!/usr/bin/env python3
"""
Integration tests for macro storage functionality
"""

import sys
import os
from pathlib import Path
import pytest
import tempfile
import json
from PyQt5.QtWidgets import QApplication

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_helpers import GUITestContext
from core.macro_types import (
    Macro, MacroStep, StepType, KeyboardTypeStep, 
    MouseClickStep, WaitTimeStep, IfConditionStep, MouseButton
)
from core.macro_storage import MacroStorage, MacroFormat
from config.settings import Settings


class TestMacroStorage:
    """Test macro storage functionality"""
    
    @pytest.fixture
    def app(self):
        """Create QApplication for tests"""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app
        
    @pytest.fixture
    def temp_storage_dir(self):
        """Create temporary storage directory"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        
    @pytest.fixture
    def test_macro(self):
        """Create a test macro with various steps"""
        macro = Macro(name="테스트 매크로")
        macro.description = "매크로 저장/불러오기 테스트용"
        
        # Add various step types
        # 1. Wait step
        wait_step = WaitTimeStep()
        wait_step.name = "대기"
        wait_step.seconds = 2.5
        macro.add_step(wait_step)
        
        # 2. Type step with variables
        type_step = KeyboardTypeStep()
        type_step.name = "텍스트 입력"
        type_step.text = "안녕하세요 {{이름}}님"
        type_step.interval = 0.05
        macro.add_step(type_step)
        
        # 3. Click step
        click_step = MouseClickStep()
        click_step.name = "마우스 클릭"
        click_step.x = 100
        click_step.y = 200
        click_step.button = MouseButton.LEFT
        click_step.clicks = 2
        macro.add_step(click_step)
        
        # 4. Conditional step
        condition_step = IfConditionStep()
        condition_step.name = "조건 확인"
        condition_step.condition_type = "variable_equals"
        condition_step.variable_name = "상태"
        condition_step.compare_value = "완료"
        
        # Add steps to branches
        true_step = KeyboardTypeStep()
        true_step.name = "완료 메시지"
        true_step.text = "작업이 완료되었습니다"
        condition_step.true_steps = [true_step]
        
        false_step = KeyboardTypeStep()
        false_step.name = "대기 메시지"
        false_step.text = "작업 대기 중입니다"
        condition_step.false_steps = [false_step]
        
        macro.add_step(condition_step)
        
        # Add variables
        macro.variables = {
            '이름': '홍길동',
            '상태': '완료'
        }
        
        return macro
        
    def test_save_macro_json(self, app, test_macro, temp_storage_dir):
        """Test saving macro in JSON format"""
        with GUITestContext(app) as ctx:
            storage = MacroStorage(Path(temp_storage_dir))
            
            # Save macro
            file_path = Path(temp_storage_dir) / "test_macro.json"
            result = storage.save_macro(test_macro, str(file_path), MacroFormat.JSON)
            
            # Verify save was successful
            assert result is True
            assert file_path.exists()
            
            # Check file content
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            assert 'schema_version' in data
            assert 'macro' in data
            assert data['macro']['name'] == "테스트 매크로"
            assert len(data['macro']['steps']) == 4
            
    def test_load_macro_json(self, app, test_macro, temp_storage_dir):
        """Test loading macro from JSON"""
        with GUITestContext(app) as ctx:
            storage = MacroStorage(Path(temp_storage_dir))
            
            # Save macro first
            file_path = Path(temp_storage_dir) / "test_macro.json"
            storage.save_macro(test_macro, str(file_path), MacroFormat.JSON)
            
            # Load macro
            loaded_macro = storage.load_macro(str(file_path))
            
            # Verify loaded macro matches original
            assert loaded_macro.name == test_macro.name
            assert loaded_macro.description == test_macro.description
            assert len(loaded_macro.steps) == len(test_macro.steps)
            assert loaded_macro.variables == test_macro.variables
            
            # Check specific steps
            assert loaded_macro.steps[0].step_type == StepType.WAIT_TIME
            assert loaded_macro.steps[0].seconds == 2.5
            
            assert loaded_macro.steps[1].step_type == StepType.KEYBOARD_TYPE
            assert loaded_macro.steps[1].text == "안녕하세요 {{이름}}님"
            
    def test_save_macro_encrypted(self, app, test_macro, temp_storage_dir):
        """Test saving macro in encrypted format"""
        with GUITestContext(app) as ctx:
            storage = MacroStorage(Path(temp_storage_dir))
            
            # Save macro as encrypted
            file_path = Path(temp_storage_dir) / "test_macro.emf"
            result = storage.save_macro(test_macro, str(file_path), MacroFormat.ENCRYPTED)
            
            # Verify save was successful
            assert result is True
            assert file_path.exists()
            
            # File should not be readable as plain text
            content = file_path.read_bytes()
            assert b'"name"' not in content  # JSON content should be encrypted
            
    def test_load_macro_encrypted(self, app, test_macro, temp_storage_dir):
        """Test loading encrypted macro"""
        with GUITestContext(app) as ctx:
            storage = MacroStorage(Path(temp_storage_dir))
            
            # Save as encrypted
            file_path = Path(temp_storage_dir) / "test_macro.emf"
            storage.save_macro(test_macro, str(file_path), MacroFormat.ENCRYPTED)
            
            # Load encrypted macro
            loaded_macro = storage.load_macro(str(file_path))
            
            # Verify loaded macro matches original
            assert loaded_macro.name == test_macro.name
            assert loaded_macro.description == test_macro.description
            assert len(loaded_macro.steps) == len(test_macro.steps)
            
    def test_macro_backup(self, app, test_macro, temp_storage_dir):
        """Test macro backup functionality"""
        with GUITestContext(app) as ctx:
            storage = MacroStorage(Path(temp_storage_dir))
            
            # Save initial macro
            file_path = Path(temp_storage_dir) / "test_macro.json"
            storage.save_macro(test_macro, str(file_path), MacroFormat.JSON)
            
            # Modify macro
            test_macro.name = "수정된 매크로"
            test_macro.add_step(WaitTimeStep())
            
            # Save again (should create backup)
            storage.save_macro(test_macro, str(file_path), MacroFormat.JSON, create_backup=True)
            
            # Check backup exists in backups directory
            backup_dir = Path(temp_storage_dir) / "backups"
            assert backup_dir.exists()
            backup_files = list(backup_dir.glob("test_macro_backup_*.json"))
            assert len(backup_files) > 0
            
    def test_list_macros(self, app, temp_storage_dir):
        """Test listing available macros"""
        with GUITestContext(app) as ctx:
            storage = MacroStorage(Path(temp_storage_dir))
            
            # Create multiple macros
            for i in range(3):
                macro = Macro(name=f"매크로 {i+1}")
                file_path = Path(temp_storage_dir) / f"macro_{i}.json"
                storage.save_macro(macro, str(file_path))
                
            # List macros
            macros = storage.list_macros()
            
            # Verify count
            assert len(macros) >= 3
            
    def test_macro_with_complex_steps(self, app, temp_storage_dir):
        """Test saving/loading macro with complex nested steps"""
        with GUITestContext(app) as ctx:
            storage = MacroStorage(Path(temp_storage_dir))
            
            # Create macro with nested conditions
            macro = Macro(name="복잡한 매크로")
            
            # Nested if condition
            outer_condition = IfConditionStep()
            outer_condition.name = "외부 조건"
            outer_condition.condition_type = "variable_equals"
            outer_condition.variable_name = "mode"
            outer_condition.compare_value = "auto"
            
            # Inner condition in true branch
            inner_condition = IfConditionStep()
            inner_condition.name = "내부 조건"
            inner_condition.condition_type = "variable_not_empty"
            inner_condition.variable_name = "target"
            
            inner_true_step = KeyboardTypeStep()
            inner_true_step.text = "자동 처리: {{target}}"
            inner_condition.true_steps = [inner_true_step]
            
            outer_condition.true_steps = [inner_condition]
            macro.add_step(outer_condition)
            
            # Save and load
            file_path = Path(temp_storage_dir) / "complex_macro.json"
            storage.save_macro(macro, str(file_path))
            loaded_macro = storage.load_macro(str(file_path))
            
            # Verify nested structure preserved
            assert len(loaded_macro.steps) == 1
            outer = loaded_macro.steps[0]
            assert outer.step_type == StepType.IF_CONDITION
            assert len(outer.true_steps) == 1
            
            inner = outer.true_steps[0]
            assert inner.step_type == StepType.IF_CONDITION
            assert len(inner.true_steps) == 1
            assert inner.true_steps[0].text == "자동 처리: {{target}}"
            
    def test_invalid_file_handling(self, app, temp_storage_dir):
        """Test handling of invalid files"""
        with GUITestContext(app) as ctx:
            storage = MacroStorage(Path(temp_storage_dir))
            
            # Non-existent file
            with pytest.raises(FileNotFoundError):
                storage.load_macro("/nonexistent/file.json")
                
            # Invalid JSON
            invalid_file = Path(temp_storage_dir) / "invalid.json"
            invalid_file.write_text("{ invalid json }")
            
            with pytest.raises(json.JSONDecodeError):
                storage.load_macro(str(invalid_file))
                
    def test_file_permissions(self, app, test_macro, temp_storage_dir):
        """Test saving with different file permissions"""
        with GUITestContext(app) as ctx:
            storage = MacroStorage(Path(temp_storage_dir))
            
            # Normal save
            file_path = Path(temp_storage_dir) / "test_macro.json"
            result = storage.save_macro(test_macro, str(file_path))
            assert result is True
            
            # Verify file permissions (should be readable/writable by user)
            assert os.access(file_path, os.R_OK)
            assert os.access(file_path, os.W_OK)


def run_tests():
    """Run tests standalone"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_tests()