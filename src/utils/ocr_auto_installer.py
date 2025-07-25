"""
Automatic OCR installer for Excel Macro Automation
PaddleOCR installation only
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
        """PaddleOCR 자동 설치 실행"""
        try:
            # 1. pip 업그레이드
            self.progress.emit(5, "pip 업그레이드 중...")
            self._run_pip_command([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
            
            # 2. Python 버전 확인
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
            if python_version not in ["3.8", "3.9", "3.10", "3.11"]:
                raise Exception(f"PaddleOCR는 Python 3.8 ~ 3.11을 지원합니다. 현재 버전: {python_version}")
            
            # 3. PaddlePaddle 설치 (CPU 버전)
            self.progress.emit(20, "PaddlePaddle 설치 중... (약 500MB)")
            self._run_pip_command([
                sys.executable, "-m", "pip", "install", 
                "paddlepaddle>=2.5.0", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple"
            ])
            
            # 4. PaddleOCR 설치
            self.progress.emit(60, "PaddleOCR 설치 중...")
            self._run_pip_command([
                sys.executable, "-m", "pip", "install", "paddleocr>=2.7.0"
            ])
            
            # 5. 추가 의존성
            self.progress.emit(70, "추가 구성요소 설치 중...")
            self._run_pip_command([
                sys.executable, "-m", "pip", "install",
                "opencv-python", "pillow", "numpy"
            ])
            
            # 6. OCR 초기화 및 모델 다운로드
            self.progress.emit(80, "OCR 모델 다운로드 중... (한국어)")
            self._initialize_paddleocr()
            
            # 7. 설치 완료 표시
            self._save_status("installed")
            self.progress.emit(100, "설치 완료!")
            self.finished.emit(True, "PaddleOCR이 성공적으로 설치되었습니다.")
            
        except subprocess.CalledProcessError as e:
            error_msg = f"패키지 설치 실패: {e}"
            self._save_status("failed", error=error_msg)
            self.finished.emit(False, error_msg)
            
        except Exception as e:
            error_msg = f"설치 중 오류 발생: {str(e)}"
            self._save_status("failed", error=error_msg)
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
    
    def _initialize_paddleocr(self):
        """PaddleOCR 초기화 및 모델 다운로드"""
        init_code = """
from paddleocr import PaddleOCR
import os
# 로그 레벨 설정
os.environ['PPOCR_DEBUG'] = '0'
# 한국어 OCR 초기화 (모델 자동 다운로드)
# PaddleOCR 2.7.0에서는 lang='korean' 지정 시 자동으로 적절한 모델 사용
ocr = PaddleOCR(
    lang='korean',              # 한국어 모델
    use_angle_cls=True         # 텍스트 각도 분류
)
print("PaddleOCR initialized successfully")
"""
        
        # Python 스크립트로 실행
        result = subprocess.run(
            [sys.executable, "-c", init_code],
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"PaddleOCR 초기화 실패: {result.stderr}")
    
    def _save_status(self, status, error=None):
        """설치 상태 저장"""
        status_data = {
            "status": status,
            "ocr_type": "paddleocr",
            "version": "2.0.0",
            "timestamp": time.time()
        }
        
        if error:
            status_data["error"] = error
            
        with open(self.status_file, 'w', encoding='utf-8') as f:
            json.dump(status_data, f, ensure_ascii=False, indent=2)