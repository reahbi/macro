# Easy Macro 구현 가이드 v2.0

## 1. 전체 구조

### 1.1 디렉토리 구조
```
src/ui/easy_macro/
├── __init__.py
├── easy_macro_dialog.py      # 메인 다이얼로그
├── conversation_engine.py    # 대화 처리 엔진
├── action_builders/          # 액션별 빌더
│   ├── __init__.py
│   ├── click_builder.py
│   ├── type_builder.py
│   ├── search_builder.py
│   └── condition_builder.py
├── widgets/                  # UI 컴포넌트
│   ├── chat_widget.py
│   ├── action_card.py
│   ├── macro_preview.py
│   └── excel_preview.py
└── utils/
    ├── pattern_matcher.py    # 패턴 인식
    └── template_manager.py   # 템플릿 관리
```

## 2. 메인 다이얼로그 구현

### 2.1 EasyMacroDialog
```python
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import json
from typing import Dict, List, Optional

class EasyMacroDialog(QDialog):
    """Easy Macro 메인 다이얼로그"""
    
    def __init__(self, parent=None, excel_data=None):
        super().__init__(parent)
        self.parent_window = parent
        self.excel_data = excel_data
        
        # 엔진 초기화
        self.conversation_engine = ConversationEngine()
        self.action_stack = []
        self.current_action_builder = None
        
        self.setWindowTitle("Easy Macro - 대화로 만드는 매크로")
        self.setMinimumSize(1200, 800)
        
        self.init_ui()
        self.start_conversation()
        
    def init_ui(self):
        """UI 초기화"""
        main_layout = QVBoxLayout()
        
        # 상단 진행 표시
        self.progress_widget = self.create_progress_widget()
        main_layout.addWidget(self.progress_widget)
        
        # 메인 컨텐츠
        content_layout = QHBoxLayout()
        
        # 좌측: 대화 인터페이스
        self.chat_widget = ChatWidget()
        self.chat_widget.option_selected.connect(self.on_option_selected)
        content_layout.addWidget(self.chat_widget, 2)
        
        # 중앙: 매크로 구성 미리보기
        self.preview_widget = MacroPreview()
        self.preview_widget.action_edited.connect(self.on_action_edited)
        self.preview_widget.action_deleted.connect(self.on_action_deleted)
        content_layout.addWidget(self.preview_widget, 2)
        
        # 우측: 엑셀 데이터 미리보기
        self.excel_widget = ExcelPreview(self.excel_data)
        content_layout.addWidget(self.excel_widget, 1)
        
        main_layout.addLayout(content_layout)
        
        # 하단 버튼
        self.button_layout = self.create_bottom_buttons()
        main_layout.addLayout(self.button_layout)
        
        self.setLayout(main_layout)
```

## 3. 대화 엔진 구현

### 3.1 ConversationEngine
```python
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

class ConversationContext(Enum):
    """대화 컨텍스트 상태"""
    EXCEL_SETUP = "excel_setup"
    REPEAT_SETUP = "repeat_setup"
    ACTION_SELECTION = "action_selection"
    ACTION_DETAIL = "action_detail"
    TEST_CONFIRM = "test_confirm"
    SAVE_CONFIRM = "save_confirm"

@dataclass
class ConversationPrompt:
    """대화 프롬프트"""
    message: str
    options: List[Dict[str, any]]
    input_type: str = "options"  # options, file, text, capture
    context_data: Dict = None

class ConversationEngine:
    """대화 처리 엔진"""
    
    def __init__(self):
        self.context = ConversationContext.EXCEL_SETUP
        self.context_stack = []
        self.data = {
            "excel_file": None,
            "excel_columns": [],
            "repeat_mode": None,
            "actions": [],
            "current_action": None
        }
        
    def get_initial_prompt(self) -> ConversationPrompt:
        """초기 프롬프트"""
        return ConversationPrompt(
            message="안녕하세요! Excel 데이터를 활용해서 작업을 자동화해보세요.\n"
                   "엑셀 파일을 드래그하거나 클릭해서 업로드해주세요.",
            options=[{"icon": "📁", "text": "파일 선택", "action": "select_file"}],
            input_type="file"
        )
        
    def process_excel_file(self, file_path: str, excel_data: Dict) -> ConversationPrompt:
        """엑셀 파일 처리"""
        self.data["excel_file"] = file_path
        self.data["excel_columns"] = excel_data.get("columns", [])
        
        # 파일 정보 표시
        sheet_name = excel_data.get("sheet", "Sheet1")
        row_count = excel_data.get("row_count", 0)
        columns = ", ".join(excel_data.get("columns", []))
        
        message = f"'{file_path.split('/')[-1]}' 파일을 확인했어요!\n\n"
        message += f"📊 시트: {sheet_name}\n"
        message += f"📋 데이터: {row_count}행\n"
        message += f"📑 열 목록: {columns}\n\n"
        message += "이 데이터로 작업을 시작할까요?"
        
        self.context = ConversationContext.REPEAT_SETUP
        
        return ConversationPrompt(
            message=message,
            options=[
                {"icon": "✅", "text": "네, 시작해요", "action": "start"},
                {"icon": "🔄", "text": "다른 시트 선택", "action": "change_sheet"}
            ]
        )
```

