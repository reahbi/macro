"""
PaddleOCR 기반 텍스트 추출기
EasyOCR를 대체하는 새로운 OCR 엔진 구현
"""

from typing import Optional, List, Tuple, Dict, Any
from dataclasses import dataclass
import mss
from PIL import Image
from logger.app_logger import get_logger
import time
from functools import wraps

# PaddleOCR 임포트 시도
try:
    from paddleocr import PaddleOCR
    PADDLEOCR_AVAILABLE = True
except ImportError:
    PADDLEOCR_AVAILABLE = False
    PaddleOCR = None

def measure_performance(func):
    """성능 측정 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        
        # 성능 로깅
        logger = get_logger(__name__)
        logger.info(f"{func.__name__} 실행 시간: {elapsed_time:.3f}초")
        
        # 느린 작업 경고
        if elapsed_time > 2.0:
            logger.warning(f"{func.__name__}이 {elapsed_time:.3f}초 걸렸습니다. 최적화가 필요할 수 있습니다.")
        
        return result
    return wrapper

@dataclass
class TextResult:
    """텍스트 검출 결과"""
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    center: Tuple[int, int]  # (center_x, center_y)

class PaddleTextExtractor:
    """PaddleOCR 기반 텍스트 추출기"""
    
    _instance = None
    _ocr = None
    
    def __new__(cls):
        """싱글톤 패턴"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """텍스트 추출기 초기화"""
        if not hasattr(self, 'initialized'):
            self.logger = get_logger(__name__)
            self.initialized = True
            
            # 이미지 전처리 옵션 (필요시 활성화)
            self.enable_preprocessing = False
            
            # OCR 상태 확인
            from utils.ocr_manager import OCRManager
            self.ocr_manager = OCRManager()
            
            if not PADDLEOCR_AVAILABLE:
                self.logger.warning("PaddleOCR이 설치되지 않았습니다. 텍스트 검색 기능이 제한됩니다.")
            
    def _get_ocr(self) -> Optional['PaddleOCR']:
        """PaddleOCR 인스턴스 생성 (지연 로딩)"""
        if not PADDLEOCR_AVAILABLE:
            error_msg = (
                "텍스트 추출을 사용할 수 없습니다. PaddleOCR이 설치되지 않았습니다.\n"
                "설치 명령: pip install paddlepaddle paddleocr"
            )
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
            
        if PaddleTextExtractor._ocr is None:
            try:
                self.logger.info("PaddleOCR 초기화 중...")
                
                # GPU 사용 가능 여부 확인
                use_gpu = False
                try:
                    import paddle
                    use_gpu = paddle.is_compiled_with_cuda() and paddle.device.cuda.device_count() > 0
                    if use_gpu:
                        self.logger.info("GPU 감지됨! GPU 가속을 사용합니다.")
                    else:
                        self.logger.info("GPU를 사용할 수 없습니다. CPU를 사용합니다.")
                except:
                    self.logger.info("GPU 감지 실패. CPU를 사용합니다.")
                
                # CPU 코어 수에 따른 동적 스레드 할당
                import multiprocessing
                cpu_count = multiprocessing.cpu_count()
                optimal_threads = max(1, min(cpu_count - 1, 8))  # 1~8 사이, CPU-1
                
                # PaddleOCR 초기화 - 한국어 텍스트 인식
                # PaddleOCR 2.7.0에서는 lang='korean' 지정 시 자동으로 적절한 모델 사용
                PaddleTextExtractor._ocr = PaddleOCR(
                    lang='korean',              # 한국어 모델 (영어, 숫자 포함)
                    use_angle_cls=True         # 텍스트 각도 분류 활성화
                )
                self.logger.info("PaddleOCR 초기화 완료")
                
            except Exception as e:
                self.logger.error(f"PaddleOCR 초기화 실패: {e}")
                error_msg = (
                    f"PaddleOCR 초기화에 실패했습니다.\n"
                    f"가능한 원인:\n"
                    f"1. PaddleOCR이 제대로 설치되지 않았습니다.\n"
                    f"   해결: pip install --upgrade paddleocr paddlepaddle\n"
                    f"2. Python 버전이 맞지 않습니다. (Python 3.8 ~ 3.11 필요)\n"
                    f"3. Visual C++ 재배포 가능 패키지가 필요할 수 있습니다.\n"
                    f"오류: {e}"
                )
                raise RuntimeError(error_msg)
                
        return PaddleTextExtractor._ocr
    
    def preprocess_image_for_ocr(self, img_array):
        """OCR 전 이미지 전처리"""
        try:
            # OpenCV가 없으면 원본 이미지 반환
            try:
                import cv2
            except ImportError:
                self.logger.debug("OpenCV가 설치되지 않았습니다. 이미지 전처리를 건너뜁니다.")
                return img_array
            
            # 그레이스케일 변환
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # 노이즈 제거 (빠른 버전 사용)
            denoised = cv2.medianBlur(gray, 3)
            
            # 대비 향상
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(denoised)
            
            # 이진화 (Otsu's method)
            _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # 다시 RGB로 변환 (PaddleOCR 입력 형식)
            result = cv2.cvtColor(binary, cv2.COLOR_GRAY2RGB)
            
            return result
            
        except Exception as e:
            self.logger.error(f"이미지 전처리 오류: {e}")
            return img_array
    
    def set_preprocessing(self, enable: bool):
        """이미지 전처리 활성화/비활성화"""
        self.enable_preprocessing = enable
        self.logger.info(f"이미지 전처리: {'활성화' if enable else '비활성화'}")
    
    @measure_performance
    def extract_text_from_region(self, region: Optional[Tuple[int, int, int, int]] = None,
                                confidence_threshold: float = 0.5) -> List[TextResult]:
        """
        화면 영역에서 텍스트 추출 (EasyOCR 인터페이스 호환)
        
        Args:
            region: (x, y, width, height) 또는 None (전체 화면)
            confidence_threshold: 최소 신뢰도
            
        Returns:
            TextResult 객체 리스트
        """
        try:
            # 스크린샷 캡처
            monitor_offset_x = 0
            monitor_offset_y = 0
            
            with mss.mss() as sct:
                if region:
                    x, y, width, height = region
                    monitor = {"left": x, "top": y, "width": width, "height": height}
                else:
                    monitor = sct.monitors[0]  # 모든 모니터
                    monitor_offset_x = monitor["left"]
                    monitor_offset_y = monitor["top"]
                    
                # 스크린샷 캡처
                screenshot = sct.grab(monitor)
            
            # PIL Image로 변환
            img_pil = Image.frombytes('RGB', (screenshot.width, screenshot.height), 
                                    screenshot.bgra, 'raw', 'BGRX')
            
            # numpy 배열로 변환 (PaddleOCR 입력)
            import numpy as np
            img_array = np.array(img_pil)
            
            # 이미지 전처리 적용 (선택적)
            if self.enable_preprocessing:
                self.logger.debug("이미지 전처리 적용 중...")
                img_array = self.preprocess_image_for_ocr(img_array)
            
            # PaddleOCR 실행
            ocr = self._get_ocr()
            self.logger.debug(f"Performing OCR on image shape: {img_array.shape}")
            results = ocr.ocr(img_array)
            
            # 결과 디버깅
            self.logger.debug(f"OCR raw results: {results}")
            
            # 결과 변환
            text_results = []
            
            # PP-OCRv5는 결과를 다른 형식으로 반환할 수 있음
            if results is None:
                self.logger.warning("OCR returned None results")
                return text_results
            
            # 결과가 딕셔너리인 경우 처리 (PP-OCRv5 가능성)
            if isinstance(results, dict):
                self.logger.debug(f"OCR returned dictionary with keys: {list(results.keys())}")
                # 일반적인 키들 확인
                if 'result' in results:
                    results = results['result']
                elif 'data' in results:
                    results = results['data']
                elif len(results) > 0:
                    # 첫 번째 값 사용
                    first_key = list(results.keys())[0]
                    results = results[first_key]
            
            # 결과가 리스트가 아닌 경우
            if not isinstance(results, list):
                self.logger.error(f"Unexpected results type: {type(results)}")
                # 단일 결과를 리스트로 변환
                results = [results] if results else []
            
            # 각 페이지/결과 처리
            for idx, page_result in enumerate(results):
                if page_result is None:
                    continue
                
                # page_result가 리스트가 아닌 경우 처리
                if not isinstance(page_result, list):
                    self.logger.debug(f"Page {idx} result is not a list: {type(page_result)}")
                    # 딕셔너리인 경우
                    if isinstance(page_result, dict):
                        # 텍스트 결과가 포함된 키 찾기
                        if 'texts' in page_result:
                            page_result = page_result['texts']
                        elif 'lines' in page_result:
                            page_result = page_result['lines']
                        else:
                            page_result = [page_result]
                    else:
                        page_result = [page_result]
                
                # 각 라인 처리
                for line_idx, line in enumerate(page_result):
                    try:
                        # line이 None인 경우
                        if line is None:
                            continue
                        
                        # 변수 초기화
                        bbox_points = None
                        text = ""
                        confidence = 0.0
                        
                        # line의 실제 형식 로깅
                        self.logger.debug(f"Line {line_idx} type: {type(line)}, content: {line}")
                        
                        # 딕셔너리 형식 (PP-OCRv5 가능성)
                        if isinstance(line, dict):
                            # 가능한 키 확인
                            self.logger.debug(f"Line {line_idx} dict keys: {list(line.keys())}")
                            
                            # PP-OCRv5 새로운 형식 처리
                            if 'rec_texts' in line and 'rec_polys' in line:
                                # PP-OCRv5 형식: 여러 텍스트가 한 번에 들어옴
                                texts = line.get('rec_texts', [])
                                scores = line.get('rec_scores', [])
                                polys = line.get('rec_polys', line.get('rec_boxes', []))
                                
                                self.logger.debug(f"PP-OCRv5 format detected: {len(texts)} texts found")
                                
                                # 각 텍스트에 대해 처리
                                for text_idx, text in enumerate(texts):
                                    if text_idx < len(scores) and text_idx < len(polys):
                                        confidence = scores[text_idx]
                                        bbox_array = polys[text_idx]
                                        
                                        # numpy array를 리스트로 변환
                                        if hasattr(bbox_array, 'tolist'):
                                            bbox_points = bbox_array.tolist()
                                        else:
                                            bbox_points = bbox_array
                                        
                                        # 좌표 처리
                                        if confidence >= confidence_threshold and text.strip():
                                            try:
                                                # 4개 점 또는 4개 좌표
                                                if len(bbox_points) == 4 and isinstance(bbox_points[0], (list, tuple)):
                                                    # [[x1,y1], [x2,y2], [x3,y3], [x4,y4]] 형식
                                                    x_coords = [p[0] for p in bbox_points]
                                                    y_coords = [p[1] for p in bbox_points]
                                                elif len(bbox_points) == 4:
                                                    # [x, y, width, height] 형식
                                                    x, y, w, h = bbox_points
                                                    x_coords = [x, x+w, x+w, x]
                                                    y_coords = [y, y, y+h, y+h]
                                                else:
                                                    self.logger.warning(f"Unexpected bbox format: {bbox_points}")
                                                    continue
                                                
                                                min_x = int(min(x_coords))
                                                min_y = int(min(y_coords))
                                                max_x = int(max(x_coords))
                                                max_y = int(max(y_coords))
                                                
                                                width = max_x - min_x
                                                height = max_y - min_y
                                                
                                                # 중심점 계산
                                                center_x = min_x + width // 2
                                                center_y = min_y + height // 2
                                                
                                                # 영역이 지정된 경우 좌표 조정
                                                if region:
                                                    min_x += region[0]
                                                    min_y += region[1]
                                                    center_x += region[0]
                                                    center_y += region[1]
                                                else:
                                                    # 전체 화면인 경우 모니터 오프셋 적용
                                                    min_x += monitor_offset_x
                                                    min_y += monitor_offset_y
                                                    center_x += monitor_offset_x
                                                    center_y += monitor_offset_y
                                                
                                                result = TextResult(
                                                    text=text,
                                                    confidence=confidence,
                                                    bbox=(min_x, min_y, width, height),
                                                    center=(center_x, center_y)
                                                )
                                                text_results.append(result)
                                                
                                            except Exception as e:
                                                self.logger.error(f"Error processing PP-OCRv5 text {text_idx}: {e}")
                                
                                # PP-OCRv5 형식은 이미 처리했으므로 다음 라인으로
                                continue
                            
                            # 기존 딕셔너리 형식 처리
                            else:
                                bbox_points = line.get('points', line.get('bbox', line.get('box', [])))
                                text = line.get('text', line.get('transcription', ''))
                                confidence = line.get('confidence', line.get('score', line.get('prob', 1.0)))
                                
                                # bbox_points가 평면 리스트인 경우 변환
                                if isinstance(bbox_points, list) and len(bbox_points) == 8:
                                    # [x1,y1,x2,y2,x3,y3,x4,y4] -> [[x1,y1],[x2,y2],[x3,y3],[x4,y4]]
                                    bbox_points = [[bbox_points[i], bbox_points[i+1]] for i in range(0, 8, 2)]
                        
                        # 기존 리스트/튜플 형식
                        elif isinstance(line, (list, tuple)) and len(line) >= 2:
                            bbox_points = line[0]
                            self.logger.debug(f"Line {line_idx} bbox_points type: {type(bbox_points)}, content: {bbox_points}")
                            
                            # 텍스트와 신뢰도 추출
                            if isinstance(line[1], (list, tuple)) and len(line[1]) >= 2:
                                text = str(line[1][0])
                                confidence = float(line[1][1])
                            elif isinstance(line[1], str):
                                text = line[1]
                                confidence = 1.0
                            elif isinstance(line[1], dict):
                                text = line[1].get('text', '')
                                confidence = line[1].get('confidence', 1.0)
                            else:
                                self.logger.warning(f"Unexpected text format in line {line_idx}: {type(line[1])}")
                                continue
                        else:
                            self.logger.warning(f"Unexpected line format at index {line_idx}: {type(line)}")
                            continue
                        
                        # bbox_points 유효성 검사
                        if not bbox_points or not isinstance(bbox_points, (list, tuple)):
                            self.logger.warning(f"Invalid bbox_points for line {line_idx}: {bbox_points}")
                            self.logger.warning(f"Full line content: {line}")
                            continue
                            
                        # 빈 텍스트 건너뛰기
                        if not text or not text.strip():
                            continue
                            
                    except Exception as e:
                        self.logger.error(f"Error parsing line {line_idx}: {e}, line content: {line}")
                        continue
                    
                    if confidence >= confidence_threshold:
                        # bbox 좌표 계산
                        try:
                            # bbox_points가 리스트의 리스트인지 확인
                            if isinstance(bbox_points[0], (list, tuple)):
                                x_coords = [p[0] for p in bbox_points]
                                y_coords = [p[1] for p in bbox_points]
                            else:
                                # 평면 리스트인 경우 [x1,y1,x2,y2,...]
                                x_coords = [bbox_points[i] for i in range(0, len(bbox_points), 2)]
                                y_coords = [bbox_points[i+1] for i in range(0, len(bbox_points), 2)]
                            
                            if not x_coords or not y_coords:
                                self.logger.warning(f"Empty coordinates for text: {text}")
                                continue
                                
                            min_x = int(min(x_coords))
                            min_y = int(min(y_coords))
                            max_x = int(max(x_coords))
                            max_y = int(max(y_coords))
                        except (ValueError, IndexError) as e:
                            self.logger.error(f"Error calculating bbox: {e}, bbox_points: {bbox_points}")
                            continue
                        
                        width = max_x - min_x
                        height = max_y - min_y
                        
                        # 중심점 계산
                        center_x = min_x + width // 2
                        center_y = min_y + height // 2
                        
                        # 영역이 지정된 경우 좌표 조정
                        if region:
                            min_x += region[0]
                            min_y += region[1]
                            center_x += region[0]
                            center_y += region[1]
                        else:
                            # 전체 화면인 경우 모니터 오프셋 적용
                            min_x += monitor_offset_x
                            min_y += monitor_offset_y
                            center_x += monitor_offset_x
                            center_y += monitor_offset_y
                        
                        result = TextResult(
                            text=text,
                            confidence=confidence,
                            bbox=(min_x, min_y, width, height),
                            center=(center_x, center_y)
                        )
                        text_results.append(result)
                        
            self.logger.info(f"추출된 텍스트 항목: {len(text_results)}개")
            
            # 디버그 로깅
            if len(text_results) > 0:
                self.logger.debug("추출된 텍스트 목록:")
                for i, result in enumerate(text_results):
                    self.logger.debug(f"  [{i}] '{result.text}' (신뢰도: {result.confidence:.2f})")
                    
            return text_results
            
        except Exception as e:
            self.logger.error(f"텍스트 추출 오류: {e}")
            import traceback
            self.logger.error(f"상세 오류: {traceback.format_exc()}")
            return []
    
    @measure_performance
    def find_text(self, target_text: str, region: Optional[Tuple[int, int, int, int]] = None,
                  exact_match: bool = False, confidence_threshold: float = 0.5,
                  confidence: float = None, max_retries: int = 1) -> Optional[TextResult]:
        """
        특정 텍스트 찾기 (EasyOCR 인터페이스 호환)
        
        Args:
            target_text: 찾을 텍스트
            region: (x, y, width, height) 또는 None (전체 화면)
            exact_match: 정확히 일치 여부
            confidence_threshold: 최소 OCR 신뢰도
            confidence: 하위 호환성을 위한 매개변수
            max_retries: 최대 재시도 횟수
            
        Returns:
            TextResult 또는 None
        """
        # 하위 호환성 - confidence 매개변수 처리
        if confidence is not None:
            confidence_threshold = confidence
            
        try:
            # 영역 유효성 검사
            if region is not None:
                if not isinstance(region, (tuple, list)) or len(region) != 4:
                    self.logger.error(f"잘못된 영역 형식: {region}")
                    return None
                    
                # 모든 값이 정수인지 확인
                try:
                    region = tuple(int(x) for x in region)
                except (ValueError, TypeError) as e:
                    self.logger.error(f"잘못된 영역 값: {region}, 오류: {e}")
                    return None
                    
                # 영역 크기 검증
                x, y, width, height = region
                if width <= 0 or height <= 0:
                    self.logger.error(f"잘못된 영역 크기: width={width}, height={height}")
                    return None
                    
            # 모든 텍스트 추출
            text_results = self.extract_text_from_region(region, confidence_threshold)
            
            # 대상 텍스트 정규화
            target_lower = target_text.lower().strip()
            
            # 특수 문자 정규화 (전각 -> 반각)
            def normalize_special_chars(text):
                """특수 문자 정규화"""
                replacements = {
                    '：': ':', '；': ';', '（': '(', '）': ')',
                    '［': '[', '］': ']', '｛': '{', '｝': '}',
                    '＜': '<', '＞': '>', '，': ',', '。': '.',
                    '！': '!', '？': '?', '　': ' '
                }
                for full, half in replacements.items():
                    text = text.replace(full, half)
                return text
            
            # 대상 텍스트 정규화
            target_normalized = normalize_special_chars(target_lower)
            
            # 매칭 로직
            best_match = None
            best_score = 0.0
            
            for result in text_results:
                text_lower = result.text.lower().strip()
                text_normalized = normalize_special_chars(text_lower)
                
                if exact_match:
                    # 정확한 매칭 - 정규화된 텍스트로 비교
                    if text_normalized == target_normalized:
                        return result
                else:
                    # 부분 매칭 - 대상이 검출된 텍스트에 포함
                    if target_normalized in text_normalized:
                        # 매칭 점수 계산
                        score = len(target_normalized) / len(text_normalized)
                        if score > best_score:
                            best_match = result
                            best_score = score
                    # 검출된 텍스트가 대상에 포함 (부분 OCR 결과)
                    elif text_normalized in target_normalized and len(text_normalized) > 2:
                        score = len(text_normalized) / len(target_normalized)
                        if score > best_score:
                            best_match = result
                            best_score = score
                    # 공백 제거 후 비교 (띄어쓰기 차이 허용)
                    elif target_normalized.replace(' ', '') in text_normalized.replace(' ', ''):
                        score = len(target_normalized) / len(text_normalized) * 0.9  # 약간 낮은 점수
                        if score > best_score:
                            best_match = result
                            best_score = score
            
            if best_match:
                self.logger.info(f"텍스트 '{target_text}' 찾음: {best_match.center}")
            else:
                self.logger.info(f"텍스트 '{target_text}'를 찾을 수 없음")
                
            return best_match
            
        except Exception as e:
            self.logger.error(f"텍스트 검색 오류: {e}")
            return None
    
    def find_all_text(self, target_text: str, region: Optional[Tuple[int, int, int, int]] = None,
                      exact_match: bool = False, confidence_threshold: float = 0.5) -> List[TextResult]:
        """
        모든 일치하는 텍스트 찾기 (EasyOCR 인터페이스 호환)
        
        Args:
            target_text: 찾을 텍스트
            region: (x, y, width, height) 또는 None (전체 화면)
            exact_match: 정확히 일치 여부
            confidence_threshold: 최소 OCR 신뢰도
            
        Returns:
            TextResult 객체 리스트
        """
        try:
            # 모든 텍스트 추출
            text_results = self.extract_text_from_region(region, confidence_threshold)
            
            # 대상 텍스트 정규화
            target_lower = target_text.lower().strip()
            
            # 모든 매칭 찾기
            matches = []
            
            for result in text_results:
                text_lower = result.text.lower().strip()
                
                if exact_match:
                    if text_lower == target_lower:
                        matches.append(result)
                else:
                    # 부분 매칭
                    if target_lower in text_lower or text_lower in target_lower:
                        matches.append(result)
            
            self.logger.info(f"'{target_text}'의 {len(matches)}개 항목 찾음")
            return matches
            
        except Exception as e:
            self.logger.error(f"모든 텍스트 찾기 오류: {e}")
            return []
    
    def preload_models(self):
        """OCR 모델 사전 로드"""
        try:
            self.logger.info("PaddleOCR 모델 사전 로드 중...")
            ocr = self._get_ocr()
            
            # 더미 이미지로 인식 수행
            import numpy as np
            dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
            dummy_img.fill(255)  # 흰색 배경
            
            ocr.ocr(dummy_img)
            self.logger.info("PaddleOCR 모델 사전 로드 완료")
            
        except Exception as e:
            self.logger.error(f"모델 사전 로드 오류: {e}")

# 전역 인스턴스 생성
paddle_text_extractor = PaddleTextExtractor()