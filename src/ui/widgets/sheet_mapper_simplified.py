"""
Simplified sheet and column mapping UI widget
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

class SimplifiedColumnMappingTable(QTableWidget):
    """Simplified table widget for column mapping - removed 'required' checkbox"""
    
    mappingChanged = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.columns: List[ColumnInfo] = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        # Set headers - Reduced from 6 to 5 columns
        self.setColumnCount(5)
        self.setHorizontalHeaderLabels([
            "선택", "Excel 열", "변수명", "데이터 타입", "샘플 데이터"
        ])
        
        # Configure table
        self.horizontalHeader().setStretchLastSection(False)
        self.horizontalHeader().setSectionResizeMode(0, QHeaderView.Fixed)
        self.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        
        self.setColumnWidth(0, 50)  # 선택
        
        # Enable sorting
        self.setSortingEnabled(True)
        
    def set_columns(self, columns: List[ColumnInfo]):
        """Set columns for mapping"""
        self.columns = columns
        self.setRowCount(len(columns))
        
        for row, col_info in enumerate(columns):
            # Selection checkbox
            select_checkbox = QCheckBox()
            select_checkbox.setChecked(True)  # Default to selected
            select_checkbox.stateChanged.connect(self.mappingChanged.emit)
            self.setCellWidget(row, 0, select_checkbox)
            
            # Excel column name
            col_item = QTableWidgetItem(col_info.name)
            col_item.setFlags(col_item.flags() & ~Qt.ItemIsEditable)
            self.setItem(row, 1, col_item)
            
            # Variable name (editable) - Enhanced auto-generation
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
            
    def _generate_variable_name(self, column_name: str) -> str:
        """Enhanced variable name generation with Korean to English mapping"""
        import re
        
        # Common Korean to English mappings
        korean_mappings = {
            '이름': 'name',
            '성명': 'full_name',
            '환자명': 'patient_name',
            '환자': 'patient',
            '번호': 'number',
            '전화': 'phone',
            '전화번호': 'phone_number',
            '주소': 'address',
            '생년월일': 'birth_date',
            '생일': 'birthday',
            '나이': 'age',
            '성별': 'gender',
            '날짜': 'date',
            '시간': 'time',
            '일시': 'datetime',
            '상태': 'status',
            '코드': 'code',
            '메모': 'memo',
            '비고': 'note',
            '금액': 'amount',
            '가격': 'price',
            '수량': 'quantity',
            '합계': 'total',
            '설명': 'description',
            '제목': 'title',
            '내용': 'content',
            '유형': 'type',
            '분류': 'category',
            '등록일': 'reg_date',
            '수정일': 'mod_date',
            '아이디': 'id',
            'ID': 'id'
        }
        
        # Check if column name is in mappings
        for korean, english in korean_mappings.items():
            if korean in column_name:
                return english
        
        # Fallback: Remove special characters and convert to snake_case
        var_name = re.sub(r'[^\w\s]', '', column_name)
        var_name = var_name.strip().lower().replace(' ', '_')
        
        # Ensure it starts with letter
        if var_name and not var_name[0].isalpha():
            var_name = 'col_' + var_name
            
        # If still empty or invalid, use generic name
        if not var_name or not var_name.replace('_', '').isalnum():
            var_name = 'column'
            
        return var_name
        
    def get_mappings(self) -> List[ColumnMapping]:
        """Get current column mappings"""
        mappings = []
        
        for row in range(self.rowCount()):
            select_checkbox = self.cellWidget(row, 0)
            if not select_checkbox.isChecked():
                continue
                
            excel_col = self.item(row, 1).text()
            var_name = self.item(row, 2).text()
            type_combo = self.cellWidget(row, 3)
            
            if var_name.strip():  # Only add if variable name is not empty
                mapping = ColumnMapping(
                    excel_column=excel_col,
                    variable_name=var_name.strip(),
                    data_type=ColumnType(type_combo.currentText()),
                    is_required=True  # All selected columns are considered required
                )
                mappings.append(mapping)
                
        return mappings

class SheetMapperWidget(QWidget):
    """Complete sheet and column mapping widget - simplified version"""
    
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
        mapping_group = QGroupBox("열 선택 및 매핑")
        mapping_layout = QVBoxLayout()
        
        # Instructions
        instructions = QLabel(
            "사용할 열을 선택하고 변수명을 지정하세요.\n"
            "변수명은 자동으로 생성되며, 필요시 수정할 수 있습니다."
        )
        instructions.setWordWrap(True)
        mapping_layout.addWidget(instructions)
        
        # Mapping table
        self.mapping_table = SimplifiedColumnMappingTable()
        mapping_layout.addWidget(self.mapping_table)
        
        # Quick actions
        action_layout = QHBoxLayout()
        
        self.select_all_btn = QPushButton("전체 선택")
        self.select_all_btn.clicked.connect(self._select_all)
        action_layout.addWidget(self.select_all_btn)
        
        self.select_none_btn = QPushButton("전체 해제")
        self.select_none_btn.clicked.connect(self._select_none)
        action_layout.addWidget(self.select_none_btn)
        
        self.auto_detect_btn = QPushButton("상태 열 자동 감지")
        self.auto_detect_btn.clicked.connect(self._auto_detect_status)
        action_layout.addWidget(self.auto_detect_btn)
        
        self.status_label = QLabel()
        action_layout.addWidget(self.status_label)
        action_layout.addStretch()
        
        mapping_layout.addLayout(action_layout)
        mapping_group.setLayout(mapping_layout)
        layout.addWidget(mapping_group)
        
        # Apply button
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.apply_btn = QPushButton("매핑 적용")
        self.apply_btn.clicked.connect(self._apply_mapping)
        self.apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 4px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
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
                
    def _select_all(self):
        """Select all columns"""
        for row in range(self.mapping_table.rowCount()):
            checkbox = self.mapping_table.cellWidget(row, 0)
            checkbox.setChecked(True)
            
    def _select_none(self):
        """Deselect all columns"""
        for row in range(self.mapping_table.rowCount()):
            checkbox = self.mapping_table.cellWidget(row, 0)
            checkbox.setChecked(False)
                
    def _auto_detect_status(self):
        """Auto-detect status column"""
        if not self.current_sheet:
            return
            
        status_keywords = ['상태', 'Status', '완료', '처리', 'status', 'STATUS', '결과', 'Result']
        
        for row in range(self.mapping_table.rowCount()):
            col_name = self.mapping_table.item(row, 1).text()
            
            # Check if column name contains status keywords
            for keyword in status_keywords:
                if keyword in col_name:
                    # Update variable name to 'status'
                    self.mapping_table.item(row, 2).setText('status')
                    # Ensure it's selected
                    checkbox = self.mapping_table.cellWidget(row, 0)
                    checkbox.setChecked(True)
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
            QMessageBox.warning(self, "경고", "최소 하나 이상의 열을 선택해주세요.")
            return
            
        # Check for duplicate variable names
        var_names = [m.variable_name for m in mappings]
        if len(var_names) != len(set(var_names)):
            QMessageBox.warning(self, "경고", "변수명이 중복되었습니다.\n각 변수명은 고유해야 합니다.")
            return
            
        self.mappingComplete.emit(
            self.sheet_selector.get_selected_sheet(),
            mappings
        )