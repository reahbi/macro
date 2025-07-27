# Excel 매크로 자동화 애플리케이션 리팩토링 보고서

## 개요
이 보고서는 Excel 매크로 자동화 애플리케이션의 코드베이스를 분석하여 코드 품질, 유지보수성, 성능을 개선할 수 있는 리팩토링 기회를 식별합니다.

## 목차
1. [코드 중복 문제](#1-코드-중복-문제)
2. [복잡한 함수들](#2-복잡한-함수들)
3. [명명 규칙 및 명확성](#3-명명-규칙-및-명확성)
4. [디자인 패턴 적용 기회](#4-디자인-패턴-적용-기회)
5. [성능 개선 기회](#5-성능-개선-기회)
6. [코드 구조 및 모듈 조직](#6-코드-구조-및-모듈-조직)
7. [오류 처리 패턴](#7-오류-처리-패턴)
8. [의존성 및 결합도](#8-의존성-및-결합도)

---

## 1. 코드 중복 문제

### 1.1 모니터 위치 이름 생성 로직 중복
**위치**: `text_search_step_dialog.py`의 여러 메서드  
**우선순위**: 🔴 높음

**문제 코드**:
```python
# _populate_monitor_options()에서
if monitor['y'] < -100:  # Above primary monitor
    if abs(monitor['x']) < x_offset_threshold:
        pos_name = "위쪽"
    elif monitor['x'] < -x_offset_threshold:
        pos_name = "왼쪽 위"
    else:
        pos_name = "오른쪽 위"
# ... 동일한 로직이 _select_region()과 _on_search_scope_changed()에서 반복
```

**리팩토링 제안**:
```python
def _get_monitor_position_name(self, monitor: dict) -> str:
    """모니터의 상대적 위치에 따른 이름 반환"""
    x_offset_threshold = 300
    
    if monitor['is_primary']:
        return "주"
    
    # Y축 기준 우선 판단
    if monitor['y'] < -100:  # 위쪽
        if abs(monitor['x']) < x_offset_threshold:
            return "위쪽"
        elif monitor['x'] < -x_offset_threshold:
            return "왼쪽 위"
        else:
            return "오른쪽 위"
    elif monitor['y'] > 100:  # 아래쪽
        if abs(monitor['x']) < x_offset_threshold:
            return "아래쪽"
        elif monitor['x'] < -x_offset_threshold:
            return "왼쪽 아래"
        else:
            return "오른쪽 아래"
    elif monitor['x'] < -100:
        return "왼쪽"
    elif monitor['x'] > 100:
        return "오른쪽"
    else:
        return "보조"

def _format_monitor_display_name(self, monitor: dict) -> str:
    """모니터 표시 이름 포맷"""
    position = self._get_monitor_position_name(monitor)
    return f"{position} 모니터 ({monitor['width']}x{monitor['height']})"
```

### 1.2 Excel 상태 업데이트 로직 중복
**위치**: `engine.py`, `excel_manager.py`  
**우선순위**: 🟡 중간

**문제**: Excel 상태 업데이트와 저장 로직이 여러 곳에 분산되어 있음

**리팩토링 제안**:
```python
class ExcelStatusManager:
    """Excel 상태 관리를 위한 전용 클래스"""
    
    def __init__(self, excel_manager: ExcelManager):
        self.excel_manager = excel_manager
        self.logger = get_logger(__name__)
    
    def update_and_save(self, row_index: int, status: str, save_immediately: bool = True):
        """상태 업데이트와 저장을 원자적으로 처리"""
        try:
            self.excel_manager.update_row_status(row_index, status)
            if save_immediately:
                saved_path = self.excel_manager.save_file()
                if saved_path:
                    self.logger.info(f"상태 업데이트 후 저장 완료: {saved_path}")
                else:
                    self.logger.warning("Excel 파일 저장 실패")
        except Exception as e:
            self.logger.error(f"상태 업데이트 중 오류: {e}")
            raise
```

---

## 2. 복잡한 함수들

### 2.1 `StepExecutor._execute_text_search()` 메서드
**위치**: `executor.py` (425-662줄)  
**우선순위**: 🔴 높음  
**복잡도**: 237줄, 중첩 레벨 5+

**문제점**:
- 단일 책임 원칙 위반 (변수 처리, 텍스트 검색, 클릭 수행 등)
- 과도한 조건문 중첩
- 두 가지 다른 Step 타입 처리 로직 혼재

**리팩토링 제안**:
```python
class TextSearchExecutor:
    """텍스트 검색 실행을 위한 전용 클래스"""
    
    def __init__(self, text_extractor, variables, logger):
        self.text_extractor = text_extractor
        self.variables = variables
        self.logger = logger
    
    def execute(self, step) -> Optional[Tuple[int, int]]:
        """텍스트 검색 단계 실행"""
        # 화면 안정화 대기
        self._wait_for_screen_stabilization(step)
        
        # OCR 설치 확인
        self._ensure_ocr_installed()
        
        # 검색 파라미터 추출
        params = self._extract_search_params(step)
        
        # 검색 텍스트 준비
        search_text = self._prepare_search_text(params)
        
        # 텍스트 검색 수행
        result = self._perform_search_with_retry(search_text, params)
        
        # 결과 처리
        return self._handle_search_result(result, params)
    
    def _extract_search_params(self, step) -> SearchParams:
        """단계에서 검색 파라미터 추출"""
        step_type = step.__class__.__name__
        
        if step_type == "DynamicTextSearchStep":
            return self._extract_dynamic_params(step)
        elif step_type == "TextSearchStep":
            return self._extract_text_search_params(step)
        else:
            return self._extract_legacy_params(step)
    
    def _prepare_search_text(self, params: SearchParams) -> str:
        """검색 텍스트 준비 (변수 치환, 정규화 등)"""
        text = params.search_text
        
        # 변수 치환
        if params.use_variables:
            text = self._substitute_variables(text)
        
        # 텍스트 정규화
        if params.normalize_text:
            text = self._normalize_special_chars(text)
        
        return text.strip()
    
    def _normalize_special_chars(self, text: str) -> str:
        """전각 문자를 반각으로 변환"""
        replacements = {
            '：': ':', '；': ';', '（': '(', '）': ')',
            '［': '[', '］': ']', '｛': '{', '｝': '}',
            '＜': '<', '＞': '>', '，': ',', '。': '.',
            '！': '!', '？': '?', '　': ' '
        }
        for full_width, half_width in replacements.items():
            text = text.replace(full_width, half_width)
        return text
```

### 2.2 `ExecutionEngine._execute_with_excel_workflow()` 메서드
**위치**: `engine.py` (636-791줄)  
**우선순위**: 🟡 중간  
**복잡도**: 155줄, 중첩 레벨 4+

**리팩토링 제안**:
```python
class ExcelWorkflowExecutor:
    """Excel 워크플로우 실행을 위한 전용 클래스"""
    
    def execute(self, macro: Macro, excel_manager: ExcelManager):
        """Excel 워크플로우 블록 실행"""
        self._validate_excel_manager(excel_manager)
        self._ensure_status_column(excel_manager)
        
        blocks = self._find_excel_blocks(macro.steps)
        if not blocks:
            raise ValueError("유효한 Excel 워크플로우 블록이 없습니다")
        
        for block in blocks:
            self._execute_block(block, excel_manager)
    
    def _execute_block(self, block: dict, excel_manager: ExcelManager):
        """단일 Excel 블록 실행"""
        target_rows = self._determine_target_rows(block['start_step'], excel_manager)
        
        for row_index in target_rows:
            if self._should_stop():
                break
                
            self._wait_if_paused()
            self._execute_row_in_block(row_index, block, excel_manager)
```

---

## 3. 명명 규칙 및 명확성

### 3.1 불명확한 변수명
**우선순위**: 🟡 중간

**문제 사례**:
- `df` → `dataframe` 또는 `excel_data`
- `x_offset_threshold` → `monitor_alignment_threshold`
- `results` → `extracted_text_results`
- `found_result` → `matching_text_location`

### 3.2 일관성 없는 메서드 접두사
**우선순위**: 🟢 낮음

**문제**: private 메서드 표시가 일관되지 않음
- 일부는 `_` 접두사 사용
- 일부는 접두사 없이 사용

**권장사항**: 모든 private 메서드에 `_` 접두사 사용

---

## 4. 디자인 패턴 적용 기회

### 4.1 Strategy 패턴: Step 실행
**위치**: `StepExecutor` 클래스  
**우선순위**: 🔴 높음

**현재 문제**: 거대한 핸들러 딕셔너리와 if-else 체인

**리팩토링 제안**:
```python
from abc import ABC, abstractmethod

class StepExecutionStrategy(ABC):
    """단계 실행 전략의 기본 클래스"""
    
    @abstractmethod
    def execute(self, step: MacroStep, context: ExecutionContext) -> Any:
        """단계 실행"""
        pass
    
    @abstractmethod
    def validate(self, step: MacroStep) -> List[str]:
        """단계 유효성 검증"""
        pass

class MouseClickStrategy(StepExecutionStrategy):
    """마우스 클릭 실행 전략"""
    
    def execute(self, step: MouseClickStep, context: ExecutionContext) -> None:
        x, y = context.get_absolute_position(step.x, step.y, step.relative_to)
        
        if step.clicks == 1:
            context.click_with_human_delay(x, y, button=step.button.value)
        else:
            context.human_like_mouse_move(x, y)
            if context.enable_human_movement:
                time.sleep(random.uniform(context.click_delay_min, context.click_delay_max))
            pyautogui.click(x=x, y=y, clicks=step.clicks, 
                          interval=step.interval, button=step.button.value)

class StepExecutor:
    """리팩토링된 Step 실행자"""
    
    def __init__(self, settings: Settings):
        self.strategies = {
            StepType.MOUSE_CLICK: MouseClickStrategy(),
            StepType.KEYBOARD_TYPE: KeyboardTypeStrategy(),
            # ... 다른 전략들
        }
    
    def execute_step(self, step: MacroStep) -> Any:
        strategy = self.strategies.get(step.step_type)
        if not strategy:
            raise NotImplementedError(f"No strategy for {step.step_type}")
        
        context = ExecutionContext(self.settings, self.variables)
        return strategy.execute(step, context)
```

### 4.2 Observer 패턴: 진행 상황 추적
**위치**: 실행 엔진과 UI 간 통신  
**우선순위**: 🟡 중간

**리팩토링 제안**:
```python
class ProgressObserver(ABC):
    """진행 상황 관찰자 인터페이스"""
    
    @abstractmethod
    def on_step_started(self, step: MacroStep, row_index: int):
        pass
    
    @abstractmethod
    def on_step_completed(self, step: MacroStep, success: bool):
        pass
    
    @abstractmethod
    def on_progress_updated(self, current: int, total: int):
        pass

class ExecutionEngine:
    def __init__(self):
        self._observers: List[ProgressObserver] = []
    
    def add_observer(self, observer: ProgressObserver):
        self._observers.append(observer)
    
    def _notify_step_started(self, step: MacroStep, row_index: int):
        for observer in self._observers:
            observer.on_step_started(step, row_index)
```

---

## 5. 성능 개선 기회

### 5.1 Excel 파일 저장 최적화
**위치**: `excel_manager.py`  
**우선순위**: 🔴 높음

**문제**: 각 행마다 전체 Excel 파일을 다시 저장

**리팩토링 제안**:
```python
class BatchedExcelWriter:
    """배치 단위로 Excel 변경사항 저장"""
    
    def __init__(self, excel_manager: ExcelManager, batch_size: int = 10):
        self.excel_manager = excel_manager
        self.batch_size = batch_size
        self.pending_updates = []
        self.last_save_time = time.time()
    
    def update_row_status(self, row_index: int, status: str):
        """상태 업데이트를 버퍼에 추가"""
        self.pending_updates.append((row_index, status))
        
        if len(self.pending_updates) >= self.batch_size:
            self.flush()
    
    def flush(self):
        """버퍼의 모든 업데이트 적용 및 저장"""
        if not self.pending_updates:
            return
            
        # 모든 업데이트 적용
        for row_index, status in self.pending_updates:
            self.excel_manager._current_data.update_row_status(row_index, status)
        
        # 한 번만 저장
        self.excel_manager.save_file()
        self.pending_updates.clear()
        self.last_save_time = time.time()
```

### 5.2 이미지 매칭 캐싱
**위치**: `image_matcher.py`  
**우선순위**: 🟡 중간

**리팩토링 제안**:
```python
from functools import lru_cache
import hashlib

class ImageMatcher:
    def __init__(self):
        self._template_cache = {}
    
    @lru_cache(maxsize=32)
    def _load_and_prepare_template(self, image_path: str) -> np.ndarray:
        """템플릿 이미지 로드 및 전처리 (캐시됨)"""
        template = cv2.imread(image_path)
        if template is None:
            raise ValueError(f"Cannot load image: {image_path}")
        return cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    def find_image(self, image_path: str, region: Optional[Tuple] = None) -> ImageSearchResult:
        """캐시를 활용한 이미지 검색"""
        template = self._load_and_prepare_template(image_path)
        # ... 검색 로직
```

---

## 6. 코드 구조 및 모듈 조직

### 6.1 순환 의존성 문제
**우선순위**: 🔴 높음

**문제**: `macro_types.py`가 다른 모듈을 import하면서 순환 의존성 발생

**리팩토링 제안**:
```
src/
├── core/
│   ├── base_types.py      # 기본 타입, enum, 추상 클래스
│   ├── step_types.py       # 구체적인 Step 클래스들
│   ├── step_factory.py     # StepFactory 분리
│   └── macro.py           # Macro 클래스
```

### 6.2 UI와 비즈니스 로직 분리
**우선순위**: 🟡 중간

**문제**: Dialog 클래스에 비즈니스 로직이 포함됨

**리팩토링 제안**:
```python
class TextSearchStepModel:
    """텍스트 검색 단계의 비즈니스 로직"""
    
    def __init__(self, step: TextSearchStep):
        self.step = step
    
    def validate(self) -> List[str]:
        """단계 유효성 검증"""
        errors = []
        if not self.has_valid_search_source():
            errors.append("검색 텍스트 또는 엑셀 열을 지정해야 합니다")
        return errors
    
    def has_valid_search_source(self) -> bool:
        """유효한 검색 소스가 있는지 확인"""
        return bool(self.step.search_text) or bool(self.step.excel_column)

class TextSearchStepDialog(QDialog):
    """UI만 담당하는 다이얼로그"""
    
    def __init__(self, model: TextSearchStepModel):
        self.model = model
        # UI 초기화
```

---

## 7. 오류 처리 패턴

### 7.1 일관성 없는 예외 처리
**우선순위**: 🟡 중간

**문제**: 예외 처리 방식이 일관되지 않음

**리팩토링 제안**:
```python
class MacroExecutionError(Exception):
    """매크로 실행 관련 기본 예외"""
    pass

class StepExecutionError(MacroExecutionError):
    """단계 실행 실패"""
    def __init__(self, step: MacroStep, original_error: Exception):
        self.step = step
        self.original_error = original_error
        super().__init__(f"Step '{step.name}' failed: {original_error}")

class OCRNotInstalledError(MacroExecutionError):
    """OCR이 설치되지 않음"""
    pass

# 사용 예
try:
    self.step_executor.execute_step(step)
except OCRNotInstalledError:
    # OCR 설치 안내
    self._prompt_ocr_installation()
except StepExecutionError as e:
    # 단계별 오류 처리
    self._handle_step_error(e.step, e.original_error)
```

### 7.2 리소스 정리 보장
**우선순위**: 🟡 중간

**리팩토링 제안**:
```python
from contextlib import contextmanager

@contextmanager
def excel_file_context(excel_manager: ExcelManager):
    """Excel 파일 작업 컨텍스트"""
    try:
        yield excel_manager
    finally:
        # 항상 저장 시도
        try:
            excel_manager.save_file()
        except Exception as e:
            logger.error(f"Failed to save Excel file: {e}")

# 사용
with excel_file_context(self.excel_manager) as em:
    for row in rows:
        em.update_row_status(row, "처리중")
        # ... 작업 수행
```

---

## 8. 의존성 및 결합도

### 8.1 높은 결합도: StepExecutor
**우선순위**: 🔴 높음

**문제**: StepExecutor가 너무 많은 책임과 의존성을 가짐

**리팩토링 제안**:
```python
# 의존성 주입을 통한 느슨한 결합
class StepExecutor:
    def __init__(self, 
                 image_matcher: ImageMatcherInterface,
                 text_extractor: TextExtractorInterface,
                 input_controller: InputControllerInterface,
                 variable_resolver: VariableResolverInterface):
        self.image_matcher = image_matcher
        self.text_extractor = text_extractor
        self.input_controller = input_controller
        self.variable_resolver = variable_resolver

# 인터페이스 정의
class ImageMatcherInterface(ABC):
    @abstractmethod
    def find_image(self, image_path: str, **kwargs) -> Optional[Location]:
        pass

class InputControllerInterface(ABC):
    @abstractmethod
    def click(self, x: int, y: int, **kwargs):
        pass
    
    @abstractmethod
    def type_text(self, text: str, **kwargs):
        pass
```

---

## 우선순위별 요약

### 🔴 높은 우선순위 (즉시 처리 필요)
1. **텍스트 검색 메서드 분해**: 복잡도 감소, 유지보수성 향상
2. **Strategy 패턴 적용**: Step 실행 로직 개선
3. **Excel 저장 최적화**: 성능 대폭 향상
4. **순환 의존성 해결**: 모듈 구조 개선

### 🟡 중간 우선순위 (점진적 개선)
1. **Excel 워크플로우 리팩토링**: 가독성 향상
2. **오류 처리 일관성**: 디버깅 용이성 향상
3. **UI/비즈니스 로직 분리**: 테스트 가능성 향상

### 🟢 낮은 우선순위 (여유 있을 때)
1. **명명 규칙 통일**: 코드 일관성
2. **문서화 개선**: 유지보수성 향상

---

## 예상 효과

### 성능 개선
- Excel 저장 횟수 90% 감소 (배치 처리)
- 이미지 매칭 속도 30% 향상 (캐싱)

### 유지보수성 향상
- 텍스트 검색 로직 이해 시간 70% 단축
- 새로운 Step 타입 추가 시간 50% 단축

### 안정성 향상
- 예외 처리 일관성으로 버그 감소
- 리소스 누수 방지

---

## 구현 로드맵

### Phase 1 (1-2주)
- [ ] 텍스트 검색 메서드 분해
- [ ] Excel 저장 최적화
- [ ] 중복 코드 제거

### Phase 2 (2-3주)
- [ ] Strategy 패턴 구현
- [ ] 순환 의존성 해결
- [ ] 오류 처리 개선

### Phase 3 (3-4주)
- [ ] UI/비즈니스 로직 분리
- [ ] 전체적인 코드 정리
- [ ] 문서화 업데이트