### 3.2 액션 선택 처리
```python
def get_action_selection_prompt(self) -> ConversationPrompt:
    """액션 선택 프롬프트"""
    message = "어떤 작업을 추가할까요?"
    
    # 이미 추가된 액션이 있으면 표시
    if self.data["actions"]:
        message = f"지금까지 {len(self.data['actions'])}개의 작업을 추가했어요.\n"
        message += "어떤 작업을 더 추가할까요?"
    
    options = [
        {"icon": "🖱️", "text": "화면 클릭", "action": "click"},
        {"icon": "⌨️", "text": "텍스트 입력", "action": "type"},
        {"icon": "🔍", "text": "텍스트 찾기", "action": "text_search"},
        {"icon": "🖼️", "text": "이미지 찾기", "action": "image_search"},
        {"icon": "⏱️", "text": "잠시 대기", "action": "wait"},
        {"icon": "❓", "text": "조건 확인", "action": "condition"}
    ]
    
    # 액션이 있으면 완료 옵션 추가
    if self.data["actions"]:
        options.append({"icon": "✅", "text": "완료", "action": "complete"})
    
    return ConversationPrompt(
        message=message,
        options=options
    )
```

## 4. 액션 빌더 구현

### 4.1 베이스 액션 빌더
```python
from abc import ABC, abstractmethod
from typing import Dict, List
from core.macro_types import MacroStep

class BaseActionBuilder(ABC):
    """액션 빌더 베이스 클래스"""
    
    def __init__(self):
        self.responses = {}
        self.current_question = "init"
        
    @abstractmethod
    def get_next_prompt(self) -> ConversationPrompt:
        """다음 프롬프트 반환"""
        pass
        
    @abstractmethod
    def process_response(self, response: any) -> bool:
        """응답 처리. 완료되면 True 반환"""
        pass
        
    @abstractmethod
    def build_step(self) -> MacroStep:
        """최종 MacroStep 생성"""
        pass
```

### 4.2 텍스트 찾기 빌더
```python
class TextSearchBuilder(BaseActionBuilder):
    """텍스트 찾기 액션 빌더"""
    
    def __init__(self, excel_columns: List[str]):
        super().__init__()
        self.excel_columns = excel_columns
        self.flow = {
            "init": self._ask_search_source,
            "search_source": self._ask_search_text,
            "search_text": self._ask_found_action,
            "found_action": self._ask_action_detail,
            "complete": None
        }
        
    def get_next_prompt(self) -> ConversationPrompt:
        """현재 상태에 따른 프롬프트"""
        handler = self.flow.get(self.current_question)
        if handler:
            return handler()
        return None
        
    def _ask_search_source(self) -> ConversationPrompt:
        """검색 소스 질문"""
        return ConversationPrompt(
            message="어떤 텍스트를 찾을까요?",
            options=[
                {"icon": "📊", "text": "엑셀 데이터 사용", "action": "excel"},
                {"icon": "📝", "text": "직접 입력", "action": "manual"}
            ]
        )
        
    def _ask_search_text(self) -> ConversationPrompt:
        """검색 텍스트 선택/입력"""
        if self.responses["search_source"] == "excel":
            # 엑셀 열 선택
            options = []
            for col in self.excel_columns:
                options.append({"text": col, "action": f"column:{col}"})
                
            return ConversationPrompt(
                message="어떤 열의 데이터를 찾을까요?",
                options=options
            )
        else:
            # 직접 입력
            return ConversationPrompt(
                message="찾을 텍스트를 입력해주세요:",
                options=[],
                input_type="text"
            )
            
    def _ask_found_action(self) -> ConversationPrompt:
        """찾았을 때 액션"""
        text = self.responses.get("search_text", "텍스트")
        return ConversationPrompt(
            message=f"'{text}'을(를) 찾으면 어떻게 할까요?",
            options=[
                {"icon": "🖱️", "text": "클릭하기", "action": "click"},
                {"icon": "🖱️🖱️", "text": "더블클릭", "action": "double_click"},
                {"icon": "⌨️", "text": "텍스트 입력", "action": "type"},
                {"icon": "➡️", "text": "그냥 넘어가기", "action": "continue"}
            ]
        )
```

