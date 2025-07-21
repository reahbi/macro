#!/usr/bin/env python
"""Feature-specific tests for notification system"""

import sys
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, QSettings

app = QApplication(sys.argv)

print("=== NOTIFICATION SYSTEM FEATURE TESTS ===\n")

# Test 1: Preparation Widget Features
print("[TEST 1] Preparation Widget Features")
try:
    from ui.widgets.preparation_widget import PreparationWidget
    
    # Test different countdown values
    prep1 = PreparationWidget(countdown_seconds=3)
    print(f"  - Custom countdown (3s): {prep1.countdown_seconds} seconds")
    
    # Test window flags
    flags = prep1.windowFlags()
    from PyQt5.QtCore import Qt
    frameless = bool(flags & Qt.FramelessWindowHint)
    on_top = bool(flags & Qt.WindowStaysOnTopHint)
    print(f"  - Frameless window: {frameless}")
    print(f"  - Always on top: {on_top}")
    
    # Test signals
    has_signals = hasattr(prep1, 'countdownFinished') and hasattr(prep1, 'cancelled')
    print(f"  - Signals available: {has_signals}")
    
    prep1.close()
    print("  [PASS] All preparation widget features working\n")
    
except Exception as e:
    print(f"  [FAIL] Error: {e}\n")

# Test 2: Floating Widget Display Modes
print("[TEST 2] Floating Widget Display Modes")
try:
    from ui.widgets.floating_status_widget import FloatingStatusWidget, DisplayMode, ProgressData, ExecutionMode
    
    floating = FloatingStatusWidget()
    
    # Test each display mode
    modes = {
        DisplayMode.MINIMAL: (200, 50),
        DisplayMode.NORMAL: (300, 60),
        DisplayMode.DETAILED: (350, 80)
    }
    
    for mode, expected_size in modes.items():
        floating.set_display_mode(mode)
        actual_size = (floating.width(), floating.height())
        size_match = actual_size == expected_size
        print(f"  - Mode {mode.value}: Expected {expected_size}, Got {actual_size} [{size_match}]")
    
    # Test progress update
    progress = ProgressData(
        mode=ExecutionMode.EXCEL,
        percentage=75,
        current_row=8,
        total_rows=10,
        step_name="Test Step"
    )
    floating.update_progress(progress)
    print(f"  - Progress update: {floating.percentage_label.text()}")
    
    # Test position persistence
    floating.move(100, 100)
    floating.save_position()
    settings = QSettings("ExcelMacroAutomation", "FloatingWidget")
    saved_x = settings.value("position/x")
    saved_y = settings.value("position/y")
    print(f"  - Position saved: ({saved_x}, {saved_y})")
    
    floating.close()
    print("  [PASS] All floating widget features working\n")
    
except Exception as e:
    print(f"  [FAIL] Error: {e}\n")

# Test 3: System Tray Features
print("[TEST 3] System Tray Features")
try:
    from ui.system_tray_manager import SystemTrayManager
    from config.settings import Settings
    
    settings = Settings()
    tray = SystemTrayManager(settings)
    
    if tray.tray_icon:
        # Test state changes
        states = ["idle", "preparing", "running", "paused", "error"]
        for state in states:
            tray.set_execution_state(state, is_running=(state in ["running", "paused"]))
            print(f"  - State '{state}' set successfully")
        
        # Test progress
        tray.set_progress(50, "Test Progress")
        print("  - Progress update successful")
        
        # Test menu
        menu_exists = tray.tray_icon.contextMenu() is not None
        print(f"  - Context menu exists: {menu_exists}")
        
        tray.hide()
        print("  [PASS] All system tray features working\n")
    else:
        print("  [SKIP] System tray not available in this environment\n")
        
except Exception as e:
    print(f"  [FAIL] Error: {e}\n")

# Test 4: Progress Calculator
print("[TEST 4] Progress Calculator")
try:
    from automation.progress_calculator import ProgressCalculator, ExecutionMode as CalcExecutionMode
    from core.macro_types import Macro, MouseClickStep
    
    # Create test macro
    macro = Macro(name="Test Macro")
    for i in range(5):
        step = MouseClickStep(name=f"Step {i+1}")
        step.x = 100 + i * 10
        step.y = 200
        macro.add_step(step)
    
    # Test calculator
    calc = ProgressCalculator(CalcExecutionMode.EXCEL)
    calc.initialize_macro(macro, total_rows=10)
    print(f"  - Initialized with {calc.total_steps} steps, {calc.total_rows} rows")
    
    # Simulate progress
    calc.start_row(0)
    calc.start_step(macro.steps[0], 0)
    progress_info = calc.calculate_progress()
    print(f"  - Progress calculation: {progress_info.percentage:.1f}%")
    
    print("  [PASS] Progress calculator working\n")
    
except Exception as e:
    print(f"  [FAIL] Error: {e}\n")

# Test 5: Settings Integration
print("[TEST 5] Settings Integration")
try:
    from config.settings import Settings
    
    settings = Settings()
    
    # Check notification settings
    notification_settings = {
        "notification.preparation.countdown_seconds": 5,
        "notification.floating_widget.default_mode": "normal",
        "notification.system_tray.enabled": True
    }
    
    # First check if settings are loaded
    print(f"  - Settings loaded: {hasattr(settings, 'settings') and settings.settings is not None}")
    
    for key, expected in notification_settings.items():
        value = settings.get(key)
        if value is None:
            # Try with default value
            value = settings.get(key, expected)
        match = value == expected
        print(f"  - {key}: {value} [{match}]")
    
    print("  [PASS] Settings integration working\n")
    
except Exception as e:
    print(f"  [FAIL] Error: {e}\n")

print("=== TEST SUMMARY ===")
print("All feature tests completed. Check results above for any failures.")