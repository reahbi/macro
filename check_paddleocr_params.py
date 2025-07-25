import sys
import os

# Add to path
sys.path.insert(0, 'venv311/Lib/site-packages')

try:
    from paddleocr import PaddleOCR
    
    # Try different parameter combinations
    print("Testing PaddleOCR initialization parameters...")
    
    # Test 1: Minimal parameters
    try:
        ocr = PaddleOCR(lang='korean')
        print("[OK] Minimal parameters work (lang='korean')")
    except Exception as e:
        print(f"[ERROR] Minimal parameters failed: {e}")
    
    # Test 2: With use_angle_cls
    try:
        ocr = PaddleOCR(lang='korean', use_angle_cls=True)
        print("[OK] use_angle_cls parameter works")
    except Exception as e:
        print(f"[ERROR] use_angle_cls failed: {e}")
        
    # Test 3: With det and rec
    try:
        ocr = PaddleOCR(lang='korean', det=True, rec=True)
        print("[OK] det and rec parameters work")
    except Exception as e:
        print(f"[ERROR] det/rec failed: {e}")
        
except ImportError as e:
    print(f"Import error: {e}")