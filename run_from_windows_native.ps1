# Excel Macro Automation - Windows Native Execution
# PowerShell script for running the application directly on Windows

Write-Host "=" * 50
Write-Host "Excel Macro Automation - Windows Native Setup"
Write-Host "=" * 50

# Check if running as administrator
if (-NOT ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "이 스크립트는 관리자 권한이 필요합니다." -ForegroundColor Red
    Write-Host "PowerShell을 관리자 권한으로 다시 실행해주세요." -ForegroundColor Yellow
    pause
    exit
}

# WSL path to Windows path conversion
$wslPath = "\\wsl.localhost\Ubuntu\home\nosky\macro"
$windowsPath = "C:\ExcelMacroAutomation"

Write-Host "`n1. 프로젝트 파일 복사 중..." -ForegroundColor Green

# Create directory if not exists
if (!(Test-Path $windowsPath)) {
    New-Item -ItemType Directory -Path $windowsPath | Out-Null
}

# Copy files from WSL to Windows
Write-Host "   WSL에서 Windows로 파일 복사 중..."
Copy-Item -Path "$wslPath\*" -Destination $windowsPath -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`n2. Python 확인 중..." -ForegroundColor Green

# Check Python installation
try {
    $pythonVersion = python --version 2>&1
    Write-Host "   Python 발견: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "   Python이 설치되어 있지 않습니다." -ForegroundColor Red
    Write-Host "   Python 다운로드 페이지를 엽니다..." -ForegroundColor Yellow
    Start-Process "https://www.python.org/downloads/"
    Write-Host "   Python 설치 후 이 스크립트를 다시 실행해주세요."
    pause
    exit
}

Write-Host "`n3. 필수 패키지 설치 중..." -ForegroundColor Green

# Create virtual environment
Set-Location $windowsPath
if (!(Test-Path "venv_windows")) {
    Write-Host "   가상환경 생성 중..."
    python -m venv venv_windows
}

# Activate virtual environment and install packages
Write-Host "   패키지 설치 중 (시간이 걸릴 수 있습니다)..."
& "$windowsPath\venv_windows\Scripts\python.exe" -m pip install --upgrade pip | Out-Null
& "$windowsPath\venv_windows\Scripts\python.exe" -m pip install PyQt5 pandas openpyxl pyautogui opencv-python numpy easyocr flask

Write-Host "`n4. Windows용 실행 스크립트 생성 중..." -ForegroundColor Green

# Create run script for Windows
$runScript = @'
import sys
import os
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.absolute()
src_path = project_root / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(project_root))

# Import and run main
try:
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtCore import Qt
    
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    
    app = QApplication(sys.argv)
    
    from ui.main_window import MainWindow
    from config.settings import Settings
    
    settings = Settings()
    window = MainWindow(settings)
    window.show()
    
    print("\nExcel Macro Automation이 실행되었습니다!")
    print("Windows 네이티브 모드로 실행 중...")
    
    sys.exit(app.exec_())
    
except Exception as e:
    print(f"오류: {e}")
    import traceback
    traceback.print_exc()
    input("\n엔터를 눌러 종료...")
'@

$runScript | Out-File -FilePath "$windowsPath\run_windows.py" -Encoding UTF8

Write-Host "`n5. 배치 파일 생성 중..." -ForegroundColor Green

# Create batch file for easy execution
$batchFile = @"
@echo off
cd /d $windowsPath
call venv_windows\Scripts\activate
python run_windows.py
pause
"@

$batchFile | Out-File -FilePath "$windowsPath\ExcelMacroAutomation.bat" -Encoding ASCII

Write-Host "`n6. 바탕화면 바로가기 생성 중..." -ForegroundColor Green

# Create desktop shortcut
$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcut = (New-Object -ComObject WScript.Shell).CreateShortcut("$desktopPath\Excel Macro Automation.lnk")
$shortcut.TargetPath = "$windowsPath\ExcelMacroAutomation.bat"
$shortcut.WorkingDirectory = $windowsPath
$shortcut.IconLocation = "C:\Windows\System32\shell32.dll,13"
$shortcut.Save()

Write-Host "`n✅ 설치 완료!" -ForegroundColor Green
Write-Host "`n실행 옵션:" -ForegroundColor Yellow
Write-Host "1. 바탕화면의 'Excel Macro Automation' 바로가기 더블클릭"
Write-Host "2. $windowsPath\ExcelMacroAutomation.bat 실행"
Write-Host "3. 이 PowerShell에서: & '$windowsPath\ExcelMacroAutomation.bat'"

Write-Host "`n지금 실행하시겠습니까? (Y/N): " -NoNewline
$response = Read-Host

if ($response -eq 'Y' -or $response -eq 'y') {
    Write-Host "`n애플리케이션을 실행합니다..." -ForegroundColor Green
    Start-Process "$windowsPath\ExcelMacroAutomation.bat"
}

Write-Host "`n완료되었습니다. 엔터를 눌러 종료..." -ForegroundColor Green
pause