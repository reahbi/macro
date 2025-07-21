"""
OCR Manager for handling EasyOCR installation and initialization
"""

import os
import sys
import json
from pathlib import Path
from typing import Optional, Callable
from PyQt5.QtCore import QThread, pyqtSignal
from logger.app_logger import get_logger

class OCRStatus:
    """OCR 설치 상태"""
    NOT_INSTALLED = "not_installed"
    INSTALLING = "installing"
    INSTALLED = "installed"
    FAILED = "failed"

class OCRManager:
    """EasyOCR 설치 및 관리"""
    
    _instance = None
    _status = OCRStatus.NOT_INSTALLED
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.logger = get_logger(__name__)
            self.ocr_path = Path.home() / ".excel_macro" / "ocr"
            self.status_file = self.ocr_path / "status.json"
            self.initialized = True
            self._check_status()
    
    def _check_status(self):
        """OCR 설치 상태 확인"""
        if self.status_file.exists():
            try:
                with open(self.status_file, 'r') as f:
                    data = json.load(f)
                    self._status = data.get('status', OCRStatus.NOT_INSTALLED)
            except:
                self._status = OCRStatus.NOT_INSTALLED
        else:
            self._status = OCRStatus.NOT_INSTALLED
    
    def get_status(self) -> str:
        """현재 OCR 상태 반환"""
        return self._status
    
    def is_installed(self) -> bool:
        """OCR 설치 여부"""
        return self._status == OCRStatus.INSTALLED
    
    def is_available(self) -> bool:
        """OCR 사용 가능 여부"""
        if not self.is_installed():
            return False
        
        try:
            # 실제로 import 가능한지 확인
            import easyocr
            return True
        except ImportError:
            return False
    
    def set_status(self, status: str):
        """상태 업데이트"""
        self._status = status
        self.ocr_path.mkdir(parents=True, exist_ok=True)
        
        with open(self.status_file, 'w') as f:
            json.dump({'status': status}, f)
    
    def get_text_extractor(self):
        """TextExtractor 인스턴스 반환"""
        if not self.is_available():
            raise RuntimeError("OCR이 설치되지 않았습니다. 첫 실행 시 자동으로 설치됩니다.")
        
        from vision.text_extractor import TextExtractor
        return TextExtractor()


class OCRInstallThread(QThread):
    """OCR 설치 스레드"""
    progress = pyqtSignal(int, str)  # percent, message
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, ocr_path: Path):
        super().__init__()
        self.ocr_path = ocr_path
        self.logger = get_logger(__name__)
    
    def run(self):
        """OCR 구성요소 설치"""
        try:
            # 자동 설치 모듈 사용
            from utils.ocr_auto_installer import AutoOCRInstaller
            
            installer = AutoOCRInstaller()
            
            # 진행률 연결
            installer.progress.connect(lambda p, m: self.progress.emit(p, m))
            installer.finished.connect(lambda s, m: self.finished.emit(s, m))
            
            # 설치 실행
            installer.run()
                
        except Exception as e:
            self.logger.error(f"OCR 설치 실패: {e}")
            self.finished.emit(False, str(e))