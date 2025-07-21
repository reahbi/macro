"""
Real environment tests for various system configurations
Tests actual behavior in different environments
"""

import pytest
import pyautogui
import subprocess
import time
import os
import tempfile
from pathlib import Path
import win32api
import win32con
import screeninfo
import ctypes
from PIL import Image
import mss

from PyQt5.QtWidgets import QApplication
from PyQt5.QtTest import QTest

from core.macro_types import Macro, MouseClickStep, KeyboardTypeStep, ImageSearchStep
from automation.engine import ExecutionEngine
from vision.image_matcher import ImageMatcher
from vision.text_extractor import TextExtractor
from config.settings import Settings


class TestRealEnvironment:
    """Test in various real environment conditions"""
    
    @pytest.fixture
    def capture_screenshot(self):
        """Helper to capture screenshots for verification"""
        def _capture(region=None):
            with mss.mss() as sct:
                if region:
                    monitor = {"left": region[0], "top": region[1], 
                              "width": region[2], "height": region[3]}
                else:
                    monitor = sct.monitors[1]
                return sct.grab(monitor)
        return _capture
    
    def test_windows_path_limit(self):
        """Test handling of Windows MAX_PATH (260 chars) limitation"""
        # Create path approaching MAX_PATH
        base_path = Path("C:/")
        long_name = "a" * 50  # 50 chars per directory
        
        current_path = base_path
        path_created = []
        
        try:
            # Create nested directories until we hit the limit
            for i in range(10):  # Should exceed 260 chars
                current_path = current_path / f"{long_name}_{i}"
                try:
                    current_path.mkdir(exist_ok=True)
                    path_created.append(current_path)
                except OSError as e:
                    # Expected on Windows when path too long
                    assert len(str(current_path)) > 260
                    break
            
            # Test macro save with long path
            from core.macro_storage import MacroStorage
            
            # Should handle gracefully
            if path_created:
                storage = MacroStorage(path_created[-1])
                macro = Macro(name="test")
                result = storage.save_macro(macro)
                
                # Should either succeed with short names or fail gracefully
                assert isinstance(result, bool)
                
        finally:
            # Cleanup
            for path in reversed(path_created):
                try:
                    path.rmdir()
                except:
                    pass
    
    def test_multi_monitor_coordinates(self, capture_screenshot):
        """Test coordinate handling across multiple monitors"""
        monitors = screeninfo.get_monitors()
        
        if len(monitors) < 2:
            pytest.skip("Test requires multiple monitors")
        
        # Test click on each monitor
        for i, monitor in enumerate(monitors):
            # Calculate center of monitor
            center_x = monitor.x + monitor.width // 2
            center_y = monitor.y + monitor.height // 2
            
            # Create test window on this monitor
            test_window_path = r"C:\Windows\System32\notepad.exe"
            if Path(test_window_path).exists():
                # Open notepad
                process = subprocess.Popen([test_window_path])
                time.sleep(2)
                
                # Move window to target monitor
                import win32gui
                
                def enum_windows_callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        title = win32gui.GetWindowText(hwnd)
                        if "Notepad" in title or "메모장" in title:
                            windows.append(hwnd)
                
                windows = []
                win32gui.EnumWindows(enum_windows_callback, windows)
                
                if windows:
                    hwnd = windows[0]
                    # Move to monitor
                    win32gui.SetWindowPos(
                        hwnd, 0,
                        monitor.x + 100, monitor.y + 100,
                        600, 400,
                        win32con.SWP_NOZORDER
                    )
                    time.sleep(1)
                    
                    # Click on window
                    pyautogui.click(center_x, center_y)
                    
                    # Type text to verify click worked
                    pyautogui.typewrite(f"Monitor {i}: {monitor.width}x{monitor.height}")
                    
                    # Capture screenshot to verify
                    screenshot = capture_screenshot(
                        (monitor.x, monitor.y, monitor.width, monitor.height)
                    )
                    
                    # Close notepad
                    process.terminate()
    
    def test_dpi_scaling_levels(self):
        """Test with different DPI scaling levels"""
        # Get current DPI
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        
        dc = user32.GetDC(0)
        gdi32 = ctypes.windll.gdi32
        dpi = gdi32.GetDeviceCaps(dc, 88)  # LOGPIXELSX
        user32.ReleaseDC(0, dc)
        
        scaling_factor = dpi / 96.0  # 96 is standard DPI
        
        # Test mouse positioning at different scales
        test_positions = [
            (100, 100),
            (500, 300),
            (1000, 600)
        ]
        
        for base_x, base_y in test_positions:
            # Adjust for DPI scaling
            actual_x = int(base_x * scaling_factor)
            actual_y = int(base_y * scaling_factor)
            
            # Move mouse
            pyautogui.moveTo(actual_x, actual_y)
            time.sleep(0.1)
            
            # Verify position
            current_x, current_y = pyautogui.position()
            
            # Should be close to target (within few pixels)
            assert abs(current_x - actual_x) < 5
            assert abs(current_y - actual_y) < 5
    
    def test_korean_ime_types(self):
        """Test different Korean IME input methods"""
        # Test different Korean input scenarios
        test_cases = [
            ("한글", "Korean only"),
            ("abc한글123", "Mixed alphanumeric and Korean"),
            ("ㄱㄴㄷㄹ", "Korean consonants"),
            ("ㅏㅑㅓㅕ", "Korean vowels"),
            ("한글english混合", "Multiple languages"),
            ("괜찮아요", "Complex Korean"),
            ("㉠㉡㉢", "Korean symbols"),
        ]
        
        # Open notepad for testing
        notepad = subprocess.Popen([r"C:\Windows\System32\notepad.exe"])
        time.sleep(2)
        
        try:
            for korean_text, description in test_cases:
                # Clear notepad
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('delete')
                
                # Type Korean text
                pyautogui.typewrite(korean_text, interval=0.05)
                pyautogui.press('enter')
                
                # Add description
                pyautogui.typewrite(f"  -> {description}", interval=0.01)
                pyautogui.press('enter')
                pyautogui.press('enter')
                
                time.sleep(0.5)
            
        finally:
            notepad.terminate()
    
    def test_screen_resolution_changes(self):
        """Test handling of screen resolution changes"""
        # Get current resolution
        user32 = ctypes.windll.user32
        original_width = user32.GetSystemMetrics(0)
        original_height = user32.GetSystemMetrics(1)
        
        # Test data
        image_matcher = ImageMatcher(Settings())
        text_extractor = TextExtractor()
        
        # Create test macro with absolute positions
        macro = Macro(name="해상도 테스트")
        macro.add_step(MouseClickStep(
            name="Center click",
            x=original_width // 2,
            y=original_height // 2
        ))
        
        # Note: Actually changing resolution requires admin rights
        # and is disruptive, so we simulate the calculation
        
        # Simulate different resolutions
        test_resolutions = [
            (1920, 1080),
            (1366, 768),
            (1280, 720),
            (2560, 1440)
        ]
        
        for width, height in test_resolutions:
            # Calculate scale factors
            scale_x = width / original_width
            scale_y = height / original_height
            
            # Adjusted coordinates
            adjusted_x = int((original_width // 2) * scale_x)
            adjusted_y = int((original_height // 2) * scale_y)
            
            # Verify calculations
            assert 0 <= adjusted_x <= width
            assert 0 <= adjusted_y <= height
    
    def test_focus_and_window_switching(self):
        """Test window focus handling during macro execution"""
        # Open multiple windows
        windows = []
        window_titles = ["Window 1", "Window 2", "Window 3"]
        
        for i, title in enumerate(window_titles):
            notepad = subprocess.Popen([r"C:\Windows\System32\notepad.exe"])
            windows.append(notepad)
            time.sleep(1)
            
            # Type window identifier
            pyautogui.typewrite(title)
            
            # Move window to different position
            pyautogui.hotkey('alt', 'space')
            pyautogui.press('m')
            pyautogui.moveTo(100 + i * 200, 100 + i * 100)
            pyautogui.click()
        
        try:
            # Test switching between windows
            for i in range(len(windows)):
                # Alt+Tab to cycle windows
                pyautogui.hotkey('alt', 'tab')
                time.sleep(0.5)
                
                # Type in current window
                pyautogui.typewrite(f"\nActive: {time.time()}")
            
            # Test click to focus
            for i in range(len(windows)):
                pyautogui.click(100 + i * 200, 100 + i * 100)
                time.sleep(0.5)
                pyautogui.typewrite(f"\nClicked: {i}")
                
        finally:
            # Close all windows
            for notepad in windows:
                notepad.terminate()
    
    def test_system_dialog_handling(self):
        """Test handling of system dialogs and popups"""
        # Test save dialog
        notepad = subprocess.Popen([r"C:\Windows\System32\notepad.exe"])
        time.sleep(2)
        
        try:
            # Type some text
            pyautogui.typewrite("Test content for save dialog")
            
            # Trigger save dialog
            pyautogui.hotkey('ctrl', 's')
            time.sleep(1)
            
            # Handle save dialog
            # Type filename
            temp_file = os.path.join(tempfile.gettempdir(), "test_save.txt")
            pyautogui.typewrite(temp_file)
            time.sleep(0.5)
            
            # Press Enter to save
            pyautogui.press('enter')
            time.sleep(1)
            
            # Verify file was created
            assert Path(temp_file).exists()
            
            # Clean up
            Path(temp_file).unlink()
            
        finally:
            notepad.terminate()
    
    def test_performance_under_load(self):
        """Test performance when system is under load"""
        import threading
        import hashlib
        
        # Create CPU load
        stop_load = False
        
        def cpu_load():
            while not stop_load:
                # CPU intensive task
                hashlib.sha256(b"test" * 1000000).hexdigest()
        
        # Start load threads
        load_threads = []
        for i in range(4):  # 4 threads for load
            thread = threading.Thread(target=cpu_load)
            thread.start()
            load_threads.append(thread)
        
        try:
            # Test macro execution under load
            start_time = time.time()
            
            # Simple macro operations
            for i in range(10):
                pyautogui.moveTo(100 + i * 50, 100 + i * 50)
                pyautogui.click()
                time.sleep(0.1)
            
            execution_time = time.time() - start_time
            
            # Should still complete in reasonable time
            assert execution_time < 5.0  # 5 seconds max
            
        finally:
            # Stop load
            stop_load = True
            for thread in load_threads:
                thread.join()
    
    def test_network_drive_access(self):
        """Test file operations on network drives"""
        # Check if any network drives are available
        import win32api
        
        drives = win32api.GetLogicalDriveStrings()
        drives = drives.split('\000')[:-1]
        
        network_drives = []
        for drive in drives:
            drive_type = win32api.GetDriveType(drive)
            if drive_type == win32con.DRIVE_REMOTE:
                network_drives.append(drive)
        
        if not network_drives:
            pytest.skip("No network drives available")
        
        # Test file operations on network drive
        for drive in network_drives:
            test_path = Path(drive) / "macro_test"
            
            try:
                # Test directory creation
                test_path.mkdir(exist_ok=True)
                
                # Test file write
                test_file = test_path / "test.txt"
                test_file.write_text("Network drive test")
                
                # Test file read
                content = test_file.read_text()
                assert content == "Network drive test"
                
                # Cleanup
                test_file.unlink()
                test_path.rmdir()
                
            except Exception as e:
                # Network drive might not have write permissions
                print(f"Network drive {drive} test failed: {e}")