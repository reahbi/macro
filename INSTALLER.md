# Excel Macro Automation 설치 프로그램 가이드

## 개요
Excel Macro Automation을 사용자 친화적인 설치 프로그램으로 배포하기 위한 가이드입니다.
EasyOCR 텍스트 추출 기능을 필수 기능으로 포함하는 2단계 설치 방식을 채택합니다.

## 설치 전략: 스마트 2단계 설치

### 1단계: 빠른 초기 설치 (80MB, 30초)
- 핵심 애플리케이션 설치
- OCR 다운로더 모듈 포함
- 기본 UI 및 Excel 처리 기능

### 2단계: 첫 실행 시 필수 구성요소 설치 (300MB, 2-3분)
- EasyOCR 및 의존성 자동 다운로드
- 진행률 표시와 함께 백그라운드 설치
- 설치 중에도 기본 기능 사용 가능

## 기술 스택

### 빌드 도구
- **PyInstaller**: Python 코드를 실행 파일로 변환
- **Inno Setup** 또는 **NSIS**: Windows 설치 프로그램 생성

### 소스코드 보호
- PyInstaller `--key` 옵션으로 바이트코드 암호화
- 핵심 로직은 Cython으로 컴파일 (선택사항)

## 디렉토리 구조

```
excel-macro-automation/
├── src/                      # 소스 코드
├── resources/               # 리소스 파일
├── installer/              # 설치 프로그램 관련
│   ├── build_installer.bat # 빌드 스크립트
│   ├── installer.iss       # Inno Setup 스크립트
│   ├── ocr_installer.py    # OCR 설치 모듈
│   └── icons/             # 설치 아이콘
├── dist/                   # 빌드 출력
│   └── ExcelMacro_Setup.exe
└── releases/              # 배포 파일
    ├── core/              # 핵심 파일
    └── ocr/               # OCR 구성요소
```

## PyInstaller 설정

### excel_macro.spec
```python
# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('resources', 'resources'),
        ('installer/ocr_installer.py', 'installer'),
    ],
    hiddenimports=[
        'PyQt5',
        'pandas',
        'openpyxl',
        'pyautogui',
        'cryptography',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['easyocr', 'torch', 'torchvision'],  # OCR은 별도 설치
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='ExcelMacro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='resources/icons/app.ico',
    version='version_info.txt'
)
```

## Inno Setup 스크립트

### installer.iss
```ini
[Setup]
AppName=Excel Macro Automation
AppVersion=1.0.0
AppPublisher=Your Company
AppPublisherURL=https://yourcompany.com
DefaultDirName={autopf}\ExcelMacro
DefaultGroupName=Excel Macro
UninstallDisplayIcon={app}\ExcelMacro.exe
Compression=lzma2
SolidCompression=yes
OutputDir=..\dist
OutputBaseFilename=ExcelMacro_Setup
SetupIconFile=icons\setup.ico
WizardStyle=modern

[Languages]
Name: "korean"; MessagesFile: "compiler:Languages\Korean.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\dist\ExcelMacro.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\resources\*"; DestDir: "{app}\resources"; Flags: ignoreversion recursesubdirs
Source: "ocr_installer.py"; DestDir: "{app}\installer"; Flags: ignoreversion

[Icons]
Name: "{group}\Excel Macro"; Filename: "{app}\ExcelMacro.exe"
Name: "{group}\{cm:UninstallProgram,Excel Macro}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Excel Macro"; Filename: "{app}\ExcelMacro.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"

[Run]
Filename: "{app}\ExcelMacro.exe"; Description: "{cm:LaunchProgram,Excel Macro}"; Flags: nowait postinstall skipifsilent

[Code]
function InitializeSetup(): Boolean;
begin
  Result := True;
end;
```

## OCR 설치 모듈

