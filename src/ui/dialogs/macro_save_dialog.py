"""
Macro save and load dialogs
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTextEdit, QRadioButton, QButtonGroup, QPushButton,
    QCheckBox, QSpinBox, QGroupBox, QProgressBar,
    QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from core.macro_types import Macro, MacroStep
from typing import List, Optional


class MacroSaveDialog(QDialog):
    """Dialog for saving macro with options"""
    
    def __init__(self, macro: Macro, parent=None):
        super().__init__(parent)
        self.macro = macro
        self.setWindowTitle("Save Macro")
        self.setModal(True)
        self.resize(400, 300)
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Macro name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name:"))
        self.name_edit = QLineEdit(self.macro.name)
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Description
        layout.addWidget(QLabel("Description:"))
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlainText(self.macro.description)
        self.desc_edit.setMaximumHeight(80)
        layout.addWidget(self.desc_edit)
        
        # Format selection
        format_group = QGroupBox("File Format")
        format_layout = QVBoxLayout()
        
        self.format_group = QButtonGroup()
        self.json_radio = QRadioButton("JSON (Human readable)")
        self.json_radio.setChecked(True)
        self.encrypted_radio = QRadioButton("Encrypted (Secure)")
        
        self.format_group.addButton(self.json_radio, 0)
        self.format_group.addButton(self.encrypted_radio, 1)
        
        format_layout.addWidget(self.json_radio)
        format_layout.addWidget(self.encrypted_radio)
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # Options
        options_group = QGroupBox("Options")
        options_layout = QVBoxLayout()
        
        self.include_vars_cb = QCheckBox("Include variables")
        self.include_vars_cb.setChecked(True)
        options_layout.addWidget(self.include_vars_cb)
        
        self.compress_cb = QCheckBox("Compress file")
        self.compress_cb.setChecked(False)
        options_layout.addWidget(self.compress_cb)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        save_btn.setDefault(True)
        btn_layout.addWidget(save_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
    def get_options(self) -> dict:
        """Get save options"""
        return {
            'name': self.name_edit.text(),
            'description': self.desc_edit.toPlainText(),
            'format': 'encrypted' if self.encrypted_radio.isChecked() else 'json',
            'include_variables': self.include_vars_cb.isChecked(),
            'compress': self.compress_cb.isChecked()
        }


class PartialMacroExportDialog(QDialog):
    """Dialog for exporting selected macro steps"""
    
    def __init__(self, selected_steps: List[MacroStep], all_variables: dict, parent=None):
        super().__init__(parent)
        self.selected_steps = selected_steps
        self.all_variables = all_variables
        self.setWindowTitle("Export Macro Steps")
        self.setModal(True)
        self.resize(450, 400)
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Info
        info_label = QLabel(f"Exporting {len(self.selected_steps)} selected steps")
        info_label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(info_label)
        
        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Export Name:"))
        self.name_edit = QLineEdit("Partial Macro Export")
        name_layout.addWidget(self.name_edit)
        layout.addLayout(name_layout)
        
        # Description
        layout.addWidget(QLabel("Description:"))
        self.desc_edit = QTextEdit()
        self.desc_edit.setPlainText("Exported macro steps")
        self.desc_edit.setMaximumHeight(60)
        layout.addWidget(self.desc_edit)
        
        # Variable dependencies
        var_group = QGroupBox("Variable Dependencies")
        var_layout = QVBoxLayout()
        
        # Check which variables are used
        used_vars = self._check_variable_usage()
        
        if used_vars:
            var_label = QLabel(f"The following variables are used in selected steps:")
            var_layout.addWidget(var_label)
            
            for var_name in used_vars:
                cb = QCheckBox(f"Include '{var_name}'")
                cb.setChecked(True)
                cb.setObjectName(var_name)
                var_layout.addWidget(cb)
        else:
            var_label = QLabel("No variables are used in selected steps")
            var_layout.addWidget(var_label)
            
        var_group.setLayout(var_layout)
        layout.addWidget(var_group)
        
        # Format
        format_group = QGroupBox("Export Format")
        format_layout = QVBoxLayout()
        
        self.format_group = QButtonGroup()
        self.json_radio = QRadioButton("JSON (Human readable)")
        self.json_radio.setChecked(True)
        self.encrypted_radio = QRadioButton("Encrypted (Secure)")
        
        self.format_group.addButton(self.json_radio, 0)
        self.format_group.addButton(self.encrypted_radio, 1)
        
        format_layout.addWidget(self.json_radio)
        format_layout.addWidget(self.encrypted_radio)
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        export_btn = QPushButton("Export")
        export_btn.clicked.connect(self.accept)
        export_btn.setDefault(True)
        btn_layout.addWidget(export_btn)
        
        layout.addLayout(btn_layout)
        self.setLayout(layout)
        
    def _check_variable_usage(self) -> List[str]:
        """Check which variables are used in selected steps"""
        used_vars = set()
        
        for step in self.selected_steps:
            # Check various step properties for variable usage
            step_dict = step.to_dict()
            self._find_variables_in_dict(step_dict, used_vars)
            
        return sorted(list(used_vars))
        
    def _find_variables_in_dict(self, d: dict, used_vars: set):
        """Recursively find variable references in dictionary"""
        for key, value in d.items():
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                var_name = value[2:-1]
                if var_name in self.all_variables:
                    used_vars.add(var_name)
            elif isinstance(value, dict):
                self._find_variables_in_dict(value, used_vars)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._find_variables_in_dict(item, used_vars)
                        
    def get_export_data(self) -> dict:
        """Get export data"""
        # Collect selected variables
        selected_vars = {}
        var_group = self.findChild(QGroupBox, "Variable Dependencies")
        if var_group:
            for cb in var_group.findChildren(QCheckBox):
                if cb.isChecked():
                    var_name = cb.objectName()
                    if var_name in self.all_variables:
                        selected_vars[var_name] = self.all_variables[var_name]
                        
        return {
            'name': self.name_edit.text(),
            'description': self.desc_edit.toPlainText(),
            'format': 'encrypted' if self.encrypted_radio.isChecked() else 'json',
            'steps': self.selected_steps,
            'variables': selected_vars
        }


class MacroLoadProgressDialog(QDialog):
    """Progress dialog for loading macros"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Loading Macro")
        self.setModal(True)
        self.setFixedSize(300, 100)
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        self.label = QLabel("Loading macro file...")
        layout.addWidget(self.label)
        
        self.progress = QProgressBar()
        self.progress.setRange(0, 0)  # Indeterminate
        layout.addWidget(self.progress)
        
        self.setLayout(layout)
        
    def set_message(self, message: str):
        """Set progress message"""
        self.label.setText(message)