"""
First run dialog for OCR installation
"""

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QPixmap
from utils.ocr_manager import OCRManager, OCRStatus, OCRInstallThread
from logger.app_logger import get_logger

class FirstRunDialog(QDialog):
    """첫 실행 시 OCR 설치 다이얼로그"""
    
    installCompleted = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger(__name__)
        self.ocr_manager = OCRManager()
        self.setWindowTitle("Excel Macro 초기 설정")
        self.setFixedSize(500, 350)
        self.setModal(True)
        
        self.init_ui()
        
    def init_ui(self):
        """UI 초기화"""
        layout = QVBoxLayout()
        
        # 제목
        title = QLabel("텍스트 검색 기능 설치")
        title.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title)
        
        # 설명
        info_text = """
Excel Macro의 텍스트 검색 기능은 필수 기능입니다.
OCR 구성요소를 반드시 설치해야 합니다.

• 다운로드 크기: 약 300MB
• 예상 시간: 2-3분 (인터넷 속도에 따라)
• 설치 위치: 사용자 폴더

[주의] OCR은 필수 기능이므로 설치해야만 
프로그램을 사용할 수 있습니다.
        """
        info_label = QLabel(info_text.strip())
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # 진행률 표시 (초기에는 숨김)
        self.progress_widget = QWidget()
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("준비 중...")
        progress_layout.addWidget(self.status_label)
        
        self.progress_widget.setLayout(progress_layout)
        self.progress_widget.setVisible(False)
        layout.addWidget(self.progress_widget)
        
        # 버튼
        button_layout = QHBoxLayout()
        
        self.install_btn = QPushButton("설치")
        self.install_btn.clicked.connect(self.start_installation)
        button_layout.addWidget(self.install_btn)
        
        # 건너뛰기 버튼 제거 - OCR은 필수
        # self.skip_btn = QPushButton("나중에")
        # self.skip_btn.clicked.connect(self.skip_installation)
        # button_layout.addWidget(self.skip_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def closeEvent(self, event):
        """다이얼로그 닫기 이벤트 - OCR은 필수이므로 닫기 불가"""
        event.ignore()
        QMessageBox.warning(self, "설치 필수",
            "OCR은 필수 기능입니다.\n"
            "설치를 진행해주세요.")
    
    def start_installation(self):
        """설치 시작"""
        self.install_btn.setEnabled(False)
        # self.skip_btn.setEnabled(False)  # 건너뛰기 버튼 제거됨
        self.progress_widget.setVisible(True)
        
        # OCR 설치 스레드 시작
        self.install_thread = OCRInstallThread(self.ocr_manager.ocr_path)
        self.install_thread.progress.connect(self.update_progress)
        self.install_thread.finished.connect(self.installation_finished)
        self.install_thread.start()
        
        # 상태 업데이트
        self.ocr_manager.set_status(OCRStatus.INSTALLING)
    
    def update_progress(self, percent, message):
        """진행률 업데이트"""
        self.progress_bar.setValue(percent)
        self.status_label.setText(message)
    
    def installation_finished(self, success, message):
        """설치 완료"""
        if success:
            self.ocr_manager.set_status(OCRStatus.INSTALLED)
            QMessageBox.information(self, "설치 완료", 
                "텍스트 검색 기능이 성공적으로 설치되었습니다.")
            self.installCompleted.emit()
            self.accept()
        else:
            self.ocr_manager.set_status(OCRStatus.FAILED)
            retry = QMessageBox.question(self, "설치 실패",
                f"설치 중 오류가 발생했습니다:\n{message}\n\n다시 시도하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No)
            
            if retry == QMessageBox.Yes:
                self.start_installation()
            else:
                # OCR은 필수이므로 프로그램 종료
                QMessageBox.critical(self, "설치 필수",
                    "OCR은 필수 기능입니다.\n프로그램을 종료합니다.")
                import sys
                sys.exit(1)
    
    def skip_installation(self):
        """설치 건너뛰기 - OCR은 필수이므로 사용 안 함"""
        # OCR은 필수 기능이므로 건너뛰기 불가
        QMessageBox.critical(self, "설치 필수",
            "OCR은 필수 기능입니다.\n"
            "프로그램을 사용하려면 반드시 설치해야 합니다.")
        import sys
        sys.exit(1)


class SplashScreenWithOCR(QSplashScreen):
    """OCR 설치 확인이 포함된 스플래시 스크린"""
    
    def __init__(self, pixmap=None):
        super().__init__(pixmap or QPixmap())
        self.logger = get_logger(__name__)
        self.ocr_manager = OCRManager()
        
    def show_and_check_ocr(self):
        """스플래시 표시 및 OCR 확인"""
        self.show()
        self.showMessage("Excel Macro 시작 중...", Qt.AlignBottom | Qt.AlignCenter)
        
        # OCR 상태 확인
        QTimer.singleShot(500, self.check_ocr_status)
    
    def check_ocr_status(self):
        """OCR 설치 상태 확인"""
        if not self.ocr_manager.is_installed():
            self.showMessage("텍스트 검색 기능 확인 중...", Qt.AlignBottom | Qt.AlignCenter)
            # 첫 실행 다이얼로그 표시
            QTimer.singleShot(100, self.show_first_run_dialog)
        else:
            # 이미 설치됨
            self.showMessage("구성요소 로드 중...", Qt.AlignBottom | Qt.AlignCenter)
            QTimer.singleShot(1000, self.close)
    
    def show_first_run_dialog(self):
        """첫 실행 다이얼로그 표시"""
        self.hide()
        
        dialog = FirstRunDialog()
        dialog.installCompleted.connect(self.ocr_installed)
        
        if dialog.exec_() == QDialog.Rejected:
            # OCR은 필수이므로 설치 거부 시 프로그램 종료
            import sys
            sys.exit(1)
        
    def ocr_installed(self):
        """OCR 설치 완료"""
        self.showMessage("설치 완료! 시작 중...", Qt.AlignBottom | Qt.AlignCenter)
        self.show()
        QTimer.singleShot(1000, self.close)