"""
Variable palette widget for drag and drop functionality
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QGroupBox, QToolButton,
    QMenu, QStyle, QStyledItemDelegate, QStyleOptionViewItem
)
from PyQt5.QtCore import Qt, QMimeData, QByteArray, pyqtSignal, QRect, QSize
from PyQt5.QtGui import (
    QDrag, QPixmap, QPainter, QColor, QFont, QIcon,
    QPalette, QBrush, QPen
)
from excel.models import ColumnMapping, ColumnType
from typing import List, Optional
import json


class VariableItem(QListWidgetItem):
    """Custom list item representing a draggable variable"""
    
    def __init__(self, column_mapping: ColumnMapping):
        super().__init__()
        self.column_mapping = column_mapping
        self.excel_column = column_mapping.excel_column
        self.variable_name = column_mapping.variable_name
        self.column_type = column_mapping.data_type
        
        # Set display text
        self.setText(f"${{{self.variable_name}}}")
        
        # Set icon based on type
        self.set_type_icon()
        
        # Enable drag
        self.setFlags(self.flags() | Qt.ItemIsDragEnabled)
        
    def set_type_icon(self):
        """Set icon based on column type"""
        icon_text = ""
        tooltip = ""
        
        if self.column_type == ColumnType.TEXT:
            icon_text = "📝"
            tooltip = "텍스트 타입"
        elif self.column_type == ColumnType.NUMBER:
            icon_text = "🔢"
            tooltip = "숫자 타입"
        elif self.column_type == ColumnType.DATE:
            icon_text = "📅"
            tooltip = "날짜 타입"
            
        # Create icon from emoji
        pixmap = QPixmap(32, 32)
        pixmap.fill(Qt.transparent)
        painter = QPainter(pixmap)
        painter.setFont(QFont("Arial", 16))
        painter.drawText(pixmap.rect(), Qt.AlignCenter, icon_text)
        painter.end()
        
        self.setIcon(QIcon(pixmap))
        self.setToolTip(f"{self.variable_name} ({tooltip})")


class VariableItemDelegate(QStyledItemDelegate):
    """Custom delegate for variable items with visual enhancement"""
    
    def paint(self, painter: QPainter, option: QStyleOptionViewItem, index):
        """Custom painting for variable items"""
        # Get item data
        item = index.data(Qt.UserRole)
        if not isinstance(item, VariableItem):
            super().paint(painter, option, index)
            return
            
        # Save painter state
        painter.save()
        
        # Draw background
        if option.state & QStyle.State_Selected:
            painter.fillRect(option.rect, QColor(51, 153, 255, 100))
        elif option.state & QStyle.State_MouseOver:
            painter.fillRect(option.rect, QColor(51, 153, 255, 50))
            
        # Draw border
        if option.state & QStyle.State_Selected:
            painter.setPen(QPen(QColor(51, 153, 255), 2))
            painter.drawRoundedRect(option.rect.adjusted(2, 2, -2, -2), 5, 5)
            
        # Draw icon
        icon_rect = QRect(option.rect.left() + 5, 
                         option.rect.top() + 5,
                         24, 24)
        item.icon().paint(painter, icon_rect)
        
        # Draw text
        text_rect = QRect(icon_rect.right() + 5,
                         option.rect.top(),
                         option.rect.width() - icon_rect.width() - 15,
                         option.rect.height())
        
        painter.setFont(QFont("Arial", 11, QFont.Bold))
        painter.setPen(Qt.black)
        painter.drawText(text_rect, Qt.AlignVCenter, item.text())
        
        # Draw type badge
        type_text = ""
        type_color = QColor()
        
        if item.column_type == ColumnType.TEXT:
            type_text = "T"
            type_color = QColor(52, 168, 83)
        elif item.column_type == ColumnType.NUMBER:
            type_text = "N"
            type_color = QColor(66, 133, 244)
        elif item.column_type == ColumnType.DATE:
            type_text = "D"
            type_color = QColor(251, 188, 5)
            
        badge_rect = QRect(option.rect.right() - 25,
                          option.rect.top() + 5,
                          20, 20)
        painter.setBrush(QBrush(type_color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(badge_rect)
        
        painter.setPen(Qt.white)
        painter.setFont(QFont("Arial", 10, QFont.Bold))
        painter.drawText(badge_rect, Qt.AlignCenter, type_text)
        
        # Restore painter state
        painter.restore()


class DraggableVariableList(QListWidget):
    """List widget with drag functionality for variables"""
    
    variableDragged = pyqtSignal(str, str, str)  # variable_name, column_type, excel_column
    
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setDefaultDropAction(Qt.CopyAction)
        self.setSelectionMode(QListWidget.SingleSelection)
        
        # Set custom delegate
        self.setItemDelegate(VariableItemDelegate())
        
        # Style
        self.setStyleSheet("""
            QListWidget {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                padding: 5px;
            }
            QListWidget::item {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 3px;
                padding: 8px;
                margin: 3px;
                min-height: 35px;
            }
            QListWidget::item:selected {
                background-color: #e3f2fd;
                border: 1px solid #2196f3;
            }
            QListWidget::item:hover {
                background-color: #f5f5f5;
                border: 1px solid #2196f3;
            }
        """)
        
    def startDrag(self, supportedActions):
        """Start drag operation"""
        item = self.currentItem()
        if not isinstance(item, VariableItem):
            return
            
        # Create drag object
        drag = QDrag(self)
        
        # Create mime data
        mime_data = QMimeData()
        
        # Add variable data as JSON
        variable_data = {
            'variable_name': item.variable_name,
            'excel_column': item.excel_column,
            'column_type': item.column_type.value,
            'display_text': item.text()
        }
        
        mime_data.setText(item.text())  # For simple text drop
        mime_data.setData('application/x-variable', 
                         QByteArray(json.dumps(variable_data).encode()))
        
        drag.setMimeData(mime_data)
        
        # Create drag pixmap
        pixmap = self.create_drag_pixmap(item)
        drag.setPixmap(pixmap)
        drag.setHotSpot(pixmap.rect().center())
        
        # Emit signal
        self.variableDragged.emit(
            item.variable_name,
            item.column_type.value,
            item.excel_column
        )
        
        # Execute drag
        drag.exec_(Qt.CopyAction)
        
    def create_drag_pixmap(self, item: VariableItem) -> QPixmap:
        """Create pixmap for drag operation"""
        # Create pixmap
        pixmap = QPixmap(200, 50)
        pixmap.fill(Qt.transparent)
        
        # Paint
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.setBrush(QBrush(QColor(255, 255, 255, 230)))
        painter.setPen(QPen(QColor(51, 153, 255), 2))
        painter.drawRoundedRect(pixmap.rect().adjusted(1, 1, -1, -1), 10, 10)
        
        # Icon
        icon_rect = QRect(10, 10, 30, 30)
        item.icon().paint(painter, icon_rect)
        
        # Text
        painter.setPen(Qt.black)
        painter.setFont(QFont("Arial", 12, QFont.Bold))
        text_rect = QRect(50, 0, 140, 50)
        painter.drawText(text_rect, Qt.AlignVCenter, item.text())
        
        painter.end()
        return pixmap


class VariablePalette(QWidget):
    """Variable palette widget for Excel columns"""
    
    variableSelected = pyqtSignal(str)  # variable_name
    variableDragged = pyqtSignal(str, str, str)  # variable_name, column_type, excel_column
    
    def __init__(self):
        super().__init__()
        self.column_mappings: List[ColumnMapping] = []
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI components"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("변수 팔레트")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Help button
        help_btn = QToolButton()
        help_btn.setText("?")
        help_btn.setToolTip(
            "Excel 열을 변수로 사용할 수 있습니다.\n"
            "변수를 드래그하여 텍스트 입력 필드에 놓으세요."
        )
        header_layout.addWidget(help_btn)
        
        layout.addLayout(header_layout)
        
        # Search/Filter
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("변수 검색...")
        self.search_input.textChanged.connect(self.filter_variables)
        layout.addWidget(self.search_input)
        
        # Variable list
        self.variable_list = DraggableVariableList()
        self.variable_list.itemClicked.connect(self.on_variable_clicked)
        self.variable_list.variableDragged.connect(self.variableDragged.emit)
        layout.addWidget(self.variable_list)
        
        # Quick insert buttons
        quick_group = QGroupBox("빠른 삽입")
        quick_layout = QVBoxLayout()
        
        # Common variables
        common_vars = [
            ("현재 행 번호", "${현재행}"),
            ("전체 행 수", "${총행수}"),
            ("오늘 날짜", "${오늘날짜}")
        ]
        
        for label, var in common_vars:
            btn = QPushButton(label)
            btn.setToolTip(f"클릭하여 {var} 삽입")
            btn.clicked.connect(lambda checked, v=var: self.variableSelected.emit(v))
            quick_layout.addWidget(btn)
            
        quick_group.setLayout(quick_layout)
        layout.addWidget(quick_group)
        
        # Style
        self.setMinimumWidth(250)
        self.setMaximumWidth(300)
        
    def set_column_mappings(self, mappings: List[ColumnMapping]):
        """Set column mappings from Excel"""
        self.column_mappings = mappings
        self.update_variable_list()
        
    def update_variable_list(self):
        """Update variable list display"""
        self.variable_list.clear()
        
        for mapping in self.column_mappings:
            item = VariableItem(mapping)
            self.variable_list.addItem(item)
            
    def filter_variables(self, text: str):
        """Filter variables based on search text"""
        for i in range(self.variable_list.count()):
            item = self.variable_list.item(i)
            if isinstance(item, VariableItem):
                visible = (text.lower() in item.variable_name.lower() or
                          text.lower() in item.excel_column.lower())
                item.setHidden(not visible)
                
    def on_variable_clicked(self, item: QListWidgetItem):
        """Handle variable click"""
        if isinstance(item, VariableItem):
            self.variableSelected.emit(item.text())
            
    def add_custom_variable(self, name: str, value: str = ""):
        """Add a custom variable"""
        # Create dummy mapping for custom variables
        mapping = ColumnMapping(
            excel_column=f"custom_{name}",
            variable_name=name,
            data_type=ColumnType.TEXT
        )
        item = VariableItem(mapping)
        item.setText(f"${{{name}}}")
        self.variable_list.addItem(item)


# Add missing import
from PyQt5.QtWidgets import QLineEdit