"""
Pytest configuration and fixtures for Excel Macro Automation tests
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any
import pytest
import pandas as pd
from unittest.mock import Mock, patch, MagicMock

# Add src to Python path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Mock EasyOCR for all tests
@pytest.fixture(autouse=True)
def mock_easyocr_globally():
    """Mock EasyOCR to avoid initialization in tests"""
    # Mock the easyocr module itself
    mock_easyocr = MagicMock()
    mock_reader = Mock()
    mock_reader.readtext.return_value = []
    mock_easyocr.Reader.return_value = mock_reader
    
    with patch.dict('sys.modules', {'easyocr': mock_easyocr}):
        yield mock_easyocr

@pytest.fixture(autouse=True)
def mock_vision_dependencies():
    """Mock all vision dependencies to avoid import errors"""
    # Create comprehensive mocks for cv2
    mock_cv2 = MagicMock()
    mock_cv2.__version__ = '4.8.0'
    mock_cv2.imread.return_value = MagicMock()
    mock_cv2.cvtColor.return_value = MagicMock()
    mock_cv2.matchTemplate.return_value = MagicMock()
    mock_cv2.minMaxLoc.return_value = (0, 0.95, (0, 0), (100, 100))
    
    # Mock mss
    mock_mss = MagicMock()
    mock_sct = MagicMock()
    mock_sct.monitors = [{"left": 0, "top": 0, "width": 1920, "height": 1080}]
    mock_sct.grab.return_value = MagicMock()
    mock_mss.mss.return_value.__enter__.return_value = mock_sct
    
    # Mock numpy if needed
    mock_numpy = MagicMock()
    mock_numpy.array.return_value = MagicMock()
    mock_numpy.uint8 = MagicMock()
    
    # Apply all mocks
    patches = {
        'cv2': mock_cv2,
        'mss': mock_mss,
        'numpy': mock_numpy,
        'easyocr': MagicMock()
    }
    
    with patch.dict('sys.modules', patches):
        yield

# PyQt5 setup for GUI tests
@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for GUI tests"""
    try:
        from PyQt5.QtWidgets import QApplication
        import sys
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        yield app
        app.quit()
    except ImportError:
        pytest.skip("PyQt5 not available")

@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create temporary directory for tests"""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)

@pytest.fixture
def isolated_filesystem(tmp_path):
    """Completely isolated file system environment for testing"""
    with patch('pathlib.Path.home', return_value=tmp_path):
        with patch('os.getcwd', return_value=str(tmp_path)):
            with patch('pathlib.Path.cwd', return_value=tmp_path):
                # Create basic directory structure
                (tmp_path / 'macros').mkdir()
                (tmp_path / '.config').mkdir()
                (tmp_path / 'temp').mkdir()
                
                # Set environment variables for Windows
                with patch.dict(os.environ, {
                    'USERPROFILE': str(tmp_path),
                    'APPDATA': str(tmp_path / '.config'),
                    'TEMP': str(tmp_path / 'temp'),
                    'TMP': str(tmp_path / 'temp')
                }):
                    yield tmp_path

@pytest.fixture
def mock_settings():
    """Mock Settings object with default values"""
    settings = Mock()
    
    def mock_get(key, default=None):
        settings_map = {
            "execution.default_delay_ms": 100,
            "ui.window_size": [1280, 720],
            "ui.compact_mode": False,
            "macro.recent_files": [],
            "execution.hotkeys.start": "F9",
            "execution.hotkeys.stop": "Esc",
            "execution.hotkeys.pause": "F10"
        }
        return settings_map.get(key, default)
    
    settings.get.side_effect = mock_get
    settings.set.return_value = None
    settings.save.return_value = None
    return settings

@pytest.fixture
def sample_excel_data():
    """Sample Excel data for testing"""
    return pd.DataFrame({
        '이름': ['김철수', '박영희', '이민수'],
        '이메일': ['kim@example.com', 'park@example.com', 'lee@example.com'],
        '전화번호': ['010-1234-5678', '010-2345-6789', '010-3456-7890'],
        '나이': [25, 30, 28],
        '상태': ['', '', '']
    })

@pytest.fixture
def sample_excel_file(temp_dir, sample_excel_data):
    """Create sample Excel file for testing"""
    excel_path = temp_dir / "test_data.xlsx"
    sample_excel_data.to_excel(excel_path, index=False)
    return excel_path

@pytest.fixture
def mock_encryption_manager():
    """Mock EncryptionManager for testing"""
    manager = Mock()
    manager.encrypt.return_value = b'encrypted_data'
    manager.decrypt.return_value = b'decrypted_data'
    manager.is_key_valid.return_value = True
    manager.generate_key.return_value = b'test_key'
    return manager

@pytest.fixture
def mock_pyautogui():
    """Mock PyAutoGUI for automation tests"""
    with patch('pyautogui') as mock:
        mock.size.return_value = (1920, 1080)
        mock.position.return_value = (960, 540)
        mock.click.return_value = None
        mock.typewrite.return_value = None
        mock.hotkey.return_value = None
        mock.locateOnScreen.return_value = (100, 100, 50, 50)
        yield mock

@pytest.fixture
def mock_vision_systems():
    """Mock vision system components (OpenCV/EasyOCR)"""
    mocks = {}
    
    # Mock ImageMatcher
    with patch('vision.image_matcher.ImageMatcher') as image_mock:
        matcher = Mock()
        from dataclasses import dataclass
        
        @dataclass
        class MatchResult:
            found: bool = True
            confidence: float = 0.95
            location: tuple = (100, 100, 50, 50)
            center: tuple = (125, 125)
            
        matcher.find_image.return_value = MatchResult()
        image_mock.return_value = matcher
        mocks['image_matcher'] = matcher
    
    # Mock TextExtractor
    with patch('vision.text_extractor.TextExtractor') as text_mock:
        extractor = Mock()
        
        @dataclass 
        class TextResult:
            text: str = "sample text"
            confidence: float = 0.9
            bbox: tuple = (100, 100, 200, 50)
            center: tuple = (200, 125)
            
        extractor.find_text.return_value = TextResult()
        text_mock.return_value = extractor
        mocks['text_extractor'] = extractor
        
    yield mocks

@pytest.fixture
def mock_logger():
    """Mock logger for testing"""
    with patch('logger.app_logger.get_logger') as mock:
        logger = Mock()
        mock.return_value = logger
        yield logger

@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset all singleton instances between tests to ensure test isolation"""
    # Reset EncryptionManager singleton
    try:
        from utils.encryption import EncryptionManager
        if hasattr(EncryptionManager, '_instance'):
            EncryptionManager._instance = None
    except ImportError:
        pass
    
    yield
    
    # Clean up after test
    try:
        from utils.encryption import EncryptionManager
        if hasattr(EncryptionManager, '_instance'):
            EncryptionManager._instance = None
    except ImportError:
        pass

