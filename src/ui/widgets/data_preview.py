"""
Excel data preview widget with pagination
"""

from typing import Optional, List
import pandas as pd
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, 
    QTableWidgetItem, QPushButton, QLabel, QSpinBox,
    QComboBox, QLineEdit, QCheckBox, QHeaderView,
    QGroupBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QColor, QBrush
from excel.models import ExcelData, ColumnType

class DataPreviewTable(QTableWidget):
    """Table widget for previewing Excel data"""
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        # Configure table appearance
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setDefaultSectionSize(24)
        
    def load_data(self, dataframe: pd.DataFrame, start_row: int = 0, 
                  rows_per_page: int = 100, highlight_status: bool = True):
        """Load data into table"""
        # Clear existing data
        self.clear()
        
        # Set columns
        columns = dataframe.columns.tolist()
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)
        
        # Determine rows to display
        end_row = min(start_row + rows_per_page, len(dataframe))
        display_rows = end_row - start_row
        self.setRowCount(display_rows)
        
        # Find status column
        status_col_idx = None
        if highlight_status:
            status_columns = ['매크로_상태', '상태', 'Status', '완료여부', '처리상태', 'status', 'STATUS']
            for idx, col in enumerate(columns):
                if col in status_columns:
                    status_col_idx = idx
                    break
        
        # Populate data
        for row in range(display_rows):
            df_row = start_row + row
            
            # Set row header to show actual row number
            self.setVerticalHeaderItem(row, QTableWidgetItem(str(df_row + 1)))
            
            for col in range(len(columns)):
                value = dataframe.iloc[df_row, col]
                
                # Handle different data types
                if pd.isna(value):
                    item_text = ""
                elif isinstance(value, float):
                    item_text = f"{value:.2f}" if value % 1 else str(int(value))
                else:
                    item_text = str(value)
                
                item = QTableWidgetItem(item_text)
                
                # Apply status highlighting
                if col == status_col_idx and highlight_status:
                    if value in ['완료', 'Completed', 'Complete', 'Done']:
                        item.setBackground(QBrush(QColor(200, 255, 200)))
                    elif value in ['실패', 'Failed', 'Error']:
                        item.setBackground(QBrush(QColor(255, 200, 200)))
                    elif value in ['진행중', 'Processing', 'In Progress']:
                        item.setBackground(QBrush(QColor(255, 255, 200)))
                
                self.setItem(row, col, item)
        
        # Resize columns to content
        self.resizeColumnsToContents()

