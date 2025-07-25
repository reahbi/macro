#!/usr/bin/env python3
"""Test script to compare ROI selection between Image Search and Text Search dialogs"""

import sys
import os

# Add the macro directory to Python path
macro_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(macro_dir, 'src')
sys.path.insert(0, macro_dir)
sys.path.insert(0, src_dir)

from PyQt5.QtWidgets import QApplication, QPushButton, QVBoxLayout, QWidget, QTextEdit
from PyQt5.QtCore import Qt
import traceback

# Import both dialogs
from ui.dialogs.image_step_dialog import ImageSearchStepDialog
from ui.dialogs.text_search_step_dialog import TextSearchStepDialog
from core.macro_types import ImageSearchStep, TextSearchStep

class TestWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ROI Selector Test")
        self.setGeometry(100, 100, 600, 500)
        
        layout = QVBoxLayout()
        
        # Buttons to test each dialog
        self.image_btn = QPushButton("Test Image Search ROI")
        self.image_btn.clicked.connect(self.test_image_search_roi)
        layout.addWidget(self.image_btn)
        
        self.text_btn = QPushButton("Test Text Search ROI")
        self.text_btn.clicked.connect(self.test_text_search_roi)
        layout.addWidget(self.text_btn)
        
        # Log output
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        
        self.setLayout(layout)
        
        # Store dialogs to prevent garbage collection
        self.image_dialog = None
        self.text_dialog = None
    
    def log(self, message):
        """Add message to log output"""
        self.log_output.append(message)
        print(message)  # Also print to console
        QApplication.processEvents()
    
    def test_image_search_roi(self):
        """Test ROI selection in Image Search dialog"""
        self.log("\n=== Testing Image Search ROI ===")
        
        try:
            # Create step and dialog
            step = ImageSearchStep()
            self.image_dialog = ImageSearchStepDialog(step, parent=self)
            
            # Check if _select_region method exists
            if hasattr(self.image_dialog, '_select_region'):
                self.log("✓ ImageSearchStepDialog has _select_region method")
                
                # Check method signature
                import inspect
                sig = inspect.signature(self.image_dialog._select_region)
                self.log(f"  Method signature: {sig}")
                
                # Try to call it directly
                self.log("  Attempting to call _select_region()...")
                try:
                    self.image_dialog._select_region()
                    self.log("  ✓ _select_region() called successfully")
                except Exception as e:
                    self.log(f"  ✗ Error calling _select_region(): {e}")
                    self.log(f"    {traceback.format_exc()}")
            else:
                self.log("✗ ImageSearchStepDialog does NOT have _select_region method")
                
            # Check for region selector button
            if hasattr(self.image_dialog, 'region_selector_btn'):
                self.log("✓ ImageSearchStepDialog has region_selector_btn")
                
                # Check if it's connected
                try:
                    # Get the signal
                    clicked_signal = self.image_dialog.region_selector_btn.clicked
                    self.log(f"  Button has {clicked_signal.receivers(Qt.UniqueConnection)} connected slots")
                except Exception as e:
                    self.log(f"  Error checking connections: {e}")
            else:
                self.log("✗ ImageSearchStepDialog does NOT have region_selector_btn")
                
            # List all attributes related to region
            self.log("\nRegion-related attributes:")
            for attr in dir(self.image_dialog):
                if 'region' in attr.lower() or 'roi' in attr.lower():
                    self.log(f"  - {attr}")
                    
        except Exception as e:
            self.log(f"✗ Error testing Image Search ROI: {e}")
            self.log(traceback.format_exc())
    
    def test_text_search_roi(self):
        """Test ROI selection in Text Search dialog"""
        self.log("\n=== Testing Text Search ROI ===")
        
        try:
            # Create step and dialog
            step = TextSearchStep()
            self.text_dialog = TextSearchStepDialog(step, parent=self)
            
            # Check if _select_region method exists
            if hasattr(self.text_dialog, '_select_region'):
                self.log("✓ TextSearchStepDialog has _select_region method")
                
                # Check method signature
                import inspect
                sig = inspect.signature(self.text_dialog._select_region)
                self.log(f"  Method signature: {sig}")
                
                # Try to call it directly
                self.log("  Attempting to call _select_region()...")
                try:
                    self.text_dialog._select_region()
                    self.log("  ✓ _select_region() called successfully")
                except Exception as e:
                    self.log(f"  ✗ Error calling _select_region(): {e}")
                    self.log(f"    {traceback.format_exc()}")
            else:
                self.log("✗ TextSearchStepDialog does NOT have _select_region method")
                
            # Check for region selector button
            if hasattr(self.text_dialog, 'region_selector_btn'):
                self.log("✓ TextSearchStepDialog has region_selector_btn")
                
                # Check if it's connected
                try:
                    # Get the signal
                    clicked_signal = self.text_dialog.region_selector_btn.clicked
                    self.log(f"  Button has {clicked_signal.receivers(Qt.UniqueConnection)} connected slots")
                    
                    # Check what it's connected to
                    # Note: This is a hack and may not work in all PyQt versions
                    if hasattr(clicked_signal, '_slots'):
                        for slot in clicked_signal._slots:
                            self.log(f"    Connected to: {slot}")
                except Exception as e:
                    self.log(f"  Error checking connections: {e}")
            else:
                self.log("✗ TextSearchStepDialog does NOT have region_selector_btn")
                
            # List all attributes related to region
            self.log("\nRegion-related attributes:")
            for attr in dir(self.text_dialog):
                if 'region' in attr.lower() or 'roi' in attr.lower() or 'select' in attr.lower():
                    self.log(f"  - {attr}")
                    
            # Check search_scope_combo
            if hasattr(self.text_dialog, 'search_scope_combo'):
                self.log("\n✓ TextSearchStepDialog has search_scope_combo")
                self.log(f"  Current index: {self.text_dialog.search_scope_combo.currentIndex()}")
                self.log(f"  Current text: {self.text_dialog.search_scope_combo.currentText()}")
                
                # Check if combo box change is connected
                try:
                    changed_signal = self.text_dialog.search_scope_combo.currentIndexChanged
                    self.log(f"  ComboBox has {changed_signal.receivers(Qt.UniqueConnection)} connected slots")
                except Exception as e:
                    self.log(f"  Error checking combo connections: {e}")
                    
        except Exception as e:
            self.log(f"✗ Error testing Text Search ROI: {e}")
            self.log(traceback.format_exc())
        
    def compare_roi_mechanisms(self):
        """Compare ROI selection mechanisms between the two dialogs"""
        self.log("\n=== Comparing ROI Mechanisms ===")
        
        # First test both individually
        self.test_image_search_roi()
        self.test_text_search_roi()
        
        self.log("\n=== Summary ===")
        
        # Compare key differences
        if self.image_dialog and self.text_dialog:
            # Check for common ROI selection methods
            image_methods = set(dir(self.image_dialog))
            text_methods = set(dir(self.text_dialog))
            
            # Find methods unique to each
            image_only = image_methods - text_methods
            text_only = text_methods - image_methods
            
            roi_related_image_only = [m for m in image_only if 'region' in m.lower() or 'roi' in m.lower()]
            roi_related_text_only = [m for m in text_only if 'region' in m.lower() or 'roi' in m.lower()]
            
            if roi_related_image_only:
                self.log("\nMethods in ImageSearchStepDialog but NOT in TextSearchStepDialog:")
                for method in roi_related_image_only:
                    self.log(f"  - {method}")
                    
            if roi_related_text_only:
                self.log("\nMethods in TextSearchStepDialog but NOT in ImageSearchStepDialog:")
                for method in roi_related_text_only:
                    self.log(f"  - {method}")

def main():
    app = QApplication(sys.argv)
    window = TestWindow()
    window.show()
    
    # Automatically run comparison after window is shown
    QApplication.processEvents()
    window.compare_roi_mechanisms()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()