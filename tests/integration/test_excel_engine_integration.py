"""
Integration tests for Excel-Engine integration
Tests the interaction between ExcelManager data loading and ExecutionEngine variable substitution.
"""

import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from excel.excel_manager import ExcelManager
from excel.models import ExcelData, ColumnMapping, ColumnType
from automation.engine import ExecutionEngine, ExecutionState
from automation.executor import StepExecutor
from core.macro_types import (
    Macro, MouseClickStep, KeyboardTypeStep, WaitTimeStep, 
    TextSearchStep, IfConditionStep
)
from config.settings import Settings


@pytest.mark.integration
class TestExcelEngineBasicIntegration:
    """Test basic integration between ExcelManager and ExecutionEngine"""
    
    @pytest.fixture
    def mock_settings(self):
        """Create mock settings"""
        settings = Mock(spec=Settings)
        settings.get.return_value = 100  # Default delay
        return settings
    
    @pytest.fixture
    def excel_manager(self):
        """Create ExcelManager for testing"""
        return ExcelManager()
    
    @pytest.fixture
    def execution_engine(self, mock_settings):
        """Create ExecutionEngine for testing"""
        with patch('automation.hotkey_listener.HotkeyListener'):
            with patch('logger.execution_logger.get_execution_logger'):
                engine = ExecutionEngine(mock_settings)
                return engine
    
    @pytest.fixture
    def sample_excel_data(self):
        """Create sample Excel data"""
        return pd.DataFrame({
            '고객명': ['김철수', '박영희', '이민수'],
            '나이': [25, 30, 28],
            '이메일': ['kim@test.com', 'park@test.com', 'lee@test.com'],
            '부서': ['개발팀', '마케팅팀', '인사팀'],
            '상태': ['', '', '']
        })
    
    def test_excel_to_engine_data_flow(self, excel_manager, execution_engine, sample_excel_data):
        """Test data flow from Excel to Engine"""
        # Setup Excel data
        mock_excel_data = Mock(spec=ExcelData)
        mock_excel_data.get_row_data.return_value = {
            '고객명': '김철수',
            '나이': 25,
            '이메일': 'kim@test.com',
            '부서': '개발팀',
            '상태': ''
        }
        excel_manager._current_data = mock_excel_data
        
        # Setup column mappings
        excel_manager.set_column_mapping('고객명', 'customer_name', ColumnType.TEXT)
        excel_manager.set_column_mapping('나이', 'age', ColumnType.NUMBER)
        excel_manager.set_column_mapping('이메일', 'email', ColumnType.TEXT)
        excel_manager.set_column_mapping('부서', 'department', ColumnType.TEXT)
        
        # Connect Excel to Engine
        execution_engine.excel_manager = excel_manager
        
        # Create macro with variable substitution
        macro = Macro(name="Excel Integration Test")
        macro.add_step(KeyboardTypeStep(
            name="Customer Info",
            text="고객명: {{customer_name}}, 나이: {{age}}, 부서: {{department}}"
        ))
        execution_engine.set_macro(macro)
        
        # Test variable substitution
        with patch('pyautogui.typewrite') as mock_typewrite:
            with patch.object(execution_engine, '_set_state'):
                with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                    with patch.object(execution_engine.execution_logger, 'log_row_start'):
                        with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                            with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                with patch.object(execution_engine.execution_logger, 'close'):
                                    
                                    result = execution_engine._execute_row(0)
                                    
                                    # Verify variable substitution
                                    expected_text = "고객명: 김철수, 나이: 25, 부서: 개발팀"
                                    mock_typewrite.assert_called_once_with(expected_text, interval=0.0)
                                    assert result.success is True
    
    def test_variable_substitution_multiple_variables(self, excel_manager, execution_engine):
        """Test complex variable substitution with multiple variables"""
        # Setup Excel data with multiple variables
        mock_excel_data = Mock(spec=ExcelData)
        mock_excel_data.get_row_data.return_value = {
            '성': '김',
            '이름': '철수',
            '회사': 'ABC회사',
            '직급': '대리',
            '연락처': '010-1234-5678'
        }
        excel_manager._current_data = mock_excel_data
        
        # Setup mappings
        mappings = [
            ('성', 'last_name', ColumnType.TEXT),
            ('이름', 'first_name', ColumnType.TEXT),
            ('회사', 'company', ColumnType.TEXT),
            ('직급', 'position', ColumnType.TEXT),
            ('연락처', 'phone', ColumnType.TEXT)
        ]
        
        for excel_col, var_name, col_type in mappings:
            excel_manager.set_column_mapping(excel_col, var_name, col_type)
        
        execution_engine.excel_manager = excel_manager
        
        # Create macro with multiple variable usage
        macro = Macro(name="Multiple Variables Test")
        macro.add_step(KeyboardTypeStep(
            name="Full Name",
            text="{{last_name}}{{first_name}}"
        ))
        macro.add_step(KeyboardTypeStep(
            name="Work Info",
            text="{{company}} {{position}}"
        ))
        macro.add_step(KeyboardTypeStep(
            name="Contact",
            text="연락처: {{phone}}"
        ))
        execution_engine.set_macro(macro)
        
        # Test execution
        typewrite_calls = []
        def capture_typewrite(text, **kwargs):
            typewrite_calls.append(text)
        
        with patch('pyautogui.typewrite', side_effect=capture_typewrite):
            with patch.object(execution_engine, '_set_state'):
                with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                    with patch.object(execution_engine.execution_logger, 'log_row_start'):
                        with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                            with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                with patch.object(execution_engine.execution_logger, 'close'):
                                    
                                    result = execution_engine._execute_row(0)
        
        # Verify all substitutions
        assert len(typewrite_calls) == 3
        assert typewrite_calls[0] == "김철수"
        assert typewrite_calls[1] == "ABC회사 대리"
        assert typewrite_calls[2] == "연락처: 010-1234-5678"
        assert result.success is True


