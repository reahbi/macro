"""
Step executor for macro steps
"""

import re
import time
import os
from typing import Dict, Any, Optional, Tuple
import pyautogui
import pyperclip
import random
import math
from core.macro_types import MacroStep, StepType
from config.settings import Settings
from logger.app_logger import get_logger
from core.error_handler import get_error_handler, ErrorCategory

class StepExecutor:
    """Executes individual macro steps"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        self.variables: Dict[str, Any] = {}
        self.error_handler = get_error_handler()
        
        # Execution control flags
        self.stop_execution = False
        self.skip_to_row_end = False
        self.retry_count = 0
        
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
        
        self.logger.info(f"\n{'='*50}")
        self.logger.info(f"단계 실행 시작: {step.name} ({step.step_type.value})")
        self.logger.info(f"{'='*50}")
        
        try:
            result = handler(step)
            self.logger.info(f"단계 실행 완료: {step.name}")
            return result
        except Exception as e:
            # 오류 카테고리 결정
            category = self._determine_error_category(step.step_type)
            
            # 오류 처리
            context = {
                'step': step,
                'step_name': step.name,
                'step_type': step.step_type.value
            }
            
            # 복구 시도
            recovered = self.error_handler.handle_error(e, category, context)
            
            if recovered:
                # 복구 성공 - 재시도
                self.logger.info("오류 복구 성공 - 재시도")
                return handler(step)
            else:
                # 복구 실패 - 오류 전파
                self.logger.error(f"단계 실행 실패: {step.name} - {e}")
                raise
    
    def _determine_error_category(self, step_type: StepType) -> ErrorCategory:
        """단계 타입에 따른 오류 카테고리 결정"""
        if step_type in [StepType.WAIT_IMAGE]:
            return ErrorCategory.IMAGE_SEARCH
        elif step_type in [StepType.WAIT_TEXT]:
            return ErrorCategory.TEXT_SEARCH
        elif step_type in [StepType.MOUSE_CLICK, StepType.MOUSE_MOVE, 
                         StepType.KEYBOARD_TYPE, StepType.KEYBOARD_HOTKEY]:
            return ErrorCategory.EXECUTION
        else:
            return ErrorCategory.GENERAL
            
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
        
    def _prepare_search_text(self, step: MacroStep) -> str:
        """
        텍스트 검색에 사용할 최종 텍스트를 준비합니다.
        변수 치환, 텍스트 정규화, 유효성 검사를 수행합니다.
        
        Args:
            step: 텍스트 검색 단계 객체
            
        Returns:
            str: OCR 검색에 사용할 최종 텍스트
            
        Raises:
            ValueError: 필요한 텍스트나 변수를 찾을 수 없을 때
        """
        # 1. 검색할 텍스트의 원본 소스를 가져옵니다
        search_text = getattr(step, 'search_text', '')
        
        # 2. ${변수명} 형식의 변수 참조 처리
        if search_text:
            # 변수 패턴 체크
            import re
            variable_pattern = r'^\$\{([^}]+)\}$'
            variable_match = re.match(variable_pattern, search_text)
            
            if variable_match:
                # 변수 형식인 경우
                column_name = variable_match.group(1)
                self.logger.debug(f"Found variable reference for column: '{column_name}'")
                
                if not self.variables:
                    raise ValueError(f"엑셀 열 '{column_name}'을(를) 사용하려고 했지만, 현재 엑셀 데이터가 없습니다. "
                                   f"이 단계가 Excel 반복 블록 안에 있는지 확인하세요.")
                elif column_name in self.variables:
                    search_text = str(self.variables[column_name])
                    self.logger.debug(f"Replaced with Excel data from column '{column_name}': {search_text}")
                else:
                    # 열 이름 정규화 후 재시도
                    normalized_column = column_name.strip()
                    found = False
                    for var_name in self.variables.keys():
                        if var_name.strip() == normalized_column:
                            search_text = str(self.variables[var_name])
                            self.logger.debug(f"Found column after normalization: '{var_name}' -> {search_text}")
                            found = True
                            break
                    
                    if not found:
                        available_cols = list(self.variables.keys())
                        raise ValueError(f"엑셀 열 '{column_name}'을(를) 현재 행 데이터에서 찾을 수 없습니다. "
                                       f"사용 가능한 열: {available_cols}")
        
        # 3. 레거시 호환성: search_text가 비어있고 excel_column이 있는 경우
        if not search_text:
            excel_column = getattr(step, 'excel_column', None)
            if excel_column:
                self.logger.debug(f"Legacy: Excel column specified: '{excel_column}'")
                if not self.variables:
                    raise ValueError(f"엑셀 열 '{excel_column}'을(를) 사용하려고 했지만, 현재 엑셀 데이터가 없습니다.")
                elif excel_column in self.variables:
                    search_text = str(self.variables[excel_column])
                    self.logger.debug(f"Legacy: Using Excel data from column '{excel_column}': {search_text}")
                else:
                    available_cols = list(self.variables.keys())
                    raise ValueError(f"엑셀 열 '{excel_column}'을(를) 찾을 수 없습니다. "
                                   f"사용 가능한 열: {available_cols}")
        
        # 4. 검색 텍스트가 여전히 비어있는지 확인
        if not search_text:
            raise ValueError("검색할 텍스트가 지정되지 않았습니다.")
        
        # 5. 변수 치환 (일반 텍스트 내의 ${변수} 패턴)
        search_text = self._substitute_variables(search_text)
        
        # 6. 텍스트 정규화 (전각->반각 변환 등)
        if getattr(step, 'normalize_text', False):
            # 전각 문자를 반각으로 변환
            replacements = {
                '：': ':', '；': ';', '（': '(', '）': ')',
                '［': '[', '］': ']', '｛': '{', '｝': '}',
                '＜': '<', '＞': '>', '，': ',', '。': '.',
                '！': '!', '？': '?', '　': ' '
            }
            for full_width, half_width in replacements.items():
                search_text = search_text.replace(full_width, half_width)
            self.logger.debug(f"Normalized text: {search_text}")
        
        # 7. 양쪽 공백 제거 후 반환
        return search_text.strip()
        
    def _log_search_debug_info(self, search_text: str, exact_match: bool, confidence: float,
                               region: Optional[Tuple[int, int, int, int]], 
                               click_on_found: bool, click_offset: Tuple[int, int]) -> None:
        """텍스트 검색 디버그 정보 로깅"""
        debug_mode = getattr(self.settings, 'debug_mode', False) if hasattr(self, 'settings') else False
        
        if debug_mode:
            self.logger.debug(f"텍스트 검색 시작: '{search_text}'")
            self.logger.debug(f"옵션: exact_match={exact_match}, confidence={confidence}")
            self.logger.debug(f"영역: {region if region else '전체 화면'}")
            self.logger.debug(f"클릭 옵션: click_on_found={click_on_found}, offset={click_offset}")
    
    def _search_text_with_retry(self, search_text: str, region: Optional[Tuple[int, int, int, int]],
                                exact_match: bool, confidence: float, step: MacroStep, 
                                monitor_info: Optional[Dict] = None) -> Optional[Any]:
        """재시도 로직을 포함한 텍스트 검색"""
        max_retries = step.retry_count if hasattr(step, 'retry_count') and step.retry_count > 0 else 3
        retry_delay = 1.0
        
        # 성능 모니터링
        search_start_time = time.time()
        
        result = None
        for attempt in range(max_retries):
            try:
                # 텍스트 검색 수행 (monitor_info 전달)
                result = self._text_extractor.find_text(
                    search_text,
                    region=region,
                    exact_match=exact_match,
                    confidence_threshold=confidence,
                    monitor_info=monitor_info
                )
                
                if result:
                    break  # 찾았으면 루프 종료
                    
            except Exception as e:
                if attempt == max_retries - 1:
                    raise  # 마지막 시도에서는 예외 재발생
                self.logger.warning(f"텍스트 검색 시도 {attempt + 1}/{max_retries} 실패: {e}")
            
            # 재시도 전 대기 (마지막 시도가 아닌 경우)
            if attempt < max_retries - 1 and not result:
                self.logger.info(f"텍스트를 찾지 못했습니다. {retry_delay}초 후 재시도합니다... (시도 {attempt + 1}/{max_retries})")
                time.sleep(retry_delay)
        
        # 성능 경고
        search_elapsed = time.time() - search_start_time
        if search_elapsed > 5.0:
            self.logger.warning(f"텍스트 검색이 {search_elapsed:.2f}초 걸렸습니다. 검색 영역을 좁히는 것을 고려하세요.")
            
        return result
    
    def _perform_text_click(self, result: Any, click_offset: Tuple[int, int], double_click: bool) -> None:
        """텍스트 검색 결과에 대한 클릭 수행"""
        click_x = result.center[0] + click_offset[0]
        click_y = result.center[1] + click_offset[1]
        
        # 사람처럼 자연스러운 마우스 이동 및 클릭
        self._click_with_human_delay(click_x, click_y, double_click=double_click)
        
        if double_click:
            # IME 안정화 및 편집 모드 활성화 대기
            self.logger.info(f"더블클릭 후 IME 안정화 대기 0.3초")
            time.sleep(0.3)
        
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
            
    def _execute_search_action(self, action_config: Dict[str, Any], position: Optional[Tuple[int, int]] = None) -> None:
        """
        Execute search action (found/not found)
        
        Args:
            action_config: Action configuration with 'action' and 'params'
            position: Position where text/image was found (None if not found)
        """
        if not action_config:
            return
            
        action_type = action_config.get("action", "").lower()
        params = action_config.get("params", {})
        
        self.logger.info(f"Executing search action: {action_type}")
        
        # Handle different action types
        if action_type == "클릭" or action_type == "click":
            if position:
                # Click with offset from found position
                offset_x = params.get("offset_x", 0)
                offset_y = params.get("offset_y", 0)
                click_x = position[0] + offset_x
                click_y = position[1] + offset_y
                self.logger.info(f"Clicking at ({click_x}, {click_y})")
                self._click_with_human_delay(click_x, click_y)
            elif "x" in params and "y" in params:
                # Click at absolute position (for not found case)
                click_x = params["x"]
                click_y = params["y"]
                self.logger.info(f"Clicking at absolute position ({click_x}, {click_y})")
                self._click_with_human_delay(click_x, click_y)
                
        elif action_type == "더블클릭" or action_type == "double_click":
            if position:
                # Double click with offset from found position
                offset_x = params.get("offset_x", 0)
                offset_y = params.get("offset_y", 0)
                click_x = position[0] + offset_x
                click_y = position[1] + offset_y
                self.logger.info(f"Double clicking at ({click_x}, {click_y})")
                self._click_with_human_delay(click_x, click_y, double_click=True)
            elif "x" in params and "y" in params:
                # Double click at absolute position (for not found case)
                click_x = params["x"]
                click_y = params["y"]
                self.logger.info(f"Double clicking at absolute position ({click_x}, {click_y})")
                self._click_with_human_delay(click_x, click_y, double_click=True)
                
        elif action_type == "입력" or action_type == "type":
            text = params.get("text", "")
            if text:
                # Substitute variables in text
                text = self._substitute_variables(text)
                self.logger.info(f"Typing text: {text}")
                pyautogui.typewrite(text, interval=0.05)
                
        elif action_type == "계속" or action_type == "continue":
            self.logger.info("Continuing to next step")
            # No special action needed
            
        elif action_type == "중지" or action_type == "stop":
            self.logger.info("Stopping execution")
            # Set flag to stop execution (will be handled by executor)
            self.stop_execution = True
            
        elif action_type == "행_건너뛰기" or action_type == "skip_row":
            self.logger.info("Skipping to end of current Excel row")
            # Set flag to skip to row end (will be handled by macro runner)
            self.skip_to_row_end = True
            
        elif action_type == "재시도" or action_type == "retry":
            max_retries = params.get("max_retries", 3)
            self.logger.info(f"Setting retry count: {max_retries}")
            # This would be handled by the calling method
            self.retry_count = max_retries
            
        # Wait after action if specified
        wait_time = params.get("wait_time", 0)
        if wait_time > 0:
            self.logger.info(f"Waiting {wait_time}s after action")
            time.sleep(wait_time)
            
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
        # 클릭 전 위치
        before_x, before_y = pyautogui.position()
        self.logger.info(f"클릭 전 마우스 위치: ({before_x}, {before_y}) → 목표 위치: ({x}, {y})")
        
        # 먼저 마우스를 자연스럽게 이동
        self._human_like_mouse_move(x, y)
        
        if self.enable_human_movement:
            # 클릭 전 짧은 랜덤 대기
            delay = random.uniform(self.click_delay_min, self.click_delay_max)
            time.sleep(delay)
        
        # 클릭 수행
        if double_click:
            # 더블클릭 간격도 자연스럽게
            self.logger.info(f"더블클릭 수행 중 - 위치: ({x}, {y}), 버튼: {button}")
            pyautogui.click(x, y, button=button)
            time.sleep(random.uniform(0.1, 0.2))
            pyautogui.click(x, y, button=button)
        else:
            self.logger.info(f"클릭 수행 중 - 위치: ({x}, {y}), 버튼: {button}")
            pyautogui.click(x, y, button=button)
        
        # 클릭 후 위치 확인
        after_x, after_y = pyautogui.position()
        self.logger.info(f"클릭 후 마우스 위치: ({after_x}, {after_y})")
            
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
        # 입력 전 IME 준비 대기
        time.sleep(0.1)
        
        # 현재 마우스 위치 (입력 위치로 추정)
        current_x, current_y = pyautogui.position()
        
        text = step.text
        self.logger.info(f"======== 키보드 입력 시작 ========")
        self.logger.info(f"현재 마우스 위치 (입력 위치): ({current_x}, {current_y})")
        self.logger.info(f"원본 텍스트: '{text}'")
        self.logger.info(f"변수 치환 사용: {step.use_variables}")
        self.logger.info(f"사용 가능한 변수: {list(self.variables.keys()) if self.variables else '없음'}")
        
        # Substitute variables if enabled
        if step.use_variables:
            text = self._substitute_variables(text)
            self.logger.info(f"치환된 텍스트: '{text}'")
        
        self.logger.info(f"입력 시작 - 텍스트: '{text}', 간격: {step.interval}초")
        
        # Check if text contains non-ASCII characters (like Korean)
        if any(ord(char) > 127 for char in text):
            self.logger.info("한글 또는 유니코드 문자 감지 - pyperclip을 사용하여 입력")
            # Use clipboard method for non-ASCII text
            pyperclip.copy(text)
            # Small delay to ensure clipboard is ready
            time.sleep(0.05)
            # Paste using Ctrl+V
            pyautogui.hotkey('ctrl', 'v')
        else:
            # Use typewrite for ASCII text
            pyautogui.typewrite(text, interval=step.interval)
        
        # 입력 완료 후 위치
        after_x, after_y = pyautogui.position()
        self.logger.info(f"입력 완료 - 마우스 위치: ({after_x}, {after_y})")
        self.logger.info(f"======== 키보드 입력 완료 ========")
        
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
        
        # 현재 마우스 위치
        current_x, current_y = pyautogui.position()
        self.logger.info(f"스크린샷 시작 - 현재 마우스 위치: ({current_x}, {current_y})")
        
        if self._image_matcher and hasattr(step, 'region') and step.region:
            # Capture specific region
            self.logger.info(f"영역 스크린샷: {step.region}")
            self._image_matcher.capture_region(step.region, filename)
        else:
            # Full screen capture
            screen_width, screen_height = pyautogui.size()
            self.logger.info(f"전체 화면 스크린샷: (0, 0, {screen_width}, {screen_height})")
            pyautogui.screenshot(filename)
            
        self.logger.info(f"스크린샷 저장 완료: {filename}")
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
        
        # Handle search results with new action system
        if location and center:
            # Image found
            self.logger.info(f"Image found at location: {location}")
            
            # Check for new on_found action first
            if hasattr(step, 'on_found') and step.on_found:
                self._execute_search_action(step.on_found, center)
            # Fallback to legacy click behavior
            elif step.click_on_found:
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
        else:
            # Image not found
            self.logger.info("Image not found")
            
            # Check for new on_not_found action
            if hasattr(step, 'on_not_found') and step.on_not_found:
                self._execute_search_action(step.on_not_found, None)
                
        return location
            
    def _execute_text_search(self, step) -> Optional[Tuple[int, int]]:
        """Execute text search and optionally click"""
        try:
            # Dynamic screen stabilization delay
            stabilization_delay = getattr(step, 'screen_delay', 0.3)  # Default 300ms
            if stabilization_delay > 0:
                self.logger.debug(f"Waiting {stabilization_delay}s for screen stabilization")
                time.sleep(stabilization_delay)
            
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
            
            # 1. 새로운 헬퍼 메서드를 사용하여 검색할 텍스트 준비
            search_text = self._prepare_search_text(step)
            
            # 2. 검색 옵션 가져오기
            region = getattr(step, 'region', None)
            if region and isinstance(region, list):
                region = tuple(region)
            monitor_info = getattr(step, 'monitor_info', None)  # Get monitor info
            confidence = getattr(step, 'confidence', 0.5)
            exact_match = getattr(step, 'exact_match', False)
            click_on_found = getattr(step, 'click_on_found', True)
            click_offset = getattr(step, 'click_offset', (0, 0))
            double_click = getattr(step, 'double_click', False)
            
            # 3. 상세 로깅
            self.logger.info(f"======== 텍스트 검색 시작 ========")
            self.logger.info(f"검색 텍스트: '{search_text}'")
            self.logger.info(f"검색 영역: {region if region else '전체 화면'}")
            if monitor_info:
                self.logger.info(f"모니터 정보: {monitor_info.get('name', 'Unknown')} (Index: {monitor_info.get('index', 'N/A')})")
            self.logger.info(f"검색 옵션: exact_match={exact_match}, confidence={confidence}")
            self.logger.info(f"클릭 옵션: click_on_found={click_on_found}, offset={click_offset}, double_click={double_click}")
            
            # Debug logging
            self._log_search_debug_info(search_text, exact_match, confidence, region, click_on_found, click_offset)
            
            # Perform text search with retry logic
            result = self._search_text_with_retry(search_text, region, exact_match, confidence, step, monitor_info)
            
            # Handle search result with new action system
            if result:
                self.logger.info(f"======== 텍스트 검색 성공 ========")
                self.logger.info(f"찾은 텍스트: '{result.text}'")
                self.logger.info(f"텍스트 영역: {result.bbox} (x, y, width, height)")
                self.logger.info(f"텍스트 중심점: {result.center}")
                self.logger.info(f"신뢰도: {result.confidence:.2f}")
                
                # Check for new on_found action first
                if hasattr(step, 'on_found') and step.on_found:
                    self.logger.info("Executing on_found action")
                    self._execute_search_action(step.on_found, result.center)
                # Fallback to legacy click behavior
                elif click_on_found:
                    self.logger.info(f"클릭 설정: True, 오프셋: {click_offset}")
                    click_x = result.center[0] + click_offset[0]
                    click_y = result.center[1] + click_offset[1]
                    self.logger.info(f"계산된 클릭 위치: ({click_x}, {click_y})")
                    self._perform_text_click(result, click_offset, double_click)
                else:
                    self.logger.info(f"클릭 설정: False (클릭하지 않음)")
                    
                return result.center
            else:
                # Text not found after all retries
                self.logger.warning(f"======== 텍스트 검색 실패 ========")
                self.logger.warning(f"찾을 수 없는 텍스트: '{search_text}'")
                
                # Check for new on_not_found action
                if hasattr(step, 'on_not_found') and step.on_not_found:
                    self.logger.info("Executing on_not_found action")
                    self._execute_search_action(step.on_not_found, None)
                    
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