"""
If condition step configuration dialog
"""

from typing import Optional, Dict, Any, List
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox,
    QPushButton, QLabel, QGroupBox, QListWidget,
    QListWidgetItem, QTextEdit, QWidget, QSplitter,
    QMessageBox, QCompleter, QCheckBox, QFileDialog,
    QMenu
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from core.macro_types import IfConditionStep, MacroStep, StepType
from ui.widgets.roi_selector import ROISelectorWidget

class DraggableStepButton(QPushButton):
    """Draggable button for step types"""
    
    def __init__(self, step_type: StepType, text: str):
        super().__init__(text)
        self.step_type = step_type
        self.setStyleSheet("""
            QPushButton {
                padding: 8px 12px;
                border: 2px solid #2196F3;
                border-radius: 4px;
                background-color: white;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #e3f2fd;
                cursor: move;
            }
        """)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_position = event.pos()
            
    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.LeftButton):
            return
            
        if (event.pos() - self.drag_start_position).manhattanLength() < 10:
            return
            
        # Start drag
        from PyQt5.QtGui import QDrag
        from PyQt5.QtCore import QMimeData, QByteArray, QDataStream, QIODevice
        
        drag = QDrag(self)
        mime_data = QMimeData()
        
        # Store step type in MIME data
        # Use setText instead of binary encoding to avoid Qt version issues
        mime_data.setData("application/x-steptype", self.step_type.value.encode())
        mime_data.setText(self.text())
        drag.setMimeData(mime_data)
        
        drag.exec_(Qt.CopyAction)

