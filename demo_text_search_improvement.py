"""
PaddleOCR 텍스트 검색 데모
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from vision.text_extractor_paddle import PaddleTextExtractor
import time

def demo():
    print("=== PaddleOCR 텍스트 검색 데모 ===\n")
    
    # 검색할 텍스트 (화면에 보이는 텍스트로 변경하세요)
    search_text = input("검색할 텍스트를 입력하세요: ")
    
    print(f"\n'{search_text}' 검색 중...\n")
    
    # PaddleOCR 초기화
    print("PaddleOCR 초기화 중...")
    extractor = PaddleTextExtractor()
    
    # 텍스트 검색
    start = time.time()
    result = extractor.find_text(search_text, confidence_threshold=0.5)
    elapsed = time.time() - start
    
    if result:
        print(f"✓ 찾음! 위치: {result.center}, 신뢰도: {result.confidence:.2f}")
    else:
        print("✗ 찾지 못함")
    print(f"소요 시간: {elapsed:.2f}초")
    
    # 전체 텍스트 추출
    print("\n전체 화면에서 추출된 텍스트:")
    all_results = extractor.extract_text_from_region()
    for i, res in enumerate(all_results[:10]):  # 상위 10개만
        print(f"  [{i+1}] '{res.text}' - 신뢰도: {res.confidence:.2%}")
    
    if len(all_results) > 10:
        print(f"  ... 외 {len(all_results)-10}개")

if __name__ == "__main__":
    demo()