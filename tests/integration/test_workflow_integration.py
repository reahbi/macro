"""
Integration tests for complete workflows
Tests the integration of Excel data, macro creation, and execution engine
"""

import pytest
import pandas as pd
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import uuid

from excel.excel_manager import ExcelManager
from excel.models import ExcelData, ColumnMapping, ColumnType
from automation.engine import ExecutionEngine, ExecutionState
from automation.executor import StepExecutor
from core.macro_types import (
    Macro, LoopStep, DynamicTextSearchStep, 
    KeyboardTypeStep, WaitTimeStep, IfConditionStep,
    MouseClickStep
)
from core.macro_storage import MacroStorage
from logger.execution_logger import ExecutionLogger
from config.settings import Settings


@pytest.mark.integration
class TestWorkflowIntegration:
    """Test integration of Excel data processing with macro execution"""
    
    @pytest.fixture
    def mock_settings(self):
        """Create mock settings"""
        settings = Mock(spec=Settings)
        settings.get.side_effect = lambda key, default=None: {
            'execution.default_delay_ms': 100,
            'execution.screenshot_on_error': True,
            'macro.recent_files': []
        }.get(key, default)
        return settings
    
    @pytest.fixture
    def excel_manager(self):
        """Create Excel manager"""
        return ExcelManager()
    
    @pytest.fixture
    def execution_engine(self, mock_settings):
        """Create execution engine with mocked dependencies"""
        with patch('automation.hotkey_listener.HotkeyListener'):
            with patch('logger.execution_logger.get_execution_logger'):
                engine = ExecutionEngine(mock_settings)
                return engine
    
    @pytest.fixture
    def mock_step_executor(self):
        """Mock step executor"""
        with patch('automation.executor.StepExecutor') as mock_executor:
            instance = Mock()
            instance.execute.return_value = (True, None)
            mock_executor.return_value = instance
            yield instance
    
    def test_excel_to_macro_variable_mapping(self, excel_manager):
        """Test Excel column to macro variable mapping"""
        # Create test Excel data
        test_data = pd.DataFrame({
            '고객번호': ['C001', 'C002', 'C003'],
            '고객명': ['테스트1', '테스트2', '테스트3'],
            '연락처': ['010-1111-1111', '010-2222-2222', '010-3333-3333']
        })
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            test_data.to_excel(tmp.name, index=False, sheet_name='고객목록')
            
            # Load Excel file
            file_info = excel_manager.load_file(tmp.name)
            excel_manager.set_active_sheet('고객목록')
            
            # Create column mappings
            mappings = [
                ColumnMapping('고객번호', '고객번호', ColumnType.TEXT),
                ColumnMapping('고객명', '고객명', ColumnType.TEXT),
                ColumnMapping('연락처', '연락처', ColumnType.TEXT)
            ]
            excel_manager.set_column_mappings(mappings)
            
            # Get mapped data
            excel_data = excel_manager.get_mapped_data()
            
            # Verify mapping
            assert excel_data.total_rows == 3
            assert '고객번호' in excel_data.column_names
            assert excel_data.data.iloc[0]['고객번호'] == 'C001'
    
    def test_dynamic_text_search_with_excel_variable(self, excel_manager, mock_step_executor):
        """Test dynamic text search with Excel variable substitution"""
        # Create test data with search text
        test_data = pd.DataFrame({
            '검색어': ['확인', '저장', '취소'],
            '클릭여부': ['Y', 'Y', 'N']
        })
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            test_data.to_excel(tmp.name, index=False)
            
            # Load and map data
            excel_manager.load_file(tmp.name)
            excel_manager.set_active_sheet('Sheet1')
            mappings = [
                ColumnMapping('검색어', '검색어', ColumnType.TEXT),
                ColumnMapping('클릭여부', '클릭여부', ColumnType.TEXT)
            ]
            excel_manager.set_column_mappings(mappings)
            excel_data = excel_manager.get_mapped_data()
            
            # Create macro with dynamic text search
            macro = Macro("텍스트 검색 테스트")
            loop_step = LoopStep(
                step_id=str(uuid.uuid4()),
                name="검색어 반복",
                loop_type="excel_rows"
            )
            
            # Add dynamic text search step
            search_step = DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="텍스트 검색",
                search_text="${검색어}",
                click_on_found=True
            )
            
            # Add condition based on click flag
            condition_step = IfConditionStep(
                step_id=str(uuid.uuid4()),
                name="클릭 여부 확인",
                condition="${클릭여부} == 'Y'",
                true_steps=[search_step],
                false_steps=[]
            )
            
            loop_step.steps = [condition_step]
            macro.add_step(loop_step)
            
            # Verify macro structure
            assert len(macro.steps) == 1
            assert isinstance(macro.steps[0], LoopStep)
            assert len(loop_step.steps) == 1
            assert isinstance(loop_step.steps[0], IfConditionStep)
    
    def test_complex_workflow_execution_simulation(self, excel_manager, execution_engine, mock_step_executor):
        """Test complex workflow with multiple step types"""
        # Create comprehensive test data
        test_data = pd.DataFrame({
            '작업유형': ['입력', '검색', '대기'],
            '대상': ['홍길동', '저장', ''],
            '값': ['서울시 강남구', '', '3'],
            '조건': ['Y', 'Y', 'N']
        })
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            test_data.to_excel(tmp.name, index=False)
            
            # Load data
            excel_manager.load_file(tmp.name)
            excel_manager.set_active_sheet('Sheet1')
            mappings = [
                ColumnMapping('작업유형', '작업유형', ColumnType.TEXT),
                ColumnMapping('대상', '대상', ColumnType.TEXT),
                ColumnMapping('값', '값', ColumnType.TEXT),
                ColumnMapping('조건', '조건', ColumnType.TEXT)
            ]
            excel_manager.set_column_mappings(mappings)
            excel_data = excel_manager.get_mapped_data()
            
            # Create complex macro
            macro = Macro("복합 워크플로우")
            loop_step = LoopStep(
                step_id=str(uuid.uuid4()),
                name="작업 반복",
                loop_type="excel_rows"
            )
            
            # Multiple conditions based on work type
            type_condition = IfConditionStep(
                step_id=str(uuid.uuid4()),
                name="작업 유형 분기",
                condition="${작업유형} == '입력'",
                true_steps=[
                    KeyboardTypeStep(
                        step_id=str(uuid.uuid4()),
                        name="데이터 입력",
                        search_text="${값}"
                    )
                ],
                false_steps=[
                    IfConditionStep(
                        step_id=str(uuid.uuid4()),
                        name="검색 확인",
                        condition="${작업유형} == '검색'",
                        true_steps=[
                            DynamicTextSearchStep(
                                step_id=str(uuid.uuid4()),
                                name="텍스트 검색",
                                search_text="${대상}",
                                click_on_found=True
                            )
                        ],
                        false_steps=[
                            WaitTimeStep(
                                step_id=str(uuid.uuid4()),
                                name="대기",
                                seconds=3.0
                            )
                        ]
                    )
                ]
            )
            
            loop_step.steps = [type_condition]
            macro.add_step(loop_step)
            
            # Simulate execution with mock
            execution_count = 0
            
            def mock_execute(step, context):
                nonlocal execution_count
                execution_count += 1
                
                # Verify context has Excel data
                assert 'current_row' in context
                assert context['current_row'] is not None
                
                return True, None
            
            mock_step_executor.execute.side_effect = mock_execute
            
            # Execute would process 3 rows with different actions
            # Row 1: Input action
            # Row 2: Search action  
            # Row 3: Wait action
            
            # Verify macro complexity
            assert self._count_total_steps(macro) >= 5
    
    def test_workflow_with_error_handling(self, excel_manager, mock_settings):
        """Test workflow execution with error handling"""
        # Create test data with potential error cases
        test_data = pd.DataFrame({
            '항목': ['정상', '오류발생', '재시도'],
            '값': ['OK', 'ERROR', 'RETRY']
        })
        
        with tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False) as tmp:
            test_data.to_excel(tmp.name, index=False)
            
            # Create macro with error handling
            macro = Macro("오류 처리 테스트")
            loop_step = LoopStep(
                step_id=str(uuid.uuid4()),
                name="항목 처리",
                loop_type="excel_rows"
            )
            
            # Add step that might fail
            risky_step = DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="위험한 검색",
                search_text="${값}",
                error_handling="continue"  # Continue on error
            )
            
            loop_step.steps = [risky_step]
            macro.add_step(loop_step)
            
            # Verify error handling configuration
            assert risky_step.error_handling == "continue"
    
    def test_macro_save_and_load_with_workflow(self, tmp_path):
        """Test saving and loading complex workflow macros"""
        # Create complex macro
        macro = Macro("저장 테스트 매크로")
        
        # Add various step types
        loop_step = LoopStep(
            step_id=str(uuid.uuid4()),
            name="메인 루프",
            loop_type="excel_rows"
        )
        
        loop_step.steps = [
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="검색",
                search_text="${검색어}"
            ),
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="입력",
                search_text="${입력값}"
            ),
            IfConditionStep(
                step_id=str(uuid.uuid4()),
                name="조건",
                condition="${조건} == 'Y'",
                true_steps=[
                    WaitTimeStep(
                        step_id=str(uuid.uuid4()),
                        name="대기",
                        seconds=2.0
                    )
                ],
                false_steps=[]
            )
        ]
        
        macro.add_step(loop_step)
        
        # Save macro
        storage = MacroStorage()
        save_path = tmp_path / "test_workflow.emf"
        storage.save_macro(macro, str(save_path))
        
        # Load macro
        loaded_macro = storage.load_macro(str(save_path))
        
        # Verify structure preserved
        assert loaded_macro.name == macro.name
        assert len(loaded_macro.steps) == 1
        assert isinstance(loaded_macro.steps[0], LoopStep)
        
        loaded_loop = loaded_macro.steps[0]
        assert len(loaded_loop.steps) == 3
        assert isinstance(loaded_loop.steps[0], DynamicTextSearchStep)
        assert isinstance(loaded_loop.steps[1], KeyboardTypeStep)
        assert isinstance(loaded_loop.steps[2], IfConditionStep)
    
    def _count_total_steps(self, macro: Macro) -> int:
        """Count total steps including nested ones"""
        count = 0
        
        def count_steps(steps):
            nonlocal count
            for step in steps:
                count += 1
                if isinstance(step, LoopStep):
                    count_steps(step.steps)
                elif isinstance(step, IfConditionStep):
                    count_steps(step.true_steps)
                    count_steps(step.false_steps)
        
        count_steps(macro.steps)
        return count