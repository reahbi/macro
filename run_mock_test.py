"""
Run mock test directly
"""

import sys
import os
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

# Run pytest programmatically
import pytest

if __name__ == "__main__":
    # Run specific test
    result = pytest.main([
        "tests/test_workflow_mock.py",
        "-v",
        "-s",
        "--tb=short"
    ])
    
    print(f"\nTest result code: {result}")