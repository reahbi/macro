"""
Test script to verify Settings behavior
"""

from pathlib import Path
import tempfile
from src.config.settings import Settings

# Test with temporary directory
with tempfile.TemporaryDirectory() as temp_dir:
    settings = Settings(Path(temp_dir))
    
    # Test getting nested values
    print("Testing Settings.get() method:")
    print(f"execution.default_delay_ms = {settings.get('execution.default_delay_ms')}")
    print(f"Type: {type(settings.get('execution.default_delay_ms'))}")
    
    # Test getting with default
    print(f"\nWith default: {settings.get('execution.default_delay_ms', 100)}")
    print(f"Type: {type(settings.get('execution.default_delay_ms', 100))}")
    
    # Test getting whole dict
    print(f"\nexecution = {settings.get('execution')}")
    print(f"Type: {type(settings.get('execution'))}")
    
    # Test division
    delay = settings.get('execution.default_delay_ms', 100)
    print(f"\nDelay value: {delay}")
    print(f"Delay / 1000.0 = {delay / 1000.0}")