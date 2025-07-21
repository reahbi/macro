"""
End-to-End tests for office workflows based on WORKFLOW_EXAMPLES.md
Tests complete office automation scenarios
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from datetime import datetime

from core.macro_types import (
    Macro, MacroStep, StepType, LoopStep,
    KeyboardTypeStep, WaitTimeStep, MouseClickStep,
    DynamicTextSearchStep, IfConditionStep
)
from excel.excel_manager import ExcelManager
from excel.models import ExcelData, ColumnMapping, ColumnType
from automation.engine import ExecutionEngine
import uuid


@pytest.mark.e2e
class TestElectronicApprovalWorkflow:
    """Test electronic approval batch submission workflow"""
    
    @pytest.fixture
    def test_data_path(self):
        """Get test data file path"""
        return Path(__file__).parent.parent.parent / "test_data" / "approval_data.xlsx"
    
    @pytest.fixture
    def mock_file_dialog(self):
        """Mock file dialog for attachment handling"""
        with patch('PyQt5.QtWidgets.QFileDialog.getOpenFileName') as mock_dialog:
            mock_dialog.return_value = ("C:\\test\\file.pdf", "PDF Files (*.pdf)")
            yield mock_dialog
    
    def create_approval_macro(self) -> Macro:
        """Create electronic approval submission macro"""
        macro = Macro(
            name="전자결재 일괄 상신",
            description="여러 건의 품의서를 그룹웨어에 일괄 상신"
        )
        
        # Main loop for approval list
        loop_step = LoopStep(
            step_id=str(uuid.uuid4()),
            name="품의서 목록 반복",
            loop_type="excel_rows"
        )
        
        steps = [
            # 1. Click new approval
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="새결재 버튼 클릭",
                search_text="새결재",
                click_on_found=True
            ),
            
            # 2. Select approval form
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="일반품의 양식 선택",
                search_text="일반품의",
                click_on_found=True
            ),
            
            # 3. Wait for form loading
            WaitTimeStep(
                step_id=str(uuid.uuid4()),
                name="양식 로딩 대기",
                seconds=2.0
            ),
            
            # 4. Click title field
            MouseClickStep(
                step_id=str(uuid.uuid4()),
                name="제목 입력란 클릭",
                x=300,
                y=150
            ),
            
            # 5. Type title
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="제목 입력",
                search_text="${제목}"
            ),
            
            # 6. Click amount field
            MouseClickStep(
                step_id=str(uuid.uuid4()),
                name="금액 입력란 클릭",
                x=300,
                y=200
            ),
            
            # 7. Type amount
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="금액 입력",
                search_text="${금액}"
            ),
            
            # 8. Click content field
            MouseClickStep(
                step_id=str(uuid.uuid4()),
                name="내용 입력란 클릭",
                x=300,
                y=300
            ),
            
            # 9. Type content
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="내용 입력",
                search_text="${내용}"
            ),
            
            # 10. Click approval line
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="결재선지정 클릭",
                search_text="결재선지정",
                click_on_found=True
            ),
            
            # 11. Search and add first approver
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="결재선1 검색",
                search_text="${결재선1}",
                click_on_found=True
            ),
            
            # 12. Search and add second approver
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="결재선2 검색",
                search_text="${결재선2}",
                click_on_found=True
            ),
            
            # 13. Confirm approval line
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="확인 클릭",
                search_text="확인",
                click_on_found=True
            ),
            
            # 14. Condition for attachment
            IfConditionStep(
                step_id=str(uuid.uuid4()),
                name="첨부파일 확인",
                condition="${첨부파일} != ''",
                true_steps=[
                    DynamicTextSearchStep(
                        step_id=str(uuid.uuid4()),
                        name="파일첨부 클릭",
                        search_text="파일첨부",
                        click_on_found=True
                    ),
                    KeyboardTypeStep(
                        step_id=str(uuid.uuid4()),
                        name="파일경로 입력",
                        search_text="${첨부파일}"
                    ),
                    DynamicTextSearchStep(
                        step_id=str(uuid.uuid4()),
                        name="열기 클릭",
                        search_text="열기",
                        click_on_found=True
                    )
                ],
                false_steps=[]
            ),
            
            # 15. Submit approval
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="상신 버튼 클릭",
                search_text="상신",
                click_on_found=True
            ),
            
            # 16. Confirm popup
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="확인 팝업 클릭",
                search_text="확인",
                click_on_found=True
            ),
            
            # 17. Wait for next
            WaitTimeStep(
                step_id=str(uuid.uuid4()),
                name="다음 건 대기",
                seconds=3.0
            )
        ]
        
        loop_step.steps = steps
        macro.add_step(loop_step)
        
        return macro
    
    def test_approval_workflow_execution(self, test_data_path):
        """Test electronic approval workflow execution"""
        # Load Excel data
        excel_manager = ExcelManager()
        file_info = excel_manager.load_file(str(test_data_path))
        excel_manager.set_active_sheet("결재목록")
        
        # Create column mappings
        mappings = [
            ColumnMapping("제목", "제목", ColumnType.TEXT),
            ColumnMapping("금액", "금액", ColumnType.NUMBER),
            ColumnMapping("내용", "내용", ColumnType.TEXT),
            ColumnMapping("결재선1", "결재선1", ColumnType.TEXT),
            ColumnMapping("결재선2", "결재선2", ColumnType.TEXT),
            ColumnMapping("첨부파일", "첨부파일", ColumnType.TEXT)
        ]
        excel_manager.set_column_mappings(mappings)
        
        # Get data
        excel_data = excel_manager.get_mapped_data()
        assert excel_data.total_rows == 4  # 4 approvals
        
        # Create macro
        macro = self.create_approval_macro()
        
        # Verify conditional attachment handling
        loop_step = macro.steps[0]
        attachment_condition = None
        for step in loop_step.steps:
            if isinstance(step, IfConditionStep) and "첨부파일" in step.name:
                attachment_condition = step
                break
        
        assert attachment_condition is not None
        assert len(attachment_condition.true_steps) == 3  # 3 steps for attachment
        
        # Check data variations
        df = excel_data.data
        # Second row has no attachment
        assert df.iloc[1]['첨부파일'] == '' or pd.isna(df.iloc[1]['첨부파일'])
        # First row has attachment
        assert df.iloc[0]['첨부파일'] != ''


@pytest.mark.e2e 
class TestPayslipEmailWorkflow:
    """Test payslip email sending workflow"""
    
    def create_payslip_macro(self) -> Macro:
        """Create payslip email sending macro"""
        macro = Macro(
            name="급여명세서 이메일 발송",
            description="전 직원 급여명세서 개별 이메일 발송"
        )
        
        # Create test data inline
        loop_step = LoopStep(
            step_id=str(uuid.uuid4()),
            name="직원 목록 반복",
            loop_type="excel_rows"
        )
        
        steps = [
            # 1. New email
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="새메일 버튼 클릭",
                search_text="새메일",
                click_on_found=True
            ),
            
            # 2. Click recipient field
            MouseClickStep(
                step_id=str(uuid.uuid4()),
                name="받는사람 입력란 클릭",
                x=300,
                y=100
            ),
            
            # 3. Type email
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="이메일 입력",
                search_text="${이메일}"
            ),
            
            # 4. Click subject field
            MouseClickStep(
                step_id=str(uuid.uuid4()),
                name="제목 입력란 클릭",
                x=300,
                y=150
            ),
            
            # 5. Type subject with template
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="제목 입력",
                search_text="[2024년 1월] ${이름}님 급여명세서"
            ),
            
            # 6. Click body field
            MouseClickStep(
                step_id=str(uuid.uuid4()),
                name="본문 입력란 클릭",
                x=300,
                y=250
            ),
            
            # 7. Type body with template
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="본문 입력",
                search_text="안녕하세요 ${이름}님,\\n1월 급여명세서를 첨부합니다."
            ),
            
            # 8. File attachment
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="파일첨부 클릭",
                search_text="파일첨부",
                click_on_found=True
            ),
            
            # 9. Type file path
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="파일경로 입력",
                search_text="${급여명세서경로}"
            ),
            
            # 10. Click open
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="열기 클릭",
                search_text="열기",
                click_on_found=True
            ),
            
            # 11. Wait for attachment
            WaitTimeStep(
                step_id=str(uuid.uuid4()),
                name="첨부 완료 대기",
                seconds=2.0
            ),
            
            # 12. Send email
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="보내기 클릭",
                search_text="보내기",
                click_on_found=True
            ),
            
            # 13. Wait before next
            WaitTimeStep(
                step_id=str(uuid.uuid4()),
                name="다음 메일 대기",
                seconds=1.0
            )
        ]
        
        loop_step.steps = steps
        macro.add_step(loop_step)
        
        return macro
    
    def test_payslip_template_substitution(self):
        """Test template string substitution in payslip workflow"""
        # Create sample data
        test_data = pd.DataFrame({
            '사번': ['E001', 'E002'],
            '이름': ['홍길동', '김철수'],
            '이메일': ['hong@company.com', 'kim@company.com'],
            '급여명세서경로': [
                'C:\\급여\\2024-01\\E001.pdf',
                'C:\\급여\\2024-01\\E002.pdf'
            ]
        })
        
        # Create macro
        macro = self.create_payslip_macro()
        loop_step = macro.steps[0]
        
        # Find template steps
        subject_step = None
        body_step = None
        
        for step in loop_step.steps:
            if isinstance(step, KeyboardTypeStep):
                if "제목 입력" in step.name:
                    subject_step = step
                elif "본문 입력" in step.name:
                    body_step = step
        
        # Verify templates
        assert subject_step is not None
        assert "${이름}" in subject_step.text
        assert "[2024년 1월]" in subject_step.text
        
        assert body_step is not None
        assert "${이름}" in body_step.text
        assert "\\n" in body_step.text  # Line break
        
        # Test variable substitution simulation
        for _, row in test_data.iterrows():
            # Simulate substitution
            subject = subject_step.text.replace("${이름}", row['이름'])
            assert row['이름'] in subject
            assert "[2024년 1월]" in subject
            
            body = body_step.text.replace("${이름}", row['이름'])
            body = body.replace("\\n", "\n")
            assert row['이름'] in body
            assert "급여명세서를 첨부합니다" in body