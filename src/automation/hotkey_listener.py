"""
Global hotkey listener for execution control
"""

import threading
from typing import Optional, Dict, Callable
from PyQt5.QtCore import QObject, pyqtSignal
try:
    from pynput import keyboard
except ImportError:
    # Fallback for systems without pynput
    keyboard = None
from config.settings import Settings
from logger.app_logger import get_logger

class HotkeyListener(QObject):
    """Listens for global hotkeys"""
    
    # Signals
    startPressed = pyqtSignal()  # F5 시작 키 추가
    pausePressed = pyqtSignal()
    stopPressed = pyqtSignal()
    
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.logger = get_logger(__name__)
        self._listener: Optional[keyboard.Listener] = None
        self._running = False
        
        # Get hotkey settings
        self.start_key = self._parse_key(settings.get("hotkeys.start", "F5"))
        self.pause_key = self._parse_key(settings.get("hotkeys.pause", "F9"))
        self.stop_key = self._parse_key(settings.get("hotkeys.stop", "Escape"))
        
        # Current key states
        self._pressed_keys = set()
        
    def _parse_key(self, key_string: str):
        """Parse key string to pynput key"""
        if not keyboard:
            return None
            
        # Map common key names
        key_map = {
            "F1": keyboard.Key.f1,
            "F2": keyboard.Key.f2,
            "F3": keyboard.Key.f3,
            "F4": keyboard.Key.f4,
            "F5": keyboard.Key.f5,
            "F6": keyboard.Key.f6,
            "F7": keyboard.Key.f7,
            "F8": keyboard.Key.f8,
            "F9": keyboard.Key.f9,
            "F10": keyboard.Key.f10,
            "F11": keyboard.Key.f11,
            "F12": keyboard.Key.f12,
            "Escape": keyboard.Key.esc,
            "Space": keyboard.Key.space,
            "Enter": keyboard.Key.enter,
            "Tab": keyboard.Key.tab,
            "Backspace": keyboard.Key.backspace,
            "Delete": keyboard.Key.delete,
            "Home": keyboard.Key.home,
            "End": keyboard.Key.end,
            "PageUp": keyboard.Key.page_up,
            "PageDown": keyboard.Key.page_down,
            "Left": keyboard.Key.left,
            "Right": keyboard.Key.right,
            "Up": keyboard.Key.up,
            "Down": keyboard.Key.down,
        }
        
        return key_map.get(key_string, key_string.lower())
        
    def start(self):
        """Start listening for hotkeys"""
        if not keyboard:
            self.logger.warning("pynput not available, hotkeys disabled")
            return
            
        if self._running:
            return
            
        self._running = True
        
        try:
            self._listener = keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self._listener.start()
            self.logger.info(f"Hotkey listener started (Start: {self.start_key}, Pause: {self.pause_key}, Stop: {self.stop_key})")
        except Exception as e:
            self.logger.error(f"Failed to start hotkey listener: {e}")
            
    def stop(self):
        """Stop listening for hotkeys"""
        if not self._running:
            return
            
        self._running = False
        
        if self._listener:
            self._listener.stop()
            self._listener = None
            
        self.logger.info("Hotkey listener stopped")
        
    def _on_press(self, key):
        """Handle key press"""
        try:
            # Add to pressed keys
            self._pressed_keys.add(key)
            
            # Check for start hotkey
            if self._check_key(key, self.start_key):
                self.logger.debug("Start hotkey pressed")
                self.startPressed.emit()
                
            # Check for pause hotkey
            elif self._check_key(key, self.pause_key):
                self.logger.debug("Pause hotkey pressed")
                self.pausePressed.emit()
                
            # Check for stop hotkey
            elif self._check_key(key, self.stop_key):
                self.logger.debug("Stop hotkey pressed")
                self.stopPressed.emit()
                
        except Exception as e:
            self.logger.error(f"Error in key press handler: {e}")
            
    def _on_release(self, key):
        """Handle key release"""
        try:
            # Remove from pressed keys
            self._pressed_keys.discard(key)
        except Exception as e:
            self.logger.error(f"Error in key release handler: {e}")
            
    def _check_key(self, key, target_key) -> bool:
        """Check if pressed key matches target"""
        if not target_key:
            return False
            
        # Direct key comparison
        if key == target_key:
            return True
            
        # String comparison for character keys
        try:
            if hasattr(key, 'char') and key.char == target_key:
                return True
        except:
            pass
            
        return False

class SimpleHotkeyListener(QObject):
    """Simple hotkey listener using QShortcut (fallback)"""
    
    pausePressed = pyqtSignal()
    stopPressed = pyqtSignal()
    
    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.logger = get_logger(__name__)
        
    def start(self):
        """Start listening (no-op for simple listener)"""
        self.logger.info("Using simple hotkey listener (widget must have focus)")
        
    def stop(self):
        """Stop listening (no-op for simple listener)"""
        pass