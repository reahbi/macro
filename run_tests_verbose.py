"""
Run tests with verbose output and capture all errors
"""
import sys
import os
import subprocess

# Add to path
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('src'))

print("Running tests with PaddleOCR installed...")
print("="*80)

# Run unit tests with full output
print("\n1. UNIT TESTS")
print("-"*40)
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_text_search_unit.py", "-v", "-s", "--tb=short"],
    capture_output=False,  # Show output directly
    text=True
)

# Run integration tests
print("\n\n2. INTEGRATION TESTS")
print("-"*40)
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_text_search_integration_fixed.py", "-v", "-s", "--tb=short"],
    capture_output=False,
    text=True
)

# Run E2E tests
print("\n\n3. E2E TESTS")
print("-"*40)
result = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_text_search_e2e.py", "-v", "-s", "--tb=short"],
    capture_output=False,
    text=True
)

print("\n" + "="*80)
print("Test execution completed with PaddleOCR")
print("="*80)