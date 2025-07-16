#!/usr/bin/env python3
"""
Integration tests for image capture and search functionality
"""

import sys
import os
from pathlib import Path
import pytest
import tempfile
import numpy as np
from PIL import Image
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt, QRect, QPoint

# Add parent directories to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_helpers import GUITestContext
from vision.image_matcher import ImageMatcher
from vision.screen_capture import ScreenCapture
from core.macro_types import WaitImageStep, StepType
from config.settings import Settings


class TestImageCapture:
    """Test image capture and search functionality"""
    
    @pytest.fixture
    def app(self):
        """Create QApplication for tests"""
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app
        
    @pytest.fixture
    def temp_image_dir(self):
        """Create temporary directory for test images"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        # Cleanup
        import shutil
        shutil.rmtree(temp_dir)
        
    @pytest.fixture
    def test_image(self, temp_image_dir):
        """Create a test image"""
        # Create a simple test image
        img_array = np.zeros((100, 100, 3), dtype=np.uint8)
        # Add some distinctive features
        img_array[20:40, 20:80] = [255, 0, 0]  # Red rectangle
        img_array[60:80, 30:70] = [0, 255, 0]  # Green rectangle
        
        img = Image.fromarray(img_array)
        img_path = Path(temp_image_dir) / "test_image.png"
        img.save(img_path)
        
        return str(img_path)
        
    def test_screen_capture_region(self, app):
        """Test capturing a specific screen region"""
        with GUITestContext(app) as ctx:
            capture = ScreenCapture()
            
            # Define test region
            region = QRect(100, 100, 200, 200)
            
            # Capture region
            screenshot = capture.capture_region(region)
            
            # Verify capture
            assert screenshot is not None
            assert screenshot.shape[0] == 200  # Height
            assert screenshot.shape[1] == 200  # Width
            assert screenshot.shape[2] == 3    # RGB channels
            
    def test_image_matcher_initialization(self, app):
        """Test ImageMatcher initialization"""
        with GUITestContext(app) as ctx:
            settings = Settings()
            matcher = ImageMatcher(settings)
            
            # Verify initialization
            assert matcher is not None
            assert hasattr(matcher, 'find_image')
            assert hasattr(matcher, 'wait_for_image')
            
    def test_find_image_in_screenshot(self, app, test_image):
        """Test finding an image within a screenshot"""
        with GUITestContext(app) as ctx:
            settings = Settings()
            matcher = ImageMatcher(settings)
            
            # Create a larger screenshot with our test image embedded
            screenshot = np.zeros((300, 300, 3), dtype=np.uint8)
            # Load test image
            test_img = np.array(Image.open(test_image))
            # Place test image in screenshot
            screenshot[50:150, 50:150] = test_img
            
            # Find the image
            location = matcher.find_image(test_image, screenshot=screenshot)
            
            # Verify location found
            assert location is not None
            assert location[0] >= 45  # Allow small margin
            assert location[0] <= 55
            assert location[1] >= 45
            assert location[1] <= 55
            
    def test_image_not_found(self, app, test_image):
        """Test behavior when image is not found"""
        with GUITestContext(app) as ctx:
            settings = Settings()
            matcher = ImageMatcher(settings)
            
            # Create empty screenshot
            screenshot = np.zeros((300, 300, 3), dtype=np.uint8)
            
            # Try to find image
            location = matcher.find_image(test_image, screenshot=screenshot)
            
            # Should return None
            assert location is None
            
    def test_confidence_threshold(self, app, test_image):
        """Test image matching with different confidence thresholds"""
        with GUITestContext(app) as ctx:
            settings = Settings()
            matcher = ImageMatcher(settings)
            
            # Create screenshot with slightly modified test image
            screenshot = np.zeros((300, 300, 3), dtype=np.uint8)
            test_img = np.array(Image.open(test_image))
            # Add noise to test image
            noisy_img = test_img + np.random.randint(-20, 20, test_img.shape, dtype=np.int16)
            noisy_img = np.clip(noisy_img, 0, 255).astype(np.uint8)
            screenshot[50:150, 50:150] = noisy_img
            
            # High confidence - might not find
            location_high = matcher.find_image(test_image, screenshot=screenshot, confidence=0.95)
            
            # Low confidence - should find
            location_low = matcher.find_image(test_image, screenshot=screenshot, confidence=0.7)
            
            # Low confidence should be more likely to find the image
            assert location_low is not None
            
    def test_wait_image_step_configuration(self, app, test_image):
        """Test WaitImageStep configuration"""
        with GUITestContext(app) as ctx:
            # Create wait image step
            step = WaitImageStep()
            step.name = "이미지 대기 테스트"
            step.image_path = test_image
            step.timeout_seconds = 5
            step.confidence_threshold = 0.8
            
            # Verify configuration
            assert step.step_type == StepType.WAIT_IMAGE
            assert step.image_path == test_image
            assert step.timeout_seconds == 5
            assert step.confidence_threshold == 0.8
            
            # Test serialization
            step_dict = step.to_dict()
            assert step_dict['step_type'] == StepType.WAIT_IMAGE.value
            assert step_dict['image_path'] == test_image
            assert step_dict['timeout_seconds'] == 5
            assert step_dict['confidence_threshold'] == 0.8
            
    def test_roi_selection(self, app):
        """Test Region of Interest (ROI) selection"""
        with GUITestContext(app) as ctx:
            # Test ROI configuration
            roi = {
                'x': 100,
                'y': 200,
                'width': 300,
                'height': 400
            }
            
            # Create step with ROI
            step = WaitImageStep()
            step.region = roi
            
            # Verify ROI configuration
            assert step.region == roi
            assert step.region['x'] == 100
            assert step.region['y'] == 200
            assert step.region['width'] == 300
            assert step.region['height'] == 400
            
    def test_multiple_image_search(self, app, temp_image_dir):
        """Test searching for multiple instances of an image"""
        with GUITestContext(app) as ctx:
            settings = Settings()
            matcher = ImageMatcher(settings)
            
            # Create small pattern
            pattern = np.zeros((20, 20, 3), dtype=np.uint8)
            pattern[5:15, 5:15] = [255, 255, 0]  # Yellow square
            
            pattern_path = Path(temp_image_dir) / "pattern.png"
            Image.fromarray(pattern).save(pattern_path)
            
            # Create screenshot with multiple instances
            screenshot = np.zeros((200, 200, 3), dtype=np.uint8)
            # Place pattern in multiple locations
            screenshot[20:40, 20:40] = pattern
            screenshot[100:120, 50:70] = pattern
            screenshot[60:80, 150:170] = pattern
            
            # Find all instances (this would require extending ImageMatcher)
            # For now, just verify we can find at least one
            location = matcher.find_image(str(pattern_path), screenshot=screenshot)
            assert location is not None


def run_tests():
    """Run tests standalone"""
    pytest.main([__file__, "-v"])


if __name__ == "__main__":
    run_tests()