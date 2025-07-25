"""
Quick check to see if OCR is working in the app environment
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from utils.ocr_manager import OCRManager

# Check OCR status
ocr_manager = OCRManager()

print("=== OCR Status Check ===")
print(f"OCR Available: {ocr_manager.is_available()}")
print(f"Installation Status: {ocr_manager.get_installation_status()}")

if ocr_manager.is_available():
    print("\n✓ OCR is available and ready to use!")
    
    # Try a quick test
    try:
        from vision.text_extractor_paddle import PaddleTextExtractor
        extractor = PaddleTextExtractor()
        print("✓ PaddleOCR text extractor initialized successfully")
        
        # Test on a small region
        results = extractor.extract_text_from_region((0, 0, 300, 100))
        print(f"✓ OCR test completed - found {len(results)} text items")
        
    except Exception as e:
        print(f"✗ Error during OCR test: {e}")
else:
    print("\n✗ OCR is not available")
    print("The app should have prompted you to install OCR dependencies.")
    print("If you declined, you can manually install with:")
    print("  pip install paddlepaddle>=2.5.0 paddleocr>=2.7.0")