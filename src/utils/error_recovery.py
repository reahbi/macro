"""
Windows 환경 자동 오류 복구 시스템
"""

import sys
import os
import traceback
import json
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
import subprocess
import chardet
import locale
from datetime import datetime
from logger.app_logger import get_logger

class ErrorPattern:
    """오류 패턴 정의"""
    def __init__(self, name: str, patterns: List[str], 
                 recovery_func: Callable, priority: int = 0):
        self.name = name
        self.patterns = patterns
        self.recovery_func = recovery_func
        self.priority = priority
        self.success_count = 0
        self.fail_count = 0

class AutoErrorRecovery:
    """자동 오류 복구 매니저"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.error_patterns: List[ErrorPattern] = []
        self.recovery_history = []
        self.max_history = 100
        self._init_error_patterns()
        
    def _init_error_patterns(self):
        """오류 패턴 초기화"""
        # 인코딩 오류
        self.register_pattern(
            "encoding_error",
            ["UnicodeDecodeError", "UnicodeEncodeError", "codec can't decode"],
            self._fix_encoding_error,
            priority=10
        )
        
        # 임포트 오류
        self.register_pattern(
            "import_error",
            ["ImportError", "ModuleNotFoundError", "No module named"],
            self._fix_import_error,
            priority=9
        )
        
        # 파일 경로 오류
        self.register_pattern(
            "path_error",
            ["FileNotFoundError", "WindowsError", "cannot find the path"],
            self._fix_path_error,
            priority=8
        )
        
        # 권한 오류
        self.register_pattern(
            "permission_error",
            ["PermissionError", "Access is denied", "Permission denied"],
            self._fix_permission_error,
            priority=7
        )
        
        # Qt 관련 오류
        self.register_pattern(
            "qt_error",
            ["QPixmap", "QTimer", "AttributeError.*Qt", "Qt platform"],
            self._fix_qt_error,
            priority=6
        )
        
        # 메모리/리소스 오류
        self.register_pattern(
            "resource_error",
            ["MemoryError", "OSError.*resources", "Too many open files"],
            self._fix_resource_error,
            priority=5
        )
        
        # Excel 저장 관련 오류
        self.register_pattern(
            "excel_save_error",
            ["No data to save", "데이터가 없습니다", "저장할 데이터가 없습니다"],
            self._fix_excel_save_error,
            priority=4
        )
        
    def register_pattern(self, name: str, patterns: List[str], 
                        recovery_func: Callable, priority: int = 0):
        """오류 패턴 등록"""
        pattern = ErrorPattern(name, patterns, recovery_func, priority)
        self.error_patterns.append(pattern)
        self.error_patterns.sort(key=lambda x: x.priority, reverse=True)
        
    def analyze_error(self, error: Exception, tb_str: str = None) -> Optional[ErrorPattern]:
        """오류 분석 및 패턴 매칭"""
        error_str = str(error)
        error_type = type(error).__name__
        
        if tb_str is None:
            tb_str = traceback.format_exc()
            
        full_error = f"{error_type}: {error_str}\n{tb_str}"
        
        # 패턴 매칭
        for pattern in self.error_patterns:
            for p in pattern.patterns:
                if p in full_error or p in error_type:
                    self.logger.info(f"오류 패턴 감지: {pattern.name}")
                    return pattern
                    
        return None
        
    def try_recover(self, error: Exception, context: Dict[str, Any] = None) -> bool:
        """오류 복구 시도"""
        try:
            tb_str = traceback.format_exc()
            pattern = self.analyze_error(error, tb_str)
            
            if not pattern:
                self.logger.warning(f"알 수 없는 오류: {error}")
                return False
                
            self.logger.info(f"복구 시도: {pattern.name}")
            
            # 복구 함수 실행
            success = pattern.recovery_func(error, context or {})
            
            # 기록 저장
            self._save_recovery_history(pattern.name, error, success)
            
            if success:
                pattern.success_count += 1
                self.logger.info(f"복구 성공: {pattern.name}")
            else:
                pattern.fail_count += 1
                self.logger.error(f"복구 실패: {pattern.name}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"복구 중 오류 발생: {e}")
            return False
            
    def _fix_encoding_error(self, error: Exception, context: Dict) -> bool:
        """인코딩 오류 수정"""
        try:
            # Windows 기본 인코딩 설정
            if sys.platform == 'win32':
                # UTF-8 모드 활성화
                os.environ['PYTHONUTF8'] = '1'
                
                # 로케일 설정
                try:
                    locale.setlocale(locale.LC_ALL, 'Korean_Korea.utf8')
                except:
                    locale.setlocale(locale.LC_ALL, 'Korean_Korea.949')
                    
            # 파일 인코딩 감지 및 변환
            if 'file_path' in context:
                file_path = context['file_path']
                if os.path.exists(file_path):
                    # 인코딩 감지
                    with open(file_path, 'rb') as f:
                        raw_data = f.read()
                        result = chardet.detect(raw_data)
                        encoding = result['encoding']
                        
                    self.logger.info(f"감지된 인코딩: {encoding}")
                    
                    # UTF-8로 변환
                    if encoding and encoding.lower() != 'utf-8':
                        text = raw_data.decode(encoding, errors='replace')
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(text)
                        self.logger.info(f"파일을 UTF-8로 변환: {file_path}")
                        
            return True
            
        except Exception as e:
            self.logger.error(f"인코딩 수정 실패: {e}")
            return False
            
    def _fix_import_error(self, error: Exception, context: Dict) -> bool:
        """임포트 오류 수정"""
        try:
            error_msg = str(error)
            
            # 모듈명 추출
            if "No module named" in error_msg:
                module_name = error_msg.split("'")[1].split('.')[0]
                
                # 알려진 모듈 매핑
                module_map = {
                    'cv2': 'opencv-python',
                    'PIL': 'Pillow',
                    'sklearn': 'scikit-learn',
                    'paddleocr': 'paddleocr',
                    'paddle': 'paddlepaddle',
                    'pynput': 'pynput',
                    'mss': 'mss',
                    'chardet': 'chardet'
                }
                
                install_name = module_map.get(module_name, module_name)
                
                # pip 설치 시도
                self.logger.info(f"모듈 설치 시도: {install_name}")
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', install_name],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    self.logger.info(f"모듈 설치 성공: {install_name}")
                    return True
                else:
                    self.logger.error(f"모듈 설치 실패: {result.stderr}")
                    
            return False
            
        except Exception as e:
            self.logger.error(f"임포트 수정 실패: {e}")
            return False
            
    def _fix_path_error(self, error: Exception, context: Dict) -> bool:
        """경로 오류 수정"""
        try:
            # Windows 경로 정규화
            if 'file_path' in context:
                file_path = context['file_path']
                
                # 경로 정규화
                normalized = os.path.normpath(file_path)
                normalized = normalized.replace('/', '\\') if sys.platform == 'win32' else normalized
                
                # 디렉토리 생성
                dir_path = os.path.dirname(normalized)
                if dir_path and not os.path.exists(dir_path):
                    os.makedirs(dir_path, exist_ok=True)
                    self.logger.info(f"디렉토리 생성: {dir_path}")
                    
                context['file_path'] = normalized
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"경로 수정 실패: {e}")
            return False
            
    def _fix_permission_error(self, error: Exception, context: Dict) -> bool:
        """권한 오류 수정"""
        try:
            if sys.platform == 'win32':
                # 관리자 권한 확인
                import ctypes
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                
                if not is_admin:
                    self.logger.warning("관리자 권한이 필요합니다")
                    # 권한 상승 요청은 사용자 상호작용이 필요하므로 False 반환
                    return False
                    
            return False
            
        except Exception as e:
            self.logger.error(f"권한 수정 실패: {e}")
            return False
            
    def _fix_qt_error(self, error: Exception, context: Dict) -> bool:
        """Qt 관련 오류 수정"""
        try:
            error_str = str(error)
            
            # QTimer 오류
            if "QTimer" in error_str and "currentTime" in error_str:
                self.logger.info("QTimer.currentTime() -> QTime.currentTime() 오류 감지")
                # 이미 코드에서 수정했으므로 재시작 권장
                return False
                
            # QPixmap null 오류
            if "QPixmap" in error_str and "null pixmap" in error_str:
                self.logger.info("Null pixmap 오류 감지")
                # 이미지 파일 확인 필요
                return False
                
            # Qt 플랫폼 오류
            if "qt.qpa.plugin" in error_str:
                os.environ['QT_QPA_PLATFORM'] = 'windows' if sys.platform == 'win32' else 'xcb'
                self.logger.info("Qt 플랫폼 설정 완료")
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Qt 오류 수정 실패: {e}")
            return False
            
    def _fix_resource_error(self, error: Exception, context: Dict) -> bool:
        """리소스 오류 수정"""
        try:
            # 가비지 컬렉션 강제 실행
            import gc
            gc.collect()
            
            # Windows 리소스 정리
            if sys.platform == 'win32':
                # 임시 파일 정리
                temp_dir = Path(os.environ.get('TEMP', '/tmp'))
                for f in temp_dir.glob('tmp*'):
                    try:
                        if f.is_file() and (datetime.now() - datetime.fromtimestamp(f.stat().st_mtime)).days > 1:
                            f.unlink()
                    except:
                        pass
                        
            self.logger.info("리소스 정리 완료")
            return True
            
        except Exception as e:
            self.logger.error(f"리소스 정리 실패: {e}")
            return False
    
    def _fix_excel_save_error(self, error: Exception, context: Dict) -> bool:
        """Excel 저장 오류 수정"""
        try:
            self.logger.info("Excel 저장 오류 감지 - Excel 데이터 없이 실행 중")
            
            # 이 오류는 정상적인 상황 (Excel 없이 실행)이므로 무시
            # 향후 engine.py에서 이미 수정했으므로 발생하지 않아야 함
            
            # 컨텍스트에 excel_manager가 있으면 상태 확인
            if 'excel_manager' in context:
                excel_mgr = context['excel_manager']
                if hasattr(excel_mgr, '_current_data') and excel_mgr._current_data is None:
                    self.logger.info("Excel 데이터 없음 확인 - 정상 동작")
                    return True
                    
            # 오류 메시지 확인
            if "No data to save" in str(error):
                self.logger.info("Excel 없이 매크로 실행 중 - 저장 건너뜀")
                return True
                
            return False
            
        except Exception as e:
            self.logger.error(f"Excel 저장 오류 처리 실패: {e}")
            return False
            
    def _save_recovery_history(self, pattern_name: str, error: Exception, success: bool):
        """복구 기록 저장"""
        record = {
            'timestamp': datetime.now().isoformat(),
            'pattern': pattern_name,
            'error_type': type(error).__name__,
            'error_msg': str(error),
            'success': success
        }
        
        self.recovery_history.append(record)
        
        # 최대 기록 수 유지
        if len(self.recovery_history) > self.max_history:
            self.recovery_history = self.recovery_history[-self.max_history:]
            
        # 파일로 저장
        try:
            history_file = Path.home() / '.excel_macro_automation' / 'error_recovery_history.json'
            history_file.parent.mkdir(exist_ok=True)
            
            with open(history_file, 'w', encoding='utf-8') as f:
                json.dump(self.recovery_history, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"복구 기록 저장 실패: {e}")
            
    def get_statistics(self) -> Dict[str, Any]:
        """복구 통계 반환"""
        stats = {
            'patterns': [],
            'total_recoveries': len(self.recovery_history),
            'success_rate': 0
        }
        
        success_count = sum(1 for r in self.recovery_history if r['success'])
        if self.recovery_history:
            stats['success_rate'] = success_count / len(self.recovery_history) * 100
            
        for pattern in self.error_patterns:
            stats['patterns'].append({
                'name': pattern.name,
                'success': pattern.success_count,
                'fail': pattern.fail_count,
                'rate': pattern.success_count / (pattern.success_count + pattern.fail_count) * 100 
                        if (pattern.success_count + pattern.fail_count) > 0 else 0
            })
            
        return stats

# 전역 인스턴스
_recovery_manager = None

def get_recovery_manager() -> AutoErrorRecovery:
    """복구 매니저 인스턴스 반환"""
    global _recovery_manager
    if _recovery_manager is None:
        _recovery_manager = AutoErrorRecovery()
    return _recovery_manager