"""
Drag and drop macro editor widget
"""

from typing import Optional, List, Dict, Any
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QListWidgetItem,
    QPushButton, QLabel, QScrollArea, QFrame, QMenu, QMessageBox,
    QSplitter, QGroupBox, QToolButton, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData, QByteArray, QDataStream, QIODevice
from PyQt5.QtGui import QDrag, QDragEnterEvent, QDropEvent, QPalette, QIcon, QCursor
from core.macro_types import (
    MacroStep, StepType, Macro, StepFactory,
    MouseClickStep, KeyboardTypeStep, WaitTimeStep
)

class StepPaletteItem(QListWidgetItem):
    """Draggable step type item"""
    
    def __init__(self, step_type: StepType, display_name: str, icon: Optional[QIcon] = None):
        super().__init__(display_name)
        self.step_type = step_type
        if icon:
            self.setIcon(icon)
        self.setToolTip(self._get_tooltip())
        
    def _get_tooltip(self) -> str:
        """Get tooltip for step type"""
        tooltips = {
            StepType.MOUSE_CLICK: "마우스 클릭 동작을 추가합니다",
            StepType.MOUSE_MOVE: "마우스 이동 동작을 추가합니다",
            StepType.KEYBOARD_TYPE: "텍스트 입력 동작을 추가합니다",
            StepType.KEYBOARD_HOTKEY: "단축키 입력 동작을 추가합니다",
            StepType.WAIT_TIME: "지정된 시간만큼 대기합니다",
            StepType.WAIT_IMAGE: "이미지가 나타날 때까지 대기합니다",
            StepType.IMAGE_SEARCH: "화면에서 이미지를 검색합니다",
            StepType.OCR_TEXT: "화면에서 텍스트를 검색하고 클릭합니다",
            StepType.SCREENSHOT: "화면을 캡처합니다",
            StepType.IF_CONDITION: "조건문을 추가합니다",
            StepType.LOOP: "반복문을 추가합니다"
        }
        return tooltips.get(self.step_type, "")

class StepPalette(QListWidget):
    """Palette of draggable step types"""
    
    def __init__(self):
        super().__init__()
        self.setDragEnabled(True)
        self.setDefaultDropAction(Qt.CopyAction)
        self.setMaximumWidth(200)
        self.init_steps()
        
    def init_steps(self):
        """Initialize available step types"""
        step_configs = [
            (StepType.MOUSE_CLICK, "마우스 클릭", "🖱️"),
            (StepType.MOUSE_MOVE, "마우스 이동", "↗️"),
            (StepType.KEYBOARD_TYPE, "텍스트 입력", "⌨️"),
            (StepType.KEYBOARD_HOTKEY, "단축키", "⌘"),
            (StepType.WAIT_TIME, "대기", "⏱️"),
            (StepType.WAIT_IMAGE, "이미지 대기", "🖼️"),
            (StepType.IMAGE_SEARCH, "이미지 검색", "🔍"),
            (StepType.OCR_TEXT, "텍스트 검색", "🔤"),
            (StepType.SCREENSHOT, "화면 캡처", "📷"),
            (StepType.IF_CONDITION, "조건문", "❓"),
            (StepType.LOOP, "반복문", "🔄"),
        ]
        
        for step_type, name, emoji in step_configs:
            item = StepPaletteItem(step_type, f"{emoji} {name}")
            self.addItem(item)
            
    def startDrag(self, supportedActions):
        """Start dragging a step type"""
        item = self.currentItem()
        if isinstance(item, StepPaletteItem):
            drag = QDrag(self)
            mime_data = QMimeData()
            
            # Store step type in MIME data
            byte_array = QByteArray()
            stream = QDataStream(byte_array, QIODevice.WriteOnly)
            stream.writeQString(item.step_type.value)
            
            mime_data.setData("application/x-steptype", byte_array)
            mime_data.setText(item.text())
            drag.setMimeData(mime_data)
            
            drag.exec_(Qt.CopyAction)

