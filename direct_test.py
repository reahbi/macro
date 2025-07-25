"""
Direct test execution without subprocess
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('src'))

# First, let's try to import and see what errors we get
print("Testing imports...")

try:
    from vision.text_extractor_paddle import PaddleTextExtractor, TextResult
    print("✓ PaddleTextExtractor imported successfully")
except Exception as e:
    print(f"✗ Error importing PaddleTextExtractor: {e}")
    
try:
    from core.macro_types import TextSearchStep
    print("✓ TextSearchStep imported successfully")
except Exception as e:
    print(f"✗ Error importing TextSearchStep: {e}")
    
try:
    from ui.dialogs.text_search_step_dialog import TextSearchStepDialog
    print("✓ TextSearchStepDialog imported successfully")
except Exception as e:
    print(f"✗ Error importing TextSearchStepDialog: {e}")

print("\nTrying to run a simple test...")

# Simple test
try:
    result = TextResult(
        text="테스트",
        position=[[10, 20], [100, 20], [100, 50], [10, 50]],
        confidence=0.95
    )
    print(f"✓ TextResult created: text={result.text}, center={result.center}")
except Exception as e:
    print(f"✗ Error creating TextResult: {e}")

# Test TextSearchStep
try:
    step = TextSearchStep()
    step.search_text = "테스트"
    print(f"✓ TextSearchStep created: search_text={step.search_text}")
except Exception as e:
    print(f"✗ Error creating TextSearchStep: {e}")