### ocr_installer.py
```python
import os
import sys
import json
import hashlib
import zipfile
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

class OCRInstaller:
    """EasyOCR 구성요소 설치 관리자"""
    
    GITHUB_REPO = "https://github.com/yourusername/excel-macro-automation"
    OCR_VERSION = "1.0.0"
    
    COMPONENTS = {
        'pytorch_cpu': {
            'filename': 'pytorch_cpu.whl',
            'size': 157286400,  # 150MB
            'sha256': 'YOUR_SHA256_HASH_HERE',
            'required': True
        },
        'easyocr_models': {
            'filename': 'easyocr_models.zip',
            'size': 209715200,  # 200MB
            'sha256': 'YOUR_SHA256_HASH_HERE',
            'required': True
        }
    }
    
    def __init__(self, install_dir=None):
        self.install_dir = Path(install_dir or os.path.expanduser("~/.excel_macro/ocr"))
        self.install_dir.mkdir(parents=True, exist_ok=True)
        self.progress_callback = None
        
    def is_installed(self):
        """OCR 구성요소 설치 여부 확인"""
        marker_file = self.install_dir / "installed.json"
        if not marker_file.exists():
            return False
            
        try:
            with open(marker_file, 'r') as f:
                installed_info = json.load(f)
            return installed_info.get('version') == self.OCR_VERSION
        except:
            return False
    
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
        
        try:
            with urlopen(req) as response:
                total_size = int(response.headers.get('Content-Length', 0))
                if downloaded:
                    total_size += downloaded
                
                with open(filepath, mode) as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if self.progress_callback:
                            progress = (downloaded / total_size) * 100 if total_size else 0
                            self.progress_callback(progress, downloaded, total_size)
                            
            return True
            
        except URLError as e:
            print(f"Download error: {e}")
            return False
    
    def verify_file(self, filepath, expected_hash):
        """파일 무결성 검증"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        return sha256_hash.hexdigest() == expected_hash
    
    def install_components(self, progress_callback=None):
        """OCR 구성요소 설치"""
        self.progress_callback = progress_callback
        
        for comp_id, comp_info in self.COMPONENTS.items():
            if not comp_info['required']:
                continue
                
            # 다운로드 URL
            url = f"{self.GITHUB_REPO}/releases/download/ocr-v{self.OCR_VERSION}/{comp_info['filename']}"
            filepath = self.install_dir / comp_info['filename']
            
            # 다운로드
            print(f"Downloading {comp_id}...")
            if not self.download_file(url, filepath, comp_info['size']):
                raise Exception(f"Failed to download {comp_id}")
            
            # 무결성 검증
            if not self.verify_file(filepath, comp_info['sha256']):
                filepath.unlink()  # 손상된 파일 삭제
                raise Exception(f"File verification failed for {comp_id}")
            
            # 압축 해제 (필요한 경우)
            if filepath.suffix == '.zip':
                print(f"Extracting {comp_id}...")
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(self.install_dir)
        
        # 설치 완료 마커
        marker_file = self.install_dir / "installed.json"
        with open(marker_file, 'w') as f:
            json.dump({
                'version': self.OCR_VERSION,
                'components': list(self.COMPONENTS.keys())
            }, f)
        
        return True

def setup_ocr_path():
    """OCR 경로를 Python 경로에 추가"""
    ocr_dir = Path.home() / ".excel_macro" / "ocr"
    if ocr_dir.exists():
        sys.path.insert(0, str(ocr_dir))
```

## 빌드 스크립트

### build_installer.bat
```batch
@echo off
echo ========================================
echo Excel Macro 설치 프로그램 빌드
echo ========================================

REM Python 가상환경 활성화 (있는 경우)
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM 1. PyInstaller로 실행 파일 생성
echo.
echo [1/3] 실행 파일 생성 중...
pyinstaller excel_macro.spec --clean

if errorlevel 1 (
    echo [ERROR] PyInstaller 빌드 실패
    pause
    exit /b 1
)

REM 2. OCR 구성요소 준비 (GitHub Release에 업로드용)
echo.
echo [2/3] OCR 구성요소 패키징 중...
python prepare_ocr_components.py

REM 3. Inno Setup으로 설치 프로그램 생성
echo.
echo [3/3] 설치 프로그램 생성 중...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer\installer.iss

if errorlevel 1 (
    echo [ERROR] Inno Setup 빌드 실패
    pause
    exit /b 1
)

echo.
echo ========================================
echo 빌드 완료!
echo 출력 파일: dist\ExcelMacro_Setup.exe
echo ========================================
pause
```

## 첫 실행 시 OCR 설치 UI

