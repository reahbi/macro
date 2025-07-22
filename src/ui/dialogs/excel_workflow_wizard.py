"""
Excel workflow wizard for step-by-step workflow creation
"""

from PyQt5.QtWidgets import (
    QWizard, QWizardPage, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFileDialog, QTableWidget, QTableWidgetItem,
    QComboBox, QListWidget, QListWidgetItem, QGroupBox,
    QTextEdit, QCheckBox, QSpinBox, QLineEdit, QRadioButton,
    QButtonGroup, QMessageBox, QHeaderView, QAbstractItemView,
    QInputDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QSize
from PyQt5.QtGui import QFont, QIcon
from excel.excel_manager import ExcelManager
from excel.models import ColumnMapping, ColumnType
from core.macro_types import (
    MacroStep, StepType, DynamicTextSearchStep, 
    KeyboardTypeStep, MouseClickStep, WaitTimeStep
)
import uuid
import os


class ExcelFileSelectionPage(QWizardPage):
    """Step 1: Excel file selection"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Step 1: Excel 파일 선택")
        self.setSubTitle("반복 작업에 사용할 Excel 파일을 선택하세요")
        
        self.excel_manager = ExcelManager()
        self.selected_file = None
        
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        
        # File selection group
        file_group = QGroupBox("Excel 파일")
        file_layout = QVBoxLayout()
        
        # File path display
        self.file_label = QLabel("파일을 선택하세요...")
        self.file_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        file_layout.addWidget(self.file_label)
        
        # Browse button
        browse_btn = QPushButton("파일 찾아보기...")
        browse_btn.clicked.connect(self.browse_file)
        file_layout.addWidget(browse_btn)
        
        file_group.setLayout(file_layout)
        layout.addWidget(file_group)
        
        # Sheet selection
        sheet_group = QGroupBox("시트 선택")
        sheet_layout = QVBoxLayout()
        
        self.sheet_combo = QComboBox()
        self.sheet_combo.setEnabled(False)
        self.sheet_combo.currentTextChanged.connect(self.on_sheet_changed)
        sheet_layout.addWidget(self.sheet_combo)
        
        sheet_group.setLayout(sheet_layout)
        layout.addWidget(sheet_group)
        
        # Preview
        preview_group = QGroupBox("데이터 미리보기")
        preview_layout = QVBoxLayout()
        
        self.preview_table = QTableWidget()
        self.preview_table.setMaximumHeight(200)
        preview_layout.addWidget(self.preview_table)
        
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Example
        example_label = QLabel(
            "💡 <b>팁:</b> Excel 파일의 첫 번째 행은 열 제목으로 사용됩니다.\n"
            "예: 환자번호, 이름, 혈압, 혈당 등"
        )
        example_label.setWordWrap(True)
        example_label.setStyleSheet("background-color: #e8f4f8; padding: 10px; border-radius: 5px;")
        layout.addWidget(example_label)
        
        layout.addStretch()
        
    def browse_file(self):
        """Browse for Excel file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Excel 파일 선택",
            "",
            "Excel Files (*.xlsx *.xls);;All Files (*.*)"
        )
        
        if file_path:
            self.load_file(file_path)
            
    def load_file(self, file_path: str):
        """Load Excel file"""
        try:
            file_info = self.excel_manager.load_file(file_path)
            if file_info:
                self.selected_file = file_path
                self.file_label.setText(os.path.basename(file_path))
                
                # Update sheet combo
                self.sheet_combo.setEnabled(True)
                self.sheet_combo.clear()
                # Extract sheet names from SheetInfo objects
                sheet_names = [sheet.name for sheet in file_info.sheets]
                self.sheet_combo.addItems(sheet_names)
                
                self.completeChanged.emit()
        except Exception as e:
            QMessageBox.critical(self, "오류", f"파일을 불러올 수 없습니다: {str(e)}")
            
    def on_sheet_changed(self, sheet_name: str):
        """Handle sheet selection change"""
        if sheet_name:
            self.excel_manager.set_active_sheet(sheet_name)
            self.update_preview()
            
    def update_preview(self):
        """Update data preview"""
        try:
            df = self.excel_manager.get_sheet_data()
            if df is not None:
                # Show first 5 rows
                preview_df = df.head(5)
                
                # Update table
                self.preview_table.setRowCount(len(preview_df))
                self.preview_table.setColumnCount(len(preview_df.columns))
                self.preview_table.setHorizontalHeaderLabels(preview_df.columns.tolist())
                
                for row in range(len(preview_df)):
                    for col in range(len(preview_df.columns)):
                        item = QTableWidgetItem(str(preview_df.iloc[row, col]))
                        self.preview_table.setItem(row, col, item)
                        
                self.preview_table.resizeColumnsToContents()
        except Exception as e:
            print(f"Preview update error: {e}")
            
    def isComplete(self):
        """Check if page is complete"""
        return bool(self.selected_file and self.sheet_combo.currentText())
        
    def get_excel_manager(self):
        """Get Excel manager instance"""
        return self.excel_manager


