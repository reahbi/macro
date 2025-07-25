"""Check PaddleOCR installation and run basic tests"""
import sys
import os

# Add paths
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('src'))

print("Checking PaddleOCR installation...")
print("-" * 50)

# Check imports
try:
    import numpy as np
    print(f"[OK] NumPy version: {np.__version__}")
except ImportError as e:
    print(f"[FAIL] NumPy import failed: {e}")

try:
    import cv2
    print(f"[OK] OpenCV version: {cv2.__version__}")
except ImportError:
    print("[INFO] OpenCV not installed (optional)")

try:
    from paddleocr import PaddleOCR
    print("[OK] PaddleOCR imported successfully")
    
    # Try to create instance
    try:
        ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
        print("[OK] PaddleOCR instance created")
    except Exception as e:
        print(f"[FAIL] PaddleOCR initialization error: {e}")
        
except ImportError as e:
    print(f"[FAIL] PaddleOCR import failed: {e}")

# Check text extractor
print("\nChecking text extractor module...")
print("-" * 50)

try:
    from vision.text_extractor_paddle import PaddleTextExtractor, TextResult
    print("[OK] Text extractor imported successfully")
    
    # Try to create instance
    try:
        extractor = PaddleTextExtractor()
        print("[OK] Text extractor instance created")
    except Exception as e:
        print(f"[FAIL] Text extractor initialization error: {e}")
        
except ImportError as e:
    print(f"[FAIL] Text extractor import failed: {e}")

# Run a simple test
print("\nRunning simple test...")
print("-" * 50)

try:
    # Create a TextResult
    result = TextResult(
        text="test",
        confidence=0.9,
        bbox=(10, 20, 30, 40),
        center=(25, 40)
    )
    print(f"[OK] Created TextResult: text='{result.text}', confidence={result.confidence}")
    print(f"  bbox={result.bbox}, center={result.center}")
except Exception as e:
    print(f"[FAIL] Failed to create TextResult: {e}")

print("\nTest complete!")