"""
Keyboard type step configuration dialog
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QSpinBox, QDialogButtonBox, QTextEdit,
    QFormLayout, QGroupBox, QCheckBox, QListWidget, QSplitter,
    QWidget
)
from PyQt5.QtCore import Qt
from core.macro_types import KeyboardTypeStep
from ui.widgets.droppable_widgets import DroppableTextEdit
from ui.widgets.variable_palette import VariablePalette
from excel.models import ColumnMapping, ColumnType


class KeyboardTypeStepDialog(QDialog):
    """Dialog for configuring keyboard type step"""
    
    def __init__(self, step: KeyboardTypeStep, excel_columns=None, parent=None):
        super().__init__(parent)
        self.step = step
        self.excel_columns = excel_columns or []
        self.setWindowTitle("텍스트 입력 설정")
        self.setModal(True)
        self.setMinimumWidth(500)
        # Prevent dialog from closing parent window
        self.setAttribute(Qt.WA_DeleteOnClose, False)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
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
        
        # Create splitter for variable palette and text input
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
            self.variable_palette.variableSelected.connect(self.insert_variable_text)
            splitter.addWidget(self.variable_palette)
        
        # Right side - Text input
        text_widget = QWidget()
        text_layout = QVBoxLayout(text_widget)
        
        text_group = QGroupBox("입력할 텍스트")
        text_group_layout = QVBoxLayout()
        
        # Droppable text edit
        self.text_edit = DroppableTextEdit()
        self.text_edit.setPlaceholderText(
            "텍스트를 입력하거나 변수를 드래그하여 놓으세요.\n"
            "변수는 ${변수명} 형식으로 자동 삽입됩니다."
        )
        self.text_edit.setMinimumHeight(150)
        self.text_edit.variableDropped.connect(self.on_variable_dropped)
        text_group_layout.addWidget(self.text_edit)
        
        # Variable usage indicator
        usage_label = QLabel("사용된 변수:")
        usage_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
        text_group_layout.addWidget(usage_label)
        
        self.used_variables_label = QLabel("없음")
        self.used_variables_label.setStyleSheet("color: #666; padding: 5px;")
        text_group_layout.addWidget(self.used_variables_label)
        
        text_group.setLayout(text_group_layout)
        text_layout.addWidget(text_group)
        
        # Typing options
        options_group = QGroupBox("입력 옵션")
        options_layout = QFormLayout()
        
        # Typing interval
        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(0, 1000)
        self.interval_spin.setSuffix(" ms")
        self.interval_spin.setValue(0)
        options_layout.addRow("키 입력 간격:", self.interval_spin)
        
        # Use variables checkbox
        self.use_variables_check = QCheckBox("변수 치환 사용")
        self.use_variables_check.setChecked(True)
        options_layout.addRow("", self.use_variables_check)
        
        options_group.setLayout(options_layout)
        text_layout.addWidget(options_group)
        
        splitter.addWidget(text_widget)
        
        # Set splitter sizes (30% palette, 70% text)
        if self.excel_columns:
            splitter.setSizes([300, 700])
        
        main_layout.addWidget(splitter)
        
        # Dialog buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal
        )
        # Use lambda to ensure proper handling
        buttons.accepted.connect(lambda: self.done(QDialog.Accepted))
        buttons.rejected.connect(lambda: self.done(QDialog.Rejected))
        main_layout.addWidget(buttons)
        
        self.setLayout(main_layout)
        
        # Update variable usage on text change
        self.text_edit.textChanged.connect(self.update_variable_usage)
        
    def load_step_data(self):
        """Load data from step"""
        self.name_edit.setText(self.step.name)
        self.text_edit.setPlainText(self.step.text)
        self.interval_spin.setValue(int(self.step.interval * 1000))
        self.use_variables_check.setChecked(self.step.use_variables)
        
    def insert_variable(self, item):
        """Insert variable at cursor position"""
        cursor = self.text_edit.textCursor()
        cursor.insertText(item.text())
        
    def insert_variable_text(self, variable_text):
        """Insert variable text from palette click"""
        cursor = self.text_edit.textCursor()
        cursor.insertText(variable_text)
        self.text_edit.setFocus()
        
    def on_variable_dropped(self, variable_text):
        """Handle variable drop"""
        self.update_variable_usage()
        
    def update_variable_usage(self):
        """Update the display of used variables"""
        import re
        text = self.text_edit.toPlainText()
        
        # Find all variables in the text
        pattern = r'\$\{(\w+)\}'
        variables = re.findall(pattern, text)
        
        if variables:
            unique_vars = list(set(variables))
            self.used_variables_label.setText(", ".join([f"${{{var}}}" for var in unique_vars]))
            self.used_variables_label.setStyleSheet("color: #28a745; padding: 5px; font-weight: bold;")
        else:
            self.used_variables_label.setText("없음")
            self.used_variables_label.setStyleSheet("color: #666; padding: 5px;")
            
    def get_step_data(self):
        """Get configured step data"""
        return {
            'name': self.name_edit.text(),
            'text': self.text_edit.toPlainText(),
            'interval': self.interval_spin.value() / 1000.0,
            'use_variables': self.use_variables_check.isChecked()
        }
        
    def closeEvent(self, event):
        """Handle close event to prevent parent window from closing"""
        event.accept()
        # Don't propagate to parent