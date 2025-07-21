"""
Direct import test to debug issues
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("Testing imports...")

try:
    from core.macro_types import Macro, LoopStep
    print("[OK] Basic macro types imported")
except Exception as e:
    print(f"[ERROR] Basic types: {e}")

try:
    from core.macro_types import IfConditionStep
    print("[OK] IfConditionStep imported from macro_types")
except Exception as e:
    print(f"[INFO] IfConditionStep not in macro_types: {e}")
    
try:
    from core.step_imports import IfConditionStep
    print("[OK] IfConditionStep imported from step_imports")
except Exception as e:
    print(f"[ERROR] IfConditionStep from step_imports: {e}")

# Create simple objects
try:
    import uuid
    
    # Test creating condition without importing encryption
    class SimpleIfCondition:
        def __init__(self, condition, true_steps=None, false_steps=None):
            self.condition = condition
            self.true_steps = true_steps or []
            self.false_steps = false_steps or []
    
    condition = SimpleIfCondition(
        condition="${test} == 'value'",
        true_steps=[],
        false_steps=[]
    )
    print("[OK] Simple condition created")
    
except Exception as e:
    print(f"[ERROR] Creating condition: {e}")