#!/usr/bin/env python3
"""Direct test of ROI selector signal emission"""

import sys
import os

# Add the macro directory to Python path
macro_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(macro_dir, 'src')
sys.path.insert(0, macro_dir)
sys.path.insert(0, src_dir)

from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtCore import Qt
from ui.widgets.roi_selector import ROISelectorOverlay

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROI Signal Test")
        self.setGeometry(100, 100, 400, 300)
        
        layout = QVBoxLayout()
        
        # Button to trigger ROI selection
        self.test_btn = QPushButton("Test ROI Selection")
        self.test_btn.clicked.connect(self.test_roi)
        layout.addWidget(self.test_btn)
        
        # Log output
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        layout.addWidget(self.log)
        
        self.setLayout(layout)
        
    def log_message(self, msg):
        """Add message to log"""
        self.log.append(msg)
        print(msg)
        
    def test_roi(self):
        """Test ROI selector"""
        self.log_message("\n=== Starting ROI Selection Test ===")
        
        try:
            # Create ROI selector
            self.log_message("Creating ROI selector...")
            self.roi_selector = ROISelectorOverlay(parent=None)
            self.log_message(f"ROI selector created: {self.roi_selector}")
            
            # Connect signal with detailed logging
            self.log_message("Connecting selectionComplete signal...")
            self.roi_selector.selectionComplete.connect(self.on_selection_complete)
            self.log_message("Signal connected")
            
            # Connect cancelled signal
            self.log_message("Connecting selectionCancelled signal...")
            self.roi_selector.selectionCancelled.connect(self.on_selection_cancelled)
            self.log_message("Signal connected")
            
            # Hide main window
            self.hide()
            self.log_message("Main window hidden")
            
            # Show ROI selector
            self.log_message("Calling start_selection()...")
            self.roi_selector.start_selection()
            self.log_message("start_selection() called")
            
            self.log_message("Showing ROI selector...")
            self.roi_selector.show()
            self.log_message("ROI selector shown")
            
        except Exception as e:
            self.log_message(f"ERROR: {e}")
            import traceback
            self.log_message(traceback.format_exc())
            self.show()
    
    def on_selection_complete(self, region):
        """Handle selection complete"""
        self.log_message(f"\n=== SIGNAL RECEIVED ===")
        self.log_message(f"Region: {region}")
        self.log_message(f"Type: {type(region)}")
        self.log_message(f"Length: {len(region) if hasattr(region, '__len__') else 'N/A'}")
        self.show()
        
    def on_selection_cancelled(self):
        """Handle selection cancelled"""
        self.log_message("\n=== Selection Cancelled ===")
        self.show()

def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()