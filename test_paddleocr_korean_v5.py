"""
PP-OCRv5 한국어 모델 테스트 스크립트
korean_PP-OCRv5_mobile_rec 모델 사용 확인
"""

import os
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import logging

# 로깅 설정
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_test_image_with_korean_text():
    """한국어 텍스트가 포함된 테스트 이미지 생성"""
    # 흰색 배경 이미지 생성
    width, height = 800, 600
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # 한국어 텍스트 리스트
    korean_texts = [
        "홍길동 고객님",
        "김철수 매니저",
        "이영희 대리",
        "박민수 사원",
        "최지우 팀장",
        "테스트 문서",
        "2025년 7월 25일",
        "주문번호: 12345",
        "금액: 50,000원",
        "상태: 처리완료"
    ]
    
    # 폰트 설정 (Windows 기본 한글 폰트)
    try:
        font = ImageFont.truetype("C:\\Windows\\Fonts\\malgun.ttf", 32)
    except:
        logger.warning("한글 폰트를 찾을 수 없습니다. 기본 폰트 사용")
        font = ImageFont.load_default()
    
    # 텍스트 그리기
    y_position = 50
    for text in korean_texts:
        draw.text((50, y_position), text, font=font, fill='black')
        y_position += 50
    
    # 이미지 저장
    test_image_path = "test_korean_text.png"
    img.save(test_image_path)
    logger.info(f"테스트 이미지 생성 완료: {test_image_path}")
    return test_image_path

def test_paddleocr_korean():
    """PaddleOCR 한국어 인식 테스트"""
    try:
        # PaddleOCR 임포트
        from paddleocr import PaddleOCR
        
        logger.info("=== PP-OCRv5 한국어 모델 테스트 시작 ===")
        
        # PP-OCRv5 한국어 모델 초기화
        logger.info("PaddleOCR 초기화 중...")
        ocr = PaddleOCR(
            lang='korean',              # korean_PP-OCRv5_mobile_rec 모델 사용
            use_angle_cls=True,         # 텍스트 각도 분류 활성화
            show_log=False              # 상세 로그 비활성화
        )
        logger.info("PaddleOCR 초기화 완료")
        
        # 테스트 이미지 생성
        test_image_path = create_test_image_with_korean_text()
        
        # OCR 수행
        logger.info("OCR 수행 중...")
        results = ocr.ocr(test_image_path)
        
        # 결과 형식 분석
        logger.info(f"\n=== 결과 형식 분석 ===")
        logger.info(f"Results type: {type(results)}")
        logger.info(f"Results content: {results}")
        
        if results:
            logger.info(f"Results length: {len(results)}")
            
            # 첫 번째 요소 분석
            if len(results) > 0:
                first_element = results[0]
                logger.info(f"\nFirst element type: {type(first_element)}")
                logger.info(f"First element: {first_element}")
                
                # 딕셔너리인 경우
                if isinstance(first_element, dict):
                    logger.info(f"Dictionary keys: {list(first_element.keys())}")
                
                # 리스트인 경우
                elif isinstance(first_element, list) and len(first_element) > 0:
                    logger.info(f"First element length: {len(first_element)}")
                    if first_element:
                        first_line = first_element[0]
                        logger.info(f"\nFirst line type: {type(first_line)}")
                        logger.info(f"First line: {first_line}")
        
        # 결과 파싱 시도
        logger.info(f"\n=== 인식된 텍스트 ===")
        if results:
            # 다양한 결과 형식 처리
            parsed_texts = []
            
            # 케이스 1: [[[[x,y],...], (text, conf)], ...] 형식
            if isinstance(results, list) and len(results) > 0:
                for page_idx, page_result in enumerate(results):
                    if isinstance(page_result, list):
                        for line_idx, line in enumerate(page_result):
                            try:
                                if isinstance(line, list) and len(line) >= 2:
                                    text_info = line[1]
                                    if isinstance(text_info, (list, tuple)) and len(text_info) >= 2:
                                        text = text_info[0]
                                        confidence = text_info[1]
                                        parsed_texts.append(f"{text} (신뢰도: {confidence:.2f})")
                                        logger.info(f"[{line_idx}] {text} (신뢰도: {confidence:.2f})")
                            except Exception as e:
                                logger.error(f"라인 파싱 오류: {e}, line: {line}")
            
            # 케이스 2: 딕셔너리 형식 처리
            elif isinstance(results, dict):
                logger.info("딕셔너리 형식의 결과 처리 중...")
                for key, value in results.items():
                    logger.info(f"Key: {key}, Value type: {type(value)}")
        
        else:
            logger.warning("OCR 결과가 비어있습니다.")
        
        # 테스트 이미지 삭제
        if os.path.exists(test_image_path):
            os.remove(test_image_path)
            
        logger.info("\n=== 테스트 완료 ===")
        
    except ImportError as e:
        logger.error(f"PaddleOCR 임포트 실패: {e}")
        logger.error("설치 명령: pip install paddlepaddle paddleocr")
    except Exception as e:
        logger.error(f"테스트 중 오류 발생: {e}")
        import traceback
        logger.error(traceback.format_exc())

def test_direct_paddleocr_api():
    """PaddleOCR API 직접 테스트"""
    try:
        from paddleocr import PaddleOCR
        
        logger.info("\n=== PaddleOCR 직접 API 테스트 ===")
        
        # 간단한 테스트 이미지 생성
        img = np.ones((100, 300, 3), dtype=np.uint8) * 255
        
        # PaddleOCR 초기화
        ocr = PaddleOCR(lang='korean')
        
        # OCR 수행
        result = ocr.ocr(img)
        
        logger.info(f"Direct API result: {result}")
        logger.info(f"Result type: {type(result)}")
        
    except Exception as e:
        logger.error(f"직접 API 테스트 실패: {e}")

if __name__ == "__main__":
    # PP-OCRv5 한국어 모델 테스트
    test_paddleocr_korean()
    
    # 직접 API 테스트
    test_direct_paddleocr_api()