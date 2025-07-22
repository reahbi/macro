"""
End-to-End tests for healthcare workflows based on WORKFLOW_EXAMPLES.md
Tests complete healthcare scenarios from Excel data to macro execution
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QTimer

from ui.main_window import MainWindow
from core.macro_types import (
    Macro, MacroStep, StepType, LoopStep, 
    KeyboardTypeStep, WaitTimeStep, MouseClickStep,
    DynamicTextSearchStep, IfConditionStep, ScreenshotStep
)
from excel.excel_manager import ExcelManager
from excel.models import ExcelData, ColumnMapping, ColumnType
from automation.engine import ExecutionEngine, ExecutionState
from core.macro_storage import MacroStorage
import uuid


@pytest.mark.e2e
class TestHealthcareCheckupWorkflow:
    """Test healthcare checkup result batch input workflow"""
    
    @pytest.fixture
    def test_data_path(self):
        """Get test data file path"""
        return Path(__file__).parent.parent.parent / "test_data" / "healthcare_checkup.xlsx"
    
    @pytest.fixture
    def excel_manager(self):
        """Create Excel manager instance"""
        return ExcelManager()
    
    @pytest.fixture
    def mock_pyautogui(self):
        """Mock pyautogui for testing"""
        with patch('pyautogui.click') as mock_click, \
             patch('pyautogui.typewrite') as mock_type, \
             patch('pyautogui.press') as mock_press, \
             patch('pyautogui.locateOnScreen') as mock_locate, \
             patch('pyautogui.screenshot') as mock_screenshot:
            
            # Configure mocks
            mock_locate.return_value = (100, 100, 50, 20)  # x, y, width, height
            mock_screenshot.return_value = MagicMock()
            
            yield {
                'click': mock_click,
                'typewrite': mock_type,
                'press': mock_press,
                'locate': mock_locate,
                'screenshot': mock_screenshot
            }
    
    @pytest.fixture
    def mock_ocr(self):
        """Mock OCR functionality"""
        with patch('vision.text_extractor.TextExtractor') as mock_extractor:
            mock_instance = Mock()
            mock_instance.find_text.return_value = [(100, 100)]  # Found at position
            mock_extractor.return_value = mock_instance
            yield mock_instance
    
    def create_checkup_macro(self) -> Macro:
        """Create healthcare checkup input macro based on WORKFLOW_EXAMPLES.md"""
        macro = Macro(
            name="건강검진 결과 일괄 입력",
            description="EMR 시스템에 검진 결과 자동 입력"
        )
        
        # Create main loop for Excel data
        loop_step = LoopStep(
            step_id=str(uuid.uuid4()),
            name="Excel 데이터 반복",
            loop_type="excel_rows"
        )
        
        # Steps inside the loop
        steps = [
            # 1. Find and click "환자조회"
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="환자조회 찾기",
                search_text="환자조회",
                click_on_found=True
            ),
            
            # 2. Type patient number
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="환자번호 입력",
                text="${환자번호}"
            ),
            
            # 3. Press Enter
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="Enter 키",
                text="{ENTER}"
            ),
            
            # 4. Wait for loading
            WaitTimeStep(
                step_id=str(uuid.uuid4()),
                name="로딩 대기",
                seconds=2.0
            ),
            
            # 5. Find and click "검진결과입력"
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="검진결과입력 찾기",
                search_text="검진결과입력",
                click_on_found=True
            ),
            
            # 6. Click blood pressure field
            MouseClickStep(
                step_id=str(uuid.uuid4()),
                name="혈압 입력란 클릭",
                x=300,
                y=200
            ),
            
            # 7. Type blood pressure
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="혈압 입력",
                text="${혈압}"
            ),
            
            # 8. Click blood sugar field
            MouseClickStep(
                step_id=str(uuid.uuid4()),
                name="혈당 입력란 클릭",
                x=300,
                y=250
            ),
            
            # 9. Type blood sugar
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="혈당 입력",
                text="${혈당}"
            ),
            
            # 10. Click cholesterol field
            MouseClickStep(
                step_id=str(uuid.uuid4()),
                name="콜레스테롤 입력란 클릭",
                x=300,
                y=300
            ),
            
            # 11. Type cholesterol
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="콜레스테롤 입력",
                text="${콜레스테롤}"
            ),
            
            # 12. Click judgment field
            MouseClickStep(
                step_id=str(uuid.uuid4()),
                name="판정 선택란 클릭",
                x=300,
                y=350
            ),
            
            # 13. Find and click judgment value
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="판정 선택",
                search_text="${판정}",
                click_on_found=True
            ),
            
            # 14. Find and click "저장"
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="저장 버튼 클릭",
                search_text="저장",
                click_on_found=True
            ),
            
            # 15. Wait
            WaitTimeStep(
                step_id=str(uuid.uuid4()),
                name="저장 대기",
                seconds=1.0
            ),
            
            # 16. Find and click "확인"
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="확인 팝업 클릭",
                search_text="확인",
                click_on_found=True
            )
        ]
        
        # Add steps to loop
        loop_step.steps = steps
        macro.add_step(loop_step)
        
        return macro
    
    def test_checkup_workflow_execution(self, excel_manager, test_data_path, 
                                      mock_pyautogui, mock_ocr):
        """Test complete healthcare checkup workflow execution"""
        # Load Excel data
        file_info = excel_manager.load_file(str(test_data_path))
        assert file_info is not None
        assert len(file_info.sheets) > 0
        
        # Select sheet and create column mappings
        excel_manager.set_active_sheet("검진결과")
        
        # Create column mappings
        mappings = [
            ColumnMapping("환자번호", "환자번호", ColumnType.TEXT),
            ColumnMapping("이름", "이름", ColumnType.TEXT),
            ColumnMapping("혈압", "혈압", ColumnType.TEXT),
            ColumnMapping("혈당", "혈당", ColumnType.NUMBER),
            ColumnMapping("콜레스테롤", "콜레스테롤", ColumnType.NUMBER),
            ColumnMapping("판정", "판정", ColumnType.TEXT)
        ]
        excel_manager.set_column_mappings(mappings)
        
        # Get Excel data
        excel_data = excel_manager.get_mapped_data()
        assert excel_data is not None
        assert excel_data.total_rows == 5  # 5 patients in test data
        
        # Create macro
        macro = self.create_checkup_macro()
        assert len(macro.steps) == 1  # One loop step
        assert isinstance(macro.steps[0], LoopStep)
        
        # Create execution engine
        with patch('automation.engine.ExecutionEngine') as MockEngine:
            engine_instance = Mock()
            MockEngine.return_value = engine_instance
            
            # Configure engine mock
            engine_instance.state = ExecutionState.IDLE
            engine_instance.current_row = 0
            
            # Simulate execution
            def simulate_execution(macro, excel_data):
                # Simulate processing each row
                for idx, row in excel_data.data.iterrows():
                    # Verify text searches are called
                    mock_ocr.find_text.assert_any_call("환자조회")
                    mock_ocr.find_text.assert_any_call("검진결과입력")
                    
                    # Verify data input
                    expected_calls = [
                        call(row['환자번호']),
                        call(str(row['혈압'])),
                        call(str(row['혈당'])),
                        call(str(row['콜레스테롤']))
                    ]
                    
                    # Verify mouse clicks
                    assert mock_pyautogui['click'].call_count >= 3
                    
                    # Verify Enter key press
                    mock_pyautogui['press'].assert_any_call('enter')
            
            engine_instance.execute.side_effect = lambda m, d: simulate_execution(m, d)
            
            # Execute macro
            engine = MockEngine()
            engine.execute(macro, excel_data)
            
            # Verify execution was called
            engine.execute.assert_called_once_with(macro, excel_data)
    
    def test_checkup_workflow_with_conditions(self, excel_manager, test_data_path):
        """Test checkup workflow with conditional logic"""
        # Create macro with condition for "재검" cases
        macro = self.create_checkup_macro()
        
        # Add conditional step for re-examination
        condition_step = IfConditionStep(
            step_id=str(uuid.uuid4()),
            name="재검 여부 확인",
            condition_type="variable_equals",
            condition_value={"variable": "판정", "value": "재검"},
            true_steps=[
                # Additional steps for re-examination
                DynamicTextSearchStep(
                    step_id=str(uuid.uuid4()),
                    name="재검사유 입력",
                    search_text="재검사유",
                    click_on_found=True
                ),
                KeyboardTypeStep(
                    step_id=str(uuid.uuid4()),
                    name="사유 입력",
                    text="정밀검사 필요"
                )
            ],
            false_steps=[]
        )
        
        # Insert condition after judgment selection
        loop_step = macro.steps[0]
        loop_step.steps.insert(14, condition_step)
        
        # Verify macro structure
        assert len(loop_step.steps) == 17  # Original 16 + 1 condition
        assert isinstance(loop_step.steps[14], IfConditionStep)


@pytest.mark.e2e
class TestPrescriptionWorkflow:
    """Test prescription issuance workflow"""
    
    @pytest.fixture
    def test_data_path(self):
        """Get test data file path"""
        return Path(__file__).parent.parent.parent / "test_data" / "prescription_data.xlsx"
    
    def create_prescription_macro(self) -> Macro:
        """Create prescription issuance macro"""
        macro = Macro(
            name="처방전 일괄 발행",
            description="만성질환자 정기 처방전 발행"
        )
        
        # Main loop
        loop_step = LoopStep(
            step_id=str(uuid.uuid4()),
            name="처방 대상자 반복",
            loop_type="excel_rows"
        )
        
        # Steps inside loop
        steps = [
            # 1. Click prescription menu
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="처방 메뉴 클릭",
                search_text="처방",
                click_on_found=True
            ),
            
            # 2. Type patient number
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="환자번호 입력",
                text="${환자번호}"
            ),
            
            # 3. Wait
            WaitTimeStep(
                step_id=str(uuid.uuid4()),
                name="대기",
                seconds=1.0
            ),
            
            # 4. Add medicine button
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="약품추가 버튼",
                search_text="약품추가",
                click_on_found=True
            ),
            
            # 5. Type medicine code 1
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="약품코드1 입력",
                text="${약품코드1}"
            ),
            
            # 6. Tab key
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="Tab 키",
                text="{TAB}"
            ),
            
            # 7. Type dosage 1
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="용량1 입력",
                text="${용량1}"
            ),
            
            # 8. Add button
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="추가 버튼",
                search_text="추가",
                click_on_found=True
            ),
            
            # 9. Condition for second medicine
            IfConditionStep(
                step_id=str(uuid.uuid4()),
                name="약품2 확인",
                condition="${약품코드2} != ''",
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
            ),
            
            # 10. Click days field
            MouseClickStep(
                step_id=str(uuid.uuid4()),
                name="처방일수 클릭",
                x=400,
                y=400
            ),
            
            # 11. Type days
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="일수 입력",
                text="${일수}"
            ),
            
            # 12. Save prescription
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="처방저장",
                search_text="처방저장",
                click_on_found=True
            ),
            
            # 13. Screenshot
            ScreenshotStep(
                step_id=str(uuid.uuid4()),
                name="처방전 캡처",
                filename_pattern="prescription_${환자번호}.png",
                save_directory="captures/"
            ),
            
            # 14. Print button
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="출력 버튼",
                search_text="출력",
                click_on_found=True
            )
        ]
        
        loop_step.steps = steps
        macro.add_step(loop_step)
        
        return macro
    
    def test_prescription_workflow_with_conditions(self, test_data_path):
        """Test prescription workflow with conditional medicine addition"""
        # Load test data
        excel_manager = ExcelManager()
        file_info = excel_manager.load_file(str(test_data_path))
        excel_manager.set_active_sheet("처방목록")
        
        # Verify data
        df = excel_manager.get_sheet_data()
        assert len(df) == 4  # 4 patients
        
        # Check conditional data
        # P102 has no second medicine
        p102_data = df[df['환자번호'] == 'P102'].iloc[0]
        assert p102_data['약품코드2'] == '' or pd.isna(p102_data['약품코드2'])
        
        # Create and verify macro
        macro = self.create_prescription_macro()
        
        # Find condition step
        loop_step = macro.steps[0]
        condition_step = None
        for step in loop_step.steps:
            if isinstance(step, IfConditionStep):
                condition_step = step
                break
        
        assert condition_step is not None
        assert condition_step.condition == "${약품코드2} != ''"
        assert len(condition_step.true_steps) == 5  # 5 steps for second medicine