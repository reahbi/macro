#!/usr/bin/env python3
"""
실제 메인 애플리케이션 실행 스크립트
모든 import 문제를 해결하여 실행
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
else:
    os.environ['QT_QPA_PLATFORM'] = 'xcb'
os.environ['PYTHONPATH'] = f"{project_root}:{src_path}"
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 이제 메인 애플리케이션 실행
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
    
    # High DPI 지원 - QApplication 생성 전에 설정
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 애플리케이션 초기화
    app = QApplication(sys.argv)
    app.setApplicationName("Excel Macro Automation")
    
    # 한글 폰트 설정
    font = QFont("Malgun Gothic", 10)  # Windows 기본 한글 폰트
    app.setFont(font)
    
    # 메인 윈도우 import 및 실행
    from ui.main_window import MainWindow
    from config.settings import Settings
    from logger.app_logger import setup_logger
    from ui.dialogs.first_run_dialog import SplashScreenWithOCR
    from utils.ocr_manager import OCRManager
    
    # 로거 설정
    logger = setup_logger()
    logger.info("Starting Excel Macro Automation Application")
    
    # 설정 초기화
    settings = Settings()
    
    # OCR 체크가 포함된 스플래시 스크린
    splash = SplashScreenWithOCR()
    splash.show_and_check_ocr()
    
    # 스플래시가 닫힐 때까지 대기
    while splash.isVisible():
        app.processEvents()
    
    # 메인 윈도우 생성 및 표시
    window = MainWindow(settings)
    window.setWindowTitle("Excel 기반 작업 자동화 매크로")
    window.show()
    
    print("\nExcel Macro Automation 애플리케이션이 실행되었습니다!")
    print("모든 GUI 컴포넌트가 로드되었습니다.")
    print("\n기능:")
    print("- Excel 탭: 파일 불러오기, 시트 선택, 데이터 미리보기")
    print("- Editor 탭: 드래그 앤 드롭 매크로 편집")
    print("- Run 탭: 매크로 실행 및 모니터링")
    print("\n창을 닫으면 종료됩니다.")
    
    # 이벤트 루프 실행
    sys.exit(app.exec_())
    
except Exception as e:
    print(f"\n오류 발생: {e}")
    print("\n자세한 오류 정보:")
    import traceback
    traceback.print_exc()
    
    print("\n디버깅 정보:")
    print(f"Project root: {project_root}")
    print(f"Src path: {src_path}")
    print(f"Python path: {sys.path[:3]}")
    
    # 오류 발생 시 일시 정지
    input("\nPress Enter to exit...")
    sys.exit(1)