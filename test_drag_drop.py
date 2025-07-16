#!/usr/bin/env python3
"""
Test script to reproduce the drag-and-drop issue
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
from PyQt5.QtCore import Qt, QByteArray, QDataStream, QIODevice

def test_drag_drop_data():
    """Test the drag and drop data serialization"""
    try:
        # Create Qt application
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        
        # Import after Qt is set up
        from core.macro_types import StepType
        
        # Test serialization like it happens in drag-and-drop
        test_step_type = StepType.IMAGE_SEARCH
        print(f"✓ Original step type: {test_step_type}")
        print(f"✓ Step type value: {test_step_type.value}")
        
        # Simulate the writeQString process
        byte_array = QByteArray()
        write_stream = QDataStream(byte_array, QIODevice.WriteOnly)
        write_stream.writeQString(test_step_type.value)
        print(f"✓ Serialized successfully")
        
        # Simulate the readQString process
        read_stream = QDataStream(byte_array, QIODevice.ReadOnly)
        step_type_str_result = read_stream.readQString()
        print(f"✓ Read result: {step_type_str_result}")
        print(f"✓ Result type: {type(step_type_str_result)}")
        
        # Apply the fix
        step_type_str = step_type_str_result[0] if isinstance(step_type_str_result, tuple) else step_type_str_result
        print(f"✓ Fixed string: {step_type_str}")
        print(f"✓ Fixed string type: {type(step_type_str)}")
        
        # Test StepType conversion
        recreated_step_type = StepType(step_type_str)
        print(f"✓ Recreated step type: {recreated_step_type}")
        
        # Test step creation
        from core.macro_types import StepFactory
        new_step = StepFactory.create_step(recreated_step_type)
        print(f"✓ Created step: {new_step}")
        
        print("✓ All drag-and-drop serialization tests passed!")
        
    except Exception as e:
        print(f"✗ Error during drag-and-drop test: {e}")
        import traceback
        traceback.print_exc()
        
    return True

if __name__ == "__main__":
    test_drag_drop_data()