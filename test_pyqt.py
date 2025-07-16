#!/usr/bin/env python3
"""
PyQt5 테스트 스크립트
"""

import sys
import os

print("PyQt5 테스트 시작...")

try:
    from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
    from PyQt5.QtCore import Qt
    print("✓ PyQt5 import 성공")
except Exception as e:
    print(f"✗ PyQt5 import 실패: {e}")
    input("Press Enter to exit...")
    sys.exit(1)

try:
    # 애플리케이션 생성
    app = QApplication(sys.argv)
    print("✓ QApplication 생성 성공")
    
    # 간단한 윈도우 생성
    window = QMainWindow()
    window.setWindowTitle("PyQt5 Test")
    window.setGeometry(100, 100, 300, 200)
    
    label = QLabel("PyQt5가 정상적으로 작동합니다!", window)
    label.setAlignment(Qt.AlignCenter)
    window.setCentralWidget(label)
    
    window.show()
    print("✓ 윈도우 생성 및 표시 성공")
    
    print("\n테스트 윈도우가 표시되었습니다. 창을 닫으면 종료됩니다.")
    
    # 이벤트 루프 실행
    sys.exit(app.exec_())
    
except Exception as e:
    print(f"✗ PyQt5 테스트 실패: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")
    sys.exit(1)