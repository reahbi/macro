# Easy Macro 구현 가이드

## 1. 메인 다이얼로그 구현

### 1.1 EasyMacroDialog 클래스
```python
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

class EasyMacroDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Easy Macro - 쉽게 매크로 만들기")
        self.setMinimumSize(1000, 700)
        
        # 대화 엔진 초기화
        self.conversation_engine = ConversationEngine()
        self.macro_builder = MacroBuilder()
        
        self.init_ui()
        self.start_conversation()
        
    def init_ui(self):
        layout = QHBoxLayout()
        
        # 왼쪽: 채팅 인터페이스
        self.chat_widget = self.create_chat_widget()
        layout.addWidget(self.chat_widget, 3)
        
        # 오른쪽: 매크로 미리보기
        self.preview_widget = self.create_preview_widget()
        layout.addWidget(self.preview_widget, 2)
        
        self.setLayout(layout)
```

### 1.2 채팅 위젯 구현
```python
def create_chat_widget(self):
    widget = QWidget()
    layout = QVBoxLayout()
    
    # 채팅 히스토리
    self.chat_history = QTextEdit()
    self.chat_history.setReadOnly(True)
    self.chat_history.setStyleSheet("""
        QTextEdit {
            background-color: #f5f5f5;
            border: 1px solid #ddd;
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
        }
    """)
    layout.addWidget(self.chat_history)
    
    # 선택지 버튼 영역
    self.options_widget = QWidget()
    self.options_layout = QHBoxLayout(self.options_widget)
    layout.addWidget(self.options_widget)
    
    widget.setLayout(layout)
    return widget
```

## 2. 대화 엔진 구현

### 2.1 ConversationEngine 클래스
```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional

class ConversationState(Enum):
    GREETING = "greeting"
    PURPOSE = "purpose"
    DATA_SOURCE = "data_source"
    EXCEL_MAPPING = "excel_mapping"
    ACTION_SEQUENCE = "action_sequence"
    ACTION_DETAIL = "action_detail"
    CONFIRMATION = "confirmation"
    COMPLETE = "complete"

@dataclass
class ConversationResponse:
    message: str
    options: List[str]
    action_required: Optional[str] = None
    
class ConversationEngine:
    def __init__(self):
        self.state = ConversationState.GREETING
        self.context = {
            "purpose": None,
            "use_excel": False,
            "excel_columns": [],
            "actions": []
        }
        
    def get_greeting(self) -> ConversationResponse:
        return ConversationResponse(
            message="안녕하세요! 👋 Excel Macro Helper입니다.\n어떤 작업을 자동화하고 싶으신가요?",
            options=[
                "📝 웹사이트에 데이터 입력",
                "🔍 웹사이트에서 정보 수집",
                "💾 파일 다운로드",
                "🎯 기타 작업"
            ]
        )
```

### 2.2 상태 전이 로직
```python
def process_option_selection(self, option: str) -> ConversationResponse:
    """옵션 선택 처리"""
    if self.state == ConversationState.GREETING:
        return self._handle_purpose_selection(option)
    elif self.state == ConversationState.PURPOSE:
        return self._handle_data_source_selection(option)
    elif self.state == ConversationState.DATA_SOURCE:
        return self._handle_excel_upload(option)
    # ... 추가 상태 처리
    
def _handle_purpose_selection(self, option: str) -> ConversationResponse:
    """목적 선택 처리"""
    if "데이터 입력" in option:
        self.context["purpose"] = "data_input"
        self.state = ConversationState.DATA_SOURCE
        return ConversationResponse(
            message="웹사이트에 데이터를 입력하시는군요! 📊\n엑셀 파일의 데이터를 사용하시나요?",
            options=[
                "예, 엑셀 파일이 있어요",
                "아니요, 직접 입력할게요"
            ]
        )
```

## 3. 매크로 빌더 구현

### 3.1 액션 템플릿 시스템
```python
class ActionTemplate:
    """자주 사용하는 액션 패턴을 템플릿화"""
    
    @staticmethod
    def create_login_sequence() -> List[MacroStep]:
        return [
            TextSearchStep(
                name="아이디 입력란 찾기",
                search_text="아이디",
                on_found={"action": "클릭", "params": {}}
            ),
            KeyboardTypeStep(
                name="아이디 입력",
                text="${아이디}",
                use_variables=True
            ),
            TextSearchStep(
                name="비밀번호 입력란 찾기",
                search_text="비밀번호",
                on_found={"action": "클릭", "params": {}}
            ),
            KeyboardTypeStep(
                name="비밀번호 입력",
                text="${비밀번호}",
                use_variables=True
            ),
            TextSearchStep(
                name="로그인 버튼 클릭",
                search_text="로그인",
                on_found={"action": "클릭", "params": {}}
            )
        ]
```

### 3.2 자연어 액션 변환
```python
class NaturalLanguageParser:
    """자연어를 매크로 액션으로 변환"""
    
    def __init__(self):
        self.action_patterns = {
            "클릭": ["클릭", "누르", "선택"],
            "입력": ["입력", "쓰기", "작성"],
            "검색": ["검색", "찾기"],
            "대기": ["기다리", "잠시", "대기"]
        }
        
    def parse_user_action(self, description: str) -> MacroStep:
        """사용자 설명을 MacroStep으로 변환"""
        description_lower = description.lower()
        
        # 클릭 액션 감지
        if any(word in description_lower for word in self.action_patterns["클릭"]):
            # "로그인 버튼을 클릭해요" → TextSearchStep + Click
            target = self.extract_target(description)
            return TextSearchStep(
                name=f"{target} 클릭",
                search_text=target,
                on_found={"action": "클릭", "params": {}}
            )
```

