"""
통합 검색 및 조건부 실행 다이얼로그
사용자 편의성을 최대한 고려한 직관적인 UI
"""

from typing import Optional, Dict, Any, List
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QComboBox, QStackedWidget, QGroupBox, QRadioButton,
    QButtonGroup, QLineEdit, QSpinBox, QDoubleSpinBox,
    QCheckBox, QTextEdit, QTabWidget, QWidget, QListWidget,
    QListWidgetItem, QFileDialog, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QIcon, QFont

class SearchAndActionDialog(QDialog):
    """통합 검색 및 조건부 실행 설정 다이얼로그"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("🔍 검색하고 실행하기")
        self.setModal(True)
        self.setMinimumSize(800, 600)
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        # 상단 제목과 설명
        header = self._create_header()
        layout.addWidget(header)
        
        # 메인 컨텐츠 - 3단계 구조
        main_content = QVBoxLayout()
        
        # Step 1: 무엇을 찾을까요?
        step1 = self._create_search_section()
        main_content.addWidget(step1)
        
        # Step 2: 찾으면 어떻게 할까요?
        step2 = self._create_success_action_section()
        main_content.addWidget(step2)
        
        # Step 3: 못 찾으면 어떻게 할까요?
        step3 = self._create_failure_action_section()
        main_content.addWidget(step3)
        
        layout.addLayout(main_content)
        
        # 하단 버튼
        buttons = self._create_buttons()
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
    def _create_header(self) -> QWidget:
        """상단 헤더 생성"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 제목
        title = QLabel("🔍 검색하고 실행하기")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        
        # 설명
        desc = QLabel("화면에서 이미지나 텍스트를 찾고, 찾은 결과에 따라 다른 동작을 실행합니다.")
        desc.setWordWrap(True)
        desc.setStyleSheet("color: #666; padding: 5px;")
        
        layout.addWidget(title)
        layout.addWidget(desc)
        
        widget.setLayout(layout)
        return widget
        
    def _create_search_section(self) -> QGroupBox:
        """Step 1: 검색 설정 섹션"""
        group = QGroupBox("📌 Step 1: 무엇을 찾을까요?")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #2196F3;
            }
        """)
        
        layout = QVBoxLayout()
        
        # 검색 타입 선택 (큰 버튼으로)
        type_layout = QHBoxLayout()
        
        self.search_type_group = QButtonGroup()
        
        # 이미지 검색 버튼
        image_btn = QPushButton("🖼️ 이미지 찾기")
        image_btn.setCheckable(True)
        image_btn.setChecked(True)
        image_btn.setMinimumHeight(60)
        image_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                border: 2px solid #ddd;
                border-radius: 8px;
                background-color: white;
            }
            QPushButton:checked {
                background-color: #e3f2fd;
                border-color: #2196F3;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """)
        self.search_type_group.addButton(image_btn, 0)
        
        # 텍스트 검색 버튼
        text_btn = QPushButton("📝 텍스트 찾기")
        text_btn.setCheckable(True)
        text_btn.setMinimumHeight(60)
        text_btn.setStyleSheet(image_btn.styleSheet())
        self.search_type_group.addButton(text_btn, 1)
        
        type_layout.addWidget(image_btn)
        type_layout.addWidget(text_btn)
        layout.addLayout(type_layout)
        
        # 검색 설정 스택 위젯
        self.search_stack = QStackedWidget()
        
        # 이미지 검색 설정
        image_widget = self._create_image_search_widget()
        self.search_stack.addWidget(image_widget)
        
        # 텍스트 검색 설정
        text_widget = self._create_text_search_widget()
        self.search_stack.addWidget(text_widget)
        
        layout.addWidget(self.search_stack)
        
        # 검색 타입 변경 시 스택 전환
        self.search_type_group.buttonClicked.connect(
            lambda btn: self.search_stack.setCurrentIndex(self.search_type_group.id(btn))
        )
        
        group.setLayout(layout)
        return group
        
    def _create_image_search_widget(self) -> QWidget:
        """이미지 검색 설정 위젯"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 이미지 선택
        img_layout = QHBoxLayout()
        img_layout.addWidget(QLabel("이미지 파일:"))
        self.image_path_edit = QLineEdit()
        self.image_path_edit.setPlaceholderText("클릭하여 이미지 선택...")
        img_layout.addWidget(self.image_path_edit)
        
        browse_btn = QPushButton("📁 찾아보기")
        browse_btn.clicked.connect(self._browse_image)
        img_layout.addWidget(browse_btn)
        
        capture_btn = QPushButton("📸 화면 캡처")
        capture_btn.clicked.connect(self._capture_screen)
        img_layout.addWidget(capture_btn)
        
        layout.addLayout(img_layout)
        
        # 이미지 미리보기
        self.image_preview = QLabel()
        self.image_preview.setMinimumHeight(100)
        self.image_preview.setMaximumHeight(200)
        self.image_preview.setStyleSheet("""
            QLabel {
                border: 2px dashed #ddd;
                border-radius: 8px;
                background-color: #f9f9f9;
            }
        """)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setText("이미지가 여기에 표시됩니다")
        layout.addWidget(self.image_preview)
        
        # 정확도 설정
        accuracy_layout = QHBoxLayout()
        accuracy_layout.addWidget(QLabel("일치 정확도:"))
        self.confidence_slider = QDoubleSpinBox()
        self.confidence_slider.setRange(0.1, 1.0)
        self.confidence_slider.setSingleStep(0.1)
        self.confidence_slider.setValue(0.8)
        self.confidence_slider.setSuffix(" (80%)")
        self.confidence_slider.valueChanged.connect(
            lambda v: self.confidence_slider.setSuffix(f" ({int(v*100)}%)")
        )
        accuracy_layout.addWidget(self.confidence_slider)
        accuracy_layout.addStretch()
        layout.addLayout(accuracy_layout)
        
        # 검색 영역 설정
        self.search_area_check = QCheckBox("특정 영역에서만 검색")
        self.search_area_btn = QPushButton("🔲 영역 선택")
        self.search_area_btn.setEnabled(False)
        self.search_area_check.toggled.connect(self.search_area_btn.setEnabled)
        
        area_layout = QHBoxLayout()
        area_layout.addWidget(self.search_area_check)
        area_layout.addWidget(self.search_area_btn)
        area_layout.addStretch()
        layout.addLayout(area_layout)
        
        widget.setLayout(layout)
        return widget
        
    def _create_text_search_widget(self) -> QWidget:
        """텍스트 검색 설정 위젯"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # 검색할 텍스트
        text_layout = QVBoxLayout()
        text_layout.addWidget(QLabel("찾을 텍스트:"))
        self.search_text_edit = QLineEdit()
        self.search_text_edit.setPlaceholderText("검색할 텍스트를 입력하세요...")
        text_layout.addWidget(self.search_text_edit)
        
        # 변수 사용 힌트
        hint = QLabel("💡 팁: {{변수명}} 형식으로 Excel 데이터를 사용할 수 있습니다")
        hint.setStyleSheet("color: #666; font-size: 12px; padding: 5px;")
        text_layout.addWidget(hint)
        
        layout.addLayout(text_layout)
        
        # 검색 옵션
        self.exact_match_check = QCheckBox("정확히 일치하는 텍스트만 찾기")
        layout.addWidget(self.exact_match_check)
        
        # 검색 영역 설정
        self.text_search_area_check = QCheckBox("특정 영역에서만 검색")
        self.text_search_area_btn = QPushButton("🔲 영역 선택")
        self.text_search_area_btn.setEnabled(False)
        self.text_search_area_check.toggled.connect(self.text_search_area_btn.setEnabled)
        
        area_layout = QHBoxLayout()
        area_layout.addWidget(self.text_search_area_check)
        area_layout.addWidget(self.text_search_area_btn)
        area_layout.addStretch()
        layout.addLayout(area_layout)
        
        widget.setLayout(layout)
        return widget
        
    def _create_success_action_section(self) -> QGroupBox:
        """Step 2: 성공 시 액션 설정"""
        group = QGroupBox("✅ Step 2: 찾으면 어떻게 할까요?")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #4CAF50;
            }
        """)
        
        layout = QVBoxLayout()
        
        # 액션 선택 콤보박스
        action_layout = QHBoxLayout()
        action_layout.addWidget(QLabel("동작:"))
        
        self.success_action_combo = QComboBox()
        self.success_action_combo.addItems([
            "🖱️ 클릭하기",
            "🖱️🖱️ 더블클릭하기",
            "⌨️ 텍스트 입력하기",
            "🔄 다른 매크로 실행",
            "⏸️ 아무것도 안함 (확인만)",
            "📋 위치를 변수에 저장"
        ])
        self.success_action_combo.setMinimumHeight(35)
        action_layout.addWidget(self.success_action_combo)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        # 액션별 상세 설정 스택
        self.success_detail_stack = QStackedWidget()
        
        # 클릭 설정
        click_widget = QWidget()
        click_layout = QVBoxLayout()
        self.click_offset_check = QCheckBox("클릭 위치 조정")
        offset_layout = QHBoxLayout()
        offset_layout.addWidget(QLabel("X:"))
        self.offset_x = QSpinBox()
        self.offset_x.setRange(-500, 500)
        offset_layout.addWidget(self.offset_x)
        offset_layout.addWidget(QLabel("Y:"))
        self.offset_y = QSpinBox()
        self.offset_y.setRange(-500, 500)
        offset_layout.addWidget(self.offset_y)
        offset_layout.addStretch()
        click_layout.addWidget(self.click_offset_check)
        click_layout.addLayout(offset_layout)
        click_widget.setLayout(click_layout)
        
        # 텍스트 입력 설정
        type_widget = QWidget()
        type_layout = QVBoxLayout()
        type_layout.addWidget(QLabel("입력할 텍스트:"))
        self.type_text_edit = QLineEdit()
        self.type_text_edit.setPlaceholderText("입력할 텍스트 또는 {{변수명}}")
        type_layout.addWidget(self.type_text_edit)
        type_widget.setLayout(type_layout)
        
        self.success_detail_stack.addWidget(click_widget)  # 클릭
        self.success_detail_stack.addWidget(QWidget())     # 더블클릭
        self.success_detail_stack.addWidget(type_widget)   # 텍스트 입력
        self.success_detail_stack.addWidget(QWidget())     # 매크로 실행
        self.success_detail_stack.addWidget(QWidget())     # 아무것도 안함
        self.success_detail_stack.addWidget(QWidget())     # 변수 저장
        
        layout.addWidget(self.success_detail_stack)
        
        # 액션 변경 시 상세 설정 전환
        self.success_action_combo.currentIndexChanged.connect(
            self.success_detail_stack.setCurrentIndex
        )
        
        group.setLayout(layout)
        return group
        
    def _create_failure_action_section(self) -> QGroupBox:
        """Step 3: 실패 시 액션 설정"""
        group = QGroupBox("❌ Step 3: 못 찾으면 어떻게 할까요?")
        group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                color: #F44336;
            }
        """)
        
        layout = QVBoxLayout()
        
        # 액션 선택
        action_layout = QHBoxLayout()
        action_layout.addWidget(QLabel("동작:"))
        
        self.failure_action_combo = QComboBox()
        self.failure_action_combo.addItems([
            "➡️ 계속 진행",
            "⏹️ 매크로 중지",
            "🔄 다시 시도 (최대 3회)",
            "⏭️ 다른 검색 조건으로 시도",
            "📢 경고 메시지 표시",
            "🔀 다른 매크로 실행"
        ])
        self.failure_action_combo.setMinimumHeight(35)
        action_layout.addWidget(self.failure_action_combo)
        action_layout.addStretch()
        
        layout.addLayout(action_layout)
        
        # 실패 시 대기 시간
        wait_layout = QHBoxLayout()
        self.failure_wait_check = QCheckBox("실패 시 대기")
        self.failure_wait_spin = QSpinBox()
        self.failure_wait_spin.setRange(1, 60)
        self.failure_wait_spin.setValue(3)
        self.failure_wait_spin.setSuffix(" 초")
        self.failure_wait_spin.setEnabled(False)
        self.failure_wait_check.toggled.connect(self.failure_wait_spin.setEnabled)
        
        wait_layout.addWidget(self.failure_wait_check)
        wait_layout.addWidget(self.failure_wait_spin)
        wait_layout.addStretch()
        layout.addLayout(wait_layout)
        
        group.setLayout(layout)
        return group
        
    def _create_buttons(self) -> QWidget:
        """하단 버튼들"""
        widget = QWidget()
        layout = QHBoxLayout()
        
        # 테스트 버튼
        test_btn = QPushButton("🧪 지금 테스트")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 20px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        
        # 저장/취소 버튼
        save_btn = QPushButton("💾 저장")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 30px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        cancel_btn = QPushButton("취소")
        cancel_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px;
                padding: 10px 30px;
            }
        """)
        
        layout.addWidget(test_btn)
        layout.addStretch()
        layout.addWidget(cancel_btn)
        layout.addWidget(save_btn)
        
        save_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        
        widget.setLayout(layout)
        return widget
        
    def _browse_image(self):
        """이미지 파일 선택"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "이미지 파일 선택",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)"
        )
        if filename:
            self.image_path_edit.setText(filename)
            # 미리보기 표시
            pixmap = QPixmap(filename)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.image_preview.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_preview.setPixmap(scaled)
                
    def _capture_screen(self):
        """화면 캡처 (구현 필요)"""
        # TODO: 화면 캡처 구현
        pass


# 테스트용 실행 코드
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = SearchAndActionDialog()
    dialog.show()
    sys.exit(app.exec_())