### first_run_wizard.py
```python
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
from pathlib import Path

class OCRInstallThread(QThread):
    progress = pyqtSignal(int, int, int)  # percent, downloaded, total
    finished = pyqtSignal(bool, str)  # success, message
    
    def run(self):
        try:
            from installer.ocr_installer import OCRInstaller
            installer = OCRInstaller()
            
            if installer.is_installed():
                self.finished.emit(True, "이미 설치됨")
                return
            
            def progress_callback(percent, downloaded, total):
                self.progress.emit(int(percent), downloaded, total)
            
            installer.install_components(progress_callback)
            self.finished.emit(True, "설치 완료")
            
        except Exception as e:
            self.finished.emit(False, str(e))

class FirstRunWizard(QWizard):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Excel Macro 초기 설정")
        self.setFixedSize(600, 400)
        
        # 환영 페이지
        self.welcome_page = self.create_welcome_page()
        self.addPage(self.welcome_page)
        
        # 설치 페이지
        self.install_page = self.create_install_page()
        self.addPage(self.install_page)
        
        # 완료 페이지
        self.complete_page = self.create_complete_page()
        self.addPage(self.complete_page)
    
    def create_welcome_page(self):
        page = QWizardPage()
        page.setTitle("Excel Macro Automation에 오신 것을 환영합니다!")
        
        layout = QVBoxLayout()
        
        info_label = QLabel(
            "텍스트 검색 기능을 사용하기 위해\n"
            "필수 구성요소를 설치해야 합니다.\n\n"
            "다운로드 크기: 약 300MB\n"
            "예상 시간: 2-3분 (인터넷 속도에 따라 다름)\n\n"
            "설치를 진행하시겠습니까?"
        )
        layout.addWidget(info_label)
        
        page.setLayout(layout)
        return page
    
    def create_install_page(self):
        page = QWizardPage()
        page.setTitle("필수 구성요소 설치 중...")
        page.setCommitPage(True)
        
        layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("준비 중...")
        layout.addWidget(self.status_label)
        
        self.details_text = QTextEdit()
        self.details_text.setReadOnly(True)
        self.details_text.setMaximumHeight(100)
        layout.addWidget(self.details_text)
        
        page.setLayout(layout)
        
        # 설치 시작
        self.install_thread = OCRInstallThread()
        self.install_thread.progress.connect(self.update_progress)
        self.install_thread.finished.connect(self.install_finished)
        
        return page
    
    def update_progress(self, percent, downloaded, total):
        self.progress_bar.setValue(percent)
        mb_downloaded = downloaded / (1024 * 1024)
        mb_total = total / (1024 * 1024)
        self.status_label.setText(f"다운로드 중: {mb_downloaded:.1f}MB / {mb_total:.1f}MB")
    
    def install_finished(self, success, message):
        if success:
            self.status_label.setText("설치 완료!")
            self.next()
        else:
            QMessageBox.critical(self, "설치 실패", f"설치 중 오류 발생:\n{message}")
    
    def create_complete_page(self):
        page = QWizardPage()
        page.setTitle("설정 완료")
        
        layout = QVBoxLayout()
        
        complete_label = QLabel(
            "모든 구성요소가 성공적으로 설치되었습니다!\n\n"
            "이제 텍스트 검색 기능을 포함한\n"
            "모든 기능을 사용할 수 있습니다."
        )
        layout.addWidget(complete_label)
        
        page.setLayout(layout)
        return page
    
    def showEvent(self, event):
        super().showEvent(event)
        # 설치 페이지에 도달하면 설치 시작
        if self.currentPage() == self.install_page:
            QTimer.singleShot(100, self.install_thread.start)
```

## GitHub Release 구조

```
releases/
├── v1.0.0/
│   ├── ExcelMacro_Setup.exe (80MB) - 기본 설치 프로그램
│   ├── ocr-v1.0.0/
│   │   ├── pytorch_cpu.whl (150MB)
│   │   ├── easyocr_models.zip (200MB)
│   │   └── checksums.txt
│   └── release_notes.md
```

## 배포 프로세스

1. **빌드**
   ```batch
   build_installer.bat
   ```

2. **GitHub Release 생성**
   - 태그: v1.0.0
   - ExcelMacro_Setup.exe 업로드
   - OCR 구성요소 별도 업로드

3. **테스트**
   - 깨끗한 Windows 환경에서 설치
   - OCR 자동 다운로드 확인
   - 모든 기능 작동 확인

## 업데이트 메커니즘

향후 자동 업데이트 기능 추가:
- 앱 시작 시 버전 확인
- 새 버전 알림
- 백그라운드 다운로드
- 재시작 후 적용

## 문제 해결

### 일반적인 문제
1. **바이러스 백신 오탐지**
   - 코드 서명 인증서 고려
   - 백신 업체에 화이트리스트 요청

2. **OCR 다운로드 실패**
   - 재시도 메커니즘
   - 오프라인 설치 옵션 제공

3. **권한 문제**
   - 관리자 권한 없이 설치 가능하도록 설계
   - 사용자 폴더에 설치

## 라이선스 및 상업화 준비

### 라이선스 확인 모듈 (향후)
```python
class LicenseManager:
    def check_license(self):
        # 무료 버전: 기본 기능
        # Pro 버전: 고급 기능 잠금 해제
        pass
```

### 원격 측정 (선택사항)
- 사용 통계 수집
- 오류 리포팅
- 기능 사용 패턴 분석