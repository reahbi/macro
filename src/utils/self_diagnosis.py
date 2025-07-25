"""
Windows 환경 자가 진단 및 복구 도구
"""

import sys
import os
import platform
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any
import importlib
import locale
import ctypes
from datetime import datetime

from logger.app_logger import get_logger

class DiagnosticResult:
    """진단 결과"""
    def __init__(self, category: str, name: str, passed: bool, 
                 message: str, fix_command: str = None):
        self.category = category
        self.name = name
        self.passed = passed
        self.message = message
        self.fix_command = fix_command
        self.timestamp = datetime.now()

class SelfDiagnosis:
    """자가 진단 시스템"""
    
    def __init__(self):
        self.logger = get_logger(__name__)
        self.results: List[DiagnosticResult] = []
        self.fixes_applied = 0
        
    def run_full_diagnosis(self) -> Dict[str, Any]:
        """전체 진단 실행"""
        self.logger.info("=" * 50)
        self.logger.info("자가 진단 시작")
        self.logger.info("=" * 50)
        
        self.results.clear()
        self.fixes_applied = 0
        
        # 진단 항목들
        self._check_python_environment()
        self._check_platform_settings()
        self._check_required_packages()
        self._check_file_system()
        self._check_encoding_settings()
        self._check_permissions()
        self._check_qt_environment()
        self._check_resources()
        
        # 결과 요약
        summary = self._generate_summary()
        
        # 결과 저장
        self._save_results()
        
        return summary
        
    def _check_python_environment(self):
        """Python 환경 검사"""
        # Python 버전
        py_version = sys.version_info
        passed = py_version >= (3, 7)
        self.results.append(DiagnosticResult(
            "Python", 
            "버전 체크",
            passed,
            f"Python {py_version.major}.{py_version.minor}.{py_version.micro}",
            "Python 3.7 이상 설치 필요" if not passed else None
        ))
        
        # 가상환경 확인
        in_venv = hasattr(sys, 'real_prefix') or (
            hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
        )
        self.results.append(DiagnosticResult(
            "Python",
            "가상환경",
            True,  # 가상환경은 선택사항
            "가상환경 사용 중" if in_venv else "시스템 Python 사용 중",
            None
        ))
        
    def _check_platform_settings(self):
        """플랫폼 설정 검사"""
        # Windows 확인
        is_windows = sys.platform == 'win32'
        self.results.append(DiagnosticResult(
            "Platform",
            "운영체제",
            is_windows,
            f"{platform.system()} {platform.release()}",
            None
        ))
        
        # Qt 플랫폼 설정
        qt_platform = os.environ.get('QT_QPA_PLATFORM', '')
        correct_platform = 'windows' if is_windows else 'xcb'
        passed = qt_platform == correct_platform or qt_platform == ''
        
        if not passed and is_windows:
            os.environ['QT_QPA_PLATFORM'] = 'windows'
            self.fixes_applied += 1
            
        self.results.append(DiagnosticResult(
            "Platform",
            "Qt 플랫폼",
            passed,
            f"QT_QPA_PLATFORM={qt_platform}",
            f"QT_QPA_PLATFORM을 '{correct_platform}'로 설정" if not passed else None
        ))
        
    def _check_required_packages(self):
        """필수 패키지 검사"""
        required_packages = {
            'PyQt5': 'PyQt5',
            'pandas': 'pandas',
            'openpyxl': 'openpyxl',
            'numpy': 'numpy',
            'Pillow': 'PIL',
            'opencv-python': 'cv2',
            'pyautogui': 'pyautogui',
            'mss': 'mss',
            'chardet': 'chardet'
        }
        
        optional_packages = {
            'paddleocr': 'paddleocr',
            'paddlepaddle': 'paddle',
            'pynput': 'pynput',
            'scipy': 'scipy',
            'scikit-learn': 'sklearn'
        }
        
        # 필수 패키지 검사
        for package_name, import_name in required_packages.items():
            try:
                importlib.import_module(import_name)
                passed = True
                message = f"{package_name} 설치됨"
            except ImportError:
                passed = False
                message = f"{package_name} 미설치"
                
            self.results.append(DiagnosticResult(
                "Packages",
                package_name,
                passed,
                message,
                f"pip install {package_name}" if not passed else None
            ))
            
        # 선택 패키지 검사
        for package_name, import_name in optional_packages.items():
            try:
                importlib.import_module(import_name)
                message = f"{package_name} 설치됨 (선택사항)"
            except ImportError:
                message = f"{package_name} 미설치 (선택사항)"
                
            self.results.append(DiagnosticResult(
                "Packages",
                package_name,
                True,  # 선택사항은 항상 통과
                message,
                None
            ))
            
    def _check_file_system(self):
        """파일 시스템 검사"""
        # 프로젝트 구조 확인
        project_root = Path(__file__).parent.parent.parent
        required_dirs = [
            'src/core',
            'src/ui',
            'src/automation',
            'src/excel',
            'src/vision',
            'src/utils',
            'resources'
        ]
        
        for dir_path in required_dirs:
            full_path = project_root / dir_path
            exists = full_path.exists()
            
            if not exists:
                # 디렉토리 생성 시도
                try:
                    full_path.mkdir(parents=True, exist_ok=True)
                    self.fixes_applied += 1
                    exists = True
                except:
                    pass
                    
            self.results.append(DiagnosticResult(
                "FileSystem",
                f"디렉토리: {dir_path}",
                exists,
                "존재함" if exists else "없음",
                f"mkdir {dir_path}" if not exists else None
            ))
            
        # 로그 디렉토리
        log_dir = Path.home() / '.excel_macro_automation'
        if not log_dir.exists():
            try:
                log_dir.mkdir(parents=True, exist_ok=True)
                self.fixes_applied += 1
            except:
                pass
                
    def _check_encoding_settings(self):
        """인코딩 설정 검사"""
        # 시스템 인코딩
        sys_encoding = sys.getdefaultencoding()
        self.results.append(DiagnosticResult(
            "Encoding",
            "시스템 인코딩",
            sys_encoding == 'utf-8',
            f"기본 인코딩: {sys_encoding}",
            None
        ))
        
        # UTF-8 모드
        utf8_mode = os.environ.get('PYTHONUTF8', '0')
        if utf8_mode != '1' and sys.platform == 'win32':
            os.environ['PYTHONUTF8'] = '1'
            self.fixes_applied += 1
            
        self.results.append(DiagnosticResult(
            "Encoding",
            "UTF-8 모드",
            utf8_mode == '1',
            f"PYTHONUTF8={utf8_mode}",
            "PYTHONUTF8=1 설정" if utf8_mode != '1' else None
        ))
        
        # 로케일 설정
        try:
            current_locale = locale.getlocale()
            self.results.append(DiagnosticResult(
                "Encoding",
                "로케일",
                True,
                f"로케일: {current_locale}",
                None
            ))
        except:
            self.results.append(DiagnosticResult(
                "Encoding",
                "로케일",
                False,
                "로케일 확인 실패",
                None
            ))
            
    def _check_permissions(self):
        """권한 검사"""
        if sys.platform == 'win32':
            # 관리자 권한 확인
            try:
                is_admin = ctypes.windll.shell32.IsUserAnAdmin()
                self.results.append(DiagnosticResult(
                    "Permissions",
                    "관리자 권한",
                    True,  # 관리자 권한은 선택사항
                    "관리자 권한으로 실행 중" if is_admin else "일반 권한으로 실행 중",
                    None
                ))
            except:
                self.results.append(DiagnosticResult(
                    "Permissions",
                    "관리자 권한",
                    True,
                    "권한 확인 불가",
                    None
                ))
                
    def _check_qt_environment(self):
        """Qt 환경 검사"""
        try:
            from PyQt5.QtCore import QT_VERSION_STR
            from PyQt5.Qt import PYQT_VERSION_STR
            
            self.results.append(DiagnosticResult(
                "Qt",
                "Qt 버전",
                True,
                f"Qt {QT_VERSION_STR}, PyQt {PYQT_VERSION_STR}",
                None
            ))
        except ImportError:
            self.results.append(DiagnosticResult(
                "Qt",
                "Qt 설치",
                False,
                "PyQt5 미설치",
                "pip install PyQt5"
            ))
            
    def _check_resources(self):
        """시스템 리소스 검사"""
        try:
            import psutil
            
            # CPU 사용률
            cpu_percent = psutil.cpu_percent(interval=1)
            self.results.append(DiagnosticResult(
                "Resources",
                "CPU 사용률",
                cpu_percent < 80,
                f"CPU: {cpu_percent}%",
                "높은 CPU 사용률" if cpu_percent >= 80 else None
            ))
            
            # 메모리 사용률
            memory = psutil.virtual_memory()
            self.results.append(DiagnosticResult(
                "Resources",
                "메모리",
                memory.percent < 80,
                f"메모리: {memory.percent}% 사용 중",
                "메모리 부족" if memory.percent >= 80 else None
            ))
            
            # 디스크 공간
            disk = psutil.disk_usage('/')
            self.results.append(DiagnosticResult(
                "Resources",
                "디스크",
                disk.percent < 90,
                f"디스크: {disk.percent}% 사용 중",
                "디스크 공간 부족" if disk.percent >= 90 else None
            ))
            
        except ImportError:
            self.results.append(DiagnosticResult(
                "Resources",
                "리소스 모니터링",
                True,
                "psutil 미설치 (선택사항)",
                None
            ))
            
    def _generate_summary(self) -> Dict[str, Any]:
        """진단 결과 요약"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed
        
        categories = {}
        for result in self.results:
            if result.category not in categories:
                categories[result.category] = {'passed': 0, 'failed': 0}
                
            if result.passed:
                categories[result.category]['passed'] += 1
            else:
                categories[result.category]['failed'] += 1
                
        summary = {
            'total_checks': total,
            'passed': passed,
            'failed': failed,
            'fixes_applied': self.fixes_applied,
            'categories': categories,
            'timestamp': datetime.now().isoformat()
        }
        
        # 콘솔 출력
        self.logger.info("\n" + "=" * 50)
        self.logger.info("진단 결과 요약")
        self.logger.info("=" * 50)
        self.logger.info(f"총 검사 항목: {total}")
        self.logger.info(f"통과: {passed}")
        self.logger.info(f"실패: {failed}")
        self.logger.info(f"자동 수정 적용: {self.fixes_applied}")
        
        if failed > 0:
            self.logger.warning("\n실패한 항목:")
            for result in self.results:
                if not result.passed:
                    self.logger.warning(f"- [{result.category}] {result.name}: {result.message}")
                    if result.fix_command:
                        self.logger.info(f"  수정 방법: {result.fix_command}")
                        
        return summary
        
    def _save_results(self):
        """진단 결과 저장"""
        try:
            results_file = Path.home() / '.excel_macro_automation' / 'diagnosis_results.json'
            results_file.parent.mkdir(exist_ok=True)
            
            data = {
                'timestamp': datetime.now().isoformat(),
                'results': [
                    {
                        'category': r.category,
                        'name': r.name,
                        'passed': r.passed,
                        'message': r.message,
                        'fix_command': r.fix_command
                    }
                    for r in self.results
                ],
                'summary': self._generate_summary()
            }
            
            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"진단 결과 저장 실패: {e}")
            
    def auto_fix(self) -> int:
        """자동 수정 가능한 문제 해결"""
        fixed_count = 0
        
        for result in self.results:
            if not result.passed and result.fix_command:
                if result.fix_command.startswith("pip install"):
                    # pip 설치
                    package = result.fix_command.split()[-1]
                    try:
                        subprocess.run(
                            [sys.executable, '-m', 'pip', 'install', package],
                            check=True,
                            capture_output=True
                        )
                        fixed_count += 1
                        self.logger.info(f"패키지 설치 성공: {package}")
                    except:
                        self.logger.error(f"패키지 설치 실패: {package}")
                        
        return fixed_count

def run_diagnosis():
    """진단 실행 헬퍼 함수 (배치 파일 호환성)"""
    diagnosis = SelfDiagnosis()
    result = diagnosis.run_full_diagnosis()
    
    # 배치 파일에서 호출 시 자동으로 수정 시도
    if result['summary']['failed'] > 0:
        print("\n수정이 필요한 항목이 있습니다.")
        # 배치 파일에서는 입력을 받지 않고 자동 수정
        if 'BATCH_MODE' in os.environ or not sys.stdin.isatty():
            print("자동 수정을 시도합니다...")
            fixed = diagnosis.auto_fix()
            print(f"\n{fixed}개 항목을 자동으로 수정했습니다.")
        else:
            response = input("자동 수정을 시도하시겠습니까? (y/n): ")
            if response.lower() == 'y':
                fixed = diagnosis.auto_fix()
                print(f"\n{fixed}개 항목을 자동으로 수정했습니다.")
            
    return result

if __name__ == "__main__":
    run_diagnosis()