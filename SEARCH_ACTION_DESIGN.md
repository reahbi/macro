# 검색 액션 디자인 문서

## 개요

기존 구조를 최대한 유지하면서 현재의 이미지 및 텍스트 검색 기능에 "찾았을 때/못 찾았을 때" 액션을 추가하는 솔루션입니다.

## 1. 핵심 개념: 기존 검색 스텝 확장

새로운 스텝 타입을 만드는 대신, 기존의 `IMAGE_SEARCH`와 `OCR_TEXT` 스텝에 선택적 성공/실패 액션을 추가합니다.

```python
# 현재 구조 (변경 없음)
class ImageSearchStep(MacroStep):
    step_type = StepType.IMAGE_SEARCH
    image_path: str
    confidence: float
    region: Optional[Region]
    
    # 신규: 선택적 액션 속성
    on_found: Optional[Dict[str, Any]] = None
    on_not_found: Optional[Dict[str, Any]] = None

class OCRTextStep(MacroStep):
    step_type = StepType.OCR_TEXT
    search_text: str
    exact_match: bool
    region: Optional[Region]
    
    # 신규: 선택적 액션 속성
    on_found: Optional[Dict[str, Any]] = None
    on_not_found: Optional[Dict[str, Any]] = None
```

## 2. 액션 구조

기존 실행기(executor)와 호환되는 간단한 액션 형식:

```python
on_found/on_not_found = {
    "action": "click" | "type" | "continue" | "stop" | "skip_row" | "retry",
    "params": {
        # 액션별 파라미터
        "text": "...",          # type 액션용
        "offset_x": 0,          # click 액션용
        "offset_y": 0,          # click 액션용
        "max_retries": 3,       # retry 액션용
        "wait_time": 1,         # 액션 후 대기 시간
    }
}
```

## 3. UI 변경사항 (최소화)

### 옵션 1: 확장된 다이얼로그 (권장)

IMAGE_SEARCH 또는 OCR_TEXT 스텝을 더블클릭할 때 접을 수 있는 액션 섹션이 포함된 확장 다이얼로그 표시:

```
┌─────────────────────────────────────┐
│ 🔍 이미지 검색 설정                 │
├─────────────────────────────────────┤
│ [기본 설정 - 현재와 동일]           │
│ • 이미지 경로: [___________] [📁]   │
│ • 정확도: [====80%====]             │
│ • 영역: [ ] 특정 영역               │
│                                     │
│ ▼ 액션 (선택사항)                  │
│ ┌─────────────────────────────────┐ │
│ │ ✅ 찾았을 때:                   │ │
│ │ [✓] 액션 활성화                 │ │
│ │ 액션: [클릭         ▼]          │ │
│ │ 대기 시간: [1]초                │ │
│ └─────────────────────────────────┘ │
│ ┌─────────────────────────────────┐ │
│ │ ❌ 못 찾았을 때:               │ │
│ │ [✓] 액션 활성화                 │ │
│ │ 액션: [계속 진행     ▼]         │ │
│ └─────────────────────────────────┘ │
│                                     │
│ [테스트] [확인] [취소]              │
└─────────────────────────────────────┘
```

### 옵션 2: 탭 기반 다이얼로그

기존 다이얼로그에 탭 추가:

```
┌─────────────────────────────────────┐
│ [검색] [액션] [테스트]              │
├─────────────────────────────────────┤
│ 액션 탭 내용...                     │
└─────────────────────────────────────┘
```

## 4. 실행기 변경사항 (최소화)

```python
# executor.py - 기존 검색 실행 확장
def execute_image_search(self, step: ImageSearchStep):
    # 기존 검색 로직
    found, position = self.search_image(step.image_path, step.confidence)
    
    # 신규: 액션 처리
    if found and step.on_found:
        self._execute_search_action(step.on_found, position)
    elif not found and step.on_not_found:
        self._execute_search_action(step.on_not_found, None)
    
    return found

def _execute_search_action(self, action_config, position):
    action_type = action_config.get("action")
    params = action_config.get("params", {})
    
    if action_type == "click" and position:
        offset_x = params.get("offset_x", 0)
        offset_y = params.get("offset_y", 0)
        pyautogui.click(position[0] + offset_x, position[1] + offset_y)
    elif action_type == "type":
        text = self.substitute_variables(params.get("text", ""))
        pyautogui.typewrite(text)
    elif action_type == "stop":
        self.stop_execution = True
    elif action_type == "skip_row":
        self.skip_to_row_end = True
    elif action_type == "retry":
        # 재시도 로직
        pass
    
    # 지정된 경우 대기
    if params.get("wait_time"):
        time.sleep(params.get("wait_time"))
```

## 5. 하위 호환성

- 액션이 없는 기존 매크로는 이전과 동일하게 작동
- 새 액션은 선택사항 - 설정하지 않으면 동작 변경 없음
- 기존 스텝 타입 그대로 유지

## 6. 이 접근법의 장점

### 1) 최소한의 코드 변경
- 새로운 스텝 타입 없음
- 매크로 구조 변경 없음
- 실행기 변경사항은 추가만

### 2) UI 단순성
- 기존 다이얼로그 확장(교체 아님)
- 액션은 선택적이고 접을 수 있음
- 사용자에게 친숙한 인터페이스

### 3) 자연스러운 흐름
- 검색 → 찾음/못찾음 → 액션
- 복잡한 중첩이나 조건 없음
- 이해하기 쉬움

### 4) 엑셀 통합
- 모든 텍스트 필드에서 {{변수}} 작동
- 엑셀 워크플로우를 위한 "행 건너뛰기" 액션
- 엑셀 처리 변경 없음

## 7. 구현 우선순위

1. **1단계**: 기본 액션 (클릭, 계속, 중지)
2. **2단계**: 엑셀 액션 (행 건너뛰기, 변수)
3. **3단계**: 고급 액션 (재시도, 대기, 대체 검색)

## 8. 사용 예시

```python
# 클릭이 포함된 간단한 이미지 검색
step = ImageSearchStep(
    image_path="button.png",
    confidence=0.8,
    on_found={"action": "click"},
    on_not_found={"action": "continue"}
)

# 데이터 입력이 포함된 텍스트 검색
step = OCRTextStep(
    search_text="{{고객명}}",
    on_found={
        "action": "type",
        "params": {"text": "{{전화번호}}"}
    },
    on_not_found={"action": "skip_row"}
)
```

## 결론

이 디자인은 현재 시스템의 단순성을 유지하면서 강력한 조건부 실행 기능을 추가합니다. 변경사항은 최소화되고, 하위 호환성이 있으며, 사용자에게 직관적입니다.