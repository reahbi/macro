#!/usr/bin/env python3
"""Test script for compact mode functionality"""

import sys
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow
from src.config.settings import Settings

def main():
    app = QApplication(sys.argv)
    
    # Initialize settings
    settings = Settings()
    
    # Create and show main window
    window = MainWindow(settings)
    window.show()
    
    # Print instructions
    print("Compact Mode Test")
    print("-" * 40)
    print("1. Check View menu - 'Compact Mode' option should be visible")
    print("2. Use Ctrl+Shift+C to toggle compact mode")
    print("3. When enabled:")
    print("   - UI elements should be more condensed")
    print("   - Font size should be smaller (11px)")
    print("   - Padding and margins should be reduced")
    print("   - Tab bar should be more compact")
    print("   - Status bar should be smaller")
    print("4. Setting should persist after restart")
    print("-" * 40)
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()