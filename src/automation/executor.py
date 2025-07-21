"""
Step executor for macro steps
"""

import re
import time
import os
from typing import Dict, Any, Optional, Tuple
import pyautogui
from core.macro_types import MacroStep, StepType
from config.settings import Settings
from logger.app_logger import get_logger

class StepExecutor:
    """Executes individual macro steps"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        self.variables: Dict[str, Any] = {}
        
        # Initialize image matcher
        self._image_matcher = None
        self._init_image_matcher()
        
        # Initialize text extractor
        self._text_extractor = None
        self._init_text_extractor()
        
        # Step handlers mapping
        self._handlers = {
            StepType.MOUSE_CLICK: self._execute_mouse_click,
            StepType.MOUSE_MOVE: self._execute_mouse_move,
            StepType.MOUSE_DRAG: self._execute_mouse_drag,
            StepType.MOUSE_SCROLL: self._execute_mouse_scroll,
            StepType.KEYBOARD_TYPE: self._execute_keyboard_type,
            StepType.KEYBOARD_HOTKEY: self._execute_keyboard_hotkey,
            StepType.WAIT_TIME: self._execute_wait_time,
            StepType.WAIT_IMAGE: self._execute_wait_image,
            StepType.SCREENSHOT: self._execute_screenshot,
            StepType.IMAGE_SEARCH: self._execute_image_search,
            StepType.OCR_TEXT: self._execute_text_search,
            StepType.IF_CONDITION: self._execute_if_condition,
            StepType.LOOP: self._execute_loop,
        }
        
    def _init_image_matcher(self):
        """Initialize image matcher with fallback"""
        try:
            from vision.image_matcher import ImageMatcher
            self._image_matcher = ImageMatcher(self.settings)
            self.logger.info("Using OpenCV-based image matcher")
        except ImportError:
            self.logger.warning("OpenCV not available, using pyautogui fallback")
            self._image_matcher = None
            
    def _init_text_extractor(self):
        """Initialize text extractor"""
        try:
            from vision.text_extractor import TextExtractor
            self._text_extractor = TextExtractor()
            self.logger.info("Using EasyOCR-based text extractor")
        except Exception as e:
            self.logger.warning(f"Text extraction not available: {e}")
            self.logger.warning("Text search features will be disabled")
            self._text_extractor = None
        
    def set_variables(self, variables: Dict[str, Any]):
        """Set variables for template substitution"""
        self.variables = variables
        
    def execute_step(self, step: MacroStep) -> Any:
        """Execute a single step"""
        handler = self._handlers.get(step.step_type)
        if not handler:
            raise NotImplementedError(f"No handler for step type: {step.step_type}")
            
        self.logger.debug(f"Executing step: {step.name} ({step.step_type.value})")
        
        try:
            result = handler(step)
            return result
        except Exception as e:
            self.logger.error(f"Step execution failed: {e}")
            raise
            
    def _substitute_variables(self, text: str) -> str:
        """Substitute variables in text"""
        if not text:
            return text
            
        # Find all {{variable}} patterns
        pattern = r'\{\{(\w+)\}\}'
        
        def replacer(match):
            var_name = match.group(1)
            if var_name in self.variables:
                return str(self.variables[var_name])
            return match.group(0)  # Keep original if not found
            
        return re.sub(pattern, replacer, text)
        
    def _get_absolute_position(self, x: int, y: int, relative_to: str) -> Tuple[int, int]:
        """Convert coordinates to absolute screen position"""
        if relative_to == "screen":
            return x, y
        elif relative_to == "window":
            # TODO: Implement window-relative coordinates
            # For now, treat as screen coordinates
            return x, y
        elif relative_to == "image":
            # TODO: Implement image-relative coordinates
            # For now, treat as screen coordinates
            return x, y
        else:
            return x, y
            
    # Mouse handlers
    
    def _execute_mouse_click(self, step) -> None:
        """Execute mouse click"""
        x, y = self._get_absolute_position(step.x, step.y, step.relative_to)
        
        pyautogui.click(
            x=x,
            y=y,
            clicks=step.clicks,
            interval=step.interval,
            button=step.button.value
        )
        
    def _execute_mouse_move(self, step) -> None:
        """Execute mouse move"""
        x, y = self._get_absolute_position(step.x, step.y, step.relative_to)
        
        if step.duration > 0:
            pyautogui.moveTo(x, y, duration=step.duration)
        else:
            pyautogui.moveTo(x, y)
            
    def _execute_mouse_drag(self, step) -> None:
        """Execute mouse drag"""
        # This would need to be implemented with proper drag coordinates
        # For now, using simple drag
        x, y = self._get_absolute_position(step.x, step.y, step.relative_to)
        pyautogui.dragTo(x, y, duration=step.duration, button=step.button.value)
        
    def _execute_mouse_scroll(self, step) -> None:
        """Execute mouse scroll"""
        pyautogui.scroll(step.clicks)
        
    # Keyboard handlers
    
    def _execute_keyboard_type(self, step) -> None:
        """Execute keyboard typing"""
        text = step.text
        
        # Substitute variables if enabled
        if step.use_variables:
            text = self._substitute_variables(text)
            
        pyautogui.typewrite(text, interval=step.interval)
        
    def _execute_keyboard_hotkey(self, step) -> None:
        """Execute keyboard hotkey"""
        if step.keys:
            pyautogui.hotkey(*step.keys)
            
    # Wait handlers
    
    def _execute_wait_time(self, step) -> None:
        """Execute time wait"""
        time.sleep(step.seconds)
        
    def _execute_wait_image(self, step) -> Optional[Tuple[int, int, int, int]]:
        """Execute wait for image"""
        if self._image_matcher:
            # Use OpenCV-based matcher
            result = self._image_matcher.wait_for_image(
                step.image_path,
                timeout=step.timeout,
                confidence=step.confidence,
                region=step.region
            )
            
            if result.found:
                self.logger.debug(f"Image found at: {result.location}")
                return result.location
            else:
                raise TimeoutError(f"Image not found within {step.timeout} seconds")
        else:
            # Fallback to pyautogui
            start_time = time.time()
            
            while time.time() - start_time < step.timeout:
                try:
                    # Try to locate image
                    location = pyautogui.locateOnScreen(
                        step.image_path,
                        confidence=step.confidence,
                        region=step.region
                    )
                    
                    if location:
                        self.logger.debug(f"Image found at: {location}")
                        return location
                        
                except Exception as e:
                    self.logger.debug(f"Image search error: {e}")
                    
                time.sleep(0.5)  # Check every 500ms
                
            raise TimeoutError(f"Image not found within {step.timeout} seconds")
        
    # Screen handlers
    
    def _execute_screenshot(self, step) -> str:
        """Execute screenshot"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        
        # Create screenshots directory
        screenshots_dir = os.path.join(
            os.path.dirname(__file__), 
            "../../screenshots"
        )
        os.makedirs(screenshots_dir, exist_ok=True)
        
        # Generate filename
        filename = os.path.join(
            screenshots_dir,
            f"screenshot_{timestamp}.png"
        )
        
        if self._image_matcher and hasattr(step, 'region') and step.region:
            # Capture specific region
            self._image_matcher.capture_region(step.region, filename)
        else:
            # Full screen capture
            pyautogui.screenshot(filename)
            
        self.logger.info(f"Screenshot saved: {filename}")
        return filename
        
    def _execute_image_search(self, step) -> Optional[Tuple[int, int, int, int]]:
        """Execute image search and optionally click"""
        location = None
        center = None
        
        if self._image_matcher:
            # Use OpenCV-based matcher
            result = self._image_matcher.find_image(
                step.image_path,
                confidence=step.confidence,
                region=step.region
            )
            
            if result.found:
                self.logger.debug(f"Image found at: {result.location}")
                location = result.location
                center = result.center
            else:
                self.logger.debug("Image not found with OpenCV matcher")
                return None
        else:
            # Fallback to pyautogui
            try:
                location = pyautogui.locateOnScreen(
                    step.image_path,
                    confidence=step.confidence,
                    region=step.region
                )
                if location:
                    center = pyautogui.center(location)
                else:
                    self.logger.debug("Image not found with pyautogui")
                    return None
            except Exception as e:
                self.logger.error(f"Error in image search: {e}")
                return None
        
        # If image was found and click is requested
        if location and center and step.click_after_find:
            # Apply click offset
            click_x = center[0] + step.click_offset[0]
            click_y = center[1] + step.click_offset[1]
            
            self.logger.info(f"Clicking at ({click_x}, {click_y})")
            
            # Perform click
            if step.double_click:
                pyautogui.doubleClick(click_x, click_y)
                self.logger.debug("Performed double click")
            else:
                pyautogui.click(click_x, click_y)
                self.logger.debug("Performed single click")
                
        return location
            
    def _execute_text_search(self, step) -> Optional[Tuple[int, int]]:
        """Execute text search and optionally click"""
        if not self._text_extractor:
            # OCR이 설치되지 않은 경우 사용자에게 알림
            from utils.ocr_manager import OCRManager
            ocr_manager = OCRManager()
            
            if not ocr_manager.is_installed():
                self.logger.error("텍스트 검색 기능을 사용하려면 OCR 구성요소가 필요합니다.")
                raise RuntimeError(
                    "텍스트 검색 기능을 사용하려면 OCR 구성요소가 필요합니다.\n"
                    "프로그램을 재시작하면 자동으로 설치됩니다."
                )
            else:
                self.logger.error("OCR이 설치되었지만 초기화에 실패했습니다.")
                raise RuntimeError("OCR 초기화 실패. 프로그램을 재시작해주세요.")
            
        # Handle different step types
        if hasattr(step, 'search_text'):
            # DynamicTextSearchStep
            search_text = step.search_text
            region = getattr(step, 'search_region', None)
            confidence = getattr(step, 'confidence_threshold', 0.7)
            click_on_found = getattr(step, 'click_on_found', True)
            fail_if_not_found = getattr(step, 'fail_if_not_found', True)
            mask_in_logs = getattr(step, 'mask_in_logs', False)
        else:
            # Legacy OCRTextStep
            search_text = getattr(step, 'text', step.search_text)
            region = getattr(step, 'region', None)
            confidence = getattr(step, 'confidence', 0.7)
            click_on_found = getattr(step, 'click_after_find', True)
            fail_if_not_found = False
            mask_in_logs = False
            
            # Handle Excel column reference
            if hasattr(step, 'excel_column') and step.excel_column and step.excel_column in self.variables:
                search_text = str(self.variables[step.excel_column])
            
        if not search_text:
            raise ValueError("No search text specified")
            
        # Replace variables in search text
        search_text = self._substitute_variables(search_text)
        
        # Log search (mask if sensitive)
        if mask_in_logs:
            self.logger.info("Searching for text: [MASKED]")
        else:
            self.logger.info(f"Searching for text: {search_text}")
        
        # Find text on screen
        result = self._text_extractor.find_text(
            search_text,
            region=region,
            confidence=confidence
        )
        
        if result:
            if mask_in_logs:
                self.logger.info("Text found at: [MASKED LOCATION]")
            else:
                self.logger.info(f"Text found at: {result.center}")
            
            # Click if requested
            if click_on_found:
                click_offset = getattr(step, 'click_offset', (0, 0))
                click_x = result.center[0] + click_offset[0]
                click_y = result.center[1] + click_offset[1]
                
                # Perform click
                if hasattr(step, 'double_click') and step.double_click:
                    pyautogui.doubleClick(click_x, click_y)
                    self.logger.debug(f"Double clicked at: ({click_x}, {click_y})")
                else:
                    pyautogui.click(click_x, click_y)
                    self.logger.debug(f"Clicked at: ({click_x}, {click_y})")
                
            return result.center
        else:
            # Handle not found case
            if fail_if_not_found:
                error_msg = f"Text not found: {search_text if not mask_in_logs else '[MASKED]'}"
                raise ValueError(error_msg)
            else:
                self.logger.warning(f"Text not found: {search_text if not mask_in_logs else '[MASKED]'}")
                return None
    
    # Flow control handlers
    
    def _execute_if_condition(self, step) -> bool:
        """Execute if condition and run appropriate branch"""
        condition_result = False
        
        try:
            # Evaluate condition based on type
            if step.condition_type == "image_exists":
                # Check if image exists on screen
                image_path = step.condition_value.get('image_path', '')
                confidence = step.condition_value.get('confidence', 0.9)
                region = step.condition_value.get('region')
                
                if self._image_matcher:
                    result = self._image_matcher.find_image(
                        image_path,
                        confidence=confidence,
                        region=region
                    )
                    condition_result = result.found if result else False
                else:
                    # Fallback to pyautogui
                    try:
                        location = pyautogui.locateOnScreen(
                            image_path,
                            confidence=confidence,
                            region=region
                        )
                        condition_result = location is not None
                    except:
                        condition_result = False
                        
            elif step.condition_type == "text_exists":
                # Check if text exists on screen
                search_text = step.condition_value.get('text', '')
                exact_match = step.condition_value.get('exact_match', False)
                region = step.condition_value.get('region')
                
                # Substitute variables in search text
                search_text = self._substitute_variables(search_text)
                
                if search_text:
                    result = self._text_extractor.find_text(
                        search_text,
                        region=region,
                        exact_match=exact_match,
                        confidence_threshold=0.5
                    )
                    condition_result = result is not None
                else:
                    condition_result = False
                    
            elif step.condition_type in ["variable_equals", "variable_contains", "variable_greater", "variable_less"]:
                # Variable comparison conditions
                variable_name = step.condition_value.get('variable', '')
                compare_value = step.condition_value.get('compare_value', '')
                
                # Get variable value
                variable_value = self.variables.get(variable_name, '')
                
                # Substitute variables in compare value
                compare_value = self._substitute_variables(compare_value)
                
                # Perform comparison
                if step.condition_type == "variable_equals":
                    condition_result = str(variable_value) == str(compare_value)
                elif step.condition_type == "variable_contains":
                    condition_result = str(compare_value) in str(variable_value)
                elif step.condition_type == "variable_greater":
                    try:
                        condition_result = float(variable_value) > float(compare_value)
                    except (ValueError, TypeError):
                        # If not numeric, do string comparison
                        condition_result = str(variable_value) > str(compare_value)
                elif step.condition_type == "variable_less":
                    try:
                        condition_result = float(variable_value) < float(compare_value)
                    except (ValueError, TypeError):
                        # If not numeric, do string comparison
                        condition_result = str(variable_value) < str(compare_value)
                        
            self.logger.info(f"Condition '{step.condition_type}' evaluated to: {condition_result}")
            
            # Execute appropriate branch
            if condition_result:
                # Execute true branch steps
                for nested_step in step.true_steps:
                    if nested_step.enabled:
                        self.execute_step(nested_step)
            else:
                # Execute false branch steps
                for nested_step in step.false_steps:
                    if nested_step.enabled:
                        self.execute_step(nested_step)
                        
            return condition_result
            
        except Exception as e:
            self.logger.error(f"Error evaluating condition: {e}")
            # On error, execute false branch
            for nested_step in step.false_steps:
                if nested_step.enabled:
                    self.execute_step(nested_step)
            return False
        
    def _execute_loop(self, step) -> None:
        """Execute loop"""
        # TODO: Implement loop execution
        # This would need to interact with the main engine
        pass