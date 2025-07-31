# 📋 Excel 매크로 자동화 도구 - 종합 오류 해결 가이드

## 🔍 현재 로직 분석 결과

### 1. **Excel 파일 처리 로직 문제점**

#### 현재 구현:
- `ExcelManager.load_file()`: 파일 로드 시 첫 번째 시트만 자동으로 df에 로드
- `read_sheet()`: 시트 데이터 읽기 시 status 컬럼 자동 검색/생성
- 인코딩 처리가 명시적이지 않음

#### 주요 문제:
1. **한글 인코딩 문제**: pandas의 기본 엔진이 한글을 제대로 처리하지 못함
2. **열 이름 공백 문제**: 엑셀 열 이름의 앞뒤 공백이 정규화되지 않음
3. **변수 매핑 오류**: `${columnName}` 형식 변환 시 열 이름 불일치

### 2. **멀티 모니터 좌표 시스템 문제점**

#### 현재 구현:
- `monitor_utils.py`: screeninfo 라이브러리 우선, tkinter 폴백
- `ROISelectorOverlay`: mss 라이브러리로 절대 좌표 사용
- 음수 좌표 지원 (왼쪽/위쪽 모니터)

#### 주요 문제:
1. **좌표계 불일치**: Qt (PyQt5) vs mss 좌표계 차이
2. **DPI 스케일링**: Windows DPI 설정이 적용되지 않음
3. **모니터 경계 검증**: 영역이 모니터 범위를 벗어나는 경우 처리 미흡

### 3. **이미지 검색 오류**

#### 현재 구현:
- OpenCV 기반 템플릿 매칭
- 다중 스케일 검색 지원
- pyautogui 폴백

#### 주요 문제:
1. **경로 처리**: 상대 경로/절대 경로 변환 로직 불완전
2. **캐시 메모리 누수**: 템플릿 캐시가 계속 증가
3. **신뢰도 설정**: 고정된 신뢰도로 인한 매칭 실패

### 4. **텍스트 검색 (OCR) 오류**

#### 현재 구현:
- PaddleOCR 한국어 모델 사용
- 동적 텍스트 지원 (Excel 변수)
- 디버그 스크린샷 저장

#### 주요 문제:
1. **초기화 실패**: PaddleOCR 의존성 문제
2. **영역 좌표 변환**: 절대 좌표 vs 상대 좌표 혼용
3. **변수 치환 타이밍**: Excel 데이터 로드 전 변수 참조

---

## 🛠️ 구체적인 수정 방안

### 1. Excel 파일 처리 개선

```python
# src/excel/excel_manager.py 수정

def load_file(self, file_path: str) -> ExcelFileInfo:
    """Excel 파일 로드 with 인코딩 처리"""
    file_path = Path(file_path)
    
    # ... 기존 검증 코드 ...
    
    # 인코딩 감지 및 처리 추가
    try:
        # 먼저 UTF-8로 시도
        self.df = pd.read_excel(file_path, sheet_name=sheet_names[0], engine='openpyxl')
    except UnicodeDecodeError:
        # CP949 (한글 Windows) 인코딩으로 재시도
        import chardet
        with open(file_path, 'rb') as f:
            detected = chardet.detect(f.read())
        encoding = detected['encoding'] or 'cp949'
        self.df = pd.read_excel(file_path, sheet_name=sheet_names[0], 
                               engine='openpyxl', encoding=encoding)
    
    # 열 이름 정규화 추가
    if self.df is not None:
        self.df.columns = self.df.columns.str.strip()  # 앞뒤 공백 제거
        self.df.columns = self.df.columns.str.replace(r'\s+', ' ', regex=True)  # 중복 공백 제거
    
    # ... 나머지 코드 ...

def _prepare_search_text(self, step):
    """검색 텍스트 준비 with 개선된 변수 치환"""
    search_text = getattr(step, 'search_text', '')
    
    # 변수 참조 확인 (${columnName} 형식)
    import re
    variable_pattern = r'\$\{([^}]+)\}'
    matches = re.findall(variable_pattern, search_text)
    
    if matches and self.excel_manager and self.excel_manager.has_data():
        try:
            # 현재 행 데이터 가져오기
            current_row = self.current_excel_row
            if current_row is not None:
                row_data = self.excel_manager.get_row_data(current_row)
                
                # 각 변수 치환
                for var_name in matches:
                    # 열 이름 정규화 (공백 처리)
                    normalized_var = var_name.strip()
                    
                    # 여러 변형 시도
                    value = None
                    for col in row_data.keys():
                        if col.strip() == normalized_var:
                            value = row_data[col]
                            break
                    
                    if value is not None:
                        search_text = search_text.replace(f'${{{var_name}}}', str(value))
                    else:
                        self.logger.warning(f"Column '{var_name}' not found. Available: {list(row_data.keys())}")
        except Exception as e:
            self.logger.error(f"Variable substitution error: {e}")
    
    return search_text
```

