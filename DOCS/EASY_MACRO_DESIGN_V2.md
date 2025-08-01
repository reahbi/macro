# Easy Macro 모드 설계 문서 v2.0

## 1. 개요

Easy Macro는 대화형 인터페이스를 통해 누구나 쉽게 매크로를 만들 수 있는 기능입니다. 엑셀 데이터를 기반으로 시작하여, 실제 매크로 기능들을 하나씩 추가하면서 자연스럽게 자동화 작업을 구성할 수 있습니다.

## 2. 핵심 컨셉

### 2.1 설계 원칙
- **엑셀 중심**: 엑셀 데이터 연동을 시작점으로
- **기능 중심**: 실제 매크로 액션을 중심으로 대화 진행
- **점진적 구성**: 한 번에 하나씩 액션을 추가하며 매크로 완성
- **실시간 피드백**: 각 단계마다 시각적 확인 가능

### 2.2 대화 흐름
```
엑셀 연동 → 반복 설정 → 액션 추가(반복) → 테스트 → 저장
    ↓           ↓            ↓
  데이터 확인  범위 선택   기능별 대화
```

## 3. 대화 시나리오

### 3.1 시작: 엑셀 연동
```
🤖 안녕하세요! Excel 데이터를 활용해서 작업을 자동화해보세요.
   엑셀 파일을 드래그하거나 클릭해서 업로드해주세요.

   [📁 파일 선택...]

🤖 '평가.xlsx' 파일을 확인했어요!
   다음 정보들을 찾았습니다:
   
   📊 시트: Sheet1
   📋 데이터: 103행
   📑 열 목록: 환자명, 전화번호, 주소
   
   이 데이터로 작업을 시작할까요?
   
   [✅ 네, 시작해요]  [🔄 다른 시트 선택]
```

### 3.2 반복 설정
```
🤖 어떤 데이터를 처리할까요?

   [📊 모든 데이터 (103개)]
   [✅ 아직 처리 안 된 것만 (98개)]
   [🎯 특정 범위 선택]
   [1️⃣ 하나만 테스트]

👤 아직 처리 안 된 것만

🤖 좋아요! 98개의 미처리 데이터를 순서대로 처리하겠습니다.
   이제 각 데이터로 무엇을 할지 정해볼까요?
```

### 3.3 액션 추가 - 메인 대화
```
🤖 어떤 작업을 추가할까요?

   [🖱️ 화면 클릭]
   [⌨️ 텍스트 입력]
   [🔍 텍스트 찾기]
   [🖼️ 이미지 찾기]
   [⏱️ 잠시 대기]
   [❓ 조건 확인]
   [✅ 완료]

👤 텍스트 찾기
```

### 3.4 텍스트 찾기 상세 설정
```
🤖 어떤 텍스트를 찾을까요?

   [📊 엑셀 데이터 사용]
   [📝 직접 입력]

👤 엑셀 데이터 사용

🤖 어떤 열의 데이터를 찾을까요?

   [환자명]
   [전화번호]
   [주소]

👤 환자명

🤖 '환자명'을 찾으면 어떻게 할까요?

   [🖱️ 클릭하기]
   [🖱️🖱️ 더블클릭]
   [⌨️ 텍스트 입력]
   [➡️ 그냥 넘어가기]

👤 더블클릭

🤖 좋아요! 추가했어요: "환자명 텍스트를 찾아서 더블클릭"
   
   다른 작업을 추가하시겠어요?
   
   [➕ 네, 더 추가할게요]
   [✅ 아니요, 이제 됐어요]
```

### 3.5 텍스트 입력 상세 설정
```
🤖 무엇을 입력할까요?

   [📊 엑셀 데이터]
   [📝 고정 텍스트]
   [🔤 변수 조합]
   [📅 오늘 날짜]

👤 엑셀 데이터

🤖 어떤 데이터를 입력할까요?

   [환자명]
   [전화번호]
   [주소]
   [여러 개 조합]

👤 전화번호

🤖 추가했어요: "전화번호 입력"
   
   💡 팁: 입력 후 Tab이나 Enter를 누르시겠어요?
   
   [⌨️ Tab 키]
   [⏎ Enter 키]
   [❌ 아니요]
```

### 3.6 이미지 찾기 상세 설정
```
🤖 찾을 이미지를 선택해주세요

   [📸 화면에서 캡처]
   [📁 파일에서 선택]

👤 화면에서 캡처

🤖 찾고 싶은 부분을 마우스로 선택해주세요
   (ESC: 취소)

   [화면 캡처 모드 실행]

🤖 이미지를 캡처했어요! 이 이미지를 찾으면 어떻게 할까요?

   [🖱️ 클릭]
   [🖱️🖱️ 더블클릭]
   [🖱️ 우클릭]
   [⏱️ 잠시 대기]
   [❌ 못 찾으면 건너뛰기]
```