class DataPreviewWidget(QWidget):
    """Complete data preview widget with controls"""
    
    rowSelected = pyqtSignal(int)  # Emit actual dataframe row index
    
    def __init__(self):
        super().__init__()
        self.excel_data: Optional[ExcelData] = None
        self.current_page = 0
        self.rows_per_page = 100
        self.filtered_indices: Optional[List[int]] = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Filter controls - make more compact
        filter_group = QGroupBox("필터 옵션")
        filter_group.setMaximumHeight(80)  # Limit height to save space
        filter_layout = QHBoxLayout()
        filter_layout.setContentsMargins(5, 5, 5, 5)  # Reduce margins
        
        # Status filter
        self.incomplete_only = QCheckBox("미완료 항목만 표시")
        self.incomplete_only.stateChanged.connect(self._apply_filter)
        filter_layout.addWidget(self.incomplete_only)
        
        # Search
        filter_layout.addWidget(QLabel("검색:"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("검색어 입력...")
        self.search_input.textChanged.connect(self._apply_filter)
        filter_layout.addWidget(self.search_input)
        
        filter_layout.addStretch()
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Data table
        self.data_table = DataPreviewTable()
        self.data_table.cellDoubleClicked.connect(self._on_cell_double_clicked)
        layout.addWidget(self.data_table)
        
        # Pagination controls
        pagination_layout = QHBoxLayout()
        
        # Page size
        pagination_layout.addWidget(QLabel("행/페이지:"))
        self.page_size_spin = QSpinBox()
        self.page_size_spin.setRange(10, 1000)
        self.page_size_spin.setSingleStep(50)
        self.page_size_spin.setValue(self.rows_per_page)
        self.page_size_spin.valueChanged.connect(self._on_page_size_changed)
        pagination_layout.addWidget(self.page_size_spin)
        
        pagination_layout.addStretch()
        
        # Page navigation
        self.prev_btn = QPushButton("◀ 이전")
        self.prev_btn.clicked.connect(self._prev_page)
        pagination_layout.addWidget(self.prev_btn)
        
        self.page_label = QLabel("1 / 1")
        pagination_layout.addWidget(self.page_label)
        
        self.next_btn = QPushButton("다음 ▶")
        self.next_btn.clicked.connect(self._next_page)
        pagination_layout.addWidget(self.next_btn)
        
        pagination_layout.addStretch()
        
        # Row count info
        self.row_info_label = QLabel()
        pagination_layout.addWidget(self.row_info_label)
        
        layout.addLayout(pagination_layout)
        self.setLayout(layout)
        
    def load_excel_data(self, excel_data: ExcelData):
        """Load Excel data for preview"""
        self.excel_data = excel_data
        self.current_page = 0
        self.filtered_indices = None
        self._apply_filter()
        
    def _apply_filter(self):
        """Apply current filter settings"""
        if not self.excel_data:
            return
            
        df = self.excel_data.dataframe
        
        # Start with all rows
        mask = pd.Series([True] * len(df))
        
        # Apply incomplete filter
        if self.incomplete_only.isChecked():
            # First try to find 매크로_상태 column, then fall back to get_status_column
            status_col = None
            if '매크로_상태' in df.columns:
                status_col = '매크로_상태'
            else:
                status_col = self.excel_data.get_status_column()
            
            if status_col:
                mask &= ~df[status_col].isin(['완료', 'Completed', 'Complete', 'Done'])
        
        # Apply search filter
        search_text = self.search_input.text().strip()
        if search_text:
            search_mask = pd.Series([False] * len(df))
            for col in df.columns:
                if df[col].dtype == 'object':  # String columns only
                    search_mask |= df[col].astype(str).str.contains(
                        search_text, case=False, na=False
                    )
            mask &= search_mask
        
        # Get filtered indices
        self.filtered_indices = df[mask].index.tolist()
        
        # Reset to first page
        self.current_page = 0
        self._update_display()
        
    def _update_display(self):
        """Update table display"""
        if not self.excel_data:
            return
            
        df = self.excel_data.dataframe
        
        # Use filtered data if available
        if self.filtered_indices is not None:
            if not self.filtered_indices:
                self.data_table.setRowCount(0)
                self._update_pagination_controls()
                return
            display_df = df.loc[self.filtered_indices]
        else:
            display_df = df
        
        # Calculate page boundaries
        start_idx = self.current_page * self.rows_per_page
        
        # Load data into table
        self.data_table.load_data(
            display_df,
            start_row=start_idx,
            rows_per_page=self.rows_per_page
        )
        
        self._update_pagination_controls()
        
    def _update_pagination_controls(self):
        """Update pagination control states"""
        if not self.excel_data:
            return
            
        # Calculate total pages
        if self.filtered_indices is not None:
            total_rows = len(self.filtered_indices)
        else:
            total_rows = len(self.excel_data.dataframe)
            
        total_pages = max(1, (total_rows + self.rows_per_page - 1) // self.rows_per_page)
        
        # Update label
        self.page_label.setText(f"{self.current_page + 1} / {total_pages}")
        
        # Update button states
        self.prev_btn.setEnabled(self.current_page > 0)
        self.next_btn.setEnabled(self.current_page < total_pages - 1)
        
        # Update row info
        if self.filtered_indices is not None:
            self.row_info_label.setText(
                f"표시: {len(self.filtered_indices)} / 전체: {len(self.excel_data.dataframe)} 행"
            )
        else:
            self.row_info_label.setText(f"전체: {total_rows} 행")
        
    def _on_page_size_changed(self, value: int):
        """Handle page size change"""
        self.rows_per_page = value
        self.current_page = 0
        self._update_display()
        
    def _prev_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self._update_display()
            
    def _next_page(self):
        """Go to next page"""
        self.current_page += 1
        self._update_display()
        
    def _on_cell_double_clicked(self, row: int, column: int):
        """Handle cell double click"""
        # Calculate actual dataframe row index
        actual_row = self.current_page * self.rows_per_page + row
        
        if self.filtered_indices is not None:
            if actual_row < len(self.filtered_indices):
                df_row_index = self.filtered_indices[actual_row]
                self.rowSelected.emit(df_row_index)
        else:
            self.rowSelected.emit(actual_row)