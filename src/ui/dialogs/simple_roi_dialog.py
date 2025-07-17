"""
간단한 ROI 선택 다이얼로그
모달 문제를 완전히 우회하는 독립적인 구현
"""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QPushButton, QLabel, QApplication
from PyQt5.QtCore import Qt, pyqtSignal
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ui.widgets.simple_roi_selector import SimpleROISelector


class SimpleROIDialog(QDialog):
    """ROI 선택만을 위한 간단한 다이얼로그"""
    
    regionSelected = pyqtSignal(tuple)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("영역 선택")
        self.setModal(False)  # 비모달!
        self.selected_region = None
        
        layout = QVBoxLayout()
        
        self.info_label = QLabel("버튼을 클릭하여 화면 영역을 선택하세요")
        layout.addWidget(self.info_label)
        
        self.select_btn = QPushButton("화면 영역 선택")
        self.select_btn.clicked.connect(self.start_selection)
        layout.addWidget(self.select_btn)
        
        self.setLayout(layout)
        
    def start_selection(self):
        """ROI 선택 시작"""
        print("DEBUG: SimpleROIDialog starting selection")
        
        # 다이얼로그 완전히 숨기기
        self.hide()
        
        # 새 애플리케이션 이벤트 루프에서 실행
        QApplication.processEvents()
        
        # ROI 선택기 실행
        self.roi_selector = SimpleROISelector()
        self.roi_selector.selectionComplete.connect(self.on_selection_complete)
        self.roi_selector.selectionCancelled.connect(self.on_selection_cancelled)
        self.roi_selector.start_selection()
        
    def on_selection_complete(self, region):
        """선택 완료"""
        print(f"DEBUG: Region selected: {region}")
        self.selected_region = region
        self.regionSelected.emit(region)
        self.accept()
        
    def on_selection_cancelled(self):
        """선택 취소"""
        print("DEBUG: Selection cancelled")
        self.show()


# 독립 실행 테스트
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = SimpleROIDialog()
    dialog.show()
    
    def on_region(region):
        print(f"Selected region: {region}")
        app.quit()
        
    dialog.regionSelected.connect(on_region)
    sys.exit(app.exec_())