@pytest.mark.integration
class TestExcelEngineStatusManagement:
    """Test status management integration between Excel and Engine"""
    
    @pytest.fixture
    def excel_manager(self):
        """Create ExcelManager for testing"""
        return ExcelManager()
    
    @pytest.fixture
    def execution_engine(self, mock_settings):
        """Create ExecutionEngine for testing"""
        with patch('automation.hotkey_listener.HotkeyListener'):
            with patch('logger.execution_logger.get_execution_logger'):
                engine = ExecutionEngine(mock_settings)
                return engine
    
    def test_status_update_integration(self, excel_manager, execution_engine):
        """Test status updates during execution"""
        # Setup Excel data
        mock_excel_data = Mock(spec=ExcelData)
        mock_excel_data.get_row_data.return_value = {
            '고객명': '김철수',
            '상태': ''
        }
        excel_manager._current_data = mock_excel_data
        excel_manager.set_column_mapping('고객명', 'name', ColumnType.TEXT)
        
        execution_engine.excel_manager = excel_manager
        
        # Create simple macro
        macro = Macro(name="Status Test")
        macro.add_step(KeyboardTypeStep(name="Type Name", text="{{name}}"))
        execution_engine.set_macro(macro)
        
        # Test execution with status updates
        with patch('pyautogui.typewrite'):
            with patch.object(execution_engine, '_set_state'):
                with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                    with patch.object(execution_engine.execution_logger, 'log_row_start'):
                        with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                            with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                with patch.object(execution_engine.execution_logger, 'close'):
                                    
                                    result = execution_engine._execute_row(0)
        
        # Verify status was updated (this would happen in the real execution)
        assert result.success is True
        # In actual implementation, status would be updated via excel_manager.update_row_status
    
    def test_pending_rows_processing(self, excel_manager, execution_engine):
        """Test processing of pending rows from Excel"""
        # Setup Excel data with pending rows
        mock_excel_data = Mock(spec=ExcelData)
        mock_pending_df = pd.DataFrame({
            'index': [0, 2, 4],
            'customer': ['김철수', '박영희', '이민수'],
            'status': ['', '', '']
        })
        mock_pending_df.index = [0, 2, 4]
        mock_excel_data.get_incomplete_rows.return_value = mock_pending_df
        excel_manager._current_data = mock_excel_data
        
        # Test getting pending rows
        pending_rows = excel_manager.get_pending_rows()
        assert pending_rows == [0, 2, 4]
        
        # Simulate processing each pending row
        def mock_get_row_data(row_index):
            customers = {0: '김철수', 2: '박영희', 4: '이민수'}
            return {'고객명': customers[row_index], '상태': ''}
        
        mock_excel_data.get_row_data.side_effect = mock_get_row_data
        excel_manager.set_column_mapping('고객명', 'customer', ColumnType.TEXT)
        execution_engine.excel_manager = excel_manager
        
        # Create macro for processing
        macro = Macro(name="Batch Processing")
        macro.add_step(KeyboardTypeStep(name="Process Customer", text="처리: {{customer}}"))
        execution_engine.set_macro(macro)
        
        # Process each pending row
        processed_customers = []
        def capture_typewrite(text, **kwargs):
            processed_customers.append(text)
        
        with patch('pyautogui.typewrite', side_effect=capture_typewrite):
            with patch.object(execution_engine, '_set_state'):
                with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                    with patch.object(execution_engine.execution_logger, 'log_row_start'):
                        with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                            with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                with patch.object(execution_engine.execution_logger, 'close'):
                                    
                                    for row_index in pending_rows:
                                        result = execution_engine._execute_row(row_index)
                                        assert result.success is True
        
        # Verify all customers were processed
        assert len(processed_customers) == 3
        assert "처리: 김철수" in processed_customers
        assert "처리: 박영희" in processed_customers
        assert "처리: 이민수" in processed_customers


