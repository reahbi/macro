"""
Unit tests for macro types (MacroStep classes and validation logic)
Tests all 12+ MacroStep classes, their validation rules, and serialization.
"""

import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, patch
from typing import Dict, Any

from core.macro_types import (
    MacroStep, Macro, StepFactory, StepType, ErrorHandling, MouseButton, ConditionOperator,
    MouseClickStep, MouseMoveStep, KeyboardTypeStep, KeyboardHotkeyStep,
    WaitTimeStep, WaitImageStep, TextSearchStep, IfConditionStep, LoopStep,
    ImageSearchStep, ScreenshotStep
)


class TestStepTypeEnum:
    """Test StepType enumeration"""
    
    def test_step_type_values(self):
        """Test that all step types have correct values"""
        expected_types = {
            "mouse_click", "mouse_move", "mouse_drag", "mouse_scroll",
            "keyboard_type", "keyboard_hotkey",
            "wait_time", "wait_image", "wait_text",
            "screenshot", "image_search", "ocr_text",
            "if_condition", "loop",
            "excel_read", "excel_write"
        }
        
        actual_types = {step_type.value for step_type in StepType}
        assert actual_types == expected_types
    
    def test_error_handling_enum(self):
        """Test ErrorHandling enumeration"""
        assert ErrorHandling.STOP.value == "stop"
        assert ErrorHandling.CONTINUE.value == "continue"
        assert ErrorHandling.RETRY.value == "retry"
    
    def test_mouse_button_enum(self):
        """Test MouseButton enumeration"""
        assert MouseButton.LEFT.value == "left"
        assert MouseButton.RIGHT.value == "right"
        assert MouseButton.MIDDLE.value == "middle"


class TestMacroStepBase:
    """Test base MacroStep functionality"""
    
    def test_abstract_base_class(self):
        """Test that MacroStep is abstract and cannot be instantiated"""
        with pytest.raises(TypeError):
            MacroStep()
    
    def test_base_fields_default_values(self):
        """Test default values for base MacroStep fields"""
        # Use concrete implementation
        step = MouseClickStep()
        
        assert isinstance(step.step_id, str)
        assert len(step.step_id) > 0
        assert step.name == ""
        assert step.description == ""
        assert step.enabled is True
        assert step.error_handling == ErrorHandling.STOP
        assert step.retry_count == 0
    
    def test_step_id_uniqueness(self):
        """Test that step IDs are unique"""
        step1 = MouseClickStep()
        step2 = MouseClickStep()
        
        assert step1.step_id != step2.step_id
        assert len(step1.step_id) == 36  # UUID4 length
        assert len(step2.step_id) == 36


