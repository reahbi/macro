"""
Main application window
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QMenuBar, QMenu, QAction, QStatusBar, QLabel,
    QMessageBox, QTabWidget, QFileDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from config.settings import Settings
from logger.app_logger import get_logger
from core.macro_storage import MacroStorage, MacroFormat
from core.macro_types import Macro
import os
from typing import List, Optional

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.logger = get_logger(__name__)
        
        # Macro storage
        self.macro_storage = MacroStorage()
        self.current_macro_path: Optional[str] = None
        self.recent_macros: List[str] = self.settings.get("macro.recent_files", [])
        
        self.init_ui()
        self.load_window_state()
        
        # Apply compact mode if enabled
        if self.settings.get("ui.compact_mode", False):
            self.apply_compact_mode(True)
        
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("Excel Macro Automation")
        
        # Set window size from settings
        window_size = self.settings.get("ui.window_size", [1280, 720])
        self.resize(*window_size)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Add Excel widget
        from ui.widgets.excel_widget import ExcelWidget
        self.excel_widget = ExcelWidget()
        self.tab_widget.addTab(self.excel_widget, "Excel")
        
        # Add Macro Editor widget
        from ui.widgets.macro_editor import MacroEditorWidget
        self.macro_editor = MacroEditorWidget()
        self.tab_widget.addTab(self.macro_editor, "Editor")
        
        # Add Execution widget
        from ui.widgets.execution_widget import ExecutionWidget
        self.execution_widget = ExecutionWidget(self.settings)
        self.tab_widget.addTab(self.execution_widget, "Run")
        
        # Connect Excel and Macro widgets to Execution
        self.excel_widget.dataReady.connect(self._on_excel_data_ready)
        self.macro_editor.macroChanged.connect(self._on_macro_changed)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.create_status_bar()
        
    def create_menu_bar(self):
        """Create application menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_action = QAction("New Project", self)
        new_action.setShortcut("Ctrl+N")
        file_menu.addAction(new_action)
        
        open_action = QAction("Open Project", self)
        open_action.setShortcut("Ctrl+O")
        file_menu.addAction(open_action)
        
        save_action = QAction("Save Project", self)
        save_action.setShortcut("Ctrl+Alt+S")
        file_menu.addAction(save_action)
        
        file_menu.addSeparator()
        
        # Macro menu items
        save_macro_action = QAction("Save Macro", self)
        save_macro_action.setShortcut("Ctrl+S")
        save_macro_action.triggered.connect(self.save_macro)
        file_menu.addAction(save_macro_action)
        
        load_macro_action = QAction("Load Macro", self)
        load_macro_action.setShortcut("Ctrl+O")
        load_macro_action.triggered.connect(self.load_macro)
        file_menu.addAction(load_macro_action)
        
        export_macro_action = QAction("Export Macro", self)
        export_macro_action.setShortcut("Ctrl+E")
        export_macro_action.triggered.connect(self.export_macro)
        file_menu.addAction(export_macro_action)
        
        file_menu.addSeparator()
        
        # Recent macros submenu
        self.recent_macros_menu = QMenu("Recent Macros", self)
        file_menu.addMenu(self.recent_macros_menu)
        self.update_recent_macros_menu()
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        settings_action = QAction("Settings", self)
        settings_action.setShortcut("Ctrl+,")
        edit_menu.addAction(settings_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        theme_action = QAction("Toggle Theme", self)
        view_menu.addAction(theme_action)
        
        # Add compact mode toggle
        self.compact_mode_action = QAction("Compact Mode", self)
        self.compact_mode_action.setCheckable(True)
        self.compact_mode_action.setChecked(self.settings.get("ui.compact_mode", False))
        self.compact_mode_action.setShortcut("Ctrl+Shift+C")
        self.compact_mode_action.setStatusTip("Toggle compact mode to reduce UI spacing (Ctrl+Shift+C)")
        self.compact_mode_action.triggered.connect(self.toggle_compact_mode)
        view_menu.addAction(self.compact_mode_action)
        
        view_menu.addSeparator()
        
        log_viewer_action = QAction("Execution Logs", self)
        log_viewer_action.setShortcut("Ctrl+L")
        log_viewer_action.triggered.connect(self.show_log_viewer)
        view_menu.addAction(log_viewer_action)
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
    def create_status_bar(self):
        """Create application status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # Add permanent widgets
        self.status_label = QLabel("Ready")
        self.status_bar.addPermanentWidget(self.status_label)
        
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Excel Macro Automation",
            "Excel-based Task Automation Macro\n\n"
            "Version: 1.0.0\n"
            "Automate repetitive tasks using Excel data"
        )
        
    def show_log_viewer(self):
        """Show log viewer dialog"""
        from ui.dialogs.log_viewer_dialog import LogViewerDialog
        dialog = LogViewerDialog(parent=self)
        dialog.show()  # Non-modal
        
    def closeEvent(self, event):
        """Handle window close event"""
        if self.settings.get("ui.confirm_exit", True):
            reply = QMessageBox.question(
                self,
                "Confirm Exit",
                "Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self.save_window_state()
                event.accept()
            else:
                event.ignore()
        else:
            self.save_window_state()
            event.accept()
            
    def save_window_state(self):
        """Save window size and position"""
        self.settings.set("ui.window_size", [self.width(), self.height()])
        self.settings.save()
        
    def load_window_state(self):
        """Load window size and position"""
        # Window state loading is handled in init_ui
        pass
        
    def _on_excel_data_ready(self, excel_data):
        """Handle Excel data ready"""
        excel_manager = self.excel_widget.get_excel_manager()
        macro = self.macro_editor.get_macro()
        self.execution_widget.set_macro_and_excel(macro, excel_manager)
        
    def _on_macro_changed(self, macro):
        """Handle macro change"""
        excel_manager = self.excel_widget.get_excel_manager()
        if excel_manager._current_data:
            self.execution_widget.set_macro_and_excel(macro, excel_manager)
            
    def save_macro(self):
        """Save current macro to file"""
        try:
            macro = self.macro_editor.get_macro()
            if not macro or not macro.steps:
                QMessageBox.warning(self, "Warning", "No macro to save.")
                return
                
            # Get save path
            if self.current_macro_path:
                # Use current path
                file_path = self.current_macro_path
            else:
                # Show save dialog
                file_path, selected_filter = QFileDialog.getSaveFileName(
                    self,
                    "Save Macro",
                    os.path.expanduser("~/"),
                    "JSON files (*.json);;Encrypted files (*.emf);;All files (*.*)"
                )
                
                if not file_path:
                    return
                    
            # Determine format based on extension
            if file_path.endswith('.emf'):
                format_type = MacroFormat.ENCRYPTED
            else:
                format_type = MacroFormat.JSON
                if not file_path.endswith('.json'):
                    file_path += '.json'
                    
            # Save macro
            success = self.macro_storage.save_macro(macro, file_path, format_type)
            
            if success:
                self.current_macro_path = file_path
                self.add_to_recent_macros(file_path)
                self.update_window_title()
                self.status_label.setText(f"Macro saved to {os.path.basename(file_path)}")
                QMessageBox.information(self, "Success", "Macro saved successfully.")
            else:
                QMessageBox.critical(self, "Error", "Failed to save macro.")
                
        except Exception as e:
            self.logger.error(f"Error saving macro: {e}")
            QMessageBox.critical(self, "Error", f"Failed to save macro: {str(e)}")
            
    def load_macro(self):
        """Load macro from file"""
        try:
            # Show open dialog
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Load Macro",
                os.path.expanduser("~/"),
                "Macro files (*.json *.emf);;JSON files (*.json);;Encrypted files (*.emf);;All files (*.*)"
            )
            
            if not file_path:
                return
                
            # Load macro
            macro = self.macro_storage.load_macro(file_path)
            
            if macro:
                self.macro_editor.set_macro(macro)
                self.current_macro_path = file_path
                self.add_to_recent_macros(file_path)
                self.update_window_title()
                self.status_label.setText(f"Macro loaded from {os.path.basename(file_path)}")
                QMessageBox.information(self, "Success", "Macro loaded successfully.")
            else:
                QMessageBox.critical(self, "Error", "Failed to load macro.")
                
        except Exception as e:
            self.logger.error(f"Error loading macro: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load macro: {str(e)}")
            
    def export_macro(self):
        """Export selected macro steps"""
        try:
            # Get selected steps from macro editor
            selected_steps = self.macro_editor.get_selected_steps()
            
            if not selected_steps:
                QMessageBox.warning(self, "Warning", "No steps selected for export.")
                return
                
            # Create partial macro
            macro = self.macro_editor.get_macro()
            partial_macro = Macro(
                name=f"{macro.name}_partial",
                description=f"Partial export of {macro.name}",
                steps=selected_steps,
                variables=macro.variables  # Include all variables for now
            )
            
            # Show save dialog
            file_path, selected_filter = QFileDialog.getSaveFileName(
                self,
                "Export Macro Steps",
                os.path.expanduser("~/"),
                "JSON files (*.json);;Encrypted files (*.emf);;All files (*.*)"
            )
            
            if not file_path:
                return
                
            # Determine format
            if file_path.endswith('.emf'):
                format_type = MacroFormat.ENCRYPTED
            else:
                format_type = MacroFormat.JSON
                if not file_path.endswith('.json'):
                    file_path += '.json'
                    
            # Save partial macro
            success = self.macro_storage.save_macro(partial_macro, file_path, format_type)
            
            if success:
                self.status_label.setText(f"Exported {len(selected_steps)} steps to {os.path.basename(file_path)}")
                QMessageBox.information(self, "Success", f"Exported {len(selected_steps)} steps successfully.")
            else:
                QMessageBox.critical(self, "Error", "Failed to export macro steps.")
                
        except Exception as e:
            self.logger.error(f"Error exporting macro: {e}")
            QMessageBox.critical(self, "Error", f"Failed to export macro: {str(e)}")
            
    def add_to_recent_macros(self, file_path: str):
        """Add file to recent macros list"""
        # Remove if already exists
        if file_path in self.recent_macros:
            self.recent_macros.remove(file_path)
            
        # Add to front
        self.recent_macros.insert(0, file_path)
        
        # Keep only last 5
        self.recent_macros = self.recent_macros[:5]
        
        # Save to settings
        self.settings.set("macro.recent_files", self.recent_macros)
        self.settings.save()
        
        # Update menu
        self.update_recent_macros_menu()
        
    def update_recent_macros_menu(self):
        """Update recent macros menu"""
        self.recent_macros_menu.clear()
        
        if not self.recent_macros:
            action = QAction("(No recent macros)", self)
            action.setEnabled(False)
            self.recent_macros_menu.addAction(action)
            return
            
        for file_path in self.recent_macros:
            if os.path.exists(file_path):
                action = QAction(os.path.basename(file_path), self)
                action.setStatusTip(file_path)
                action.triggered.connect(lambda checked, path=file_path: self.load_recent_macro(path))
                self.recent_macros_menu.addAction(action)
                
    def load_recent_macro(self, file_path: str):
        """Load a recent macro"""
        try:
            macro = self.macro_storage.load_macro(file_path)
            
            if macro:
                self.macro_editor.set_macro(macro)
                self.current_macro_path = file_path
                self.update_window_title()
                self.status_label.setText(f"Macro loaded from {os.path.basename(file_path)}")
            else:
                QMessageBox.critical(self, "Error", f"Failed to load macro from {os.path.basename(file_path)}")
                self.recent_macros.remove(file_path)
                self.update_recent_macros_menu()
                
        except Exception as e:
            self.logger.error(f"Error loading recent macro: {e}")
            QMessageBox.critical(self, "Error", f"Failed to load macro: {str(e)}")
            
    def update_window_title(self):
        """Update window title with current macro file"""
        title = "Excel Macro Automation"
        if self.current_macro_path:
            title += f" - {os.path.basename(self.current_macro_path)}"
        self.setWindowTitle(title)
        
    def toggle_compact_mode(self):
        """Toggle compact mode for the UI"""
        is_compact = self.compact_mode_action.isChecked()
        self.settings.set("ui.compact_mode", is_compact)
        self.settings.save()
        
        # Apply compact mode styling
        self.apply_compact_mode(is_compact)
        self.status_label.setText(f"Compact mode {'enabled' if is_compact else 'disabled'}")
        
    def apply_compact_mode(self, is_compact: bool):
        """Apply compact mode styling to the application"""
        if is_compact:
            # Compact mode stylesheet
            compact_style = """
            /* General compact styling */
            QWidget {
                font-size: 11px;
            }
            
            /* Reduce padding in tabs */
            QTabBar::tab {
                padding: 3px 8px;
                min-height: 20px;
            }
            
            /* Compact buttons */
            QPushButton {
                padding: 3px 8px;
                min-height: 22px;
            }
            
            /* Compact list items */
            QListWidget::item {
                padding: 2px;
                min-height: 20px;
            }
            
            /* Compact table rows */
            QTableWidget::item {
                padding: 2px;
            }
            
            /* Compact menu items */
            QMenu::item {
                padding: 3px 20px 3px 10px;
            }
            
            /* Compact group boxes */
            QGroupBox {
                margin-top: 1ex;
                padding-top: 10px;
            }
            
            QGroupBox::title {
                top: -7px;
                left: 10px;
            }
            
            /* Compact status bar */
            QStatusBar {
                min-height: 18px;
                font-size: 10px;
            }
            
            /* Compact splitters */
            QSplitter::handle {
                background-color: #ddd;
                height: 3px;
            }
            
            /* Compact scroll bars */
            QScrollBar:vertical {
                width: 10px;
            }
            
            QScrollBar:horizontal {
                height: 10px;
            }
            
            /* Compact line edits */
            QLineEdit, QTextEdit, QPlainTextEdit {
                padding: 2px;
            }
            
            /* Compact spin boxes */
            QSpinBox, QDoubleSpinBox {
                padding: 2px;
                min-height: 20px;
            }
            
            /* Compact combo boxes */
            QComboBox {
                padding: 2px 5px;
                min-height: 20px;
            }
            
            /* Compact tool buttons */
            QToolButton {
                padding: 2px;
                min-height: 20px;
                min-width: 20px;
            }
            
            /* Compact dialogs */
            QDialog {
                font-size: 11px;
            }
            
            /* Compact labels */
            QLabel {
                margin: 1px;
            }
            
            /* Compact progress bars */
            QProgressBar {
                min-height: 14px;
                max-height: 14px;
                font-size: 10px;
            }
            
            /* Compact checkboxes and radio buttons */
            QCheckBox, QRadioButton {
                spacing: 3px;
            }
            
            /* Compact tree widget */
            QTreeWidget::item {
                padding: 1px;
                min-height: 18px;
            }
            """
            self.setStyleSheet(compact_style)
            
            # Apply specific compact settings to widgets
            self._apply_compact_to_widgets(True)
        else:
            # Reset to normal styling
            self.setStyleSheet("")
            self._apply_compact_to_widgets(False)
            
    def _apply_compact_to_widgets(self, is_compact: bool):
        """Apply compact mode settings to specific widgets"""
        # Set tab widget spacing
        if is_compact:
            self.tab_widget.setDocumentMode(True)
            self.centralWidget().layout().setContentsMargins(5, 5, 5, 5)
            self.centralWidget().layout().setSpacing(5)
        else:
            self.tab_widget.setDocumentMode(False)
            self.centralWidget().layout().setContentsMargins(9, 9, 9, 9)
            self.centralWidget().layout().setSpacing(6)
            
        # Apply to child widgets if they have compact mode support
        for i in range(self.tab_widget.count()):
            widget = self.tab_widget.widget(i)
            if hasattr(widget, 'set_compact_mode'):
                widget.set_compact_mode(is_compact)