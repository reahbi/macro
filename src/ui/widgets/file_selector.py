"""
Excel file selection widget with drag-drop support
"""

import os
from pathlib import Path
from typing import Optional
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QListWidget, QListWidgetItem, QFileDialog,
    QGroupBox, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QMimeData
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QIcon

class FileDropArea(QLabel):
    """Drag and drop area for Excel files"""
    
    fileDropped = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 20px;
                background-color: #f5f5f5;
                min-height: 100px;
            }
            QLabel:hover {
                border-color: #555;
                background-color: #e8e8e8;
            }
        """)
        self.setText("엑셀 파일을 여기에 드래그하거나\n아래 버튼을 클릭하세요")
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter event"""
        if event.mimeData().hasUrls():
            # Check if any file is Excel
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    path = url.toLocalFile()
                    if path.lower().endswith(('.xlsx', '.xls', '.xlsm')):
                        event.acceptProposedAction()
                        self.setStyleSheet("""
                            QLabel {
                                border: 2px solid #4CAF50;
                                border-radius: 5px;
                                padding: 20px;
                                background-color: #e8f5e9;
                                min-height: 100px;
                            }
                        """)
                        return
        event.ignore()
        
    def dragLeaveEvent(self, event):
        """Handle drag leave event"""
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 20px;
                background-color: #f5f5f5;
                min-height: 100px;
            }
        """)
        
    def dropEvent(self, event: QDropEvent):
        """Handle drop event"""
        for url in event.mimeData().urls():
            if url.isLocalFile():
                path = url.toLocalFile()
                if path.lower().endswith(('.xlsx', '.xls', '.xlsm')):
                    self.fileDropped.emit(path)
                    event.acceptProposedAction()
                    self.dragLeaveEvent(None)
                    return

class RecentFilesList(QListWidget):
    """List of recently opened Excel files"""
    
    fileSelected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.setMaximumHeight(150)
        self.itemDoubleClicked.connect(self._on_item_double_clicked)
        
    def add_recent_file(self, file_path: str):
        """Add file to recent files list"""
        # Check if already exists
        for i in range(self.count()):
            if self.item(i).data(Qt.UserRole) == file_path:
                # Move to top
                item = self.takeItem(i)
                self.insertItem(0, item)
                return
        
        # Add new item
        file_name = os.path.basename(file_path)
        item = QListWidgetItem(file_name)
        item.setData(Qt.UserRole, file_path)
        item.setToolTip(file_path)
        self.insertItem(0, item)
        
        # Keep only 10 recent files
        while self.count() > 10:
            self.takeItem(self.count() - 1)
            
    def _on_item_double_clicked(self, item: QListWidgetItem):
        """Handle double click on item"""
        file_path = item.data(Qt.UserRole)
        if file_path and os.path.exists(file_path):
            self.fileSelected.emit(file_path)

class FileSelectorWidget(QWidget):
    """Excel file selection widget"""
    
    fileSelected = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.current_file: Optional[str] = None
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Current file info
        self.file_info_label = QLabel("선택된 파일: 없음")
        self.file_info_label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(self.file_info_label)
        
        # Drop area
        self.drop_area = FileDropArea()
        self.drop_area.fileDropped.connect(self._on_file_selected)
        layout.addWidget(self.drop_area)
        
        # Browse button
        browse_button = QPushButton("파일 찾아보기...")
        browse_button.clicked.connect(self._browse_file)
        layout.addWidget(browse_button)
        
        # Recent files
        recent_group = QGroupBox("최근 파일")
        recent_layout = QVBoxLayout()
        self.recent_files = RecentFilesList()
        self.recent_files.fileSelected.connect(self._on_file_selected)
        recent_layout.addWidget(self.recent_files)
        recent_group.setLayout(recent_layout)
        layout.addWidget(recent_group)
        
        layout.addStretch()
        self.setLayout(layout)
        
    def _browse_file(self):
        """Open file dialog to select Excel file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "엑셀 파일 선택",
            "",
            "Excel Files (*.xlsx *.xls *.xlsm);;All Files (*.*)"
        )
        
        if file_path:
            self._on_file_selected(file_path)
            
    def _on_file_selected(self, file_path: str):
        """Handle file selection"""
        if not os.path.exists(file_path):
            QMessageBox.warning(self, "파일 오류", f"파일을 찾을 수 없습니다:\n{file_path}")
            return
            
        self.current_file = file_path
        self.file_info_label.setText(f"선택된 파일: {os.path.basename(file_path)}")
        self.recent_files.add_recent_file(file_path)
        self.fileSelected.emit(file_path)
        
    def get_recent_files(self) -> list:
        """Get list of recent files"""
        files = []
        for i in range(self.recent_files.count()):
            item = self.recent_files.item(i)
            files.append(item.data(Qt.UserRole))
        return files
        
    def set_recent_files(self, files: list):
        """Set recent files list"""
        self.recent_files.clear()
        for file_path in files:
            if os.path.exists(file_path):
                self.recent_files.add_recent_file(file_path)