class TestMouseClickStep:
    """Test MouseClickStep validation and serialization"""
    
    def test_default_values(self):
        """Test default values for MouseClickStep"""
        step = MouseClickStep()
        
        assert step.step_type == StepType.MOUSE_CLICK
        assert step.x == 0
        assert step.y == 0
        assert step.button == MouseButton.LEFT
        assert step.clicks == 1
        assert step.interval == 0.0
        assert step.relative_to == "screen"
    
    def test_validation_valid_cases(self):
        """Test validation with valid parameters"""
        valid_cases = [
            # Standard click
            {"x": 100, "y": 200, "clicks": 1},
            # Double click
            {"x": 0, "y": 0, "clicks": 2, "interval": 0.1},
            # Multi-monitor negative coordinates
            {"x": -100, "y": -50, "clicks": 1},
            # Maximum values
            {"x": 9999, "y": 9999, "clicks": 10, "interval": 5.0}
        ]
        
        for case in valid_cases:
            step = MouseClickStep(**case)
            errors = step.validate()
            assert errors == [], f"Validation failed for case: {case}"
    
    def test_validation_invalid_cases(self):
        """Test validation with invalid parameters"""
        invalid_cases = [
            # Invalid click count
            {"clicks": 0, "expected_error": "Click count must be at least 1"},
            {"clicks": -1, "expected_error": "Click count must be at least 1"},
            # Invalid interval
            {"interval": -0.1, "expected_error": "Interval must be non-negative"},
            {"interval": -1.0, "expected_error": "Interval must be non-negative"}
        ]
        
        for case in invalid_cases:
            expected_error = case.pop("expected_error")
            step = MouseClickStep(**case)
            errors = step.validate()
            assert any(expected_error in error for error in errors), \
                f"Expected error '{expected_error}' not found in {errors}"
    
    def test_multi_monitor_coordinates(self):
        """Test support for multi-monitor negative coordinates"""
        # Test negative coordinates (multi-monitor setup)
        step = MouseClickStep(x=-1920, y=-1080)
        errors = step.validate()
        assert errors == []  # Negative coordinates should be valid
        
        # Test extreme coordinates
        step = MouseClickStep(x=999999, y=-999999)
        errors = step.validate()
        assert errors == []  # Extreme coordinates should be valid
    
    def test_serialization_round_trip(self):
        """Test to_dict and from_dict serialization"""
        original = MouseClickStep(
            name="Test Click",
            description="Test mouse click step",
            x=150, y=250,
            button=MouseButton.RIGHT,
            clicks=2,
            interval=0.5,
            relative_to="window"
        )
        
        # Serialize to dict
        data = original.to_dict()
        
        # Verify dict structure
        assert data["step_type"] == "mouse_click"
        assert data["x"] == 150
        assert data["y"] == 250
        assert data["button"] == "right"
        assert data["clicks"] == 2
        assert data["interval"] == 0.5
        
        # Deserialize from dict
        restored = MouseClickStep.from_dict(data)
        
        # Verify restored object
        assert restored.name == original.name
        assert restored.x == original.x
        assert restored.y == original.y
        assert restored.button == original.button
        assert restored.clicks == original.clicks
        assert restored.interval == original.interval


class TestMouseMoveStep:
    """Test MouseMoveStep validation and serialization"""
    
    def test_default_values(self):
        """Test default values for MouseMoveStep"""
        step = MouseMoveStep()
        
        assert step.step_type == StepType.MOUSE_MOVE
        assert step.x == 0
        assert step.y == 0
        assert step.duration == 0.0
        assert step.relative_to == "screen"
    
    def test_validation_valid_cases(self):
        """Test validation with valid parameters"""
        valid_cases = [
            {"x": 100, "y": 200, "duration": 0.0},  # Instant move
            {"x": 500, "y": 300, "duration": 1.5},  # Smooth move
            {"x": -100, "y": -200, "duration": 0.1}  # Multi-monitor
        ]
        
        for case in valid_cases:
            step = MouseMoveStep(**case)
            errors = step.validate()
            assert errors == [], f"Validation failed for case: {case}"
    
    def test_validation_invalid_duration(self):
        """Test validation with invalid duration"""
        step = MouseMoveStep(duration=-0.1)
        errors = step.validate()
        assert any("Duration must be non-negative" in error for error in errors)


class TestKeyboardTypeStep:
    """Test KeyboardTypeStep validation and serialization"""
    
    def test_default_values(self):
        """Test default values for KeyboardTypeStep"""
        step = KeyboardTypeStep()
        
        assert step.step_type == StepType.KEYBOARD_TYPE
        assert step.text == ""
        assert step.interval == 0.0
        assert step.use_variables is True
    
    def test_validation_valid_cases(self):
        """Test validation with valid text input"""
        valid_cases = [
            {"text": "Hello World"},
            {"text": "한글 텍스트 입력 테스트"},
            {"text": "{{variable}} substitution test"},
            {"text": "Special chars: !@#$%^&*()"},
            {"text": "Numbers 12345 and symbols"},
            {"text": "A" * 1000}  # Long text
        ]
        
        for case in valid_cases:
            step = KeyboardTypeStep(**case)
            errors = step.validate()
            assert errors == [], f"Validation failed for case: {case}"
    
    def test_validation_empty_text(self):
        """Test validation fails for empty text"""
        step = KeyboardTypeStep(text="")
        errors = step.validate()
        assert any("Text cannot be empty" in error for error in errors)
    
    def test_validation_invalid_interval(self):
        """Test validation fails for negative interval"""
        step = KeyboardTypeStep(text="test", interval=-0.1)
        errors = step.validate()
        assert any("Interval must be non-negative" in error for error in errors)
    
    def test_variable_substitution_support(self):
        """Test variable substitution patterns"""
        step = KeyboardTypeStep(
            text="Hello {{name}}, your age is {{age}}",
            use_variables=True
        )
        errors = step.validate()
        assert errors == []
        
        # Verify serialization preserves variable patterns
        data = step.to_dict()
        assert "{{name}}" in data["text"]
        assert "{{age}}" in data["text"]


