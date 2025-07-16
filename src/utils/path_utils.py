"""
Cross-platform path utilities for Windows/WSL compatibility
"""

import os
import sys
import platform


def normalize_path(path: str) -> str:
    """
    Normalize path for the current platform
    Handles both Windows and WSL/Linux paths
    """
    if not path:
        return path
    
    # Convert to absolute path if relative
    if not os.path.isabs(path):
        path = os.path.abspath(path)
    
    # Normalize separators
    path = os.path.normpath(path)
    
    return path


def get_project_root() -> str:
    """
    Get the project root directory in a platform-independent way
    """
    # Get the directory of this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go up two levels (utils -> src -> project_root)
    project_root = os.path.dirname(os.path.dirname(current_dir))
    
    return normalize_path(project_root)


def get_captures_dir() -> str:
    """
    Get the captures directory, creating it if necessary
    """
    captures_dir = os.path.join(get_project_root(), "captures")
    os.makedirs(captures_dir, exist_ok=True)
    return captures_dir


def get_logs_dir() -> str:
    """
    Get the logs directory, creating it if necessary
    """
    logs_dir = os.path.join(get_project_root(), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir


def is_wsl() -> bool:
    """
    Check if running in WSL environment
    """
    return 'microsoft' in platform.uname().release.lower()


def is_windows_native() -> bool:
    """
    Check if running in native Windows (not WSL)
    """
    return sys.platform == 'win32' and not is_wsl()


def convert_wsl_to_windows_path(wsl_path: str) -> str:
    """
    Convert WSL path to Windows path
    Example: /home/user/file -> \\\\wsl$\\Ubuntu\\home\\user\\file
    """
    if not wsl_path.startswith('/'):
        return wsl_path
    
    # Get WSL distribution name (default to Ubuntu)
    import subprocess
    try:
        result = subprocess.run(['wslpath', '-w', wsl_path], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    # Fallback conversion
    windows_path = wsl_path.replace('/', '\\')
    return f"\\\\wsl$\\Ubuntu{windows_path}"


def convert_windows_to_wsl_path(windows_path: str) -> str:
    """
    Convert Windows path to WSL path
    Example: C:\\Users\\file -> /mnt/c/Users/file
    """
    if ':' not in windows_path:
        return windows_path
    
    # Use wslpath if available
    import subprocess
    try:
        result = subprocess.run(['wslpath', '-u', windows_path], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    # Fallback conversion
    drive = windows_path[0].lower()
    path = windows_path[2:].replace('\\', '/')
    return f"/mnt/{drive}{path}"