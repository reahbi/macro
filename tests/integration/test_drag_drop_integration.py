#!/usr/bin/env python3
"""
Integration tests for drag and drop functionality
"""

import sys
import os
from pathlib import Path
import pytest
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QPoint, Qt

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_helpers import MockDragDropEvent, GUITestContext, TestScenario
from ui.widgets.macro_editor import MacroEditorWidget, StepPalette, MacroFlowWidget
from core.macro_types import Macro, StepType, MacroStep
from config.settings import Settings


class TestDragDropIntegration:
    """Test drag and drop functionality"""
    
    @pytest.fixture
    def app(self):
        """Create QApplication for tests"""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app
        
    @pytest.fixture
    def macro_editor(self, app):
        """Create macro editor widget"""
        editor = MacroEditorWidget()
        editor.show()
        app.processEvents()
        yield editor
        editor.close()
        
    def test_drag_new_step_from_palette(self, app, macro_editor):
        """Test dragging a new step from palette to flow"""
        with GUITestContext(app) as ctx:
            # Get palette and flow widgets
            palette = macro_editor.palette
            flow = macro_editor.flow_widget
            
            # Initial state - should be empty
            assert len(flow.macro.steps) == 0
            
            # Create drag event for Click step
            mime_data = MockDragDropEvent.create_step_mime_data("mouse_click")
            
            # Simulate drag enter
            drag_enter_event = MockDragDropEvent.create_drag_enter_event(mime_data)
            flow.dragEnterEvent(drag_enter_event)
            assert drag_enter_event.isAccepted()
            
            # Simulate drop at position
            drop_event = MockDragDropEvent.create_drop_event(mime_data, QPoint(100, 50))
            flow.dropEvent(drop_event)
            
            # Process events
            ctx.process_events(200)
            
            # Verify step was added
            assert len(flow.macro.steps) == 1
            assert flow.macro.steps[0].step_type == StepType.MOUSE_CLICK
            assert flow.macro.steps[0].name == "마우스 클릭"
            
    def test_drag_multiple_steps(self, app, macro_editor):
        """Test dragging multiple different step types"""
        with GUITestContext(app) as ctx:
            flow = macro_editor.flow_widget
            
            # Step types to test
            step_types = [
                ("mouse_click", StepType.MOUSE_CLICK, "마우스 클릭"),
                ("keyboard_type", StepType.KEYBOARD_TYPE, "텍스트 입력"),
                ("wait_time", StepType.WAIT_TIME, "대기"),
                ("if_condition", StepType.IF_CONDITION, "조건문")
            ]
            
            # Add each step type
            for i, (mime_type, expected_type, expected_name) in enumerate(step_types):
                mime_data = MockDragDropEvent.create_step_mime_data(mime_type)
                drop_event = MockDragDropEvent.create_drop_event(
                    mime_data, 
                    QPoint(100, 50 + i * 100)
                )
                flow.dropEvent(drop_event)
                ctx.process_events(100)
                
            # Verify all steps were added
            assert len(flow.macro.steps) == len(step_types)
            
            for i, (_, expected_type, expected_name) in enumerate(step_types):
                assert flow.macro.steps[i].step_type == expected_type
                assert flow.macro.steps[i].name == expected_name
                
    def test_reorder_existing_steps(self, app, macro_editor):
        """Test reordering steps by dragging"""
        with GUITestContext(app) as ctx:
            flow = macro_editor.flow_widget
            
            # Add 3 steps first
            for i in range(3):
                mime_data = MockDragDropEvent.create_step_mime_data("mouse_click")
                drop_event = MockDragDropEvent.create_drop_event(mime_data)
                flow.dropEvent(drop_event)
                ctx.process_events(50)
                
            # Get step IDs
            step_ids = [step.step_id for step in flow.macro.steps]
            
            # Move first step to last position
            mime_data = MockDragDropEvent.create_move_mime_data(step_ids[0], 0)
            drop_event = MockDragDropEvent.create_drop_event(
                mime_data,
                QPoint(100, 300)  # Drop at bottom
            )
            flow.dropEvent(drop_event)
            ctx.process_events(100)
            
            # Verify order changed
            new_step_ids = [step.step_id for step in flow.macro.steps]
            assert new_step_ids == [step_ids[1], step_ids[2], step_ids[0]]
            
    def test_drop_at_specific_positions(self, app, macro_editor):
        """Test dropping at specific positions between steps"""
        with GUITestContext(app) as ctx:
            flow = macro_editor.flow_widget
            
            # Add initial steps
            for i in range(2):
                mime_data = MockDragDropEvent.create_step_mime_data("wait_time")
                drop_event = MockDragDropEvent.create_drop_event(mime_data)
                flow.dropEvent(drop_event)
                ctx.process_events(50)
                
            # Drop new step between existing ones
            mime_data = MockDragDropEvent.create_step_mime_data("keyboard_type")
            drop_event = MockDragDropEvent.create_drop_event(
                mime_data,
                QPoint(100, 75)  # Between first and second
            )
            flow.dropEvent(drop_event)
            ctx.process_events(100)
            
            # Verify insertion position
            assert len(flow.macro.steps) == 3
            assert flow.macro.steps[0].step_type == StepType.WAIT_TIME
            assert flow.macro.steps[1].step_type == StepType.KEYBOARD_TYPE
            assert flow.macro.steps[2].step_type == StepType.WAIT_TIME
            
    def test_drag_cancel(self, app, macro_editor):
        """Test canceling a drag operation"""
        with GUITestContext(app) as ctx:
            flow = macro_editor.flow_widget
            
            # Initial count
            initial_count = len(flow.macro.steps)
            
            # Start drag but don't drop
            mime_data = MockDragDropEvent.create_step_mime_data("click")
            drag_enter_event = MockDragDropEvent.create_drag_enter_event(mime_data)
            flow.dragEnterEvent(drag_enter_event)
            
            # Simulate drag leave (cancel)
            flow.dragLeaveEvent(None)
            ctx.process_events(100)
            
            # Verify no change
            assert len(flow.macro.steps) == initial_count
            
    def test_invalid_mime_data(self, app, macro_editor):
        """Test handling invalid mime data"""
        with GUITestContext(app) as ctx:
            flow = macro_editor.flow_widget
            
            # Create invalid mime data
            from PyQt5.QtCore import QMimeData
            mime_data = QMimeData()
            mime_data.setText("invalid data")
            
            # Try to drop
            drop_event = MockDragDropEvent.create_drop_event(mime_data)
            flow.dropEvent(drop_event)
            ctx.process_events(100)
            
            # Should not crash and no steps added
            assert len(flow.macro.steps) == 0


def run_tests():
    """Run tests standalone"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_tests()