## 5. UI 위젯 구현

### 5.1 채팅 위젯
```python
class ChatWidget(QWidget):
    """대화 인터페이스 위젯"""
    
    option_selected = pyqtSignal(str)  # 옵션 선택 시그널
    text_entered = pyqtSignal(str)     # 텍스트 입력 시그널
    file_selected = pyqtSignal(str)    # 파일 선택 시그널
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.message_widgets = []
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 채팅 영역 (스크롤)
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.chat_layout = QVBoxLayout(self.scroll_widget)
        self.chat_layout.addStretch()
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        
        layout.addWidget(self.scroll_area)
        
        # 입력 영역
        self.input_widget = QWidget()
        self.input_layout = QVBoxLayout(self.input_widget)
        layout.addWidget(self.input_widget)
        
        self.setLayout(layout)
        
    def add_bot_message(self, message: str, typing_effect: bool = True):
        """봇 메시지 추가"""
        msg_widget = BotMessage(message, typing_effect)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, msg_widget)
        self.message_widgets.append(msg_widget)
        self._scroll_to_bottom()
        
    def add_user_message(self, message: str):
        """사용자 메시지 추가"""
        msg_widget = UserMessage(message)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, msg_widget)
        self.message_widgets.append(msg_widget)
        self._scroll_to_bottom()
        
    def show_options(self, options: List[Dict]):
        """선택지 표시"""
        # 기존 입력 위젯 제거
        self._clear_input_area()
        
        # 옵션 버튼 생성
        button_layout = QHBoxLayout()
        for option in options:
            btn = OptionButton(option)
            btn.clicked.connect(lambda checked, opt=option: 
                              self._on_option_selected(opt))
            button_layout.addWidget(btn)
            
        button_layout.addStretch()
        self.input_layout.addLayout(button_layout)
```

### 5.2 액션 카드 위젯
```python
class ActionCard(QFrame):
    """액션 카드 위젯"""
    
    edited = pyqtSignal(int)    # 수정 시그널
    deleted = pyqtSignal(int)   # 삭제 시그널
    
    def __init__(self, step: MacroStep, index: int):
        super().__init__()
        self.step = step
        self.index = index
        self.init_ui()
        
    def init_ui(self):
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
                padding: 10px;
            }
            QFrame:hover {
                border: 2px solid #007bff;
            }
        """)
        
        layout = QVBoxLayout()
        
        # 헤더 (번호 + 타입)
        header_layout = QHBoxLayout()
        
        # 번호
        number_label = QLabel(f"{self.index + 1}")
        number_label.setStyleSheet("""
            background-color: #007bff;
            color: white;
            border-radius: 12px;
            padding: 4px 8px;
            font-weight: bold;
        """)
        header_layout.addWidget(number_label)
        
        # 액션 타입
        type_label = QLabel(self._get_action_type_text())
        type_label.setStyleSheet("font-weight: bold;")
        header_layout.addWidget(type_label)
        header_layout.addStretch()
        
        # 버튼
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(30, 30)
        edit_btn.clicked.connect(lambda: self.edited.emit(self.index))
        header_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(30, 30)
        delete_btn.clicked.connect(lambda: self.deleted.emit(self.index))
        header_layout.addWidget(delete_btn)
        
        layout.addLayout(header_layout)
        
        # 상세 정보
        detail_label = QLabel(self._get_action_detail())
        detail_label.setWordWrap(True)
        detail_label.setStyleSheet("color: #666; padding: 5px 0;")
        layout.addWidget(detail_label)
        
        self.setLayout(layout)
```

