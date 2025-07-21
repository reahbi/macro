"""
OCR Installer for Excel Macro Automation
This module will be packaged with the installer
"""

import os
import sys
import json
import hashlib
import zipfile
import time
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

class OCRInstaller:
    """EasyOCR 구성요소 설치 관리자"""
    
    # GitHub Release URL (실제 배포 시 변경 필요)
    GITHUB_REPO = "https://github.com/yourusername/excel-macro-automation"
    OCR_VERSION = "1.0.0"
    
    # 구성요소 정보 (실제 파일 크기와 해시는 빌드 시 업데이트)
    COMPONENTS = {
        'pytorch_cpu': {
            'filename': 'pytorch_cpu.whl',
            'size': 157286400,  # 150MB
            'sha256': 'TO_BE_UPDATED_AT_BUILD_TIME',
            'required': True,
            'description': 'PyTorch CPU 런타임'
        },
        'easyocr_package': {
            'filename': 'easyocr_package.whl', 
            'size': 10485760,  # 10MB
            'sha256': 'TO_BE_UPDATED_AT_BUILD_TIME',
            'required': True,
            'description': 'EasyOCR 패키지'
        },
        'korean_model': {
            'filename': 'korean_g2.pth',
            'size': 67108864,  # 64MB
            'sha256': 'TO_BE_UPDATED_AT_BUILD_TIME',
            'required': True,
            'description': '한국어 인식 모델'
        },
        'english_model': {
            'filename': 'english_g2.pth',
            'size': 67108864,  # 64MB  
            'sha256': 'TO_BE_UPDATED_AT_BUILD_TIME',
            'required': True,
            'description': '영어 인식 모델'
        },
        'craft_model': {
            'filename': 'craft_mlt_25k.pth',
            'size': 20971520,  # 20MB
            'sha256': 'TO_BE_UPDATED_AT_BUILD_TIME',
            'required': True,
            'description': '텍스트 감지 모델'
        }
    }
    
    def __init__(self, install_dir=None):
        self.install_dir = Path(install_dir or os.path.expanduser("~/.excel_macro/ocr"))
        self.install_dir.mkdir(parents=True, exist_ok=True)
        self.models_dir = self.install_dir / "models"
        self.models_dir.mkdir(exist_ok=True)
        self.progress_callback = None
        self.cancel_requested = False
        
    def is_installed(self):
        """OCR 구성요소 설치 여부 확인"""
        marker_file = self.install_dir / "installed.json"
        if not marker_file.exists():
            return False
            
        try:
            with open(marker_file, 'r', encoding='utf-8') as f:
                installed_info = json.load(f)
            
            # 버전 확인
            if installed_info.get('version') != self.OCR_VERSION:
                return False
                
            # 모든 필수 파일 확인
            for comp_id, comp_info in self.COMPONENTS.items():
                if comp_info['required']:
                    if comp_id.endswith('_model'):
                        filepath = self.models_dir / comp_info['filename']
                    else:
                        filepath = self.install_dir / comp_info['filename']
                    
                    if not filepath.exists():
                        return False
                        
            return True
            
        except Exception:
            return False
    
    def get_download_url(self, component_info):
        """컴포넌트 다운로드 URL 생성"""
        # 실제 배포 시에는 GitHub Releases 또는 CDN URL 사용
        filename = component_info['filename']
        return f"{self.GITHUB_REPO}/releases/download/ocr-v{self.OCR_VERSION}/{filename}"
    
    def download_file(self, url, filepath, expected_size=None):
        """파일 다운로드 (재개 지원)"""
        headers = {}
        mode = 'wb'
        downloaded = 0
        
        # 이어받기 확인
        if filepath.exists():
            downloaded = filepath.stat().st_size
            if expected_size and downloaded >= expected_size:
                return True
            headers['Range'] = f'bytes={downloaded}-'
            mode = 'ab'
        
        req = Request(url, headers=headers)
        req.add_header('User-Agent', 'Excel-Macro-Automation/1.0')
        
        try:
            with urlopen(req, timeout=30) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                if downloaded:
                    total_size += downloaded
                
                with open(filepath, mode) as f:
                    chunk_size = 8192
                    last_progress_time = time.time()
                    
                    while not self.cancel_requested:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # 진행률 콜백 (0.1초마다)
                        current_time = time.time()
                        if self.progress_callback and current_time - last_progress_time > 0.1:
                            progress = (downloaded / total_size) * 100 if total_size else 0
                            self.progress_callback(progress, downloaded, total_size)
                            last_progress_time = current_time
                            
            return not self.cancel_requested
            
        except URLError as e:
            print(f"Download error: {e}")
            return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
    
    def verify_file(self, filepath, expected_hash):
        """파일 무결성 검증"""
        if expected_hash == 'TO_BE_UPDATED_AT_BUILD_TIME':
            # 개발 중에는 해시 검증 스킵
            return True
            
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest() == expected_hash
    
    def install_components(self, progress_callback=None):
        """OCR 구성요소 설치"""
        self.progress_callback = progress_callback
        self.cancel_requested = False
        
        total_size = sum(comp['size'] for comp in self.COMPONENTS.values() if comp['required'])
        total_downloaded = 0
        
        try:
            for comp_id, comp_info in self.COMPONENTS.items():
                if not comp_info['required'] or self.cancel_requested:
                    continue
                
                # 파일 경로 결정
                if comp_id.endswith('_model'):
                    filepath = self.models_dir / comp_info['filename']
                else:
                    filepath = self.install_dir / comp_info['filename']
                
                # 이미 다운로드된 크기
                existing_size = filepath.stat().st_size if filepath.exists() else 0
                
                # 다운로드 URL
                url = self.get_download_url(comp_info)
                
                # 진행률 래퍼
                def component_progress(percent, downloaded, total):
                    overall_downloaded = total_downloaded + downloaded - existing_size
                    overall_percent = (overall_downloaded / total_size) * 100
                    if self.progress_callback:
                        self.progress_callback(
                            overall_percent, 
                            overall_downloaded, 
                            total_size
                        )
                
                # 다운로드
                print(f"다운로드 중: {comp_info['description']}...")
                self.progress_callback = component_progress
                
                if not self.download_file(url, filepath, comp_info['size']):
                    if self.cancel_requested:
                        raise Exception("설치가 취소되었습니다")
                    raise Exception(f"{comp_info['description']} 다운로드 실패")
                
                # 무결성 검증
                if not self.verify_file(filepath, comp_info['sha256']):
                    filepath.unlink()  # 손상된 파일 삭제
                    raise Exception(f"{comp_info['description']} 파일 검증 실패")
                
                total_downloaded += comp_info['size'] - existing_size
            
            # Python 경로 설정 파일 생성
            self._create_pth_file()
            
            # 설치 완료 마커
            marker_file = self.install_dir / "installed.json"
            with open(marker_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'version': self.OCR_VERSION,
                    'components': list(self.COMPONENTS.keys()),
                    'install_date': time.strftime('%Y-%m-%d %H:%M:%S')
                }, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"설치 오류: {e}")
            # 실패 시 부분적으로 다운로드된 파일 정리 (선택사항)
            return False
    
    def _create_pth_file(self):
        """Python 경로 파일 생성"""
        pth_content = f"""# Excel Macro OCR paths
import sys
sys.path.insert(0, r'{self.install_dir}')
"""
        pth_file = self.install_dir / "excel_macro_ocr.pth"
        with open(pth_file, 'w', encoding='utf-8') as f:
            f.write(pth_content)
    
    def cancel_installation(self):
        """설치 취소"""
        self.cancel_requested = True
    
    def uninstall(self):
        """OCR 구성요소 제거"""
        import shutil
        
        if self.install_dir.exists():
            shutil.rmtree(self.install_dir)
            return True
        return False


def setup_ocr_path():
    """OCR 경로를 Python 경로에 추가"""
    ocr_dir = Path.home() / ".excel_macro" / "ocr"
    if ocr_dir.exists():
        if str(ocr_dir) not in sys.path:
            sys.path.insert(0, str(ocr_dir))
        
        # 모델 디렉토리도 EasyOCR이 찾을 수 있도록 설정
        models_dir = ocr_dir / "models"
        if models_dir.exists():
            os.environ['EASYOCR_MODULE_PATH'] = str(models_dir)


# 테스트용 코드
if __name__ == "__main__":
    print("OCR Installer Test")
    print("-" * 50)
    
    installer = OCRInstaller()
    
    if installer.is_installed():
        print("✓ OCR이 이미 설치되어 있습니다.")
    else:
        print("✗ OCR이 설치되지 않았습니다.")
        print("\n실제 설치는 프로그램 첫 실행 시 진행됩니다.")