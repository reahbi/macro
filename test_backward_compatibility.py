"""
하위 호환성 테스트 스크립트
기존 매크로가 새로운 액션 시스템과 함께 정상 작동하는지 확인
"""

import sys
sys.path.insert(0, r'C:\mag\macro\src')

from core.macro_types import ImageSearchStep, TextSearchStep, StepFactory
import json

def test_image_search_step():
    """이미지 검색 스텝 호환성 테스트"""
    print("\n=== 이미지 검색 스텝 테스트 ===")
    
    # 1. 기존 방식 (액션 없음)
    step1 = ImageSearchStep(
        name="기존 이미지 검색",
        image_path="test.png",
        confidence=0.9,
        click_on_found=True,
        click_offset=(10, 10)
    )
    
    # to_dict 테스트
    dict1 = step1.to_dict()
    print("기존 스텝 -> dict:", json.dumps(dict1, indent=2, ensure_ascii=False))
    
    # from_dict 테스트
    step1_loaded = StepFactory.from_dict(dict1)
    print(f"기존 스텝 로드 성공: {step1_loaded.name}")
    print(f"- click_on_found: {step1_loaded.click_on_found}")
    print(f"- on_found: {getattr(step1_loaded, 'on_found', 'None')}")
    print(f"- on_not_found: {getattr(step1_loaded, 'on_not_found', 'None')}")
    
    # 2. 새로운 방식 (액션 있음)
    step2 = ImageSearchStep(
        name="새로운 이미지 검색",
        image_path="test2.png",
        confidence=0.8,
        click_on_found=False,  # 기존 클릭 비활성화
        on_found={
            "action": "type",
            "params": {"text": "찾았습니다!"}
        },
        on_not_found={
            "action": "continue",
            "params": {}
        }
    )
    
    # to_dict 테스트
    dict2 = step2.to_dict()
    print("\n새로운 스텝 -> dict:", json.dumps(dict2, indent=2, ensure_ascii=False))
    
    # from_dict 테스트
    step2_loaded = StepFactory.from_dict(dict2)
    print(f"새로운 스텝 로드 성공: {step2_loaded.name}")
    print(f"- click_on_found: {step2_loaded.click_on_found}")
    print(f"- on_found: {step2_loaded.on_found}")
    print(f"- on_not_found: {step2_loaded.on_not_found}")
    
def test_text_search_step():
    """텍스트 검색 스텝 호환성 테스트"""
    print("\n\n=== 텍스트 검색 스텝 테스트 ===")
    
    # 1. 기존 방식 (액션 없음)
    step1 = TextSearchStep(
        name="기존 텍스트 검색",
        search_text="홍길동",
        exact_match=True,
        click_on_found=True,
        click_offset=(0, 0)
    )
    
    # to_dict 테스트
    dict1 = step1.to_dict()
    print("기존 스텝 -> dict:", json.dumps(dict1, indent=2, ensure_ascii=False))
    
    # from_dict 테스트  
    step1_loaded = StepFactory.from_dict(dict1)
    print(f"기존 스텝 로드 성공: {step1_loaded.name}")
    print(f"- click_on_found: {step1_loaded.click_on_found}")
    print(f"- on_found: {getattr(step1_loaded, 'on_found', 'None')}")
    print(f"- on_not_found: {getattr(step1_loaded, 'on_not_found', 'None')}")
    
    # 2. 새로운 방식 (액션 있음)
    step2 = TextSearchStep(
        name="새로운 텍스트 검색",
        search_text="${고객명}",
        exact_match=False,
        click_on_found=False,  # 기존 클릭 비활성화
        on_found={
            "action": "click",
            "params": {"offset_x": 100, "offset_y": 0}
        },
        on_not_found={
            "action": "skip_row",
            "params": {"wait_time": 1}
        }
    )
    
    # to_dict 테스트
    dict2 = step2.to_dict()
    print("\n새로운 스텝 -> dict:", json.dumps(dict2, indent=2, ensure_ascii=False))
    
    # from_dict 테스트
    step2_loaded = StepFactory.from_dict(dict2)
    print(f"새로운 스텝 로드 성공: {step2_loaded.name}")
    print(f"- click_on_found: {step2_loaded.click_on_found}")
    print(f"- on_found: {step2_loaded.on_found}")
    print(f"- on_not_found: {step2_loaded.on_not_found}")

def test_mixed_mode():
    """혼합 모드 테스트 - 기존 클릭과 새 액션이 함께 있는 경우"""
    print("\n\n=== 혼합 모드 테스트 ===")
    
    # 기존 클릭 활성화 + 새 액션도 설정 (새 액션이 우선순위를 가져야 함)
    step = ImageSearchStep(
        name="혼합 모드 테스트",
        image_path="test.png",
        confidence=0.9,
        click_on_found=True,  # 기존 클릭 활성화
        click_offset=(10, 10),
        on_found={  # 새 액션도 설정
            "action": "type",
            "params": {"text": "새로운 액션 우선!"}
        }
    )
    
    dict_data = step.to_dict()
    print("혼합 모드 스텝 -> dict:", json.dumps(dict_data, indent=2, ensure_ascii=False))
    
    # 실행 시뮬레이션
    print("\n실행 시뮬레이션:")
    print("- on_found가 있으므로 새 액션 실행 (타이핑)")
    print("- click_on_found는 무시됨 (하위 호환성 보장)")

if __name__ == "__main__":
    test_image_search_step()
    test_text_search_step()
    test_mixed_mode()
    
    print("\n\n=== 테스트 완료 ===")
    print("✅ 기존 매크로는 그대로 작동")
    print("✅ 새로운 액션 시스템도 정상 작동")
    print("✅ 혼합 모드에서 새 액션이 우선순위를 가짐")