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
from vision.text_extractor import TextExtractor
import pyautogui

class TextSearchStepDialog(QDialog):
    """Dialog for configuring text search steps"""
    
    def __init__(self, step: Optional[TextSearchStep] = None, 
                 excel_columns: list = None, parent=None):
        super().__init__(parent)
        self.step = step or TextSearchStep()
        self.excel_columns = excel_columns or []
        self.region = self.step.region
        self.text_extractor = TextExtractor()
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
        self.excel_column_combo.addItems(self.excel_columns)
        excel_layout.addWidget(self.excel_column_combo)
        self.excel_column_widget.setLayout(excel_layout)
        self.excel_column_widget.setVisible(False)
        search_layout.addWidget(self.excel_column_widget)
        
        # Connect radio buttons to show/hide widgets
        self.fixed_text_radio.toggled.connect(self.fixed_text_widget.setVisible)
        self.excel_column_radio.toggled.connect(self.excel_column_widget.setVisible)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Search region configuration
        region_group = QGroupBox("검색 영역")
        region_layout = QVBoxLayout()
        
        # Region display
        self.region_label = QLabel("전체 화면")
        if self.region:
            self.region_label.setText(
                f"영역: ({self.region[0]}, {self.region[1]}) "
                f"크기: {self.region[2]}x{self.region[3]}"
            )
        region_layout.addWidget(self.region_label)
        
        # Region buttons
        region_btn_layout = QHBoxLayout()
        
        self.select_region_btn = QPushButton("영역 선택")
        self.select_region_btn.clicked.connect(self._select_region)
        region_btn_layout.addWidget(self.select_region_btn)
        
        self.clear_region_btn = QPushButton("영역 초기화")
        self.clear_region_btn.clicked.connect(self._clear_region)
        region_btn_layout.addWidget(self.clear_region_btn)
        
        self.preview_region_btn = QPushButton("영역 미리보기")
        self.preview_region_btn.clicked.connect(self._preview_region)
        region_btn_layout.addWidget(self.preview_region_btn)
        
        region_layout.addLayout(region_btn_layout)
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
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Click options
        click_group = QGroupBox("클릭 옵션")
        click_layout = QFormLayout()
        
        self.click_after_find_check = QCheckBox("찾은 후 클릭")
        self.click_after_find_check.setChecked(True)
        click_layout.addRow("동작:", self.click_after_find_check)
        
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
        self.click_after_find_check.toggled.connect(self.click_type_combo.setEnabled)
        
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
        
    def load_step_data(self):
        """Load data from step"""
        self.name_edit.setText(self.step.name)
        
        # Set search method
        if self.step.excel_column:
            self.excel_column_radio.setChecked(True)
            # Find and select the column
            index = self.excel_column_combo.findText(self.step.excel_column)
            if index >= 0:
                self.excel_column_combo.setCurrentIndex(index)
        else:
            self.fixed_text_radio.setChecked(True)
            self.search_text_edit.setText(self.step.search_text)
        
        # Set options
        self.exact_match_check.setChecked(self.step.exact_match)
        self.confidence_spin.setValue(self.step.confidence)
        self.click_after_find_check.setChecked(self.step.click_after_find)
        self.offset_x_spin.setValue(self.step.click_offset[0])
        self.offset_y_spin.setValue(self.step.click_offset[1])
        
        # Set click type
        if hasattr(self.step, 'double_click'):
            self.click_type_combo.setCurrentIndex(1 if self.step.double_click else 0)
        
    def _select_region(self):
        """Select screen region"""
        # Hide dialog temporarily
        self.hide()
        # Give time for dialog to hide before showing ROI selector
        QTimer.singleShot(200, self._show_region_selector)
        
    def _show_region_selector(self):
        """Show region selector overlay"""
        try:
            print("DEBUG: Creating ROI selector")
            # Create ROI selector as a top-level window
            self.roi_selector = ROISelectorOverlay(parent=None)
            self.roi_selector.selectionComplete.connect(self._on_region_selected)
            self.roi_selector.selectionCancelled.connect(lambda: self.show())
            print("DEBUG: Starting ROI selection")
            self.roi_selector.start_selection()
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
        try:
            # Ensure region is properly formatted
            if region and len(region) == 4:
                # Convert all values to integers to avoid any type issues
                formatted_region = tuple(int(x) for x in region)
                self.region = formatted_region
                self.region_label.setText(
                    f"영역: ({formatted_region[0]}, {formatted_region[1]}) "
                    f"크기: {formatted_region[2]}x{formatted_region[3]}"
                )
            else:
                self.region = None
                self.region_label.setText("전체 화면")
            
            # Restore dialog visibility
            self.show()
            self.raise_()
            self.activateWindow()
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
        self.region_label.setText("전체 화면")
        
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
            if pixmap.width() > 800 or pixmap.height() > 600:
                pixmap = pixmap.scaled(800, 600, Qt.KeepAspectRatio, Qt.SmoothTransformation)
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
                self.region,
                self.exact_match_check.isChecked(),
                self.confidence_spin.value()
            )
            
            if found_result:
                print(f"DEBUG: Found text at {found_result.center}")
                # Show result
                if self.click_after_find_check.isChecked():
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
                self.region,
                self.exact_match_check.isChecked(),
                self.confidence_spin.value()
            )
            
            if found_result:
                print(f"DEBUG: Found text at {found_result.center}")
                # Show result
                if self.click_after_find_check.isChecked():
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
        return {
            'name': self.name_edit.text() or "텍스트 검색",
            'search_text': self.search_text_edit.text() if self.fixed_text_radio.isChecked() else "",
            'excel_column': self.excel_column_combo.currentText() if self.excel_column_radio.isChecked() else None,
            'region': self.region,
            'exact_match': self.exact_match_check.isChecked(),
            'confidence': self.confidence_spin.value(),
            'click_after_find': self.click_after_find_check.isChecked(),
            'click_offset': (self.offset_x_spin.value(), self.offset_y_spin.value()),
            'double_click': self.click_type_combo.currentIndex() == 1  # True if "더블 클릭" selected
        }