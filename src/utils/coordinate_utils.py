"""
Coordinate system utilities for handling multi-monitor environments
"""

from typing import Tuple, Dict, Optional, List
import mss
from logger.app_logger import get_logger

logger = get_logger(__name__)


class CoordinateConverter:
    """Handles coordinate conversion between different systems"""
    
    def __init__(self):
        self.sct = mss.mss()
        self.monitors = self.sct.monitors
        self.virtual_monitor = self.monitors[0] if self.monitors else None
        
    def qt_to_mss(self, qt_x: int, qt_y: int) -> Tuple[int, int]:
        """Convert Qt global coordinates to mss coordinates
        
        Note: Both Qt and mss use absolute screen coordinates in multi-monitor setups.
        No conversion is needed - they use the same coordinate system.
        """
        logger.debug(f"Qt to mss: ({qt_x}, {qt_y}) -> ({qt_x}, {qt_y}) (no conversion needed)")
        return qt_x, qt_y
    
    def mss_to_qt(self, mss_x: int, mss_y: int) -> Tuple[int, int]:
        """Convert mss coordinates to Qt global coordinates
        
        Note: Both Qt and mss use absolute screen coordinates in multi-monitor setups.
        No conversion is needed - they use the same coordinate system.
        """
        logger.debug(f"mss to Qt: ({mss_x}, {mss_y}) -> ({mss_x}, {mss_y}) (no conversion needed)")
        return mss_x, mss_y
    
    def get_monitor_at_point(self, x: int, y: int) -> Optional[Dict]:
        """Get monitor information at the given point"""
        # Skip virtual monitor (index 0)
        for i, monitor in enumerate(self.monitors[1:], 1):
            if (monitor['left'] <= x < monitor['left'] + monitor['width'] and
                monitor['top'] <= y < monitor['top'] + monitor['height']):
                return {
                    'index': i,
                    'monitor': monitor,
                    'relative_x': x - monitor['left'],
                    'relative_y': y - monitor['top']
                }
        return None
    
    def absolute_to_monitor_relative(self, x: int, y: int, monitor_index: int = None) -> Tuple[int, int, int]:
        """Convert absolute coordinates to monitor-relative coordinates
        
        Returns: (relative_x, relative_y, monitor_index)
        """
        if monitor_index and 0 < monitor_index < len(self.monitors):
            monitor = self.monitors[monitor_index]
            return x - monitor['left'], y - monitor['top'], monitor_index
        
        # Find which monitor contains the point
        monitor_info = self.get_monitor_at_point(x, y)
        if monitor_info:
            return monitor_info['relative_x'], monitor_info['relative_y'], monitor_info['index']
        
        # Default to primary monitor
        if len(self.monitors) > 1:
            primary = self.monitors[1]
            return x - primary['left'], y - primary['top'], 1
        
        return x, y, 0
    
    def monitor_relative_to_absolute(self, rel_x: int, rel_y: int, monitor_index: int) -> Tuple[int, int]:
        """Convert monitor-relative coordinates to absolute coordinates"""
        if 0 < monitor_index < len(self.monitors):
            monitor = self.monitors[monitor_index]
            abs_x = rel_x + monitor['left']
            abs_y = rel_y + monitor['top']
            logger.debug(f"Monitor {monitor_index} relative ({rel_x}, {rel_y}) -> absolute ({abs_x}, {abs_y})")
            return abs_x, abs_y
        
        logger.warning(f"Invalid monitor index: {monitor_index}")
        return rel_x, rel_y
    
    def verify_region_match(self, region: Tuple[int, int, int, int], 
                          saved_preview_path: str = None) -> bool:
        """Verify if the current screen matches the saved region
        
        This can be used to detect if monitors have been rearranged
        """
        # TODO: Implement image comparison logic
        # For now, just check if the region is within screen bounds
        x, y, w, h = region
        
        # Check if region is within any monitor
        for monitor in self.monitors[1:]:
            if (x >= monitor['left'] and 
                y >= monitor['top'] and 
                x + w <= monitor['left'] + monitor['width'] and
                y + h <= monitor['top'] + monitor['height']):
                return True
        
        logger.warning(f"Region {region} is outside all monitor bounds")
        return False
    
    def get_debug_info(self) -> Dict:
        """Get debug information about the coordinate system"""
        info = {
            'virtual_monitor': self.virtual_monitor,
            'monitor_count': len(self.monitors) - 1,  # Exclude virtual
            'monitors': []
        }
        
        for i, monitor in enumerate(self.monitors[1:], 1):
            info['monitors'].append({
                'index': i,
                'bounds': {
                    'left': monitor['left'],
                    'top': monitor['top'],
                    'width': monitor['width'],
                    'height': monitor['height']
                }
            })
        
        return info
    
    def close(self):
        """Clean up resources"""
        if hasattr(self, 'sct'):
            self.sct.close()


# Global instance for convenience
_converter = None


def get_converter() -> CoordinateConverter:
    """Get global coordinate converter instance"""
    global _converter
    if _converter is None:
        _converter = CoordinateConverter()
    return _converter


def cleanup():
    """Clean up global resources"""
    global _converter
    if _converter:
        _converter.close()
        _converter = None