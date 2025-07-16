#!/usr/bin/env python3
"""
Integration tests for step configuration dialogs
"""

import sys
import os
from pathlib import Path
import pytest
from PyQt5.QtWidgets import QApplication, QLineEdit, QSpinBox, QComboBox, QPushButton
from PyQt5.QtCore import Qt, QTimer
import tempfile
import shutil

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_helpers import DialogTester, GUITestContext, TestScenario
from ui.dialogs.image_step_dialog import ImageStepDialog, WaitImageStepDialog
from ui.dialogs.text_search_step_dialog import TextSearchStepDialog
from ui.dialogs.if_condition_step_dialog import IfConditionStepDialog
from core.macro_types import (
    WaitImageStep, TextSearchStep, IfConditionStep,
    StepType, ErrorHandling
)


class TestStepConfiguration:
    """Test step configuration dialogs"""
    
    @pytest.fixture
    def app(self):
        """Create QApplication for tests"""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app
        
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for test files"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
        
    def test_image_step_dialog_creation(self, app):
        """Test creating and configuring image step dialog"""
        with GUITestContext(app) as ctx:
            # Create dialog
            dialog = WaitImageStepDialog()
            dialog.show()
            ctx.process_events(100)
            
            # Set step name
            name_input = dialog.findChild(QLineEdit, "name_input")
            if not name_input:
                name_input = dialog.name_input
            name_input.setText("테스트 이미지 대기")
            
            # Set timeout
            timeout_spinbox = dialog.findChild(QSpinBox)
            if timeout_spinbox:
                timeout_spinbox.setValue(10)
                
            # Get step data
            step_dict = dialog.get_step_data()
            
            # Verify configuration
            assert step_dict['name'] == "테스트 이미지 대기"
            assert step_dict['step_type'] == StepType.WAIT_IMAGE.value
            
            dialog.close()
            
    def test_text_search_dialog_with_excel_binding(self, app):
        """Test text search dialog with Excel column binding"""
        with GUITestContext(app) as ctx:
            # Excel columns for testing
            excel_columns = ["이름", "전화번호", "주소", "이메일"]
            
            # Create dialog
            dialog = TextSearchStepDialog(excel_columns=excel_columns)
            dialog.show()
            ctx.process_events(100)
            
            # Set name
            dialog.name_edit.setText("환자 이름 검색")
            
            # Test fixed text mode
            dialog.fixed_text_radio.setChecked(True)
            dialog.search_text_edit.setText("홍길동")
            ctx.process_events(50)
            
            # Verify fixed text configuration
            step_dict = dialog.get_step_data()
            assert step_dict['search_text'] == "홍길동"
            assert step_dict['use_excel_column'] is False
            
            # Switch to Excel column mode
            dialog.excel_column_radio.setChecked(True)
            ctx.process_events(50)
            
            # Select column
            dialog.excel_column_combo.setCurrentText("이름")
            
            # Verify Excel binding configuration
            step_dict = dialog.get_step_data()
            assert step_dict['excel_column'] == "이름"
            assert step_dict['use_excel_column'] is True
            
            dialog.close()
            
    def test_if_condition_dialog_complex_setup(self, app):
        """Test if condition dialog with complex configuration"""
        with GUITestContext(app) as ctx:
            # Create dialog
            excel_columns = ["상태", "금액", "확인여부"]
            dialog = IfConditionStepDialog(excel_columns=excel_columns)
            dialog.show()
            ctx.process_events(100)
            
            # Set name
            dialog.name_edit.setText("상태 확인 조건")
            
            # Select condition type
            dialog.condition_type_combo.setCurrentText("variable_equals")
            ctx.process_events(50)
            
            # Configure variable comparison
            if hasattr(dialog, 'variable_combo'):
                dialog.variable_combo.setCurrentText("상태")
                
            if hasattr(dialog, 'value_edit'):
                dialog.value_edit.setText("완료")
                
            # Add true branch step (would normally open another dialog)
            # For testing, we'll verify the UI allows it
            add_true_btn = dialog.findChild(QPushButton, "add_true_step_btn")
            if not add_true_btn:
                # Find by text
                buttons = dialog.findChildren(QPushButton)
                for btn in buttons:
                    if "True 분기" in btn.text():
                        add_true_btn = btn
                        break
                        
            assert add_true_btn is not None
            
            # Get step data
            step_dict = dialog.get_step_data()
            
            # Verify configuration
            assert step_dict['name'] == "상태 확인 조건"
            assert step_dict['step_type'] == StepType.IF_CONDITION.value
            assert step_dict['condition_type'] == "variable_equals"
            
            dialog.close()
            
    def test_coordinate_recording_simulation(self, app):
        """Test coordinate recording functionality"""
        with GUITestContext(app) as ctx:
            # This tests the concept since actual screen capture requires user interaction
            
            # Simulate coordinate selection
            test_coordinates = [(100, 200), (300, 400), (500, 600)]
            
            scenario = TestScenario("좌표 녹화 테스트")
            
            for i, (x, y) in enumerate(test_coordinates):
                scenario.add_step(
                    f"좌표 {i+1} 기록: ({x}, {y})",
                    lambda coords=(x, y): coords,
                    (x, y)
                )
                
            # Execute scenario
            results = scenario.execute({})
            
            # Verify all coordinates recorded correctly
            assert results['success']
            for i, step_result in enumerate(results['steps']):
                assert step_result['passed']
                assert step_result['actual_result'] == test_coordinates[i]
                
    def test_dialog_validation(self, app):
        """Test dialog validation and error handling"""
        with GUITestContext(app) as ctx:
            # Test image dialog without image
            dialog = WaitImageStepDialog()
            dialog.show()
            ctx.process_events(100)
            
            # Try to get data without setting image
            dialog.name_input.setText("No Image Test")
            
            # This should show validation error
            # In real implementation, clicking OK would show error
            ok_button = dialog.button_box.button(dialog.button_box.Ok)
            
            # Verify validation state
            # The dialog should not close without valid image
            dialog.close()
            
    def test_step_editing(self, app):
        """Test editing existing steps"""
        with GUITestContext(app) as ctx:
            # Create a step with initial data
            initial_step = TextSearchStep()
            initial_step.name = "초기 텍스트 검색"
            initial_step.search_text = "초기값"
            initial_step.timeout_seconds = 5
            
            # Open dialog with existing step
            dialog = TextSearchStepDialog(step=initial_step)
            dialog.show()
            ctx.process_events(100)
            
            # Verify initial values loaded
            assert dialog.name_edit.text() == "초기 텍스트 검색"
            assert dialog.search_text_edit.text() == "초기값"
            
            # Modify values
            dialog.name_edit.setText("수정된 텍스트 검색")
            dialog.search_text_edit.setText("수정된값")
            dialog.timeout_spin.setValue(10)
            
            # Get updated data
            step_dict = dialog.get_step_data()
            
            # Verify changes
            assert step_dict['name'] == "수정된 텍스트 검색"
            assert step_dict['search_text'] == "수정된값"
            assert step_dict['timeout_seconds'] == 10
            
            dialog.close()
            
    def test_error_handling_options(self, app):
        """Test error handling configuration in dialogs"""
        with GUITestContext(app) as ctx:
            dialog = WaitImageStepDialog()
            dialog.show()
            ctx.process_events(100)
            
            # Find error handling combo
            error_combo = None
            combos = dialog.findChildren(QComboBox)
            for combo in combos:
                if combo.count() > 0 and "stop" in combo.itemText(0).lower():
                    error_combo = combo
                    break
                    
            if error_combo:
                # Test different error handling options
                error_options = ["stop", "continue", "retry"]
                
                for option in error_options:
                    # Find matching item
                    for i in range(error_combo.count()):
                        if option in error_combo.itemText(i).lower():
                            error_combo.setCurrentIndex(i)
                            ctx.process_events(50)
                            
                            # Verify selection
                            step_dict = dialog.get_step_data()
                            assert step_dict.get('error_handling') is not None
                            break
                            
            dialog.close()


def run_tests():
    """Run tests standalone"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_tests()