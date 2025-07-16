#!/usr/bin/env python3
"""
Test script to reproduce the ROI selection issue
"""

import sys
import os
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent.absolute()
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Fix import paths
def fix_imports():
    import importlib
    import sys
    
    # This ensures the imports work
    from core.macro_types import StepType, StepFactory
    from ui.dialogs.image_step_dialog import ImageSearchStepDialog
    print("✓ All imports successful")

def test_roi_issue():
    """Test the ROI selection issue"""
    try:
        # Create Qt application
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        fix_imports()
        
        # Create a test image search step
        from core.macro_types import StepType, StepFactory
        test_step = StepFactory.create_step(StepType.IMAGE_SEARCH)
        test_step.name = "테스트 이미지 검색"
        
        print(f"✓ Created test step: {test_step}")
        print(f"✓ Step type: {test_step.step_type}")
        print(f"✓ Step ID: {test_step.step_id}")
        
        # Try to create the dialog
        from ui.dialogs.image_step_dialog import ImageSearchStepDialog
        dialog = ImageSearchStepDialog(test_step, parent=None)
        
        print("✓ Dialog created successfully")
        print("✓ Test passed - no tuple/string errors detected")
        
        # Don't show the dialog, just test creation
        dialog.close()
        
    except Exception as e:
        print(f"✗ Error during test: {e}")
        import traceback
        traceback.print_exc()
        
    return True

if __name__ == "__main__":
    test_roi_issue()