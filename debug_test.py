"""
Debug test environment and run simple test
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
sys.path.insert(0, os.path.dirname(__file__))

def test_imports():
    """Test basic imports"""
    print("Testing imports...")
    
    try:
        from src.core.macro_types import Macro, LoopStep, DynamicTextSearchStep
        print("[OK] Core types imported")
    except Exception as e:
        print(f"[ERROR] Core types: {e}")
        return False
    
    try:
        from src.excel.excel_manager import ExcelManager
        print("[OK] Excel manager imported")
    except Exception as e:
        print(f"[ERROR] Excel manager: {e}")
        return False
    
    try:
        import pandas as pd
        df = pd.DataFrame({'A': [1, 2, 3]})
        print(f"[OK] Pandas working: {df.shape}")
    except Exception as e:
        print(f"[ERROR] Pandas: {e}")
        return False
    
    return True

def test_dynamic_text_step():
    """Test DynamicTextSearchStep creation"""
    print("\nTesting DynamicTextSearchStep...")
    
    try:
        from src.core.dynamic_text_step import DynamicTextSearchStep
        import uuid
        
        # Check what parameters it accepts
        print("DynamicTextSearchStep attributes:")
        print(DynamicTextSearchStep.__annotations__)
        
        # Create instance
        step = DynamicTextSearchStep(
            step_id=str(uuid.uuid4()),
            name="Test Step",
            search_text="Test Text"
        )
        print(f"[OK] Created step: {step.name}")
        return True
    except Exception as e:
        print(f"[ERROR] DynamicTextSearchStep: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Python version:", sys.version)
    print("Working directory:", os.getcwd())
    print("-" * 60)
    
    if test_imports():
        test_dynamic_text_step()