class TestKeyboardHotkeyStep:
    """Test KeyboardHotkeyStep validation and serialization"""
    
    def test_default_values(self):
        """Test default values for KeyboardHotkeyStep"""
        step = KeyboardHotkeyStep()
        
        assert step.step_type == StepType.KEYBOARD_HOTKEY
        assert step.keys == []
    
    def test_validation_valid_hotkeys(self):
        """Test validation with valid hotkey combinations"""
        valid_cases = [
            {"keys": ["ctrl", "c"]},  # Copy
            {"keys": ["ctrl", "alt", "del"]},  # Three-key combo
            {"keys": ["win", "r"]},  # Run dialog
            {"keys": ["alt", "f4"]},  # Close window
            {"keys": ["f1"]},  # Single function key
            {"keys": ["shift", "ctrl", "alt", "f12"]}  # Complex combo
        ]
        
        for case in valid_cases:
            step = KeyboardHotkeyStep(**case)
            errors = step.validate()
            assert errors == [], f"Validation failed for case: {case}"
    
    def test_validation_empty_keys(self):
        """Test validation fails for empty keys list"""
        step = KeyboardHotkeyStep(keys=[])
        errors = step.validate()
        assert any("At least one key must be specified" in error for error in errors)


class TestWaitTimeStep:
    """Test WaitTimeStep validation and serialization"""
    
    def test_default_values(self):
        """Test default values for WaitTimeStep"""
        step = WaitTimeStep()
        
        assert step.step_type == StepType.WAIT_TIME
        assert step.seconds == 1.0
    
    def test_validation_valid_times(self):
        """Test validation with valid time values"""
        valid_times = [0.1, 1.0, 5.5, 60.0, 3600.0]
        
        for seconds in valid_times:
            step = WaitTimeStep(seconds=seconds)
            errors = step.validate()
            assert errors == [], f"Validation failed for seconds: {seconds}"
    
    def test_validation_invalid_times(self):
        """Test validation with invalid time values"""
        invalid_times = [0, -0.1, -1.0, -60.0]
        
        for seconds in invalid_times:
            step = WaitTimeStep(seconds=seconds)
            errors = step.validate()
            assert any("Wait time must be positive" in error for error in errors), \
                f"Expected validation error for seconds: {seconds}"


