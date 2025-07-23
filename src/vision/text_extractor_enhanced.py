"""
Enhanced text extraction with better Korean OCR support
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

class EnhancedTextExtractor:
    """Enhanced text extractor with better Korean support"""
    
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
            self.sct = None
            self.initialized = True
            
            # OCR 상태 확인
            from utils.ocr_manager import OCRManager
            self.ocr_manager = OCRManager()
            
            if not self.ocr_manager.is_available():
                self.logger.warning("OCR이 아직 설치되지 않았습니다. 텍스트 검색 기능이 제한됩니다.")
    
    def preprocess_image_for_korean(self, img_rgb):
        """Preprocess image to improve Korean OCR accuracy"""
        if not NUMPY_AVAILABLE or cv2 is None:
            return img_rgb
            
        try:
            # Convert to numpy array if needed
            if isinstance(img_rgb, Image.Image):
                img_rgb = np.array(img_rgb)
            
            # 1. Convert to grayscale
            gray = cv2.cvtColor(img_rgb, cv2.COLOR_RGB2GRAY)
            
            # 2. Apply bilateral filter to reduce noise while keeping edges sharp
            # This is especially important for Korean characters
            bilateral = cv2.bilateralFilter(gray, 9, 75, 75)
            
            # 3. Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
            # Improves contrast in different regions
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            enhanced = clahe.apply(bilateral)
            
            # 4. Apply adaptive threshold for better text/background separation
            # Use different methods and compare
            thresh1 = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY, 11, 2)
            thresh2 = cv2.adaptiveThreshold(enhanced, 255, cv2.ADAPTIVE_THRESH_MEAN_C,
                                          cv2.THRESH_BINARY, 11, 2)
            
            # 5. Denoise
            denoised1 = cv2.fastNlMeansDenoising(thresh1, h=10)
            denoised2 = cv2.fastNlMeansDenoising(thresh2, h=10)
            
            # 6. Try morphological operations to connect broken characters
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2,2))
            morph1 = cv2.morphologyEx(denoised1, cv2.MORPH_CLOSE, kernel)
            morph2 = cv2.morphologyEx(denoised2, cv2.MORPH_CLOSE, kernel)
            
            # Convert back to RGB for EasyOCR
            processed_images = [
                cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB),  # Enhanced grayscale
                cv2.cvtColor(morph1, cv2.COLOR_GRAY2RGB),   # Threshold method 1
                cv2.cvtColor(morph2, cv2.COLOR_GRAY2RGB),   # Threshold method 2
                img_rgb  # Original
            ]
            
            return processed_images
            
        except Exception as e:
            self.logger.warning(f"Image preprocessing failed: {e}")
            return [img_rgb]  # Return original if preprocessing fails
    
    def _get_reader(self) -> Optional['easyocr.Reader']:
        """Get or create EasyOCR reader with optimized settings"""
        if not EASYOCR_AVAILABLE or not NUMPY_AVAILABLE:
            error_msg = (
                "Text extraction is not available due to missing dependencies.\n"
                "Required: numpy, opencv-python, easyocr\n"
                "Please install with: pip install numpy opencv-python easyocr"
            )
            self.logger.error(error_msg)
            raise RuntimeError(error_msg)
            
        if EnhancedTextExtractor._reader is None:
            try:
                self.logger.info("Initializing EasyOCR reader with Korean and English support...")
                
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
                
                # Initialize with optimized settings for Korean
                EnhancedTextExtractor._reader = easyocr.Reader(
                    ['ko', 'en'], 
                    gpu=gpu_available, 
                    download_enabled=True,
                    recognizer=True,
                    verbose=False
                )
                self.logger.info("EasyOCR reader initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize EasyOCR: {e}")
                raise RuntimeError(f"EasyOCR initialization failed: {e}")
        return EnhancedTextExtractor._reader
    
    def extract_text_from_region_multi(self, region: Optional[Tuple[int, int, int, int]] = None,
                                     confidence_threshold: float = 0.3) -> List[TextResult]:
        """
        Extract text with multiple preprocessing methods for better accuracy
        
        Args:
            region: (x, y, width, height) or None for full screen
            confidence_threshold: Minimum confidence for text detection (lowered for Korean)
            
        Returns:
            List of TextResult objects (deduplicated)
        """
        try:
            monitor_offset_x = 0
            monitor_offset_y = 0
            
            with mss.mss() as sct:
                # Capture screen region
                if region:
                    x, y, width, height = region
                    monitor = {"left": x, "top": y, "width": width, "height": height}
                else:
                    monitor = sct.monitors[0]  # All monitors
                    monitor_offset_x = monitor["left"]
                    monitor_offset_y = monitor["top"]
                    
                # Capture screenshot
                screenshot = sct.grab(monitor)
            
            # Convert to numpy array
            if not NUMPY_AVAILABLE:
                img_pil = Image.frombytes('RGB', (screenshot.width, screenshot.height), 
                                        screenshot.bgra, 'raw', 'BGRX')
                img_rgb = img_pil
                processed_images = [img_rgb]
            else:
                img = np.array(screenshot)
                # Convert BGRA to RGB
                if cv2:
                    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGRA2RGB)
                else:
                    img_rgb = img[:, :, [2, 1, 0]]  # BGR to RGB
                
                # Get multiple preprocessed versions
                processed_images = self.preprocess_image_for_korean(img_rgb)
            
            # Get reader
            reader = self._get_reader()
            
            # Perform OCR on all versions and collect results
            all_results = {}  # Use dict to deduplicate by text and position
            
            for idx, processed_img in enumerate(processed_images):
                try:
                    # Use different parameters for different preprocessing methods
                    if idx == 0:  # Enhanced grayscale
                        results = reader.readtext(processed_img, width_ths=0.7, height_ths=0.7)
                    elif idx in [1, 2]:  # Thresholded versions
                        results = reader.readtext(processed_img, width_ths=0.8, height_ths=0.8)
                    else:  # Original
                        results = reader.readtext(processed_img)
                    
                    # Process results
                    for bbox, text, confidence in results:
                        if confidence >= confidence_threshold:
                            # Convert bbox format
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
                                min_x += monitor_offset_x
                                min_y += monitor_offset_y
                                center_x += monitor_offset_x
                                center_y += monitor_offset_y
                            
                            # Create unique key for deduplication
                            key = f"{text}_{center_x}_{center_y}"
                            
                            # Keep the result with highest confidence
                            if key not in all_results or all_results[key].confidence < confidence:
                                all_results[key] = TextResult(
                                    text=text,
                                    confidence=confidence,
                                    bbox=(min_x, min_y, width, height),
                                    center=(center_x, center_y)
                                )
                                
                except Exception as e:
                    self.logger.warning(f"OCR failed on preprocessed image {idx}: {e}")
                    continue
            
            # Convert to list and sort by confidence
            text_results = sorted(all_results.values(), key=lambda x: x.confidence, reverse=True)
            
            self.logger.info(f"Extracted {len(text_results)} unique text items from region")
            return text_results
            
        except Exception as e:
            self.logger.error(f"Error extracting text: {e}")
            return []
    
    def find_text_fuzzy(self, target_text: str, region: Optional[Tuple[int, int, int, int]] = None,
                       similarity_threshold: float = 0.7, confidence_threshold: float = 0.3) -> Optional[TextResult]:
        """
        Find text with fuzzy matching for better Korean support
        
        Args:
            target_text: Text to search for
            region: (x, y, width, height) or None for full screen
            similarity_threshold: Minimum similarity score (0-1)
            confidence_threshold: Minimum OCR confidence
            
        Returns:
            TextResult if found, None otherwise
        """
        try:
            # Try to import fuzzy matching library
            try:
                from difflib import SequenceMatcher
                fuzzy_available = True
            except ImportError:
                fuzzy_available = False
                self.logger.warning("Fuzzy matching not available")
            
            # Extract all text with enhanced method
            text_results = self.extract_text_from_region_multi(region, confidence_threshold)
            
            # Normalize target text
            target_lower = target_text.lower().strip()
            target_no_space = target_lower.replace(" ", "")
            
            best_match = None
            best_score = 0.0
            
            for result in text_results:
                text_lower = result.text.lower().strip()
                text_no_space = text_lower.replace(" ", "")
                
                # Exact match
                if text_lower == target_lower or text_no_space == target_no_space:
                    return result
                
                # Calculate similarity scores
                scores = []
                
                # Partial match
                if target_lower in text_lower or text_lower in target_lower:
                    scores.append(0.8)
                if target_no_space in text_no_space or text_no_space in target_no_space:
                    scores.append(0.8)
                
                # Fuzzy match
                if fuzzy_available:
                    # Compare with spaces
                    ratio1 = SequenceMatcher(None, target_lower, text_lower).ratio()
                    scores.append(ratio1)
                    
                    # Compare without spaces (important for Korean)
                    ratio2 = SequenceMatcher(None, target_no_space, text_no_space).ratio()
                    scores.append(ratio2)
                    
                    # Character-level comparison for Korean
                    if len(target_lower) > 0 and len(text_lower) > 0:
                        char_matches = sum(1 for c in target_lower if c in text_lower)
                        char_ratio = char_matches / len(target_lower)
                        scores.append(char_ratio * 0.9)  # Slightly lower weight
                
                # Use best score
                if scores:
                    score = max(scores)
                    if score >= similarity_threshold and score > best_score:
                        best_match = result
                        best_score = score
            
            if best_match:
                self.logger.info(f"Found text '{target_text}' with similarity {best_score:.2f} at {best_match.center}")
            else:
                self.logger.info(f"Text '{target_text}' not found in region")
                
            return best_match
            
        except Exception as e:
            self.logger.error(f"Error in fuzzy text search: {e}")
            return None

# Create a global instance
enhanced_text_extractor = EnhancedTextExtractor()