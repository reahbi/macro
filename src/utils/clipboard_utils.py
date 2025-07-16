"""
Clipboard utilities for cross-platform image handling
"""

import os
import sys
import time
import subprocess
from typing import Optional
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication
from utils.path_utils import get_captures_dir, is_wsl


def save_clipboard_image() -> Optional[str]:
    """
    Try multiple methods to save clipboard image to file
    Returns the saved file path or None if no image found
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"clipboard_{timestamp}.png"
    
    # Create captures directory using path utility
    captures_dir = get_captures_dir()
    file_path = os.path.join(captures_dir, filename)
    
    # Method 1: Try Windows PowerShell if in WSL
    if is_wsl():
        if save_from_windows_clipboard(file_path):
            return file_path
    
    # Method 2: Try Qt clipboard
    if save_from_qt_clipboard(file_path):
        return file_path
    
    # Method 3: Try PIL
    if save_from_pil_clipboard(file_path):
        return file_path
    
    return None


def save_from_windows_clipboard(file_path: str) -> bool:
    """
    Use PowerShell to save clipboard image (WSL specific)
    """
    try:
        # Convert WSL path to Windows path
        win_path = subprocess.check_output(['wslpath', '-w', file_path]).decode().strip()
        
        # PowerShell script to save clipboard image
        ps_script = f'''
        Add-Type -Assembly System.Windows.Forms
        $clipboard = [System.Windows.Forms.Clipboard]::GetImage()
        if ($clipboard -ne $null) {{
            $clipboard.Save("{win_path}", [System.Drawing.Imaging.ImageFormat]::Png)
            Write-Host "SUCCESS"
        }} else {{
            Write-Host "NO_IMAGE"
        }}
        '''
        
        # Run PowerShell command
        result = subprocess.run(
            ['powershell.exe', '-Command', ps_script],
            capture_output=True,
            text=True
        )
        
        if "SUCCESS" in result.stdout:
            print("Successfully saved image from Windows clipboard")
            return True
        elif "NO_IMAGE" in result.stdout:
            print("No image in Windows clipboard")
        else:
            print(f"PowerShell error: {result.stderr}")
            
    except Exception as e:
        print(f"Windows clipboard error: {e}")
    
    return False


def save_from_qt_clipboard(file_path: str) -> bool:
    """
    Save image from Qt clipboard
    """
    try:
        clipboard = QApplication.clipboard()
        
        # Try image first
        if clipboard.mimeData().hasImage():
            image = clipboard.image()
            if not image.isNull():
                if image.save(file_path, "PNG"):
                    print("Successfully saved image from Qt clipboard")
                    return True
        
        # Try pixmap
        pixmap = clipboard.pixmap()
        if not pixmap.isNull():
            if pixmap.save(file_path, "PNG"):
                print("Successfully saved pixmap from Qt clipboard")
                return True
                
    except Exception as e:
        print(f"Qt clipboard error: {e}")
    
    return False


def save_from_pil_clipboard(file_path: str) -> bool:
    """
    Save image from PIL clipboard
    """
    try:
        from PIL import ImageGrab
        
        # Try multiple times with delay
        for attempt in range(3):
            if attempt > 0:
                time.sleep(0.1)
                
            img = ImageGrab.grabclipboard()
            if img:
                img.save(file_path)
                print("Successfully saved image from PIL clipboard")
                return True
                
    except Exception as e:
        print(f"PIL clipboard error: {e}")
    
    return False