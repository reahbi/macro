"""
Workflow test with mocked dependencies
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.mark.e2e
class TestWorkflowWithMocks:
    """Test workflow with mocked pandas/numpy"""
    
    @patch('pandas.read_excel')
    @patch('pandas.DataFrame')
    def test_healthcare_workflow_mocked(self, mock_dataframe, mock_read_excel):
        """Test healthcare workflow with mocks"""
        from core.macro_types import Macro, LoopStep
        from core.dynamic_text_step import DynamicTextSearchStep
        from core.macro_types import KeyboardTypeStep, WaitTimeStep
        import uuid
        
        # Mock pandas DataFrame
        mock_df = MagicMock()
        mock_df.shape = (5, 7)
        mock_df.columns = ['환자번호', '이름', '혈압', '혈당', '콜레스테롤', '판정']
        mock_df.iterrows.return_value = [
            (0, {'환자번호': 'P001', '이름': '홍길동', '혈압': '120/80'}),
            (1, {'환자번호': 'P002', '이름': '김영희', '혈압': '130/85'})
        ]
        mock_dataframe.return_value = mock_df
        mock_read_excel.return_value = mock_df
        
        # Create macro
        macro = Macro(
            name="건강검진 결과 입력",
            description="Test healthcare workflow"
        )
        
        # Create loop
        loop_step = LoopStep(
            step_id=str(uuid.uuid4()),
            name="환자 데이터 반복",
            loop_type="excel_rows"
        )
        
        # Create steps
        steps = [
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="환자조회 찾기",
                search_text="환자조회",
                click_on_found=True
            ),
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="환자번호 입력",
                text="${환자번호}"
            ),
            WaitTimeStep(
                step_id=str(uuid.uuid4()),
                name="대기",
                seconds=2.0
            ),
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="검진결과입력 찾기",
                search_text="검진결과입력",
                click_on_found=True
            ),
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="혈압 입력",
                text="${혈압}"
            )
        ]
        
        loop_step.steps = steps
        macro.add_step(loop_step)
        
        # Verify structure
        assert len(macro.steps) == 1
        assert isinstance(macro.steps[0], LoopStep)
        assert len(loop_step.steps) == 5
        
        # Verify steps
        assert isinstance(loop_step.steps[0], DynamicTextSearchStep)
        assert loop_step.steps[0].search_text == "환자조회"
        assert loop_step.steps[0].click_on_found == True
        
        assert isinstance(loop_step.steps[1], KeyboardTypeStep)
        assert loop_step.steps[1].text == "${환자번호}"
        
        assert isinstance(loop_step.steps[2], WaitTimeStep)
        assert loop_step.steps[2].seconds == 2.0
    
    def test_office_workflow_structure(self):
        """Test office workflow structure"""
        import sys
        # Avoid importing through core.__init__ to prevent encryption import
        import core.macro_types
        Macro = core.macro_types.Macro
        LoopStep = core.macro_types.LoopStep
        IfConditionStep = core.macro_types.IfConditionStep
        KeyboardTypeStep = core.macro_types.KeyboardTypeStep
        WaitTimeStep = core.macro_types.WaitTimeStep
        MouseClickStep = core.macro_types.MouseClickStep
        
        from core.dynamic_text_step import DynamicTextSearchStep
        import uuid
        
        # Create approval workflow
        macro = Macro(
            name="전자결재 일괄 상신",
            description="Office approval workflow"
        )
        
        loop = LoopStep(
            step_id=str(uuid.uuid4()),
            name="품의서 반복",
            loop_type="excel_rows"
        )
        
        # Create conditional step for attachment
        attachment_condition = IfConditionStep(
            step_id=str(uuid.uuid4()),
            name="첨부파일 확인",
            condition_type="variable_equals",
            condition_value={"variable": "첨부파일", "value": "", "negate": True},
            true_steps=[
                DynamicTextSearchStep(
                    step_id=str(uuid.uuid4()),
                    name="파일첨부",
                    search_text="파일첨부",
                    click_on_found=True
                ),
                KeyboardTypeStep(
                    step_id=str(uuid.uuid4()),
                    name="파일경로",
                    text="${첨부파일}"
                )
            ],
            false_steps=[]
        )
        
        # Add steps including condition
        loop.steps = [
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="새결재",
                search_text="새결재",
                click_on_found=True
            ),
            WaitTimeStep(
                step_id=str(uuid.uuid4()),
                name="대기",
                seconds=2.0
            ),
            attachment_condition,
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="상신",
                search_text="상신",
                click_on_found=True
            )
        ]
        
        macro.add_step(loop)
        
        # Verify structure
        assert len(macro.steps) == 1
        assert len(loop.steps) == 4
        assert isinstance(loop.steps[2], IfConditionStep)
        assert len(loop.steps[2].true_steps) == 2
        assert loop.steps[2].condition_type == "variable_equals"
        assert loop.steps[2].condition_value["negate"] == True