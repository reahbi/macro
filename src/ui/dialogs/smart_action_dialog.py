"""
스마트 액션 다이얼로그 - 엑셀 연동 통합 GUI
"""

from typing import Optional, Dict, Any, List
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QGroupBox, QRadioButton, QLineEdit, QComboBox, QSpinBox,
    QCheckBox, QTextEdit, QFileDialog, QListWidget, QListWidgetItem,
    QTabWidget, QWidget, QTableWidget, QTableWidgetItem, QHeaderView,
    QSplitter, QFrame, QButtonGroup, QMessageBox, QCompleter
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor, QPalette

class SmartActionDialog(QDialog):
    """엑셀 연동 스마트 액션 설정 다이얼로그"""
    
    def __init__(self, parent=None, excel_columns=None, excel_data=None):
        super().__init__(parent)
        self.excel_columns = excel_columns or []
        self.excel_data = excel_data or []
        self.action_list = []  # 설정된 액션 목록
        
        self.setWindowTitle("🎯 스마트 액션 설정")
        self.setMinimumSize(900, 700)
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 메인 스플리터
        splitter = QSplitter(Qt.Horizontal)
        
        # 왼쪽: 엑셀 데이터 뷰
        left_panel = self.create_excel_panel()
        splitter.addWidget(left_panel)
        
        # 오른쪽: 액션 설정
        right_panel = self.create_action_panel()
        splitter.addWidget(right_panel)
        
        # 비율 설정 (40:60)
        splitter.setSizes([360, 540])
        layout.addWidget(splitter)
        
        # 하단 버튼
        self.create_bottom_buttons(layout)
        
    def create_excel_panel(self):
        """엑셀 데이터 패널 생성"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)
        panel.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 헤더
        header = QLabel("📊 엑셀 데이터")
        header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 5px;
        """)
        layout.addWidget(header)
        
        # 엑셀 테이블
        self.excel_table = QTableWidget()
        self.excel_table.setAlternatingRowColors(True)
        self.excel_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.excel_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #ced4da;
                border-radius: 4px;
            }
            QTableWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        
        # 엑셀 데이터 설정
        if self.excel_columns:
            self.excel_table.setColumnCount(len(self.excel_columns))
            self.excel_table.setHorizontalHeaderLabels(self.excel_columns)
            
            # 샘플 데이터 추가
            if self.excel_data:
                self.excel_table.setRowCount(len(self.excel_data))
                for row, data in enumerate(self.excel_data):
                    for col, value in enumerate(data):
                        self.excel_table.setItem(row, col, QTableWidgetItem(str(value)))
            else:
                # 샘플 데이터 생성
                sample_data = [
                    ["홍길동", "010-1234-5678", "서울시 강남구", "hong@email.com", "신규"],
                    ["김철수", "010-2345-6789", "서울시 서초구", "kim@email.com", "기존"],
                    ["이영희", "010-3456-7890", "서울시 송파구", "lee@email.com", "VIP"],
                ]
                self.excel_table.setRowCount(len(sample_data))
                for row, data in enumerate(sample_data):
                    for col, value in enumerate(data[:len(self.excel_columns)]):
                        self.excel_table.setItem(row, col, QTableWidgetItem(value))
        else:
            # 엑셀 없음 메시지
            self.excel_table.setColumnCount(1)
            self.excel_table.setHorizontalHeaderLabels(["메시지"])
            self.excel_table.setRowCount(1)
            self.excel_table.setItem(0, 0, QTableWidgetItem("엑셀 파일이 로드되지 않았습니다"))
            
        self.excel_table.horizontalHeader().setStretchLastSection(True)
        self.excel_table.verticalHeader().setVisible(False)
        
        layout.addWidget(self.excel_table)
        
        # 변수 사용 안내
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #e7f3ff;
                border: 1px solid #b3d9ff;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        info_layout = QVBoxLayout(info_frame)
        
        info_label = QLabel("💡 변수 사용법")
        info_label.setStyleSheet("font-weight: bold; color: #0066cc;")
        info_layout.addWidget(info_label)
        
        # 사용 가능한 변수 목록
        if self.excel_columns:
            var_text = "사용 가능한 변수:\n"
            for col in self.excel_columns:
                var_text += f"  • {{{{{col}}}}}\n"
        else:
            var_text = "엑셀을 로드하면 변수를 사용할 수 있습니다"
            
        var_label = QLabel(var_text)
        var_label.setStyleSheet("color: #333; font-size: 12px;")
        var_label.setWordWrap(True)
        info_layout.addWidget(var_label)
        
        layout.addWidget(info_frame)
        
        return panel
        
    def create_action_panel(self):
        """액션 설정 패널 생성"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.Box)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # 헤더
        header = QLabel("⚡ 액션 설정")
        header.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            padding: 5px;
        """)
        layout.addWidget(header)
        
        # 탭 위젯
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ced4da;
                background-color: white;
            }
            QTabBar::tab {
                padding: 8px 16px;
                margin-right: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #007bff;
            }
        """)
        
        # 탭 1: 빠른 설정
        quick_tab = self.create_quick_setup_tab()
        self.tab_widget.addTab(quick_tab, "⚡ 빠른 설정")
        
        # 탭 2: 상세 설정
        detail_tab = self.create_detail_setup_tab()
        self.tab_widget.addTab(detail_tab, "🔧 상세 설정")
        
        # 탭 3: 액션 순서
        sequence_tab = self.create_sequence_tab()
        self.tab_widget.addTab(sequence_tab, "📋 액션 순서")
        
        layout.addWidget(self.tab_widget)
        
        return panel
        
    def create_quick_setup_tab(self):
        """빠른 설정 탭"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # 시나리오 선택
        scenario_group = QGroupBox("📌 작업 시나리오 선택")
        scenario_layout = QVBoxLayout()
        
        self.scenario_group = QButtonGroup()
        
        scenarios = [
            ("🔍 검색 후 클릭", "search_click", "텍스트나 이미지를 찾아서 클릭합니다"),
            ("📝 폼 자동 입력", "form_fill", "입력 필드를 찾아서 데이터를 입력합니다"),
            ("✅ 데이터 검증", "verify", "화면의 데이터가 맞는지 확인합니다"),
            ("📊 데이터 수집", "collect", "화면에서 데이터를 추출합니다"),
            ("🔄 반복 작업", "repeat", "동일한 작업을 여러 번 반복합니다")
        ]
        
        for i, (text, value, desc) in enumerate(scenarios):
            radio = QRadioButton(text)
            radio.setStyleSheet("font-weight: bold;")
            scenario_layout.addWidget(radio)
            
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("color: #666; margin-left: 25px; margin-bottom: 10px;")
            scenario_layout.addWidget(desc_label)
            
            self.scenario_group.addButton(radio, i)
            
        scenario_group.setLayout(scenario_layout)
        layout.addWidget(scenario_group)
        
        # 빠른 설정 옵션
        self.quick_options = QGroupBox("⚙️ 빠른 옵션")
        self.quick_options_layout = QVBoxLayout()
        self.quick_options.setLayout(self.quick_options_layout)
        layout.addWidget(self.quick_options)
        
        # 시나리오 선택 시 옵션 표시
        self.scenario_group.buttonClicked.connect(self.on_scenario_selected)
        
        layout.addStretch()
        
        # 액션 생성 버튼
        create_btn = QPushButton("➕ 액션 생성")
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-size: 14px;
                font-weight: bold;
                padding: 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        create_btn.clicked.connect(self.create_action_from_quick)
        layout.addWidget(create_btn)
        
        return widget
        
    def create_detail_setup_tab(self):
        """상세 설정 탭"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 검색 대상
        search_group = QGroupBox("🔍 검색 대상")
        search_layout = QVBoxLayout()
        
        # 검색 타입
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("타입:"))
        self.search_type_combo = QComboBox()
        self.search_type_combo.addItems(["텍스트", "이미지", "좌표"])
        type_layout.addWidget(self.search_type_combo)
        type_layout.addStretch()
        search_layout.addLayout(type_layout)
        
        # 검색 값
        self.search_value_edit = QLineEdit()
        self.search_value_edit.setPlaceholderText("검색할 값 (예: {{고객명}}, 확인 버튼)")
        
        # 변수 자동완성
        if self.excel_columns:
            completer = QCompleter([f"{{{{{col}}}}}" for col in self.excel_columns])
            self.search_value_edit.setCompleter(completer)
            
        search_layout.addWidget(self.search_value_edit)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # 성공 액션
        success_group = QGroupBox("✅ 찾았을 때")
        success_layout = QVBoxLayout()
        
        self.success_action_combo = QComboBox()
        self.success_action_combo.addItems([
            "클릭", "더블클릭", "우클릭",
            "텍스트 입력", "키 입력", 
            "대기", "스크린샷",
            "값 저장", "값 검증"
        ])
        success_layout.addWidget(self.success_action_combo)
        
        # 액션 파라미터
        self.success_param_edit = QLineEdit()
        self.success_param_edit.setPlaceholderText("액션 파라미터 (예: {{전화번호}})")
        success_layout.addWidget(self.success_param_edit)
        
        success_group.setLayout(success_layout)
        layout.addWidget(success_group)
        
        # 실패 액션
        fail_group = QGroupBox("❌ 못 찾았을 때")
        fail_layout = QVBoxLayout()
        
        self.fail_action_combo = QComboBox()
        self.fail_action_combo.addItems([
            "다음으로 진행",
            "중지",
            "재시도 (3회)",
            "다음 엑셀 행으로",
            "경고 메시지",
            "대체 검색"
        ])
        fail_layout.addWidget(self.fail_action_combo)
        
        fail_group.setLayout(fail_layout)
        layout.addWidget(fail_group)
        
        # 고급 옵션
        advanced_group = QGroupBox("🔧 고급 옵션")
        advanced_layout = QVBoxLayout()
        
        self.wait_before_check = QCheckBox("실행 전 대기")
        self.wait_before_spin = QSpinBox()
        self.wait_before_spin.setRange(0, 10)
        self.wait_before_spin.setSuffix("초")
        self.wait_before_spin.setEnabled(False)
        self.wait_before_check.toggled.connect(self.wait_before_spin.setEnabled)
        
        wait_layout = QHBoxLayout()
        wait_layout.addWidget(self.wait_before_check)
        wait_layout.addWidget(self.wait_before_spin)
        wait_layout.addStretch()
        advanced_layout.addLayout(wait_layout)
        
        self.region_check = QCheckBox("특정 영역에서만 검색")
        advanced_layout.addWidget(self.region_check)
        
        advanced_group.setLayout(advanced_layout)
        layout.addWidget(advanced_group)
        
        layout.addStretch()
        
        # 액션 추가 버튼
        add_btn = QPushButton("➕ 액션 추가")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #007bff;
                color: white;
                font-weight: bold;
                padding: 10px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
        """)
        add_btn.clicked.connect(self.add_action_from_detail)
        layout.addWidget(add_btn)
        
        return widget
        
    def create_sequence_tab(self):
        """액션 순서 탭"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 액션 목록
        self.action_list_widget = QListWidget()
        self.action_list_widget.setDragDropMode(QListWidget.InternalMove)
        self.action_list_widget.setStyleSheet("""
            QListWidget {
                border: 1px solid #ced4da;
                border-radius: 4px;
            }
            QListWidget::item {
                padding: 10px;
                margin: 2px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 4px;
            }
            QListWidget::item:selected {
                background-color: #007bff;
                color: white;
            }
        """)
        
        layout.addWidget(QLabel("📋 액션 실행 순서 (드래그로 순서 변경 가능)"))
        layout.addWidget(self.action_list_widget)
        
        # 버튼들
        btn_layout = QHBoxLayout()
        
        edit_btn = QPushButton("✏️ 편집")
        edit_btn.clicked.connect(self.edit_selected_action)
        
        delete_btn = QPushButton("🗑️ 삭제")
        delete_btn.clicked.connect(self.delete_selected_action)
        
        clear_btn = QPushButton("🧹 전체 삭제")
        clear_btn.clicked.connect(self.clear_all_actions)
        
        btn_layout.addWidget(edit_btn)
        btn_layout.addWidget(delete_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(clear_btn)
        
        layout.addLayout(btn_layout)
        
        # 실행 미리보기
        preview_group = QGroupBox("👁️ 실행 미리보기")
        preview_layout = QVBoxLayout()
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        self.preview_text.setStyleSheet("""
            QTextEdit {
                font-family: Consolas, monospace;
                font-size: 12px;
                background-color: #f5f5f5;
            }
        """)
        
        preview_layout.addWidget(self.preview_text)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        return widget
        
    def create_bottom_buttons(self, layout):
        """하단 버튼 생성"""
        btn_frame = QFrame()
        btn_frame.setFrameStyle(QFrame.Box)
        btn_frame.setStyleSheet("background-color: #f8f9fa; border-top: 1px solid #dee2e6;")
        
        btn_layout = QHBoxLayout(btn_frame)
        
        # 테스트 버튼
        test_btn = QPushButton("🧪 테스트 실행")
        test_btn.setStyleSheet("""
            QPushButton {
                background-color: #ffc107;
                color: #212529;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e0a800;
            }
        """)
        test_btn.clicked.connect(self.test_actions)
        
        # 확인/취소
        ok_btn = QPushButton("✔️ 확인")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                font-weight: bold;
                padding: 8px 30px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
        """)
        ok_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("✖️ 취소")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                font-weight: bold;
                padding: 8px 30px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        btn_layout.addWidget(test_btn)
        btn_layout.addStretch()
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addWidget(btn_frame)
        
    def on_scenario_selected(self, button):
        """시나리오 선택 시"""
        # 기존 옵션 제거
        while self.quick_options_layout.count():
            child = self.quick_options_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
                
        scenario_idx = self.scenario_group.id(button)
        
        if scenario_idx == 0:  # 검색 후 클릭
            self.search_input = QLineEdit()
            self.search_input.setPlaceholderText("검색할 텍스트 (예: {{고객명}}, 확인)")
            self.quick_options_layout.addWidget(QLabel("검색할 텍스트:"))
            self.quick_options_layout.addWidget(self.search_input)
            
        elif scenario_idx == 1:  # 폼 자동 입력
            self.form_fields = []
            for col in self.excel_columns[:3]:  # 최대 3개 필드
                label = QLabel(f"{col}:")
                edit = QLineEdit()
                edit.setText(f"{{{{{col}}}}}")
                self.quick_options_layout.addWidget(label)
                self.quick_options_layout.addWidget(edit)
                self.form_fields.append((col, edit))
                
        elif scenario_idx == 2:  # 데이터 검증
            self.verify_field = QComboBox()
            self.verify_field.addItems(self.excel_columns)
            self.quick_options_layout.addWidget(QLabel("검증할 필드:"))
            self.quick_options_layout.addWidget(self.verify_field)
            
    def create_action_from_quick(self):
        """빠른 설정에서 액션 생성"""
        if self.scenario_group.checkedId() == -1:
            QMessageBox.warning(self, "경고", "시나리오를 선택해주세요.")
            return
            
        scenario_idx = self.scenario_group.checkedId()
        
        if scenario_idx == 0:  # 검색 후 클릭
            if hasattr(self, 'search_input') and self.search_input.text():
                action = {
                    'type': 'search_and_click',
                    'search': self.search_input.text(),
                    'action': 'click'
                }
                self.add_action_to_list(action)
                
    def add_action_from_detail(self):
        """상세 설정에서 액션 추가"""
        action = {
            'search_type': self.search_type_combo.currentText(),
            'search_value': self.search_value_edit.text(),
            'success_action': self.success_action_combo.currentText(),
            'success_param': self.success_param_edit.text(),
            'fail_action': self.fail_action_combo.currentText(),
            'wait_before': self.wait_before_spin.value() if self.wait_before_check.isChecked() else 0,
            'use_region': self.region_check.isChecked()
        }
        
        if not action['search_value']:
            QMessageBox.warning(self, "경고", "검색할 값을 입력해주세요.")
            return
            
        self.add_action_to_list(action)
        
        # 입력 필드 초기화
        self.search_value_edit.clear()
        self.success_param_edit.clear()
        
    def add_action_to_list(self, action):
        """액션을 목록에 추가"""
        self.action_list.append(action)
        
        # 리스트 위젯에 표시
        item_text = self.format_action_display(action)
        self.action_list_widget.addItem(item_text)
        
        # 미리보기 업데이트
        self.update_preview()
        
        # 액션 순서 탭으로 전환
        self.tab_widget.setCurrentIndex(2)
        
    def format_action_display(self, action):
        """액션을 보기 좋게 포맷"""
        if 'type' in action and action['type'] == 'search_and_click':
            return f"🔍 '{action['search']}' 검색 → 클릭"
        else:
            search = f"{action['search_type']}: {action['search_value']}"
            success = f"✅ {action['success_action']}"
            if action['success_param']:
                success += f" ({action['success_param']})"
            fail = f"❌ {action['fail_action']}"
            return f"{search} → {success} / {fail}"
            
    def update_preview(self):
        """실행 미리보기 업데이트"""
        preview_text = "=== 실행 시나리오 ===\n\n"
        
        if self.excel_columns:
            preview_text += f"엑셀 데이터: {len(self.excel_columns)}개 컬럼\n"
            preview_text += f"반복 실행: 각 행에 대해 아래 액션 수행\n\n"
            
        for i, action in enumerate(self.action_list, 1):
            preview_text += f"{i}. {self.format_action_display(action)}\n"
            
        self.preview_text.setPlainText(preview_text)
        
    def edit_selected_action(self):
        """선택된 액션 편집"""
        # TODO: 구현
        pass
        
    def delete_selected_action(self):
        """선택된 액션 삭제"""
        current = self.action_list_widget.currentRow()
        if current >= 0:
            self.action_list_widget.takeItem(current)
            del self.action_list[current]
            self.update_preview()
            
    def clear_all_actions(self):
        """모든 액션 삭제"""
        reply = QMessageBox.question(self, "확인", "모든 액션을 삭제하시겠습니까?")
        if reply == QMessageBox.Yes:
            self.action_list_widget.clear()
            self.action_list.clear()
            self.update_preview()
            
    def test_actions(self):
        """액션 테스트"""
        if not self.action_list:
            QMessageBox.information(self, "정보", "테스트할 액션이 없습니다.")
            return
            
        # TODO: 실제 테스트 구현
        QMessageBox.information(self, "테스트", "액션 테스트 기능은 구현 예정입니다.")
        
    def get_actions(self):
        """설정된 액션 목록 반환"""
        return self.action_list