### 5.3 매크로 프리뷰 위젯
```python
class MacroPreview(QWidget):
    """매크로 구성 미리보기"""
    
    action_edited = pyqtSignal(int)
    action_deleted = pyqtSignal(int)
    
    def __init__(self):
        super().__init__()
        self.action_cards = []
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 제목
        title = QLabel("매크로 구성")
        title.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # 스크롤 영역
        self.scroll_area = QScrollArea()
        self.scroll_widget = QWidget()
        self.cards_layout = QVBoxLayout(self.scroll_widget)
        self.cards_layout.addStretch()
        
        self.scroll_area.setWidget(self.scroll_widget)
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)
        
        # 빈 상태 메시지
        self.empty_label = QLabel("아직 추가된 작업이 없어요.\n대화를 통해 작업을 추가해보세요!")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #999; padding: 50px;")
        self.cards_layout.addWidget(self.empty_label)
        
        self.setLayout(layout)
        
    def add_action(self, step: MacroStep):
        """액션 추가"""
        # 빈 상태 메시지 숨기기
        if self.empty_label.isVisible():
            self.empty_label.hide()
            
        # 카드 생성
        card = ActionCard(step, len(self.action_cards))
        card.edited.connect(self.action_edited.emit)
        card.deleted.connect(self._on_card_deleted)
        
        # 애니메이션 효과
        self._animate_card_entry(card)
        
        # 레이아웃에 추가
        self.cards_layout.insertWidget(self.cards_layout.count() - 1, card)
        self.action_cards.append(card)
```

## 6. 스마트 기능 구현

### 6.1 패턴 매처
```python
class PatternMatcher:
    """사용 패턴 인식 및 추천"""
    
    def __init__(self):
        self.patterns = {
            "login": {
                "keywords": ["로그인", "login", "인증", "접속"],
                "suggest_actions": [
                    ("text_search", {"text": "아이디", "action": "click"}),
                    ("type", {"source": "input", "prompt": "아이디를 입력하세요"}),
                    ("text_search", {"text": "비밀번호", "action": "click"}),
                    ("type", {"source": "input", "prompt": "비밀번호를 입력하세요"}),
                    ("text_search", {"text": "로그인", "action": "click"})
                ]
            },
            "data_entry": {
                "keywords": ["입력", "등록", "저장", "폼"],
                "suggest_actions": [
                    ("text_search", {"text": "${필드명}", "action": "click"}),
                    ("type", {"source": "excel"}),
                    ("keyboard", {"key": "tab"})
                ]
            }
        }
        
    def detect_pattern(self, user_input: str) -> Optional[str]:
        """사용자 입력에서 패턴 감지"""
        input_lower = user_input.lower()
        
        for pattern_name, pattern_data in self.patterns.items():
            if any(keyword in input_lower for keyword in pattern_data["keywords"]):
                return pattern_name
                
        return None
        
    def get_suggested_actions(self, pattern_name: str) -> List[Tuple[str, Dict]]:
        """패턴에 따른 추천 액션"""
        pattern = self.patterns.get(pattern_name)
        if pattern:
            return pattern["suggest_actions"]
        return []
```

### 6.2 액션 추천 시스템
```python
class ActionRecommender:
    """다음 액션 추천"""
    
    def __init__(self):
        self.action_sequences = {
            # 이전 액션 → 추천 다음 액션
            "type": ["keyboard:tab", "keyboard:enter", "wait"],
            "click": ["type", "wait"],
            "text_search": ["click", "type"],
            "image_search": ["click", "wait"]
        }
        
    def recommend_next_action(self, current_actions: List[MacroStep]) -> List[str]:
        """현재 액션 기반 다음 액션 추천"""
        if not current_actions:
            return ["text_search", "click", "type"]
            
        last_action = current_actions[-1]
        last_type = last_action.step_type.value
        
        # 기본 추천
        recommendations = self.action_sequences.get(last_type, [])
        
        # 컨텍스트 기반 추천
        if last_type == "type":
            # 입력 후 탭이나 엔터 추천
            if not any(a.step_type.value == "keyboard" for a in current_actions[-3:]):
                recommendations.insert(0, "keyboard:enter")
                
        return recommendations[:3]  # 상위 3개만 반환
```

