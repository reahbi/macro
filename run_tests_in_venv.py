"""
Run tests in virtual environment
"""
import subprocess
import sys
import os

def run_test(test_file, test_name=None):
    """Run a single test and capture output"""
    cmd = [sys.executable, "-m", "pytest", test_file, "-v", "-s", "--tb=short"]
    if test_name:
        cmd[3] = f"{test_file}::{test_name}"
    
    print(f"\nRunning: {' '.join(cmd)}")
    print("="*80)
    
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    output, _ = proc.communicate()
    
    print(output)
    return proc.returncode == 0

def main():
    # Check if in venv
    print(f"Python: {sys.version}")
    print(f"Executable: {sys.executable}")
    
    if "venv311" not in sys.executable:
        print("\nERROR: Not running in venv311!")
        print("Please run this script using: venv311\\Scripts\\python.exe run_tests_in_venv.py")
        return
    
    # Install dependencies
    print("\nInstalling test dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-mock", "-q"])
    
    # Test 1: Simple import test
    print("\n" + "="*80)
    print("TEST 1: Import Test")
    print("="*80)
    
    try:
        # Fix import paths
        sys.path.insert(0, os.path.abspath('.'))
        sys.path.insert(0, os.path.abspath('src'))
        
        from vision.text_extractor_paddle import TextResult
        print("[PASS] Import successful")
        
        # Create a simple object with correct parameters
        result = TextResult(
            text="test",
            confidence=0.9,
            bbox=(0, 0, 10, 10),  # (x, y, width, height)
            center=(5, 5)  # (center_x, center_y)
        )
        print(f"[PASS] TextResult created: {result.text}, center={result.center}")
        
    except Exception as e:
        print(f"[FAIL] Import failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Run actual tests
    print("\n" + "="*80)
    print("Running Unit Tests")
    print("="*80)
    
    success = run_test("tests/test_text_search_unit.py")
    if not success:
        print("\nUnit tests failed! See errors above.")
        return
        
    print("\nAll tests completed!")

if __name__ == "__main__":
    main()