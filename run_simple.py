#!/usr/bin/env python3
"""
간단한 실행 스크립트 - import 문제 해결
"""

import sys
import os
from pathlib import Path

# 프로젝트 경로 설정
project_root = Path(__file__).parent.absolute()
src_path = project_root / "src"

# Python 경로에 추가
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

# 환경 변수 설정
if sys.platform == 'win32':
    os.environ['QT_QPA_PLATFORM'] = 'windows'
elif sys.platform.startswith('linux'):
    os.environ['QT_QPA_PLATFORM'] = 'xcb'
    if 'DISPLAY' not in os.environ:
        os.environ['DISPLAY'] = ':0'

print("Excel Macro Automation 시작...")

try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    
    # High DPI 설정
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    
    # 애플리케이션 생성
    app = QApplication(sys.argv)
    app.setApplicationName("Excel Macro Automation")
    
    # 설정 및 로거 초기화
    from config.settings import Settings
    from logger.app_logger import setup_logger
    
    settings = Settings()
    logger = setup_logger()
    
    # 메인 윈도우 생성
    from ui.main_window import MainWindow
    window = MainWindow(settings)
    
    # 윈도우 표시
    window.show()
    
    print("✓ GUI가 실행되었습니다!")
    print("종료하려면 창을 닫으세요.")
    
    # 이벤트 루프 실행
    sys.exit(app.exec_())
    
except Exception as e:
    print(f"\n오류 발생: {e}")
    import traceback
    traceback.print_exc()
    input("\nEnter를 눌러 종료...")