### 2. 좌표 시스템 통합

```python
# src/utils/coordinate_utils.py (새 파일)

from typing import Tuple, Optional, Dict
import mss
from PyQt5.QtWidgets import QApplication

class CoordinateSystem:
    """통합 좌표 시스템 관리"""
    
    def __init__(self):
        self.sct = mss.mss()
        self._dpi_scale = None
        
    def get_dpi_scale(self) -> float:
        """DPI 스케일 가져오기"""
        if self._dpi_scale is None:
            app = QApplication.instance()
            if app:
                screen = app.primaryScreen()
                self._dpi_scale = screen.devicePixelRatio()
            else:
                self._dpi_scale = 1.0
        return self._dpi_scale
    
    def qt_to_absolute(self, x: int, y: int, monitor_info: Optional[Dict] = None) -> Tuple[int, int]:
        """Qt 좌표를 절대 좌표로 변환"""
        scale = self.get_dpi_scale()
        
        # DPI 스케일 적용
        abs_x = int(x * scale)
        abs_y = int(y * scale)
        
        return abs_x, abs_y
    
    def absolute_to_qt(self, x: int, y: int) -> Tuple[int, int]:
        """절대 좌표를 Qt 좌표로 변환"""
        scale = self.get_dpi_scale()
        
        qt_x = int(x / scale)
        qt_y = int(y / scale)
        
        return qt_x, qt_y
    
    def validate_region(self, region: Tuple[int, int, int, int], 
                      monitor_bounds: Optional[Dict] = None) -> bool:
        """영역 유효성 검사"""
        x, y, width, height = region
        
        # 기본 검증
        if width <= 0 or height <= 0:
            return False
        
        # 모니터 경계 검증
        if monitor_bounds:
            mon_x = monitor_bounds.get('x', 0)
            mon_y = monitor_bounds.get('y', 0)
            mon_w = monitor_bounds.get('width', 1920)
            mon_h = monitor_bounds.get('height', 1080)
            
            # 영역이 모니터 내에 있는지 확인
            if x < mon_x or y < mon_y:
                return False
            if x + width > mon_x + mon_w:
                return False
            if y + height > mon_y + mon_h:
                return False
        
        return True

# ROISelectorOverlay 수정
def _on_region_selected(self, result):
    """개선된 영역 선택 처리"""
    # ... 기존 코드 ...
    
    # 좌표 시스템 통합
    coord_system = CoordinateSystem()
    
    # 영역 유효성 검사
    if not coord_system.validate_region(region, self.monitor_info):
        self.logger.warning(f"Invalid region selected: {region}")
        self.region = None
        return
    
    # DPI 스케일 보정
    if self.monitor_info and 'dpi_scale' in self.monitor_info:
        scale = self.monitor_info['dpi_scale']
        region = tuple(int(v * scale) for v in region)
```

### 3. 이미지 검색 개선

