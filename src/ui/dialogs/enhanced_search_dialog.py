"""
향상된 검색 다이얼로그 - 기존 이미지/텍스트 검색에 성공/실패 액션 추가
"""

from typing import Optional, Dict, Any, List
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QRadioButton, QLineEdit, QComboBox, QSpinBox,
    QCheckBox, QTextEdit, QFileDialog, QListWidget, QListWidgetItem,
    QTabWidget, QWidget, QSlider, QFrame, QButtonGroup, 
    QDialogButtonBox, QCompleter, QStackedWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette, QPixmap

class EnhancedSearchDialog(QDialog):
    """기존 이미지/텍스트 검색에 조건부 액션을 추가한 다이얼로그"""
    
    def __init__(self, parent=None, search_type="image", excel_columns=None):
        super().__init__(parent)
        self.search_type = search_type  # "image" or "text"
        self.excel_columns = excel_columns or []
        self.region = None
        
        self.setWindowTitle(f"{'🖼️ 이미지' if search_type == 'image' else '📝 텍스트'} 검색 설정")
        self.setMinimumSize(650, 600)
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # 헤더
        header_text = "이미지를 검색하고 액션 실행" if self.search_type == "image" else "텍스트를 검색하고 액션 실행"
        header = QLabel(f"🔍 {header_text}")
        header.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 10px;
                background-color: #ecf0f1;
                border-radius: 5px;
            }
        """)
        layout.addWidget(header)
        
        # 메인 탭
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                background-color: white;
            }
            QTabBar::tab {
                padding: 8px 20px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 3px solid #3498db;
            }
        """)
        
        # 탭 1: 검색 설정
        search_tab = self.create_search_tab()
        self.tab_widget.addTab(search_tab, "🔍 검색 설정")
        
        # 탭 2: 액션 설정
        action_tab = self.create_action_tab()
        self.tab_widget.addTab(action_tab, "⚡ 액션 설정")
        
        # 탭 3: 요약
        summary_tab = self.create_summary_tab()
        self.tab_widget.addTab(summary_tab, "📋 설정 요약")
        
        layout.addWidget(self.tab_widget)
        
        # 하단 버튼
        self.create_bottom_buttons(layout)
        
        # 탭 변경 시 요약 업데이트
        self.tab_widget.currentChanged.connect(self.update_summary)
        
    def create_search_tab(self):
        """검색 설정 탭"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        if self.search_type == "image":
            # 이미지 검색 설정
            self.create_image_search_settings(layout)
        else:
            # 텍스트 검색 설정
            self.create_text_search_settings(layout)
            
        # 공통 설정
        common_group = QGroupBox("🔧 검색 옵션")
        common_layout = QVBoxLayout()
        
        # 검색 영역
        self.use_region_check = QCheckBox("특정 영역에서만 검색")
        self.region_btn = QPushButton("🎯 영역 선택")
        self.region_btn.setEnabled(False)
        self.use_region_check.toggled.connect(self.region_btn.setEnabled)
        
        region_layout = QHBoxLayout()
        region_layout.addWidget(self.use_region_check)
        region_layout.addWidget(self.region_btn)
        region_layout.addStretch()
        common_layout.addLayout(region_layout)
        
        # 타임아웃 설정
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("검색 타임아웃:"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 30)
        self.timeout_spin.setValue(5)
        self.timeout_spin.setSuffix("초")
        timeout_layout.addWidget(self.timeout_spin)
        timeout_layout.addStretch()
        common_layout.addLayout(timeout_layout)
        
        common_group.setLayout(common_layout)
        layout.addWidget(common_group)
        
        layout.addStretch()
        
        return widget
        
    def create_image_search_settings(self, layout):
        """이미지 검색 설정"""
        group = QGroupBox("🖼️ 이미지 선택")
        group_layout = QVBoxLayout()
        
        # 이미지 경로
        path_layout = QHBoxLayout()
        self.image_path_edit = QLineEdit()
        self.image_path_edit.setPlaceholderText("이미지 파일을 선택하세요...")
        
        browse_btn = QPushButton("📁 찾아보기")
        browse_btn.clicked.connect(self.browse_image)
        
        capture_btn = QPushButton("📸 화면 캡처")
        capture_btn.clicked.connect(self.capture_screen)
        
        path_layout.addWidget(self.image_path_edit, 3)
        path_layout.addWidget(browse_btn, 1)
        path_layout.addWidget(capture_btn, 1)
        
        group_layout.addLayout(path_layout)
        
        # 이미지 미리보기
        self.preview_label = QLabel("이미지 미리보기")
        self.preview_label.setMinimumHeight(100)
        self.preview_label.setMaximumHeight(200)
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #bdc3c7;
                background-color: #ecf0f1;
                border-radius: 5px;
            }
        """)
        group_layout.addWidget(self.preview_label)
        
        # 정확도 설정
        accuracy_layout = QHBoxLayout()
        accuracy_layout.addWidget(QLabel("일치율:"))
        
        self.accuracy_slider = QSlider(Qt.Horizontal)
        self.accuracy_slider.setRange(50, 100)
        self.accuracy_slider.setValue(80)
        self.accuracy_slider.setTickPosition(QSlider.TicksBelow)
        self.accuracy_slider.setTickInterval(10)
        
        self.accuracy_label = QLabel("80%")
        self.accuracy_label.setMinimumWidth(40)
        self.accuracy_slider.valueChanged.connect(
            lambda v: self.accuracy_label.setText(f"{v}%")
        )
        
        accuracy_layout.addWidget(self.accuracy_slider)
        accuracy_layout.addWidget(self.accuracy_label)
        
        group_layout.addLayout(accuracy_layout)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
    def create_text_search_settings(self, layout):
        """텍스트 검색 설정"""
        group = QGroupBox("📝 텍스트 입력")
        group_layout = QVBoxLayout()
        
        # 검색 텍스트
        self.search_text_edit = QLineEdit()
        self.search_text_edit.setPlaceholderText("검색할 텍스트를 입력하세요...")
        
        # 변수 자동완성
        if self.excel_columns:
            completer = QCompleter([f"{{{{{col}}}}}" for col in self.excel_columns])
            self.search_text_edit.setCompleter(completer)
            
        group_layout.addWidget(self.search_text_edit)
        
        # 변수 힌트
        if self.excel_columns:
            hint_text = "💡 사용 가능한 변수: "
            hint_text += ", ".join([f"{{{{{col}}}}}" for col in self.excel_columns[:5]])
            if len(self.excel_columns) > 5:
                hint_text += " ..."
                
            hint_label = QLabel(hint_text)
            hint_label.setWordWrap(True)
            hint_label.setStyleSheet("color: #7f8c8d; font-size: 12px; padding: 5px;")
            group_layout.addWidget(hint_label)
        
        # 검색 옵션
        self.exact_match_check = QCheckBox("정확히 일치하는 텍스트만 찾기")
        self.case_sensitive_check = QCheckBox("대소문자 구분")
        
        group_layout.addWidget(self.exact_match_check)
        group_layout.addWidget(self.case_sensitive_check)
        
        group.setLayout(group_layout)
        layout.addWidget(group)
        
    def create_action_tab(self):
        """액션 설정 탭"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # 성공 시 액션
        success_group = QGroupBox("✅ 찾았을 때 실행할 액션")
        success_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #27ae60;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                color: #27ae60;
            }
        """)
        
        success_layout = QVBoxLayout()
        
        # 액션 선택
        self.success_action_combo = QComboBox()
        self.success_action_combo.addItems([
            "🖱️ 클릭",
            "🖱️🖱️ 더블클릭",
            "🖱️ 우클릭",
            "⌨️ 텍스트 입력",
            "⌨️ 단축키 입력",
            "📋 위치 저장",
            "📸 스크린샷",
            "✔️ 확인만 (다음 진행)"
        ])
        success_layout.addWidget(self.success_action_combo)
        
        # 액션별 추가 설정
        self.success_stack = QStackedWidget()
        
        # 클릭 옵션
        click_widget = QWidget()
        click_layout = QVBoxLayout(click_widget)
        self.click_offset_check = QCheckBox("클릭 위치 조정")
        self.offset_x_spin = QSpinBox()
        self.offset_x_spin.setRange(-100, 100)
        self.offset_x_spin.setPrefix("X: ")
        self.offset_y_spin = QSpinBox()
        self.offset_y_spin.setRange(-100, 100)
        self.offset_y_spin.setPrefix("Y: ")
        
        offset_layout = QHBoxLayout()
        offset_layout.addWidget(self.click_offset_check)
        offset_layout.addWidget(self.offset_x_spin)
        offset_layout.addWidget(self.offset_y_spin)
        offset_layout.addStretch()
        
        self.click_offset_check.toggled.connect(self.offset_x_spin.setEnabled)
        self.click_offset_check.toggled.connect(self.offset_y_spin.setEnabled)
        self.offset_x_spin.setEnabled(False)
        self.offset_y_spin.setEnabled(False)
        
        click_layout.addLayout(offset_layout)
        self.success_stack.addWidget(click_widget)
        
        # 더블클릭 (클릭과 동일)
        self.success_stack.addWidget(QWidget())
        
        # 우클릭 (클릭과 동일)
        self.success_stack.addWidget(QWidget())
        
        # 텍스트 입력
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        self.input_text_edit = QLineEdit()
        self.input_text_edit.setPlaceholderText("입력할 텍스트 ({{변수}} 사용 가능)")
        text_layout.addWidget(QLabel("입력할 텍스트:"))
        text_layout.addWidget(self.input_text_edit)
        self.success_stack.addWidget(text_widget)
        
        # 단축키 입력
        hotkey_widget = QWidget()
        hotkey_layout = QVBoxLayout(hotkey_widget)
        self.hotkey_edit = QLineEdit()
        self.hotkey_edit.setPlaceholderText("예: ctrl+c, alt+tab")
        hotkey_layout.addWidget(QLabel("단축키:"))
        hotkey_layout.addWidget(self.hotkey_edit)
        self.success_stack.addWidget(hotkey_widget)
        
        # 위치 저장
        save_widget = QWidget()
        save_layout = QVBoxLayout(save_widget)
        self.save_var_edit = QLineEdit()
        self.save_var_edit.setPlaceholderText("변수명 (예: button_position)")
        save_layout.addWidget(QLabel("저장할 변수명:"))
        save_layout.addWidget(self.save_var_edit)
        self.success_stack.addWidget(save_widget)
        
        # 나머지는 빈 위젯
        self.success_stack.addWidget(QWidget())  # 스크린샷
        self.success_stack.addWidget(QWidget())  # 확인만
        
        self.success_action_combo.currentIndexChanged.connect(self.success_stack.setCurrentIndex)
        
        success_layout.addWidget(self.success_stack)
        
        # 성공 후 대기
        wait_layout = QHBoxLayout()
        self.success_wait_check = QCheckBox("액션 후 대기")
        self.success_wait_spin = QSpinBox()
        self.success_wait_spin.setRange(0, 10)
        self.success_wait_spin.setValue(1)
        self.success_wait_spin.setSuffix("초")
        self.success_wait_spin.setEnabled(False)
        
        self.success_wait_check.toggled.connect(self.success_wait_spin.setEnabled)
        
        wait_layout.addWidget(self.success_wait_check)
        wait_layout.addWidget(self.success_wait_spin)
        wait_layout.addStretch()
        
        success_layout.addLayout(wait_layout)
        
        success_group.setLayout(success_layout)
        layout.addWidget(success_group)
        
        # 실패 시 액션
        failure_group = QGroupBox("❌ 못 찾았을 때 실행할 액션")
        failure_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #e74c3c;
                border-radius: 5px;
                margin-top: 10px;
            }
            QGroupBox::title {
                color: #e74c3c;
            }
        """)
        
        failure_layout = QVBoxLayout()
        
        self.failure_action_combo = QComboBox()
        self.failure_action_combo.addItems([
            "➡️ 다음으로 진행",
            "⏹️ 매크로 중지",
            "🔄 재시도",
            "⏭️ 다음 엑셀 행으로",
            "📢 경고 표시 후 계속",
            "⏸️ 대기 후 계속",
            "🔀 대체 검색"
        ])
        failure_layout.addWidget(self.failure_action_combo)
        
        # 실패 액션별 설정
        self.failure_stack = QStackedWidget()
        
        # 다음으로 진행 (빈 위젯)
        self.failure_stack.addWidget(QWidget())
        
        # 매크로 중지 (빈 위젯)
        self.failure_stack.addWidget(QWidget())
        
        # 재시도
        retry_widget = QWidget()
        retry_layout = QVBoxLayout(retry_widget)
        retry_options = QHBoxLayout()
        retry_options.addWidget(QLabel("재시도 횟수:"))
        self.retry_count_spin = QSpinBox()
        self.retry_count_spin.setRange(1, 10)
        self.retry_count_spin.setValue(3)
        retry_options.addWidget(self.retry_count_spin)
        retry_options.addWidget(QLabel("회"))
        
        retry_options.addWidget(QLabel("  간격:"))
        self.retry_interval_spin = QSpinBox()
        self.retry_interval_spin.setRange(1, 10)
        self.retry_interval_spin.setValue(1)
        self.retry_interval_spin.setSuffix("초")
        retry_options.addWidget(self.retry_interval_spin)
        retry_options.addStretch()
        
        retry_layout.addLayout(retry_options)
        self.failure_stack.addWidget(retry_widget)
        
        # 다음 엑셀 행으로 (빈 위젯)
        self.failure_stack.addWidget(QWidget())
        
        # 경고 표시
        alert_widget = QWidget()
        alert_layout = QVBoxLayout(alert_widget)
        self.alert_text_edit = QLineEdit()
        self.alert_text_edit.setPlaceholderText("경고 메시지...")
        self.alert_text_edit.setText(f"{'이미지' if self.search_type == 'image' else '텍스트'}를 찾을 수 없습니다")
        alert_layout.addWidget(QLabel("경고 메시지:"))
        alert_layout.addWidget(self.alert_text_edit)
        self.failure_stack.addWidget(alert_widget)
        
        # 대기 후 계속
        wait_widget = QWidget()
        wait_layout = QVBoxLayout(wait_widget)
        wait_options = QHBoxLayout()
        wait_options.addWidget(QLabel("대기 시간:"))
        self.wait_time_spin = QSpinBox()
        self.wait_time_spin.setRange(1, 30)
        self.wait_time_spin.setValue(3)
        self.wait_time_spin.setSuffix("초")
        wait_options.addWidget(self.wait_time_spin)
        wait_options.addStretch()
        wait_layout.addLayout(wait_options)
        self.failure_stack.addWidget(wait_widget)
        
        # 대체 검색
        alt_widget = QWidget()
        alt_layout = QVBoxLayout(alt_widget)
        if self.search_type == "image":
            self.alt_image_edit = QLineEdit()
            self.alt_image_edit.setPlaceholderText("대체 이미지 경로...")
            alt_browse_btn = QPushButton("📁 찾아보기")
            alt_path_layout = QHBoxLayout()
            alt_path_layout.addWidget(self.alt_image_edit)
            alt_path_layout.addWidget(alt_browse_btn)
            alt_layout.addWidget(QLabel("대체 이미지:"))
            alt_layout.addLayout(alt_path_layout)
        else:
            self.alt_text_edit = QLineEdit()
            self.alt_text_edit.setPlaceholderText("대체 검색 텍스트...")
            alt_layout.addWidget(QLabel("대체 텍스트:"))
            alt_layout.addWidget(self.alt_text_edit)
        self.failure_stack.addWidget(alt_widget)
        
        self.failure_action_combo.currentIndexChanged.connect(self.failure_stack.setCurrentIndex)
        
        failure_layout.addWidget(self.failure_stack)
        
        failure_group.setLayout(failure_layout)
        layout.addWidget(failure_group)
        
        layout.addStretch()
        
        return widget
        
    def create_summary_tab(self):
        """요약 탭"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 요약 텍스트
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 13px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 10px;
            }
        """)
        
        layout.addWidget(QLabel("📋 설정 요약"))
        layout.addWidget(self.summary_text)
        
        # 테스트 버튼
        test_btn = QPushButton("🧪 지금 테스트")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        test_btn.clicked.connect(self.test_search)
        
        layout.addWidget(test_btn)
        
        return widget
        
    def create_bottom_buttons(self, layout):
        """하단 버튼"""
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        buttons.button(QDialogButtonBox.Ok).setText("확인")
        buttons.button(QDialogButtonBox.Cancel).setText("취소")
        
        layout.addWidget(buttons)
        
    def browse_image(self):
        """이미지 파일 선택"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "이미지 선택", "",
            "이미지 파일 (*.png *.jpg *.jpeg *.bmp);;모든 파일 (*.*)"
        )
        if file_path:
            self.image_path_edit.setText(file_path)
            # 미리보기 업데이트
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                scaled = pixmap.scaled(
                    self.preview_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.preview_label.setPixmap(scaled)
                
    def capture_screen(self):
        """화면 캡처"""
        # TODO: 구현
        pass
        
    def test_search(self):
        """검색 테스트"""
        # TODO: 구현
        pass
        
    def update_summary(self):
        """요약 업데이트"""
        if self.tab_widget.currentIndex() != 2:  # 요약 탭이 아니면
            return
            
        summary = "=== 검색 및 액션 설정 요약 ===\n\n"
        
        # 검색 설정
        if self.search_type == "image":
            image_path = self.image_path_edit.text() if hasattr(self, 'image_path_edit') else ""
            accuracy = self.accuracy_slider.value() if hasattr(self, 'accuracy_slider') else 80
            summary += f"🖼️ 이미지 검색\n"
            summary += f"  • 파일: {image_path}\n"
            summary += f"  • 일치율: {accuracy}%\n"
        else:
            search_text = self.search_text_edit.text() if hasattr(self, 'search_text_edit') else ""
            exact = self.exact_match_check.isChecked() if hasattr(self, 'exact_match_check') else False
            summary += f"📝 텍스트 검색\n"
            summary += f"  • 검색어: {search_text}\n"
            summary += f"  • 정확히 일치: {'예' if exact else '아니오'}\n"
            
        if hasattr(self, 'use_region_check') and self.use_region_check.isChecked():
            summary += f"  • 특정 영역에서 검색\n"
            
        summary += f"\n"
        
        # 성공 액션
        if hasattr(self, 'success_action_combo'):
            success_action = self.success_action_combo.currentText()
            summary += f"✅ 찾았을 때:\n"
            summary += f"  • {success_action}\n"
            
            # 액션별 추가 정보
            if "텍스트 입력" in success_action and hasattr(self, 'input_text_edit'):
                text = self.input_text_edit.text()
                if text:
                    summary += f"    입력: {text}\n"
                    
        # 실패 액션
        if hasattr(self, 'failure_action_combo'):
            failure_action = self.failure_action_combo.currentText()
            summary += f"\n❌ 못 찾았을 때:\n"
            summary += f"  • {failure_action}\n"
            
            # 액션별 추가 정보
            if "재시도" in failure_action and hasattr(self, 'retry_count_spin'):
                count = self.retry_count_spin.value()
                interval = self.retry_interval_spin.value()
                summary += f"    {count}회 재시도 ({interval}초 간격)\n"
                
        self.summary_text.setPlainText(summary)
        
    def get_configuration(self) -> Dict[str, Any]:
        """설정값 반환"""
        config = {
            "search_type": self.search_type,
            "search_config": {},
            "success_action": {},
            "failure_action": {}
        }
        
        # 검색 설정
        if self.search_type == "image":
            config["search_config"] = {
                "image_path": self.image_path_edit.text(),
                "confidence": self.accuracy_slider.value() / 100.0,
                "use_region": self.use_region_check.isChecked(),
                "region": self.region
            }
        else:
            config["search_config"] = {
                "text": self.search_text_edit.text(),
                "exact_match": self.exact_match_check.isChecked(),
                "case_sensitive": self.case_sensitive_check.isChecked(),
                "use_region": self.use_region_check.isChecked(),
                "region": self.region
            }
            
        # 성공 액션
        success_actions = ["click", "double_click", "right_click", "type", "hotkey", 
                          "save_position", "screenshot", "continue"]
        config["success_action"]["type"] = success_actions[self.success_action_combo.currentIndex()]
        
        # 액션별 파라미터
        if config["success_action"]["type"] == "type":
            config["success_action"]["text"] = self.input_text_edit.text()
        elif config["success_action"]["type"] == "hotkey":
            config["success_action"]["keys"] = self.hotkey_edit.text()
        elif config["success_action"]["type"] == "save_position":
            config["success_action"]["variable"] = self.save_var_edit.text()
            
        if self.success_wait_check.isChecked():
            config["success_action"]["wait_after"] = self.success_wait_spin.value()
            
        # 실패 액션
        failure_actions = ["continue", "stop", "retry", "skip_row", "alert", "wait", "alt_search"]
        config["failure_action"]["type"] = failure_actions[self.failure_action_combo.currentIndex()]
        
        # 액션별 파라미터
        if config["failure_action"]["type"] == "retry":
            config["failure_action"]["count"] = self.retry_count_spin.value()
            config["failure_action"]["interval"] = self.retry_interval_spin.value()
        elif config["failure_action"]["type"] == "alert":
            config["failure_action"]["message"] = self.alert_text_edit.text()
        elif config["failure_action"]["type"] == "wait":
            config["failure_action"]["seconds"] = self.wait_time_spin.value()
            
        return config