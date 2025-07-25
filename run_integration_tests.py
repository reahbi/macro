"""
Run integration tests in virtual environment
"""
import subprocess
import sys
import os

def main():
    # Check if in venv
    print(f"Python: {sys.version}")
    print(f"Executable: {sys.executable}")
    
    if "venv311" not in sys.executable:
        print("\nERROR: Not running in venv311!")
        return 1
    
    # Fix paths
    sys.path.insert(0, os.path.abspath('.'))
    sys.path.insert(0, os.path.abspath('src'))
    
    # Install dependencies
    print("\nInstalling dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-qt", "pytest-mock", "-q"])
    
    # Run integration tests
    print("\n" + "="*80)
    print("Running Integration Tests")
    print("="*80)
    
    cmd = [sys.executable, "-m", "pytest", "tests/test_text_search_integration.py", "-v", "--tb=short"]
    result = subprocess.run(cmd)
    
    return result.returncode

if __name__ == "__main__":
    exit(main())