class TestWaitImageStep:
    """Test WaitImageStep validation and serialization"""
    
    def test_default_values(self):
        """Test default values for WaitImageStep"""
        step = WaitImageStep()
        
        assert step.step_type == StepType.WAIT_IMAGE
        assert step.image_path == ""
        assert step.timeout == 10.0
        assert step.confidence == 0.9
        assert step.region is None
    
    def test_validation_valid_cases(self):
        """Test validation with valid parameters"""
        valid_cases = [
            {"image_path": "test.png", "timeout": 5.0, "confidence": 0.8},
            {"image_path": "C:\\temp\\image.jpg", "timeout": 30.0, "confidence": 1.0},
            {"image_path": "/home/user/pic.png", "timeout": 1.0, "confidence": 0.0},
            {"image_path": "image.bmp", "region": (100, 100, 200, 200)}
        ]
        
        for case in valid_cases:
            step = WaitImageStep(**case)
            errors = step.validate()
            assert errors == [], f"Validation failed for case: {case}"
    
    def test_validation_invalid_cases(self):
        """Test validation with invalid parameters"""
        invalid_cases = [
            {"image_path": "", "expected_error": "Image path cannot be empty"},
            {"image_path": "test.png", "timeout": 0, "expected_error": "Timeout must be positive"},
            {"image_path": "test.png", "timeout": -1, "expected_error": "Timeout must be positive"},
            {"image_path": "test.png", "confidence": -0.1, "expected_error": "Confidence must be between 0 and 1"},
            {"image_path": "test.png", "confidence": 1.1, "expected_error": "Confidence must be between 0 and 1"}
        ]
        
        for case in invalid_cases:
            expected_error = case.pop("expected_error")
            step = WaitImageStep(**case)
            errors = step.validate()
            assert any(expected_error in error for error in errors), \
                f"Expected error '{expected_error}' not found in {errors}"
    
    def test_region_serialization(self):
        """Test region tuple serialization"""
        step = WaitImageStep(
            image_path="test.png",
            region=(100, 200, 300, 400)
        )
        
        data = step.to_dict()
        assert data["region"] == [100, 200, 300, 400]  # Tuple converted to list
        
        restored = WaitImageStep.from_dict(data)
        assert restored.region == (100, 200, 300, 400)  # List converted back to tuple


class TestTextSearchStep:
    """Test TextSearchStep (OCR) validation and serialization"""
    
    def test_default_values(self):
        """Test default values for TextSearchStep"""
        step = TextSearchStep()
        
        assert step.step_type == StepType.OCR_TEXT
        assert step.search_text == ""
        assert step.excel_column is None
        assert step.region is None
        assert step.exact_match is False
        assert step.confidence == 0.5
        assert step.click_after_find is True
        assert step.click_offset == (0, 0)
        assert step.double_click is False
    
    def test_validation_valid_cases(self):
        """Test validation with valid parameters"""
        valid_cases = [
            # Text search
            {"search_text": "Click Here"},
            # Excel column binding
            {"excel_column": "button_text"},
            # Both specified (should still be valid)
            {"search_text": "{{text}}", "excel_column": "backup_text"},
            # With region and options
            {"search_text": "Login", "region": (0, 0, 800, 600), "exact_match": True}
        ]
        
        for case in valid_cases:
            step = TextSearchStep(**case)
            errors = step.validate()
            assert errors == [], f"Validation failed for case: {case}"
    
    def test_validation_neither_text_nor_column(self):
        """Test validation fails when neither search_text nor excel_column specified"""
        step = TextSearchStep()  # Both empty/None
        errors = step.validate()
        assert any("Either search text or Excel column must be specified" in error for error in errors)
    
    def test_validation_invalid_confidence(self):
        """Test validation with invalid confidence values"""
        invalid_confidences = [-0.1, 1.1, 2.0]
        
        for confidence in invalid_confidences:
            step = TextSearchStep(search_text="test", confidence=confidence)
            errors = step.validate()
            assert any("Confidence must be between 0 and 1" in error for error in errors)
    
    def test_click_offset_serialization(self):
        """Test click offset tuple serialization"""
        step = TextSearchStep(
            search_text="test",
            click_offset=(50, -25)
        )
        
        data = step.to_dict()
        assert data["click_offset"] == [50, -25]
        
        restored = TextSearchStep.from_dict(data)
        assert restored.click_offset == (50, -25)


