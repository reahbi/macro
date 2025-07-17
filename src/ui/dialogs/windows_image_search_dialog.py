"""
Windows 환경에 최적화된 이미지 검색 다이얼로그
변수 범위 문제가 완전히 해결된 안정적인 구현
"""

import os
from typing import Optional, Dict, Any, Tuple
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QDoubleSpinBox, QGroupBox, QFileDialog,
    QDialogButtonBox, QMessageBox, QCheckBox, QComboBox,
    QFormLayout, QWidget, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.macro_types import MacroStep, StepType
from vision.image_matcher import ImageMatcher
from config.settings import Settings
from ui.widgets.simple_roi_selector import SimpleROISelector
from utils.clipboard_utils import save_clipboard_image


class WindowsImageSearchDialog(QDialog):
    """Windows 환경에 최적화된 이미지 검색 다이얼로그"""
    
    def __init__(self, step: Optional[MacroStep] = None, 
                 settings: Optional[Settings] = None,
                 parent=None):
        super().__init__(parent)
        print("DEBUG: WindowsImageSearchDialog __init__")
        
        # 기본 설정
        self.step = step
        self.settings = settings or Settings()
        self.image_matcher = ImageMatcher(self.settings)
        
        # 선택된 영역 저장
        self.selected_region = None
        
        # 스텝 데이터
        self.step_data: Dict[str, Any] = {}
        if step:
            self.step_data = step.to_dict()
            
        # UI 초기화
        self.init_ui()
        self.load_step_data()
        
    def init_ui(self):
        """UI 초기화"""
        self.setWindowTitle("이미지 검색 단계 설정")
        self.setModal(True)  # 모달 다이얼로그로 설정
        self.setMinimumWidth(650)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout()
        
        # 1. 기본 정보
        self._create_basic_info_section(layout)
        
        # 2. 이미지 선택
        self._create_image_section(layout)
        
        # 3. 검색 영역
        self._create_region_section(layout)
        
        # 4. 검색 옵션
        self._create_search_options_section(layout)
        
        # 5. 클릭 옵션
        self._create_click_options_section(layout)
        
        # 6. 대화상자 버튼
        self._create_dialog_buttons(layout)
        
        self.setLayout(layout)
        
    def _create_basic_info_section(self, layout):
        """기본 정보 섹션"""
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("예: 로그인 버튼 찾기")
        form_layout.addRow("단계 이름:", self.name_input)
        
        layout.addLayout(form_layout)
        
    def _create_image_section(self, layout):
        """이미지 선택 섹션"""
        image_group = QGroupBox("참조 이미지")
        image_layout = QVBoxLayout()
        
        # 이미지 경로
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("이미지 경로:"))
        self.image_path_input = QLineEdit()
        self.image_path_input.setReadOnly(True)
        path_layout.addWidget(self.image_path_input)
        
        # 버튼들
        self.browse_btn = QPushButton("찾아보기...")
        self.browse_btn.clicked.connect(self._browse_image)
        path_layout.addWidget(self.browse_btn)
        
        self.capture_btn = QPushButton("화면 캡처")
        self.capture_btn.clicked.connect(self._capture_image)
        path_layout.addWidget(self.capture_btn)
        
        self.paste_btn = QPushButton("붙여넣기")
        self.paste_btn.clicked.connect(self._paste_from_clipboard)
        path_layout.addWidget(self.paste_btn)
        
        # Ctrl+V 단축키
        paste_shortcut = QShortcut(QKeySequence("Ctrl+V"), self)
        paste_shortcut.activated.connect(self._paste_from_clipboard)
        
        image_layout.addLayout(path_layout)
        
        # 이미지 미리보기
        self.image_preview = QLabel()
        self.image_preview.setMinimumHeight(150)
        self.image_preview.setMaximumHeight(300)
        self.image_preview.setScaledContents(False)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("""
            QLabel {
                border: 2px solid #ccc;
                background-color: #f9f9f9;
                border-radius: 4px;
            }
        """)
        self.image_preview.setText("이미지를 선택하세요")
        image_layout.addWidget(self.image_preview)
        
        # 도움말
        help_label = QLabel(
            "💡 팁: Shift + Win + S 로 화면을 캡처한 후 '붙여넣기' 버튼을 클릭하세요."
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet("""
            color: #0066cc; 
            font-size: 12px; 
            padding: 8px; 
            background-color: #e6f2ff; 
            border-radius: 4px;
        """)
        image_layout.addWidget(help_label)
        
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)
        
    def _create_region_section(self, layout):
        """검색 영역 섹션"""
        region_group = QGroupBox("검색 영역 (선택사항)")
        region_layout = QVBoxLayout()
        
        # 영역 정보 표시
        self.region_label = QLabel("전체 화면")
        if self.selected_region:
            self.region_label.setText(
                f"영역: ({self.selected_region[0]}, {self.selected_region[1]}) "
                f"크기: {self.selected_region[2]}x{self.selected_region[3]}"
            )
        self.region_label.setStyleSheet("font-weight: bold;")
        region_layout.addWidget(self.region_label)
        
        # 버튼들
        button_layout = QHBoxLayout()
        
        self.select_region_btn = QPushButton("🔲 화면 영역 선택")
        self.select_region_btn.clicked.connect(self._select_region)
        self.select_region_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                font-weight: bold;
            }
        """)
        button_layout.addWidget(self.select_region_btn)
        
        self.clear_region_btn = QPushButton("초기화")
        self.clear_region_btn.clicked.connect(self._clear_region)
        self.clear_region_btn.setEnabled(False)
        button_layout.addWidget(self.clear_region_btn)
        
        region_layout.addLayout(button_layout)
        
        region_group.setLayout(region_layout)
        layout.addWidget(region_group)
        
    def _create_search_options_section(self, layout):
        """검색 옵션 섹션"""
        options_group = QGroupBox("검색 옵션")
        options_layout = QFormLayout()
        
        # 신뢰도
        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setRange(0.1, 1.0)
        self.confidence_spin.setSingleStep(0.05)
        self.confidence_spin.setValue(0.9)
        self.confidence_spin.setDecimals(2)
        options_layout.addRow("일치도:", self.confidence_spin)
        
        # 모든 항목 찾기
        self.search_all_check = QCheckBox("모든 일치 항목 찾기")
        options_layout.addRow("", self.search_all_check)
        
        # 최대 결과 수
        self.max_results_spin = QSpinBox()
        self.max_results_spin.setRange(1, 100)
        self.max_results_spin.setValue(10)
        self.max_results_spin.setEnabled(False)
        options_layout.addRow("최대 결과:", self.max_results_spin)
        
        # 연결
        self.search_all_check.toggled.connect(self.max_results_spin.setEnabled)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
    def _create_click_options_section(self, layout):
        """클릭 옵션 섹션"""
        click_group = QGroupBox("클릭 옵션")
        click_layout = QVBoxLayout()
        
        # 찾은 후 클릭
        self.click_after_find_check = QCheckBox("이미지를 찾은 후 클릭")
        self.click_after_find_check.setChecked(True)
        click_layout.addWidget(self.click_after_find_check)
        
        # 클릭 타입
        click_type_widget = QWidget()
        click_type_layout = QHBoxLayout()
        click_type_layout.setContentsMargins(20, 0, 0, 0)
        
        click_type_layout.addWidget(QLabel("클릭 유형:"))
        self.click_type_combo = QComboBox()
        self.click_type_combo.addItems(["한번 클릭", "더블 클릭"])
        click_type_layout.addWidget(self.click_type_combo)
        click_type_layout.addStretch()
        
        click_type_widget.setLayout(click_type_layout)
        click_layout.addWidget(click_type_widget)
        
        # 클릭 오프셋
        offset_widget = QWidget()
        offset_layout = QHBoxLayout()
        offset_layout.setContentsMargins(20, 0, 0, 0)
        
        offset_layout.addWidget(QLabel("클릭 오프셋:"))
        offset_layout.addWidget(QLabel("X:"))
        self.offset_x_spin = QSpinBox()
        self.offset_x_spin.setRange(-500, 500)
        self.offset_x_spin.setValue(0)
        offset_layout.addWidget(self.offset_x_spin)
        
        offset_layout.addWidget(QLabel("Y:"))
        self.offset_y_spin = QSpinBox()
        self.offset_y_spin.setRange(-500, 500)
        self.offset_y_spin.setValue(0)
        offset_layout.addWidget(self.offset_y_spin)
        
        offset_layout.addStretch()
        offset_widget.setLayout(offset_layout)
        click_layout.addWidget(offset_widget)
        
        # 연결
        self.click_after_find_check.toggled.connect(click_type_widget.setEnabled)
        self.click_after_find_check.toggled.connect(offset_widget.setEnabled)
        
        click_group.setLayout(click_layout)
        layout.addWidget(click_group)
        
    def _create_dialog_buttons(self, layout):
        """대화상자 버튼"""
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
    def _browse_image(self):
        """이미지 파일 찾아보기"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "참조 이미지 선택",
            "",
            "이미지 파일 (*.png *.jpg *.jpeg *.bmp);;모든 파일 (*.*)"
        )
        
        if file_path:
            self.image_path_input.setText(file_path)
            self._update_preview()
            
    def _capture_image(self):
        """화면 캡처"""
        # Hide dialog temporarily
        self.hide()
        # Give time for dialog to hide before showing ROI selector
        QTimer.singleShot(200, self._show_capture_selector)
        
    def _show_capture_selector(self):
        """캡처 시작"""
        try:
            print("DEBUG: Creating SimpleROISelector for image capture")
            # 새로운 안정적인 ROI 선택기 사용
            self.simple_roi_selector = SimpleROISelector(parent=None)
            self.simple_roi_selector.selectionComplete.connect(self._on_capture_complete)
            self.simple_roi_selector.selectionCancelled.connect(self._on_capture_cancelled)
            print("DEBUG: Starting SimpleROI capture selection")
            self.simple_roi_selector.start_selection()
        except Exception as e:
            print(f"ERROR: Failed to start capture: {e}")
            import traceback
            traceback.print_exc()
            self.show()
            QMessageBox.warning(self, "오류", f"화면 캡처를 시작할 수 없습니다: {str(e)}")
            
    def _on_capture_complete(self, region):
        """캡처 완료"""
        print(f"DEBUG: Capture complete: {region}")
        
        try:
            if region and len(region) == 4:
                # 캡처 수행
                import time
                import pyautogui
                
                timestamp = time.strftime("%Y%m%d_%H%M%S")
                filename = f"capture_{timestamp}.png"
                
                # captures 디렉토리 생성
                captures_dir = os.path.join(os.path.dirname(__file__), "../../../captures")
                os.makedirs(captures_dir, exist_ok=True)
                
                file_path = os.path.join(captures_dir, filename)
                
                # pyautogui로 캡처
                x, y, w, h = region
                screenshot = pyautogui.screenshot(region=(x, y, w, h))
                screenshot.save(file_path)
                
                # UI 업데이트
                self.image_path_input.setText(file_path)
                QTimer.singleShot(50, self._update_preview)
                
        except Exception as e:
            print(f"ERROR: Failed to save capture: {e}")
            QMessageBox.warning(self, "오류", f"캡처 저장 실패: {str(e)}")
            
        finally:
            # 다이얼로그 복원
            self.show()
            self.raise_()
            self.activateWindow()
            
    def _on_capture_cancelled(self):
        """캡처 취소"""
        print("DEBUG: Capture cancelled")
        self.show()
        self.raise_()
        self.activateWindow()
        
    def _paste_from_clipboard(self):
        """클립보드에서 붙여넣기"""
        file_path = save_clipboard_image()
        
        if file_path and os.path.exists(file_path):
            self.image_path_input.setText(file_path)
            QTimer.singleShot(50, self._update_preview)
            QMessageBox.information(self, "성공", "클립보드에서 이미지를 붙여넣었습니다.")
        else:
            QMessageBox.information(
                self, 
                "안내", 
                "클립보드에 이미지가 없습니다.\\n\\n"
                "Shift + Win + S 로 화면을 캡처한 후 다시 시도하세요."
            )
            
    def _update_preview(self):
        """이미지 미리보기 업데이트"""
        image_path = self.image_path_input.text()
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # 미리보기 크기에 맞게 조정
                label_width = self.image_preview.width() - 10
                label_height = self.image_preview.height() - 10
                
                scaled = pixmap.scaled(
                    label_width,
                    label_height,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_preview.setPixmap(scaled)
                self.image_preview.setToolTip(f"원본 크기: {pixmap.width()} x {pixmap.height()}")
            else:
                self.image_preview.setText("잘못된 이미지 파일")
        else:
            self.image_preview.setText("이미지를 선택하세요")
            
    def _select_region(self):
        """Select screen region"""
        # Hide dialog temporarily
        self.hide()
        # Give time for dialog to hide before showing ROI selector
        QTimer.singleShot(200, self._show_region_selector)
        
    def _show_region_selector(self):
        """안정적인 SimpleROISelector를 사용하여 영역 선택"""
        try:
            print("DEBUG: Creating SimpleROISelector for image search")
            # 새로운 안정적인 ROI 선택기 사용
            self.simple_roi_selector = SimpleROISelector(parent=None)
            self.simple_roi_selector.selectionComplete.connect(self._on_region_selected)
            self.simple_roi_selector.selectionCancelled.connect(self._on_selection_cancelled)
            print("DEBUG: Starting SimpleROI selection")
            self.simple_roi_selector.start_selection()
        except Exception as e:
            print(f"DEBUG: Error in _show_region_selector: {e}")
            import traceback
            traceback.print_exc()
            self.show()
            
    def _on_region_selected(self, region: Tuple[int, int, int, int]):
        """Handle region selection"""
        try:
            # Ensure region is properly formatted
            if region and len(region) == 4:
                # Convert all values to integers to avoid any type issues
                formatted_region = tuple(int(x) for x in region)
                self.selected_region = formatted_region
                self.region_label.setText(
                    f"영역: ({formatted_region[0]}, {formatted_region[1]}) "
                    f"크기: {formatted_region[2]}x{formatted_region[3]}"
                )
                self.clear_region_btn.setEnabled(True)
            else:
                self.selected_region = None
                self.region_label.setText("전체 화면에서 검색")
            
            # Restore dialog visibility
            self.show()
            self.raise_()
            self.activateWindow()
        except Exception as e:
            print(f"DEBUG: Error in _on_region_selected: {e}")
            import traceback
            traceback.print_exc()
            # Still try to show the dialog
            self.selected_region = None
            self.region_label.setText("전체 화면에서 검색")
            self.show()
        
    def _on_selection_cancelled(self):
        """영역 선택 취소 처리"""
        print("DEBUG: Image search region selection cancelled")
        # 다이얼로그 복원
        self.show()
        self.raise_()
        self.activateWindow()
        
    def _clear_region(self):
        """Clear selected region"""
        self.selected_region = None
        self.region_label.setText("전체 화면")
        self.clear_region_btn.setEnabled(False)
        
    def load_step_data(self):
        """기존 스텝 데이터 로드"""
        if self.step:
            self.name_input.setText(self.step.name)
            
            if hasattr(self.step, 'image_path'):
                self.image_path_input.setText(self.step.image_path)
                self._update_preview()
                
            if hasattr(self.step, 'region') and self.step.region:
                self.selected_region = self.step.region
                x, y, w, h = self.step.region
                self.region_label.setText(f"선택된 영역: ({x}, {y}) - 크기: {w}×{h}")
                self.clear_region_btn.setEnabled(True)
                
            if hasattr(self.step, 'confidence'):
                self.confidence_spin.setValue(self.step.confidence)
                
            if hasattr(self.step, 'click_after_find'):
                self.click_after_find_check.setChecked(self.step.click_after_find)
                
            if hasattr(self.step, 'click_offset'):
                offset = self.step.click_offset
                if offset and len(offset) >= 2:
                    self.offset_x_spin.setValue(offset[0])
                    self.offset_y_spin.setValue(offset[1])
                    
            if hasattr(self.step, 'double_click'):
                self.click_type_combo.setCurrentIndex(1 if self.step.double_click else 0)
                
    def get_step_data(self) -> Dict[str, Any]:
        """스텝 데이터 반환"""
        return {
            'name': self.name_input.text() or "이미지 검색",
            'step_type': StepType.IMAGE_SEARCH,
            'image_path': self.image_path_input.text(),
            'region': self.selected_region,
            'confidence': self.confidence_spin.value(),
            'search_all': self.search_all_check.isChecked(),
            'max_results': self.max_results_spin.value(),
            'click_after_find': self.click_after_find_check.isChecked(),
            'click_offset': (self.offset_x_spin.value(), self.offset_y_spin.value()),
            'double_click': self.click_type_combo.currentIndex() == 1
        }
        
    def accept(self):
        """다이얼로그 승인"""
        # 유효성 검사
        if not self.name_input.text():
            QMessageBox.warning(self, "확인", "단계 이름을 입력해주세요.")
            return
            
        if not self.image_path_input.text():
            QMessageBox.warning(self, "확인", "참조 이미지를 선택해주세요.")
            return
            
        if not os.path.exists(self.image_path_input.text()):
            QMessageBox.warning(self, "확인", "선택한 이미지 파일이 존재하지 않습니다.")
            return
            
        super().accept()