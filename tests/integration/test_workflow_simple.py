"""
Simple workflow integration test
"""

import pytest
from pathlib import Path
import sys
import uuid

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

@pytest.mark.integration
class TestWorkflowSimple:
    """Test simple workflow execution"""
    
    def test_basic_workflow_creation(self):
        """Test creating a basic workflow without imports"""
        # Direct imports to avoid encryption
        from core.macro_types import Macro, LoopStep, MacroStep, StepType
        from core.macro_types import KeyboardTypeStep, WaitTimeStep, MouseClickStep
        
        # Create macro
        macro = Macro(
            name="Simple Test Macro",
            description="Basic workflow test"
        )
        
        # Add simple steps
        steps = [
            MouseClickStep(
                step_id=str(uuid.uuid4()),
                name="Click Button",
                x=100,
                y=200
            ),
            WaitTimeStep(
                step_id=str(uuid.uuid4()),
                name="Wait",
                seconds=1.0
            ),
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="Type Text",
                text="Hello World"
            )
        ]
        
        for step in steps:
            macro.add_step(step)
        
        # Verify
        assert len(macro.steps) == 3
        assert isinstance(macro.steps[0], MouseClickStep)
        assert macro.steps[0].x == 100
        assert macro.steps[0].y == 200
        
        assert isinstance(macro.steps[1], WaitTimeStep)
        assert macro.steps[1].seconds == 1.0
        
        assert isinstance(macro.steps[2], KeyboardTypeStep)
        assert macro.steps[2].text == "Hello World"
    
    def test_workflow_with_variables(self):
        """Test workflow with Excel variables"""
        from core.macro_types import Macro, LoopStep
        from core.macro_types import KeyboardTypeStep
        
        macro = Macro(
            name="Variable Test",
            description="Test Excel variables"
        )
        
        loop = LoopStep(
            step_id=str(uuid.uuid4()),
            name="Data Loop",
            loop_type="excel_rows"
        )
        
        # Add steps with variables
        loop.steps = [
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="Type Name",
                text="${name}"
            ),
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="Type Email",
                text="${email}"
            )
        ]
        
        macro.add_step(loop)
        
        # Verify
        assert len(macro.steps) == 1
        assert isinstance(macro.steps[0], LoopStep)
        assert len(macro.steps[0].steps) == 2
        
        # Check variables
        for step in macro.steps[0].steps:
            assert "${" in step.text
            assert "}" in step.text