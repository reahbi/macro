"""
오류 자동 복구 데코레이터
"""

import functools
import traceback
from typing import Any, Callable, Optional
from logger.app_logger import get_logger
from utils.error_recovery import get_recovery_manager

logger = get_logger(__name__)

def auto_recover(retry_count: int = 1, context_func: Optional[Callable] = None):
    """
    오류 자동 복구 데코레이터
    
    Args:
        retry_count: 재시도 횟수
        context_func: 컨텍스트 정보를 제공하는 함수
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            recovery_manager = get_recovery_manager()
            
            for attempt in range(retry_count + 1):
                try:
                    return func(*args, **kwargs)
                    
                except Exception as e:
                    last_error = e
                    logger.error(f"{func.__name__} 실행 중 오류 (시도 {attempt + 1}/{retry_count + 1}): {e}")
                    
                    if attempt < retry_count:
                        # 컨텍스트 수집
                        context = {}
                        if context_func:
                            try:
                                context = context_func(*args, **kwargs)
                            except:
                                pass
                                
                        # 자동 복구 시도
                        if recovery_manager.try_recover(e, context):
                            logger.info(f"오류 복구 성공, 재시도합니다...")
                            continue
                            
                    # 복구 실패 또는 마지막 시도
                    if attempt == retry_count:
                        logger.error(f"{func.__name__} 최종 실패: {e}")
                        logger.error(traceback.format_exc())
                        
            raise last_error
            
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, **kwargs) -> tuple[bool, Any]:
    """
    안전한 함수 실행
    
    Returns:
        (성공여부, 결과값 또는 오류)
    """
    recovery_manager = get_recovery_manager()
    
    try:
        result = func(*args, **kwargs)
        return True, result
        
    except Exception as e:
        logger.error(f"안전 실행 중 오류: {e}")
        
        # 복구 시도
        if recovery_manager.try_recover(e):
            try:
                # 복구 후 재시도
                result = func(*args, **kwargs)
                return True, result
            except Exception as retry_error:
                logger.error(f"재시도 실패: {retry_error}")
                return False, retry_error
                
        return False, e

class ErrorContext:
    """오류 컨텍스트 관리자"""
    
    def __init__(self, operation_name: str, **context):
        self.operation_name = operation_name
        self.context = context
        self.recovery_manager = get_recovery_manager()
        
    def __enter__(self):
        logger.debug(f"{self.operation_name} 시작")
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            logger.error(f"{self.operation_name} 중 오류 발생: {exc_val}")
            
            # 복구 시도
            if self.recovery_manager.try_recover(exc_val, self.context):
                logger.info(f"{self.operation_name} 오류 복구 성공")
                return True  # 예외 전파 방지
                
        return False  # 예외 전파

# 자주 사용되는 컨텍스트 함수들
def file_context(*args, **kwargs) -> dict:
    """파일 관련 컨텍스트"""
    context = {}
    
    # 첫 번째 인자가 파일 경로인 경우가 많음
    if args and isinstance(args[0], str):
        context['file_path'] = args[0]
        
    # kwargs에서 파일 경로 찾기
    for key in ['file_path', 'path', 'filename']:
        if key in kwargs:
            context['file_path'] = kwargs[key]
            break
            
    return context

def excel_context(*args, **kwargs) -> dict:
    """엑셀 관련 컨텍스트"""
    context = file_context(*args, **kwargs)
    
    # ExcelManager 인스턴스 찾기
    if args and hasattr(args[0], 'file_path'):
        context['excel_file'] = getattr(args[0], 'file_path', None)
        
    return context

def ui_context(*args, **kwargs) -> dict:
    """UI 관련 컨텍스트"""
    context = {}
    
    # QWidget 인스턴스 찾기
    if args:
        for arg in args:
            if hasattr(arg, 'windowTitle'):
                context['window'] = arg
                context['window_title'] = arg.windowTitle()
                break
                
    return context