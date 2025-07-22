"""
Droppable widgets that accept variable drag and drop
"""

from PyQt5.QtWidgets import (
    QLineEdit, QTextEdit, QComboBox, QLabel,
    QWidget, QHBoxLayout, QVBoxLayout
)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData, QPropertyAnimation, QRect
from PyQt5.QtGui import QPainter, QColor, QPen, QBrush, QFont
import json


class DroppableLineEdit(QLineEdit):
    """Line edit that accepts variable drops"""
    
    variableDropped = pyqtSignal(str, int)  # variable_text, cursor_position
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.highlight_drop = False
        
        # Style
        self.base_style = """
            QLineEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 5px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #80bdff;
                box-shadow: 0 0 0 0.2rem rgba(0,123,255,.25);
            }
        """
        self.drop_style = """
            QLineEdit {
                border: 2px dashed #28a745;
                border-radius: 4px;
                padding: 5px;
                font-size: 13px;
                background-color: #d4edda;
            }
        """
        self.setStyleSheet(self.base_style)
        
    def dragEnterEvent(self, event):
        """Handle drag enter"""
        if event.mimeData().hasFormat('application/x-variable') or event.mimeData().hasText():
            event.acceptProposedAction()
            self.highlight_drop = True
            self.setStyleSheet(self.drop_style)
            
    def dragLeaveEvent(self, event):
        """Handle drag leave"""
        self.highlight_drop = False
        self.setStyleSheet(self.base_style)
        
    def dropEvent(self, event):
        """Handle drop event"""
        mime_data = event.mimeData()
        
        # Get drop position
        cursor_pos = self.cursorPositionAt(event.pos())
        
        # Extract variable data
        variable_text = ""
        
        if mime_data.hasFormat('application/x-variable'):
            # Custom variable data
            data = mime_data.data('application/x-variable')
            variable_info = json.loads(bytes(data).decode())
            variable_text = variable_info.get('display_text', '')
        elif mime_data.hasText():
            # Simple text
            variable_text = mime_data.text()
            
        if variable_text:
            # Insert at cursor position
            current_text = self.text()
            new_text = current_text[:cursor_pos] + variable_text + current_text[cursor_pos:]
            self.setText(new_text)
            
            # Set cursor after inserted text
            self.setCursorPosition(cursor_pos + len(variable_text))
            
            # Emit signal
            self.variableDropped.emit(variable_text, cursor_pos)
            
        # Reset style
        self.highlight_drop = False
        self.setStyleSheet(self.base_style)
        
        event.acceptProposedAction()
        
    def paintEvent(self, event):
        """Custom paint for drop highlight"""
        super().paintEvent(event)
        
        if self.highlight_drop:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Draw drop indicator
            pen = QPen(QColor(40, 167, 69), 2, Qt.DashLine)
            painter.setPen(pen)
            painter.setBrush(Qt.NoBrush)
            painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), 4, 4)


class DroppableTextEdit(QTextEdit):
    """Text edit that accepts variable drops"""
    
    variableDropped = pyqtSignal(str)  # variable_text
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.highlight_drop = False
        
        # Style
        self.base_style = """
            QTextEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 5px;
                font-size: 13px;
            }
            QTextEdit:focus {
                border-color: #80bdff;
            }
        """
        self.drop_style = """
            QTextEdit {
                border: 2px dashed #28a745;
                border-radius: 4px;
                padding: 5px;
                font-size: 13px;
                background-color: #d4edda;
            }
        """
        self.setStyleSheet(self.base_style)
        
    def dragEnterEvent(self, event):
        """Handle drag enter"""
        if event.mimeData().hasFormat('application/x-variable') or event.mimeData().hasText():
            event.acceptProposedAction()
            self.highlight_drop = True
            self.setStyleSheet(self.drop_style)
            
    def dragLeaveEvent(self, event):
        """Handle drag leave"""
        self.highlight_drop = False
        self.setStyleSheet(self.base_style)
        
    def dropEvent(self, event):
        """Handle drop event"""
        mime_data = event.mimeData()
        
        # Extract variable data
        variable_text = ""
        
        if mime_data.hasFormat('application/x-variable'):
            # Custom variable data
            data = mime_data.data('application/x-variable')
            variable_info = json.loads(bytes(data).decode())
            variable_text = variable_info.get('display_text', '')
        elif mime_data.hasText():
            # Simple text
            variable_text = mime_data.text()
            
        if variable_text:
            # Insert at cursor
            cursor = self.textCursor()
            cursor.insertText(variable_text)
            
            # Emit signal
            self.variableDropped.emit(variable_text)
            
        # Reset style
        self.highlight_drop = False
        self.setStyleSheet(self.base_style)
        
        event.acceptProposedAction()


class DroppableConditionWidget(QWidget):
    """Widget for condition setup with variable drops"""
    
    conditionChanged = pyqtSignal(str)  # condition_expression
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Variable field
        self.variable_field = DroppableLineEdit()
        self.variable_field.setPlaceholderText("변수를 드롭하세요")
        self.variable_field.variableDropped.connect(self.update_condition)
        self.variable_field.textChanged.connect(self.update_condition)
        layout.addWidget(self.variable_field)
        
        # Operator combo
        self.operator_combo = QComboBox()
        self.operator_combo.addItems(["==", "!=", ">", "<", ">=", "<=", "contains"])
        self.operator_combo.currentTextChanged.connect(self.update_condition)
        layout.addWidget(self.operator_combo)
        
        # Value field
        self.value_field = DroppableLineEdit()
        self.value_field.setPlaceholderText("값 또는 변수")
        self.value_field.variableDropped.connect(self.update_condition)
        self.value_field.textChanged.connect(self.update_condition)
        layout.addWidget(self.value_field)
        
    def update_condition(self):
        """Update condition expression"""
        variable = self.variable_field.text()
        operator = self.operator_combo.currentText()
        value = self.value_field.text()
        
        if operator == "contains":
            condition = f'"{value}" in {variable}' if variable else ""
        else:
            condition = f"{variable} {operator} {value}" if variable and value else ""
            
        self.conditionChanged.emit(condition)
        
    def get_condition(self) -> str:
        """Get current condition"""
        variable = self.variable_field.text()
        operator = self.operator_combo.currentText()
        value = self.value_field.text()
        
        if operator == "contains":
            return f'"{value}" in {variable}' if variable else ""
        else:
            return f"{variable} {operator} {value}" if variable and value else ""


class VariableHighlightWidget(QWidget):
    """Widget that highlights variable usage"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.variables_in_use = []
        self.setMinimumHeight(30)
        
    def set_variables(self, variables: list):
        """Set variables to highlight"""
        self.variables_in_use = variables
        self.update()
        
    def paintEvent(self, event):
        """Paint variable usage indicators"""
        if not self.variables_in_use:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Background
        painter.fillRect(self.rect(), QColor(248, 249, 250))
        
        # Draw variable badges
        x = 10
        y = 5
        
        for var in self.variables_in_use:
            # Measure text
            font = QFont("Arial", 10)
            painter.setFont(font)
            metrics = painter.fontMetrics()
            text_width = metrics.width(var)
            
            # Draw badge
            badge_rect = QRect(x, y, text_width + 20, 20)
            painter.setBrush(QBrush(QColor(52, 144, 220)))
            painter.setPen(Qt.NoPen)
            painter.drawRoundedRect(badge_rect, 10, 10)
            
            # Draw text
            painter.setPen(Qt.white)
            painter.drawText(badge_rect, Qt.AlignCenter, var)
            
            x += text_width + 30
            
            # Wrap to next line if needed
            if x > self.width() - 100:
                x = 10
                y += 25