class ConditionTypeWidget(QWidget):
    """Widget for configuring condition parameters based on type"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        
    def set_condition_type(self, condition_type: str, excel_columns: List[str] = None):
        """Update UI based on condition type"""
        # Clear existing widgets
        while self.layout.count():
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        if condition_type == "image_exists":
            self._setup_image_condition()
        elif condition_type == "text_exists":
            self._setup_text_condition()
        elif condition_type in ["variable_equals", "variable_contains", "variable_greater", "variable_less"]:
            self._setup_variable_condition(excel_columns)
            
    def _setup_image_condition(self):
        """Setup UI for image exists condition"""
        form_layout = QFormLayout()
        
        # Image path
        self.image_path_edit = QLineEdit()
        self.image_browse_btn = QPushButton("찾아보기...")
        self.image_browse_btn.clicked.connect(self._browse_image)
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.image_path_edit)
        image_layout.addWidget(self.image_browse_btn)
        form_layout.addRow("이미지 파일:", image_layout)
        
        # Confidence
        self.confidence_spin = QDoubleSpinBox()
        self.confidence_spin.setRange(0.1, 1.0)
        self.confidence_spin.setSingleStep(0.1)
        self.confidence_spin.setValue(0.9)
        form_layout.addRow("정확도:", self.confidence_spin)
        
        # Region selector
        self.region_selector = ROISelectorWidget()
        form_layout.addRow("검색 영역:", self.region_selector)
        
        # Test button
        self.test_btn = QPushButton("조건 테스트")
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.test_btn.clicked.connect(self._test_image_condition)
        
        # Test result
        self.test_result_label = QLabel()
        self.test_result_label.setWordWrap(True)
        
        test_layout = QVBoxLayout()
        test_layout.addWidget(self.test_btn)
        test_layout.addWidget(self.test_result_label)
        form_layout.addRow("", test_layout)
        
        self.layout.addLayout(form_layout)
        
    def _browse_image(self):
        """Browse for image file"""
        filename, _ = QFileDialog.getOpenFileName(
            self,
            "이미지 파일 선택",
            "",
            "Image Files (*.png *.jpg *.jpeg *.bmp *.gif);;All Files (*.*)"
        )
        if filename:
            self.image_path_edit.setText(filename)
        
    def _setup_text_condition(self):
        """Setup UI for text exists condition"""
        form_layout = QFormLayout()
        
        # Search text
        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("검색할 텍스트 또는 {{변수}}")
        form_layout.addRow("텍스트:", self.text_edit)
        
        # Exact match
        self.exact_match_check = QCheckBox("정확히 일치")
        form_layout.addRow("", self.exact_match_check)
        
        # Region selector
        self.region_selector = ROISelectorWidget()
        form_layout.addRow("검색 영역:", self.region_selector)
        
        self.layout.addLayout(form_layout)
        
    def _setup_variable_condition(self, excel_columns: List[str] = None):
        """Setup UI for variable comparison condition"""
        form_layout = QFormLayout()
        
        # Variable name
        self.variable_combo = QComboBox()
        self.variable_combo.setEditable(True)
        if excel_columns:
            self.variable_combo.addItems(excel_columns)
        form_layout.addRow("변수:", self.variable_combo)
        
        # Comparison value
        self.compare_value_edit = QLineEdit()
        self.compare_value_edit.setPlaceholderText("비교할 값 또는 {{변수}}")
        form_layout.addRow("비교값:", self.compare_value_edit)
        
        self.layout.addLayout(form_layout)
        
    def get_condition_value(self) -> Dict[str, Any]:
        """Get condition parameters"""
        value = {}
        
        # Image exists
        if hasattr(self, 'image_path_edit'):
            value['image_path'] = self.image_path_edit.text()
            value['confidence'] = self.confidence_spin.value()
            value['region'] = self.region_selector.get_region()
            
        # Text exists
        elif hasattr(self, 'text_edit'):
            value['text'] = self.text_edit.text()
            value['exact_match'] = self.exact_match_check.isChecked()
            value['region'] = self.region_selector.get_region()
            
        # Variable comparison
        elif hasattr(self, 'variable_combo'):
            value['variable'] = self.variable_combo.currentText()
            value['compare_value'] = self.compare_value_edit.text()
            
        return value
        
    def _test_image_condition(self):
        """Test image condition"""
        image_path = self.image_path_edit.text()
        if not image_path:
            self.test_result_label.setText("❌ 이미지 파일을 선택해주세요.")
            self.test_result_label.setStyleSheet("color: red;")
            return
            
        try:
            import pyautogui
            # Test image search
            location = pyautogui.locateOnScreen(
                image_path,
                confidence=self.confidence_spin.value(),
                region=self.region_selector.get_region()
            )
            
            if location:
                self.test_result_label.setText(f"✅ 이미지를 찾았습니다! 위치: ({location.left}, {location.top})")
                self.test_result_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.test_result_label.setText("❌ 이미지를 찾을 수 없습니다.")
                self.test_result_label.setStyleSheet("color: red;")
                
        except Exception as e:
            self.test_result_label.setText(f"❌ 테스트 중 오류: {str(e)}")
            self.test_result_label.setStyleSheet("color: red;")
        
    def set_condition_value(self, value: Dict[str, Any]):
        """Set condition parameters"""
        # Image exists
        if hasattr(self, 'image_path_edit') and 'image_path' in value:
            self.image_path_edit.setText(value.get('image_path', ''))
            self.confidence_spin.setValue(value.get('confidence', 0.9))
            if value.get('region'):
                self.region_selector.set_region(value['region'])
                
        # Text exists
        elif hasattr(self, 'text_edit') and 'text' in value:
            self.text_edit.setText(value.get('text', ''))
            self.exact_match_check.setChecked(value.get('exact_match', False))
            if value.get('region'):
                self.region_selector.set_region(value['region'])
                
        # Variable comparison
        elif hasattr(self, 'variable_combo') and 'variable' in value:
            self.variable_combo.setCurrentText(value.get('variable', ''))
            self.compare_value_edit.setText(value.get('compare_value', ''))

class StepListWidget(QListWidget):
    """Widget for displaying and managing nested steps"""
    
    stepAdded = pyqtSignal(MacroStep)
    stepRemoved = pyqtSignal(str)  # step_id
    stepEdited = pyqtSignal(MacroStep)
    
    def __init__(self):
        super().__init__()
        self.steps: List[MacroStep] = []
        self.setAcceptDrops(True)
        self.setDragDropMode(QListWidget.InternalMove)
        self.setStyleSheet("""
            QListWidget {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 3px;
                padding: 5px;
                min-height: 100px;
            }
            QListWidget::item {
                padding: 5px;
                margin: 2px;
                border: 1px solid #e0e0e0;
                border-radius: 3px;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
                border-color: #bdbdbd;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border-color: #2196F3;
            }
        """)
        
    def add_step(self, step_type: StepType):
        """Add a new step of given type"""
        from core.macro_types import StepFactory
        step = StepFactory.create_step(step_type)
        
        # Set default name
        step_names = {
            StepType.MOUSE_CLICK: "마우스 클릭",
            StepType.KEYBOARD_TYPE: "텍스트 입력",
            StepType.WAIT_TIME: "대기",
            StepType.IMAGE_SEARCH: "이미지 검색",
            StepType.OCR_TEXT: "텍스트 검색"
        }
        step.name = step_names.get(step_type, step_type.value)
        
        self.steps.append(step)
        self._refresh_list()
        self.stepAdded.emit(step)
        
    def remove_selected(self):
        """Remove selected step"""
        current_row = self.currentRow()
        if 0 <= current_row < len(self.steps):
            removed_step = self.steps.pop(current_row)
            self._refresh_list()
            self.stepRemoved.emit(removed_step.step_id)
            
    def get_steps(self) -> List[MacroStep]:
        """Get all steps"""
        return self.steps
        
    def set_steps(self, steps: List[MacroStep]):
        """Set steps"""
        self.steps = steps.copy()
        self._refresh_list()
        
    def _refresh_list(self):
        """Refresh list display"""
        self.clear()
        
        for step in self.steps:
            icon = self._get_step_icon(step.step_type)
            text = f"{icon} {step.name}"
            if hasattr(step, 'description') and step.description:
                text += f" - {step.description}"
                
            item = QListWidgetItem(text)
            self.addItem(item)
            
    def _get_step_icon(self, step_type: StepType) -> str:
        """Get icon for step type"""
        icons = {
            StepType.MOUSE_CLICK: "🖱️",
            StepType.KEYBOARD_TYPE: "⌨️",
            StepType.WAIT_TIME: "⏱️",
            StepType.IMAGE_SEARCH: "🔍",
            StepType.OCR_TEXT: "🔤"
        }
        return icons.get(step_type, "")
        
    def dragEnterEvent(self, event):
        """Handle drag enter event"""
        if event.mimeData().hasFormat("application/x-steptype"):
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)
            
    def dragMoveEvent(self, event):
        """Handle drag move event"""
        if event.mimeData().hasFormat("application/x-steptype"):
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)
            
    def dropEvent(self, event):
        """Handle drop event"""
        if event.mimeData().hasFormat("application/x-steptype"):
            # Extract step type from mime data
            # Use simpler byte decoding to avoid Qt version issues
            byte_array = event.mimeData().data("application/x-steptype")
            step_type_str = bytes(byte_array).decode('utf-8')
            
            # Create new step
            step_type = StepType(step_type_str)
            self.add_step(step_type)
            
            event.acceptProposedAction()
        else:
            super().dropEvent(event)

class IfConditionStepDialog(QDialog):
    """Dialog for configuring if condition step"""
    
    def __init__(self, step: Optional[IfConditionStep] = None, 
                 excel_columns: List[str] = None, parent=None):
        super().__init__(parent)
        self.step = step or IfConditionStep()
        self.excel_columns = excel_columns or []
        self.init_ui()
        self.load_step_data()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("조건문 설정")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout()
        
        # Basic info
        info_group = QGroupBox("기본 정보")
        info_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.name_edit.setText(self.step.name or "조건문")
        info_layout.addRow("이름:", self.name_edit)
        
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(60)
        self.description_edit.setText(self.step.description)
        info_layout.addRow("설명:", self.description_edit)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Condition configuration
        condition_group = QGroupBox("조건 설정")
        condition_layout = QVBoxLayout()
        
        # Condition type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("조건 유형:"))
        
        self.condition_type_combo = QComboBox()
        
        # Add items properly with display text and data
        condition_items = [
            ("이미지가 존재하면", "image_exists"),
            ("텍스트가 존재하면", "text_exists"),
            ("변수가 같으면", "variable_equals"),
            ("변수가 포함하면", "variable_contains"),
            ("변수가 크면", "variable_greater"),
            ("변수가 작으면", "variable_less")
        ]
        
        for display_text, value in condition_items:
            self.condition_type_combo.addItem(display_text)
            self.condition_type_combo.setItemData(self.condition_type_combo.count() - 1, value, Qt.UserRole)
            
        self.condition_type_combo.currentIndexChanged.connect(self._on_condition_type_changed)
        type_layout.addWidget(self.condition_type_combo)
        type_layout.addStretch()
        condition_layout.addLayout(type_layout)
        
        # Condition parameters
        self.condition_widget = ConditionTypeWidget()
        condition_layout.addWidget(self.condition_widget)
        
        condition_group.setLayout(condition_layout)
        layout.addWidget(condition_group)
        
        # Branch steps
        branches_group = QGroupBox("분기 동작")
        branches_layout = QVBoxLayout()
        
        # Add help text
        help_text = QLabel("💡 팁: 아래 단계 유형을 드래그하여 조건 분기에 추가하거나, '단계 추가' 버튼을 사용하세요.")
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #0066cc; font-size: 12px; padding: 5px; background-color: #e6f2ff; border-radius: 3px;")
        branches_layout.addWidget(help_text)
        
        # Add mini palette
        palette_layout = QHBoxLayout()
        palette_label = QLabel("단계 유형:")
        palette_label.setStyleSheet("font-weight: bold;")
        palette_layout.addWidget(palette_label)
        
        # Create draggable step type buttons
        step_types = [
            (StepType.MOUSE_CLICK, "🖱️ 클릭"),
            (StepType.KEYBOARD_TYPE, "⌨️ 입력"),
            (StepType.WAIT_TIME, "⏱️ 대기"),
            (StepType.IMAGE_SEARCH, "🔍 이미지"),
        ]
        
        for step_type, label in step_types:
            btn = DraggableStepButton(step_type, label)
            palette_layout.addWidget(btn)
            
        palette_layout.addStretch()
        branches_layout.addLayout(palette_layout)
        
        # Create splitter for true/false branches
        splitter = QSplitter(Qt.Horizontal)
        
        # True branch
        true_widget = QWidget()
        true_widget.setStyleSheet("""
            QWidget {
                background-color: #e8f5e9;
                border: 2px solid #4caf50;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        true_layout = QVBoxLayout()
        true_label = QLabel("✅ 조건이 참일 때:")
        true_label.setStyleSheet("font-weight: bold; color: #2e7d32; font-size: 13px;")
        true_layout.addWidget(true_label)
        
        self.true_steps_list = StepListWidget()
        true_layout.addWidget(self.true_steps_list)
        
        # True branch buttons
        true_btn_layout = QHBoxLayout()
        
        add_true_menu = QPushButton("단계 추가")
        add_true_menu.setMenu(self._create_step_menu(self.true_steps_list))
        true_btn_layout.addWidget(add_true_menu)
        
        remove_true_btn = QPushButton("삭제")
        remove_true_btn.clicked.connect(self.true_steps_list.remove_selected)
        true_btn_layout.addWidget(remove_true_btn)
        
        true_btn_layout.addStretch()
        true_layout.addLayout(true_btn_layout)
        
        true_widget.setLayout(true_layout)
        splitter.addWidget(true_widget)
        
        # False branch
        false_widget = QWidget()
        false_widget.setStyleSheet("""
            QWidget {
                background-color: #ffebee;
                border: 2px solid #f44336;
                border-radius: 5px;
                padding: 5px;
            }
        """)
        false_layout = QVBoxLayout()
        false_label = QLabel("❌ 조건이 거짓일 때:")
        false_label.setStyleSheet("font-weight: bold; color: #c62828; font-size: 13px;")
        false_layout.addWidget(false_label)
        
        self.false_steps_list = StepListWidget()
        false_layout.addWidget(self.false_steps_list)
        
        # False branch buttons
        false_btn_layout = QHBoxLayout()
        
        add_false_menu = QPushButton("단계 추가")
        add_false_menu.setMenu(self._create_step_menu(self.false_steps_list))
        false_btn_layout.addWidget(add_false_menu)
        
        remove_false_btn = QPushButton("삭제")
        remove_false_btn.clicked.connect(self.false_steps_list.remove_selected)
        false_btn_layout.addWidget(remove_false_btn)
        
        false_btn_layout.addStretch()
        false_layout.addLayout(false_btn_layout)
        
        false_widget.setLayout(false_layout)
        splitter.addWidget(false_widget)
        
        branches_layout.addWidget(splitter)
        branches_group.setLayout(branches_layout)
        layout.addWidget(branches_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        ok_btn = QPushButton("확인")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton("취소")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
        # Initialize condition type
        self._on_condition_type_changed()
        
    def _create_step_menu(self, step_list: StepListWidget):
        """Create menu for adding steps"""
        menu = QMenu()
        
        # Simple steps only (no nested conditions)
        simple_steps = [
            (StepType.MOUSE_CLICK, "🖱️ 마우스 클릭"),
            (StepType.KEYBOARD_TYPE, "⌨️ 텍스트 입력"),
            (StepType.WAIT_TIME, "⏱️ 대기"),
            (StepType.IMAGE_SEARCH, "🔍 이미지 검색"),
            (StepType.OCR_TEXT, "🔤 텍스트 검색")
        ]
        
        for step_type, name in simple_steps:
            action = menu.addAction(name)
            action.triggered.connect(lambda checked, st=step_type: step_list.add_step(st))
            
        return menu
        
    def _on_condition_type_changed(self):
        """Handle condition type change"""
        # Get selected type value
        condition_type = self.condition_type_combo.currentData(Qt.UserRole)
        if not condition_type:
            condition_type = self.condition_type_combo.currentText()
            
        # Map display text to type value
        type_mapping = {
            "이미지가 존재하면": "image_exists",
            "텍스트가 존재하면": "text_exists",
            "변수가 같으면": "variable_equals",
            "변수가 포함하면": "variable_contains",
            "변수가 크면": "variable_greater",
            "변수가 작으면": "variable_less"
        }
        
        if condition_type in type_mapping:
            condition_type = type_mapping[condition_type]
            
        self.condition_widget.set_condition_type(condition_type, self.excel_columns)
        
    def load_step_data(self):
        """Load data from step"""
        if not self.step:
            return
            
        self.name_edit.setText(self.step.name)
        self.description_edit.setText(self.step.description)
        
        # Set condition type
        type_index = {
            "image_exists": 0,
            "text_exists": 1,
            "variable_equals": 2,
            "variable_contains": 3,
            "variable_greater": 4,
            "variable_less": 5
        }.get(self.step.condition_type, 0)
        
        self.condition_type_combo.setCurrentIndex(type_index)
        self.condition_widget.set_condition_value(self.step.condition_value)
        
        # Set branch steps
        self.true_steps_list.set_steps(self.step.true_steps)
        self.false_steps_list.set_steps(self.step.false_steps)
        
    def get_step_data(self) -> Dict[str, Any]:
        """Get configured step data"""
        # Get condition type
        condition_type = self.condition_type_combo.currentData(Qt.UserRole)
        if not condition_type:
            type_mapping = {
                "이미지가 존재하면": "image_exists",
                "텍스트가 존재하면": "text_exists",
                "변수가 같으면": "variable_equals",
                "변수가 포함하면": "variable_contains",
                "변수가 크면": "variable_greater",
                "변수가 작으면": "variable_less"
            }
            condition_type = type_mapping.get(self.condition_type_combo.currentText(), "image_exists")
            
        return {
            'name': self.name_edit.text(),
            'description': self.description_edit.toPlainText(),
            'condition_type': condition_type,
            'condition_value': self.condition_widget.get_condition_value(),
            'true_steps': self.true_steps_list.get_steps(),
            'false_steps': self.false_steps_list.get_steps()
        }
        
    def accept(self):
        """Validate and accept"""
        # Basic validation
        if not self.name_edit.text():
            QMessageBox.warning(self, "경고", "이름을 입력해주세요.")
            return
            
        # Validate condition parameters
        condition_value = self.condition_widget.get_condition_value()
        condition_type = self.get_step_data()['condition_type']
        
        if condition_type == "image_exists" and not condition_value.get('image_path'):
            QMessageBox.warning(self, "경고", "이미지 파일을 선택해주세요.")
            return
            
        elif condition_type == "text_exists" and not condition_value.get('text'):
            QMessageBox.warning(self, "경고", "검색할 텍스트를 입력해주세요.")
            return
            
        elif condition_type in ["variable_equals", "variable_contains", "variable_greater", "variable_less"]:
            if not condition_value.get('variable'):
                QMessageBox.warning(self, "경고", "변수를 선택해주세요.")
                return
            if not condition_value.get('compare_value'):
                QMessageBox.warning(self, "경고", "비교값을 입력해주세요.")
                return
                
        super().accept()