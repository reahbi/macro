"""
Simple test to verify environment setup
"""

import sys
import os

def test_environment():
    """Test Python environment"""
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Test imports
    try:
        import pandas as pd
        print("[OK] Pandas imported successfully")
        
        # Create simple dataframe
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        print(f"[OK] DataFrame created: {df.shape}")
        
    except Exception as e:
        print(f"[ERROR] Pandas error: {e}")
    
    try:
        from src.core.macro_types import Macro, LoopStep
        print("[OK] Core imports successful")
    except Exception as e:
        print(f"[ERROR] Core import error: {e}")
    
    try:
        from src.excel.excel_manager import ExcelManager
        print("[OK] Excel manager import successful")
    except Exception as e:
        print(f"[ERROR] Excel manager import error: {e}")

if __name__ == "__main__":
    # Add src to path
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    test_environment()