## 4. UI 인터랙션 구현

### 4.1 애니메이션 효과
```python
class AnimatedMessage(QWidget):
    """타이핑 효과가 있는 메시지 위젯"""
    
    def __init__(self, message: str, is_bot: bool = True):
        super().__init__()
        self.message = message
        self.is_bot = is_bot
        self.displayed_text = ""
        self.char_index = 0
        
        self.init_ui()
        self.start_animation()
        
    def start_animation(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_text)
        self.timer.start(30)  # 30ms마다 한 글자씩
        
    def update_text(self):
        if self.char_index < len(self.message):
            self.displayed_text += self.message[self.char_index]
            self.label.setText(self.displayed_text)
            self.char_index += 1
        else:
            self.timer.stop()
```

### 4.2 선택지 버튼 스타일
```python
def create_option_button(self, text: str) -> QPushButton:
    """스타일이 적용된 선택지 버튼 생성"""
    button = QPushButton(text)
    button.setStyleSheet("""
        QPushButton {
            background-color: #ffffff;
            border: 2px solid #007bff;
            border-radius: 20px;
            padding: 10px 20px;
            font-size: 14px;
            font-weight: bold;
            color: #007bff;
            min-width: 150px;
        }
        QPushButton:hover {
            background-color: #007bff;
            color: white;
        }
        QPushButton:pressed {
            background-color: #0056b3;
            border-color: #0056b3;
        }
    """)
    return button
```

## 5. 실시간 미리보기 구현

### 5.1 플로우차트 방식 미리보기
```python
class MacroFlowChart(QWidget):
    """매크로를 플로우차트로 시각화"""
    
    def __init__(self):
        super().__init__()
        self.steps = []
        self.init_ui()
        
    def add_step(self, step: MacroStep):
        """새 단계 추가 시 애니메이션"""
        step_widget = self.create_step_widget(step)
        
        # 페이드인 애니메이션
        effect = QGraphicsOpacityEffect()
        step_widget.setGraphicsEffect(effect)
        
        self.fade_animation = QPropertyAnimation(effect, b"opacity")
        self.fade_animation.setDuration(500)
        self.fade_animation.setStartValue(0)
        self.fade_animation.setEndValue(1)
        self.fade_animation.start()
        
        self.layout.addWidget(step_widget)
        self.steps.append(step_widget)
```

## 6. 엑셀 연동 도우미

### 6.1 스마트 컬럼 매핑
```python
class ExcelColumnMapper:
    """엑셀 열과 웹 필드를 자동 매핑"""
    
    def __init__(self):
        self.common_mappings = {
            "이름": ["name", "성명", "고객명", "사용자명"],
            "전화번호": ["phone", "연락처", "휴대폰", "전화"],
            "이메일": ["email", "메일", "이메일주소"],
            "주소": ["address", "addr", "주소지"],
        }
        
    def suggest_mapping(self, excel_columns: List[str], 
                       web_fields: List[str]) -> Dict[str, str]:
        """엑셀 열과 웹 필드 자동 매핑 제안"""
        mappings = {}
        
        for excel_col in excel_columns:
            excel_normalized = excel_col.lower().strip()
            
            # 정확히 일치하는 경우
            for web_field in web_fields:
                if excel_normalized == web_field.lower():
                    mappings[excel_col] = web_field
                    break
            
            # 유사어 매핑
            if excel_col not in mappings:
                for key, synonyms in self.common_mappings.items():
                    if excel_normalized in synonyms:
                        # 웹 필드에서 유사어 찾기
                        for web_field in web_fields:
                            if any(syn in web_field.lower() for syn in synonyms):
                                mappings[excel_col] = web_field
                                break
        
        return mappings
```

## 7. 통합 및 실행

### 7.1 메인 윈도우에 Easy Macro 버튼 추가
```python
# main_window.py 수정
def create_toolbar(self):
    """툴바에 Easy Macro 버튼 추가"""
    toolbar = self.addToolBar('Main')
    
    # 기존 버튼들...
    
    # Easy Macro 버튼
    easy_macro_action = QAction(QIcon('resources/icons/magic.png'), 
                               'Easy Macro', self)
    easy_macro_action.setStatusTip('대화형으로 쉽게 매크로 만들기')
    easy_macro_action.triggered.connect(self.open_easy_macro)
    toolbar.addAction(easy_macro_action)
    
def open_easy_macro(self):
    """Easy Macro 다이얼로그 열기"""
    dialog = EasyMacroDialog(self)
    if dialog.exec_() == QDialog.Accepted:
        # 생성된 매크로 JSON 로드
        macro_json = dialog.get_generated_macro()
        self.load_macro_from_json(macro_json)
        
        # Editor 탭으로 자동 전환
        self.tabs.setCurrentWidget(self.editor_tab)
```

### 7.2 JSON 생성 및 저장
```python
def generate_macro_json(self) -> dict:
    """대화 결과를 JSON으로 변환"""
    return {
        "name": f"Easy Macro - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "description": f"Easy Macro로 생성: {self.context['purpose']}",
        "steps": [step.to_dict() for step in self.macro_builder.steps],
        "created_by": "Easy Macro",
        "version": "1.0"
    }
```

## 8. 향후 확장 계획

### 8.1 AI 통합
- OpenAI API 연동으로 더 자연스러운 대화
- 사용자 의도 자동 파악
- 복잡한 시나리오 자동 생성

### 8.2 음성 인터페이스
- 음성 명령으로 매크로 생성
- TTS로 가이드 음성 제공

### 8.3 모바일 앱
- 모바일에서 매크로 생성
- QR 코드로 PC 연동