class TestIfConditionStep:
    """Test IfConditionStep validation and serialization (complex nested structure)"""
    
    def test_default_values(self):
        """Test default values for IfConditionStep"""
        step = IfConditionStep()
        
        assert step.step_type == StepType.IF_CONDITION
        assert step.condition_type == "image_exists"
        assert step.condition_value == {}
        assert step.true_steps == []
        assert step.false_steps == []
    
    def test_validation_image_exists_condition(self):
        """Test validation for image_exists condition"""
        # Valid case
        step = IfConditionStep(
            condition_type="image_exists",
            condition_value={"image_path": "button.png", "confidence": 0.9}
        )
        errors = step.validate()
        assert errors == []
        
        # Invalid case - no image path
        step = IfConditionStep(
            condition_type="image_exists",
            condition_value={}
        )
        errors = step.validate()
        assert any("Image path must be specified" in error for error in errors)
    
    def test_validation_text_exists_condition(self):
        """Test validation for text_exists condition"""
        # Valid case
        step = IfConditionStep(
            condition_type="text_exists",
            condition_value={"text": "Submit Button"}
        )
        errors = step.validate()
        assert errors == []
        
        # Invalid case - no text
        step = IfConditionStep(
            condition_type="text_exists",
            condition_value={}
        )
        errors = step.validate()
        assert any("Text must be specified" in error for error in errors)
    
    def test_validation_variable_conditions(self):
        """Test validation for variable comparison conditions"""
        variable_conditions = [
            "variable_equals", "variable_contains", 
            "variable_greater", "variable_less"
        ]
        
        for condition_type in variable_conditions:
            # Valid case
            step = IfConditionStep(
                condition_type=condition_type,
                condition_value={"variable": "user_name", "compare_value": "admin"}
            )
            errors = step.validate()
            assert errors == [], f"Validation failed for {condition_type}"
            
            # Invalid case - no variable
            step = IfConditionStep(
                condition_type=condition_type,
                condition_value={"compare_value": "admin"}
            )
            errors = step.validate()
            assert any("Variable name must be specified" in error for error in errors)
            
            # Invalid case - no compare value
            step = IfConditionStep(
                condition_type=condition_type,
                condition_value={"variable": "user_name"}
            )
            errors = step.validate()
            assert any("Comparison value must be specified" in error for error in errors)
    
    @patch('sys.modules')
    def test_nested_step_serialization(self, mock_modules):
        """Test serialization with nested steps"""
        # Mock the module system to avoid circular import issues
        mock_module = Mock()
        mock_module.StepFactory = StepFactory
        mock_modules.__getitem__.return_value = mock_module
        
        # Create nested steps
        true_step = MouseClickStep(name="True Click", x=100, y=200)
        false_step = KeyboardTypeStep(name="False Type", text="false branch")
        
        step = IfConditionStep(
            condition_type="image_exists",
            condition_value={"image_path": "test.png"},
            true_steps=[true_step],
            false_steps=[false_step]
        )
        
        # Serialize
        data = step.to_dict()
        assert len(data["true_steps"]) == 1
        assert len(data["false_steps"]) == 1
        assert data["true_steps"][0]["name"] == "True Click"
        assert data["false_steps"][0]["name"] == "False Type"


class TestLoopStep:
    """Test LoopStep validation and serialization"""
    
    def test_default_values(self):
        """Test default values for LoopStep"""
        step = LoopStep()
        
        assert step.step_type == StepType.LOOP
        assert step.loop_type == "count"
        assert step.loop_count == 1
        assert step.loop_steps == []
    
    def test_validation_valid_cases(self):
        """Test validation with valid parameters"""
        valid_cases = [
            {"loop_type": "count", "loop_count": 5, "loop_steps": ["step1", "step2"]},
            {"loop_type": "while_image", "loop_steps": ["step1"]},
            {"loop_type": "for_each_row", "loop_steps": ["step1", "step2", "step3"]}
        ]
        
        for case in valid_cases:
            step = LoopStep(**case)
            errors = step.validate()
            assert errors == [], f"Validation failed for case: {case}"
    
    def test_validation_invalid_cases(self):
        """Test validation with invalid parameters"""
        invalid_cases = [
            {"loop_type": "count", "loop_count": 0, "loop_steps": ["step1"], 
             "expected_error": "Loop count must be at least 1"},
            {"loop_type": "count", "loop_count": -1, "loop_steps": ["step1"],
             "expected_error": "Loop count must be at least 1"},
            {"loop_type": "count", "loop_count": 5, "loop_steps": [],
             "expected_error": "Loop must contain at least one step"}
        ]
        
        for case in invalid_cases:
            expected_error = case.pop("expected_error")
            step = LoopStep(**case)
            errors = step.validate()
            assert any(expected_error in error for error in errors), \
                f"Expected error '{expected_error}' not found in {errors}"


