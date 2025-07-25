"""
PaddleOCR 테스트 스크립트
한국어 텍스트 인식 성능 테스트
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.vision.text_extractor_paddle import PaddleTextExtractor
from src.logger.app_logger import get_logger
import time

def test_paddleocr_korean():
    """한국어 텍스트 인식 테스트"""
    logger = get_logger(__name__)
    
    try:
        print("="*50)
        print("PaddleOCR 한국어 텍스트 인식 테스트")
        print("="*50)
        
        # 1. PaddleOCR 초기화
        print("\n1. PaddleOCR 초기화 중...")
        start_time = time.time()
        extractor = PaddleTextExtractor()
        init_time = time.time() - start_time
        print(f"   초기화 완료! (소요시간: {init_time:.2f}초)")
        
        # 2. 전체 화면에서 텍스트 추출
        print("\n2. 전체 화면에서 텍스트 추출 중...")
        start_time = time.time()
        results = extractor.extract_text_from_region()
        extract_time = time.time() - start_time
        
        print(f"   추출 완료! (소요시간: {extract_time:.2f}초)")
        print(f"   추출된 텍스트 개수: {len(results)}개")
        
        # 3. 추출된 텍스트 출력
        if results:
            print("\n3. 추출된 텍스트 목록:")
            print("-"*50)
            for i, result in enumerate(results[:10]):  # 상위 10개만 출력
                print(f"   [{i+1}] '{result.text}' (신뢰도: {result.confidence:.2%})")
                print(f"        위치: {result.center}")
            if len(results) > 10:
                print(f"   ... 외 {len(results)-10}개")
        else:
            print("\n3. 추출된 텍스트가 없습니다.")
        
        # 4. 특정 한국어 텍스트 찾기 테스트
        test_names = ["홍길동", "김철수", "이영희", "박민수", "최지우"]
        print(f"\n4. 특정 텍스트 찾기 테스트: {test_names}")
        print("-"*50)
        
        for name in test_names:
            print(f"\n   '{name}' 검색 중...")
            start_time = time.time()
            result = extractor.find_text(name, confidence_threshold=0.3)
            search_time = time.time() - start_time
            
            if result:
                print(f"   ✓ 찾음! 위치: {result.center} (신뢰도: {result.confidence:.2%})")
                print(f"   실제 인식된 텍스트: '{result.text}'")
            else:
                print(f"   ✗ 찾지 못함")
            print(f"   (검색 시간: {search_time:.2f}초)")
        
        # 5. 부분 매칭 테스트
        print("\n5. 부분 매칭 테스트")
        print("-"*50)
        partial_text = "길"  # '홍길동'의 일부
        print(f"   '{partial_text}' 포함된 텍스트 검색 중...")
        
        all_matches = extractor.find_all_text(partial_text, exact_match=False)
        if all_matches:
            print(f"   찾은 개수: {len(all_matches)}개")
            for i, match in enumerate(all_matches[:5]):  # 상위 5개만
                print(f"   [{i+1}] '{match.text}' at {match.center}")
        else:
            print("   매칭되는 텍스트를 찾지 못했습니다.")
        
        # 6. 모델 사전 로드 테스트
        print("\n6. 모델 사전 로드 테스트")
        start_time = time.time()
        extractor.preload_models()
        preload_time = time.time() - start_time
        print(f"   사전 로드 완료! (소요시간: {preload_time:.2f}초)")
        
        print("\n" + "="*50)
        print("테스트 완료!")
        print("="*50)
        
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # PaddleOCR 테스트 실행
    test_paddleocr_korean()