"""
OpenCV-based image matching engine with DPI scaling and multi-monitor support
"""

import time
from typing import Optional, Tuple, List, Dict, Any
from dataclasses import dataclass
import numpy as np
import cv2
import pyautogui
from PIL import Image
import mss
from config.settings import Settings
from logger.app_logger import get_logger

@dataclass
class MatchResult:
    """Result of image matching operation"""
    found: bool
    confidence: float
    location: Optional[Tuple[int, int, int, int]] = None  # x, y, width, height
    center: Optional[Tuple[int, int]] = None  # center x, y
    
@dataclass 
class MonitorInfo:
    """Monitor information"""
    index: int
    left: int
    top: int
    width: int
    height: int
    scale: float = 1.0

class ImageMatcher:
    """Advanced image matching with OpenCV"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        self._template_cache: Dict[str, np.ndarray] = {}
        self._sct = mss.mss()
        self._monitors = self._detect_monitors()
        
    def _detect_monitors(self) -> List[MonitorInfo]:
        """Detect all monitors and their properties"""
        monitors = []
        
        for i, monitor in enumerate(self._sct.monitors[1:], 1):  # Skip combined monitor
            info = MonitorInfo(
                index=i,
                left=monitor["left"],
                top=monitor["top"],
                width=monitor["width"],
                height=monitor["height"]
            )
            
            # Detect DPI scaling (simplified - may need platform-specific code)
            try:
                # Get actual screen size vs reported size
                actual_size = pyautogui.size()
                if i == 1:  # Primary monitor
                    scale_x = actual_size.width / monitor["width"]
                    scale_y = actual_size.height / monitor["height"]
                    info.scale = max(scale_x, scale_y)
            except:
                info.scale = 1.0
                
            monitors.append(info)
            self.logger.debug(f"Detected monitor {i}: {info}")
            
        return monitors
        
    def _load_template(self, image_path: str, scale: float = 1.0) -> np.ndarray:
        """Load and cache template image with scaling"""
        cache_key = f"{image_path}_{scale}"
        
        if cache_key in self._template_cache:
            return self._template_cache[cache_key]
            
        try:
            # Load template
            template = cv2.imread(image_path)
            if template is None:
                raise ValueError(f"Failed to load image: {image_path}")
                
            # Apply DPI scaling if needed
            if scale != 1.0:
                width = int(template.shape[1] * scale)
                height = int(template.shape[0] * scale)
                template = cv2.resize(template, (width, height), interpolation=cv2.INTER_LINEAR)
                
            # Convert to grayscale for faster matching
            template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
            
            # Cache the processed template
            self._template_cache[cache_key] = template_gray
            
            return template_gray
            
        except Exception as e:
            self.logger.error(f"Error loading template {image_path}: {e}")
            raise
            
    def _capture_screen(self, region: Optional[Tuple[int, int, int, int]] = None,
                       monitor_index: Optional[int] = None) -> np.ndarray:
        """Capture screen or region"""
        try:
            if region:
                # Capture specific region
                monitor = {
                    "left": region[0],
                    "top": region[1], 
                    "width": region[2],
                    "height": region[3]
                }
            elif monitor_index is not None and 0 <= monitor_index < len(self._monitors):
                # Capture specific monitor
                mon_info = self._monitors[monitor_index]
                monitor = {
                    "left": mon_info.left,
                    "top": mon_info.top,
                    "width": mon_info.width,
                    "height": mon_info.height
                }
            else:
                # Capture all monitors
                monitor = self._sct.monitors[0]
                
            # Capture screenshot
            screenshot = self._sct.grab(monitor)
            
            # Convert to numpy array
            img = np.array(screenshot)
            
            # Convert BGRA to BGR
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
            
            return img
            
        except Exception as e:
            self.logger.error(f"Error capturing screen: {e}")
            raise
            
    def find_image(self, template_path: str, 
                   confidence: float = 0.9,
                   region: Optional[Tuple[int, int, int, int]] = None,
                   monitor_index: Optional[int] = None,
                   grayscale: bool = True) -> MatchResult:
        """Find image on screen using template matching"""
        
        try:
            # Determine scale factor
            scale = 1.0
            if monitor_index is not None and 0 <= monitor_index < len(self._monitors):
                scale = self._monitors[monitor_index].scale
                
            # Load template
            template = self._load_template(template_path, scale)
            
            # Capture screen
            screenshot = self._capture_screen(region, monitor_index)
            
            # Convert to grayscale if needed
            if grayscale:
                screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            else:
                screenshot_gray = screenshot
                
            # Perform template matching
            result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
            
            # Find best match
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= confidence:
                # Calculate absolute coordinates
                h, w = template.shape[:2]
                x, y = max_loc
                
                # Adjust for region offset if applicable
                if region:
                    x += region[0]
                    y += region[1]
                elif monitor_index is not None:
                    mon_info = self._monitors[monitor_index]
                    x += mon_info.left
                    y += mon_info.top
                    
                location = (x, y, w, h)
                center = (x + w // 2, y + h // 2)
                
                return MatchResult(
                    found=True,
                    confidence=max_val,
                    location=location,
                    center=center
                )
            else:
                return MatchResult(found=False, confidence=max_val)
                
        except Exception as e:
            self.logger.error(f"Error in find_image: {e}")
            return MatchResult(found=False, confidence=0.0)
            
    def find_all_images(self, template_path: str,
                       confidence: float = 0.9,
                       region: Optional[Tuple[int, int, int, int]] = None,
                       limit: int = 10) -> List[MatchResult]:
        """Find all occurrences of image on screen"""
        
        results = []
        
        try:
            # Load template
            template = self._load_template(template_path)
            
            # Capture screen  
            screenshot = self._capture_screen(region)
            screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
            
            # Perform template matching
            match_result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
            
            # Find all matches above threshold
            locations = np.where(match_result >= confidence)
            
            h, w = template.shape[:2]
            
            # Process matches
            for pt in zip(*locations[::-1]):
                if len(results) >= limit:
                    break
                    
                x, y = pt
                
                # Adjust for region offset
                if region:
                    x += region[0]
                    y += region[1]
                    
                location = (x, y, w, h)
                center = (x + w // 2, y + h // 2)
                
                # Get confidence for this match
                conf = match_result[y, x]
                
                results.append(MatchResult(
                    found=True,
                    confidence=float(conf),
                    location=location,
                    center=center
                ))
                
        except Exception as e:
            self.logger.error(f"Error in find_all_images: {e}")
            
        return results
        
    def wait_for_image(self, template_path: str,
                      timeout: float = 30.0,
                      confidence: float = 0.9,
                      region: Optional[Tuple[int, int, int, int]] = None,
                      check_interval: float = 0.5) -> MatchResult:
        """Wait for image to appear on screen"""
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            result = self.find_image(template_path, confidence, region)
            
            if result.found:
                return result
                
            time.sleep(check_interval)
            
        # Timeout reached
        return MatchResult(found=False, confidence=0.0)
        
    def capture_region(self, region: Tuple[int, int, int, int], 
                      save_path: Optional[str] = None) -> np.ndarray:
        """Capture a specific region of the screen"""
        
        screenshot = self._capture_screen(region)
        
        if save_path:
            cv2.imwrite(save_path, screenshot)
            self.logger.info(f"Saved screenshot to {save_path}")
            
        return screenshot
        
    def clear_cache(self):
        """Clear template cache"""
        self._template_cache.clear()
        self.logger.debug("Template cache cleared")

class ImageMatcherLegacy:
    """Legacy image matcher using pyautogui for fallback"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        
    def find_image(self, template_path: str,
                   confidence: float = 0.9,
                   region: Optional[Tuple[int, int, int, int]] = None) -> MatchResult:
        """Find image using pyautogui"""
        
        try:
            location = pyautogui.locateOnScreen(
                template_path,
                confidence=confidence,
                region=region
            )
            
            if location:
                center = pyautogui.center(location)
                return MatchResult(
                    found=True,
                    confidence=confidence,
                    location=location,
                    center=center
                )
            else:
                return MatchResult(found=False, confidence=0.0)
                
        except Exception as e:
            self.logger.error(f"Error in legacy find_image: {e}")
            return MatchResult(found=False, confidence=0.0)