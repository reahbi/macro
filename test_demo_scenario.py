#!/usr/bin/env python3
"""
Demo test scenario for manual testing
Creates a simple macro and executes it with logging
"""

import sys
import os
from pathlib import Path
import time
import pandas as pd
import tempfile

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from config.settings import Settings
from core.macro_types import Macro, MacroStep, StepType
from logger.app_logger import setup_logger


def create_demo_excel_file():
    """Create a demo Excel file for testing"""
    temp_file = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    
    # Create test data
    test_data = pd.DataFrame({
        '작업항목': ['로그인', '데이터 입력', '검색', '결과 확인', '로그아웃'],
        '대기시간': [2, 1, 1, 3, 1],
        '입력텍스트': ['test@example.com', '테스트 데이터', '검색어', '', ''],
        '상태': ['대기', '대기', '대기', '대기', '대기'],
        'Status': ['', '', '', '', '']
    })
    
    # Save to Excel
    test_data.to_excel(temp_file.name, index=False, sheet_name='작업목록')
    temp_file.close()
    
    print(f"✅ Demo Excel file created: {temp_file.name}")
    return temp_file.name


def create_demo_macro():
    """Create a demo macro for testing"""
    macro = Macro(name="데모 테스트 매크로")
    
    # Step 1: Wait
    wait_step = MacroStep(step_type=StepType.WAIT_TIME)
    wait_step.name = "초기 대기"
    wait_step.config = {"duration_seconds": 1}
    macro.add_step(wait_step)
    
    # Step 2: Type text with variable
    type_step = MacroStep(step_type=StepType.KEYBOARD_TYPE)
    type_step.name = "작업 항목 입력"
    type_step.config = {
        "text": "작업: {{작업항목}}",
        "use_variable": True
    }
    macro.add_step(type_step)
    
    # Step 3: Variable wait time
    var_wait_step = MacroStep(step_type=StepType.WAIT_TIME)
    var_wait_step.name = "변수 대기 시간"
    var_wait_step.config = {
        "duration_seconds": "{{대기시간}}",
        "use_variable": True
    }
    macro.add_step(var_wait_step)
    
    # Step 4: Conditional text input
    cond_step = MacroStep(step_type=StepType.IF_CONDITION)
    cond_step.name = "텍스트 입력 확인"
    cond_step.config = {
        "condition_type": "variable_not_empty",
        "variable_name": "입력텍스트"
    }
    
    # True branch - type the text
    true_type_step = MacroStep(step_type=StepType.KEYBOARD_TYPE)
    true_type_step.name = "조건부 텍스트 입력"
    true_type_step.config = {
        "text": "{{입력텍스트}}",
        "use_variable": True
    }
    cond_step.true_steps = [true_type_step]
    
    macro.add_step(cond_step)
    
    print("✅ Demo macro created with 4 steps")
    return macro


def run_demo_test():
    """Run the demo test scenario"""
    print("\n" + "="*60)
    print("Excel Macro Automation - Demo Test Scenario")
    print("="*60)
    
    # Setup logger
    logger = setup_logger()
    logger.info("Starting demo test scenario")
    
    # Create test data
    excel_file = create_demo_excel_file()
    macro = create_demo_macro()
    
    print("\n📋 Test Scenario:")
    print("1. Excel 파일을 로드합니다")
    print("2. 매크로를 설정합니다")
    print("3. 각 행에 대해 매크로를 실행합니다")
    print("4. 실행 로그를 확인합니다")
    print("\n시작하려면 Enter를 누르세요...")
    input()
    
    # Create Qt application
    app = QApplication(sys.argv)
    
    # Create settings
    settings = Settings()
    
    # Create main window
    window = MainWindow(settings)
    window.show()
    
    print("\n📌 수동 테스트 단계:")
    print("1. Excel 탭에서 '열기' 버튼을 클릭하고 생성된 파일을 선택하세요")
    print(f"   파일 경로: {excel_file}")
    print("2. '작업목록' 시트를 선택하세요")
    print("3. 열 매핑을 설정하세요:")
    print("   - 작업항목 → 작업항목")
    print("   - 대기시간 → 대기시간")
    print("   - 입력텍스트 → 입력텍스트")
    print("   - Status → Status")
    print("4. Editor 탭으로 이동하세요")
    print("5. 이미 생성된 매크로가 표시됩니다")
    print("6. Run 탭으로 이동하세요")
    print("7. '시작' 버튼을 클릭하여 실행하세요")
    print("8. 실행 중/후 'CSV 로그 보기' 버튼을 클릭하세요")
    print("\n💡 테스트 포인트:")
    print("- 각 단계가 순서대로 실행되는지 확인")
    print("- 변수가 올바르게 치환되는지 확인")
    print("- 조건문이 정상 작동하는지 확인")
    print("- 로그가 실시간으로 업데이트되는지 확인")
    print("- 에러 발생 시 에러 다이얼로그가 표시되는지 확인")
    
    # Pre-load the macro in the editor
    window.macro_editor.set_macro(macro)
    
    # Pre-load Excel manager setup hint
    print("\n⚠️  주의: 실제 화면 클릭이나 텍스트 입력은 시뮬레이션됩니다.")
    print("실제 자동화를 테스트하려면 이미지 캡처와 실제 대상 프로그램이 필요합니다.")
    
    # Run the application
    app.exec_()
    
    print("\n✅ 테스트 완료!")
    print(f"생성된 Excel 파일: {excel_file}")
    print("로그 파일 위치: ~/.excel_macro_automation/execution_logs/")
    
    # Cleanup option
    cleanup = input("\n임시 파일을 삭제하시겠습니까? (y/n): ")
    if cleanup.lower() == 'y':
        try:
            os.unlink(excel_file)
            print("✅ 임시 파일이 삭제되었습니다.")
        except:
            print("⚠️  파일 삭제 실패. 수동으로 삭제해주세요.")


if __name__ == "__main__":
    run_demo_test()