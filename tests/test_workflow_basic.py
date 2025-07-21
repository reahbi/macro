"""
Basic workflow test to check environment
"""

import pytest
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

@pytest.mark.e2e
class TestBasicWorkflow:
    """Basic workflow test"""
    
    def test_imports(self):
        """Test basic imports"""
        from core.macro_types import Macro, LoopStep
        from core.dynamic_text_step import DynamicTextSearchStep
        from excel.excel_manager import ExcelManager
        
        assert Macro is not None
        assert LoopStep is not None
        assert DynamicTextSearchStep is not None
        assert ExcelManager is not None
    
    def test_create_macro(self):
        """Test macro creation"""
        from core.macro_types import Macro, LoopStep
        from core.dynamic_text_step import DynamicTextSearchStep
        import uuid
        
        macro = Macro(name="Test", description="Test macro")
        loop = LoopStep(
            step_id=str(uuid.uuid4()),
            name="Loop",
            loop_type="excel_rows"
        )
        
        step = DynamicTextSearchStep(
            step_id=str(uuid.uuid4()),
            name="Search",
            search_text="Test"
        )
        
        loop.steps = [step]
        macro.add_step(loop)
        
        assert len(macro.steps) == 1
        assert isinstance(macro.steps[0], LoopStep)
        assert len(macro.steps[0].steps) == 1
    
    @pytest.mark.skipif(not Path("test_data/healthcare_checkup.xlsx").exists(), 
                        reason="Test data not found")
    def test_excel_loading(self):
        """Test Excel file loading"""
        from excel.excel_manager import ExcelManager
        
        excel_manager = ExcelManager()
        file_info = excel_manager.load_file("test_data/healthcare_checkup.xlsx")
        
        assert file_info is not None
        assert len(file_info.sheets) > 0