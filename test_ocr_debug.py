"""
PaddleOCR 디버깅 스크립트
실제 OCR 결과 형식을 확인하기 위한 테스트
"""

import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# 프로젝트 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

def test_paddleocr_debug():
    """PaddleOCR 결과 형식 디버깅"""
    try:
        from paddleocr import PaddleOCR
        import mss
        
        print("=== PaddleOCR 디버깅 시작 ===")
        
        # PaddleOCR 초기화
        print("PaddleOCR 초기화 중...")
        ocr = PaddleOCR(
            lang='korean',
            use_angle_cls=True,
            show_log=True  # 상세 로그 활성화
        )
        
        # 화면 캡처
        print("\n화면 캡처 중...")
        with mss.mss() as sct:
            # 화면의 일부만 캡처 (상단 좌측)
            monitor = {"left": 0, "top": 0, "width": 800, "height": 600}
            screenshot = sct.grab(monitor)
            
            # PIL Image로 변환
            img_pil = Image.frombytes('RGB', (screenshot.width, screenshot.height), 
                                    screenshot.bgra, 'raw', 'BGRX')
            
            # numpy 배열로 변환
            img_array = np.array(img_pil)
            
        print(f"이미지 크기: {img_array.shape}")
        
        # OCR 수행
        print("\nOCR 수행 중...")
        results = ocr.ocr(img_array)
        
        # 결과 상세 분석
        print("\n=== OCR 결과 분석 ===")
        print(f"Results type: {type(results)}")
        print(f"Results: {results}")
        
        if results is not None:
            print(f"\nResults length: {len(results)}")
            
            # 각 요소 분석
            for i, element in enumerate(results):
                print(f"\n--- Element {i} ---")
                print(f"Type: {type(element)}")
                print(f"Content: {element}")
                
                if isinstance(element, list) and len(element) > 0:
                    print(f"First item type: {type(element[0])}")
                    if element[0]:
                        print(f"First item: {element[0]}")
                        
                        # 첫 번째 라인 상세 분석
                        if isinstance(element[0], (list, tuple)) and len(element[0]) >= 2:
                            print(f"\nFirst line bbox: {element[0][0]}")
                            print(f"First line text info: {element[0][1]}")
                            print(f"Bbox type: {type(element[0][0])}")
                            print(f"Text info type: {type(element[0][1])}")
        
        # 테스트 이미지로도 확인
        print("\n\n=== 테스트 이미지로 확인 ===")
        
        # 간단한 테스트 이미지 생성
        test_img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(test_img)
        
        # Windows 한글 폰트 사용
        try:
            font = ImageFont.truetype("C:\\Windows\\Fonts\\malgun.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # 텍스트 그리기
        draw.text((50, 50), "안녕하세요", font=font, fill='black')
        draw.text((50, 100), "Hello World", font=font, fill='black')
        
        # numpy 배열로 변환
        test_array = np.array(test_img)
        
        # OCR 수행
        print("테스트 이미지 OCR 중...")
        test_results = ocr.ocr(test_array)
        
        print(f"\nTest results type: {type(test_results)}")
        print(f"Test results: {test_results}")
        
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_paddleocr_debug()