#!/usr/bin/env python3
"""
별도 프로세스로 실행되는 ROI 선택기
모달 다이얼로그 문제를 완전히 회피
"""

import sys
import json
import os

# 경로 설정
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt5.QtWidgets import QApplication
from ui.widgets.simple_roi_selector import SimpleROISelector


def main():
    """ROI 선택기 메인 함수"""
    if len(sys.argv) < 2:
        print("Usage: roi_selector_process.py <result_file>")
        sys.exit(1)
        
    result_file = sys.argv[1]
    result = {'success': False}
    
    try:
        # Qt 애플리케이션 생성
        app = QApplication(sys.argv)
        
        # ROI 선택기 생성
        print("DEBUG: Creating ROI selector in separate process")
        roi_selector = SimpleROISelector()
        
        # 결과 처리 함수
        def on_selection_complete(region):
            print(f"DEBUG: Region selected in process: {region}")
            result['success'] = True
            result['region'] = list(region)
            app.quit()
            
        def on_selection_cancelled():
            print("DEBUG: Selection cancelled in process")
            result['success'] = False
            app.quit()
            
        # 시그널 연결
        roi_selector.selectionComplete.connect(on_selection_complete)
        roi_selector.selectionCancelled.connect(on_selection_cancelled)
        
        # 선택 시작
        print("DEBUG: Starting ROI selection in process")
        roi_selector.start_selection()
        
        # 이벤트 루프 실행
        app.exec_()
        
    except Exception as e:
        print(f"ERROR in ROI selector process: {e}")
        import traceback
        traceback.print_exc()
        result['success'] = False
        result['error'] = str(e)
        
    # 결과 저장
    try:
        with open(result_file, 'w') as f:
            json.dump(result, f)
        print(f"DEBUG: Result saved to {result_file}")
    except Exception as e:
        print(f"ERROR saving result: {e}")


if __name__ == "__main__":
    main()