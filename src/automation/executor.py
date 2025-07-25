"""
Step executor for macro steps
"""

import re
import time
import os
from typing import Dict, Any, Optional, Tuple
import pyautogui
import random
import math
from core.macro_types import MacroStep, StepType
from config.settings import Settings
from logger.app_logger import get_logger

class StepExecutor:
    """Executes individual macro steps"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        self.variables: Dict[str, Any] = {}
        
        # Human-like movement settings from config
        human_config = settings.get("execution", {}).get("human_like_movement", {})
        self.enable_human_movement = human_config.get("enabled", True)
        self.min_move_duration = human_config.get("min_move_duration", 0.3)
        self.max_move_duration = human_config.get("max_move_duration", 1.5)
        self.click_delay_min = human_config.get("click_delay_min", 0.1)
        self.click_delay_max = human_config.get("click_delay_max", 0.3)
        
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
            StepType.EXCEL_ROW_START: self._execute_excel_row_start,
            StepType.EXCEL_ROW_END: self._execute_excel_row_end,
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
            from vision.text_extractor_paddle import PaddleTextExtractor
            self._text_extractor = PaddleTextExtractor()
            self.logger.info("Using PaddleOCR-based text extractor")
        except Exception as e:
            self.logger.error(f"PaddleOCR initialization failed: {e}")
            self.logger.error("Text search features will be disabled. Please install PaddleOCR.")
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
            
        self.logger.debug(f"Substituting variables in text: {text}")
        self.logger.debug(f"Variables dict: {self.variables}")
            
        # Find all ${variable} patterns (common in Excel templates)
        pattern = r'\$\{([^}]+)\}'  # Changed to handle Korean characters
        
        def replacer(match):
            var_name = match.group(1)
            self.logger.debug(f"Trying to replace variable: {var_name}")
            if var_name in self.variables:
                value = str(self.variables[var_name])
                self.logger.debug(f"Replaced {var_name} with {value}")
                return value
            else:
                self.logger.warning(f"Variable {var_name} not found in {list(self.variables.keys())}")
            return match.group(0)  # Keep original if not found
            
        result = re.sub(pattern, replacer, text)
        
        # Also support {{variable}} pattern for backward compatibility
        pattern2 = r'\{\{([^}]+)\}\}'
        result = re.sub(pattern2, replacer, result)
        
        return result
        
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
            
    def _human_like_mouse_move(self, x: int, y: int, duration: Optional[float] = None) -> None:
        """
        사람처럼 자연스러운 마우스 움직임
        
        Args:
            x: 목표 X 좌표
            y: 목표 Y 좌표
            duration: 이동 시간 (None이면 거리 기반 자동 계산)
        """
        if not self.enable_human_movement:
            # 사람 같은 움직임 비활성화 시 즉시 이동
            pyautogui.moveTo(x, y)
            return
            
        # 현재 마우스 위치
        current_x, current_y = pyautogui.position()
        
        # 거리 계산
        distance = math.sqrt((x - current_x)**2 + (y - current_y)**2)
        
        if duration is None:
            # 거리에 따른 자동 duration 계산
            # 가까운 거리는 빠르게, 먼 거리는 천천히
            duration = min(self.max_move_duration, 
                         max(self.min_move_duration, distance / 500))
            
            # 약간의 랜덤성 추가
            duration += random.uniform(-0.1, 0.1)
            duration = max(self.min_move_duration, duration)
        
        # 베지어 곡선을 사용한 자연스러운 이동
        # pyautogui의 tween 함수 사용
        tween_functions = [
            pyautogui.easeInOutQuad,
            pyautogui.easeInQuad,
            pyautogui.easeOutQuad,
        ]
        
        # 랜덤하게 이동 스타일 선택
        tween = random.choice(tween_functions)
        
        # 마우스 이동
        try:
            pyautogui.moveTo(x, y, duration=duration, tween=tween)
            
            # 아주 짧은 랜덤 딜레이 (마우스가 도착한 후 잠시 멈춤)
            time.sleep(random.uniform(0.05, 0.15))
            
        except Exception as e:
            self.logger.warning(f"Human-like mouse move failed: {e}, falling back to instant move")
            pyautogui.moveTo(x, y)
    
    def _click_with_human_delay(self, x: int, y: int, button: str = 'left', 
                               double_click: bool = False) -> None:
        """
        사람처럼 자연스러운 클릭 (이동 후 짧은 대기 포함)
        
        Args:
            x: 클릭할 X 좌표
            y: 클릭할 Y 좌표
            button: 마우스 버튼 ('left', 'right', 'middle')
            double_click: 더블클릭 여부
        """
        # 먼저 마우스를 자연스럽게 이동
        self._human_like_mouse_move(x, y)
        
        if self.enable_human_movement:
            # 클릭 전 짧은 랜덤 대기
            delay = random.uniform(self.click_delay_min, self.click_delay_max)
            time.sleep(delay)
        
        # 클릭 수행
        if double_click:
            # 더블클릭 간격도 자연스럽게
            pyautogui.click(x, y, button=button)
            time.sleep(random.uniform(0.1, 0.2))
            pyautogui.click(x, y, button=button)
        else:
            pyautogui.click(x, y, button=button)
            
        # 클릭 후 아주 짧은 대기
        if self.enable_human_movement:
            time.sleep(random.uniform(0.05, 0.1))
            
    # Mouse handlers
    
    def _execute_mouse_click(self, step) -> None:
        """Execute mouse click"""
        x, y = self._get_absolute_position(step.x, step.y, step.relative_to)
        
        # 단일 클릭인 경우 사람처럼 자연스럽게
        if step.clicks == 1:
            self._click_with_human_delay(x, y, button=step.button.value)
        else:
            # 여러 번 클릭인 경우 먼저 이동 후 클릭
            self._human_like_mouse_move(x, y)
            
            if self.enable_human_movement:
                time.sleep(random.uniform(self.click_delay_min, self.click_delay_max))
            
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
            # 사용자가 지정한 duration이 있으면 그대로 사용
            self._human_like_mouse_move(x, y, duration=step.duration)
        else:
            # 사용자가 지정하지 않았으면 자동 계산된 자연스러운 이동
            self._human_like_mouse_move(x, y)
            
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
        self.logger.info(f"Keyboard type step - Original text: {text}")
        self.logger.info(f"Use variables: {step.use_variables}")
        self.logger.info(f"Available variables: {list(self.variables.keys()) if self.variables else 'None'}")
        
        # Substitute variables if enabled
        if step.use_variables:
            text = self._substitute_variables(text)
            self.logger.info(f"After substitution: {text}")
            
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
        if location and center and step.click_on_found:
            # Apply click offset
            click_x = center[0] + step.click_offset[0]
            click_y = center[1] + step.click_offset[1]
            
            self.logger.info(f"Clicking at ({click_x}, {click_y})")
            
            # Perform click with human-like movement
            self._click_with_human_delay(click_x, click_y, double_click=step.double_click)
            
            if step.double_click:
                self.logger.debug("Performed double click with human-like movement")
            else:
                self.logger.debug("Performed single click with human-like movement")
                
        return location
            
    def _execute_text_search(self, step) -> Optional[Tuple[int, int]]:
        """Execute text search and optionally click"""
        try:
            # Screen stabilization delay
            time.sleep(0.5)  # 500ms delay for screen to stabilize
            
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
            
            # Initialize default values
            search_text = ""
            region = None
            confidence = 0.7
            click_on_found = True
            fail_if_not_found = True
            mask_in_logs = False
            click_offset = (0, 0)
            double_click = False
            
            # Handle different step types
            step_class_name = step.__class__.__name__
            
            if step_class_name == "DynamicTextSearchStep":
                # DynamicTextSearchStep attributes
                search_text = getattr(step, 'search_text', '')
                region = getattr(step, 'search_region', None)
                confidence = getattr(step, 'confidence_threshold', 0.7)
                click_on_found = getattr(step, 'click_on_found', True)
                fail_if_not_found = getattr(step, 'fail_if_not_found', True)
                mask_in_logs = getattr(step, 'mask_in_logs', False)
                click_offset = getattr(step, 'click_offset', (0, 0))
                double_click = getattr(step, 'double_click', False)
            elif step_class_name == "TextSearchStep":
                # TextSearchStep attributes - this is the one with excel_column
                search_text = getattr(step, 'search_text', '')
                region = getattr(step, 'region', None)
                confidence = getattr(step, 'confidence', 0.5)
                click_on_found = getattr(step, 'click_on_found', True)
                click_offset = getattr(step, 'click_offset', (0, 0))
                double_click = getattr(step, 'double_click', False)
                fail_if_not_found = True  # TextSearchStep doesn't have this attribute
                mask_in_logs = False  # TextSearchStep doesn't have this attribute
                
                # Handle Excel column reference for TextSearchStep
                excel_column = getattr(step, 'excel_column', None)
                if excel_column and (not search_text or search_text == ''):
                    # Debug logging
                    self.logger.debug(f"Excel column specified: '{excel_column}'")
                    self.logger.debug(f"Available variables: {list(self.variables.keys()) if self.variables else 'None'}")
                    
                    if not self.variables:
                        raise ValueError(f"엑셀 열 '{excel_column}'을(를) 사용하려고 했지만, 현재 엑셀 데이터가 없습니다. "
                                       f"이 단계가 Excel 반복 블록 안에 있는지 확인하세요.")
                    elif excel_column in self.variables:
                        search_text = str(self.variables[excel_column])
                        self.logger.debug(f"Using Excel data from column '{excel_column}': {search_text}")
                    else:
                        available_cols = list(self.variables.keys())
                        raise ValueError(f"엑셀 열 '{excel_column}'을(를) 현재 행 데이터에서 찾을 수 없습니다. "
                                       f"사용 가능한 열: {available_cols}")
            else:
                # Legacy or unknown step type
                search_text = getattr(step, 'text', getattr(step, 'search_text', ''))
                region = getattr(step, 'region', None)
                confidence = getattr(step, 'confidence', 0.7)
                click_on_found = getattr(step, 'click_on_found', True)
                fail_if_not_found = False
                mask_in_logs = False
                
            if not search_text:
                # Provide more helpful error message
                if hasattr(step, 'excel_column') and step.excel_column:
                    excel_column = step.excel_column
                    if excel_column not in self.variables:
                        available_cols = list(self.variables.keys()) if self.variables else []
                        raise ValueError(f"Excel column '{excel_column}' not found in row data. Available columns: {available_cols}")
                    else:
                        raise ValueError(f"Excel column '{excel_column}' has empty value")
                else:
                    raise ValueError("No search text specified")
                
            # Replace variables in search text
            search_text = self._substitute_variables(search_text)
            
            # Text preprocessing for special characters
            normalize_text = getattr(step, 'normalize_text', False)
            if normalize_text:
                # Full-width to half-width conversion
                search_text = search_text.replace('：', ':')  # Full-width colon
                search_text = search_text.replace('；', ';')  # Full-width semicolon
                search_text = search_text.replace('（', '(')  # Full-width left parenthesis
                search_text = search_text.replace('）', ')')  # Full-width right parenthesis
                search_text = search_text.replace('［', '[')  # Full-width left bracket
                search_text = search_text.replace('］', ']')  # Full-width right bracket
                search_text = search_text.replace('｛', '{')  # Full-width left brace
                search_text = search_text.replace('｝', '}')  # Full-width right brace
                search_text = search_text.replace('＜', '<')  # Full-width less than
                search_text = search_text.replace('＞', '>')  # Full-width greater than
                search_text = search_text.replace('，', ',')  # Full-width comma
                search_text = search_text.replace('。', '.')  # Full-width period
                search_text = search_text.replace('！', '!')  # Full-width exclamation
                search_text = search_text.replace('？', '?')  # Full-width question mark
                search_text = search_text.replace('　', ' ')  # Full-width space
                self.logger.debug(f"Normalized text: {search_text}")
            
            # Trim whitespace
            search_text = search_text.strip()
            
            # Log search (mask if sensitive)
            if mask_in_logs:
                self.logger.info("Searching for text: [MASKED]")
            else:
                self.logger.info(f"Searching for text: {search_text}")
            
            # Debug logging
            debug_mode = False
            if hasattr(self, 'settings') and hasattr(self.settings, 'debug_mode'):
                debug_mode = self.settings.debug_mode
            
            if debug_mode:
                self.logger.debug(f"텍스트 검색 시작: '{search_text}'")
                self.logger.debug(f"옵션: exact_match={getattr(step, 'exact_match', False)}, confidence={confidence}")
                self.logger.debug(f"영역: {region if region else '전체 화면'}")
                self.logger.debug(f"클릭 옵션: click_on_found={click_on_found}, offset={click_offset if 'click_offset' in locals() else '(0,0)'}")
            
            # Retry logic
            max_retries = step.retry_count if hasattr(step, 'retry_count') and step.retry_count > 0 else 3
            retry_delay = 1.0  # 1 second between retries
            
            # Performance monitoring
            search_start_time = time.time()
            
            result = None
            for attempt in range(max_retries):
                # Find text on screen
                exact_match = getattr(step, 'exact_match', False)
                
                try:
                    # Find text using text extractor
                    result = self._text_extractor.find_text(
                        search_text,
                        region=region,
                        exact_match=exact_match,
                        confidence_threshold=confidence
                    )
                    
                    if result:
                        break  # Found it, exit retry loop
                        
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise  # Re-raise on last attempt
                    self.logger.warning(f"텍스트 검색 시도 {attempt + 1}/{max_retries} 실패: {e}")
                
                # Wait before retry (except on last attempt)
                if attempt < max_retries - 1 and not result:
                    self.logger.info(f"텍스트를 찾지 못했습니다. {retry_delay}초 후 재시도합니다... (시도 {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
            
            # Performance monitoring - log if search took too long
            search_elapsed = time.time() - search_start_time
            if search_elapsed > 5.0:
                self.logger.warning(f"텍스트 검색이 {search_elapsed:.2f}초 걸렸습니다. 검색 영역을 좁히는 것을 고려하세요.")
            
            if result:
                if mask_in_logs:
                    self.logger.info("Text found at: [MASKED LOCATION]")
                else:
                    self.logger.info(f"Text found at: {result.center}")
                
                # Click if requested
                if click_on_found:
                    click_x = result.center[0] + click_offset[0]
                    click_y = result.center[1] + click_offset[1]
                    
                    # Perform click with human-like movement
                    self._click_with_human_delay(click_x, click_y, double_click=double_click)
                    
                    if double_click:
                        self.logger.debug(f"Double clicked at: ({click_x}, {click_y}) with human-like movement")
                    else:
                        self.logger.debug(f"Clicked at: ({click_x}, {click_y}) with human-like movement")
                    
                return result.center
            else:
                # Handle not found case after all retries
                if fail_if_not_found:
                    error_msg = f"Text not found after {max_retries} attempts: {search_text if not mask_in_logs else '[MASKED]'}"
                    raise ValueError(error_msg)
                else:
                    self.logger.warning(f"Text not found after {max_retries} attempts: {search_text if not mask_in_logs else '[MASKED]'}")
                    return None
                    
        except Exception as e:
            self.logger.error(f"Text search execution failed: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            # Re-raise the exception with more context
            raise RuntimeError(f"텍스트 검색 중 오류 발생: {str(e)}")
    
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
        
    def _execute_excel_row_start(self, step) -> None:
        """Execute Excel row start"""
        # Excel row start is a control flow step
        # The actual loop handling is done in the engine
        self.logger.debug(f"Excel row start: {step.name}")
        pass
        
    def _execute_excel_row_end(self, step) -> None:
        """Execute Excel row end"""
        # Excel row end is a control flow step
        # The actual completion marking is done in the engine
        self.logger.debug(f"Excel row end: {step.name}")
        pass