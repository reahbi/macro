"""
Unit tests for text search functionality
텍스트 검색 기능의 단위 테스트
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
import numpy as np
from PIL import Image

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from vision.text_extractor_paddle import PaddleTextExtractor, TextResult


def position_to_bbox_and_center(position):
    """Convert position (4 corner points) to bbox and center"""
    # position is [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
    xs = [p[0] for p in position]
    ys = [p[1] for p in position]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    width = max_x - min_x
    height = max_y - min_y
    center_x = (min_x + max_x) // 2
    center_y = (min_y + max_y) // 2
    return (min_x, min_y, width, height), (center_x, center_y)


def create_text_result(text, position, confidence):
    """Helper to create TextResult from position"""
    bbox, center = position_to_bbox_and_center(position)
    return TextResult(text=text, confidence=confidence, bbox=bbox, center=center)


class TestTextResult(unittest.TestCase):
    """TextResult 클래스 테스트"""
    
    def test_text_result_creation(self):
        """TextResult 객체 생성 테스트"""
        position = [[10, 20], [100, 20], [100, 50], [10, 50]]
        bbox, center = position_to_bbox_and_center(position)
        
        result = TextResult(
            text="테스트",
            confidence=0.95,
            bbox=bbox,
            center=center
        )
        
        self.assertEqual(result.text, "테스트")
        self.assertEqual(result.confidence, 0.95)
        self.assertEqual(result.center, (55, 35))  # 중심점 계산 확인
        
    def test_text_result_center_calculation(self):
        """중심점 계산 테스트"""
        # 사각형 좌표
        position = [[0, 0], [100, 0], [100, 50], [0, 50]]
        bbox, center = position_to_bbox_and_center(position)
        
        result = TextResult(
            text="test",
            confidence=0.9,
            bbox=bbox,
            center=center
        )
        
        self.assertEqual(result.center, (50, 25))


class TestPaddleTextExtractor(unittest.TestCase):
    """PaddleTextExtractor 클래스 테스트"""
    
    def setUp(self):
        """테스트 전 설정"""
        # PaddleOCR 모킹을 위한 설정
        self.mock_ocr_patcher = patch('vision.text_extractor_paddle.PaddleOCR')
        self.mock_ocr_class = self.mock_ocr_patcher.start()
        
        # 싱글톤 리셋
        PaddleTextExtractor._instance = None
        PaddleTextExtractor._ocr = None
        
    def tearDown(self):
        """테스트 후 정리"""
        self.mock_ocr_patcher.stop()
        PaddleTextExtractor._instance = None
        PaddleTextExtractor._ocr = None
        
    def test_singleton_pattern(self):
        """싱글톤 패턴 테스트"""
        extractor1 = PaddleTextExtractor()
        extractor2 = PaddleTextExtractor()
        
        self.assertIs(extractor1, extractor2)
        
    def test_ocr_initialization(self):
        """OCR 초기화 테스트"""
        mock_ocr_instance = Mock()
        self.mock_ocr_class.return_value = mock_ocr_instance
        
        extractor = PaddleTextExtractor()
        _ = extractor._get_ocr()
        
        # PaddleOCR이 올바른 파라미터로 초기화되었는지 확인
        self.mock_ocr_class.assert_called_once()
        call_args = self.mock_ocr_class.call_args[1]
        self.assertEqual(call_args['lang'], 'korean')
        # use_gpu 파라미터는 더 이상 사용되지 않음
        
    @patch('vision.text_extractor_paddle.mss')
    def test_extract_text_from_full_screen(self, mock_mss):
        """전체 화면 텍스트 추출 테스트"""
        # 화면 캡처 모킹
        mock_sct = Mock()
        mock_mss.mss.return_value.__enter__.return_value = mock_sct
        
        # monitors 속성 추가
        mock_sct.monitors = [
            {"left": 0, "top": 0, "width": 1920, "height": 1080}
        ]
        
        # 가상의 스크린샷 데이터
        mock_screenshot = Mock()
        mock_screenshot.width = 1920
        mock_screenshot.height = 1080
        # bgra needs to be actual bytes for Image.frombytes (4 bytes per pixel for BGRA)
        mock_screenshot.bgra = b'\x00' * (1920 * 1080 * 4)
        mock_sct.grab.return_value = mock_screenshot
        
        # OCR 결과 모킹
        mock_ocr_instance = Mock()
        mock_ocr_result = [
            [
                [[100, 100], [200, 100], [200, 130], [100, 130]],
                ("홍길동", 0.95)
            ],
            [
                [[300, 200], [400, 200], [400, 230], [300, 230]],
                ("김철수", 0.92)
            ]
        ]
        mock_ocr_instance.ocr.return_value = [mock_ocr_result]
        self.mock_ocr_class.return_value = mock_ocr_instance
        
        # 테스트 실행
        extractor = PaddleTextExtractor()
        results = extractor.extract_text_from_region()
        
        # 결과 검증
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].text, "홍길동")
        self.assertEqual(results[0].confidence, 0.95)
        self.assertEqual(results[1].text, "김철수")
        self.assertEqual(results[1].confidence, 0.92)
        
    def test_find_text_exact_match(self):
        """정확한 텍스트 매칭 테스트"""
        # OCR 결과 모킹
        mock_ocr_instance = Mock()
        self.mock_ocr_class.return_value = mock_ocr_instance
        
        extractor = PaddleTextExtractor()
        
        # extract_text_from_region 모킹
        mock_results = [
            create_text_result("홍길동", [[10, 10], [100, 10], [100, 40], [10, 40]], 0.95),
            create_text_result("김철수", [[10, 50], [100, 50], [100, 80], [10, 80]], 0.90),
            create_text_result("이영희", [[10, 90], [100, 90], [100, 120], [10, 120]], 0.85)
        ]
        
        with patch.object(extractor, 'extract_text_from_region', return_value=mock_results):
            # 정확한 매칭
            result = extractor.find_text("홍길동", exact_match=True)
            self.assertIsNotNone(result)
            self.assertEqual(result.text, "홍길동")
            
            # 찾을 수 없는 텍스트
            result = extractor.find_text("박민수", exact_match=True)
            self.assertIsNone(result)
            
    def test_find_text_partial_match(self):
        """부분 텍스트 매칭 테스트"""
        mock_ocr_instance = Mock()
        self.mock_ocr_class.return_value = mock_ocr_instance
        
        extractor = PaddleTextExtractor()
        
        # extract_text_from_region 모킹
        mock_results = [
            create_text_result("홍길동 님", [[10, 10], [100, 10], [100, 40], [10, 40]], 0.95),
            create_text_result("김철수 대리", [[10, 50], [100, 50], [100, 80], [10, 80]], 0.90)
        ]
        
        with patch.object(extractor, 'extract_text_from_region', return_value=mock_results):
            # 부분 매칭
            result = extractor.find_text("홍길동", exact_match=False)
            self.assertIsNotNone(result)
            self.assertEqual(result.text, "홍길동 님")
            
    def test_find_all_text(self):
        """모든 매칭 텍스트 찾기 테스트"""
        mock_ocr_instance = Mock()
        self.mock_ocr_class.return_value = mock_ocr_instance
        
        extractor = PaddleTextExtractor()
        
        # extract_text_from_region 모킹
        mock_results = [
            create_text_result("홍길동", [[10, 10], [100, 10], [100, 40], [10, 40]], 0.95),
            create_text_result("홍길순", [[10, 50], [100, 50], [100, 80], [10, 80]], 0.90),
            create_text_result("김철수", [[10, 90], [100, 90], [100, 120], [10, 120]], 0.85)
        ]
        
        with patch.object(extractor, 'extract_text_from_region', return_value=mock_results):
            # 부분 매칭으로 모두 찾기
            results = extractor.find_all_text("홍", exact_match=False)
            self.assertEqual(len(results), 2)
            self.assertEqual(results[0].text, "홍길동")
            self.assertEqual(results[1].text, "홍길순")
            
    def test_confidence_threshold(self):
        """신뢰도 임계값 테스트"""
        mock_ocr_instance = Mock()
        self.mock_ocr_class.return_value = mock_ocr_instance
        
        extractor = PaddleTextExtractor()
        
        # extract_text_from_region 모킹
        mock_results = [
            create_text_result("홍길동", [[10, 10], [100, 10], [100, 40], [10, 40]], 0.95),
            create_text_result("김철수", [[10, 50], [100, 50], [100, 80], [10, 80]], 0.60),
            create_text_result("이영희", [[10, 90], [100, 90], [100, 120], [10, 120]], 0.40)
        ]
        
        # Mock extract_text_from_region to respect confidence_threshold
        def mock_extract(region=None, confidence_threshold=0.5):
            return [r for r in mock_results if r.confidence >= confidence_threshold]
        
        with patch.object(extractor, 'extract_text_from_region', side_effect=mock_extract):
            # 높은 신뢰도 임계값
            result = extractor.find_text("김철수", confidence_threshold=0.8)
            self.assertIsNone(result)  # 0.60 < 0.8
            
            # 낮은 신뢰도 임계값
            result = extractor.find_text("김철수", confidence_threshold=0.5)
            self.assertIsNotNone(result)
            self.assertEqual(result.text, "김철수")
            
    def test_error_handling(self):
        """에러 처리 테스트"""
        # OCR 초기화 실패 시뮬레이션
        self.mock_ocr_class.side_effect = Exception("PaddleOCR 초기화 실패")
        
        extractor = PaddleTextExtractor()
        
        # 초기화 실패 시 RuntimeError 발생
        with self.assertRaises(RuntimeError):
            extractor._get_ocr()
            
    @patch('vision.text_extractor_paddle.mss')
    def test_region_extraction(self, mock_mss):
        """특정 영역 텍스트 추출 테스트"""
        # 화면 캡처 모킹
        mock_sct = Mock()
        mock_mss.mss.return_value.__enter__.return_value = mock_sct
        
        # 가상의 스크린샷 데이터
        mock_screenshot = MagicMock()
        mock_screenshot.width = 500
        mock_screenshot.height = 300
        mock_screenshot.rgb = b'\x00' * (500 * 300 * 3)
        mock_sct.grab.return_value = mock_screenshot
        
        # OCR 결과 모킹
        mock_ocr_instance = Mock()
        mock_ocr_result = [
            [
                [[10, 10], [100, 10], [100, 40], [10, 40]],
                ("테스트", 0.90)
            ]
        ]
        mock_ocr_instance.ocr.return_value = [mock_ocr_result]
        self.mock_ocr_class.return_value = mock_ocr_instance
        
        # 테스트 실행
        extractor = PaddleTextExtractor()
        results = extractor.extract_text_from_region(region=(100, 100, 500, 300))
        
        # grab이 올바른 영역으로 호출되었는지 확인
        mock_sct.grab.assert_called_once()
        grab_call = mock_sct.grab.call_args[0][0]
        self.assertEqual(grab_call['left'], 100)
        self.assertEqual(grab_call['top'], 100)
        self.assertEqual(grab_call['width'], 500)
        self.assertEqual(grab_call['height'], 300)


if __name__ == '__main__':
    unittest.main()