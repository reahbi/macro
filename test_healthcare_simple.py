"""
Simplified healthcare workflow test
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pathlib import Path
import pandas as pd
from src.excel.excel_manager import ExcelManager
from src.core.macro_types import Macro, LoopStep
from src.core.dynamic_text_step import DynamicTextSearchStep
from src.core.macro_types import KeyboardTypeStep, WaitTimeStep
import uuid

def test_basic_workflow():
    """Test basic healthcare workflow"""
    print("Testing basic healthcare workflow...")
    
    # 1. Test Excel loading
    test_data_path = Path("test_data/healthcare_checkup.xlsx")
    if not test_data_path.exists():
        print(f"[ERROR] Test data not found: {test_data_path}")
        return False
    
    excel_manager = ExcelManager()
    try:
        file_info = excel_manager.load_file(str(test_data_path))
        print(f"[OK] Excel loaded: {file_info.file_path}")
        print(f"    Sheets: {file_info.sheets}")
    except Exception as e:
        print(f"[ERROR] Excel loading failed: {e}")
        return False
    
    # 2. Create macro
    macro = Macro(
        name="Test Healthcare Macro",
        description="Test macro"
    )
    
    loop_step = LoopStep(
        step_id=str(uuid.uuid4()),
        name="Data Loop",
        loop_type="excel_rows"
    )
    
    # Add steps
    steps = [
        DynamicTextSearchStep(
            step_id=str(uuid.uuid4()),
            name="Find Patient",
            search_text="환자조회",
            click_on_found=True
        ),
        KeyboardTypeStep(
            step_id=str(uuid.uuid4()),
            name="Type Patient ID",
            text="${환자번호}"
        ),
        WaitTimeStep(
            step_id=str(uuid.uuid4()),
            name="Wait",
            seconds=1.0
        )
    ]
    
    loop_step.steps = steps
    macro.add_step(loop_step)
    
    print(f"[OK] Macro created with {len(loop_step.steps)} steps")
    
    # 3. Verify macro structure
    if len(macro.steps) != 1:
        print("[ERROR] Wrong number of macro steps")
        return False
    
    if not isinstance(macro.steps[0], LoopStep):
        print("[ERROR] First step is not LoopStep")
        return False
    
    print("[OK] Macro structure verified")
    return True

if __name__ == "__main__":
    success = test_basic_workflow()
    print("\nTest result:", "PASSED" if success else "FAILED")