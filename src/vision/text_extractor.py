"""
Text extraction using EasyOCR for dynamic text search
"""

import os
from typing import Optional, List, Tuple, Dict, Any
from dataclasses import dataclass
from PIL import Image
import mss
from logger.app_logger import get_logger
from utils.monitor_utils import get_total_screen_bounds, get_monitor_at_position

# Try to import numpy and cv2 with fallback
try:
    import numpy as np
    import cv2
    NUMPY_AVAILABLE = True
except ImportError as e:
    NUMPY_AVAILABLE = False
    np = None
    cv2 = None

# Try to import EasyOCR
try:
    import easyocr
    EASYOCR_AVAILABLE = True
except ImportError as e:
    EASYOCR_AVAILABLE = False
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
            # Don't create mss instance here - create it when needed
            self.sct = None
            self.initialized = True
            
            # OCR 상태 확인
            from utils.ocr_manager import OCRManager
            self.ocr_manager = OCRManager()
            
            if not self.ocr_manager.is_available():
                self.logger.warning("OCR이 아직 설치되지 않았습니다. 텍스트 검색 기능이 제한됩니다.")
            
    def _get_reader(self) -> Optional['easyocr.Reader']:
        """Get or create EasyOCR reader (lazy loading)"""
        if not EASYOCR_AVAILABLE or not NUMPY_AVAILABLE:
            error_msg = (
                "Text extraction is not available due to missing dependencies.\n"
                "Required: numpy, opencv-python, easyocr\n"
                "Please install with: pip install numpy opencv-python easyocr"
            )
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
            
        if TextExtractor._reader is None:
            try:
                self.logger.info("Initializing EasyOCR reader with Korean and English support...")
                # Initialize with Korean and English
                # Set download_enabled=True to auto-download models if needed
                # Auto-detect GPU availability
                try:
                    import torch
                    gpu_available = torch.cuda.is_available()
                    if gpu_available:
                        self.logger.info("GPU detected! Enabling GPU acceleration for EasyOCR")
                    else:
                        self.logger.info("No GPU detected. Using CPU for EasyOCR")
                except ImportError:
                    gpu_available = False
                    self.logger.info("PyTorch not available for GPU detection. Using CPU")
                
                TextExtractor._reader = easyocr.Reader(['ko', 'en'], gpu=gpu_available, download_enabled=True)
                self.logger.info("EasyOCR reader initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize EasyOCR: {e}")
                error_msg = (
                    f"EasyOCR initialization failed.\n"
                    f"This may be due to Python 3.13 compatibility issues.\n"
                    f"Consider using Python 3.12 or earlier.\n"
                    f"Error details: {e}"
                )
                raise RuntimeError(error_msg)
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
            # Create mss instance in the same thread where it's used
            monitor_offset_x = 0
            monitor_offset_y = 0
            
            with mss.mss() as sct:
                # Capture screen region
                if region:
                    x, y, width, height = region
                    monitor = {"left": x, "top": y, "width": width, "height": height}
                else:
                    monitor = sct.monitors[0]  # All monitors
                    # Store offsets for later use
                    monitor_offset_x = monitor["left"]
                    monitor_offset_y = monitor["top"]
                    
                # Capture screenshot
                screenshot = sct.grab(monitor)
            
            # Convert to numpy array - handle import issues
            if not NUMPY_AVAILABLE:
                # Fallback: convert PIL Image for EasyOCR
                img_pil = Image.frombytes('RGB', (screenshot.width, screenshot.height), 
                                        screenshot.bgra, 'raw', 'BGRX')
                img_rgb = img_pil
            else:
                img = np.array(screenshot)
                # Convert BGRA to RGB
                if cv2:
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
                else:
                    # Manual conversion if cv2 not available
                    img_rgb = img[:, :, [2, 1, 0]]  # BGR to RGB
            
            # Get reader
            reader = self._get_reader()
            
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
                        min_x += monitor_offset_x
                        min_y += monitor_offset_y
                        center_x += monitor_offset_x
                        center_y += monitor_offset_y
                    
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
                  exact_match: bool = False, confidence_threshold: float = 0.5, 
                  confidence: float = None) -> Optional[TextResult]:
        """
        Find specific text in screen region
        
        Args:
            target_text: Text to search for
            region: (x, y, width, height) or None for full screen
            exact_match: If True, requires exact match. If False, allows partial match
            confidence_threshold: Minimum OCR confidence
            confidence: Deprecated parameter, use confidence_threshold instead
            
        Returns:
            TextResult if found, None otherwise
        """
        # Handle backward compatibility - if confidence is passed, use it
        if confidence is not None:
            confidence_threshold = confidence
            
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
            if NUMPY_AVAILABLE:
                dummy_img = np.zeros((100, 100, 3), dtype=np.uint8)
            else:
                # Create dummy image with PIL
                dummy_img = Image.new('RGB', (100, 100), color='black')
            reader.readtext(dummy_img)
            self.logger.info("EasyOCR models preloaded successfully")
        except Exception as e:
            self.logger.error(f"Error preloading models: {e}")