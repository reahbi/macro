"""
중앙 집중식 오류 처리 시스템
모든 오류를 체계적으로 관리하고 복구 전략을 제공
"""

from typing import Optional, Dict, Any, Callable, List
from enum import Enum
import traceback
from datetime import datetime
from logger.app_logger import get_logger

class ErrorCategory(Enum):
    """오류 카테고리"""
    EXCEL = "excel"
    MONITOR = "monitor"
    IMAGE_SEARCH = "image_search"
    TEXT_SEARCH = "text_search"
    EXECUTION = "execution"
    GENERAL = "general"

class ErrorSeverity(Enum):
    """오류 심각도"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class ErrorHandler:
    """중앙 집중식 오류 처리"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.error_history: List[Dict[str, Any]] = []
        self.recovery_strategies = {
            ErrorCategory.EXCEL: self._handle_excel_error,
            ErrorCategory.MONITOR: self._handle_monitor_error,
            ErrorCategory.IMAGE_SEARCH: self._handle_image_error,
            ErrorCategory.TEXT_SEARCH: self._handle_text_error,
            ErrorCategory.EXECUTION: self._handle_execution_error,
        }
        self.max_history_size = 100
    
    def handle_error(self, error: Exception, category: ErrorCategory, 
                    context: Optional[Dict[str, Any]] = None,
                    severity: ErrorSeverity = ErrorSeverity.ERROR) -> bool:
        """
        오류 처리 및 복구 시도
        
        Args:
            error: 발생한 예외
            category: 오류 카테고리
            context: 오류 컨텍스트 정보
            severity: 오류 심각도
            
        Returns:
            bool: 복구 성공 여부
        """
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error': str(error),
            'error_type': type(error).__name__,
            'category': category.value,
            'severity': severity.value,
            'context': context or {},
            'traceback': traceback.format_exc()
        }
        
        # 오류 기록
        self._add_to_history(error_info)
        
        # 로깅
        log_msg = f"[{category.value}] {error}"
        if severity == ErrorSeverity.CRITICAL:
            self.logger.critical(log_msg)
        elif severity == ErrorSeverity.ERROR:
            self.logger.error(log_msg)
        elif severity == ErrorSeverity.WARNING:
            self.logger.warning(log_msg)
        else:
            self.logger.info(log_msg)
        
        # 복구 전략 실행
        if category in self.recovery_strategies:
            try:
                return self.recovery_strategies[category](error, context)
            except Exception as recovery_error:
                self.logger.error(f"복구 전략 실행 실패: {recovery_error}")
                return False
        
        return False
    
    def _add_to_history(self, error_info: Dict[str, Any]):
        """오류 기록 추가"""
        self.error_history.append(error_info)
        
        # 기록 크기 제한
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]
    
    def _handle_excel_error(self, error: Exception, context: Dict) -> bool:
        """Excel 관련 오류 처리"""
        error_str = str(error).lower()
        
        # 인코딩 오류
        if any(keyword in error_str for keyword in ["codec", "decode", "encode", "unicodedecodeerror"]):
            self.logger.info("인코딩 오류 감지 - CP949로 재시도")
            if context and context.get('retry_with_encoding'):
                return True
        
        # 파일 접근 오류
        if "permission denied" in error_str:
            self.logger.error("Excel 파일이 다른 프로그램에서 열려있습니다")
            if context and context.get('suggest_close_file'):
                return True
        
        # 열 이름 오류
        if any(keyword in error_str for keyword in ["keyerror", "column", "not found"]):
            self.logger.info("열 이름 불일치 - 공백 정규화 필요")
            if context and context.get('normalize_columns'):
                return True
        
        return False
    
    def _handle_monitor_error(self, error: Exception, context: Dict) -> bool:
        """모니터 관련 오류 처리"""
        error_str = str(error).lower()
        
        # 좌표 범위 오류
        if any(keyword in error_str for keyword in ["out of range", "bounds", "invalid region"]):
            self.logger.info("좌표가 모니터 범위를 벗어남")
            if context and context.get('use_primary_monitor'):
                return True
        
        # DPI 스케일링 오류
        if "dpi" in error_str or "scale" in error_str:
            self.logger.info("DPI 스케일링 문제 - 1.0으로 폴백")
            if context and context.get('reset_dpi_scale'):
                return True
        
        return False
    
    def _handle_image_error(self, error: Exception, context: Dict) -> bool:
        """이미지 검색 관련 오류 처리"""
        error_str = str(error).lower()
        
        # 파일 없음 오류
        if any(keyword in error_str for keyword in ["filenotfound", "no such file", "cannot find"]):
            self.logger.info("이미지 파일을 찾을 수 없음")
            if context and context.get('search_paths'):
                # 대체 경로 시도
                return True
        
        # 신뢰도 문제
        if "confidence" in error_str or "not found" in error_str:
            self.logger.info("이미지를 찾을 수 없음 - 신뢰도 낮춤")
            if context and context.get('lower_confidence'):
                return True
        
        return False
    
    def _handle_text_error(self, error: Exception, context: Dict) -> bool:
        """OCR 관련 오류 처리"""
        error_str = str(error).lower()
        
        # PaddleOCR 초기화 오류
        if "paddleocr" in error_str or "initialization" in error_str:
            self.logger.info("OCR 초기화 실패 - 재설치 필요")
            if context and context.get('check_installation'):
                from utils.ocr_manager import OCRManager
                ocr_manager = OCRManager()
                if not ocr_manager.is_installed():
                    self.logger.error("OCR이 설치되지 않았습니다")
                return False
        
        # 영역 오류
        if "region" in error_str or "invalid" in error_str:
            self.logger.info("영역 오류 - 전체 화면으로 재시도")
            if context and context.get('use_full_screen'):
                return True
        
        # 텍스트 없음
        if "no text" in error_str or "empty" in error_str:
            self.logger.info("텍스트를 찾을 수 없음 - 전처리 적용")
            if context and context.get('enable_preprocessing'):
                return True
        
        return False
    
    def _handle_execution_error(self, error: Exception, context: Dict) -> bool:
        """실행 관련 오류 처리"""
        error_str = str(error).lower()
        
        # 타임아웃
        if "timeout" in error_str:
            self.logger.info("작업 타임아웃 - 시간 증가")
            if context and context.get('increase_timeout'):
                return True
        
        # 메모리 부족
        if "memory" in error_str:
            self.logger.info("메모리 부족 - 캐시 정리")
            if context and context.get('clear_cache'):
                return True
        
        return False
    
    def get_error_summary(self, category: Optional[ErrorCategory] = None, 
                         limit: int = 10) -> List[Dict[str, Any]]:
        """오류 요약 정보 반환"""
        errors = self.error_history
        
        # 카테고리 필터링
        if category:
            errors = [e for e in errors if e['category'] == category.value]
        
        # 최근 오류만 반환
        return errors[-limit:]
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """오류 통계 반환"""
        stats = {
            'total_errors': len(self.error_history),
            'by_category': {},
            'by_severity': {},
            'recent_errors': self.get_error_summary(limit=5)
        }
        
        # 카테고리별 집계
        for error in self.error_history:
            category = error['category']
            severity = error['severity']
            
            stats['by_category'][category] = stats['by_category'].get(category, 0) + 1
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1
        
        return stats
    
    def clear_history(self):
        """오류 기록 초기화"""
        self.error_history.clear()
        self.logger.info("오류 기록이 초기화되었습니다")

# 전역 오류 처리기
_error_handler = None

def get_error_handler() -> ErrorHandler:
    """전역 오류 처리기 반환"""
    global _error_handler
    if _error_handler is None:
        _error_handler = ErrorHandler()
    return _error_handler