class TestImageSearchStep:
    """Test ImageSearchStep validation and serialization"""
    
    def test_validation_and_serialization(self):
        """Test ImageSearchStep validation and round-trip serialization"""
        step = ImageSearchStep(
            image_path="button.png",
            confidence=0.85,
            region=(100, 100, 400, 300),
            click_after_find=True,
            click_offset=(10, -5),
            double_click=True
        )
        
        # Validate
        errors = step.validate()
        assert errors == []
        
        # Serialize and deserialize
        data = step.to_dict()
        restored = ImageSearchStep.from_dict(data)
        
        assert restored.image_path == step.image_path
        assert restored.confidence == step.confidence
        assert restored.region == step.region
        assert restored.click_after_find == step.click_after_find
        assert restored.click_offset == step.click_offset
        assert restored.double_click == step.double_click


class TestScreenshotStep:
    """Test ScreenshotStep validation and serialization"""
    
    def test_validation_and_serialization(self):
        """Test ScreenshotStep validation and round-trip serialization"""
        step = ScreenshotStep(
            filename_pattern="test_{timestamp}.png",
            save_directory="./screenshots/",
            region=(0, 0, 1920, 1080)
        )
        
        # Validate
        errors = step.validate()
        assert errors == []
        
        # Test empty filename pattern validation
        invalid_step = ScreenshotStep(filename_pattern="")
        errors = invalid_step.validate()
        assert any("Filename pattern cannot be empty" in error for error in errors)


class TestStepFactory:
    """Test StepFactory for step creation and deserialization"""
    
    def test_factory_step_creation(self):
        """Test creating steps using factory"""
        for step_type in [StepType.MOUSE_CLICK, StepType.KEYBOARD_TYPE, StepType.WAIT_TIME]:
            step = StepFactory.create_step(step_type)
            assert step.step_type == step_type
            assert isinstance(step, MacroStep)
    
    def test_factory_unknown_step_type(self):
        """Test factory with unknown step type"""
        # Create a mock step type that doesn't exist
        with pytest.raises(ValueError, match="Unknown step type"):
            # This would fail since we don't have a handler for a non-existent type
            class FakeStepType:
                value = "fake_step"
            StepFactory.create_step(FakeStepType())
    
    def test_factory_from_dict(self, macro_step_data):
        """Test deserializing steps from dictionary using factory"""
        for step_data in macro_step_data.values():
            step = StepFactory.from_dict(step_data)
            assert step.step_type.value == step_data["step_type"]
            assert step.name == step_data["name"]


