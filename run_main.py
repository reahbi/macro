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
os.environ['QT_QPA_PLATFORM'] = 'xcb'
os.environ['PYTHONPATH'] = f"{project_root}:{src_path}"

# 상대 import를 절대 import로 변경하기 위한 monkey patching
def patch_imports():
    """모든 상대 import를 절대 import로 변경"""
    
    # settings.py의 상대 import 수정
    settings_file = src_path / "config" / "settings.py"
    content = settings_file.read_text()
    content = content.replace("from ..utils.encryption", "from utils.encryption")
    content = content.replace("from ..logger.app_logger", "from logger.app_logger")
    settings_file.write_text(content)
    
    # main_window.py의 상대 import 수정  
    main_window_file = src_path / "ui" / "main_window.py"
    if main_window_file.exists():
        content = main_window_file.read_text()
        content = content.replace("from ..config.settings", "from config.settings")
        content = content.replace("from ..logger.app_logger", "from logger.app_logger")
        content = content.replace("from .widgets.excel_widget", "from ui.widgets.excel_widget")
        content = content.replace("from .widgets.macro_editor", "from ui.widgets.macro_editor")
        content = content.replace("from .widgets.execution_widget", "from ui.widgets.execution_widget")
        main_window_file.write_text(content)
    
    # excel_widget.py의 상대 import 수정
    excel_widget_file = src_path / "ui" / "widgets" / "excel_widget.py"
    if excel_widget_file.exists():
        content = excel_widget_file.read_text()
        content = content.replace("from ...excel.excel_manager", "from excel.excel_manager")
        content = content.replace("from ...config.settings", "from config.settings")
        content = content.replace("from ...logger.app_logger", "from logger.app_logger")
        excel_widget_file.write_text(content)
    
    # macro_editor.py의 상대 import 수정
    macro_editor_file = src_path / "ui" / "widgets" / "macro_editor.py"
    if macro_editor_file.exists():
        content = macro_editor_file.read_text()
        content = content.replace("from ...core", "from core")
        content = content.replace("from ..dialogs", "from ui.dialogs")
        macro_editor_file.write_text(content)
    
    # execution_widget.py의 상대 import 수정
    execution_widget_file = src_path / "ui" / "widgets" / "execution_widget.py"
    if execution_widget_file.exists():
        content = execution_widget_file.read_text()
        content = content.replace("from ...automation", "from automation")
        content = content.replace("from ...core", "from core")
        content = content.replace("from ...config", "from config")
        content = content.replace("from ...logger", "from logger")
        execution_widget_file.write_text(content)
    
    # 다른 파일들도 수정
    for py_file in src_path.rglob("*.py"):
        try:
            content = py_file.read_text()
            if "from .." in content:
                # 상대 import를 절대 import로 변경
                content = content.replace("from ...", "from ")
                content = content.replace("from ..", "from ")
                py_file.write_text(content)
        except:
            pass

# Import 수정 적용
print("Import 경로 수정 중...")
patch_imports()
print("Import 경로 수정 완료!")

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
    font = QFont("Nanum Gothic", 10)
    app.setFont(font)
    
    # 메인 윈도우 import 및 실행
    from ui.main_window import MainWindow
    from config.settings import Settings
    from logger.app_logger import setup_logger
    
    # 로거 설정
    logger = setup_logger()
    logger.info("Starting Excel Macro Automation Application")
    
    # 설정 초기화
    settings = Settings()
    
    # 메인 윈도우 생성 및 표시
    window = MainWindow(settings)
    window.setWindowTitle("Excel 기반 작업 자동화 매크로")
    window.show()
    
    print("\n✓ Excel Macro Automation 애플리케이션이 실행되었습니다!")
    print("✓ 모든 GUI 컴포넌트가 로드되었습니다.")
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