## 7. 매크로 생성 및 저장

### 7.1 JSON 변환
```python
def generate_macro_json(self) -> Dict:
    """대화 결과를 매크로 JSON으로 변환"""
    
    # 엑셀 반복 블록으로 감싸기
    steps = []
    
    # Excel Row Start
    if self.excel_data:
        excel_start = {
            "id": str(uuid.uuid4()),
            "name": "엑셀 데이터 반복 시작",
            "type": "excel_row_start",
            "enabled": True,
            "excel_file": self.excel_data.get("file_path", ""),
            "sheet": self.excel_data.get("sheet", "Sheet1"),
            "repeat_mode": self.data.get("repeat_mode", "all")
        }
        steps.append(excel_start)
    
    # 사용자가 추가한 액션들
    for action in self.action_stack:
        steps.append(action.to_dict())
    
    # Excel Row End
    if self.excel_data:
        excel_end = {
            "id": str(uuid.uuid4()),
            "name": "엑셀 데이터 반복 끝",
            "type": "excel_row_end",
            "enabled": True
        }
        steps.append(excel_end)
    
    # 매크로 메타데이터
    macro_data = {
        "name": f"Easy Macro - {datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "description": "Easy Macro로 생성된 자동화 작업",
        "version": "2.0",
        "created_by": "Easy Macro",
        "created_at": datetime.now().isoformat(),
        "steps": steps
    }
    
    return macro_data
```

### 7.2 메인 윈도우 통합
```python
# main_window.py에 추가
def create_easy_macro_button(self):
    """Easy Macro 버튼 생성"""
    easy_btn = QPushButton("🎯 Easy Macro")
    easy_btn.setStyleSheet("""
        QPushButton {
            background-color: #28a745;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            font-size: 16px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #218838;
        }
    """)
    easy_btn.clicked.connect(self.open_easy_macro)
    return easy_btn
    
def open_easy_macro(self):
    """Easy Macro 다이얼로그 열기"""
    # 현재 엑셀 데이터 가져오기
    excel_data = None
    if hasattr(self, 'excel_tab') and self.excel_tab.excel_handler.data is not None:
        excel_data = {
            "file_path": self.excel_tab.current_file_path,
            "sheet": self.excel_tab.excel_handler.active_sheet,
            "columns": self.excel_tab.excel_handler.get_column_names(),
            "row_count": len(self.excel_tab.excel_handler.data)
        }
    
    # Easy Macro 다이얼로그 실행
    dialog = EasyMacroDialog(self, excel_data)
    
    if dialog.exec_() == QDialog.Accepted:
        # 생성된 매크로 로드
        macro_json = dialog.generate_macro_json()
        
        # 임시 파일로 저장
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', 
                                       delete=False) as f:
            json.dump(macro_json, f, ensure_ascii=False, indent=2)
            temp_path = f.name
            
        # 매크로 로드
        self.editor_tab.load_macro_from_file(temp_path)
        
        # Editor 탭으로 전환
        self.tabs.setCurrentWidget(self.editor_tab)
        
        # 메시지 표시
        QMessageBox.information(
            self, 
            "Easy Macro 완료",
            "매크로가 성공적으로 생성되었습니다!\n"
            "Editor 탭에서 확인하고 수정할 수 있어요."
        )
```

## 8. 애니메이션 및 효과

### 8.1 타이핑 효과
```python
class TypingEffect(QObject):
    """타이핑 효과 애니메이션"""
    
    textUpdated = pyqtSignal(str)
    finished = pyqtSignal()
    
    def __init__(self, text: str, speed: int = 30):
        super().__init__()
        self.full_text = text
        self.current_text = ""
        self.index = 0
        self.speed = speed
        
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_text)
        
    def start(self):
        """애니메이션 시작"""
        self.timer.start(self.speed)
        
    def _update_text(self):
        """텍스트 업데이트"""
        if self.index < len(self.full_text):
            self.current_text += self.full_text[self.index]
            self.textUpdated.emit(self.current_text)
            self.index += 1
        else:
            self.timer.stop()
            self.finished.emit()
```