class MacroStepWidget(QFrame):
    """Widget representing a single macro step"""
    
    editRequested = pyqtSignal(MacroStep)
    deleteRequested = pyqtSignal(str)  # step_id
    moveRequested = pyqtSignal(str, int)  # step_id, new_index
    
    def __init__(self, step: MacroStep, index: int):
        super().__init__()
        self.step = step
        self.index = index
        self.setFrameStyle(QFrame.Box)
        self.setAcceptDrops(True)
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QHBoxLayout()
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Drag handle
        self.handle = QLabel("≡")
        self.handle.setStyleSheet("font-size: 16px; color: #888;")
        self.handle.setCursor(Qt.OpenHandCursor)
        layout.addWidget(self.handle)
        
        # Step info
        info_layout = QVBoxLayout()
        
        # Step name and type with icon
        step_icon = self._get_step_icon()
        name_text = f"{step_icon} <b>{self.step.name or self.step.step_type.value}</b>"
        name_label = QLabel(name_text)
        info_layout.addWidget(name_label)
        
        # Step details based on type
        details_text = self._get_step_details()
        if details_text:
            details_label = QLabel(details_text)
            details_label.setWordWrap(True)
            details_label.setStyleSheet("color: #666; font-size: 11px;")
            info_layout.addWidget(details_label)
            
        # Step description
        if self.step.description:
            desc_label = QLabel(self.step.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #666; font-size: 11px;")
            info_layout.addWidget(desc_label)
            
        layout.addLayout(info_layout)
        layout.addStretch()
        
        # Enable/disable checkbox
        self.enable_btn = QToolButton()
        self.enable_btn.setCheckable(True)
        self.enable_btn.setChecked(self.step.enabled)
        self.enable_btn.setText("✓" if self.step.enabled else "✗")
        self.enable_btn.toggled.connect(self._on_enable_toggled)
        layout.addWidget(self.enable_btn)
        
        # Edit button
        edit_btn = QToolButton()
        edit_btn.setText("✏️")
        edit_btn.setToolTip("편집")
        edit_btn.clicked.connect(lambda: self.editRequested.emit(self.step))
        layout.addWidget(edit_btn)
        
        # Delete button
        delete_btn = QToolButton()
        delete_btn.setText("🗑️")
        delete_btn.setToolTip("삭제")
        delete_btn.clicked.connect(lambda: self.deleteRequested.emit(self.step.step_id))
        layout.addWidget(delete_btn)
        
        self.setLayout(layout)
        self._update_style()
        
    def _get_step_icon(self) -> str:
        """Get icon for step type"""
        icons = {
            StepType.MOUSE_CLICK: "🖱️",
            StepType.MOUSE_MOVE: "↗️",
            StepType.KEYBOARD_TYPE: "⌨️",
            StepType.KEYBOARD_HOTKEY: "⌘",
            StepType.WAIT_TIME: "⏱️",
            StepType.WAIT_IMAGE: "🖼️",
            StepType.IMAGE_SEARCH: "🔍",
            StepType.OCR_TEXT: "🔤",
            StepType.SCREENSHOT: "📷",
            StepType.IF_CONDITION: "❓",
            StepType.LOOP: "🔄"
        }
        return icons.get(self.step.step_type, "")
        
    def _get_step_details(self) -> str:
        """Get step details based on type"""
        details = []
        
        if self.step.step_type == StepType.WAIT_IMAGE:
            if hasattr(self.step, 'image_path') and self.step.image_path:
                import os
                filename = os.path.basename(self.step.image_path)
                details.append(f"이미지: {filename}")
            if hasattr(self.step, 'timeout'):
                details.append(f"대기시간: {self.step.timeout}초")
            if hasattr(self.step, 'confidence'):
                details.append(f"정확도: {int(self.step.confidence * 100)}%")
            if hasattr(self.step, 'region') and self.step.region:
                details.append("✓ 영역 지정됨")
                
        elif self.step.step_type == StepType.IMAGE_SEARCH:
            if hasattr(self.step, 'image_path') and self.step.image_path:
                import os
                filename = os.path.basename(self.step.image_path)
                details.append(f"이미지: {filename}")
            if hasattr(self.step, 'confidence'):
                details.append(f"정확도: {int(self.step.confidence * 100)}%")
            if hasattr(self.step, 'region') and self.step.region:
                details.append("✓ 영역 지정됨")
                
        elif self.step.step_type == StepType.MOUSE_CLICK:
            if hasattr(self.step, 'x') and hasattr(self.step, 'y'):
                details.append(f"위치: ({self.step.x}, {self.step.y})")
            if hasattr(self.step, 'clicks') and self.step.clicks > 1:
                details.append(f"클릭 수: {self.step.clicks}")
                
        elif self.step.step_type == StepType.KEYBOARD_TYPE:
            if hasattr(self.step, 'text') and self.step.text:
                text_preview = self.step.text[:30] + "..." if len(self.step.text) > 30 else self.step.text
                details.append(f"텍스트: {text_preview}")
                
        elif self.step.step_type == StepType.WAIT_TIME:
            if hasattr(self.step, 'seconds'):
                details.append(f"대기: {self.step.seconds}초")
                
        elif self.step.step_type == StepType.OCR_TEXT:
            if hasattr(self.step, 'excel_column') and self.step.excel_column:
                details.append(f"엑셀 열: {self.step.excel_column}")
            elif hasattr(self.step, 'search_text') and self.step.search_text:
                text_preview = self.step.search_text[:20] + "..." if len(self.step.search_text) > 20 else self.step.search_text
                details.append(f"텍스트: {text_preview}")
            if hasattr(self.step, 'exact_match') and self.step.exact_match:
                details.append("정확히 일치")
            if hasattr(self.step, 'region') and self.step.region:
                details.append("✓ 영역 지정됨")
                
        return " | ".join(details) if details else ""
        
    def _on_enable_toggled(self, checked: bool):
        """Handle enable/disable toggle"""
        self.step.enabled = checked
        self.enable_btn.setText("✓" if checked else "✗")
        self._update_style()
        
    def _update_style(self):
        """Update widget style based on state"""
        if self.step.enabled:
            self.setStyleSheet("""
                MacroStepWidget {
                    background-color: white;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                }
                MacroStepWidget:hover {
                    border-color: #999;
                }
            """)
        else:
            self.setStyleSheet("""
                MacroStepWidget {
                    background-color: #f5f5f5;
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    opacity: 0.7;
                }
            """)
            
    def mousePressEvent(self, event):
        """Handle mouse press for dragging"""
        if event.button() == Qt.LeftButton:
            # Check if clicking on handle
            handle_rect = self.handle.geometry()
            if handle_rect.contains(event.pos()):
                self.drag_start_position = event.pos()
                
    def mouseMoveEvent(self, event):
        """Handle mouse move for dragging"""
        if not (event.buttons() & Qt.LeftButton):
            return
            
        if not hasattr(self, 'drag_start_position'):
            return
            
        if (event.pos() - self.drag_start_position).manhattanLength() < 10:
            return
            
        # Start drag
        drag = QDrag(self)
        mime_data = QMimeData()
        
        # Store step data
        byte_array = QByteArray()
        stream = QDataStream(byte_array, QIODevice.WriteOnly)
        stream.writeQString(self.step.step_id)
        stream.writeInt(self.index)
        
        mime_data.setData("application/x-macrostep", byte_array)
        mime_data.setText(self.step.name or self.step.step_type.value)
        drag.setMimeData(mime_data)
        
        drag.exec_(Qt.MoveAction)

class MacroFlowWidget(QWidget):
    """Widget displaying the macro flow with drag/drop support"""
    
    stepAdded = pyqtSignal(MacroStep, int)  # step, index
    stepMoved = pyqtSignal(str, int)  # step_id, new_index
    stepDeleted = pyqtSignal(str)  # step_id
    stepEdited = pyqtSignal(MacroStep)
    
    def __init__(self):
        super().__init__()
        self.macro = Macro()
        self.step_widgets: Dict[str, MacroStepWidget] = {}
        self.setAcceptDrops(True)
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        self.layout = QVBoxLayout()
        self.layout.setSpacing(5)
        
        # Empty state label
        self.empty_label = QLabel("단계를 여기로 드래그하세요")
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("""
            QLabel {
                color: #999;
                font-size: 14px;
                padding: 50px;
                border: 2px dashed #ddd;
                border-radius: 5px;
            }
        """)
        self.layout.addWidget(self.empty_label)
        
        self.layout.addStretch()
        self.setLayout(self.layout)
        
    def set_macro(self, macro: Macro):
        """Set the macro to display"""
        self.macro = macro
        self._rebuild_ui()
        
    def _rebuild_ui(self):
        """Rebuild UI from macro"""
        # Clear existing widgets
        for widget in self.step_widgets.values():
            widget.deleteLater()
        self.step_widgets.clear()
        
        # Remove all items from layout
        while self.layout.count() > 0:
            item = self.layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        # Show empty label or steps
        if not self.macro.steps:
            self.layout.addWidget(self.empty_label)
        else:
            self.empty_label.hide()
            for i, step in enumerate(self.macro.steps):
                widget = self._create_step_widget(step, i)
                self.layout.insertWidget(i, widget)
                self.step_widgets[step.step_id] = widget
                
        self.layout.addStretch()
        
    def _create_step_widget(self, step: MacroStep, index: int) -> MacroStepWidget:
        """Create widget for a step"""
        widget = MacroStepWidget(step, index)
        widget.editRequested.connect(self._on_step_edit)
        widget.deleteRequested.connect(self._on_step_delete)
        widget.moveRequested.connect(self.stepMoved.emit)
        return widget
        
    def _on_step_edit(self, step_id: str):
        """Handle step edit request"""
        step = self.macro.get_step(step_id)
        if not step:
            return
            
        # Open appropriate dialog based on step type
        if step.step_type == StepType.WAIT_IMAGE:
            from dialogs.image_step_dialog import WaitImageStepDialog
            dialog = WaitImageStepDialog(step, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                # Update step with new data
                step_data = dialog.get_step_data()
                step.name = step_data['name']
                step.image_path = step_data['image_path']
                step.timeout = step_data['timeout']
                step.confidence = step_data['confidence']
                step.region = step_data['region']
                self._rebuild_ui()
                self.stepEdited.emit(step_id)
                
        elif step.step_type == StepType.IMAGE_SEARCH:
            from dialogs.image_step_dialog import ImageSearchStepDialog
            dialog = ImageSearchStepDialog(step, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                # Update step with new data
                step_data = dialog.get_step_data()
                step.name = step_data['name']
                step.image_path = step_data['image_path']
                step.confidence = step_data['confidence']
                step.region = step_data['region']
                self._rebuild_ui()
                self.stepEdited.emit(step_id)
                
        elif step.step_type == StepType.OCR_TEXT:
            from dialogs.text_search_step_dialog import TextSearchStepDialog
            # Get Excel columns from parent widget
            excel_columns = []
            parent = self.parent()
            while parent:
                if hasattr(parent, 'excel_widget'):
                    excel_manager = parent.excel_widget.get_excel_manager()
                    if excel_manager and excel_manager._current_data is not None:
                        excel_columns = list(excel_manager._current_data.columns)
                    break
                parent = parent.parent()
                
            dialog = TextSearchStepDialog(step, excel_columns, parent=self)
            if dialog.exec_() == QDialog.Accepted:
                # Update step with new data
                step_data = dialog.get_step_data()
                step.name = step_data['name']
                step.search_text = step_data['search_text']
                step.excel_column = step_data['excel_column']
                step.region = step_data['region']
                step.exact_match = step_data['exact_match']
                step.confidence = step_data['confidence']
                step.click_after_find = step_data['click_after_find']
                step.click_offset = step_data['click_offset']
                self._rebuild_ui()
                self.stepEdited.emit(step_id)
        else:
            # For other step types, emit the signal as before
            self.stepEdited.emit(step_id)
        
    def _on_step_delete(self, step_id: str):
        """Handle step deletion"""
        reply = QMessageBox.question(
            self, "단계 삭제", 
            "이 단계를 삭제하시겠습니까?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.macro.remove_step(step_id)
            self._rebuild_ui()
            self.stepDeleted.emit(step_id)
            
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter"""
        if event.mimeData().hasFormat("application/x-steptype") or \
           event.mimeData().hasFormat("application/x-macrostep"):
            event.acceptProposedAction()
            
    def dragMoveEvent(self, event):
        """Handle drag move"""
        if event.mimeData().hasFormat("application/x-steptype") or \
           event.mimeData().hasFormat("application/x-macrostep"):
            event.acceptProposedAction()
            
    def dropEvent(self, event: QDropEvent):
        """Handle drop"""
        # Calculate drop index
        drop_index = self._get_drop_index(event.pos())
        
        if event.mimeData().hasFormat("application/x-steptype"):
            # New step from palette
            byte_array = event.mimeData().data("application/x-steptype")
            stream = QDataStream(byte_array, QIODevice.ReadOnly)
            step_type_str = stream.readQString()
            
            step_type = StepType(step_type_str)
            new_step = StepFactory.create_step(step_type)
            
            # Set default name
            step_names = {
                StepType.MOUSE_CLICK: "마우스 클릭",
                StepType.MOUSE_MOVE: "마우스 이동",
                StepType.KEYBOARD_TYPE: "텍스트 입력",
                StepType.KEYBOARD_HOTKEY: "단축키",
                StepType.WAIT_TIME: "대기",
                StepType.WAIT_IMAGE: "이미지 대기",
                StepType.IMAGE_SEARCH: "이미지 검색",
                StepType.OCR_TEXT: "텍스트 검색",
                StepType.SCREENSHOT: "화면 캡처",
                StepType.IF_CONDITION: "조건문",
                StepType.LOOP: "반복문"
            }
            new_step.name = step_names.get(step_type, step_type.value)
            
            self.macro.add_step(new_step, drop_index)
            self._rebuild_ui()
            self.stepAdded.emit(new_step, drop_index)
            
        elif event.mimeData().hasFormat("application/x-macrostep"):
            # Moving existing step
            byte_array = event.mimeData().data("application/x-macrostep")
            stream = QDataStream(byte_array, QIODevice.ReadOnly)
            step_id = stream.readQString()
            old_index = stream.readInt()
            
            # Adjust drop index if moving down
            if old_index < drop_index:
                drop_index -= 1
                
            self.macro.move_step(step_id, drop_index)
            self._rebuild_ui()
            self.stepMoved.emit(step_id, drop_index)
            
        event.acceptProposedAction()
        
    def _get_drop_index(self, pos) -> int:
        """Calculate index where item should be dropped"""
        if not self.macro.steps:
            return 0
            
        # Find the widget under the cursor
        for i, step in enumerate(self.macro.steps):
            widget = self.step_widgets.get(step.step_id)
            if widget:
                widget_rect = widget.geometry()
                if pos.y() < widget_rect.center().y():
                    return i
                    
        return len(self.macro.steps)

class MacroEditorWidget(QWidget):
    """Complete macro editor with palette and flow"""
    
    macroChanged = pyqtSignal(Macro)
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QHBoxLayout()
        
        # Create splitter
        splitter = QSplitter(Qt.Horizontal)
        
        # Step palette
        palette_group = QGroupBox("단계 팔레트")
        palette_layout = QVBoxLayout()
        
        palette_label = QLabel("단계를 드래그하여 추가하세요")
        palette_label.setWordWrap(True)
        palette_layout.addWidget(palette_label)
        
        self.palette = StepPalette()
        palette_layout.addWidget(self.palette)
        
        palette_group.setLayout(palette_layout)
        splitter.addWidget(palette_group)
        
        # Macro flow
        flow_group = QGroupBox("매크로 흐름")
        flow_layout = QVBoxLayout()
        
        # Scroll area for flow
        scroll = QScrollArea()
        self.flow_widget = MacroFlowWidget()
        self.flow_widget.stepAdded.connect(self._on_change)
        self.flow_widget.stepMoved.connect(self._on_change)
        self.flow_widget.stepDeleted.connect(self._on_change)
        self.flow_widget.stepEdited.connect(self._on_step_edit)
        
        scroll.setWidget(self.flow_widget)
        scroll.setWidgetResizable(True)
        flow_layout.addWidget(scroll)
        
        flow_group.setLayout(flow_layout)
        splitter.addWidget(flow_group)
        
        # Set splitter sizes (20% palette, 80% flow)
        splitter.setSizes([200, 800])
        
        layout.addWidget(splitter)
        self.setLayout(layout)
        
    def set_macro(self, macro: Macro):
        """Set the macro to edit"""
        self.flow_widget.set_macro(macro)
        
    def get_macro(self) -> Macro:
        """Get the current macro"""
        return self.flow_widget.macro
        
    def _on_change(self):
        """Handle macro change"""
        self.macroChanged.emit(self.flow_widget.macro)
        
    def _on_step_edit(self, step: MacroStep):
        """Handle step edit request"""
        # This will be connected to step configuration dialog
        pass