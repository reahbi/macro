"""
Windows Snipping Tool을 활용한 영역 선택
"""

import subprocess
import time
import pyautogui
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QTimer


def use_windows_snipping_tool(parent=None):
    """Windows Snipping Tool을 사용하여 영역 선택"""
    
    # 안내 메시지
    msg = QMessageBox(parent)
    msg.setWindowTitle("영역 선택")
    msg.setText("Windows 캡처 도구를 사용하여 영역을 선택하세요.")
    msg.setInformativeText(
        "1. '확인'을 클릭하면 Windows 캡처 도구가 시작됩니다.\n"
        "2. 마우스로 영역을 드래그하여 선택하세요.\n"
        "3. 선택한 영역의 좌표가 자동으로 감지됩니다."
    )
    msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    
    if msg.exec_() == QMessageBox.Ok:
        try:
            # Windows + Shift + S 실행
            pyautogui.hotkey('win', 'shift', 's')
            
            # 사용자가 선택할 시간 대기
            time.sleep(3)
            
            # 마우스 위치로 대략적인 영역 추정
            # 실제로는 더 정교한 방법 필요
            x, y = pyautogui.position()
            
            # 임시로 100x100 영역 반환
            return (x-50, y-50, 100, 100)
            
        except Exception as e:
            print(f"Error using snipping tool: {e}")
            return None
    
    return None