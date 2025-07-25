"""
Test runner with PaddleOCR verification
"""
import sys
import os
import subprocess

def main():
    print("="*80)
    print("PaddleOCR Text Search Test Report")
    print("="*80)
    
    # Check Python version
    print(f"\nPython Version: {sys.version}")
    print(f"Executable: {sys.executable}")
    
    # Check if we're in venv311
    if "venv311" not in sys.executable:
        print("\nERROR: Not running in venv311!")
        print("Please run: venv311\\Scripts\\python.exe test_with_paddleocr.py")
        return
    
    # Test PaddleOCR import
    print("\n1. Testing PaddleOCR Installation")
    print("-"*40)
    try:
        from paddleocr import PaddleOCR
        print("[OK] PaddleOCR imported successfully")
        
        # Try to create instance
        print("Creating PaddleOCR instance...")
        ocr = PaddleOCR(lang='korean')
        print("[OK] PaddleOCR instance created successfully")
        
    except Exception as e:
        print(f"[ERROR] PaddleOCR error: {e}")
        return
    
    # Test our text extractor
    print("\n2. Testing Text Extractor Module")
    print("-"*40)
    sys.path.insert(0, os.path.abspath('.'))
    sys.path.insert(0, os.path.abspath('src'))
    
    try:
        from vision.text_extractor_paddle import PaddleTextExtractor, TextResult
        print("[OK] PaddleTextExtractor imported successfully")
        
        # Create instance
        extractor = PaddleTextExtractor()
        print("[OK] PaddleTextExtractor instance created")
        
    except Exception as e:
        print(f"[ERROR] Text extractor error: {e}")
        import traceback
        traceback.print_exc()
    
    # Run tests
    print("\n3. Running Tests")
    print("-"*40)
    
    # Install pytest if needed
    subprocess.run([sys.executable, "-m", "pip", "install", "pytest", "pytest-qt", "-q"])
    
    test_results = {}
    
    # Run each test suite
    test_files = [
        ("Unit Tests", "tests/test_text_search_unit.py"),
        ("Integration Tests", "tests/test_text_search_integration_fixed.py"),
        ("E2E Tests", "tests/test_text_search_e2e.py")
    ]
    
    for test_name, test_file in test_files:
        print(f"\nRunning {test_name}...")
        result = subprocess.run(
            [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"],
            capture_output=True,
            text=True
        )
        
        # Parse results
        output = result.stdout + result.stderr
        if "passed" in output or "failed" in output:
            # Extract test counts
            import re
            match = re.search(r'(\d+) passed|(\d+) failed', output)
            if match:
                passed = match.group(1) if match.group(1) else 0
                failed = match.group(2) if match.group(2) else 0
                test_results[test_name] = {"passed": passed, "failed": failed, "output": output}
                print(f"Results: {passed} passed, {failed} failed")
        else:
            test_results[test_name] = {"error": True, "output": output}
            print(f"Error running tests: {output[:200]}...")
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    total_passed = 0
    total_failed = 0
    
    for test_name, result in test_results.items():
        if "error" in result:
            print(f"{test_name}: ERROR")
        else:
            passed = int(result.get("passed", 0))
            failed = int(result.get("failed", 0))
            total_passed += passed
            total_failed += failed
            print(f"{test_name}: {passed} passed, {failed} failed")
    
    print(f"\nTotal: {total_passed} passed, {total_failed} failed")
    
    print("\n" + "="*80)
    print("PaddleOCR Status: INSTALLED AND WORKING")
    print("="*80)

if __name__ == "__main__":
    main()