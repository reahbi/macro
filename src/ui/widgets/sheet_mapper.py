"""
Sheet and column mapping UI widget
"""

from typing import Dict, List, Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, 
    QTableWidget, QTableWidgetItem, QPushButton,
    QLabel, QGroupBox, QHeaderView, QCheckBox,
    QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from excel.models import SheetInfo, ColumnInfo, ColumnMapping, ColumnType

class SheetSelectorWidget(QWidget):
    """Widget for selecting Excel sheet"""
    
    sheetSelected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.sheets: List[SheetInfo] = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QHBoxLayout()
        
        layout.addWidget(QLabel("시트 선택:"))
        
        self.sheet_combo = QComboBox()
        self.sheet_combo.setMinimumWidth(200)
        self.sheet_combo.currentTextChanged.connect(self.sheetSelected.emit)
        layout.addWidget(self.sheet_combo)
        
        self.info_label = QLabel()
        layout.addWidget(self.info_label)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def set_sheets(self, sheets: List[SheetInfo]):
        """Set available sheets"""
        self.sheets = sheets
        self.sheet_combo.clear()
        
        for sheet in sheets:
            display_text = f"{sheet.name} ({sheet.row_count}행 × {sheet.column_count}열)"
            self.sheet_combo.addItem(display_text, sheet.name)
            
        if sheets:
            self.sheetSelected.emit(sheets[0].name)
            
    def get_selected_sheet(self) -> Optional[str]:
        """Get currently selected sheet name"""
        if self.sheet_combo.currentData():
            return self.sheet_combo.currentData()
        return None

class ColumnMappingTable(QTableWidget):
    """Table widget for column mapping"""
    
    mappingChanged = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.columns: List[ColumnInfo] = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        # Set headers
        self.setColumnCount(6)
        self.setHorizontalHeaderLabels([
            "사용", "엑셀 열", "변수명", "데이터 타입", "샘플 데이터", "필수"
        ])
        
        # Configure table
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        
        self.setColumnWidth(0, 50)  # 사용
        self.setColumnWidth(5, 50)  # 필수
        
        # Enable sorting
        self.setSortingEnabled(True)
        
    def set_columns(self, columns: List[ColumnInfo]):
        """Set columns for mapping"""
        self.columns = columns
        self.setRowCount(len(columns))
        
        for row, col_info in enumerate(columns):
            # Use checkbox
            use_checkbox = QCheckBox()
            use_checkbox.setChecked(True)
            use_checkbox.stateChanged.connect(self.mappingChanged.emit)
            self.setCellWidget(row, 0, use_checkbox)
            
            # Excel column name
            col_item = QTableWidgetItem(col_info.name)
            col_item.setFlags(col_item.flags() & ~Qt.ItemIsEditable)
            self.setItem(row, 1, col_item)
            
            # Variable name (editable)
            var_name = self._generate_variable_name(col_info.name)
            var_item = QTableWidgetItem(var_name)
            self.setItem(row, 2, var_item)
            
            # Data type
            type_combo = QComboBox()
            type_combo.addItems([t.value for t in ColumnType])
            type_combo.setCurrentText(col_info.data_type.value)
            self.setCellWidget(row, 3, type_combo)
            
            # Sample data
            sample_text = ", ".join(str(v) for v in col_info.sample_values[:3])
            if len(col_info.sample_values) > 3:
                sample_text += "..."
            sample_item = QTableWidgetItem(sample_text)
            sample_item.setFlags(sample_item.flags() & ~Qt.ItemIsEditable)
            sample_item.setToolTip("\n".join(str(v) for v in col_info.sample_values))
            self.setItem(row, 4, sample_item)
            
            # Required checkbox
            required_checkbox = QCheckBox()
            required_checkbox.setChecked(False)
            self.setCellWidget(row, 5, required_checkbox)
            
    def _generate_variable_name(self, column_name: str) -> str:
        """Generate variable name from column name"""
        # Remove special characters and convert to snake_case
        import re
        var_name = re.sub(r'[^\w\s]', '', column_name)
        var_name = var_name.strip().lower().replace(' ', '_')
        
        # Ensure it starts with letter
        if var_name and not var_name[0].isalpha():
            var_name = 'col_' + var_name
            
        return var_name or 'column'
        
    def get_mappings(self) -> List[ColumnMapping]:
        """Get current column mappings"""
        mappings = []
        
        for row in range(self.rowCount()):
            use_checkbox = self.cellWidget(row, 0)
            if not use_checkbox.isChecked():
                continue
                
            excel_col = self.item(row, 1).text()
            var_name = self.item(row, 2).text()
            type_combo = self.cellWidget(row, 3)
            required_checkbox = self.cellWidget(row, 5)
            
            if var_name.strip():  # Only add if variable name is not empty
                mapping = ColumnMapping(
                    excel_column=excel_col,
                    variable_name=var_name.strip(),
                    data_type=ColumnType(type_combo.currentText()),
                    is_required=required_checkbox.isChecked()
                )
                mappings.append(mapping)
                
        return mappings

