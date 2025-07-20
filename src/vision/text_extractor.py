"""
Text extraction using EasyOCR for dynamic text search
"""

import os
import numpy as np
from typing import Optional, List, Tuple, Dict, Any
from dataclasses import dataclass
import cv2
from PIL import Image
import mss
from logger.app_logger import get_logger
from utils.monitor_utils import get_total_screen_bounds, get_monitor_at_position

# EasyOCR is optional - will work without it
try:
    import easyocr
except ImportError:
    easyocr = None

@dataclass
class TextResult:
    """Result from text detection"""
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    center: Tuple[int, int]  # (center_x, center_y)

class TextExtractor:
    """Extract text from screen regions using EasyOCR"""
    
    _instance = None
    _reader = None
    
    def __new__(cls):
        """Singleton pattern to avoid multiple EasyOCR reader instances"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize text extractor"""
        if not hasattr(self, 'initialized'):
            self.logger = get_logger(__name__)
            self.sct = mss.mss()
            self.initialized = True
            
    def _get_reader(self) -> Optional['easyocr.Reader']:
        """Get or create EasyOCR reader (lazy loading)"""
        if easyocr is None:
            self.logger.warning("EasyOCR not installed - OCR functionality disabled")
            return None
            
        if TextExtractor._reader is None:
            try:
                self.logger.info("Initializing EasyOCR reader with Korean and English support...")
                # Initialize with Korean and English
                # Set download_enabled=True to auto-download models if needed
                TextExtractor._reader = easyocr.Reader(['ko', 'en'], gpu=False, download_enabled=True)
                self.logger.info("EasyOCR reader initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize EasyOCR: {e}")
                self.logger.warning("OCR functionality will be disabled")
                return None
        return TextExtractor._reader
    
    def extract_text_from_region(self, region: Optional[Tuple[int, int, int, int]] = None,
                                confidence_threshold: float = 0.5) -> List[TextResult]:
        """
        Extract text from screen region
        
        Args:
            region: (x, y, width, height) or None for full screen
            confidence_threshold: Minimum confidence for text detection
            
        Returns:
            List of TextResult objects
        """
        try:
            # Capture screen region
            if region:
                x, y, width, height = region
                monitor = {"left": x, "top": y, "width": width, "height": height}
            else:
                monitor = self.sct.monitors[0]  # All monitors
                
            # Capture screenshot
            screenshot = self.sct.grab(monitor)
            
            # Convert to numpy array
            img = np.array(screenshot)
            # Convert BGRA to RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
            
            # Get reader
            reader = self._get_reader()
            if reader is None:
                self.logger.warning("OCR reader not available")
                return []
            
            # Perform OCR
            try:
                results = reader.readtext(img_rgb)
            except Exception as e:
                self.logger.error(f"OCR failed: {e}")
                return []
            
            # Process results
            text_results = []
            for bbox, text, confidence in results:
                if confidence >= confidence_threshold:
                    # Convert bbox format
                    # EasyOCR returns [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
                    x_coords = [point[0] for point in bbox]
                    y_coords = [point[1] for point in bbox]
                    
                    min_x = int(min(x_coords))
                    min_y = int(min(y_coords))
                    max_x = int(max(x_coords))
                    max_y = int(max(y_coords))
                    
                    width = max_x - min_x
                    height = max_y - min_y
                    
                    # Calculate center point
                    center_x = min_x + width // 2
                    center_y = min_y + height // 2
                    
                    # Adjust coordinates if region was specified
                    if region:
                        min_x += region[0]
                        min_y += region[1]
                        center_x += region[0]
                        center_y += region[1]
                    else:
                        # When capturing all monitors, need to adjust for monitor offsets
                        monitor_info = self.sct.monitors[0]
                        min_x += monitor_info["left"]
                        min_y += monitor_info["top"]
                        center_x += monitor_info["left"]
                        center_y += monitor_info["top"]
                    
                    result = TextResult(
                        text=text,
                        confidence=confidence,
                        bbox=(min_x, min_y, width, height),
                        center=(center_x, center_y)
                    )
                    text_results.append(result)
                    
            self.logger.info(f"Extracted {len(text_results)} text items from region")
            return text_results
            
        except Exception as e:
            self.logger.error(f"Error extracting text: {e}")
            return []
    
    def find_text(self, target_text: str, region: Optional[Tuple[int, int, int, int]] = None,
                  exact_match: bool = False, confidence_threshold: float = 0.5) -> Optional[TextResult]:
        """
        Find specific text in screen region
        
        Args:
            target_text: Text to search for
            region: (x, y, width, height) or None for full screen
            exact_match: If True, requires exact match. If False, allows partial match
            confidence_threshold: Minimum OCR confidence
            
        Returns:
            TextResult if found, None otherwise
        """
        try:
            # Extract all text from region
            text_results = self.extract_text_from_region(region, confidence_threshold)
            
            # Normalize target text for comparison
            target_lower = target_text.lower().strip()
            
            # Find matching text
            best_match = None
            best_score = 0.0
            
            for result in text_results:
                text_lower = result.text.lower().strip()
                
                if exact_match:
                    if text_lower == target_lower:
                        return result
                else:
                    # Partial match - check if target is in detected text
                    if target_lower in text_lower:
                        # Score based on how much of the detected text matches
                        score = len(target_lower) / len(text_lower)
                        if score > best_score:
                            best_match = result
                            best_score = score
                    # Also check if detected text is in target (for partial OCR results)
                    elif text_lower in target_lower and len(text_lower) > 2:
                        score = len(text_lower) / len(target_lower)
                        if score > best_score:
                            best_match = result
                            best_score = score
            
            if best_match:
                self.logger.info(f"Found text '{target_text}' at {best_match.center}")
            else:
                self.logger.info(f"Text '{target_text}' not found in region")
                
            return best_match
            
        except Exception as e:
            self.logger.error(f"Error finding text: {e}")
            return None
    
    def find_all_text(self, target_text: str, region: Optional[Tuple[int, int, int, int]] = None,
                      exact_match: bool = False, confidence_threshold: float = 0.5) -> List[TextResult]:
        """
        Find all occurrences of text in screen region
        
        Args:
            target_text: Text to search for
            region: (x, y, width, height) or None for full screen
            exact_match: If True, requires exact match. If False, allows partial match
            confidence_threshold: Minimum OCR confidence
            
        Returns:
            List of TextResult objects
        """
        try:
            # Extract all text from region
            text_results = self.extract_text_from_region(region, confidence_threshold)
            
            # Normalize target text for comparison
            target_lower = target_text.lower().strip()
            
            # Find all matching text
            matches = []
            
            for result in text_results:
                text_lower = result.text.lower().strip()
                
                if exact_match:
                    if text_lower == target_lower:
                        matches.append(result)
                else:
                    # Partial match
                    if target_lower in text_lower or text_lower in target_lower:
                        matches.append(result)
            
            self.logger.info(f"Found {len(matches)} occurrences of '{target_text}'")
            return matches
            
        except Exception as e:
            self.logger.error(f"Error finding all text: {e}")
            return []
    
    def preload_models(self):
        """Preload OCR models to avoid delay on first use"""
        try:
            self.logger.info("Preloading EasyOCR models...")
            reader = self._get_reader()
            # Do a dummy recognition to load models
            dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
            reader.readtext(dummy_img)
            self.logger.info("EasyOCR models preloaded successfully")
        except Exception as e:
            self.logger.error(f"Error preloading models: {e}")