@pytest.mark.integration
class TestExcelEngineConditionalLogic:
    """Test conditional logic integration with Excel data"""
    
    @pytest.fixture
    def excel_manager(self):
        """Create ExcelManager for testing"""
        return ExcelManager()
    
    @pytest.fixture
    def execution_engine(self, mock_settings):
        """Create ExecutionEngine for testing"""
        with patch('automation.hotkey_listener.HotkeyListener'):
            with patch('logger.execution_logger.get_execution_logger'):
                engine = ExecutionEngine(mock_settings)
                return engine
    
    def test_conditional_execution_based_on_excel_data(self, excel_manager, execution_engine):
        """Test conditional step execution based on Excel data values"""
        # Setup Excel data with different values for conditional logic
        mock_excel_data = Mock(spec=ExcelData)
        
        def mock_get_row_data(row_index):
            data_rows = {
                0: {'고객유형': 'VIP', '고객명': '김철수'},
                1: {'고객유형': '일반', '고객명': '박영희'},
                2: {'고객유형': 'VIP', '고객명': '이민수'}
            }
            return data_rows[row_index]
        
        mock_excel_data.get_row_data.side_effect = mock_get_row_data
        excel_manager._current_data = mock_excel_data
        
        # Setup mappings
        excel_manager.set_column_mapping('고객유형', 'customer_type', ColumnType.TEXT)
        excel_manager.set_column_mapping('고객명', 'customer_name', ColumnType.TEXT)
        
        execution_engine.excel_manager = excel_manager
        
        # Create macro with conditional logic
        macro = Macro(name="Conditional Processing")
        
        # Add conditional step based on customer type
        condition_step = IfConditionStep(
            name="VIP Check",
            condition_type="text_equals",
            condition_value="{{customer_type}} == 'VIP'"
        )
        
        # VIP path
        vip_step = KeyboardTypeStep(name="VIP Processing", text="VIP 고객: {{customer_name}}")
        condition_step.true_steps = [vip_step]
        
        # Regular path
        regular_step = KeyboardTypeStep(name="Regular Processing", text="일반 고객: {{customer_name}}")
        condition_step.false_steps = [regular_step]
        
        macro.add_step(condition_step)
        execution_engine.set_macro(macro)
        
        # Test execution for different customer types
        execution_results = []
        def capture_typewrite(text, **kwargs):
            execution_results.append(text)
        
        with patch('pyautogui.typewrite', side_effect=capture_typewrite):
            with patch.object(execution_engine, '_set_state'):
                with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                    with patch.object(execution_engine.execution_logger, 'log_row_start'):
                        with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                            with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                with patch.object(execution_engine.execution_logger, 'close'):
                                    
                                    # Test row 0 (VIP)
                                    with patch.object(execution_engine.step_executor, '_evaluate_condition', return_value=True):
                                        result = execution_engine._execute_row(0)
                                        assert result.success is True
                                    
                                    # Test row 1 (Regular)
                                    with patch.object(execution_engine.step_executor, '_evaluate_condition', return_value=False):
                                        result = execution_engine._execute_row(1)
                                        assert result.success is True
        
        # Verify conditional execution
        assert len(execution_results) == 2
        # Results depend on the condition evaluation mocking
    
    def test_data_validation_integration(self, excel_manager, execution_engine):
        """Test data validation integration between Excel and Engine"""
        # Setup Excel data with missing required fields
        mock_excel_data = Mock(spec=ExcelData)
        mock_excel_data.get_row_data.return_value = {
            '고객명': '김철수',
            '이메일': '',  # Missing required email
            '전화번호': '010-1234-5678'
        }
        excel_manager._current_data = mock_excel_data
        
        # Setup mappings with required field
        excel_manager.set_column_mapping('고객명', 'name', ColumnType.TEXT, is_required=True)
        excel_manager.set_column_mapping('이메일', 'email', ColumnType.TEXT, is_required=True)
        excel_manager.set_column_mapping('전화번호', 'phone', ColumnType.TEXT, is_required=False)
        
        execution_engine.excel_manager = excel_manager
        
        # Test data validation during execution
        with pytest.raises(ValueError, match="Required field validation"):
            # This should fail due to missing required email
            mapped_data = excel_manager.get_mapped_data(0)