class TestMacro:
    """Test Macro class with step management"""
    
    def test_default_values(self):
        """Test default values for Macro"""
        macro = Macro()
        
        assert isinstance(macro.macro_id, str)
        assert len(macro.macro_id) == 36  # UUID4 length
        assert macro.name == "새 매크로"
        assert macro.description == ""
        assert macro.version == "1.0.0"
        assert isinstance(macro.created_at, datetime)
        assert isinstance(macro.updated_at, datetime)
        assert macro.steps == []
        assert macro.variables == {}
        assert macro.metadata == {}
    
    def test_step_management(self):
        """Test adding, removing, and moving steps"""
        macro = Macro()
        
        # Add steps
        step1 = MouseClickStep(name="Click 1")
        step2 = KeyboardTypeStep(name="Type 1")
        step3 = WaitTimeStep(name="Wait 1")
        
        macro.add_step(step1)
        macro.add_step(step2)
        macro.add_step(step3, index=1)  # Insert at position 1
        
        assert len(macro.steps) == 3
        assert macro.steps[0] == step1
        assert macro.steps[1] == step3  # Inserted step
        assert macro.steps[2] == step2
        
        # Remove step
        macro.remove_step(step3.step_id)
        assert len(macro.steps) == 2
        assert step3 not in macro.steps
        
        # Move step
        original_updated_at = macro.updated_at
        macro.move_step(step2.step_id, 0)  # Move to beginning
        assert macro.steps[0] == step2
        assert macro.steps[1] == step1
        assert macro.updated_at > original_updated_at  # Should update timestamp
    
    def test_macro_validation(self):
        """Test macro validation with step validation"""
        macro = Macro(name="Test Macro")
        
        # Add valid steps
        valid_step = MouseClickStep(name="Valid Click", x=100, y=200)
        macro.add_step(valid_step)
        
        # Add invalid step
        invalid_step = WaitTimeStep(name="Invalid Wait", seconds=-1)
        macro.add_step(invalid_step)
        
        errors = macro.validate()
        
        # Should have error from invalid step
        assert len(errors) >= 1
        assert any("Wait time must be positive" in error for error in errors)
        
        # Test empty name validation
        macro.name = ""
        errors = macro.validate()
        assert any("Macro name cannot be empty" in error for error in errors)
    
    def test_macro_serialization(self):
        """Test macro serialization with steps"""
        macro = Macro(
            name="Test Serialization Macro",
            description="Test macro for serialization",
            variables={"test_var": "test_value"},
            metadata={"created_by": "test_user"}
        )
        
        # Add some steps
        macro.add_step(MouseClickStep(name="Click Step", x=100, y=200))
        macro.add_step(KeyboardTypeStep(name="Type Step", text="Hello {{test_var}}"))
        
        # Serialize
        data = macro.to_dict()
        
        # Verify structure
        assert data["name"] == macro.name
        assert data["description"] == macro.description
        assert len(data["steps"]) == 2
        assert data["variables"]["test_var"] == "test_value"
        assert data["metadata"]["created_by"] == "test_user"
        
        # Verify step serialization
        assert data["steps"][0]["name"] == "Click Step"
        assert data["steps"][1]["text"] == "Hello {{test_var}}"
        
        # Test deserialization
        with patch('sys.modules') as mock_modules:
            mock_module = Mock()
            mock_module.StepFactory = StepFactory
            mock_modules.__getitem__.return_value = mock_module
            
            restored_macro = Macro.from_dict(data)
            
            assert restored_macro.name == macro.name
            assert restored_macro.description == macro.description
            assert len(restored_macro.steps) == 2
            assert restored_macro.variables == macro.variables
            assert restored_macro.metadata == macro.metadata