### 8.2 카드 애니메이션
```python
def _animate_card_entry(self, card: ActionCard):
    """카드 진입 애니메이션"""
    # 초기 상태
    card.setMaximumHeight(0)
    card.setMinimumHeight(0)
    
    # 높이 애니메이션
    self.height_anim = QPropertyAnimation(card, b"maximumHeight")
    self.height_anim.setDuration(300)
    self.height_anim.setStartValue(0)
    self.height_anim.setEndValue(150)
    self.height_anim.setEasingCurve(QEasingCurve.OutCubic)
    
    # 투명도 애니메이션
    effect = QGraphicsOpacityEffect()
    card.setGraphicsEffect(effect)
    
    self.opacity_anim = QPropertyAnimation(effect, b"opacity")
    self.opacity_anim.setDuration(300)
    self.opacity_anim.setStartValue(0)
    self.opacity_anim.setEndValue(1)
    
    # 애니메이션 그룹
    self.anim_group = QParallelAnimationGroup()
    self.anim_group.addAnimation(self.height_anim)
    self.anim_group.addAnimation(self.opacity_anim)
    
    # 완료 시 높이 제한 해제
    self.anim_group.finished.connect(
        lambda: card.setMaximumHeight(16777215))  # Qt max
    
    self.anim_group.start()
```

## 9. 테스트 및 디버깅

### 9.1 대화 흐름 테스트
```python
def test_conversation_flow():
    """대화 흐름 단위 테스트"""
    engine = ConversationEngine()
    
    # 초기 프롬프트
    prompt = engine.get_initial_prompt()
    assert prompt.input_type == "file"
    
    # 엑셀 파일 처리
    excel_data = {
        "columns": ["이름", "전화번호"],
        "row_count": 10,
        "sheet": "Sheet1"
    }
    prompt = engine.process_excel_file("test.xlsx", excel_data)
    assert engine.context == ConversationContext.REPEAT_SETUP
    
    # 액션 선택
    engine.process_response({"action": "start"})
    prompt = engine.get_action_selection_prompt()
    assert len(prompt.options) > 0
```

### 9.2 액션 빌더 테스트
```python
def test_text_search_builder():
    """텍스트 찾기 빌더 테스트"""
    builder = TextSearchBuilder(["이름", "전화번호"])
    
    # 검색 소스 선택
    prompt = builder.get_next_prompt()
    assert prompt.message == "어떤 텍스트를 찾을까요?"
    
    # 엑셀 선택
    builder.process_response({"action": "excel"})
    prompt = builder.get_next_prompt()
    assert len(prompt.options) == 2  # 2개 열
    
    # 열 선택
    builder.process_response({"action": "column:이름"})
    prompt = builder.get_next_prompt()
    assert "이름" in prompt.message
```

## 10. 확장 및 개선 사항

### 10.1 자연어 처리 추가
```python
class NaturalLanguageProcessor:
    """자연어 이해 처리기"""
    
    def __init__(self):
        # 간단한 키워드 기반 처리
        self.intent_patterns = {
            "click": ["클릭", "누르", "선택", "눌러"],
            "type": ["입력", "쓰", "작성", "적"],
            "search": ["찾", "검색", "확인"],
            "wait": ["기다", "대기", "잠시", "멈춤"]
        }
        
    def extract_intent(self, text: str) -> str:
        """텍스트에서 의도 추출"""
        text_lower = text.lower()
        
        for intent, patterns in self.intent_patterns.items():
            if any(pattern in text_lower for pattern in patterns):
                return intent
                
        return "unknown"
```

### 10.2 음성 인터페이스
```python
class VoiceInterface:
    """음성 인터페이스 (추가 개발 필요)"""
    
    def __init__(self):
        self.recognizer = None  # 음성 인식기
        self.tts_engine = None  # TTS 엔진
        
    def listen(self) -> str:
        """음성 입력 받기"""
        # 구현 필요
        pass
        
    def speak(self, text: str):
        """음성 출력"""
        # 구현 필요
        pass
```