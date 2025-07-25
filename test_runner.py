"""
Test runner script for text search tests
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print('='*60)
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False

def main():
    # Check if we're in venv
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("Not in virtual environment! Please activate venv311 first.")
        return
    
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # Install test dependencies
    print("\nInstalling test dependencies...")
    run_command("pip install pytest pytest-qt pytest-mock --quiet", "Installing pytest")
    
    # Run unit tests
    success = run_command(
        "python -m pytest tests/test_text_search_unit.py -v -x", 
        "Unit Tests"
    )
    
    if not success:
        print("\nUnit tests failed! Check the errors above.")
        return
    
    # Run integration tests
    success = run_command(
        "python -m pytest tests/test_text_search_integration.py -v -x",
        "Integration Tests"
    )
    
    if not success:
        print("\nIntegration tests failed! Check the errors above.")
        return
    
    # Run E2E tests
    success = run_command(
        "python -m pytest tests/test_text_search_e2e.py -v -x",
        "E2E Tests"
    )
    
    if not success:
        print("\nE2E tests failed! Check the errors above.")
        return
    
    print("\nAll tests passed!")

if __name__ == "__main__":
    main()