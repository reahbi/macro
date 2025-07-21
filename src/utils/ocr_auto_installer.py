"""
Automatic OCR installer for Excel Macro Automation
"""

import subprocess
import sys
import os
from pathlib import Path
from PyQt5.QtCore import QThread, pyqtSignal
import json
import time

class AutoOCRInstaller(QThread):
    """자동 OCR 설치 스레드"""
    progress = pyqtSignal(int, str)  # percent, message
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self):
        super().__init__()
        self.ocr_path = Path.home() / ".excel_macro" / "ocr"
        self.ocr_path.mkdir(parents=True, exist_ok=True)
        self.status_file = self.ocr_path / "status.json"
        
    def run(self):
        """OCR 자동 설치 실행"""
        try:
            # 1. pip 업그레이드
            self.progress.emit(5, "pip 업그레이드 중...")
            self._run_pip_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
            
            # 2. PyTorch CPU 설치
            self.progress.emit(10, "PyTorch CPU 버전 설치 중... (약 150MB)")
            self._run_pip_command([
                sys.executable, "-m", "pip", "install", 
                "torch", "torchvision", "torchaudio",
                "--index-url", "https://download.pytorch.org/whl/cpu"
            ])
            
            # 3. EasyOCR 설치
            self.progress.emit(50, "EasyOCR 설치 중...")
            self._run_pip_command([
                sys.executable, "-m", "pip", "install", "easyocr"
            ])
            
            # 4. 추가 의존성
            self.progress.emit(70, "추가 구성요소 설치 중...")
            self._run_pip_command([
                sys.executable, "-m", "pip", "install",
                "opencv-python-headless", "pillow", "scipy"
            ])
            
            # 5. OCR 초기화 및 모델 다운로드
            self.progress.emit(80, "OCR 모델 다운로드 중... (한국어/영어)")
            self._initialize_ocr()
            
            # 6. 설치 완료 표시
            self._save_status("installed")
            self.progress.emit(100, "설치 완료!")
            self.finished.emit(True, "EasyOCR이 성공적으로 설치되었습니다.")
            
        except subprocess.CalledProcessError as e:
            error_msg = f"패키지 설치 실패: {e}"
            self._save_status("failed", error_msg)
            self.finished.emit(False, error_msg)
            
        except Exception as e:
            error_msg = f"설치 중 오류 발생: {str(e)}"
            self._save_status("failed", error_msg)
            self.finished.emit(False, error_msg)
    
    def _run_pip_command(self, command):
        """pip 명령 실행"""
        # Windows에서 창이 뜨지 않도록 설정
        startupinfo = None
        if sys.platform == "win32":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            startupinfo=startupinfo,
            text=True
        )
        
        stdout, stderr = process.communicate()
        
        if process.returncode != 0:
            raise subprocess.CalledProcessError(
                process.returncode, command, 
                output=stdout, stderr=stderr
            )
            
        return stdout
    
    def _initialize_ocr(self):
        """OCR 초기화 및 모델 다운로드"""
        init_code = """
import easyocr
import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'
reader = easyocr.Reader(['ko', 'en'], gpu=False, download_enabled=True)
print("OCR initialized successfully")
"""
        
        # Python 스크립트로 실행
        result = subprocess.run(
            [sys.executable, "-c", init_code],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"OCR 초기화 실패: {result.stderr}")
    
    def _save_status(self, status, error=None):
        """설치 상태 저장"""
        status_data = {
            "status": status,
            "version": "1.0.0",
            "timestamp": time.time()
        }
        
        if error:
            status_data["error"] = error
            
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)