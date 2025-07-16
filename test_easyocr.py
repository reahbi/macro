#!/usr/bin/env python3
"""
Test script to check EasyOCR installation
"""

try:
    import easyocr
    print("✓ EasyOCR is installed")
    print(f"✓ EasyOCR version: {easyocr.__version__}")
    
    # Test basic initialization
    reader = easyocr.Reader(['en'], gpu=False)
    print("✓ EasyOCR Reader initialized successfully")
    
    # Test with dummy image
    import numpy as np
    dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
    result = reader.readtext(dummy_img)
    print(f"✓ EasyOCR test completed. Results: {len(result)} items found")
    
except ImportError as e:
    print("✗ EasyOCR is not installed")
    print(f"Error: {e}")
    print("\nTo install EasyOCR, run:")
    print("pip install easyocr")
    
except Exception as e:
    print(f"✗ Error testing EasyOCR: {e}")
    import traceback
    traceback.print_exc()