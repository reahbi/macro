"""
Application settings management with encryption support
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from utils.encryption import EncryptionManager

class Settings:
    """Manages application settings with encryption support"""
    
    DEFAULT_SETTINGS = {
        "version": "1.0.0",
        "language": "ko",
        "theme": "light",
        "hotkeys": {
            "pause": "F9",
            "stop": "Escape",
            "start": "F5"
        },
        "execution": {
            "default_delay_ms": 100,
            "screenshot_quality": 95,
            "ocr_confidence_threshold": 0.7
        },
        "ui": {
            "window_size": [1280, 720],
            "show_tooltips": True,
            "confirm_exit": True,
            "compact_mode": False
        },
        "notification": {
            "preparation": {
                "enabled": True,
                "countdown_seconds": 5,
                "minimize_window": True,
                "show_countdown": True
            },
            "floating_widget": {
                "enabled": True,
                "default_mode": "normal",  # minimal, normal, detailed
                "auto_hide_delay": 3000,
                "show_completion_animation": True,
                "opacity": 0.9
            },
            "system_tray": {
                "enabled": True,
                "show_notifications": True,
                "notification_duration": 3000,
                "animate_on_execution": True
            },
            "sound": {
                "enabled": False,
                "completion_sound": "",
                "error_sound": ""
            }
        }
    }
    
    def __init__(self, config_dir: Optional[Path] = None):
        """Initialize settings manager"""
        self.config_dir = config_dir or Path.home() / ".excel_macro_automation"
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        self.settings_file = self.config_dir / "settings.json"
        self.encrypted_settings_file = self.config_dir / "settings.enc"
        
        self.encryption_manager = EncryptionManager()
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create defaults"""
        # Try loading encrypted settings first
        if self.encrypted_settings_file.exists():
            try:
                encrypted_data = self.encrypted_settings_file.read_bytes()
                decrypted_data = self.encryption_manager.decrypt(encrypted_data)
                return json.loads(decrypted_data.decode('utf-8'))
            except Exception as e:
                print(f"Failed to load encrypted settings: {e}")
        
        # Try loading plain JSON settings
        if self.settings_file.exists():
            try:
                return json.loads(self.settings_file.read_text(encoding='utf-8'))
            except Exception as e:
                print(f"Failed to load settings: {e}")
        
        # Return default settings
        return self.DEFAULT_SETTINGS.copy()
    
    def save(self, encrypted: bool = True) -> None:
        """Save settings to file"""
        settings_json = json.dumps(self.settings, indent=2, ensure_ascii=False)
        
        if encrypted:
            encrypted_data = self.encryption_manager.encrypt(settings_json.encode('utf-8'))
            self.encrypted_settings_file.write_bytes(encrypted_data)
            # Remove plain text version if it exists
            if self.settings_file.exists():
                self.settings_file.unlink()
        else:
            self.settings_file.write_text(settings_json, encoding='utf-8')
            # Remove encrypted version if it exists
            if self.encrypted_settings_file.exists():
                self.encrypted_settings_file.unlink()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get setting value by key (supports dot notation)"""
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set setting value by key (supports dot notation)"""
        keys = key.split('.')
        target = self.settings
        
        for k in keys[:-1]:
            if k not in target:
                target[k] = {}
            target = target[k]
        
        target[keys[-1]] = value
    
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults"""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save()