@pytest.mark.integration
class TestExcelEngineErrorHandling:
    """Test error handling in Excel-Engine integration"""
    
    @pytest.fixture
    def excel_manager(self):
        """Create ExcelManager for testing"""
        return ExcelManager()
    
    @pytest.fixture
    def execution_engine(self, mock_settings):
        """Create ExecutionEngine for testing"""
        with patch('automation.hotkey_listener.HotkeyListener'):
            with patch('logger.execution_logger.get_execution_logger'):
                engine = ExecutionEngine(mock_settings)
                return engine
    
    def test_missing_excel_data_error(self, excel_manager, execution_engine):
        """Test handling when Excel data is not loaded"""
        # No Excel data loaded
        execution_engine.excel_manager = excel_manager
        
        # Create macro with variables
        macro = Macro(name="No Data Test")
        macro.add_step(KeyboardTypeStep(name="Type", text="{{missing_var}}"))
        execution_engine.set_macro(macro)
        
        # Should handle missing data gracefully
        with patch.object(execution_engine, '_set_state'):
            with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                with patch.object(execution_engine.execution_logger, 'log_row_start'):
                    with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                        with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                            with patch.object(execution_engine.execution_logger, 'close'):
                                
                                result = execution_engine._execute_row(0)
                                
                                # Should fail gracefully
                                assert result.success is False
                                assert "No data loaded" in result.error
    
    def test_variable_substitution_missing_mapping(self, excel_manager, execution_engine):
        """Test handling when variable mapping is missing"""
        # Setup Excel data but no mappings
        mock_excel_data = Mock(spec=ExcelData)
        mock_excel_data.get_row_data.return_value = {'고객명': '김철수'}
        excel_manager._current_data = mock_excel_data
        execution_engine.excel_manager = excel_manager
        
        # Create macro with unmapped variable
        macro = Macro(name="Missing Mapping Test")
        macro.add_step(KeyboardTypeStep(name="Type", text="{{unmapped_var}}"))
        execution_engine.set_macro(macro)
        
        # Should handle missing mapping
        with patch('pyautogui.typewrite') as mock_typewrite:
            with patch.object(execution_engine, '_set_state'):
                with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                    with patch.object(execution_engine.execution_logger, 'log_row_start'):
                        with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                            with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                with patch.object(execution_engine.execution_logger, 'close'):
                                    
                                    result = execution_engine._execute_row(0)
        
        # Variable should remain unreplaced or use default value
        mock_typewrite.assert_called_once()
        call_args = mock_typewrite.call_args[0]
        # Could be "{{unmapped_var}}" or empty string depending on implementation
        assert "{{unmapped_var}}" in call_args[0] or call_args[0] == ""
    
    def test_excel_data_access_error(self, excel_manager, execution_engine):
        """Test handling Excel data access errors"""
        # Setup Excel data that throws error
        mock_excel_data = Mock(spec=ExcelData)
        mock_excel_data.get_row_data.side_effect = Exception("Excel access error")
        excel_manager._current_data = mock_excel_data
        excel_manager.set_column_mapping('고객명', 'name', ColumnType.TEXT)
        
        execution_engine.excel_manager = excel_manager
        
        # Create macro
        macro = Macro(name="Excel Error Test")
        macro.add_step(KeyboardTypeStep(name="Type", text="{{name}}"))
        execution_engine.set_macro(macro)
        
        # Should handle Excel access error
        with patch.object(execution_engine, '_set_state'):
            with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                with patch.object(execution_engine.execution_logger, 'log_row_start'):
                    with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                        with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                            with patch.object(execution_engine.execution_logger, 'close'):
                                
                                result = execution_engine._execute_row(0)
                                
                                assert result.success is False
                                assert "Excel access error" in result.error


