"""
Configuration dialogs for image-based macro steps
"""

import os
from typing import Optional, Dict, Any, Tuple
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QDoubleSpinBox, QGroupBox, QFileDialog,
    QDialogButtonBox, QMessageBox, QCheckBox, QComboBox, QWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QPixmap, QImage, QKeySequence
from PyQt5.QtWidgets import QShortcut
from core.macro_types import MacroStep, WaitImageStep, StepType
from vision.image_matcher import ImageMatcher
from config.settings import Settings
from ui.widgets.roi_selector import ROISelectorOverlay
from utils.clipboard_utils import save_clipboard_image
from utils.monitor_utils import get_monitor_info

class ImageStepDialog(QDialog):
    """Base dialog for image step configuration"""
    
    def __init__(self, step: Optional[MacroStep] = None, 
                 settings: Optional[Settings] = None,
                 parent=None):
        super().__init__(parent)
        self.step = step
        self.settings = settings or Settings()
        self.image_matcher = ImageMatcher(self.settings)
        self.monitors = get_monitor_info()  # Get monitor information
        self.region = None  # Selected region
        
        # Step data
        self.step_data: Dict[str, Any] = {}
        if step:
            self.step_data = step.to_dict()
            # Load region from step if available
            if hasattr(step, 'region'):
                self.region = step.region
            
        self.init_ui()
        self.load_step_data()
        
    def init_ui(self):
        """Initialize base UI"""
        self.setModal(True)
        self.setMinimumWidth(600)
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        layout = QVBoxLayout()
        
        # Name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("단계 이름:"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Image selection group
        image_group = QGroupBox("참조 이미지")
        image_layout = QVBoxLayout()
        
        # Image path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("이미지 경로:"))
        self.image_path_input = QLineEdit()
        self.image_path_input.setReadOnly(True)
        path_layout.addWidget(self.image_path_input)
        
        # Browse button
        self.browse_btn = QPushButton("찾아보기...")
        self.browse_btn.clicked.connect(self._browse_image)
        path_layout.addWidget(self.browse_btn)
        
        # Capture button
        self.capture_btn = QPushButton("캡처")
        self.capture_btn.clicked.connect(self._capture_image)
        path_layout.addWidget(self.capture_btn)
        
        # Paste button for clipboard
        self.paste_btn = QPushButton("붙여넣기 (Ctrl+V)")
        self.paste_btn.clicked.connect(self._paste_from_clipboard)
        path_layout.addWidget(self.paste_btn)
        
        # Add Ctrl+V shortcut
        paste_shortcut = QShortcut(QKeySequence("Ctrl+V"), self)
        paste_shortcut.activated.connect(self._paste_from_clipboard)
        
        image_layout.addLayout(path_layout)
        
        # Image preview
        self.image_preview = QLabel()
        self.image_preview.setMinimumHeight(150)
        self.image_preview.setMaximumHeight(300)
        self.image_preview.setScaledContents(False)  # Don't stretch image
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("""
            QLabel {
                border: 1px solid #ccc;
                background-color: #f9f9f9;
            }
        """)
        image_layout.addWidget(self.image_preview)
        
        # Help text
        help_label = QLabel(
            "💡 팁: Shift + Win + S 로 화면을 캡처한 후 Ctrl+V 또는 '붙여넣기' 버튼으로 이미지를 추가할 수 있습니다."
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet("color: #0066cc; font-size: 12px; padding: 5px; background-color: #e6f2ff; border-radius: 3px; margin-top: 5px;")
        image_layout.addWidget(help_label)
        
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)
        
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
        region_layout.addWidget(self.region_label)
        
        # Region buttons (only visible for custom region selection)
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
        
        # Additional controls (implemented by subclasses)
        self.add_custom_controls(layout)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
        
        # Update preview after dialog is shown
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, self._update_preview)
        
    def add_custom_controls(self, layout: QVBoxLayout):
        """Override to add step-specific controls"""
        pass
        
    def _populate_monitor_options(self):
        """Populate monitor options in combo box"""
        options = ["전체 화면 (모든 모니터)"]
        
        # Add each monitor as an option
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
            options.append(name)
        
        # Add custom region selection at the end
        options.append("특정 영역 선택")
        
        self.search_scope_combo.addItems(options)
        
    def _on_search_scope_changed(self, index):
        """Handle search scope change"""
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
            if not self.region:
                self.region_label.setText("영역을 선택하세요")
            self.region_buttons_widget.setVisible(True)
        
    def _browse_image(self):
        """Browse for image file"""
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
        """Capture new reference image"""
        # Show instructions for Windows screen capture
        reply = QMessageBox.question(
            self,
            "화면 캡처 안내",
            "Windows 화면 캡처 도구를 사용하시겠습니까?\n\n"
            "1. Shift + Win + S 키를 눌러 화면 캡처\n"
            "2. 캡처할 영역을 선택\n"
            "3. '붙여넣기' 버튼을 클릭하여 이미지 추가\n\n"
            "이 방법을 사용하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Just show the message and let user use Windows capture
            QMessageBox.information(
                self,
                "안내",
                "지금 Shift + Win + S 를 눌러서 화면을 캡처하세요.\n"
                "캡처 후 '붙여넣기' 버튼을 클릭하세요."
            )
        else:
            # Just show the same instruction for consistency
            QMessageBox.information(
                self,
                "안내",
                "Windows 화면 캡처를 사용하세요:\n\n"
                "1. Shift + Win + S 를 눌러서 화면을 캡처\n"
                "2. 캡처할 영역을 선택\n"
                "3. '붙여넣기' 버튼을 클릭하여 이미지 추가"
            )
        
    def _paste_from_clipboard(self):
        """Paste image from clipboard"""
        # Use the unified clipboard utility
        file_path = save_clipboard_image()
        
        if file_path and os.path.exists(file_path):
            # Update UI
            self.image_path_input.setText(file_path)
            # Delay preview update to ensure dialog is properly sized
            from PyQt5.QtCore import QTimer
            QTimer.singleShot(50, self._update_preview)
            QMessageBox.information(self, "성공", "클립보드에서 이미지를 붙여넣었습니다.")
        else:
            QMessageBox.information(
                self, 
                "안내", 
                "클립보드에 이미지가 없습니다.\n\n"
                "사용 방법:\n"
                "1. Windows: Shift + Win + S 로 화면 캡처\n"
                "2. 이 버튼을 클릭하여 붙여넣기\n\n"
                "참고: WSL 환경에서는 Windows PowerShell을 통해\n"
                "클립보드에 접근합니다."
            )
    
        
    def _update_preview(self):
        """Update image preview"""
        image_path = self.image_path_input.text()
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Get the preview label size
                label_width = self.image_preview.width() - 10  # Account for padding
                label_height = self.image_preview.height() - 10
                
                # Scale to fit preview while keeping aspect ratio
                # Use the smaller of the two dimensions to ensure it fits
                scaled = pixmap.scaled(
                    label_width,
                    label_height,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_preview.setPixmap(scaled)
                
                # Show original size info
                size_text = f"원본 크기: {pixmap.width()} x {pixmap.height()}"
                self.image_preview.setToolTip(size_text)
            else:
                self.image_preview.setText("잘못된 이미지")
                self.image_preview.setToolTip("")
        else:
            self.image_preview.setText("선택된 이미지 없음")
            self.image_preview.setToolTip("")
            
    def _select_region(self):
        """Start region selection"""
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
        # Try simple selector first (better for WSL)
        try:
            # Create ROI selector with monitor bounds if available
            monitor_bounds = getattr(self, '_selected_monitor_bounds', None)
            selector = ROISelectorOverlay(parent=None, monitor_bounds=monitor_bounds)
            
            def on_selection_complete(region):
                try:
                    print(f"DEBUG: ROI selection complete with region: {region}, type: {type(region)}")
                    # Ensure region is properly formatted
                    if region and len(region) == 4:
                        # Convert all values to integers to avoid any type issues
                        formatted_region = tuple(int(x) for x in region)
                        self.region = formatted_region
                        self.region_label.setText(
                            f"선택된 영역: ({formatted_region[0]}, {formatted_region[1]}) "
                            f"크기: {formatted_region[2]}x{formatted_region[3]}"
                        )
                        print(f"DEBUG: set region successful with formatted region: {formatted_region}")
                    else:
                        print(f"DEBUG: Invalid region format: {region}")
                        self.region = None
                        self.region_label.setText("영역을 선택하세요")
                    
                    # Show dialog and ensure it stays visible
                    self.setVisible(True)
                    self.show()
                    self.raise_()
                    self.activateWindow()
                    print(f"DEBUG: dialog.show() successful")
                    
                    # Force dialog to process events
                    from PyQt5.QtWidgets import QApplication
                    QApplication.processEvents()
                    
                    # Delay selector cleanup to ensure dialog is fully shown
                    from PyQt5.QtCore import QTimer
                    QTimer.singleShot(1000, selector.deleteLater)
                except Exception as e:
                    print(f"DEBUG: Error in on_selection_complete: {e}")
                    import traceback
                    traceback.print_exc()
                    # Still try to show the dialog
                    self.setVisible(True)
                    self.show()
                    self.raise_()
                    self.activateWindow()
                    from PyQt5.QtWidgets import QApplication
                    QApplication.processEvents()
                    from PyQt5.QtCore import QTimer
                    QTimer.singleShot(1000, selector.deleteLater)
                
            def on_selection_cancelled():
                self.setVisible(True)
                self.show()
                self.raise_()
                self.activateWindow()
                from PyQt5.QtWidgets import QApplication
                QApplication.processEvents()
                from PyQt5.QtCore import QTimer
                QTimer.singleShot(1000, selector.deleteLater)
                
            selector.selectionComplete.connect(on_selection_complete)
            selector.selectionCancelled.connect(on_selection_cancelled)
            
            # Start selection
            selector.start_selection()
            
        except Exception as e:
            print(f"Selector error: {e}")
            import traceback
            traceback.print_exc()
            self.show()
            QMessageBox.warning(self, "오류", "영역 선택 중 오류가 발생했습니다.")
        
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
            import pyautogui
            x, y, width, height = self.region
            screenshot = pyautogui.screenshot(region=(x, y, width, height))
            
            # Convert to QPixmap
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
        
    def load_step_data(self):
        """Load data from existing step"""
        if self.step:
            self.name_input.setText(self.step.name)
            
            # Load image path if available
            if hasattr(self.step, 'image_path'):
                self.image_path_input.setText(self.step.image_path)
                self._update_preview()
                
            # Load region if available
            if hasattr(self.step, 'region') and self.step.region:
                self.region = self.step.region
                # Set search scope based on region
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
                
    def get_step_data(self) -> Dict[str, Any]:
        """Get configured step data"""
        data = {
            'name': self.name_input.text(),
            'image_path': self.image_path_input.text(),
            'region': self.region
        }
        
        # Add custom data from subclasses
        data.update(self.get_custom_data())
        
        return data
        
    def get_custom_data(self) -> Dict[str, Any]:
        """Override to return step-specific data"""
        return {}
        
    def accept(self):
        """Validate and accept dialog"""
        # Basic validation
        if not self.name_input.text():
            QMessageBox.warning(self, "확인 오류", "단계 이름을 입력해주세요")
            return
            
        if not self.image_path_input.text():
            QMessageBox.warning(self, "확인 오류", "참조 이미지를 선택해주세요")
            return
            
        if not os.path.exists(self.image_path_input.text()):
            QMessageBox.warning(self, "확인 오류", "선택한 이미지 파일이 존재하지 않습니다")
            return
            
        super().accept()

class WaitImageStepDialog(ImageStepDialog):
    """Dialog for configuring wait image steps"""
    
    def __init__(self, step: Optional[WaitImageStep] = None, 
                 settings: Optional[Settings] = None,
                 parent=None):
        super().__init__(step, settings, parent)
        self.setWindowTitle("이미지 대기 단계 설정")
        
    def add_custom_controls(self, layout: QVBoxLayout):
        """Add wait-specific controls"""
        # Matching parameters group
        params_group = QGroupBox("Matching Parameters")
        params_layout = QVBoxLayout()
        
        # Timeout
        timeout_layout = QHBoxLayout()
        timeout_layout.addWidget(QLabel("Timeout (seconds):"))
        self.timeout_spin = QSpinBox()
        self.timeout_spin.setMinimum(1)
        self.timeout_spin.setMaximum(300)
        self.timeout_spin.setValue(30)
        timeout_layout.addWidget(self.timeout_spin)
        params_layout.addLayout(timeout_layout)
        
        # Confidence
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(QLabel("Confidence:"))
        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setMinimum(0.1)
        self.confidence_spin.setMaximum(1.0)
        self.confidence_spin.setSingleStep(0.05)
        self.confidence_spin.setValue(0.9)
        self.confidence_spin.setDecimals(2)
        confidence_layout.addWidget(self.confidence_spin)
        
        # Test button
        self.test_btn = QPushButton("Test Match")
        self.test_btn.clicked.connect(self._test_match)
        confidence_layout.addWidget(self.test_btn)
        
        params_layout.addLayout(confidence_layout)
        
        # Test result
        self.test_result_label = QLabel()
        params_layout.addWidget(self.test_result_label)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
    def load_step_data(self):
        """Load wait image step data"""
        super().load_step_data()
        
        if isinstance(self.step, WaitImageStep):
            self.timeout_spin.setValue(int(self.step.timeout))
            self.confidence_spin.setValue(self.step.confidence)
            
    def get_custom_data(self) -> Dict[str, Any]:
        """Get wait-specific data"""
        return {
            'step_type': StepType.WAIT_IMAGE,
            'timeout': self.timeout_spin.value(),
            'confidence': self.confidence_spin.value()
        }
        
    def _test_match(self):
        """Test image matching with current settings"""
        image_path = self.image_path_input.text()
        if not image_path or not os.path.exists(image_path):
            self.test_result_label.setText("Please select a valid image first")
            return
            
        # Perform test match
        result = self.image_matcher.find_image(
            image_path,
            confidence=self.confidence_spin.value(),
            region=self.region
        )
        
        if result.found:
            self.test_result_label.setText(
                f"✓ Match found at ({result.center[0]}, {result.center[1]}) "
                f"with confidence {result.confidence:.2f}"
            )
            self.test_result_label.setStyleSheet("color: green;")
        else:
            self.test_result_label.setText(
                f"✗ No match found (best confidence: {result.confidence:.2f})"
            )
            self.test_result_label.setStyleSheet("color: red;")

class ImageSearchStepDialog(ImageStepDialog):
    """Dialog for configuring image search steps"""
    
    def __init__(self, step: Optional[MacroStep] = None,
                 settings: Optional[Settings] = None,
                 parent=None):
        super().__init__(step, settings, parent)
        self.setWindowTitle("이미지 검색 단계 설정")
        
    def add_custom_controls(self, layout: QVBoxLayout):
        """Add search-specific controls"""
        # Search parameters group
        params_group = QGroupBox("검색 파라미터")
        params_layout = QVBoxLayout()
        
        # Confidence
        confidence_layout = QHBoxLayout()
        confidence_layout.addWidget(QLabel("신뢰도:"))
        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setMinimum(0.1)
        self.confidence_spin.setMaximum(1.0)
        self.confidence_spin.setSingleStep(0.05)
        self.confidence_spin.setValue(0.9)
        self.confidence_spin.setDecimals(2)
        confidence_layout.addWidget(self.confidence_spin)
        params_layout.addLayout(confidence_layout)
        
        # Search all occurrences
        self.search_all_check = QCheckBox("모든 항목 찾기")
        params_layout.addWidget(self.search_all_check)
        
        # Max results (when search all is checked)
        max_results_layout = QHBoxLayout()
        max_results_layout.addWidget(QLabel("최대 결과:"))
        self.max_results_spin = QSpinBox()
        self.max_results_spin.setMinimum(1)
        self.max_results_spin.setMaximum(100)
        self.max_results_spin.setValue(10)
        self.max_results_spin.setEnabled(False)
        max_results_layout.addWidget(self.max_results_spin)
        params_layout.addLayout(max_results_layout)
        
        # Connect search all checkbox
        self.search_all_check.toggled.connect(self.max_results_spin.setEnabled)
        
        # Test button
        test_layout = QHBoxLayout()
        self.test_btn = QPushButton("테스트")
        self.test_btn.clicked.connect(self._test_search)
        test_layout.addWidget(self.test_btn)
        test_layout.addStretch()
        params_layout.addLayout(test_layout)
        
        # Test result label
        self.test_result_label = QLabel()
        params_layout.addWidget(self.test_result_label)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
        # Click action group
        click_group = QGroupBox("클릭 옵션")
        click_layout = QVBoxLayout()
        
        # Click after find checkbox
        self.click_after_find_check = QCheckBox("찾은 후 클릭")
        self.click_after_find_check.setChecked(True)
        click_layout.addWidget(self.click_after_find_check)
        
        # Click type selection
        click_type_layout = QHBoxLayout()
        click_type_layout.addWidget(QLabel("클릭 유형:"))
        self.click_type_combo = QComboBox()
        self.click_type_combo.addItems(["한번 클릭", "더블 클릭"])
        self.click_type_combo.setCurrentIndex(0)
        click_type_layout.addWidget(self.click_type_combo)
        click_type_layout.addStretch()
        click_layout.addLayout(click_type_layout)
        
        # Click offset
        offset_layout = QHBoxLayout()
        offset_layout.addWidget(QLabel("클릭 오프셋:"))
        
        offset_layout.addWidget(QLabel("X:"))
        self.offset_x_spin = QSpinBox()
        self.offset_x_spin.setMinimum(-500)
        self.offset_x_spin.setMaximum(500)
        self.offset_x_spin.setValue(0)
        offset_layout.addWidget(self.offset_x_spin)
        
        offset_layout.addWidget(QLabel("Y:"))
        self.offset_y_spin = QSpinBox()
        self.offset_y_spin.setMinimum(-500)
        self.offset_y_spin.setMaximum(500)
        self.offset_y_spin.setValue(0)
        offset_layout.addWidget(self.offset_y_spin)
        
        offset_layout.addStretch()
        click_layout.addLayout(offset_layout)
        
        # Enable/disable click options based on click checkbox
        self.click_after_find_check.toggled.connect(self.click_type_combo.setEnabled)
        self.click_after_find_check.toggled.connect(self.offset_x_spin.setEnabled)
        self.click_after_find_check.toggled.connect(self.offset_y_spin.setEnabled)
        
        click_group.setLayout(click_layout)
        layout.addWidget(click_group)
        
    def get_custom_data(self) -> Dict[str, Any]:
        """Get search-specific data"""
        return {
            'step_type': StepType.IMAGE_SEARCH,
            'confidence': self.confidence_spin.value(),
            'search_all': self.search_all_check.isChecked(),
            'max_results': self.max_results_spin.value(),
            'click_after_find': self.click_after_find_check.isChecked(),
            'click_offset': (self.offset_x_spin.value(), self.offset_y_spin.value()),
            'double_click': self.click_type_combo.currentIndex() == 1  # True if "더블 클릭" selected
        }
        
    def load_step_data(self):
        """Load image search step data"""
        super().load_step_data()
        
        if self.step and hasattr(self.step, 'confidence'):
            self.confidence_spin.setValue(self.step.confidence)
            
        if self.step and hasattr(self.step, 'click_after_find'):
            self.click_after_find_check.setChecked(self.step.click_after_find)
            
        if self.step and hasattr(self.step, 'click_offset'):
            offset = self.step.click_offset
            if offset and len(offset) >= 2:
                self.offset_x_spin.setValue(offset[0])
                self.offset_y_spin.setValue(offset[1])
                
        if self.step and hasattr(self.step, 'double_click'):
            self.click_type_combo.setCurrentIndex(1 if self.step.double_click else 0)
            
    def _test_search(self):
        """Test image search with current settings"""
        image_path = self.image_path_input.text()
        if not image_path or not os.path.exists(image_path):
            self.test_result_label.setText("먼저 유효한 이미지를 선택하세요")
            self.test_result_label.setStyleSheet("color: red;")
            return
            
        # Hide dialog temporarily for testing
        self.hide()
        QTimer.singleShot(300, lambda: self._perform_test_search(image_path))
        
    def _perform_test_search(self, image_path: str):
        """Perform the actual test search"""
        try:
            # Perform image search
            result = self.image_matcher.find_image(
                image_path,
                confidence=self.confidence_spin.value(),
                region=self.region
            )
            
            if result.found:
                # Show result
                if self.click_after_find_check.isChecked():
                    # Calculate click position
                    click_x = result.center[0] + self.offset_x_spin.value()
                    click_y = result.center[1] + self.offset_y_spin.value()
                    
                    message = (
                        f"✓ 이미지를 찾았습니다!\n"
                        f"위치: ({result.center[0]}, {result.center[1]})\n"
                        f"클릭 위치: ({click_x}, {click_y})\n"
                        f"신뢰도: {result.confidence:.2f}"
                    )
                else:
                    message = (
                        f"✓ 이미지를 찾았습니다!\n"
                        f"위치: ({result.center[0]}, {result.center[1]})\n"
                        f"신뢰도: {result.confidence:.2f}"
                    )
                
                self.test_result_label.setText(message.replace('\n', ' '))
                self.test_result_label.setStyleSheet("color: green;")
                
                # Highlight found image briefly
                self._highlight_found_image(result)
                
            else:
                self.test_result_label.setText(
                    f"✗ 이미지를 찾을 수 없습니다 (최고 신뢰도: {result.confidence:.2f})"
                )
                self.test_result_label.setStyleSheet("color: red;")
                
                # Show message box with more info
                QMessageBox.information(
                    self, 
                    "테스트 결과",
                    f"이미지를 찾을 수 없습니다.\n\n"
                    f"최고 신뢰도: {result.confidence:.2f}\n"
                    f"설정된 신뢰도: {self.confidence_spin.value()}\n\n"
                    f"팁:\n"
                    f"- 신뢰도를 낮춰보세요 (현재: {self.confidence_spin.value()})\n"
                    f"- 이미지가 화면에 표시되어 있는지 확인하세요\n"
                    f"- 검색 영역이 올바른지 확인하세요"
                )
                
        except Exception as e:
            print(f"DEBUG: Error in test search: {e}")
            import traceback
            traceback.print_exc()
            self.test_result_label.setText(f"오류: {str(e)}")
            self.test_result_label.setStyleSheet("color: red;")
            QMessageBox.critical(self, "오류", f"테스트 중 오류 발생:\n{str(e)}")
        finally:
            self.show()
            
    def _highlight_found_image(self, result):
        """Briefly highlight the found image on screen"""
        try:
            import pyautogui
            x, y = result.center
            # Move mouse to the found location
            pyautogui.moveTo(x, y, duration=0.5)
            
            # Optional: Draw a rectangle around the found area
            # This would require a temporary overlay window
        except Exception as e:
            print(f"Error highlighting image: {e}")