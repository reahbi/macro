"""
간단한 OCR 테스트 - 실제 PaddleTextExtractor 사용
"""

import os
import sys

# 프로젝트 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)
sys.path.insert(0, os.path.join(current_dir, 'src'))

# 로깅 설정
import logging
logging.basicConfig(level=logging.DEBUG)

def test_simple():
    """간단한 OCR 테스트"""
    try:
        # PaddleTextExtractor 임포트
        from vision.text_extractor_paddle import paddle_text_extractor
        
        print("=== PaddleTextExtractor 테스트 시작 ===")
        
        # 화면 전체에서 텍스트 추출 시도
        print("\n전체 화면에서 텍스트 추출 중...")
        results = paddle_text_extractor.extract_text_from_region()
        
        print(f"\n추출된 텍스트 개수: {len(results)}")
        
        if results:
            print("\n추출된 텍스트:")
            for i, result in enumerate(results[:5]):  # 처음 5개만 출력
                print(f"{i+1}. '{result.text}' (신뢰도: {result.confidence:.2f})")
        
        # 작은 영역에서 테스트
        print("\n\n작은 영역(100x100)에서 텍스트 추출 중...")
        small_results = paddle_text_extractor.extract_text_from_region((100, 100, 300, 200))
        print(f"추출된 텍스트 개수: {len(small_results)}")
        
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_simple()