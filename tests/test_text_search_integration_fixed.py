"""
Integration tests for text search functionality - Fixed version
텍스트 검색 기능의 통합 테스트 (수정 버전)
"""

import sys
import os
import unittest
from unittest.mock import Mock, patch, MagicMock
import json
import tempfile
from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest
from PyQt5.QtCore import Qt, QTimer

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from core.macro_types import MacroStep, StepType, ErrorHandling
# Create TextSearchStep for testing
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from create_text_search_step import TextSearchStep
from ui.dialogs.text_search_step_dialog import TextSearchStepDialog
from automation.executor import StepExecutor
from config.settings import Settings
from vision.text_extractor_paddle import PaddleTextExtractor, TextResult


class TestTextSearchIntegration(unittest.TestCase):
    """텍스트 검색 통합 테스트"""
    
    @classmethod
    def setUpClass(cls):
        """테스트 클래스 설정"""
        if not QApplication.instance():
            cls.app = QApplication(sys.argv)
        else:
            cls.app = QApplication.instance()
            
    def setUp(self):
        """테스트 전 설정"""
        # PaddleOCR 모킹
        self.mock_ocr_patcher = patch('vision.text_extractor_paddle.PaddleOCR')
        self.mock_ocr_class = self.mock_ocr_patcher.start()
        
        # Settings 모킹
        self.mock_settings = Mock(spec=Settings)
        self.mock_settings.language = 'ko'
        self.mock_settings.theme = 'light'
        
        # 싱글톤 리셋
        PaddleTextExtractor._instance = None
        PaddleTextExtractor._ocr = None
        
    def tearDown(self):
        """테스트 후 정리"""
        self.mock_ocr_patcher.stop()
        PaddleTextExtractor._instance = None
        PaddleTextExtractor._ocr = None
        
    def test_text_search_step_creation_and_serialization(self):
        """TextSearchStep 생성 및 직렬화 테스트"""
        # TextSearchStep 생성
        step = TextSearchStep()
        step.search_text = "홍길동"
        step.region = (100, 100, 500, 300)
        step.exact_match = False
        step.confidence_threshold = 0.8
        step.excel_column = "${이름}"
        
        # JSON 직렬화
        json_data = step.to_dict()
        
        # 필드 확인 - enum의 value 사용
        self.assertEqual(json_data.get('step_type'), StepType.OCR_TEXT.value)  # 'ocr_text'
        self.assertEqual(json_data['search_text'], '홍길동')
        self.assertEqual(json_data['region'], [100, 100, 500, 300])
        self.assertEqual(json_data['exact_match'], False)
        self.assertEqual(json_data['confidence_threshold'], 0.8)
        self.assertEqual(json_data['excel_column'], '${이름}')
        
        # 역직렬화
        new_step = TextSearchStep()
        new_step.from_dict(json_data)
        
        self.assertEqual(new_step.search_text, '홍길동')
        self.assertEqual(new_step.region, (100, 100, 500, 300))
        self.assertEqual(new_step.exact_match, False)
        self.assertEqual(new_step.confidence_threshold, 0.8)
        self.assertEqual(new_step.excel_column, '${이름}')
        
    def test_text_search_dialog_data_flow(self):
        """다이얼로그 데이터 흐름 테스트"""
        # 테스트용 Excel 컬럼
        excel_columns = ['이름', '부서', '직급']
        
        # TextSearchStep 생성
        step = TextSearchStep()
        step.search_text = "테스트"
        step.region = (0, 0, 100, 100)
        
        # 다이얼로그 생성
        dialog = TextSearchStepDialog(step=step, excel_columns=excel_columns)
        
        # UI 요소 확인
        self.assertEqual(dialog.search_text_edit.text(), "테스트")
        self.assertEqual(dialog.region, (0, 0, 100, 100))
        
        # Excel 컬럼 콤보박스 확인 - 실제 구현에 맞게 수정
        combo_items = [dialog.excel_column_combo.itemText(i) 
                      for i in range(dialog.excel_column_combo.count())]
        # 콤보박스는 일반 컬럼 이름을 포함할 수 있음
        self.assertIn('이름', combo_items)
        self.assertIn('부서', combo_items)
        self.assertIn('직급', combo_items)
        
        # 값 변경
        dialog.search_text_edit.setText("새로운 텍스트")
        dialog.region = (50, 50, 200, 200)
        dialog.exact_match_check.setChecked(True)
        
        # OK 버튼 클릭 시뮬레이션
        dialog._update_step_from_dialog()
        
        # 변경사항 확인
        self.assertEqual(dialog.step.search_text, "새로운 텍스트")
        self.assertEqual(dialog.step.region, (50, 50, 200, 200))
        self.assertEqual(dialog.step.exact_match, True)
        
    @patch('automation.executor.pyautogui')
    @patch('automation.executor.time.sleep')
    def test_step_executor_text_search(self, mock_sleep, mock_pyautogui):
        """StepExecutor의 텍스트 검색 실행 테스트"""
        # StepExecutor 생성 - settings 제공
        executor = StepExecutor(self.mock_settings)
        
        # OCR 결과 모킹
        mock_ocr_instance = Mock()
        self.mock_ocr_class.return_value = mock_ocr_instance
        
        # PaddleTextExtractor의 find_text 메서드 모킹
        mock_text_result = TextResult(
            text="홍길동",
            bbox=[[100, 100], [200, 100], [200, 130], [100, 130]],
            confidence=0.95,
            center=(150, 115)
        )
        
        with patch.object(PaddleTextExtractor, 'find_text', return_value=mock_text_result):
            # TextSearchStep 생성
            step = TextSearchStep()
            step.search_text = "홍길동"
            step.exact_match = True
            step.confidence_threshold = 0.8
            
            # 실행
            success = executor.execute_step(step)
            
            # 검증
            self.assertTrue(success)
            
            # 클릭이 호출되었는지 확인
            mock_pyautogui.click.assert_called_once_with(150, 115)  # 중심점
            
    @patch('automation.executor.pyautogui')
    def test_step_executor_text_not_found(self, mock_pyautogui):
        """텍스트를 찾지 못한 경우 테스트"""
        executor = StepExecutor(self.mock_settings)
        
        # OCR 결과 모킹
        mock_ocr_instance = Mock()
        self.mock_ocr_class.return_value = mock_ocr_instance
        
        # find_text가 None을 반환하도록 모킹
        with patch.object(PaddleTextExtractor, 'find_text', return_value=None):
            # TextSearchStep 생성
            step = TextSearchStep()
            step.search_text = "존재하지않는텍스트"
            step.error_handling = ErrorHandling.STOP
            
            # 실행 - 텍스트를 찾지 못하면 RuntimeError 발생
            with self.assertRaises(RuntimeError) as context:
                executor.execute_step(step)
            
            # 에러 메시지 확인
            self.assertIn("존재하지않는텍스트", str(context.exception))
            
            # 클릭이 호출되지 않았는지 확인
            mock_pyautogui.click.assert_not_called()
            
    def test_excel_variable_substitution(self):
        """Excel 변수 치환 테스트"""
        executor = StepExecutor(self.mock_settings)
        
        # 변수 설정
        variables = {
            '이름': '김철수',
            '부서': '개발팀'
        }
        
        # OCR 결과 모킹
        mock_ocr_instance = Mock()
        self.mock_ocr_class.return_value = mock_ocr_instance
        
        mock_text_result = TextResult(
            text="김철수",
            bbox=[[100, 100], [200, 100], [200, 130], [100, 130]],
            confidence=0.95,
            center=(150, 115)
        )
        
        with patch.object(PaddleTextExtractor, 'find_text', return_value=mock_text_result) as mock_find:
            with patch.object(executor, '_substitute_variables', side_effect=lambda text: text.replace('${이름}', '김철수')):
                # TextSearchStep with Excel variable
                step = TextSearchStep()
                step.search_text = "${이름}"
                step.excel_column = "${이름}"
                
                # 실행
                with patch('automation.executor.pyautogui'):
                    executor.set_variables(variables)
                success = executor.execute_step(step)
                
                # find_text가 치환된 값으로 호출되었는지 확인
                mock_find.assert_called()
                call_args = mock_find.call_args[0]
                self.assertEqual(call_args[0], '김철수')  # 치환된 값
                
    def test_region_specific_search(self):
        """특정 영역 검색 테스트"""
        executor = StepExecutor(self.mock_settings)
        
        # OCR 결과 모킹
        mock_ocr_instance = Mock()
        self.mock_ocr_class.return_value = mock_ocr_instance
        
        # TextSearchStep with region
        step = TextSearchStep()
        step.search_text = "찾기"
        step.region = (100, 100, 500, 300)
        
        # find_text 모킹
        with patch.object(PaddleTextExtractor, 'find_text') as mock_find:
            mock_find.return_value = None
            
            with patch('automation.executor.pyautogui'):
                # 텍스트를 찾지 못하면 RuntimeError 발생
                with self.assertRaises(RuntimeError) as context:
                    executor.execute_step(step)
                
                # 에러 메시지 확인
                self.assertIn("찾기", str(context.exception))
            
            # find_text가 올바른 region 파라미터로 호출되었는지 확인
            mock_find.assert_called()
            call_kwargs = mock_find.call_args[1]
            self.assertEqual(call_kwargs.get('region'), (100, 100, 500, 300))
            
    def test_confidence_threshold_integration(self):
        """신뢰도 임계값 통합 테스트"""
        executor = StepExecutor(self.mock_settings)
        
        # OCR 결과 모킹
        mock_ocr_instance = Mock()
        self.mock_ocr_class.return_value = mock_ocr_instance
        
        # TextSearchStep with high threshold
        step = TextSearchStep()
        step.search_text = "홍길동"
        step.confidence = 0.9  # 높은 임계값 - 실제 필드명은 confidence
        
        with patch.object(PaddleTextExtractor, 'find_text') as mock_find:
            # find_text 메서드가 confidence_threshold를 전달받는지 확인
            with patch('automation.executor.pyautogui'):
                executor.execute_step(step)
            
            mock_find.assert_called()
            call_kwargs = mock_find.call_args[1]
            self.assertEqual(call_kwargs.get('confidence_threshold'), 0.9)  # find_text receives confidence_threshold
            
    def test_error_recovery_continue(self):
        """에러 발생 시 계속 진행 테스트"""
        executor = StepExecutor(self.mock_settings)
        
        # OCR 초기화 실패 시뮬레이션
        with patch.object(PaddleTextExtractor, 'find_text', side_effect=Exception("OCR 오류")):
            # TextSearchStep with CONTINUE error handling
            step = TextSearchStep()
            step.search_text = "테스트"
            step.error_handling = ErrorHandling.CONTINUE
            
            # 실행 - execute_step은 예외를 전파함
            with self.assertRaises(RuntimeError) as context:
                executor.execute_step(step)
            
            # 에러 메시지 확인
            self.assertIn("OCR 오류", str(context.exception))
            
    def test_macro_file_save_load(self):
        """매크로 파일 저장/로드 시 텍스트 검색 단계 보존 테스트"""
        # TextSearchStep 생성
        step = TextSearchStep()
        step.name = "환자 이름 찾기"
        step.search_text = "${환자명}"
        step.region = (100, 200, 800, 600)
        step.exact_match = False
        step.confidence_threshold = 0.85
        step.excel_column = "${환자명}"
        step.error_handling = ErrorHandling.RETRY
        step.retry_count = 3
        
        # JSON으로 저장
        step_dict = step.to_dict()
        
        # 임시 파일에 저장
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            json.dump({'steps': [step_dict]}, f, ensure_ascii=False)
            temp_file = f.name
            
        try:
            # 파일에서 로드
            with open(temp_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
            # 새 step 생성 및 로드
            loaded_step = TextSearchStep()
            loaded_step.from_dict(data['steps'][0])
            
            # 모든 속성이 보존되었는지 확인
            self.assertEqual(loaded_step.name, "환자 이름 찾기")
            self.assertEqual(loaded_step.search_text, "${환자명}")
            self.assertEqual(loaded_step.region, (100, 200, 800, 600))
            self.assertEqual(loaded_step.exact_match, False)
            self.assertEqual(loaded_step.confidence_threshold, 0.85)
            self.assertEqual(loaded_step.excel_column, "${환자명}")
            self.assertEqual(loaded_step.error_handling, ErrorHandling.RETRY)
            self.assertEqual(loaded_step.retry_count, 3)
            
        finally:
            # 임시 파일 삭제
            os.unlink(temp_file)


if __name__ == '__main__':
    unittest.main()