class SheetMapperWidget(QWidget):
    """Complete sheet and column mapping widget"""
    
    mappingComplete = pyqtSignal(str, list)  # sheet_name, mappings
    
    def __init__(self):
        super().__init__()
        self.current_sheet: Optional[SheetInfo] = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Sheet selector
        self.sheet_selector = SheetSelectorWidget()
        self.sheet_selector.sheetSelected.connect(self._on_sheet_selected)
        layout.addWidget(self.sheet_selector)
        
        # Column mapping
        mapping_group = QGroupBox("열 매핑 설정")
        mapping_layout = QVBoxLayout()
        
        # Mapping table
        self.mapping_table = ColumnMappingTable()
        mapping_layout.addWidget(self.mapping_table)
        
        # Auto-detect status column
        auto_layout = QHBoxLayout()
        self.auto_detect_btn = QPushButton("상태 열 자동 감지")
        self.auto_detect_btn.clicked.connect(self._auto_detect_status)
        auto_layout.addWidget(self.auto_detect_btn)
        
        self.status_label = QLabel()
        auto_layout.addWidget(self.status_label)
        auto_layout.addStretch()
        
        mapping_layout.addLayout(auto_layout)
        mapping_group.setLayout(mapping_layout)
        layout.addWidget(mapping_group)
        
        # Apply button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.apply_btn = QPushButton("매핑 적용")
        self.apply_btn.clicked.connect(self._apply_mapping)
        button_layout.addWidget(self.apply_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def set_file_info(self, sheets: List[SheetInfo]):
        """Set file information"""
        self.sheet_selector.set_sheets(sheets)
        
    def _on_sheet_selected(self, sheet_name: str):
        """Handle sheet selection"""
        # Find sheet info
        for sheet in self.sheet_selector.sheets:
            if sheet.name == sheet_name:
                self.current_sheet = sheet
                self.mapping_table.set_columns(sheet.columns)
                self._auto_detect_status()
                break
                
    def _auto_detect_status(self):
        """Auto-detect status column"""
        if not self.current_sheet:
            return
            
        status_keywords = ['상태', 'Status', '완료', '처리', 'status', 'STATUS']
        
        for row in range(self.mapping_table.rowCount()):
            col_name = self.mapping_table.item(row, 1).text()
            
            # Check if column name contains status keywords
            for keyword in status_keywords:
                if keyword in col_name:
                    # Set as status column
                    self.mapping_table.item(row, 2).setText('status')
                    required_checkbox = self.mapping_table.cellWidget(row, 5)
                    required_checkbox.setChecked(True)
                    self.status_label.setText(f"상태 열 감지됨: {col_name}")
                    return
                    
        self.status_label.setText("상태 열을 찾을 수 없음 (자동 생성됨)")
        
    def _apply_mapping(self):
        """Apply current mapping"""
        if not self.sheet_selector.get_selected_sheet():
            QMessageBox.warning(self, "경고", "시트를 선택해주세요.")
            return
            
        mappings = self.mapping_table.get_mappings()
        if not mappings:
            QMessageBox.warning(self, "경고", "최소 하나 이상의 열을 매핑해주세요.")
            return
            
        # Check for duplicate variable names
        var_names = [m.variable_name for m in mappings]
        if len(var_names) != len(set(var_names)):
            QMessageBox.warning(self, "경고", "변수명이 중복되었습니다.")
            return
            
        self.mappingComplete.emit(
            self.sheet_selector.get_selected_sheet(),
            mappings
        )