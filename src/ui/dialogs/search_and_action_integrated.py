"""
통합된 검색하고 실행하기 GUI - 기존 매크로 에디터와 호환
"""

from typing import Optional, Dict, Any
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QRadioButton, QLineEdit, QComboBox, QSpinBox,
    QCheckBox, QTextEdit, QFileDialog, QListWidget, QListWidgetItem,
    QStackedWidget, QWidget, QSlider, QButtonGroup, QFrame,
    QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon, QPalette, QColor

class SearchAndActionIntegratedWidget(QWidget):
    """매크로 에디터에 통합되는 검색하고 실행하기 위젯"""
    
    # 시그널 정의
    stepConfigured = pyqtSignal(dict)  # 설정 완료 시그널
    
    def __init__(self, parent=None, initial_data=None):
        super().__init__(parent)
        self.initial_data = initial_data or {}
        self.excel_columns = []  # 엑셀 컬럼 목록
        self.init_ui()
        
    def set_excel_columns(self, columns):
        """엑셀 컬럼 목록 설정"""
        self.excel_columns = columns
        self.update_variable_completer()
        
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # 헤더
        header = QLabel("🔍 검색하고 실행하기")
        header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2196F3;
                padding: 10px;
                background-color: #E3F2FD;
                border-radius: 5px;
            }
        """)
        layout.addWidget(header)
        
        # 스크롤 영역
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(15)
        
        # Step 1: 검색 설정
        self.create_search_section(content_layout)
        
        # Step 2: 성공 시 액션
        self.create_success_action_section(content_layout)
        
        # Step 3: 실패 시 액션
        self.create_failure_action_section(content_layout)
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        # 하단 버튼
        self.create_bottom_buttons(layout)
        
    def create_search_section(self, layout):
        """검색 설정 섹션 생성"""
        group = QGroupBox("📌 Step 1: 무엇을 찾을까요?")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #ddd;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        group_layout = QVBoxLayout()
        
        # 검색 타입 선택
        type_layout = QHBoxLayout()
        self.search_type_group = QButtonGroup()
        
        self.image_radio = QRadioButton("🖼️ 이미지 찾기")
        self.text_radio = QRadioButton("📝 텍스트 찾기")
        self.image_radio.setChecked(True)
        
        self.search_type_group.addButton(self.image_radio, 0)
        self.search_type_group.addButton(self.text_radio, 1)
        
        type_layout.addWidget(self.image_radio)
        type_layout.addWidget(self.text_radio)
        type_layout.addStretch()
        
        group_layout.addLayout(type_layout)
        
        # 스택 위젯 (이미지/텍스트 설정)
        self.search_stack = QStackedWidget()
        
        # 이미지 검색 설정
        self.image_widget = self.create_image_search_widget()
        self.search_stack.addWidget(self.image_widget)
        
        # 텍스트 검색 설정
        self.text_widget = self.create_text_search_widget()
        self.search_stack.addWidget(self.text_widget)
        
        group_layout.addWidget(self.search_stack)
        
        # 시그널 연결
        self.search_type_group.buttonClicked.connect(
            lambda: self.search_stack.setCurrentIndex(self.search_type_group.checkedId())
        )
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
    def create_image_search_widget(self):
        """이미지 검색 위젯 생성"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 이미지 선택
        img_layout = QHBoxLayout()
        self.image_path_edit = QLineEdit()
        self.image_path_edit.setPlaceholderText("이미지 파일 경로...")
        
        browse_btn = QPushButton("📁 찾아보기")
        browse_btn.clicked.connect(self.browse_image)
        
        capture_btn = QPushButton("📸 화면 캡처")
        capture_btn.clicked.connect(self.capture_screen)
        
        img_layout.addWidget(self.image_path_edit, 3)
        img_layout.addWidget(browse_btn, 1)
        img_layout.addWidget(capture_btn, 1)
        
        layout.addLayout(img_layout)
        
        # 정확도 설정
        accuracy_layout = QHBoxLayout()
        accuracy_layout.addWidget(QLabel("정확도:"))
        
        self.accuracy_slider = QSlider(Qt.Horizontal)
        self.accuracy_slider.setRange(50, 100)
        self.accuracy_slider.setValue(80)
        self.accuracy_slider.setTickPosition(QSlider.TicksBelow)
        self.accuracy_slider.setTickInterval(10)
        
        self.accuracy_label = QLabel("80%")
        self.accuracy_slider.valueChanged.connect(
            lambda v: self.accuracy_label.setText(f"{v}%")
        )
        
        accuracy_layout.addWidget(self.accuracy_slider)
        accuracy_layout.addWidget(self.accuracy_label)
        
        layout.addLayout(accuracy_layout)
        
        # 검색 영역 설정
        self.search_region_check = QCheckBox("특정 영역에서만 검색")
        self.region_btn = QPushButton("🎯 영역 선택")
        self.region_btn.setEnabled(False)
        
        self.search_region_check.toggled.connect(self.region_btn.setEnabled)
        
        region_layout = QHBoxLayout()
        region_layout.addWidget(self.search_region_check)
        region_layout.addWidget(self.region_btn)
        region_layout.addStretch()
        
        layout.addLayout(region_layout)
        
        return widget
        
    def create_text_search_widget(self):
        """텍스트 검색 위젯 생성"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 검색 텍스트
        self.search_text_edit = QLineEdit()
        self.search_text_edit.setPlaceholderText("검색할 텍스트 입력... (예: {{고객명}})")
        layout.addWidget(self.search_text_edit)
        
        # 변수 힌트
        if self.excel_columns:
            hint = QLabel(f"💡 사용 가능한 변수: {', '.join([f'{{{{{col}}}}}' for col in self.excel_columns[:3]])}...")
            hint.setWordWrap(True)
            hint.setStyleSheet("color: #666; font-size: 11px;")
            layout.addWidget(hint)
        
        # 검색 옵션
        self.exact_match_check = QCheckBox("정확히 일치하는 텍스트만 찾기")
        layout.addWidget(self.exact_match_check)
        
        # 검색 영역
        self.text_region_check = QCheckBox("특정 영역에서만 검색")
        self.text_region_btn = QPushButton("🎯 영역 선택")
        self.text_region_btn.setEnabled(False)
        
        self.text_region_check.toggled.connect(self.text_region_btn.setEnabled)
        
        region_layout = QHBoxLayout()
        region_layout.addWidget(self.text_region_check)
        region_layout.addWidget(self.text_region_btn)
        region_layout.addStretch()
        
        layout.addLayout(region_layout)
        
        return widget
        
    def create_success_action_section(self, layout):
        """성공 시 액션 섹션 생성"""
        group = QGroupBox("✅ Step 2: 찾으면 어떻게 할까요?")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #4CAF50;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        group_layout = QVBoxLayout()
        
        # 액션 선택
        self.success_action_combo = QComboBox()
        self.success_action_combo.addItems([
            "🖱️ 클릭하기",
            "🖱️🖱️ 더블클릭하기",
            "⌨️ 텍스트 입력하기",
            "📋 위치를 변수에 저장",
            "➡️ 계속 진행 (확인만)",
            "⏹️ 매크로 중지"
        ])
        group_layout.addWidget(self.success_action_combo)
        
        # 액션별 추가 설정
        self.success_stack = QStackedWidget()
        
        # 클릭 설정 (빈 위젯)
        self.success_stack.addWidget(QWidget())
        
        # 더블클릭 설정 (빈 위젯)
        self.success_stack.addWidget(QWidget())
        
        # 텍스트 입력 설정
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        self.input_text_edit = QLineEdit()
        self.input_text_edit.setPlaceholderText("입력할 텍스트... ({{변수}} 사용 가능)")
        text_layout.addWidget(self.input_text_edit)
        self.success_stack.addWidget(text_widget)
        
        # 변수 저장 설정
        var_widget = QWidget()
        var_layout = QVBoxLayout(var_widget)
        self.save_var_edit = QLineEdit()
        self.save_var_edit.setPlaceholderText("저장할 변수명 (예: found_position)")
        var_layout.addWidget(self.save_var_edit)
        self.success_stack.addWidget(var_widget)
        
        # 나머지는 빈 위젯
        self.success_stack.addWidget(QWidget())  # 계속 진행
        self.success_stack.addWidget(QWidget())  # 중지
        
        self.success_action_combo.currentIndexChanged.connect(self.success_stack.setCurrentIndex)
        
        group_layout.addWidget(self.success_stack)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
    def create_failure_action_section(self, layout):
        """실패 시 액션 섹션 생성"""
        group = QGroupBox("❌ Step 3: 못 찾으면 어떻게 할까요?")
        group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                border: 2px solid #F44336;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
        """)
        
        group_layout = QVBoxLayout()
        
        # 액션 선택
        self.failure_action_combo = QComboBox()
        self.failure_action_combo.addItems([
            "➡️ 계속 진행",
            "⏹️ 매크로 중지",
            "🔄 다시 시도 (최대 N회)",
            "⏭️ 현재 엑셀 행 건너뛰기",
            "📢 경고 메시지 표시 후 계속",
            "⏸️ 대기 후 계속"
        ])
        group_layout.addWidget(self.failure_action_combo)
        
        # 액션별 추가 설정
        self.failure_stack = QStackedWidget()
        
        # 계속 진행 (빈 위젯)
        self.failure_stack.addWidget(QWidget())
        
        # 중지 (빈 위젯)
        self.failure_stack.addWidget(QWidget())
        
        # 재시도 설정
        retry_widget = QWidget()
        retry_layout = QHBoxLayout(retry_widget)
        retry_layout.addWidget(QLabel("최대 재시도 횟수:"))
        self.retry_count_spin = QSpinBox()
        self.retry_count_spin.setRange(1, 10)
        self.retry_count_spin.setValue(3)
        retry_layout.addWidget(self.retry_count_spin)
        retry_layout.addWidget(QLabel("회"))
        retry_layout.addStretch()
        self.failure_stack.addWidget(retry_widget)
        
        # 엑셀 행 건너뛰기 (빈 위젯)
        self.failure_stack.addWidget(QWidget())
        
        # 경고 메시지 설정
        alert_widget = QWidget()
        alert_layout = QVBoxLayout(alert_widget)
        self.alert_text_edit = QLineEdit()
        self.alert_text_edit.setPlaceholderText("표시할 경고 메시지...")
        alert_layout.addWidget(self.alert_text_edit)
        self.failure_stack.addWidget(alert_widget)
        
        # 대기 설정
        wait_widget = QWidget()
        wait_layout = QHBoxLayout(wait_widget)
        wait_layout.addWidget(QLabel("대기 시간:"))
        self.wait_time_spin = QSpinBox()
        self.wait_time_spin.setRange(1, 60)
        self.wait_time_spin.setValue(5)
        wait_layout.addWidget(self.wait_time_spin)
        wait_layout.addWidget(QLabel("초"))
        wait_layout.addStretch()
        self.failure_stack.addWidget(wait_widget)
        
        self.failure_action_combo.currentIndexChanged.connect(self.failure_stack.setCurrentIndex)
        
        group_layout.addWidget(self.failure_stack)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
    def create_bottom_buttons(self, layout):
        """하단 버튼 생성"""
        btn_layout = QHBoxLayout()
        
        # 테스트 버튼
        test_btn = QPushButton("🧪 지금 테스트")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        test_btn.clicked.connect(self.test_search)
        
        btn_layout.addWidget(test_btn)
        btn_layout.addStretch()
        
        layout.addLayout(btn_layout)
        
    def browse_image(self):
        """이미지 파일 선택"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "이미지 선택", "", 
            "이미지 파일 (*.png *.jpg *.jpeg *.bmp);;모든 파일 (*.*)"
        )
        if file_path:
            self.image_path_edit.setText(file_path)
            
    def capture_screen(self):
        """화면 캡처 (구현 필요)"""
        # TODO: 화면 캡처 기능 구현
        pass
        
    def test_search(self):
        """검색 테스트 (구현 필요)"""
        # TODO: 실제 검색 테스트 구현
        pass
        
    def update_variable_completer(self):
        """변수 자동완성 업데이트"""
        # TODO: QCompleter 추가
        pass
        
    def get_configuration(self) -> Dict[str, Any]:
        """현재 설정을 딕셔너리로 반환"""
        config = {
            "search_type": "image" if self.image_radio.isChecked() else "text",
            "search_target": "",
            "search_options": {},
            "success_action": "",
            "success_params": {},
            "failure_action": "",
            "failure_params": {}
        }
        
        # 검색 설정
        if config["search_type"] == "image":
            config["search_target"] = self.image_path_edit.text()
            config["search_options"] = {
                "confidence": self.accuracy_slider.value() / 100.0,
                "use_region": self.search_region_check.isChecked()
            }
        else:
            config["search_target"] = self.search_text_edit.text()
            config["search_options"] = {
                "exact_match": self.exact_match_check.isChecked(),
                "use_region": self.text_region_check.isChecked()
            }
            
        # 성공 액션
        success_actions = ["click", "double_click", "type", "save_position", "continue", "stop"]
        config["success_action"] = success_actions[self.success_action_combo.currentIndex()]
        
        if config["success_action"] == "type":
            config["success_params"]["text"] = self.input_text_edit.text()
        elif config["success_action"] == "save_position":
            config["success_params"]["variable"] = self.save_var_edit.text()
            
        # 실패 액션
        failure_actions = ["continue", "stop", "retry", "skip_row", "alert", "wait"]
        config["failure_action"] = failure_actions[self.failure_action_combo.currentIndex()]
        
        if config["failure_action"] == "retry":
            config["failure_params"]["max_retries"] = self.retry_count_spin.value()
        elif config["failure_action"] == "alert":
            config["failure_params"]["message"] = self.alert_text_edit.text()
        elif config["failure_action"] == "wait":
            config["failure_params"]["seconds"] = self.wait_time_spin.value()
            
        return config
        
    def set_configuration(self, config: Dict[str, Any]):
        """설정 로드"""
        # TODO: 설정 로드 구현
        pass


class MacroStepSearchAndActionWidget(QFrame):
    """매크로 에디터에 표시되는 SearchAndAction 스텝 위젯"""
    
    # 시그널
    editRequested = pyqtSignal()
    deleteRequested = pyqtSignal()
    
    def __init__(self, step_data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.step_data = step_data
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        self.setFrameStyle(QFrame.Box)
        self.setStyleSheet("""
            QFrame {
                background-color: #FFF3E0;
                border: 2px solid #FF9800;
                border-radius: 8px;
                margin: 2px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        
        # 헤더
        header_layout = QHBoxLayout()
        
        # 아이콘과 제목
        title_label = QLabel("🔍 검색하고 실행하기")
        title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # 편집/삭제 버튼
        edit_btn = QPushButton("✏️")
        edit_btn.setToolTip("편집")
        edit_btn.setMaximumSize(30, 30)
        edit_btn.clicked.connect(self.editRequested.emit)
        
        delete_btn = QPushButton("🗑️")
        delete_btn.setToolTip("삭제")
        delete_btn.setMaximumSize(30, 30)
        delete_btn.clicked.connect(self.deleteRequested.emit)
        
        header_layout.addWidget(edit_btn)
        header_layout.addWidget(delete_btn)
        
        layout.addLayout(header_layout)
        
        # 요약 정보
        summary = self.create_summary()
        summary_label = QLabel(summary)
        summary_label.setWordWrap(True)
        summary_label.setStyleSheet("color: #666; font-size: 12px; padding: 5px 0;")
        layout.addWidget(summary_label)
        
    def create_summary(self) -> str:
        """스텝 요약 생성"""
        search_type = self.step_data.get("search_type", "")
        search_target = self.step_data.get("search_target", "")
        success_action = self.step_data.get("success_action", "")
        failure_action = self.step_data.get("failure_action", "")
        
        # 검색 대상
        if search_type == "image":
            search_desc = f"이미지 '{search_target}'"
        else:
            search_desc = f"텍스트 '{search_target}'"
            
        # 성공 액션
        success_map = {
            "click": "클릭",
            "double_click": "더블클릭",
            "type": "텍스트 입력",
            "save_position": "위치 저장",
            "continue": "계속",
            "stop": "중지"
        }
        success_desc = success_map.get(success_action, success_action)
        
        # 실패 액션
        failure_map = {
            "continue": "계속 진행",
            "stop": "중지",
            "retry": "재시도",
            "skip_row": "행 건너뛰기",
            "alert": "경고 표시",
            "wait": "대기"
        }
        failure_desc = failure_map.get(failure_action, failure_action)
        
        return f"{search_desc} 검색 → 찾으면 {success_desc} / 못 찾으면 {failure_desc}"
        
    def mouseDoubleClickEvent(self, event):
        """더블클릭 시 편집"""
        self.editRequested.emit()