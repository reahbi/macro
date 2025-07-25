"""Run all PaddleOCR tests with proper environment setup"""
import sys
import os
import subprocess

# Add paths for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.insert(0, current_dir)
sys.path.insert(0, src_path)

def main():
    print("PaddleOCR Test Runner")
    print("=" * 60)
    print(f"Python: {sys.executable}")
    print(f"Version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    
    # Check PaddleOCR
    print("\nChecking PaddleOCR installation...")
    try:
        from paddleocr import PaddleOCR
        print("✓ PaddleOCR is installed")
        
        # Try to initialize it
        try:
            ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
            print("✓ PaddleOCR initialized successfully")
        except Exception as e:
            print(f"✗ PaddleOCR initialization failed: {e}")
    except ImportError as e:
        print(f"✗ PaddleOCR import failed: {e}")
        return
    
    # Run tests
    print("\n" + "=" * 60)
    print("RUNNING TESTS")
    print("=" * 60)
    
    test_files = [
        ("Unit Tests", "tests/test_text_search_unit.py"),
        ("Integration Tests (Fixed)", "tests/test_text_search_integration_fixed.py"),
        ("E2E Tests", "tests/test_text_search_e2e.py")
    ]
    
    results = []
    
    for test_name, test_file in test_files:
        print(f"\n--- {test_name} ---")
        cmd = [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            
            # Parse result
            passed = "passed" in result.stdout
            failed = "failed" in result.stdout
            
            if passed and not failed:
                results.append((test_name, "PASSED", result.stdout))
            else:
                results.append((test_name, "FAILED", result.stdout))
                
        except Exception as e:
            print(f"Error running {test_name}: {e}")
            results.append((test_name, "ERROR", str(e)))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    for test_name, status, _ in results:
        print(f"{test_name}: {status}")
    
    # Run overall summary
    print("\nOverall pytest summary:")
    cmd = [sys.executable, "-m", "pytest"] + [tf[1] for tf in test_files] + ["--tb=no", "-q"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"Error running summary: {e}")

if __name__ == "__main__":
    main()