### 3.7 조건부 액션
```
🤖 어떤 조건을 확인할까요?

   [📄 특정 텍스트가 있는지]
   [🖼️ 특정 이미지가 보이는지]
   [📊 엑셀 값 비교]

👤 특정 텍스트가 있는지

🤖 어떤 텍스트를 확인할까요?

   [📝 직접 입력: ___________]
   [📊 엑셀 데이터 사용]

👤 "처리완료"

🤖 "처리완료" 텍스트가 있으면 어떻게 할까요?

   [➡️ 다음 데이터로]
   [🔄 다른 작업 수행]
   [⏹️ 작업 중단]

🤖 없으면 어떻게 할까요?

   [✅ 계속 진행]
   [🔄 다른 작업 수행]
   [⏱️ 대기 후 재확인]
```

## 4. 액션 구성 UI

### 4.1 전체 레이아웃
```
┌─────────────────────────────────────────────────────────────────┐
│  Easy Macro - 쉽게 매크로 만들기                [1]→[2]→[3]→[4]→[5] │
├───────────────────────┬─────────────────────┬──────────────────┤
│   대화 인터페이스        │   매크로 구성        │  엑셀 미리보기    │
│                       │                     │                  │
│ 🤖 어떤 작업을        │ 1. 텍스트 찾기      │ 환자명 | 전화번호 │
│    추가할까요?        │    └→ "환자명"      │ ─────────────── │
│                       │    └→ 더블클릭      │ 홍길동 | 010-1234│
│ [클릭] [입력] [찾기]   │                     │ 김철수 | 010-5678│
│                       │ 2. 텍스트 입력      │ 이영희 | 010-9012│
│ 👤 입력               │    └→ 전화번호      │                  │
│                       │                     │                  │
│ 🤖 무엇을 입력할까요?  │ 3. 클릭            │                  │
│                       │    └→ "저장" 버튼   │                  │
│ [엑셀] [텍스트] [날짜] │                     │                  │
└───────────────────────┴─────────────────────┴──────────────────┘
│ [🔙 이전] [🧪 테스트] [💾 저장] [▶️ 실행]                         │
└─────────────────────────────────────────────────────────────────┘
```

### 4.2 액션 카드 디자인
```
┌─────────────────────────────┐
│ 1️⃣ 텍스트 찾기               │
│ ─────────────────────────── │
│ 🔍 찾을 텍스트: ${환자명}     │
│ 🖱️ 동작: 더블클릭            │
│                             │
│ [✏️ 수정] [🗑️ 삭제]         │
└─────────────────────────────┘
```

## 5. 스마트 어시스턴트

### 5.1 패턴 인식 및 제안
```
🤖 💡 로그인이 필요한 것 같네요! 로그인 과정을 추가할까요?

   [✅ 네, 추가해주세요]
   [❌ 아니요, 괜찮아요]

👤 네, 추가해주세요

🤖 로그인 정보는 어떻게 입력할까요?

   [📊 엑셀에 있어요]
   [🔒 매번 직접 입력]
   [💾 저장된 정보 사용]
```

### 5.2 연속 액션 제안
```
🤖 💡 텍스트를 입력하셨네요. 입력 후 Enter를 누를까요?

   [⏎ 네, Enter 추가]
   [⌨️ Tab 키 추가]
   [❌ 아니요]

🤖 💡 데이터 입력이 끝났나요? 저장 버튼을 찾아볼까요?

   [✅ 네, 저장 버튼 찾기]
   [📸 스크린샷 찍기]
   [➡️ 다음 데이터로]
```

## 6. 기술 구현

### 6.1 대화 엔진 아키텍처
```python
class ConversationFlow:
    """대화 흐름 관리"""
    
    def __init__(self):
        self.current_context = "excel_setup"
        self.action_stack = []
        self.excel_data = None
        self.pending_action = None
        
    def get_next_prompt(self) -> DialogPrompt:
        """현재 컨텍스트에 따른 다음 프롬프트 생성"""
        if self.current_context == "excel_setup":
            return self.prompt_excel_setup()
        elif self.current_context == "action_selection":
            return self.prompt_action_selection()
        elif self.current_context == "action_detail":
            return self.prompt_action_detail()
```

### 6.2 액션 빌더 시스템
```python
class ActionBuilder:
    """대화를 통한 액션 생성"""
    
    ACTION_TYPES = {
        "click": ClickActionBuilder,
        "type": TypeActionBuilder,
        "text_search": TextSearchBuilder,
        "image_search": ImageSearchBuilder,
        "wait": WaitActionBuilder,
        "condition": ConditionBuilder
    }
    
    def build_from_conversation(self, action_type: str, 
                               responses: Dict) -> MacroStep:
        """대화 응답을 MacroStep으로 변환"""
        builder = self.ACTION_TYPES[action_type]()
        return builder.create_step(responses)
```