class ColumnMappingPage(QWizardPage):
    """Step 2: Column selection and mapping"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Step 2: 열 선택")
        self.setSubTitle("작업에 사용할 Excel 열을 선택하고 이름을 지정하세요")
        
        self.mappings = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "각 열에 대해:\n"
            "1. 사용할 열을 체크하세요\n"
            "2. 변수명을 지정하세요 (한글 가능)\n"
            "3. 데이터 타입을 선택하세요"
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Mapping table
        self.mapping_table = QTableWidget()
        self.mapping_table.setColumnCount(4)
        self.mapping_table.setHorizontalHeaderLabels(["사용", "Excel 열", "변수명", "타입"])
        
        # Set column widths
        header = self.mapping_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        layout.addWidget(self.mapping_table)
        
        # Quick templates
        template_group = QGroupBox("빠른 템플릿")
        template_layout = QHBoxLayout()
        
        healthcare_btn = QPushButton("의료 템플릿")
        healthcare_btn.clicked.connect(self.apply_healthcare_template)
        template_layout.addWidget(healthcare_btn)
        
        office_btn = QPushButton("사무 템플릿")
        office_btn.clicked.connect(self.apply_office_template)
        template_layout.addWidget(office_btn)
        
        template_group.setLayout(template_layout)
        layout.addWidget(template_group)
        
    def initializePage(self):
        """Initialize page when shown"""
        # Get Excel manager from previous page
        file_page = self.wizard().page(0)
        excel_manager = file_page.get_excel_manager()
        
        # Get columns
        df = excel_manager.get_sheet_data()
        if df is not None:
            columns = df.columns.tolist()
            
            # Clear and populate table
            self.mapping_table.setRowCount(len(columns))
            
            for i, col in enumerate(columns):
                # Checkbox
                checkbox = QCheckBox()
                checkbox.setChecked(True)  # Default to checked
                self.mapping_table.setCellWidget(i, 0, checkbox)
                
                # Column name
                self.mapping_table.setItem(i, 1, QTableWidgetItem(col))
                
                # Variable name (default to column name)
                var_name_item = QTableWidgetItem(col)
                self.mapping_table.setItem(i, 2, var_name_item)
                
                # Type combo
                type_combo = QComboBox()
                type_combo.addItems(["텍스트", "숫자", "날짜"])
                self.mapping_table.setCellWidget(i, 3, type_combo)
                
    def apply_healthcare_template(self):
        """Apply healthcare-specific naming template"""
        common_mappings = {
            "환자번호": "환자번호",
            "patient_id": "환자번호",
            "이름": "이름",
            "name": "이름",
            "혈압": "혈압",
            "blood_pressure": "혈압",
            "혈당": "혈당",
            "blood_sugar": "혈당",
            "콜레스테롤": "콜레스테롤",
            "cholesterol": "콜레스테롤"
        }
        
        self.apply_template(common_mappings)
        
    def apply_office_template(self):
        """Apply office-specific naming template"""
        common_mappings = {
            "사번": "사번",
            "employee_id": "사번",
            "이름": "이름",
            "name": "이름",
            "부서": "부서",
            "department": "부서",
            "직급": "직급",
            "position": "직급"
        }
        
        self.apply_template(common_mappings)
        
    def apply_template(self, mappings: dict):
        """Apply a template mapping"""
        for row in range(self.mapping_table.rowCount()):
            col_item = self.mapping_table.item(row, 1)
            if col_item:
                col_name = col_item.text().lower()
                for key, value in mappings.items():
                    if key.lower() in col_name:
                        self.mapping_table.item(row, 2).setText(value)
                        break
                        
    def isComplete(self):
        """Check if page is complete"""
        # At least one column should be selected
        for row in range(self.mapping_table.rowCount()):
            checkbox = self.mapping_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                return True
        return False
        
    def get_column_mappings(self):
        """Get column mappings"""
        mappings = []
        
        for row in range(self.mapping_table.rowCount()):
            checkbox = self.mapping_table.cellWidget(row, 0)
            if checkbox and checkbox.isChecked():
                excel_col = self.mapping_table.item(row, 1).text()
                var_name = self.mapping_table.item(row, 2).text()
                type_combo = self.mapping_table.cellWidget(row, 3)
                
                # Convert type
                type_text = type_combo.currentText()
                if type_text == "텍스트":
                    col_type = ColumnType.TEXT
                elif type_text == "숫자":
                    col_type = ColumnType.NUMBER
                else:
                    col_type = ColumnType.DATE
                    
                mappings.append(ColumnMapping(excel_col, var_name, col_type))
                
        return mappings


class WorkflowDefinitionPage(QWizardPage):
    """Step 3: Define workflow steps"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("Step 3: 작업 정의")
        self.setSubTitle("각 행에 대해 수행할 작업을 정의하세요")
        
        self.workflow_steps = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        
        # Instructions
        instructions = QLabel(
            "반복할 작업을 추가하세요. ${변수명} 형식으로 Excel 데이터를 사용할 수 있습니다."
        )
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Step list
        step_group = QGroupBox("작업 단계")
        step_layout = QVBoxLayout()
        
        self.step_list = QListWidget()
        self.step_list.setDragDropMode(QListWidget.InternalMove)
        step_layout.addWidget(self.step_list)
        
        # Step buttons
        btn_layout = QHBoxLayout()
        
        add_text_btn = QPushButton("텍스트 찾기/클릭")
        add_text_btn.clicked.connect(lambda: self.add_step("text_search"))
        btn_layout.addWidget(add_text_btn)
        
        add_type_btn = QPushButton("텍스트 입력")
        add_type_btn.clicked.connect(lambda: self.add_step("keyboard"))
        btn_layout.addWidget(add_type_btn)
        
        add_click_btn = QPushButton("마우스 클릭")
        add_click_btn.clicked.connect(lambda: self.add_step("mouse"))
        btn_layout.addWidget(add_click_btn)
        
        add_wait_btn = QPushButton("대기")
        add_wait_btn.clicked.connect(lambda: self.add_step("wait"))
        btn_layout.addWidget(add_wait_btn)
        
        step_layout.addLayout(btn_layout)
        
        # Edit/Delete buttons
        edit_btn_layout = QHBoxLayout()
        
        edit_btn = QPushButton("편집")
        edit_btn.clicked.connect(self.edit_step)
        edit_btn_layout.addWidget(edit_btn)
        
        delete_btn = QPushButton("삭제")
        delete_btn.clicked.connect(self.delete_step)
        edit_btn_layout.addWidget(delete_btn)
        
        step_layout.addLayout(edit_btn_layout)
        
        step_group.setLayout(step_layout)
        layout.addWidget(step_group)
        
        # Common workflows
        template_group = QGroupBox("일반적인 워크플로우")
        template_layout = QVBoxLayout()
        
        emr_btn = QPushButton("EMR 데이터 입력")
        emr_btn.clicked.connect(self.add_emr_workflow)
        template_layout.addWidget(emr_btn)
        
        web_form_btn = QPushButton("웹 폼 입력")
        web_form_btn.clicked.connect(self.add_web_form_workflow)
        template_layout.addWidget(web_form_btn)
        
        template_group.setLayout(template_layout)
        layout.addWidget(template_group)
        
    def add_step(self, step_type: str):
        """Add a new step"""
        if step_type == "text_search":
            step = DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="텍스트 찾기",
                search_text="검색할 텍스트",
                click_on_found=True
            )
        elif step_type == "keyboard":
            step = KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="텍스트 입력",
                text="${변수명}",
                use_variables=True
            )
        elif step_type == "mouse":
            step = MouseClickStep(
                step_id=str(uuid.uuid4()),
                name="마우스 클릭",
                x=100,
                y=100
            )
        elif step_type == "wait":
            step = WaitTimeStep(
                step_id=str(uuid.uuid4()),
                name="대기",
                seconds=1.0
            )
        else:
            return
            
        self.workflow_steps.append(step)
        self.update_step_list()
        
    def edit_step(self):
        """Edit selected step"""
        current = self.step_list.currentRow()
        if current >= 0:
            step = self.workflow_steps[current]
            # Simple edit dialog for demonstration
            if isinstance(step, DynamicTextSearchStep):
                text, ok = QInputDialog.getText(
                    self, "텍스트 편집", 
                    "검색할 텍스트:", 
                    text=step.search_text
                )
                if ok:
                    step.search_text = text
                    self.update_step_list()
            elif isinstance(step, KeyboardTypeStep):
                text, ok = QInputDialog.getText(
                    self, "텍스트 편집", 
                    "입력할 텍스트:", 
                    text=step.text
                )
                if ok:
                    step.text = text
                    self.update_step_list()
                    
    def delete_step(self):
        """Delete selected step"""
        current = self.step_list.currentRow()
        if current >= 0:
            del self.workflow_steps[current]
            self.update_step_list()
            
    def update_step_list(self):
        """Update step list display"""
        self.step_list.clear()
        
        for i, step in enumerate(self.workflow_steps):
            if isinstance(step, DynamicTextSearchStep):
                text = f"{i+1}. 텍스트 찾기: '{step.search_text}'"
            elif isinstance(step, KeyboardTypeStep):
                text = f"{i+1}. 텍스트 입력: '{step.text}'"
            elif isinstance(step, MouseClickStep):
                text = f"{i+1}. 클릭: ({step.x}, {step.y})"
            elif isinstance(step, WaitTimeStep):
                text = f"{i+1}. 대기: {step.seconds}초"
            else:
                text = f"{i+1}. {step.name}"
                
            self.step_list.addItem(text)
            
    def add_emr_workflow(self):
        """Add EMR data entry workflow template"""
        steps = [
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="환자조회 찾기",
                search_text="환자조회",
                click_on_found=True
            ),
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="환자번호 입력",
                text="${환자번호}",
                use_variables=True
            ),
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="Enter 키",
                text="{ENTER}"
            ),
            WaitTimeStep(
                step_id=str(uuid.uuid4()),
                name="로딩 대기",
                seconds=2.0
            )
        ]
        
        self.workflow_steps.extend(steps)
        self.update_step_list()
        
    def add_web_form_workflow(self):
        """Add web form entry workflow template"""
        steps = [
            DynamicTextSearchStep(
                step_id=str(uuid.uuid4()),
                name="이름 필드 찾기",
                search_text="이름",
                click_on_found=True
            ),
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="이름 입력",
                text="${이름}",
                use_variables=True
            ),
            KeyboardTypeStep(
                step_id=str(uuid.uuid4()),
                name="Tab 키",
                text="{TAB}"
            )
        ]
        
        self.workflow_steps.extend(steps)
        self.update_step_list()
        
    def isComplete(self):
        """Check if page is complete"""
        return len(self.workflow_steps) > 0
        
    def get_workflow_steps(self):
        """Get workflow steps"""
        return self.workflow_steps


class ExcelWorkflowWizard(QWizard):
    """Main Excel workflow wizard"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Excel 워크플로우 마법사")
        self.setWizardStyle(QWizard.ModernStyle)
        self.resize(800, 600)
        
        # Add pages
        self.file_page = ExcelFileSelectionPage()
        self.mapping_page = ColumnMappingPage()
        self.workflow_page = WorkflowDefinitionPage()
        
        self.addPage(self.file_page)
        self.addPage(self.mapping_page)
        self.addPage(self.workflow_page)
        
        # Set button text
        self.setButtonText(QWizard.NextButton, "다음 >")
        self.setButtonText(QWizard.BackButton, "< 이전")
        self.setButtonText(QWizard.FinishButton, "완료")
        self.setButtonText(QWizard.CancelButton, "취소")
        
    def get_excel_file(self):
        """Get selected Excel file path"""
        return self.file_page.selected_file
        
    def get_column_mappings(self):
        """Get column mappings"""
        return self.mapping_page.get_column_mappings()
        
    def get_workflow_steps(self):
        """Get workflow steps"""
        return self.workflow_page.get_workflow_steps()