class TestComplexScenarios:
    """Test complex scenarios with multiple step types and validations"""
    
    def test_realistic_macro_scenario(self):
        """Test a realistic macro with multiple step types"""
        macro = Macro(name="Login Automation")
        
        # Click username field
        macro.add_step(MouseClickStep(
            name="Click Username Field",
            x=300, y=200,
            description="Click on username input field"
        ))
        
        # Type username
        macro.add_step(KeyboardTypeStep(
            name="Enter Username",
            text="{{username}}",
            description="Type username from Excel data"
        ))
        
        # Wait for page load
        macro.add_step(WaitTimeStep(
            name="Wait for Load",
            seconds=2.0,
            description="Wait for page to load"
        ))
        
        # Search for login button
        macro.add_step(ImageSearchStep(
            name="Find Login Button",
            image_path="login_button.png",
            confidence=0.8,
            description="Find and click login button"
        ))
        
        # Conditional check for success
        success_condition = IfConditionStep(
            name="Check Login Success",
            condition_type="text_exists",
            condition_value={"text": "Welcome"},
            description="Check if login was successful"
        )
        
        # Add nested step for success case
        success_step = ScreenshotStep(
            name="Success Screenshot",
            filename_pattern="login_success_{timestamp}.png"
        )
        success_condition.true_steps = [success_step]
        
        macro.add_step(success_condition)
        
        # Validate entire macro
        errors = macro.validate()
        assert errors == [], f"Macro validation failed: {errors}"
        
        # Test serialization
        data = macro.to_dict()
        assert len(data["steps"]) == 5
        assert "{{username}}" in data["steps"][1]["text"]
        assert data["steps"][4]["condition_type"] == "text_exists"
    
    def test_edge_case_validation_combinations(self):
        """Test edge cases and boundary value validations"""
        edge_cases = [
            # Minimum valid values
            WaitTimeStep(seconds=0.001),
            MouseClickStep(clicks=1, interval=0.0),
            TextSearchStep(search_text="A", confidence=0.0),
            
            # Maximum reasonable values
            WaitTimeStep(seconds=3600.0),  # 1 hour
            MouseClickStep(clicks=100, interval=10.0),
            TextSearchStep(search_text="A" * 1000, confidence=1.0),
            
            # Multi-monitor coordinates
            MouseClickStep(x=-3840, y=-2160),  # Dual 4K setup
            MouseMoveStep(x=7680, y=4320),     # Quad monitor setup
        ]
        
        for step in edge_cases:
            errors = step.validate()
            assert errors == [], f"Edge case validation failed for {step}: {errors}"
    
    def test_variable_pattern_preservation(self):
        """Test that variable patterns are preserved through serialization"""
        variable_patterns = [
            "{{simple_var}}",
            "{{var_with_underscore}}",
            "{{var123}}",
            "Hello {{name}}, you have {{count}} messages",
            "{{first}} {{last}} - {{email}}",
        ]
        
        for pattern in variable_patterns:
            step = KeyboardTypeStep(text=pattern)
            data = step.to_dict()
            restored = KeyboardTypeStep.from_dict(data)
            
            assert restored.text == pattern
            assert pattern in data["text"]


@pytest.mark.performance
class TestPerformanceConsiderations:
    """Test performance-related aspects of macro types"""
    
    def test_large_macro_serialization_performance(self):
        """Test serialization performance with large macros"""
        import time
        
        # Create macro with many steps
        macro = Macro(name="Large Macro")
        
        for i in range(1000):
            if i % 3 == 0:
                step = MouseClickStep(name=f"Click {i}", x=i, y=i)
            elif i % 3 == 1:
                step = KeyboardTypeStep(name=f"Type {i}", text=f"Text {i}")
            else:
                step = WaitTimeStep(name=f"Wait {i}", seconds=0.1)
            
            macro.add_step(step)
        
        # Measure serialization time
        start_time = time.time()
        data = macro.to_dict()
        serialize_time = time.time() - start_time
        
        # Should complete within reasonable time (< 1 second)
        assert serialize_time < 1.0, f"Serialization too slow: {serialize_time:.3f}s"
        assert len(data["steps"]) == 1000
    
    def test_step_validation_performance(self):
        """Test validation performance doesn't degrade with complex steps"""
        import time
        
        # Create complex conditional step with many nested steps
        condition = IfConditionStep(
            condition_type="variable_equals",
            condition_value={"variable": "test", "compare_value": "value"}
        )
        
        # Add many nested steps
        for i in range(100):
            true_step = MouseClickStep(name=f"True {i}", x=i, y=i)
            false_step = KeyboardTypeStep(name=f"False {i}", text=f"Text {i}")
            condition.true_steps.append(true_step)
            condition.false_steps.append(false_step)
        
        # Measure validation time
        start_time = time.time()
        errors = condition.validate()
        validation_time = time.time() - start_time
        
        # Should validate quickly (< 0.1 seconds)
        assert validation_time < 0.1, f"Validation too slow: {validation_time:.3f}s"
        assert errors == []