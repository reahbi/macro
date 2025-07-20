"""
Integration tests for dynamic text search functionality
Tests OCR-based text search within specified screen regions
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import numpy as np

from core.macro_types import DynamicTextSearchStep, MouseClickStep
from automation.step_executor import StepExecutor
from vision.text_extractor import TextExtractor, TextResult
from vision.screen_capture import ScreenCapture


@pytest.mark.integration
class TestDynamicTextSearch:
    """Test dynamic text search and click functionality"""
    
    @pytest.fixture
    def step_executor(self):
        """Create StepExecutor instance"""
        return StepExecutor()
    
    @pytest.fixture
    def mock_text_extractor(self):
        """Mock TextExtractor for testing"""
        mock_extractor = Mock(spec=TextExtractor)
        
        # Create mock text results
        def create_text_result(text, x, y, width=100, height=30):
            return TextResult(
                text=text,
                confidence=0.95,
                bbox=(x, y, x + width, y + height),
                center=(x + width // 2, y + height // 2)
            )
        
        # Mock find_text to return different results based on input
        def mock_find_text(text, region=None, confidence=0.7):
            text_locations = {
                "홍길동": create_text_result("홍길동", 200, 300),
                "김철수": create_text_result("김철수", 400, 500),
                "P001": create_text_result("P001", 100, 200),
                "혈액검사": create_text_result("혈액검사", 600, 400),
                "정상": create_text_result("정상", 800, 400)
            }
            return text_locations.get(text, None)
        
        mock_extractor.find_text.side_effect = mock_find_text
        return mock_extractor
    
    @pytest.fixture
    def mock_screen_capture(self):
        """Mock ScreenCapture for testing"""
        mock_capture = Mock(spec=ScreenCapture)
        
        # Create mock screenshot
        mock_screenshot = np.zeros((1080, 1920, 3), dtype=np.uint8)
        mock_capture.capture_region.return_value = mock_screenshot
        mock_capture.capture_screen.return_value = mock_screenshot
        
        return mock_capture
    
    def test_dynamic_text_search_basic(self, step_executor, mock_text_extractor, mock_screen_capture):
        """Test basic dynamic text search"""
        
        # Create dynamic text search step
        search_step = DynamicTextSearchStep(
            name="환자명 찾기",
            search_text="홍길동",
            search_region=(100, 100, 1000, 800),  # x, y, width, height
            click_on_found=True
        )
        
        # Execute with mocks
        with patch('vision.text_extractor.TextExtractor', return_value=mock_text_extractor):
            with patch('vision.screen_capture.ScreenCapture', return_value=mock_screen_capture):
                with patch('pyautogui.click') as mock_click:
                    
                    result = step_executor.execute_step(search_step, {})
                    
                    # Verify execution
                    assert result['success'] is True
                    assert 'text_found' in result
                    assert result['text_found'] is True
                    
                    # Verify click was performed at text center
                    mock_click.assert_called_once_with(x=250, y=315)  # Center of "홍길동"
    
    def test_dynamic_text_search_with_variables(self, step_executor, mock_text_extractor, mock_screen_capture):
        """Test dynamic text search with Excel variable substitution"""
        
        # Create step with variable
        search_step = DynamicTextSearchStep(
            name="동적 환자 검색",
            search_text="{{patient_name}}",
            search_region=(0, 0, 1920, 1080),
            click_on_found=True
        )
        
        # Set variables from Excel
        variables = {
            'patient_name': '김철수',
            'patient_id': 'P001'
        }
        
        with patch('vision.text_extractor.TextExtractor', return_value=mock_text_extractor):
            with patch('vision.screen_capture.ScreenCapture', return_value=mock_screen_capture):
                with patch('pyautogui.click') as mock_click:
                    
                    result = step_executor.execute_step(search_step, variables)
                    
                    assert result['success'] is True
                    # Verify searched for substituted text
                    mock_text_extractor.find_text.assert_called_with(
                        '김철수',
                        region=(0, 0, 1920, 1080),
                        confidence=0.7
                    )
                    # Verify clicked on "김철수" location
                    mock_click.assert_called_once_with(x=450, y=515)
    
    def test_dynamic_text_not_found(self, step_executor, mock_text_extractor, mock_screen_capture):
        """Test behavior when text is not found"""
        
        search_step = DynamicTextSearchStep(
            name="존재하지 않는 텍스트",
            search_text="없는텍스트",
            search_region=(0, 0, 1920, 1080),
            click_on_found=True,
            fail_if_not_found=True
        )
        
        # Mock text not found
        mock_text_extractor.find_text.return_value = None
        
        with patch('vision.text_extractor.TextExtractor', return_value=mock_text_extractor):
            with patch('vision.screen_capture.ScreenCapture', return_value=mock_screen_capture):
                with patch('pyautogui.click') as mock_click:
                    
                    result = step_executor.execute_step(search_step, {})
                    
                    assert result['success'] is False
                    assert 'text_found' in result
                    assert result['text_found'] is False
                    # No click should occur
                    mock_click.assert_not_called()
    
    def test_region_specification_ui_integration(self):
        """Test region specification UI integration"""
        
        # Create step with region
        search_step = DynamicTextSearchStep(
            name="영역 지정 테스트",
            search_text="검색어",
            search_region=(100, 200, 800, 600)
        )
        
        # Verify region is properly stored
        assert search_step.search_region == (100, 200, 800, 600)
        
        # Test region update
        search_step.update_search_region((200, 300, 900, 700))
        assert search_step.search_region == (200, 300, 900, 700)
    
    def test_ocr_confidence_threshold(self, step_executor, mock_text_extractor, mock_screen_capture):
        """Test OCR confidence threshold handling"""
        
        # Create step with custom confidence
        search_step = DynamicTextSearchStep(
            name="신뢰도 테스트",
            search_text="혈액검사",
            confidence_threshold=0.9,
            click_on_found=True
        )
        
        with patch('vision.text_extractor.TextExtractor', return_value=mock_text_extractor):
            with patch('vision.screen_capture.ScreenCapture', return_value=mock_screen_capture):
                with patch('pyautogui.click'):
                    
                    result = step_executor.execute_step(search_step, {})
                    
                    # Verify confidence was passed
                    mock_text_extractor.find_text.assert_called_with(
                        '혈액검사',
                        region=None,
                        confidence=0.9
                    )


@pytest.mark.integration
class TestMultiMonitorSupport:
    """Test multi-monitor environment support"""
    
    @pytest.fixture
    def mock_multi_monitor_setup(self):
        """Mock multi-monitor configuration"""
        import screeninfo
        
        # Mock monitors
        monitor1 = Mock()
        monitor1.x = 0
        monitor1.y = 0
        monitor1.width = 1920
        monitor1.height = 1080
        monitor1.is_primary = True
        
        monitor2 = Mock()
        monitor2.x = 1920
        monitor2.y = 0
        monitor2.width = 1920
        monitor2.height = 1080
        monitor2.is_primary = False
        
        return [monitor1, monitor2]
    
    def test_multi_monitor_coordinate_translation(self, mock_multi_monitor_setup):
        """Test coordinate translation across monitors"""
        
        with patch('screeninfo.get_monitors', return_value=mock_multi_monitor_setup):
            from utils.monitor_utils import MonitorUtils
            
            monitor_utils = MonitorUtils()
            
            # Test primary monitor coordinates
            primary_coords = monitor_utils.to_absolute_coords(500, 500, monitor_index=0)
            assert primary_coords == (500, 500)
            
            # Test secondary monitor coordinates
            secondary_coords = monitor_utils.to_absolute_coords(500, 500, monitor_index=1)
            assert secondary_coords == (2420, 500)  # 1920 + 500
    
    def test_dpi_scaling_correction(self):
        """Test DPI scaling correction for high-DPI displays"""
        
        from utils.monitor_utils import MonitorUtils
        
        # Mock high-DPI settings
        with patch('ctypes.windll.shcore.GetScaleFactorForDevice', return_value=150):  # 150% scaling
            monitor_utils = MonitorUtils()
            
            # Test coordinate scaling
            scaled_coords = monitor_utils.apply_dpi_scaling(100, 100)
            assert scaled_coords == (150, 150)  # 100 * 1.5
            
            # Test reverse scaling
            unscaled_coords = monitor_utils.remove_dpi_scaling(150, 150)
            assert unscaled_coords == (100, 100)
    
    def test_primary_monitor_fallback(self):
        """Test fallback to primary monitor when specified monitor unavailable"""
        
        # Mock single monitor setup
        single_monitor = Mock()
        single_monitor.x = 0
        single_monitor.y = 0
        single_monitor.width = 1920
        single_monitor.height = 1080
        single_monitor.is_primary = True
        
        with patch('screeninfo.get_monitors', return_value=[single_monitor]):
            from utils.monitor_utils import MonitorUtils
            
            monitor_utils = MonitorUtils()
            
            # Try to use non-existent monitor 2
            coords = monitor_utils.to_absolute_coords(500, 500, monitor_index=2)
            # Should fallback to primary monitor
            assert coords == (500, 500)


@pytest.mark.integration
class TestAdvancedFeatureIntegration:
    """Test integration of advanced features"""
    
    def test_ocr_text_search_with_multi_monitor(self):
        """Test OCR text search across multiple monitors"""
        
        # Create search step for secondary monitor
        search_step = DynamicTextSearchStep(
            name="보조 모니터 검색",
            search_text="결과",
            monitor_index=1,  # Secondary monitor
            click_on_found=True
        )
        
        # Mock monitor setup
        with patch('screeninfo.get_monitors') as mock_monitors:
            monitor1 = Mock(x=0, y=0, width=1920, height=1080, is_primary=True)
            monitor2 = Mock(x=1920, y=0, width=1920, height=1080, is_primary=False)
            mock_monitors.return_value = [monitor1, monitor2]
            
            # Verify monitor-specific search region
            expected_region = (1920, 0, 1920, 1080)  # Secondary monitor region
            assert search_step.get_absolute_search_region() == expected_region
    
    def test_dynamic_region_selection_ui(self):
        """Test dynamic region selection UI workflow"""
        
        from ui.dialogs.region_selector import RegionSelectorDialog
        
        # Mock the dialog
        with patch('ui.dialogs.region_selector.RegionSelectorDialog') as mock_dialog_class:
            mock_dialog = Mock()
            mock_dialog.exec_.return_value = 1  # Accepted
            mock_dialog.get_selected_region.return_value = (100, 200, 800, 600)
            mock_dialog_class.return_value = mock_dialog
            
            # Create dialog and get region
            dialog = RegionSelectorDialog()
            result = dialog.exec_()
            region = dialog.get_selected_region()
            
            assert result == 1
            assert region == (100, 200, 800, 600)