### 6.3 실시간 프리뷰
```python
class MacroPreview(QWidget):
    """매크로 구성 실시간 표시"""
    
    def __init__(self):
        super().__init__()
        self.flow_layout = FlowLayout()
        self.action_cards = []
        
    def add_action_card(self, step: MacroStep):
        """새 액션 카드 추가 with 애니메이션"""
        card = ActionCard(step)
        card.edited.connect(self.on_card_edited)
        card.deleted.connect(self.on_card_deleted)
        
        # 슬라이드 인 애니메이션
        self.animate_card_entry(card)
        self.action_cards.append(card)
```

## 7. 대화 상태 관리

### 7.1 컨텍스트 트리
```
excel_setup
├── sheet_selection
├── data_range
└── action_selection
    ├── click_action
    │   ├── target_selection
    │   └── click_type
    ├── type_action
    │   ├── content_selection
    │   └── post_action
    ├── search_action
    │   ├── search_target
    │   ├── search_source
    │   └── found_action
    └── condition_action
        ├── condition_type
        ├── true_branch
        └── false_branch
```

### 7.2 상태 전이 로직
```python
class StateManager:
    def __init__(self):
        self.state_stack = ["excel_setup"]
        self.context_data = {}
        
    def transition_to(self, new_state: str):
        """상태 전이 with 이전 상태 저장"""
        self.state_stack.append(new_state)
        
    def go_back(self):
        """이전 상태로 돌아가기"""
        if len(self.state_stack) > 1:
            self.state_stack.pop()
            return self.state_stack[-1]
```

## 8. 학습 및 추천 시스템

### 8.1 사용 패턴 학습
```python
class PatternLearner:
    """사용자 패턴 학습 및 추천"""
    
    def __init__(self):
        self.action_sequences = []
        self.common_patterns = {}
        
    def learn_sequence(self, actions: List[MacroStep]):
        """액션 시퀀스 학습"""
        pattern_hash = self.hash_sequence(actions)
        self.common_patterns[pattern_hash] = \
            self.common_patterns.get(pattern_hash, 0) + 1
            
    def suggest_next_action(self, current_actions: List[MacroStep]) -> str:
        """현재 액션 기반 다음 액션 추천"""
        # 유사 패턴 찾기
        similar_patterns = self.find_similar_patterns(current_actions)
        return self.most_likely_next_action(similar_patterns)
```

### 8.2 스마트 템플릿
```python
SMART_TEMPLATES = {
    "web_login": {
        "name": "웹사이트 로그인",
        "actions": [
            {"type": "text_search", "text": "아이디", "action": "click"},
            {"type": "type", "content": "${ID}"},
            {"type": "text_search", "text": "비밀번호", "action": "click"},
            {"type": "type", "content": "${PW}"},
            {"type": "text_search", "text": "로그인", "action": "click"}
        ]
    },
    "data_input": {
        "name": "폼 데이터 입력",
        "actions": [
            {"type": "text_search", "text": "${필드명}", "action": "click"},
            {"type": "type", "content": "${데이터}"},
            {"type": "keyboard", "keys": ["tab"]}
        ]
    }
}
```

## 9. 실행 및 테스트

### 9.1 단계별 테스트
```
🤖 첫 번째 데이터로 테스트해볼까요?

   [▶️ 테스트 시작]
   [⏭️ 건너뛰기]

👤 테스트 시작

🤖 테스트 중...
   ✅ 1. "홍길동" 텍스트 찾기 - 성공
   ✅ 2. 더블클릭 - 성공
   ✅ 3. "010-1234-5678" 입력 - 성공
   ⚠️ 4. "저장" 버튼 클릭 - 실패
   
   저장 버튼을 찾지 못했어요. 어떻게 할까요?
   
   [🔄 다시 설정]
   [⏭️ 이 단계 건너뛰기]
   [🛑 중단]
```

### 9.2 일괄 실행 옵션
```
🤖 매크로가 완성되었어요! 어떻게 실행할까요?

   [▶️ 전체 실행]
   [⏸️ 단계별 실행]
   [💾 저장만 하기]

👤 전체 실행

🤖 실행 옵션을 선택해주세요:

   ⏱️ 속도: [빠르게] [보통] [천천히]
   🔄 오류 시: [건너뛰기] [재시도] [중단]
   📸 기록: [스크린샷 저장] [로그만] [없음]
```

## 10. 확장성 및 발전 방향

### 10.1 AI 통합
- 자연어 이해 강화
- 화면 요소 자동 인식
- 최적 액션 순서 제안

### 10.2 협업 기능
- 매크로 템플릿 공유
- 커뮤니티 라이브러리
- 실시간 도움 요청

### 10.3 고급 기능
- 분기 처리 강화
- 변수 및 함수 지원
- API 연동 옵션

## 11. 성공 지표

### 11.1 사용성
- 5분 내 첫 매크로 생성
- 클릭 수 50% 감소
- 오류율 80% 감소

### 11.2 확장성
- 월 100개 이상 템플릿 생성
- 사용자 간 공유 활성화
- 지속적인 기능 개선