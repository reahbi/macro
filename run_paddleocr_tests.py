#!/usr/bin/env python
"""Run all PaddleOCR tests and capture results"""
import subprocess
import sys
import os

# Add paths for imports
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('src'))

def run_command(cmd, description):
    """Run a command and return its output"""
    print(f"\n{'='*50}")
    print(f"{description}")
    print('='*50)
    
    try:
        # Use subprocess.Popen for better output handling
        process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
        
        # Read output line by line
        for line in iter(process.stdout.readline, ''):
            if line:
                print(line.rstrip())
        
        process.wait()
        return process.returncode
    except Exception as e:
        print(f"Error running command: {e}")
        return 1

def main():
    # Check current Python and environment
    print(f"Current Python: {sys.executable}")
    print(f"Python version: {sys.version}")
    
    # Determine Python executable to use
    if "venv311" in sys.executable:
        # Already in venv
        python_exe = sys.executable
        print("Running in venv311 environment")
    else:
        # Use venv Python
        python_exe = os.path.join("venv311", "Scripts", "python.exe")
        if not os.path.exists(python_exe):
            print(f"Error: venv Python not found at {python_exe}")
            return
        print(f"Using venv Python: {python_exe}")
    
    # Check if PaddleOCR is installed
    print("\nChecking PaddleOCR installation...")
    ret = run_command(
        f'"{python_exe}" -c "from paddleocr import PaddleOCR; print(\'PaddleOCR is installed\')"',
        "Verifying PaddleOCR installation"
    )
    
    if ret != 0:
        print("\nPaddleOCR is not installed! Attempting to check dependencies...")
        run_command(f'"{python_exe}" -m pip list | findstr paddle', "Checking paddle packages")
        return
    
    # Run tests
    tests = [
        ("Unit Tests", f'"{python_exe}" -m pytest tests\\test_text_search_unit.py -v --tb=short'),
        ("Integration Tests (Fixed)", f'"{python_exe}" -m pytest tests\\test_text_search_integration_fixed.py -v --tb=short'),
        ("E2E Tests", f'"{python_exe}" -m pytest tests\\test_text_search_e2e.py -v --tb=short'),
    ]
    
    results = []
    for test_name, cmd in tests:
        ret = run_command(cmd, f"Running {test_name}")
        results.append((test_name, ret))
    
    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)
    
    # Run summary command
    run_command(
        f'"{python_exe}" -m pytest tests\\test_text_search_unit.py tests\\test_text_search_integration_fixed.py tests\\test_text_search_e2e.py --tb=no -q',
        "Overall Summary"
    )
    
    print("\n" + "="*50)
    print("DETAILED RESULTS")
    print("="*50)
    for test_name, ret in results:
        status = "PASSED" if ret == 0 else "FAILED"
        print(f"{test_name}: {status}")

if __name__ == "__main__":
    main()