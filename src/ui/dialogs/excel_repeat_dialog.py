"""
Excel 반복 설정 다이얼로그
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QRadioButton,
    QSpinBox, QGroupBox, QDialogButtonBox, QPushButton,
    QWidget, QButtonGroup
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont
from typing import Dict, Any, Optional


class ExcelRepeatDialog(QDialog):
    """Excel 반복 설정을 위한 다이얼로그"""
    
    settingsConfirmed = pyqtSignal(dict)  # 설정 완료 시그널
    
    def __init__(self, total_rows: int = 0, incomplete_rows: int = 0, parent=None):
        super().__init__(parent)
        self.total_rows = total_rows
        self.incomplete_rows = incomplete_rows
        self.setWindowTitle("Excel 반복 설정")
        self.setModal(True)
        self.setMinimumWidth(450)
        # Prevent dialog from affecting parent window
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout()
        layout.setSpacing(15)
        
        # 헤더
        header_label = QLabel("어떻게 반복할까요?")
        header_font = QFont()
        header_font.setPointSize(14)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(header_label)
        
        # Excel 정보
        if self.total_rows > 0:
            info_group = QGroupBox("Excel 정보")
            info_layout = QVBoxLayout()
            
            info_text = f"📊 총 {self.total_rows}개 행"
            if self.incomplete_rows > 0:
                info_text += f" (미완료: {self.incomplete_rows}개)"
            
            info_label = QLabel(info_text)
            info_label.setStyleSheet("""
                QLabel {
                    background-color: #f0f0f0;
                    padding: 10px;
                    border-radius: 5px;
                }
            """)
            info_layout.addWidget(info_label)
            info_group.setLayout(info_layout)
            layout.addWidget(info_group)
        
        # 반복 옵션
        options_group = QGroupBox("반복 옵션")
        options_layout = QVBoxLayout()
        options_layout.setSpacing(10)
        
        # 라디오 버튼 그룹
        self.button_group = QButtonGroup()
        
        # 옵션 1: 미완료 행만
        self.incomplete_radio = QRadioButton("미완료 행만 처리")
        self.incomplete_radio.setChecked(True)
        incomplete_desc = QLabel(f"   완료되지 않은 {self.incomplete_rows}개 행을 처리합니다")
        incomplete_desc.setStyleSheet("color: #666; margin-left: 25px;")
        options_layout.addWidget(self.incomplete_radio)
        options_layout.addWidget(incomplete_desc)
        self.button_group.addButton(self.incomplete_radio, 0)
        
        # 옵션 2: 특정 개수
        count_container = QWidget()
        count_layout = QHBoxLayout()
        count_layout.setContentsMargins(0, 0, 0, 0)
        
        self.count_radio = QRadioButton("특정 개수만")
        self.count_spin = QSpinBox()
        self.count_spin.setMinimum(1)
        self.count_spin.setMaximum(self.total_rows if self.total_rows > 0 else 9999)
        self.count_spin.setValue(10)
        self.count_spin.setSuffix(" 행")
        self.count_spin.setEnabled(False)
        
        count_layout.addWidget(self.count_radio)
        count_layout.addWidget(self.count_spin)
        count_layout.addStretch()
        count_container.setLayout(count_layout)
        options_layout.addWidget(count_container)
        self.button_group.addButton(self.count_radio, 1)
        
        # 옵션 3: 범위 지정
        range_container = QWidget()
        range_layout = QHBoxLayout()
        range_layout.setContentsMargins(0, 0, 0, 0)
        
        self.range_radio = QRadioButton("범위 지정")
        self.start_spin = QSpinBox()
        self.start_spin.setMinimum(1)
        self.start_spin.setMaximum(self.total_rows if self.total_rows > 0 else 9999)
        self.start_spin.setValue(1)
        self.start_spin.setEnabled(False)
        
        self.end_spin = QSpinBox()
        self.end_spin.setMinimum(1)
        self.end_spin.setMaximum(self.total_rows if self.total_rows > 0 else 9999)
        self.end_spin.setValue(min(50, self.total_rows) if self.total_rows > 0 else 50)
        self.end_spin.setEnabled(False)
        
        range_layout.addWidget(self.range_radio)
        range_layout.addWidget(self.start_spin)
        range_layout.addWidget(QLabel("행부터"))
        range_layout.addWidget(self.end_spin)
        range_layout.addWidget(QLabel("행까지"))
        range_layout.addStretch()
        range_container.setLayout(range_layout)
        options_layout.addWidget(range_container)
        self.button_group.addButton(self.range_radio, 2)
        
        # 옵션 4: 모든 행
        self.all_radio = QRadioButton("모든 행 처리")
        all_desc = QLabel(f"   전체 {self.total_rows}개 행을 모두 처리합니다")
        all_desc.setStyleSheet("color: #666; margin-left: 25px;")
        options_layout.addWidget(self.all_radio)
        options_layout.addWidget(all_desc)
        self.button_group.addButton(self.all_radio, 3)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # 라디오 버튼 선택 시 스핀박스 활성화/비활성화
        self.button_group.buttonClicked.connect(self.on_option_changed)
        
        # 버튼
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        # Ensure dialog doesn't affect parent window
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        
        # OK 버튼 텍스트 변경
        ok_button = buttons.button(QDialogButtonBox.Ok)
        ok_button.setText("확인")
        
        layout.addWidget(buttons)
        self.setLayout(layout)
        
    def on_option_changed(self, button):
        """옵션 변경 시 처리"""
        option_id = self.button_group.id(button)
        
        # 특정 개수 스핀박스
        self.count_spin.setEnabled(option_id == 1)
        
        # 범위 지정 스핀박스
        self.start_spin.setEnabled(option_id == 2)
        self.end_spin.setEnabled(option_id == 2)
        
    def get_settings(self) -> Dict[str, Any]:
        """선택된 설정 반환"""
        option_id = self.button_group.checkedId()
        
        settings = {
            "repeat_mode": "",
            "repeat_count": 0,
            "start_row": 0,
            "end_row": 0
        }
        
        if option_id == 0:  # 미완료 행만
            settings["repeat_mode"] = "incomplete_only"
        elif option_id == 1:  # 특정 개수
            settings["repeat_mode"] = "specific_count"
            settings["repeat_count"] = self.count_spin.value()
        elif option_id == 2:  # 범위 지정
            settings["repeat_mode"] = "range"
            settings["start_row"] = self.start_spin.value() - 1  # 0-based index
            settings["end_row"] = self.end_spin.value() - 1
        elif option_id == 3:  # 모든 행
            settings["repeat_mode"] = "all"
            
        return settings


class QuickExcelSetupDialog(QDialog):
    """Excel 반복 블록 추가 시 나타나는 빠른 설정 다이얼로그"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Excel 반복 블록")
        self.setModal(True)
        self.setMinimumWidth(400)
        # Ensure dialog doesn't affect parent window
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        
        # 아이콘과 메시지
        icon_label = QLabel("🔄")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(icon_label)
        
        message = QLabel(
            "Excel 반복 블록이 추가되었습니다!\n"
            "이제 블록 안에 반복할 작업을 넣어주세요."
        )
        message.setAlignment(Qt.AlignCenter)
        message.setStyleSheet("font-size: 14px; padding: 10px;")
        layout.addWidget(message)
        
        # 팁
        tip_label = QLabel(
            "💡 팁: 블록 안의 작업들이 Excel의 각 행에 대해\n"
            "자동으로 반복 실행됩니다."
        )
        tip_label.setStyleSheet("""
            QLabel {
                background-color: #e3f2fd;
                padding: 15px;
                border-radius: 5px;
                color: #1976d2;
            }
        """)
        tip_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(tip_label)
        
        # 버튼
        ok_button = QPushButton("확인")
        ok_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 10px 30px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        ok_button.clicked.connect(lambda: self.done(QDialog.Accepted))
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(ok_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        self.setLayout(layout)