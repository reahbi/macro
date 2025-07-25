"""
PaddleOCR 파라미터 테스트
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_paddleocr_init():
    print("Testing PaddleOCR initialization...")
    
    try:
        from paddleocr import PaddleOCR
        
        # 가장 기본적인 초기화 시도
        print("\n1. Testing with minimal parameters...")
        try:
            ocr = PaddleOCR(lang='korean')
            print("✓ Success with minimal parameters")
        except Exception as e:
            print(f"✗ Failed: {e}")
        
        # use_angle_cls 추가
        print("\n2. Testing with use_angle_cls...")
        try:
            ocr = PaddleOCR(lang='korean', use_angle_cls=True)
            print("✓ Success with use_angle_cls")
        except Exception as e:
            print(f"✗ Failed: {e}")
        
        # show_log 추가
        print("\n3. Testing with show_log...")
        try:
            ocr = PaddleOCR(lang='korean', use_angle_cls=True, show_log=False)
            print("✓ Success with show_log")
        except Exception as e:
            print(f"✗ Failed: {e}")
        
        # use_gpu 추가
        print("\n4. Testing with use_gpu...")
        try:
            ocr = PaddleOCR(lang='korean', use_angle_cls=True, show_log=False, use_gpu=False)
            print("✓ Success with use_gpu")
        except Exception as e:
            print(f"✗ Failed: {e}")
            
        # 지원되는 언어 확인
        print("\n5. Testing language parameter variations...")
        for lang in ['korean', 'ko', 'kor', 'ch']:
            try:
                ocr = PaddleOCR(lang=lang, show_log=False)
                print(f"✓ Success with lang='{lang}'")
            except Exception as e:
                print(f"✗ Failed with lang='{lang}': {e}")
        
    except ImportError:
        print("PaddleOCR not installed!")

if __name__ == "__main__":
    test_paddleocr_init()