"""
Test OCR and OpenCV functionality in Python 3.13 environment
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_opencv():
    """Test OpenCV functionality"""
    print("\n=== Testing OpenCV ===")
    try:
        import cv2
        import numpy as np
        
        # Create a simple test image
        img = np.zeros((100, 200, 3), dtype=np.uint8)
        cv2.putText(img, "OpenCV Test", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        print(f"OpenCV version: {cv2.__version__}")
        print(f"Created test image: {img.shape}")
        print("[OK] OpenCV is working correctly")
        return True
    except Exception as e:
        print(f"[FAIL] OpenCV error: {e}")
        return False

def test_easyocr():
    """Test EasyOCR functionality"""
    print("\n=== Testing EasyOCR ===")
    try:
        from vision.text_extractor import TextExtractor
        
        # Create text extractor instance
        extractor = TextExtractor()
        
        # Check if OCR is available
        from utils.ocr_manager import OCRManager
        ocr_manager = OCRManager()
        
        if ocr_manager.is_available():
            print("[OK] EasyOCR is available")
            
            # Try to get reader
            try:
                reader = extractor._get_reader()
                print("[OK] EasyOCR reader initialized successfully")
                return True
            except Exception as e:
                print(f"[FAIL] EasyOCR reader initialization failed: {e}")
                return False
        else:
            print("[FAIL] EasyOCR is not available")
            return False
            
    except Exception as e:
        print(f"[FAIL] EasyOCR error: {e}")
        return False

def test_image_matcher():
    """Test ImageMatcher functionality"""
    print("\n=== Testing ImageMatcher ===")
    try:
        from vision.image_matcher import ImageMatcher
        from config.settings import Settings
        
        settings = Settings()
        matcher = ImageMatcher(settings)
        
        print("[OK] ImageMatcher initialized successfully")
        print(f"Detected {len(matcher._monitors)} monitor(s)")
        return True
    except Exception as e:
        print(f"[FAIL] ImageMatcher error: {e}")
        return False

def test_gpu_detection():
    """Test GPU detection for EasyOCR"""
    print("\n=== Testing GPU Detection ===")
    try:
        import torch
        
        cuda_available = torch.cuda.is_available()
        print(f"CUDA available: {cuda_available}")
        
        if cuda_available:
            print(f"CUDA device: {torch.cuda.get_device_name(0)}")
            print(f"CUDA version: {torch.version.cuda}")
        else:
            print("Running on CPU")
            
        return True
    except Exception as e:
        print(f"[FAIL] GPU detection error: {e}")
        return False

def main():
    print("Python 3.13 OCR and OpenCV Functionality Test")
    print("=" * 50)
    print(f"Python version: {sys.version}")
    
    results = []
    results.append(("OpenCV", test_opencv()))
    results.append(("EasyOCR", test_easyocr()))
    results.append(("ImageMatcher", test_image_matcher()))
    results.append(("GPU Detection", test_gpu_detection()))
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "PASSED" if result else "FAILED"
        print(f"{name}: [{status}]")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n[OK] All tests passed! The system is ready for use.")
    else:
        print("\n[FAIL] Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()