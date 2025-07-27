"""
Dialog for configuring text search steps with Excel column binding
"""

from typing import Optional, Dict, Any, Tuple
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QCheckBox, QSpinBox,
    QDoubleSpinBox, QComboBox, QGroupBox, QMessageBox,
    QDialogButtonBox, QWidget, QApplication
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QPainter, QPen, QColor
from core.macro_types import TextSearchStep
from ui.widgets.roi_selector import ROISelectorOverlay
from vision.text_extractor_paddle import PaddleTextExtractor as TextExtractor
from utils.monitor_utils import get_monitor_info
import pyautogui
import mss

class TextSearchStepDialog(QDialog):
    """Dialog for configuring text search steps"""
    
    def __init__(self, step: Optional[TextSearchStep] = None, 
                 excel_columns: list = None, parent=None):
        super().__init__(parent)
        self.step = step or TextSearchStep()
        self.excel_columns = excel_columns or []
        self.region = self.step.region
        self.text_extractor = TextExtractor()
        self.monitors = get_monitor_info()  # Get monitor information
        self._loading_data = False  # Flag to prevent region reset during data loading
        self.setWindowTitle("텍스트 검색 단계 설정")
        self.setModal(True)
        self.setMinimumWidth(500)
        self.init_ui()
        self.load_step_data()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Basic info
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("예: 환자 이름 찾기")
        form_layout.addRow("단계 이름:", self.name_edit)
        
        layout.addLayout(form_layout)
        
        # Text search configuration
        search_group = QGroupBox("텍스트 검색 설정")
        search_layout = QVBoxLayout()
        
        # Search text type selection
        text_type_layout = QHBoxLayout()
        text_type_layout.addWidget(QLabel("검색 방법:"))
        
        self.fixed_text_radio = QCheckBox("고정 텍스트")
        self.excel_column_radio = QCheckBox("엑셀 열 데이터")
        self.fixed_text_radio.setChecked(True)
        
        # Make them mutually exclusive
        self.fixed_text_radio.toggled.connect(
            lambda checked: self.excel_column_radio.setChecked(not checked) if checked else None
        )
        self.excel_column_radio.toggled.connect(
            lambda checked: self.fixed_text_radio.setChecked(not checked) if checked else None
        )
        
        text_type_layout.addWidget(self.fixed_text_radio)
        text_type_layout.addWidget(self.excel_column_radio)
        text_type_layout.addStretch()
        search_layout.addLayout(text_type_layout)
        
        # Fixed text input
        self.fixed_text_widget = QWidget()
        fixed_text_layout = QHBoxLayout()
        fixed_text_layout.setContentsMargins(0, 0, 0, 0)
        fixed_text_layout.addWidget(QLabel("검색할 텍스트:"))
        self.search_text_edit = QLineEdit()
        self.search_text_edit.setPlaceholderText("예: 홍길동")
        fixed_text_layout.addWidget(self.search_text_edit)
        self.fixed_text_widget.setLayout(fixed_text_layout)
        search_layout.addWidget(self.fixed_text_widget)
        
        # Excel column selection
        self.excel_column_widget = QWidget()
        excel_layout = QHBoxLayout()
        excel_layout.setContentsMargins(0, 0, 0, 0)
        excel_layout.addWidget(QLabel("엑셀 열:"))
        self.excel_column_combo = QComboBox()
        # Add guidance message if no Excel columns available
        if not self.excel_columns:
            self.excel_column_combo.addItem("(엑셀 파일을 먼저 로드하세요)")
        else:
            self.excel_column_combo.addItems(self.excel_columns)
        excel_layout.addWidget(self.excel_column_combo)
        self.excel_column_widget.setLayout(excel_layout)
        self.excel_column_widget.setVisible(False)
        search_layout.addWidget(self.excel_column_widget)
        
        # Connect radio buttons to show/hide widgets
        self.fixed_text_radio.toggled.connect(self.fixed_text_widget.setVisible)
        self.excel_column_radio.toggled.connect(self.excel_column_widget.setVisible)
        self.excel_column_radio.toggled.connect(self._on_excel_column_toggled)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Search region configuration
        region_group = QGroupBox("검색 영역")
        region_layout = QVBoxLayout()
        
        # Search scope selection
        scope_layout = QHBoxLayout()
        scope_layout.addWidget(QLabel("검색 범위:"))
        
        self.search_scope_combo = QComboBox()
        # Dynamically add monitor options
        self._populate_monitor_options()
        self.search_scope_combo.currentIndexChanged.connect(self._on_search_scope_changed)
        scope_layout.addWidget(self.search_scope_combo)
        scope_layout.addStretch()
        region_layout.addLayout(scope_layout)
        
        # Region display
        self.region_label = QLabel("전체 화면 (모든 모니터)")
        if self.region:
            self.region_label.setText(
                f"영역: ({self.region[0]}, {self.region[1]}) "
                f"크기: {self.region[2]}x{self.region[3]}"
            )
            self.search_scope_combo.setCurrentIndex(len(self.monitors) + 1)  # Set to "특정 영역 선택"
        region_layout.addWidget(self.region_label)
        
        # Region buttons
        self.region_buttons_widget = QWidget()
        region_btn_layout = QHBoxLayout()
        region_btn_layout.setContentsMargins(0, 0, 0, 0)
        
        self.select_region_btn = QPushButton("영역 선택")
        self.select_region_btn.clicked.connect(self._select_region)
        region_btn_layout.addWidget(self.select_region_btn)
        
        self.clear_region_btn = QPushButton("영역 초기화")
        self.clear_region_btn.clicked.connect(self._clear_region)
        region_btn_layout.addWidget(self.clear_region_btn)
        
        self.preview_region_btn = QPushButton("영역 미리보기")
        self.preview_region_btn.clicked.connect(self._preview_region)
        region_btn_layout.addWidget(self.preview_region_btn)
        
        self.region_buttons_widget.setLayout(region_btn_layout)
        self.region_buttons_widget.setVisible(False)  # Hidden by default
        
        region_layout.addWidget(self.region_buttons_widget)
        region_group.setLayout(region_layout)
        layout.addWidget(region_group)
        
        # Matching options
        options_group = QGroupBox("매칭 옵션")
        options_layout = QFormLayout()
        
        self.exact_match_check = QCheckBox("정확히 일치")
        self.exact_match_check.setToolTip(
            "체크 시: 검색 텍스트와 정확히 일치하는 경우만 찾음\n"
            "체크 해제 시: 부분 일치도 허용"
        )
        options_layout.addRow("매칭 방식:", self.exact_match_check)
        
        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setRange(0.0, 1.0)
        self.confidence_spin.setSingleStep(0.05)
        self.confidence_spin.setValue(0.5)
        self.confidence_spin.setToolTip("OCR 인식 신뢰도 (0.0~1.0)")
        options_layout.addRow("인식 신뢰도:", self.confidence_spin)
        
        self.normalize_text_check = QCheckBox("특수 문자 정규화")
        self.normalize_text_check.setToolTip(
            "체크 시: 전각 문자를 반각으로 변환\n"
            "예: '：' → ':', '（）' → '()', '　' → ' '"
        )
        options_layout.addRow("텍스트 처리:", self.normalize_text_check)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Click options
        click_group = QGroupBox("클릭 옵션")
        click_layout = QFormLayout()
        
        self.click_on_found_check = QCheckBox("찾은 후 클릭")
        self.click_on_found_check.setChecked(True)
        click_layout.addRow("동작:", self.click_on_found_check)
        
        # Click type selection
        click_type_widget = QWidget()
        click_type_layout = QHBoxLayout()
        click_type_layout.setContentsMargins(0, 0, 0, 0)
        click_type_layout.addWidget(QLabel("클릭 유형:"))
        self.click_type_combo = QComboBox()
        self.click_type_combo.addItems(["한번 클릭", "더블 클릭"])
        self.click_type_combo.setCurrentIndex(0)
        click_type_layout.addWidget(self.click_type_combo)
        click_type_layout.addStretch()
        click_type_widget.setLayout(click_type_layout)
        click_layout.addRow("", click_type_widget)
        
        # Enable/disable click type based on click checkbox
        self.click_on_found_check.toggled.connect(self.click_type_combo.setEnabled)
        
        # Click offset
        offset_widget = QWidget()
        offset_layout = QHBoxLayout()
        offset_layout.setContentsMargins(0, 0, 0, 0)
        
        offset_layout.addWidget(QLabel("X:"))
        self.offset_x_spin = QSpinBox()
        self.offset_x_spin.setRange(-100, 100)
        self.offset_x_spin.setValue(0)
        self.offset_x_spin.setToolTip("텍스트 중심에서 X 오프셋")
        offset_layout.addWidget(self.offset_x_spin)
        
        offset_layout.addWidget(QLabel("Y:"))
        self.offset_y_spin = QSpinBox()
        self.offset_y_spin.setRange(-100, 100)
        self.offset_y_spin.setValue(0)
        self.offset_y_spin.setToolTip("텍스트 중심에서 Y 오프셋")
        offset_layout.addWidget(self.offset_y_spin)
        
        offset_widget.setLayout(offset_layout)
        click_layout.addRow("클릭 오프셋:", offset_widget)
        
        click_group.setLayout(click_layout)
        layout.addWidget(click_group)
        
        # Test button
        self.test_btn = QPushButton("테스트")
        self.test_btn.clicked.connect(self._test_search)
        layout.addWidget(self.test_btn)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def accept(self):
        """Validate dialog before accepting"""
        # Check if Excel column is selected but empty
        if self.excel_column_radio.isChecked():
            if not self.excel_column_combo.currentText() or self.excel_column_combo.currentText() == "(엑셀 파일을 먼저 로드하세요)":
                QMessageBox.warning(self, "경고", 
                    "엑셀 열을 선택하세요.\n\n"
                    "엑셀 파일이 로드되지 않았다면,\n"
                    "먼저 엑셀 탭에서 파일을 불러오세요.")
                return
        elif self.fixed_text_radio.isChecked():
            if not self.search_text_edit.text().strip():
                QMessageBox.warning(self, "경고", "검색할 텍스트를 입력하세요.")
                return
        
        # Update step with current dialog values before accepting
        self._update_step_from_dialog()
        
        # All validations passed, accept the dialog
        super().accept()
    
    def _update_step_from_dialog(self):
        """Update step object with current dialog values"""
        print(f"DEBUG: _update_step_from_dialog called, current region: {self.region}")
        
        # Update basic properties
        self.step.name = self.name_edit.text()
        
        # Update search text/column
        if self.fixed_text_radio.isChecked():
            self.step.search_text = self.search_text_edit.text()
            self.step.excel_column = None
        else:
            # Convert Excel column to variable format like KeyboardTypeStep
            column_text = self.excel_column_combo.currentText()
            # Remove any error suffixes
            if column_text.endswith(" (열을 찾을 수 없음)"):
                column_text = column_text.replace(" (열을 찾을 수 없음)", "")
            self.step.search_text = f"${{{column_text}}}"
            self.step.excel_column = None  # Don't store separately
        
        # Update region - CRITICAL
        # Ensure region is stored as tuple for consistency
        if self.region:
            if isinstance(self.region, list):
                self.step.region = tuple(self.region)
            else:
                self.step.region = self.region
        else:
            self.step.region = None
        print(f"DEBUG: Updated step.region to: {self.step.region} (type: {type(self.step.region)})")
        
        # Update matching options
        self.step.exact_match = self.exact_match_check.isChecked()
        self.step.confidence = self.confidence_spin.value()
        self.step.normalize_text = self.normalize_text_check.isChecked()
        
        # Update click options
        self.step.click_on_found = self.click_on_found_check.isChecked()
        self.step.click_offset = (self.offset_x_spin.value(), self.offset_y_spin.value())
        self.step.double_click = (self.click_type_combo.currentIndex() == 1)
        
        # Add screen stabilization delay option
        self.step.screen_delay = getattr(self.step, 'screen_delay', 0.3)  # Default 300ms
        
        print(f"DEBUG: Step updated - region: {self.step.region}, search_text: {self.step.search_text}")
    
    def _on_excel_column_toggled(self, checked):
        """Handle Excel column radio button toggle"""
        if checked and not self.excel_columns:
            # Show a message if no Excel columns are available
            QMessageBox.information(self, "알림", 
                "엑셀 열을 사용하려면 먼저 엑셀 파일을 로드해야 합니다.\n\n"
                "1. 엑셀 탭으로 이동하세요\n"
                "2. 엑셀 파일을 불러오세요\n"
                "3. 다시 이 설정으로 돌아와서 엑셀 열을 선택하세요")
        
    def load_step_data(self):
        """Load data from step"""
        self._loading_data = True  # Set flag to prevent region reset
        
        # Refresh region from step to ensure we have the latest data
        # Convert list to tuple if needed for consistency
        if self.step.region:
            self.region = tuple(self.step.region) if isinstance(self.step.region, list) else self.step.region
        else:
            self.region = None
        print(f"DEBUG [load_step_data]: Loading step data - region: {self.region} (type: {type(self.region)})")
        
        self.name_edit.setText(self.step.name)
        
        # Set search method
        # Check if search_text contains variable reference
        import re
        variable_pattern = r'^\$\{([^}]+)\}$'
        variable_match = re.match(variable_pattern, self.step.search_text) if self.step.search_text else None
        
        if self.step.excel_column or variable_match:
            self.excel_column_radio.setChecked(True)
            # Determine column name
            column_name = self.step.excel_column
            if not column_name and variable_match:
                # Extract column name from variable format
                column_name = variable_match.group(1)
                print(f"DEBUG [load_step_data]: Extracted column name '{column_name}' from search_text '{self.step.search_text}'")
            
            if column_name:
                # Find and select the column
                index = self.excel_column_combo.findText(column_name)
                if index >= 0:
                    self.excel_column_combo.setCurrentIndex(index)
                else:
                    # Column not found in current Excel file
                    if self.excel_columns:
                        # Add the missing column temporarily to preserve the setting
                        self.excel_column_combo.addItem(f"{column_name} (열을 찾을 수 없음)")
                        self.excel_column_combo.setCurrentText(f"{column_name} (열을 찾을 수 없음)")
        else:
            self.fixed_text_radio.setChecked(True)
            self.search_text_edit.setText(self.step.search_text)
        
        # Set search scope based on region
        try:
            if self.region:
                # Check if region matches any monitor exactly
                matched_monitor_index = None
                for i, monitor in enumerate(self.monitors):
                    if (self.region[0] == monitor['x'] and
                        self.region[1] == monitor['y'] and
                        self.region[2] == monitor['width'] and
                        self.region[3] == monitor['height']):
                        matched_monitor_index = i + 1  # +1 because index 0 is "전체 화면"
                        break
                
                if matched_monitor_index:
                    self.search_scope_combo.setCurrentIndex(matched_monitor_index)
                else:
                    # Custom region
                    self.search_scope_combo.setCurrentIndex(len(self.monitors) + 1)  # Last option
                    # Ensure region label is updated for custom region
                    self.region_label.setText(
                        f"영역: ({self.region[0]}, {self.region[1]}) "
                        f"크기: {self.region[2]}x{self.region[3]}"
                    )
                    # Only set visibility if widget exists
                    if hasattr(self, 'region_buttons_widget'):
                        self.region_buttons_widget.setVisible(True)
            else:
                self.search_scope_combo.setCurrentIndex(0)  # 전체 화면
        except Exception as e:
            print(f"ERROR [load_step_data]: Failed to set search scope - {e}")
            import traceback
            traceback.print_exc()
            # Fallback to full screen
            self.search_scope_combo.setCurrentIndex(0)
        
        # Set options
        self.exact_match_check.setChecked(self.step.exact_match)
        self.confidence_spin.setValue(self.step.confidence)
        self.normalize_text_check.setChecked(getattr(self.step, 'normalize_text', False))
        self.click_on_found_check.setChecked(self.step.click_on_found)
        self.offset_x_spin.setValue(self.step.click_offset[0])
        self.offset_y_spin.setValue(self.step.click_offset[1])
        
        # Set click type
        if hasattr(self.step, 'double_click'):
            self.click_type_combo.setCurrentIndex(1 if self.step.double_click else 0)
        
        # Reset loading flag
        self._loading_data = False
        
    def _select_region(self):
        """Select screen region"""
        # First, show monitor selection dialog
        monitor_dialog = QDialog(self)
        monitor_dialog.setWindowTitle("모니터 선택")
        monitor_dialog.setModal(True)
        
        layout = QVBoxLayout()
        layout.addWidget(QLabel("영역을 선택할 모니터를 선택하세요:"))
        
        # Monitor list widget
        monitor_list = QComboBox()
        for i, monitor in enumerate(self.monitors):
            if monitor['is_primary']:
                name = f"주 모니터 ({monitor['width']}x{monitor['height']})"
            else:
                # Determine position-based name - check Y axis first
                x_offset_threshold = 300
                
                if monitor['y'] < -100:  # Above primary monitor
                    if abs(monitor['x']) < x_offset_threshold:
                        pos_name = "위쪽"
                    elif monitor['x'] < -x_offset_threshold:
                        pos_name = "왼쪽 위"
                    else:
                        pos_name = "오른쪽 위"
                elif monitor['y'] > 100:  # Below primary monitor
                    if abs(monitor['x']) < x_offset_threshold:
                        pos_name = "아래쪽"
                    elif monitor['x'] < -x_offset_threshold:
                        pos_name = "왼쪽 아래"
                    else:
                        pos_name = "오른쪽 아래"
                elif monitor['x'] < -100:  # Left of primary monitor
                    pos_name = "왼쪽"
                elif monitor['x'] > 100:  # Right of primary monitor
                    pos_name = "오른쪽"
                else:
                    pos_name = "보조"
                name = f"{pos_name} 모니터 ({monitor['width']}x{monitor['height']})"
            monitor_list.addItem(name)
        
        layout.addWidget(monitor_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        ok_button = QPushButton("확인")
        cancel_button = QPushButton("취소")
        button_layout.addWidget(ok_button)
        button_layout.addWidget(cancel_button)
        layout.addLayout(button_layout)
        
        monitor_dialog.setLayout(layout)
        
        # Store selected monitor
        selected_monitor = [None]
        
        def on_ok():
            selected_monitor[0] = self.monitors[monitor_list.currentIndex()]
            monitor_dialog.accept()
            
        def on_cancel():
            monitor_dialog.reject()
            
        ok_button.clicked.connect(on_ok)
        cancel_button.clicked.connect(on_cancel)
        
        if monitor_dialog.exec_() == QDialog.Accepted and selected_monitor[0]:
            # Hide dialog temporarily
            self.hide()
            # Store selected monitor bounds
            self._selected_monitor_bounds = selected_monitor[0]
            # Give time for dialog to hide before showing ROI selector
            QTimer.singleShot(200, self._show_region_selector)
        
    def _show_region_selector(self):
        """Show region selector overlay"""
        try:
            print("DEBUG: Creating ROI selector")
            # Create ROI selector with monitor bounds if available
            monitor_bounds = getattr(self, '_selected_monitor_bounds', None)
            print(f"DEBUG: monitor_bounds: {monitor_bounds}")
            self.roi_selector = ROISelectorOverlay(parent=None, monitor_bounds=monitor_bounds)
            print(f"DEBUG: ROI selector created: {self.roi_selector}")
            
            # Connect signals
            print("DEBUG: Connecting selectionComplete signal")
            self.roi_selector.selectionComplete.connect(self._on_region_selected)
            print("DEBUG: selectionComplete connected")
            
            print("DEBUG: Connecting selectionCancelled signal")
            self.roi_selector.selectionCancelled.connect(lambda: self.show())
            print("DEBUG: selectionCancelled connected")
            
            print("DEBUG: Starting ROI selection")
            self.roi_selector.start_selection()
            print("DEBUG: start_selection() called")
            # Don't call show() separately - start_selection() already calls exec_()
            
        except Exception as e:
            print(f"DEBUG: Error in _show_region_selector: {e}")
            import traceback
            traceback.print_exc()
            self.show()
            
    def _on_selection_cancelled(self):
        """Handle selection cancellation"""
        print("DEBUG: Selection cancelled")
        self.show()
        
    def _on_region_selected(self, region: Tuple[int, int, int, int]):
        """Handle region selection"""
        print(f"DEBUG: _on_region_selected called with region: {region}, type: {type(region)}")
        try:
            # Ensure region is properly formatted
            if region and len(region) == 4:
                # Convert all values to integers to avoid any type issues
                formatted_region = tuple(int(x) for x in region)
                self.region = formatted_region
                print(f"DEBUG: set region successful with formatted region: {formatted_region}")
                self.region_label.setText(
                    f"영역: ({formatted_region[0]}, {formatted_region[1]}) "
                    f"크기: {formatted_region[2]}x{formatted_region[3]}"
                )
                print(f"DEBUG: region_label updated")
            else:
                print(f"DEBUG: Invalid region: {region}")
                self.region = None
                self.region_label.setText("전체 화면")
            
            print(f"DEBUG: About to restore dialog visibility")
            # Restore dialog visibility
            self.show()
            self.raise_()
            self.activateWindow()
            print(f"DEBUG: Dialog visibility restored")
        except Exception as e:
            print(f"DEBUG: Error in _on_region_selected: {e}")
            import traceback
            traceback.print_exc()
            # Still try to show the dialog
            self.region = None
            self.region_label.setText("전체 화면")
            self.show()
        
    def _clear_region(self):
        """Clear selected region"""
        self.region = None
        self.region_label.setText("영역을 선택하세요")
        # Keep the scope combo at "특정 영역 선택"
        self.search_scope_combo.setCurrentIndex(len(self.monitors) + 1)
        
    def _preview_region(self):
        """Preview selected region"""
        if not self.region:
            QMessageBox.information(self, "알림", "선택된 영역이 없습니다.")
            return
            
        try:
            # Take screenshot of region
            x, y, width, height = self.region
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            
            # Convert to QPixmap
            # Save to bytes first to avoid direct conversion issues
            import io
            bytes_io = io.BytesIO()
            screenshot.save(bytes_io, format='PNG')
            bytes_io.seek(0)
            
            pixmap = QPixmap()
            pixmap.loadFromData(bytes_io.read())
            
            if pixmap.isNull():
                QMessageBox.warning(self, "경고", "영역 미리보기를 생성할 수 없습니다.")
                return
            
            # Create preview dialog
            preview_dialog = QDialog(self)
            preview_dialog.setWindowTitle("영역 미리보기")
            layout = QVBoxLayout()
            
            label = QLabel()
            # Scale pixmap if too large
            if not pixmap.isNull() and (pixmap.width() > 800 or pixmap.height() > 600):
                pixmap = pixmap.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            if not pixmap.isNull():
                label.setPixmap(pixmap)
            layout.addWidget(label)
            
            # Add region info
            info_label = QLabel(f"영역: ({x}, {y}) - 크기: {width}x{height}")
            layout.addWidget(info_label)
            
            preview_dialog.setLayout(layout)
            preview_dialog.exec_()
            
        except Exception as e:
            print(f"DEBUG: Error in preview: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.warning(self, "오류", f"미리보기 생성 중 오류가 발생했습니다:\n{str(e)}")
            
    def _populate_monitor_options(self):
        """Populate monitor options in combo box"""
        options = ["전체 화면 (모든 모니터)"]
        
        # Add each monitor as an option
        for i, monitor in enumerate(self.monitors):
            if monitor['is_primary']:
                name = f"주 모니터 ({monitor['width']}x{monitor['height']})"
            else:
                # Determine position-based name - check Y axis first
                # Consider small X offsets (< 300px) as vertically aligned
                x_offset_threshold = 300
                
                if monitor['y'] < -100:  # Above primary monitor
                    if abs(monitor['x']) < x_offset_threshold:
                        pos_name = "위쪽"
                    elif monitor['x'] < -x_offset_threshold:
                        pos_name = "왼쪽 위"
                    else:
                        pos_name = "오른쪽 위"
                elif monitor['y'] > 100:  # Below primary monitor
                    if abs(monitor['x']) < x_offset_threshold:
                        pos_name = "아래쪽"
                    elif monitor['x'] < -x_offset_threshold:
                        pos_name = "왼쪽 아래"
                    else:
                        pos_name = "오른쪽 아래"
                elif monitor['x'] < -100:  # Left of primary monitor
                    pos_name = "왼쪽"
                elif monitor['x'] > 100:  # Right of primary monitor
                    pos_name = "오른쪽"
                else:
                    pos_name = "보조"
                name = f"{pos_name} 모니터 ({monitor['width']}x{monitor['height']})"
            options.append(name)
        
        # Add custom region selection at the end
        options.append("특정 영역 선택")
        
        self.search_scope_combo.addItems(options)
        
    def _on_search_scope_changed(self, index):
        """Handle search scope change"""
        # Don't reset region if we're loading data
        if self._loading_data:
            return
        
        # Check if widgets are initialized
        if not hasattr(self, 'region_buttons_widget'):
            print("DEBUG: region_buttons_widget not yet initialized, skipping")
            return
            
        if index == 0:  # 전체 화면 (모든 모니터)
            self.region = None
            self.region_label.setText("전체 화면 (모든 모니터)")
            self.region_buttons_widget.setVisible(False)
        elif index > 0 and index <= len(self.monitors):  # Specific monitor
            # Get the selected monitor
            monitor = self.monitors[index - 1]
            self.region = (
                monitor['x'], 
                monitor['y'],
                monitor['width'],
                monitor['height']
            )
            # Create display text
            if monitor['is_primary']:
                monitor_name = "주 모니터"
            else:
                # Use position-based name - check Y axis first
                x_offset_threshold = 300
                
                if monitor['y'] < -100:  # Above primary monitor
                    if abs(monitor['x']) < x_offset_threshold:
                        monitor_name = "위쪽 모니터"
                    elif monitor['x'] < -x_offset_threshold:
                        monitor_name = "왼쪽 위 모니터"
                    else:
                        monitor_name = "오른쪽 위 모니터"
                elif monitor['y'] > 100:  # Below primary monitor
                    if abs(monitor['x']) < x_offset_threshold:
                        monitor_name = "아래쪽 모니터"
                    elif monitor['x'] < -x_offset_threshold:
                        monitor_name = "왼쪽 아래 모니터"
                    else:
                        monitor_name = "오른쪽 아래 모니터"
                elif monitor['x'] < -100:  # Left of primary monitor
                    monitor_name = "왼쪽 모니터"
                elif monitor['x'] > 100:  # Right of primary monitor
                    monitor_name = "오른쪽 모니터"
                else:
                    monitor_name = "보조 모니터"
            
            self.region_label.setText(
                f"{monitor_name}: ({monitor['x']}, {monitor['y']}) "
                f"크기: {monitor['width']}x{monitor['height']}"
            )
            self.region_buttons_widget.setVisible(False)
        else:  # 특정 영역 선택
            print(f"DEBUG [_on_search_scope_changed]: Custom region selected, current region: {self.region}")
            if not self.region:
                self.region_label.setText("영역을 선택하세요")
            else:
                # Update label with current region
                self.region_label.setText(
                    f"영역: ({self.region[0]}, {self.region[1]}) "
                    f"크기: {self.region[2]}x{self.region[3]}"
                )
            self.region_buttons_widget.setVisible(True)
        
    def _test_search(self):
        """Test text search"""
        # Get search text
        if self.fixed_text_radio.isChecked():
            search_text = self.search_text_edit.text()
            if not search_text:
                QMessageBox.warning(self, "경고", "검색할 텍스트를 입력하세요.")
                return
        else:
            if self.excel_column_combo.currentText():
                search_text = f"[{self.excel_column_combo.currentText()} 열의 데이터]"
            else:
                QMessageBox.warning(self, "경고", "엑셀 열을 선택하세요.")
                return
        
        # Perform test search
        self.hide()
        QTimer.singleShot(300, lambda: self._perform_test_search(search_text))
        
    def _perform_test_search(self, search_text: str):
        """Perform the actual test search"""
        try:
            print(f"DEBUG: Starting test search for: {search_text}")
            print(f"DEBUG: Current region: {self.region}")
            
            # For testing with Excel column, use sample text
            if self.excel_column_radio.isChecked():
                test_text = QMessageBox.getText(
                    self, "테스트 텍스트",
                    f"{self.excel_column_combo.currentText()} 열의 테스트 값을 입력하세요:",
                    text="홍길동"
                )
                if test_text[1]:
                    search_text = test_text[0]
                else:
                    self.show()
                    return
            
            print("DEBUG: Extracting text from region...")
            # Extract text from region
            results = self.text_extractor.extract_text_from_region(
                self.region, 
                self.confidence_spin.value()
            )
            print(f"DEBUG: Found {len(results)} text results")
            
            print("DEBUG: Finding matching text...")
            # Find matching text
            found_result = self.text_extractor.find_text(
                search_text,
                region=self.region,
                exact_match=self.exact_match_check.isChecked(),
                confidence_threshold=self.confidence_spin.value()
            )
            
            if found_result:
                print(f"DEBUG: Found text at {found_result.center}")
                # Show result
                if self.click_on_found_check.isChecked():
                    # Calculate click position
                    click_x = found_result.center[0] + self.offset_x_spin.value()
                    click_y = found_result.center[1] + self.offset_y_spin.value()
                    
                    message = (
                        f"텍스트 '{search_text}'을(를) 찾았습니다!\n"
                        f"위치: ({found_result.center[0]}, {found_result.center[1]})\n"
                        f"클릭 위치: ({click_x}, {click_y})\n"
                        f"신뢰도: {found_result.confidence:.2f}"
                    )
                else:
                    message = (
                        f"텍스트 '{search_text}'을(를) 찾았습니다!\n"
                        f"위치: ({found_result.center[0]}, {found_result.center[1]})\n"
                        f"신뢰도: {found_result.confidence:.2f}"
                    )
                
                # Highlight found text briefly
                self._highlight_found_text(found_result)
                
            else:
                print("DEBUG: Text not found")
                # Show all found text for debugging
                if results:
                    all_text = "\n".join([f"- {r.text} (신뢰도: {r.confidence:.2f})" 
                                         for r in results[:10]])  # Show max 10
                else:
                    all_text = "텍스트를 찾을 수 없습니다."
                    
                message = (
                    f"텍스트 '{search_text}'을(를) 찾을 수 없습니다.\n\n"
                    f"발견된 텍스트:\n{all_text}"
                )
            
            QMessageBox.information(self, "테스트 결과", message)
            
        except Exception as e:
            print(f"DEBUG: Error in test search: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "오류", f"테스트 중 오류 발생: {str(e)}")
        finally:
            self.show()
            
    def _highlight_found_text(self, result):
        """Briefly highlight the found text on screen"""
        # This is a simplified version - in production, you might want
        # to create a temporary overlay window
        import time
        x, y = result.center
        pyautogui.moveTo(x, y, duration=0.5)
        
    def _perform_test_search_immediate(self, search_text: str):
        """Perform test search without hiding dialog (for Windows compatibility)"""
        loading_msg = None
        try:
            print(f"DEBUG: Starting immediate test search for: {search_text}")
            print(f"DEBUG: Current region: {self.region}")
            
            # Extract text from region first (before showing loading)
            results = self.text_extractor.extract_text_from_region(
                self.region, 
                self.confidence_spin.value()
            )
            print(f"DEBUG: Found {len(results)} text results")
            
            # Find matching text
            found_result = self.text_extractor.find_text(
                search_text,
                region=self.region,
                exact_match=self.exact_match_check.isChecked(),
                confidence_threshold=self.confidence_spin.value()
            )
            
            if found_result:
                print(f"DEBUG: Found text at {found_result.center}")
                # Show result
                if self.click_on_found_check.isChecked():
                    # Calculate click position
                    click_x = found_result.center[0] + self.offset_x_spin.value()
                    click_y = found_result.center[1] + self.offset_y_spin.value()
                    
                    message = (
                        f"텍스트 '{search_text}'을(를) 찾았습니다!\n\n"
                        f"위치: ({found_result.center[0]}, {found_result.center[1]})\n"
                        f"클릭 위치: ({click_x}, {click_y})\n"
                        f"신뢰도: {found_result.confidence:.2f}"
                    )
                else:
                    message = (
                        f"텍스트 '{search_text}'을(를) 찾았습니다!\n\n"
                        f"위치: ({found_result.center[0]}, {found_result.center[1]})\n"
                        f"신뢰도: {found_result.confidence:.2f}"
                    )
                
                QMessageBox.information(self, "테스트 성공", message)
                
                # Highlight found text
                self._highlight_found_text(found_result)
                
            else:
                print("DEBUG: Text not found")
                # Show all found text for debugging
                if results:
                    all_text = "\n".join([f"• {r.text} (신뢰도: {r.confidence:.2f})" 
                                         for r in results[:10]])  # Show max 10
                else:
                    all_text = "인식된 텍스트가 없습니다."
                    
                message = (
                    f"텍스트 '{search_text}'을(를) 찾을 수 없습니다.\n\n"
                    f"검색 영역에서 발견된 텍스트:\n{all_text}"
                )
                
                QMessageBox.warning(self, "테스트 결과", message)
                
        except Exception as e:
            print(f"DEBUG: Error in immediate test search: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(self, "오류", f"테스트 중 오류 발생:\n{str(e)}")
        
    def get_step_data(self) -> Dict[str, Any]:
        """Get step configuration data"""
        # Get excel column value, ensuring it's valid
        excel_column = None
        if self.excel_column_radio.isChecked():
            column_text = self.excel_column_combo.currentText()
            print(f"DEBUG [get_step_data]: Excel column radio checked, combo text: '{column_text}'")
            # Only set excel_column if it's a valid column name (not placeholder text)
            if column_text and column_text != "(엑셀 파일을 먼저 로드하세요)":
                # Remove the "(열을 찾을 수 없음)" suffix if present
                if column_text.endswith(" (열을 찾을 수 없음)"):
                    excel_column = column_text.replace(" (열을 찾을 수 없음)", "")
                    print(f"DEBUG [get_step_data]: Stripped suffix, excel_column: '{excel_column}'")
                else:
                    excel_column = column_text
                    print(f"DEBUG [get_step_data]: Using column as-is: '{excel_column}'")
            else:
                print(f"DEBUG [get_step_data]: Invalid column text, setting to None")
        else:
            print(f"DEBUG [get_step_data]: Fixed text radio checked")
        
        # KeyboardTypeStep처럼 Excel 열을 변수 형식으로 search_text에 저장
        search_text = ""
        if self.fixed_text_radio.isChecked():
            search_text = self.search_text_edit.text()
        elif excel_column:
            # Excel 열이 선택된 경우, 변수 형식으로 변환
            search_text = f"${{{excel_column}}}"
            print(f"DEBUG [get_step_data]: Converting excel_column '{excel_column}' to variable format: '{search_text}'")
        
        # Ensure region is tuple for consistency
        region_data = None
        if self.region:
            region_data = tuple(self.region) if isinstance(self.region, list) else self.region
        
        result = {
            'name': self.name_edit.text() or "텍스트 검색",
            'search_text': search_text,  # Excel 열도 변수 형식으로 여기에 저장
            'excel_column': excel_column,  # 호환성을 위해 유지
            'region': region_data,
            'exact_match': self.exact_match_check.isChecked(),
            'confidence': self.confidence_spin.value(),
            'normalize_text': self.normalize_text_check.isChecked(),
            'click_on_found': self.click_on_found_check.isChecked(),
            'click_offset': (self.offset_x_spin.value(), self.offset_y_spin.value()),
            'double_click': self.click_type_combo.currentIndex() == 1,  # True if "더블 클릭" selected
            'screen_delay': getattr(self.step, 'screen_delay', 0.3)  # Include screen delay
        }
        
        print(f"DEBUG [get_step_data]: Returning data with excel_column: '{result['excel_column']}'")
        print(f"DEBUG [get_step_data]: Returning data with region: {result['region']}")
        return result