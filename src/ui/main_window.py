"""
Main application window
"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QMenuBar, QMenu, QAction, QStatusBar, QLabel,
    QMessageBox, QTabWidget
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
from config.settings import Settings
from logger.app_logger import get_logger

class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.logger = get_logger(__name__)
        
        self.init_ui()
        self.load_window_state()
        
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
        save_action.setShortcut("Ctrl+S")
        file_menu.addAction(save_action)
        
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