"""
Isolated workflow test without encryption dependencies
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Mock encryption before any imports
sys.modules['utils.encryption'] = MagicMock()
sys.modules['cryptography'] = MagicMock()
sys.modules['cryptography.hazmat'] = MagicMock()
sys.modules['cryptography.hazmat.primitives'] = MagicMock()
sys.modules['cryptography.hazmat.primitives.ciphers'] = MagicMock()

@pytest.mark.e2e
class TestWorkflowIsolated:
    """Test workflow with fully isolated imports"""
    
    def test_healthcare_workflow_complete(self):
        """Test complete healthcare workflow"""
        from core.macro_types import Macro, LoopStep, IfConditionStep
        from core.dynamic_text_step import DynamicTextSearchStep
        from core.macro_types import KeyboardTypeStep, WaitTimeStep, MouseClickStep
        import uuid
        
        # Create healthcare macro
        macro = Macro(
            name="건강검진 결과 일괄 입력",
            description="EMR 시스템에 검진 결과 자동 입력"
        )
        
        # Create main loop
        loop_step = LoopStep(
            step_id=str(uuid.uuid4()),
            name="Excel 데이터 반복",
            loop_type="excel_rows"
        )
        
        # Create all steps from WORKFLOW_EXAMPLES.md
        steps = [
            # 1. 환자조회
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="환자조회 찾기",
                search_text="환자조회",
                click_on_found=True
            ),
            # 2. 환자번호 입력
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="환자번호 입력",
                text="${환자번호}"
            ),
            # 3. Enter
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="Enter 키",
                text="{ENTER}"
            ),
            # 4. 대기
            WaitTimeStep(
                step_id=str(uuid.uuid4()),
                name="로딩 대기",
                seconds=2.0
            ),
            # 5. 검진결과입력
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="검진결과입력 찾기",
                search_text="검진결과입력",
                click_on_found=True
            ),
            # 6-7. 혈압
            MouseClickStep(
                step_id=str(uuid.uuid4()),
                name="혈압 입력란 클릭",
                x=300,
                y=200
            ),
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="혈압 입력",
                text="${혈압}"
            ),
            # 8-9. 혈당
            MouseClickStep(
                step_id=str(uuid.uuid4()),
                name="혈당 입력란 클릭",
                x=300,
                y=250
            ),
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="혈당 입력",
                text="${혈당}"
            ),
            # 10-11. 콜레스테롤
            MouseClickStep(
                step_id=str(uuid.uuid4()),
                name="콜레스테롤 입력란 클릭",
                x=300,
                y=300
            ),
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="콜레스테롤 입력",
                text="${콜레스테롤}"
            ),
            # 12-13. 판정
            MouseClickStep(
                step_id=str(uuid.uuid4()),
                name="판정 선택란 클릭",
                x=300,
                y=350
            ),
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="판정 선택",
                search_text="${판정}",
                click_on_found=True
            ),
            # 14. 저장
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="저장 버튼 클릭",
                search_text="저장",
                click_on_found=True
            ),
            # 15. 대기
            WaitTimeStep(
                step_id=str(uuid.uuid4()),
                name="저장 대기",
                seconds=1.0
            ),
            # 16. 확인
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="확인 팝업 클릭",
                search_text="확인",
                click_on_found=True
            )
        ]
        
        loop_step.steps = steps
        macro.add_step(loop_step)
        
        # Verify structure
        assert len(macro.steps) == 1
        assert isinstance(macro.steps[0], LoopStep)
        assert len(loop_step.steps) == 16  # All steps as per workflow
        
        # Verify variable placeholders
        keyboard_steps = [s for s in loop_step.steps if isinstance(s, KeyboardTypeStep)]
        variable_steps = [s for s in keyboard_steps if '${' in s.text]
        assert len(variable_steps) == 4  # 환자번호, 혈압, 혈당, 콜레스테롤
        
        # Verify dynamic text searches
        search_steps = [s for s in loop_step.steps if isinstance(s, DynamicTextSearchStep)]
        assert len(search_steps) == 5  # 환자조회, 검진결과입력, 판정, 저장, 확인
        
    def test_prescription_workflow_with_condition(self):
        """Test prescription workflow with conditional logic"""
        from core.macro_types import Macro, LoopStep, IfConditionStep
        from core.dynamic_text_step import DynamicTextSearchStep
        from core.macro_types import KeyboardTypeStep, WaitTimeStep, ScreenshotStep
        import uuid
        
        macro = Macro(
            name="처방전 일괄 발행",
            description="만성질환자 정기 처방전 발행"
        )
        
        loop = LoopStep(
            step_id=str(uuid.uuid4()),
            name="처방 대상자 반복",
            loop_type="excel_rows"
        )
        
        # Condition for second medicine
        medicine2_condition = IfConditionStep(
            step_id=str(uuid.uuid4()),
            name="약품2 확인",
            condition_type="variable_equals",
            condition_value={"variable": "약품코드2", "value": "", "negate": True},
            true_steps=[
                DynamicTextSearchStep(
                    step_id=str(uuid.uuid4()),
                    name="약품추가 버튼2",
                    search_text="약품추가",
                    click_on_found=True
                ),
                KeyboardTypeStep(
                    step_id=str(uuid.uuid4()),
                    name="약품코드2 입력",
                    text="${약품코드2}"
                ),
                KeyboardTypeStep(
                    step_id=str(uuid.uuid4()),
                    name="Tab 키2",
                    text="{TAB}"
                ),
                KeyboardTypeStep(
                    step_id=str(uuid.uuid4()),
                    name="용량2 입력",
                    text="${용량2}"
                ),
                DynamicTextSearchStep(
                    step_id=str(uuid.uuid4()),
                    name="추가 버튼2",
                    search_text="추가",
                    click_on_found=True
                )
            ],
            false_steps=[]
        )
        
        # Add to main loop
        loop.steps = [
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="처방 메뉴",
                search_text="처방",
                click_on_found=True
            ),
            medicine2_condition,
            ScreenshotStep(
                step_id=str(uuid.uuid4()),
                name="처방전 화면 캡처",
                filename_pattern="prescription_${환자번호}.png",
                save_directory="captures/"
            )
        ]
        
        macro.add_step(loop)
        
        # Verify conditional structure
        assert isinstance(loop.steps[1], IfConditionStep)
        assert len(loop.steps[1].true_steps) == 5
        assert loop.steps[1].condition_type == "variable_equals"
        assert loop.steps[1].condition_value["negate"] == True