```python
# src/vision/image_matcher.py 수정

class ImageMatcher:
    def __init__(self, settings: Settings):
        # ... 기존 코드 ...
        self._max_cache_size_mb = 100  # 캐시 크기 제한
        self._cache_size = 0
        
    def _load_template(self, image_path: str, scale: float = 1.0) -> np.ndarray:
        """개선된 템플릿 로딩"""
        # 경로 정규화
        image_path = self._normalize_path(image_path)
        
        # 캐시 크기 확인
        if self._cache_size > self._max_cache_size_mb * 1024 * 1024:
            self.clear_cache()
        
        # ... 기존 캐싱 로직 ...
        
    def _normalize_path(self, image_path: str) -> str:
        """이미지 경로 정규화"""
        from pathlib import Path
        
        path = Path(image_path)
        
        # 절대 경로로 변환
        if not path.is_absolute():
            # 리소스 디렉토리 확인
            resource_paths = [
                Path("resources/images") / path.name,
                Path("captures") / path.name,
                Path(".") / path,
            ]
            
            for rpath in resource_paths:
                if rpath.exists():
                    return str(rpath.absolute())
        
        return str(path.absolute())
    
    def find_image_adaptive(self, template_path: str, 
                           initial_confidence: float = 0.9,
                           min_confidence: float = 0.6,
                           **kwargs) -> MatchResult:
        """적응형 신뢰도 검색"""
        confidence = initial_confidence
        step = 0.05
        
        while confidence >= min_confidence:
            result = self.find_image(template_path, confidence=confidence, **kwargs)
            if result.found:
                self.logger.info(f"Image found at confidence: {confidence}")
                return result
            confidence -= step
        
        return MatchResult(found=False, confidence=0.0)
```

### 4. OCR 초기화 및 오류 처리 개선

```python
# src/vision/text_extractor_paddle.py 수정

class PaddleTextExtractor:
    def _get_ocr(self) -> Optional['PaddleOCR']:
        """개선된 OCR 초기화"""
        if PaddleTextExtractor._ocr is None:
            retry_count = 0
            max_retries = 3
            
            while retry_count < max_retries:
                try:
                    self.logger.info(f"PaddleOCR 초기화 시도 {retry_count + 1}/{max_retries}")
                    
                    # GPU 사용 시도
                    use_gpu = self._check_gpu_availability()
                    
                    # 초기화 옵션
                    init_params = {
                        'lang': 'korean',
                        'use_angle_cls': True,
                        'use_gpu': use_gpu,
                        'show_log': False,  # 로그 감소
                        'use_mp': True,     # 멀티프로세싱
                        'total_process_num': 2,  # 프로세스 수 제한
                    }
                    
                    # CPU 최적화 (GPU 사용 불가 시)
                    if not use_gpu:
                        init_params.update({
                            'enable_mkldnn': True,
                            'cpu_threads': min(4, multiprocessing.cpu_count())
                        })
                    
                    PaddleTextExtractor._ocr = PaddleOCR(**init_params)
                    self.logger.info("PaddleOCR 초기화 성공")
                    break
                    
                except Exception as e:
                    retry_count += 1
                    self.logger.error(f"초기화 실패 (시도 {retry_count}): {e}")
                    
                    if retry_count < max_retries:
                        time.sleep(2)
                        # 다음 시도에서는 GPU 비활성화
                        use_gpu = False
                    else:
                        raise RuntimeError(
                            "PaddleOCR 초기화 실패\n"
                            "해결 방법:\n"
                            "1. pip install --upgrade paddleocr paddlepaddle\n"
                            "2. Visual C++ 재배포 패키지 설치\n"
                            "3. Python 3.8-3.11 버전 확인"
                        )
        
        return PaddleTextExtractor._ocr
    
    def find_text_with_fallback(self, target_text: str, **kwargs) -> Optional[TextResult]:
        """폴백 전략을 포함한 텍스트 검색"""
        # 1차: 정확한 매칭
        result = self.find_text(target_text, exact_match=True, **kwargs)
        if result:
            return result
        
        # 2차: 부분 매칭
        result = self.find_text(target_text, exact_match=False, **kwargs)
        if result:
            return result
        
        # 3차: 정규화 후 매칭
        normalized_target = self._aggressive_normalize(target_text)
        result = self.find_text(normalized_target, exact_match=False, **kwargs)
        
        return result
    
    def _aggressive_normalize(self, text: str) -> str:
        """공격적인 텍스트 정규화"""
        # 모든 공백 제거
        text = text.replace(' ', '')
        # 특수문자 제거
        import re
        text = re.sub(r'[^\w\s가-힣]', '', text)
        return text
```

### 5. 통합 오류 처리 시스템

