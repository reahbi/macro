#!/usr/bin/env python3
"""
Import 문제를 해결한 메인 실행 스크립트
"""

import sys
import os
from pathlib import Path

# UTF-8 인코딩 설정
import locale
if sys.platform == 'win32':
    # Windows에서 UTF-8 설정
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    try:
        locale.setlocale(locale.LC_ALL, 'ko_KR.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'Korean_Korea.949')
        except:
            pass

# 프로젝트 경로 설정
project_root = Path(__file__).parent.absolute()
src_path = project_root / "src"

# Python 경로에 추가
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

# 모든 import 문제 해결
def fix_all_imports():
    """모든 파일의 import 경로를 수정"""
    print("Import 경로 수정 중...")
    
    # src 디렉토리가 없으면 생성
    src_path.mkdir(exist_ok=True)
    
    # 모든 Python 파일 찾기
    for py_file in src_path.rglob("*.py"):
        if py_file.is_file():
            try:
                content = py_file.read_text(encoding='utf-8')
                original_content = content
                
                # 상대 import를 절대 import로 변경
                import re
                
                # from ..module import 패턴 변경
                content = re.sub(r'from \.\.\.([^.\s]+)', r'from \1', content)
                content = re.sub(r'from \.\.([^.\s]+)', r'from \1', content)
                content = re.sub(r'from \.([^.\s]+)', r'from ui.\1', content)
                
                # 특정 import 수정
                content = content.replace("from dialogs.", "from ui.dialogs.")
                content = content.replace("from widgets.", "from ui.widgets.")
                
                # 잘못된 위치 수정
                content = content.replace("from ui.macro_types import", "from core.macro_types import")
                content = content.replace("from ui.macro_storage import", "from core.macro_storage import")
                content = content.replace("from ui.file_selector import", "from ui.widgets.file_selector import")
                content = content.replace("from ui.sheet_mapper import", "from ui.widgets.sheet_mapper import")
                content = content.replace("from ui.data_preview import", "from ui.widgets.data_preview import")
                content = content.replace("from ui.models import", "from excel.models import")
                content = content.replace("from ui.executor import", "from automation.executor import")
                content = content.replace("from ui.hotkey_listener import", "from automation.hotkey_listener import")
                content = content.replace("from ui.image_matcher import", "from vision.image_matcher import")
                content = content.replace("from ui.text_extractor import", "from vision.text_extractor import")
                
                # 파일이 변경되었으면 저장
                if content != original_content:
                    py_file.write_text(content, encoding='utf-8')
                    print(f"수정됨: {py_file.relative_to(src_path)}")
                    
            except Exception as e:
                print(f"파일 수정 오류 {py_file}: {e}")
    
    print("Import 경로 수정 완료")

# Import 수정 실행
fix_all_imports()

# 환경 변수 설정
if sys.platform == 'win32':
    os.environ['QT_QPA_PLATFORM'] = 'windows'
else:
    os.environ['QT_QPA_PLATFORM'] = 'xcb'

# 메인 애플리케이션 실행
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    from PyQt5.QtGui import QFont
    
    # High DPI 지원
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # 애플리케이션 초기화
    app = QApplication(sys.argv)
    app.setApplicationName("Excel Macro Automation")
    
    # 폰트 설정
    if sys.platform == 'win32':
        font = QFont("맑은 고딕", 10)
    else:
        font = QFont("Nanum Gothic", 10)
    app.setFont(font)
    
    # 메인 윈도우 import 및 실행
    print("모듈 import 중...")
    
    try:
        from ui.main_window import MainWindow
        print("✓ MainWindow import 완료")
    except Exception as e:
        print(f"✗ MainWindow import 실패: {e}")
        raise
        
    try:
        from config.settings import Settings
        print("✓ Settings import 완료")
    except Exception as e:
        print(f"✗ Settings import 실패: {e}")
        raise
        
    try:
        from logger.app_logger import setup_logger
        print("✓ Logger import 완료")
    except Exception as e:
        print(f"✗ Logger import 실패: {e}")
        raise
    
    # 로거 설정
    try:
        logger = setup_logger()
        logger.info("Starting Excel Macro Automation Application")
        print("✓ Logger 설정 완료")
    except Exception as e:
        print(f"✗ Logger 설정 실패: {e}")
        # Logger 실패해도 계속 진행
        logger = None
    
    # 설정 초기화
    try:
        settings = Settings()
        print("✓ Settings 초기화 완료")
    except Exception as e:
        print(f"✗ Settings 초기화 실패: {e}")
        raise
    
    # 메인 윈도우 생성 및 표시
    try:
        print("✓ MainWindow 객체 생성 중...")
        window = MainWindow(settings)
        print("✓ MainWindow 객체 생성 완료")
        
        print("✓ 윈도우 타이틀 설정 중...")
        window.setWindowTitle("Excel 기반 작업 자동화 매크로")
        print("✓ 윈도우 타이틀 설정 완료")
        
        print("✓ 윈도우 표시 중...")
        window.show()
        print("✓ 윈도우 표시 완료")
        
        print("\n✓ Excel Macro Automation 애플리케이션이 실행되었습니다!")
        print("✓ 모든 GUI 컴포넌트가 로드되었습니다.")
        print("\n기능:")
        print("- Excel 탭: 파일 불러오기, 시트 선택, 데이터 미리보기")
        print("- Editor 탭: 드래그 앤 드롭 매크로 편집")
        print("- Run 탭: 매크로 실행 및 모니터링")
        print("\n창을 닫으면 종료됩니다.")
        print("\n✓ 이벤트 루프 시작 중...")
        
        # 이벤트 루프 실행
        result = app.exec_()
        print(f"\n✓ 이벤트 루프 종료됨 (코드: {result})")
        sys.exit(result)
        
    except Exception as window_error:
        print(f"\n메인 윈도우 생성 중 오류: {window_error}")
        import traceback
        traceback.print_exc()
        raise
    
except Exception as e:
    print(f"\n오류 발생: {e}")
    print("\n자세한 오류 정보:")
    import traceback
    traceback.print_exc()
    
    print("\n디버깅 정보:")
    print(f"Project root: {project_root}")
    print(f"Src path: {src_path}")
    print(f"Python path: {sys.path[:3]}")
    print(f"Platform: {sys.platform}")
    
    input("\nPress Enter to exit...")