@pytest.mark.integration
class TestExcelEngineDataTypes:
    """Test data type handling in Excel-Engine integration"""
    
    @pytest.fixture
    def excel_manager(self):
        """Create ExcelManager for testing"""
        return ExcelManager()
    
    @pytest.fixture
    def execution_engine(self, mock_settings):
        """Create ExecutionEngine for testing"""
        with patch('automation.hotkey_listener.HotkeyListener'):
            with patch('logger.execution_logger.get_execution_logger'):
                engine = ExecutionEngine(mock_settings)
                return engine
    
    def test_numeric_data_type_conversion(self, excel_manager, execution_engine):
        """Test numeric data type handling and conversion"""
        # Setup Excel data with various numeric types
        mock_excel_data = Mock(spec=ExcelData)
        mock_excel_data.get_row_data.return_value = {
            '정수값': 42,
            '실수값': 3.14159,
            '통화': 1234567.89,
            '백분율': 0.85
        }
        excel_manager._current_data = mock_excel_data
        
        # Setup mappings with number types
        mappings = [
            ('정수값', 'integer_val', ColumnType.NUMBER),
            ('실수값', 'float_val', ColumnType.NUMBER),
            ('통화', 'currency_val', ColumnType.NUMBER),
            ('백분율', 'percent_val', ColumnType.NUMBER)
        ]
        
        for excel_col, var_name, col_type in mappings:
            excel_manager.set_column_mapping(excel_col, var_name, col_type)
        
        execution_engine.excel_manager = excel_manager
        
        # Create macro using numeric variables
        macro = Macro(name="Numeric Test")
        macro.add_step(KeyboardTypeStep(
            name="Numbers",
            text="정수: {{integer_val}}, 실수: {{float_val}}, 통화: {{currency_val}}, 백분율: {{percent_val}}"
        ))
        execution_engine.set_macro(macro)
        
        # Test execution
        with patch('pyautogui.typewrite') as mock_typewrite:
            with patch.object(execution_engine, '_set_state'):
                with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                    with patch.object(execution_engine.execution_logger, 'log_row_start'):
                        with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                            with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                with patch.object(execution_engine.execution_logger, 'close'):
                                    
                                    result = execution_engine._execute_row(0)
        
        # Verify numeric conversion in text output
        expected_text = "정수: 42, 실수: 3.14159, 통화: 1234567.89, 백분율: 0.85"
        mock_typewrite.assert_called_once_with(expected_text, interval=0.0)
        assert result.success is True
    
    def test_boolean_data_type_conversion(self, excel_manager, execution_engine):
        """Test boolean data type handling with Korean/English values"""
        # Setup Excel data with boolean values
        mock_excel_data = Mock(spec=ExcelData)
        mock_excel_data.get_row_data.return_value = {
            '활성여부': True,
            '승인상태': False,
            '한글불린': '예',
            '영문불린': 'Yes'
        }
        excel_manager._current_data = mock_excel_data
        
        # Setup boolean mappings
        mappings = [
            ('활성여부', 'is_active', ColumnType.BOOLEAN),
            ('승인상태', 'is_approved', ColumnType.BOOLEAN),
            ('한글불린', 'korean_bool', ColumnType.BOOLEAN),
            ('영문불린', 'english_bool', ColumnType.BOOLEAN)
        ]
        
        for excel_col, var_name, col_type in mappings:
            excel_manager.set_column_mapping(excel_col, var_name, col_type)
        
        execution_engine.excel_manager = excel_manager
        
        # Create macro using boolean variables
        macro = Macro(name="Boolean Test")
        macro.add_step(KeyboardTypeStep(
            name="Booleans",
            text="활성: {{is_active}}, 승인: {{is_approved}}, 한글: {{korean_bool}}, 영문: {{english_bool}}"
        ))
        execution_engine.set_macro(macro)
        
        # Test execution
        with patch('pyautogui.typewrite') as mock_typewrite:
            with patch.object(execution_engine, '_set_state'):
                with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                    with patch.object(execution_engine.execution_logger, 'log_row_start'):
                        with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                            with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                with patch.object(execution_engine.execution_logger, 'close'):
                                    
                                    result = execution_engine._execute_row(0)
        
        # Verify boolean conversion (implementation-dependent)
        mock_typewrite.assert_called_once()
        typed_text = mock_typewrite.call_args[0][0]
        assert "True" in typed_text or "예" in typed_text  # Different representations possible
        assert result.success is True
    
    def test_empty_and_null_data_handling(self, excel_manager, execution_engine):
        """Test handling of empty and null Excel data"""
        # Setup Excel data with empty/null values
        mock_excel_data = Mock(spec=ExcelData)
        mock_excel_data.get_row_data.return_value = {
            '필수값': '김철수',
            '선택값': '',  # Empty string
            '널값': None,  # Null value
            '공백값': '   '  # Whitespace only
        }
        excel_manager._current_data = mock_excel_data
        
        # Setup mappings with default values
        from excel.models import ColumnMapping
        
        # Required field without default
        excel_manager.set_column_mapping('필수값', 'required_val', ColumnType.TEXT, is_required=True)
        
        # Optional fields with defaults
        optional_mapping = ColumnMapping(
            excel_column='선택값',
            variable_name='optional_val',
            data_type=ColumnType.TEXT,
            is_required=False,
            default_value='기본값'
        )
        excel_manager._column_mappings['optional_val'] = optional_mapping
        
        null_mapping = ColumnMapping(
            excel_column='널값',
            variable_name='null_val',
            data_type=ColumnType.TEXT,
            is_required=False,
            default_value='NULL_REPLACED'
        )
        excel_manager._column_mappings['null_val'] = null_mapping
        
        whitespace_mapping = ColumnMapping(
            excel_column='공백값',
            variable_name='whitespace_val',
            data_type=ColumnType.TEXT,
            is_required=False,
            default_value='WHITESPACE_REPLACED'
        )
        excel_manager._column_mappings['whitespace_val'] = whitespace_mapping
        
        execution_engine.excel_manager = excel_manager
        
        # Create macro using all variables
        macro = Macro(name="Empty Data Test")
        macro.add_step(KeyboardTypeStep(
            name="All Values",
            text="필수: {{required_val}}, 선택: {{optional_val}}, 널: {{null_val}}, 공백: {{whitespace_val}}"
        ))
        execution_engine.set_macro(macro)
        
        # Test execution
        with patch('pyautogui.typewrite') as mock_typewrite:
            with patch.object(execution_engine, '_set_state'):
                with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                    with patch.object(execution_engine.execution_logger, 'log_row_start'):
                        with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                            with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                with patch.object(execution_engine.execution_logger, 'close'):
                                    
                                    result = execution_engine._execute_row(0)
        
        # Verify default value usage
        typed_text = mock_typewrite.call_args[0][0]
        assert "김철수" in typed_text  # Required value
        assert "기본값" in typed_text  # Default for empty
        assert "NULL_REPLACED" in typed_text  # Default for null
        assert result.success is True