@pytest.fixture  
def macro_step_data():
    """Sample macro step data for testing"""
    return {
        "mouse_click": {
            "step_id": "test-step-1",
            "step_type": "mouse_click", 
            "name": "Test Click",
            "description": "Test mouse click",
            "x": 100,
            "y": 200,
            "button": "left",
            "clicks": 1
        },
        "keyboard_type": {
            "step_id": "test-step-2",
            "step_type": "keyboard_type",
            "name": "Test Type", 
            "description": "Test keyboard typing",
            "text": "Hello {{name}}",
            "interval": 0.1
        },
        "if_condition": {
            "step_id": "test-step-3",
            "step_type": "if_condition",
            "name": "Test Condition",
            "condition_type": "image_exists",
            "condition_value": {"image_path": "test.png"},
            "true_steps": [],
            "false_steps": []
        }
    }

# Test data generators
def generate_test_macro_data(step_count: int = 3) -> Dict[str, Any]:
    """Generate test macro data with specified number of steps"""
    from datetime import datetime
    
    return {
        "macro_id": "test-macro-123",
        "name": "Test Macro",
        "description": "Test macro for unit testing",
        "version": "1.0.0", 
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "steps": [
            {
                "step_id": f"step-{i}",
                "step_type": "mouse_click",
                "name": f"Click {i}",
                "x": i * 100,
                "y": i * 100,
                "button": "left"
            } for i in range(step_count)
        ],
        "variables": {"test_var": "test_value"},
        "metadata": {"created_by": "test"}
    }

# Collection of reusable test data
TEST_STEP_TYPES = [
    "mouse_click", "mouse_move", "keyboard_type", "keyboard_hotkey",
    "wait_time", "wait_image", "image_search", "screenshot", 
    "ocr_text", "if_condition", "loop"
]

TEST_COORDINATES = [
    (0, 0), (100, 100), (1920, 1080), (-100, -100),  # Multi-monitor support
    (999999, 999999)  # Extreme values
]

TEST_VALIDATION_CASES = {
    "valid_times": [0.1, 1.0, 10.0, 3600.0],
    "invalid_times": [-1, -0.1, "invalid", None],
    "valid_confidence": [0.0, 0.5, 0.9, 1.0],
    "invalid_confidence": [-0.1, 1.1, 2.0, "invalid"],
    "valid_paths": ["test.png", "C:\\temp\\image.jpg", "/home/user/pic.png"],
    "invalid_paths": ["", None, 123]
}

# Performance test decorators
pytest.performance = pytest.mark.slow

# Custom assertions
def assert_valid_step_data(step_data: Dict[str, Any]):
    """Assert that step data contains required fields"""
    required_fields = ["step_id", "step_type", "name"]
    for field in required_fields:
        assert field in step_data, f"Missing required field: {field}"
        assert step_data[field], f"Empty required field: {field}"

def assert_valid_macro_data(macro_data: Dict[str, Any]):
    """Assert that macro data contains required fields"""
    required_fields = ["macro_id", "name", "steps"]
    for field in required_fields:
        assert field in macro_data, f"Missing required field: {field}"