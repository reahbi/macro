#!/usr/bin/env python3
"""
오류 자동 복구 기능이 포함된 실행 스크립트
"""

import sys
import os
from pathlib import Path
import traceback
import time
from datetime import datetime

# 프로젝트 경로 설정
project_root = Path(__file__).parent.absolute()
src_path = project_root / "src"

# Python 경로에 추가
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

def setup_environment():
    """환경 설정"""
    # Windows 환경 설정
    if sys.platform == 'win32':
        os.environ['QT_QPA_PLATFORM'] = 'windows'
        os.environ['PYTHONUTF8'] = '1'
    elif sys.platform.startswith('linux'):
        os.environ['QT_QPA_PLATFORM'] = 'xcb'
        if 'DISPLAY' not in os.environ:
            os.environ['DISPLAY'] = ':0'

def run_diagnosis():
    """진단 실행"""
    print("=" * 60)
    print("시스템 진단 중...")
    print("=" * 60)
    
    try:
        from utils.self_diagnosis import SelfDiagnosis
        diagnosis = SelfDiagnosis()
        summary = diagnosis.run_full_diagnosis()
        
        if summary['failed'] > 0:
            print(f"\n⚠️  {summary['failed']}개의 문제가 발견되었습니다.")
            print("자동 수정을 적용했습니다.")
            time.sleep(2)
        else:
            print("✅ 모든 검사를 통과했습니다.")
            
        return True
        
    except Exception as e:
        print(f"❌ 진단 중 오류: {e}")
        return False

def run_application():
    """애플리케이션 실행"""
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        
        # 오류 복구 시스템 초기화
        from utils.error_recovery import get_recovery_manager
        recovery_manager = get_recovery_manager()
        
        # High DPI 설정
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        
        # 애플리케이션 생성
        app = QApplication(sys.argv)
        app.setApplicationName("Excel Macro Automation")
        app.setOrganizationName("ExcelMacro")
        
        # 전역 예외 처리기 설정
        def handle_exception(exc_type, exc_value, exc_traceback):
            """전역 예외 처리"""
            if issubclass(exc_type, KeyboardInterrupt):
                sys.__excepthook__(exc_type, exc_value, exc_traceback)
                return
                
            # 오류 로깅
            error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
            print(f"\n{'=' * 60}")
            print("예상치 못한 오류가 발생했습니다!")
            print(f"{'=' * 60}")
            print(error_msg)
            
            # 복구 시도
            if recovery_manager.try_recover(exc_value):
                print("✅ 오류가 자동으로 복구되었습니다.")
            else:
                print("❌ 오류를 자동으로 복구할 수 없습니다.")
                
                # 오류 보고 다이얼로그 표시
                try:
                    from ui.dialogs.error_report_dialog import ErrorReportDialog
                    ErrorReportDialog.show_error(
                        "애플리케이션 오류",
                        str(exc_value),
                        detailed_error=error_msg
                    )
                except:
                    pass
                    
        sys.excepthook = handle_exception
        
        # 메인 윈도우 생성
        from ui.main_window import MainWindow
        from utils.error_decorator import auto_recover
        
        # 메인 윈도우 생성을 오류 복구로 감싸기
        @auto_recover(retry_count=2)
        def create_main_window():
            return MainWindow()
            
        window = create_main_window()
        window.show()
        
        # 복구 통계 표시
        stats = recovery_manager.get_statistics()
        if stats['total_recoveries'] > 0:
            print(f"\n복구 통계: {stats['success_rate']:.1f}% 성공률")
            
        # 애플리케이션 실행
        return app.exec_()
        
    except Exception as e:
        print(f"\n❌ 애플리케이션 시작 실패: {e}")
        traceback.print_exc()
        
        # 진단 도구 실행 제안
        print("\n다음 명령어로 시스템 진단을 실행해보세요:")
        print("python -m utils.self_diagnosis")
        
        return 1

def main():
    """메인 함수"""
    print("=" * 60)
    print("Excel Macro Automation - 자동 복구 모드")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 환경 설정
    setup_environment()
    
    # 진단 실행
    if not run_diagnosis():
        print("\n시스템 진단에 실패했습니다.")
        response = input("계속 진행하시겠습니까? (y/n): ")
        if response.lower() != 'y':
            return 1
            
    # 애플리케이션 실행
    print("\n애플리케이션을 시작합니다...")
    return run_application()

if __name__ == "__main__":
    sys.exit(main())