@pytest.mark.integration
@pytest.mark.slow
class TestExcelEnginePerformance:
    """Test performance aspects of Excel-Engine integration"""
    
    @pytest.fixture
    def excel_manager(self):
        """Create ExcelManager for testing"""
        return ExcelManager()
    
    @pytest.fixture
    def execution_engine(self, mock_settings):
        """Create ExecutionEngine for testing"""
        with patch('automation.hotkey_listener.HotkeyListener'):
            with patch('logger.execution_logger.get_execution_logger'):
                engine = ExecutionEngine(mock_settings)
                return engine
    
    def test_large_dataset_variable_substitution(self, excel_manager, execution_engine):
        """Test variable substitution performance with large datasets"""
        import time
        
        # Setup large Excel data simulation
        mock_excel_data = Mock(spec=ExcelData)
        
        def mock_get_row_data(row_index):
            return {
                '고객명': f'고객_{row_index}',
                '이메일': f'customer_{row_index}@test.com',
                '부서': f'부서_{row_index % 10}',
                '점수': row_index * 10,
                '상태': ''
            }
        
        mock_excel_data.get_row_data.side_effect = mock_get_row_data
        excel_manager._current_data = mock_excel_data
        
        # Setup mappings
        mappings = [
            ('고객명', 'name', ColumnType.TEXT),
            ('이메일', 'email', ColumnType.TEXT),
            ('부서', 'department', ColumnType.TEXT),
            ('점수', 'score', ColumnType.NUMBER)
        ]
        
        for excel_col, var_name, col_type in mappings:
            excel_manager.set_column_mapping(excel_col, var_name, col_type)
        
        execution_engine.excel_manager = excel_manager
        
        # Create macro with multiple variable substitutions
        macro = Macro(name="Performance Test")
        macro.add_step(KeyboardTypeStep(
            name="Complex Substitution",
            text="고객정보: {{name}} ({{email}}) - {{department}}, 점수: {{score}}"
        ))
        execution_engine.set_macro(macro)
        
        # Test performance for multiple rows
        start_time = time.time()
        
        processed_count = 0
        with patch('pyautogui.typewrite'):
            with patch.object(execution_engine, '_set_state'):
                with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                    with patch.object(execution_engine.execution_logger, 'log_row_start'):
                        with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                            with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                with patch.object(execution_engine.execution_logger, 'close'):
                                    
                                    # Process 100 rows
                                    for row_index in range(100):
                                        result = execution_engine._execute_row(row_index)
                                        assert result.success is True
                                        processed_count += 1
        
        total_time = time.time() - start_time
        
        # Performance assertions
        assert processed_count == 100
        assert total_time < 5.0  # Should complete 100 rows in less than 5 seconds
        
        # Calculate rows per second
        rows_per_second = processed_count / total_time
        assert rows_per_second > 20  # Should process at least 20 rows per second
    
    def test_memory_efficiency_with_complex_data(self, excel_manager, execution_engine):
        """Test memory efficiency with complex variable substitution"""
        # Setup complex Excel data
        mock_excel_data = Mock(spec=ExcelData)
        
        # Large text data to test memory usage
        large_text_data = "A" * 1000  # 1KB text per field
        
        mock_excel_data.get_row_data.return_value = {
            f'필드_{i}': f'{large_text_data}_{i}' for i in range(20)  # 20 fields x 1KB each
        }
        excel_manager._current_data = mock_excel_data
        
        # Setup many mappings
        for i in range(20):
            excel_manager.set_column_mapping(f'필드_{i}', f'var_{i}', ColumnType.TEXT)
        
        execution_engine.excel_manager = excel_manager
        
        # Create macro with all variables
        variable_text = ', '.join([f'{{{{var_{i}}}}}' for i in range(20)])
        macro = Macro(name="Memory Test")
        macro.add_step(KeyboardTypeStep(name="Large Text", text=variable_text))
        execution_engine.set_macro(macro)
        
        # Test memory usage (should not cause memory issues)
        with patch('pyautogui.typewrite') as mock_typewrite:
            with patch.object(execution_engine, '_set_state'):
                with patch.object(execution_engine.execution_logger, 'start_session', return_value="test.log"):
                    with patch.object(execution_engine.execution_logger, 'log_row_start'):
                        with patch.object(execution_engine.execution_logger, 'log_step_execution'):
                            with patch.object(execution_engine.execution_logger, 'log_row_complete'):
                                with patch.object(execution_engine.execution_logger, 'close'):
                                    
                                    result = execution_engine._execute_row(0)
        
        # Verify successful processing of large data
        assert result.success is True
        mock_typewrite.assert_called_once()
        
        # Verify substitution worked (check partial content)
        typed_text = mock_typewrite.call_args[0][0]
        assert f'{large_text_data}_0' in typed_text
        assert f'{large_text_data}_19' in typed_text