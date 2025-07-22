"""
Enhanced if condition step dialog with drag and drop support
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QGroupBox, QLabel,
    QDialogButtonBox, QSplitter, QWidget
)
from PyQt5.QtCore import Qt
from core.macro_types import IfConditionStep
from ui.widgets.droppable_widgets import DroppableConditionWidget
from ui.widgets.variable_palette import VariablePalette
from excel.models import ColumnMapping, ColumnType


class EnhancedIfConditionDialog(QDialog):
    """Enhanced dialog for if condition with drag and drop"""
    
    def __init__(self, step: IfConditionStep, excel_columns=None, parent=None):
        super().__init__(parent)
        self.step = step
        self.excel_columns = excel_columns or []
        self.setWindowTitle("조건문 설정")
        self.setModal(True)
        self.resize(800, 600)
        self.init_ui()
        self.load_step_data()
        
    def init_ui(self):
        """Initialize UI"""
        main_layout = QVBoxLayout()
        
        # Step name
        name_layout = QFormLayout()
        self.name_edit = QLineEdit()
        name_layout.addRow("단계 이름:", self.name_edit)
        main_layout.addLayout(name_layout)
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Left side - Variable palette
        if self.excel_columns:
            self.variable_palette = VariablePalette()
            # Convert excel columns to ColumnMapping
            mappings = []
            for col in self.excel_columns:
                mapping = ColumnMapping(
                    excel_column=col,
                    variable_name=col,
                    data_type=ColumnType.TEXT
                )
                mappings.append(mapping)
            self.variable_palette.set_column_mappings(mappings)
            splitter.addWidget(self.variable_palette)
        
        # Right side - Condition setup
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        # Condition group
        condition_group = QGroupBox("조건 설정")
        condition_layout = QVBoxLayout()
        
        # Condition type
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("조건 유형:"))
        
        self.condition_type_combo = QComboBox()
        self.condition_type_combo.addItems([
            "변수 비교",
            "텍스트 존재",
            "이미지 존재",
            "사용자 정의"
        ])
        self.condition_type_combo.currentTextChanged.connect(self.on_condition_type_changed)
        type_layout.addWidget(self.condition_type_combo)
        type_layout.addStretch()
        
        condition_layout.addLayout(type_layout)
        
        # Condition widget container
        self.condition_container = QWidget()
        self.condition_container_layout = QVBoxLayout(self.condition_container)
        condition_layout.addWidget(self.condition_container)
        
        # Create initial condition widget
        self.create_variable_condition_widget()
        
        condition_group.setLayout(condition_layout)
        right_layout.addWidget(condition_group)
        
        # Result preview
        preview_group = QGroupBox("조건식 미리보기")
        preview_layout = QVBoxLayout()
        
        self.preview_label = QLabel("조건을 설정하세요...")
        self.preview_label.setStyleSheet(
            "padding: 10px; background-color: #f8f9fa; "
            "border: 1px solid #dee2e6; border-radius: 4px; "
            "font-family: monospace; font-size: 12px;"
        )
        self.preview_label.setWordWrap(True)
        preview_layout.addWidget(self.preview_label)
        
        preview_group.setLayout(preview_layout)
        right_layout.addWidget(preview_group)
        
        # Help text
        help_label = QLabel(
            "💡 팁: 변수를 드래그하여 조건 필드에 놓을 수 있습니다.\n"
            "예: ${환자번호} == 'P001' 또는 ${혈압} > 140"
        )
        help_label.setWordWrap(True)
        help_label.setStyleSheet(
            "background-color: #e3f2fd; padding: 10px; "
            "border-radius: 4px; color: #1976d2;"
        )
        right_layout.addWidget(help_label)
        
        right_layout.addStretch()
        
        splitter.addWidget(right_widget)
        
        # Set splitter sizes
        if self.excel_columns:
            splitter.setSizes([300, 500])
        
        main_layout.addWidget(splitter)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        main_layout.addWidget(buttons)
        
        self.setLayout(main_layout)
        
    def create_variable_condition_widget(self):
        """Create variable comparison condition widget"""
        # Clear existing widgets
        while self.condition_container_layout.count():
            item = self.condition_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Create droppable condition widget
        self.condition_widget = DroppableConditionWidget()
        self.condition_widget.conditionChanged.connect(self.update_preview)
        self.condition_container_layout.addWidget(self.condition_widget)
        
    def create_text_exists_widget(self):
        """Create text exists condition widget"""
        # Clear existing widgets
        while self.condition_container_layout.count():
            item = self.condition_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Create simple layout for text search
        widget = QWidget()
        layout = QFormLayout(widget)
        
        from ui.widgets.droppable_widgets import DroppableLineEdit
        
        self.text_search_edit = DroppableLineEdit()
        self.text_search_edit.setPlaceholderText("검색할 텍스트 또는 ${변수}")
        self.text_search_edit.textChanged.connect(self.update_preview)
        layout.addRow("검색 텍스트:", self.text_search_edit)
        
        self.condition_container_layout.addWidget(widget)
        
    def create_custom_condition_widget(self):
        """Create custom condition widget"""
        # Clear existing widgets
        while self.condition_container_layout.count():
            item = self.condition_container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Create custom expression input
        from ui.widgets.droppable_widgets import DroppableTextEdit
        
        self.custom_condition_edit = DroppableTextEdit()
        self.custom_condition_edit.setPlaceholderText(
            "Python 표현식을 입력하세요.\n"
            "예: ${혈압} > 140 and ${혈당} > 100\n"
            "변수를 드래그하여 놓을 수 있습니다."
        )
        self.custom_condition_edit.setMinimumHeight(100)
        self.custom_condition_edit.textChanged.connect(self.update_preview)
        
        self.condition_container_layout.addWidget(self.custom_condition_edit)
        
    def on_condition_type_changed(self, text):
        """Handle condition type change"""
        if text == "변수 비교":
            self.create_variable_condition_widget()
        elif text == "텍스트 존재":
            self.create_text_exists_widget()
        elif text == "사용자 정의":
            self.create_custom_condition_widget()
            
        self.update_preview()
        
    def update_preview(self):
        """Update condition preview"""
        condition_type = self.condition_type_combo.currentText()
        
        if condition_type == "변수 비교" and hasattr(self, 'condition_widget'):
            condition = self.condition_widget.get_condition()
        elif condition_type == "텍스트 존재" and hasattr(self, 'text_search_edit'):
            text = self.text_search_edit.text()
            condition = f"text_exists('{text}')" if text else ""
        elif condition_type == "사용자 정의" and hasattr(self, 'custom_condition_edit'):
            condition = self.custom_condition_edit.toPlainText()
        else:
            condition = ""
            
        if condition:
            self.preview_label.setText(f"if {condition}:")
            self.preview_label.setStyleSheet(
                "padding: 10px; background-color: #e8f5e9; "
                "border: 1px solid #4caf50; border-radius: 4px; "
                "font-family: monospace; font-size: 12px; color: #2e7d32;"
            )
        else:
            self.preview_label.setText("조건을 설정하세요...")
            self.preview_label.setStyleSheet(
                "padding: 10px; background-color: #f8f9fa; "
                "border: 1px solid #dee2e6; border-radius: 4px; "
                "font-family: monospace; font-size: 12px;"
            )
            
    def load_step_data(self):
        """Load data from step"""
        self.name_edit.setText(self.step.name)
        
        # Load condition based on type
        if self.step.condition_type == "variable_equals":
            self.condition_type_combo.setCurrentText("변수 비교")
            # Set values in condition widget
            if hasattr(self, 'condition_widget'):
                var_name = self.step.condition_value.get('variable', '')
                value = self.step.condition_value.get('value', '')
                self.condition_widget.variable_field.setText(f"${{{var_name}}}")
                self.condition_widget.operator_combo.setCurrentText("==")
                self.condition_widget.value_field.setText(value)
        elif self.step.condition_type == "text_exists":
            self.condition_type_combo.setCurrentText("텍스트 존재")
            
    def get_step_data(self):
        """Get configured step data"""
        condition_type = self.condition_type_combo.currentText()
        
        data = {
            'name': self.name_edit.text()
        }
        
        if condition_type == "변수 비교" and hasattr(self, 'condition_widget'):
            # Parse condition widget
            var_text = self.condition_widget.variable_field.text()
            operator = self.condition_widget.operator_combo.currentText()
            value = self.condition_widget.value_field.text()
            
            # Extract variable name from ${var}
            import re
            match = re.match(r'\$\{(\w+)\}', var_text)
            var_name = match.group(1) if match else var_text
            
            # Convert operator to condition type
            if operator == "==":
                data['condition_type'] = "variable_equals"
            elif operator == "!=":
                data['condition_type'] = "variable_not_equals"
            elif operator == ">":
                data['condition_type'] = "variable_greater"
            elif operator == "<":
                data['condition_type'] = "variable_less"
            elif operator == "contains":
                data['condition_type'] = "variable_contains"
            else:
                data['condition_type'] = "variable_equals"
                
            data['condition_value'] = {
                'variable': var_name,
                'value': value
            }
            
        elif condition_type == "텍스트 존재" and hasattr(self, 'text_search_edit'):
            data['condition_type'] = "text_exists"
            data['condition_value'] = {
                'text': self.text_search_edit.text()
            }
            
        elif condition_type == "사용자 정의" and hasattr(self, 'custom_condition_edit'):
            data['condition_type'] = "custom"
            data['condition'] = self.custom_condition_edit.toPlainText()
            
        return data