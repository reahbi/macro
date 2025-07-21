#!/usr/bin/env python
"""Simple test to check if basic components work"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    print("Testing imports...")
    
    # Test settings import
    from config.settings import Settings
    settings = Settings()
    print("[OK] Settings loaded successfully")
    
    # Test preparation widget
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    
    from ui.widgets.preparation_widget import PreparationWidget
    prep = PreparationWidget(countdown_seconds=5)
    print("[OK] PreparationWidget created successfully")
    
    # Test floating widget
    from ui.widgets.floating_status_widget import FloatingStatusWidget
    floating = FloatingStatusWidget()
    print("[OK] FloatingStatusWidget created successfully")
    
    # Test system tray
    from ui.system_tray_manager import SystemTrayManager
    tray = SystemTrayManager(settings)
    if tray.tray_icon:
        print("[OK] SystemTrayManager created successfully")
    else:
        print("[WARN] SystemTrayManager created but tray not available")
    
    # Test progress calculator
    from automation.progress_calculator import ProgressCalculator, ExecutionMode
    calc = ProgressCalculator(ExecutionMode.EXCEL)
    print("[OK] ProgressCalculator created successfully")
    
    print("\nAll basic components working!")
    
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()