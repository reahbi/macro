#!/usr/bin/env python3
"""
Test script for execution logging system
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pathlib import Path
from logger.execution_logger import ExecutionLogger
from ui.dialogs.log_viewer_dialog import LogViewerDialog
from ui.dialogs.error_report_dialog import ErrorReportDialog
from PyQt5.QtWidgets import QApplication
import time

def test_logging():
    """Test the logging system"""
    print("Testing execution logging system...")
    
    # Create logger
    logger = ExecutionLogger()
    
    # Start session
    log_file = logger.start_session("Test Macro", "test_data.xlsx")
    print(f"Created log file: {log_file}")
    
    # Simulate macro execution
    for row_idx in range(3):
        logger.log_row_start(row_idx, {"Name": f"User{row_idx}", "Email": f"user{row_idx}@test.com"})
        
        # Simulate steps
        for step_idx in range(2):
            step_name = f"Step {step_idx + 1}"
            
            # Simulate success/failure
            if row_idx == 1 and step_idx == 1:
                # Simulate failure
                logger.log_step_execution(
                    row_idx, step_idx, step_name, "click",
                    False, 150.5, "Image not found: button.png"
                )
            else:
                # Success
                logger.log_step_execution(
                    row_idx, step_idx, step_name, "type",
                    True, 50.3
                )
            
            time.sleep(0.1)  # Small delay
        
        # Log row complete
        if row_idx == 1:
            logger.log_row_complete(row_idx, False, 350.8, "Step 2 failed")
        else:
            logger.log_row_complete(row_idx, True, 200.6)
    
    # Log session end
    logger.log_session_end(3, 2, 1)
    
    # Flush and close
    logger.flush()
    logger.close()
    
    print("Logging test completed!")
    return log_file

def test_ui(log_file):
    """Test the UI components"""
    print("\nTesting UI components...")
    
    app = QApplication(sys.argv)
    
    # Test log viewer
    print("Opening log viewer...")
    viewer = LogViewerDialog(log_file)
    viewer.show()
    
    # Test error dialog
    print("Showing error dialog...")
    ErrorReportDialog.show_error(
        "Image not found",
        "Could not find button.png on screen",
        error_details="Failed at step 2 of macro execution\nRow index: 1",
        log_file=log_file,
        parent=viewer
    )
    
    app.exec_()

if __name__ == "__main__":
    # Test logging
    log_file = test_logging()
    
    # Test UI
    test_ui(log_file)