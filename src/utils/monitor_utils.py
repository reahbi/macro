"""
Monitor detection and coordinate utilities
"""

from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


def get_monitor_info() -> List[Dict]:
    """
    Get information about all connected monitors
    Returns list of monitor dictionaries with x, y, width, height, is_primary
    """
    monitors = []
    
    try:
        # Try using screeninfo library if available
        from screeninfo import get_monitors
        
        for m in get_monitors():
            monitors.append({
                'name': m.name,
                'x': m.x,
                'y': m.y,
                'width': m.width,
                'height': m.height,
                'is_primary': m.is_primary if hasattr(m, 'is_primary') else (m.x == 0 and m.y == 0)
            })
            
    except ImportError:
        logger.warning("screeninfo not installed, using fallback method")
        # Fallback to tkinter method
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()  # Hide the window
            
            # Get primary monitor info
            primary_width = root.winfo_screenwidth()
            primary_height = root.winfo_screenheight()
            
            # Get virtual screen size (all monitors)
            virtual_width = root.winfo_vrootwidth()
            virtual_height = root.winfo_vrootheight()
            
            monitors.append({
                'name': 'Primary',
                'x': 0,
                'y': 0,
                'width': primary_width,
                'height': primary_height,
                'is_primary': True
            })
            
            # If virtual size is larger, we have multiple monitors
            if virtual_width > primary_width:
                # Assume second monitor is to the right
                monitors.append({
                    'name': 'Secondary',
                    'x': primary_width,
                    'y': 0,
                    'width': virtual_width - primary_width,
                    'height': primary_height,
                    'is_primary': False
                })
            elif virtual_width < 0:
                # Monitor might be to the left
                monitors.insert(0, {
                    'name': 'Secondary',
                    'x': virtual_width,
                    'y': 0,
                    'width': -virtual_width,
                    'height': primary_height,
                    'is_primary': False
                })
                
            root.destroy()
            
        except Exception as e:
            logger.error(f"Failed to get monitor info: {e}")
            # Return at least one monitor
            monitors.append({
                'name': 'Default',
                'x': 0,
                'y': 0,
                'width': 1920,
                'height': 1080,
                'is_primary': True
            })
    
    return monitors


def get_monitor_at_position(x: int, y: int) -> Optional[Dict]:
    """
    Get monitor information for the monitor containing the given position
    """
    monitors = get_monitor_info()
    
    for monitor in monitors:
        if (monitor['x'] <= x < monitor['x'] + monitor['width'] and
            monitor['y'] <= y < monitor['y'] + monitor['height']):
            return monitor
            
    # If no monitor found, return the primary monitor
    for monitor in monitors:
        if monitor['is_primary']:
            return monitor
            
    return monitors[0] if monitors else None


def get_monitor_name_for_position(x: int, y: int) -> str:
    """
    Get a friendly name for the monitor at the given position
    """
    monitor = get_monitor_at_position(x, y)
    
    if not monitor:
        return "알 수 없는 모니터"
        
    # Create a friendly name based on position
    if monitor['is_primary']:
        return "주 모니터"
    elif monitor['x'] < 0:
        return "왼쪽 모니터"
    elif monitor['x'] > 0:
        return "오른쪽 모니터"
    elif monitor['y'] < 0:
        return "위쪽 모니터"
    elif monitor['y'] > 0:
        return "아래쪽 모니터"
    else:
        return monitor.get('name', '보조 모니터')


def get_total_screen_bounds() -> Tuple[int, int, int, int]:
    """
    Get the total bounds of all monitors combined
    Returns: (min_x, min_y, max_x, max_y)
    """
    monitors = get_monitor_info()
    
    if not monitors:
        return (0, 0, 1920, 1080)
        
    min_x = min(m['x'] for m in monitors)
    min_y = min(m['y'] for m in monitors)
    max_x = max(m['x'] + m['width'] for m in monitors)
    max_y = max(m['y'] + m['height'] for m in monitors)
    
    return (min_x, min_y, max_x, max_y)


def is_position_valid(x: int, y: int) -> bool:
    """
    Check if a position is within any monitor bounds
    """
    return get_monitor_at_position(x, y) is not None