"""
Configuration dialogs for image-based macro steps
"""

import os
from typing import Optional, Dict, Any, Tuple
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QSpinBox, QDoubleSpinBox, QGroupBox, QFileDialog,
    QDialogButtonBox, QMessageBox, QCheckBox, QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from core.macro_types import MacroStep, WaitImageStep, StepType
from vision.image_matcher import ImageMatcher
from config.settings import Settings
from ui.widgets.roi_selector import ROISelectorWidget

class ImageStepDialog(QDialog):
    """Base dialog for image step configuration"""
    
    def __init__(self, step: Optional[MacroStep] = None, 
                 settings: Optional[Settings] = None,
                 parent=None):
        super().__init__(parent)
        self.step = step
        self.settings = settings or Settings()
        self.image_matcher = ImageMatcher(self.settings)
        
        # Step data
        self.step_data: Dict[str, Any] = {}
        if step:
            self.step_data = step.to_dict()
            
        self.init_ui()
        self.load_step_data()
        
    def init_ui(self):
        """Initialize base UI"""
        self.setModal(True)
        self.setMinimumWidth(600)
        
        layout = QVBoxLayout()
        
        # Name input
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Step Name:"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)
        
        # Image selection group
        image_group = QGroupBox("Reference Image")
        image_layout = QVBoxLayout()
        
        # Image path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Image Path:"))
        self.image_path_input = QLineEdit()
        self.image_path_input.setReadOnly(True)
        path_layout.addWidget(self.image_path_input)
        
        # Browse button
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self._browse_image)
        path_layout.addWidget(self.browse_btn)
        
        # Capture button
        self.capture_btn = QPushButton("Capture")
        self.capture_btn.clicked.connect(self._capture_image)
        path_layout.addWidget(self.capture_btn)
        
        image_layout.addLayout(path_layout)
        
        # Image preview
        self.image_preview = QLabel()
        self.image_preview.setMinimumHeight(150)
        self.image_preview.setMaximumHeight(300)
        self.image_preview.setScaledContents(True)
        self.image_preview.setAlignment(Qt.AlignCenter)
        self.image_preview.setStyleSheet("""
            QLabel {
                border: 1px solid #ccc;
                background-color: #f9f9f9;
            }
        """)
        image_layout.addWidget(self.image_preview)
        
        image_group.setLayout(image_layout)
        layout.addWidget(image_group)
        
        # ROI selection group
        roi_group = QGroupBox("Search Region (Optional)")
        roi_layout = QVBoxLayout()
        
        # ROI selector widget
        self.roi_selector = ROISelectorWidget()
        roi_layout.addWidget(self.roi_selector)
        
        # Select region button
        self.select_region_btn = QPushButton("Select Screen Region")
        self.select_region_btn.clicked.connect(self._select_region)
        roi_layout.addWidget(self.select_region_btn)
        
        # Clear region button
        self.clear_region_btn = QPushButton("Clear Region")
        self.clear_region_btn.clicked.connect(self._clear_region)
        roi_layout.addWidget(self.clear_region_btn)
        
        roi_group.setLayout(roi_layout)
        layout.addWidget(roi_group)
        
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
        
    def add_custom_controls(self, layout: QVBoxLayout):
        """Override to add step-specific controls"""
        pass
        
    def _browse_image(self):
        """Browse for image file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Reference Image",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp);;All Files (*.*)"
        )
        
        if file_path:
            self.image_path_input.setText(file_path)
            self._update_preview()
            
    def _capture_image(self):
        """Capture new reference image"""
        # Hide dialog temporarily
        self.hide()
        
        # Use ROI selector to capture region
        from widgets.roi_selector import ROISelectorOverlay
        selector = ROISelectorOverlay()
        
        def on_selection(region):
            # Capture the selected region
            import time
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"capture_{timestamp}.png"
            
            # Create captures directory if needed
            captures_dir = os.path.join(os.path.dirname(__file__), "../../../captures")
            os.makedirs(captures_dir, exist_ok=True)
            
            file_path = os.path.join(captures_dir, filename)
            
            # Capture and save
            self.image_matcher.capture_region(region, file_path)
            
            # Update UI
            self.image_path_input.setText(file_path)
            self._update_preview()
            self.show()
            
        selector.selectionComplete.connect(on_selection)
        selector.selectionCancelled.connect(lambda: self.show())
        selector.start_selection()
        
    def _update_preview(self):
        """Update image preview"""
        image_path = self.image_path_input.text()
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                # Scale to fit preview
                scaled = pixmap.scaled(
                    self.image_preview.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.image_preview.setPixmap(scaled)
            else:
                self.image_preview.setText("Invalid image")
        else:
            self.image_preview.setText("No image selected")
            
    def _select_region(self):
        """Start region selection"""
        self.hide()
        self.roi_selector.start_selection()
        self.roi_selector.regionSelected.connect(lambda r: self.show())
        
    def _clear_region(self):
        """Clear selected region"""
        self.roi_selector.set_region(None)
        
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
                self.roi_selector.set_region(self.step.region)
                
    def get_step_data(self) -> Dict[str, Any]:
        """Get configured step data"""
        data = {
            'name': self.name_input.text(),
            'image_path': self.image_path_input.text(),
            'region': self.roi_selector.get_region()
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
            QMessageBox.warning(self, "Validation Error", "Please enter a step name")
            return
            
        if not self.image_path_input.text():
            QMessageBox.warning(self, "Validation Error", "Please select a reference image")
            return
            
        if not os.path.exists(self.image_path_input.text()):
            QMessageBox.warning(self, "Validation Error", "Selected image file does not exist")
            return
            
        super().accept()

class WaitImageStepDialog(ImageStepDialog):
    """Dialog for configuring wait image steps"""
    
    def __init__(self, step: Optional[WaitImageStep] = None, 
                 settings: Optional[Settings] = None,
                 parent=None):
        super().__init__(step, settings, parent)
        self.setWindowTitle("Configure Wait for Image Step")
        
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
            region=self.roi_selector.get_region()
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
        self.setWindowTitle("Configure Image Search Step")
        
    def add_custom_controls(self, layout: QVBoxLayout):
        """Add search-specific controls"""
        # Search parameters group
        params_group = QGroupBox("Search Parameters")
        params_layout = QVBoxLayout()
        
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
        params_layout.addLayout(confidence_layout)
        
        # Search all occurrences
        self.search_all_check = QCheckBox("Find all occurrences")
        params_layout.addWidget(self.search_all_check)
        
        # Max results (when search all is checked)
        max_results_layout = QHBoxLayout()
        max_results_layout.addWidget(QLabel("Max results:"))
        self.max_results_spin = QSpinBox()
        self.max_results_spin.setMinimum(1)
        self.max_results_spin.setMaximum(100)
        self.max_results_spin.setValue(10)
        self.max_results_spin.setEnabled(False)
        max_results_layout.addWidget(self.max_results_spin)
        params_layout.addLayout(max_results_layout)
        
        # Connect search all checkbox
        self.search_all_check.toggled.connect(self.max_results_spin.setEnabled)
        
        params_group.setLayout(params_layout)
        layout.addWidget(params_group)
        
    def get_custom_data(self) -> Dict[str, Any]:
        """Get search-specific data"""
        return {
            'step_type': StepType.IMAGE_SEARCH,
            'confidence': self.confidence_spin.value(),
            'search_all': self.search_all_check.isChecked(),
            'max_results': self.max_results_spin.value()
        }