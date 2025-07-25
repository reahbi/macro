"""
PP-OCRv5 수정 후 테스트 스크립트
"""

import os
import sys

# 프로젝트 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

# 로깅 설정
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_ocr_fixed():
    """수정된 OCR 테스트"""
    try:
        from vision.text_extractor_paddle import paddle_text_extractor
        from PIL import Image, ImageDraw, ImageFont
        import numpy as np
        
        print("=== PP-OCRv5 한국어 인식 테스트 ===")
        
        # 테스트 이미지 생성
        print("\n1. 테스트 이미지 생성 중...")
        img = Image.new('RGB', (800, 400), color='white')
        draw = ImageDraw.Draw(img)
        
        # Windows 한글 폰트
        try:
            font = ImageFont.truetype("C:\\Windows\\Fonts\\malgun.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        # 한국어 텍스트 그리기
        test_texts = [
            ("안녕하세요", 50, 50),
            ("테스트 문서입니다", 50, 120),
            ("홍길동 고객님", 50, 190),
            ("2025년 7월 25일", 50, 260),
            ("주문번호: 12345", 50, 330)
        ]
        
        for text, x, y in test_texts:
            draw.text((x, y), text, font=font, fill='black')
        
        # 이미지 저장
        test_path = "test_korean_ocr.png"
        img.save(test_path)
        print(f"테스트 이미지 저장: {test_path}")
        
        # numpy 배열로 변환
        img_array = np.array(img)
        
        # OCR 수행
        print("\n2. OCR 수행 중...")
        from paddleocr import PaddleOCR
        
        ocr = PaddleOCR(
            lang='korean',
            use_angle_cls=True,
            show_log=False
        )
        
        # 직접 OCR 호출하여 원본 결과 확인
        raw_results = ocr.ocr(img_array)
        print(f"\n원본 OCR 결과 타입: {type(raw_results)}")
        if raw_results:
            print(f"결과 길이: {len(raw_results)}")
            if len(raw_results) > 0:
                print(f"첫 번째 요소 타입: {type(raw_results[0])}")
        
        # PaddleTextExtractor로 테스트
        print("\n3. PaddleTextExtractor로 테스트...")
        results = paddle_text_extractor.extract_text_from_region()
        
        print(f"\n추출된 텍스트 개수: {len(results)}")
        
        if results:
            print("\n인식된 텍스트:")
            for i, result in enumerate(results):
                print(f"{i+1}. '{result.text}' (신뢰도: {result.confidence:.2f}, 위치: {result.center})")
        else:
            print("\n텍스트를 찾지 못했습니다.")
        
        # 특정 텍스트 찾기 테스트
        print("\n4. 특정 텍스트 찾기 테스트...")
        target = "테스트"
        found = paddle_text_extractor.find_text(target)
        if found:
            print(f"'{target}' 찾음: 위치 {found.center}, 신뢰도 {found.confidence:.2f}")
        else:
            print(f"'{target}'를 찾지 못했습니다.")
        
        # 이미지 삭제
        if os.path.exists(test_path):
            os.remove(test_path)
            
        print("\n=== 테스트 완료 ===")
        
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_ocr_fixed()