```python
# src/core/error_handler.py (새 파일)

from typing import Optional, Dict, Any, Callable
from enum import Enum
import traceback
from logger.app_logger import get_logger

class ErrorCategory(Enum):
    EXCEL = "excel"
    MONITOR = "monitor"
    IMAGE_SEARCH = "image_search"
    TEXT_SEARCH = "text_search"
    EXECUTION = "execution"

class ErrorHandler:
    """중앙 집중식 오류 처리"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.error_history = []
        self.recovery_strategies = {
            ErrorCategory.EXCEL: self._handle_excel_error,
            ErrorCategory.MONITOR: self._handle_monitor_error,
            ErrorCategory.IMAGE_SEARCH: self._handle_image_error,
            ErrorCategory.TEXT_SEARCH: self._handle_text_error,
        }
    
    def handle_error(self, error: Exception, category: ErrorCategory, 
                    context: Optional[Dict[str, Any]] = None) -> bool:
        """오류 처리 및 복구 시도"""
        error_info = {
            'error': error,
            'category': category,
            'context': context or {},
            'traceback': traceback.format_exc()
        }
        
        self.error_history.append(error_info)
        self.logger.error(f"[{category.value}] {error}")
        
        # 복구 전략 실행
        if category in self.recovery_strategies:
            return self.recovery_strategies[category](error, context)
        
        return False
    
    def _handle_excel_error(self, error: Exception, context: Dict) -> bool:
        """Excel 관련 오류 처리"""
        if "codec" in str(error) or "decode" in str(error):
            self.logger.info("인코딩 오류 감지 - CP949로 재시도")
            return True  # 재시도 신호
        
        if "Permission denied" in str(error):
            self.logger.error("Excel 파일이 다른 프로그램에서 열려있습니다")
            return False
        
        return False
    
    def _handle_text_error(self, error: Exception, context: Dict) -> bool:
        """OCR 관련 오류 처리"""
        if "PaddleOCR" in str(error):
            self.logger.info("OCR 초기화 실패 - 설치 상태 확인")
            from utils.ocr_manager import OCRManager
            ocr_manager = OCRManager()
            if not ocr_manager.is_installed():
                self.logger.error("OCR이 설치되지 않았습니다")
            return False
        
        if "region" in str(error):
            self.logger.info("영역 오류 - 전체 화면으로 재시도")
            return True  # 영역 없이 재시도
        
        return False

# Executor에 통합
class MacroExecutor:
    def __init__(self, settings: Settings, excel_manager=None):
        # ... 기존 코드 ...
        self.error_handler = ErrorHandler()
    
    def execute_step(self, step: MacroStep) -> Any:
        """개선된 단계 실행"""
        try:
            # ... 기존 실행 로직 ...
        except Exception as e:
            # 오류 카테고리 결정
            category = self._determine_error_category(step.step_type)
            
            # 오류 처리
            context = {
                'step': step,
                'step_index': getattr(self, 'current_step_index', -1)
            }
            
            if self.error_handler.handle_error(e, category, context):
                # 복구 성공 - 재시도
                self.logger.info("오류 복구 성공 - 재시도")
                return self.execute_step(step)
            else:
                # 복구 실패 - 오류 전파
                raise
```

---

## 📋 실행 체크리스트

### 1. 환경 설정
```bash
# 1. Python 버전 확인 (3.8-3.11)
python --version

# 2. 의존성 설치
pip install -r requirements.txt

# 3. OCR 모델 사전 다운로드
python -c "from paddleocr import PaddleOCR; PaddleOCR(lang='korean')"
```

### 2. 디버그 모드 활성화
```python
# settings.json
{
  "debug": true,
  "save_screenshots": true,
  "log_level": "DEBUG",
  "ocr": {
    "save_debug_images": true,
    "preprocessing": true
  }
}
```

### 3. 테스트 순서
1. **Excel 로드 테스트**: 한글 파일명, 한글 시트명
2. **모니터 감지 테스트**: 멀티 모니터 환경
3. **이미지 검색 테스트**: 다양한 신뢰도
4. **텍스트 검색 테스트**: Excel 변수 포함

---

## 🎯 즉시 적용 가능한 임시 해결책

### 1. Excel 파일 준비
- 파일명과 시트명은 영문 사용
- 열 이름 앞뒤 공백 제거
- UTF-8 인코딩으로 저장

### 2. 이미지 파일 준비
- PNG 형식 사용 권장
- 절대 경로로 저장
- 100% 크기로 캡처

### 3. OCR 사용 시
- 검색 영역 크게 설정
- 신뢰도 0.5-0.7 사용
- 부분 매칭 모드 사용

이 가이드를 따라 단계별로 수정하면 대부분의 오류를 해결할 수 있습니다.