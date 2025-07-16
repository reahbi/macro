# Windows 실행 가이드

이 문서는 WSL에서 개발된 Excel 매크로 자동화 도구를 Windows 네이티브 환경에서 실행하는 방법을 설명합니다.

## 왜 Windows에서 직접 실행해야 하나요?

WSL(Windows Subsystem for Linux)에서 GUI 애플리케이션을 실행할 때 다음과 같은 제약사항이 있습니다:
- 화면 캡처 기능이 제대로 작동하지 않음
- 마우스/키보드 이벤트 캡처 문제
- 투명 오버레이 렌더링 문제
- 클립보드 접근 제한

Windows에서 직접 실행하면 이러한 문제가 해결됩니다.

## 사전 준비사항

1. **Python 설치**
   - [python.org](https://www.python.org/downloads/)에서 Python 3.8 이상 버전 다운로드
   - 설치 시 "Add Python to PATH" 옵션 체크 필수

2. **파일 접근**
   - WSL 파일은 `\\wsl$\Ubuntu\home\사용자명\macro` 경로로 접근 가능
   - 또는 Windows 폴더로 프로젝트 복사

## 실행 방법

### 방법 1: 간단한 실행기 사용 (권장)

1. Windows 탐색기에서 프로젝트 폴더 열기:
   ```
   \\wsl.localhost\Ubuntu-22.04\home\nosky\macro
   ```

2. `RUN_ON_WINDOWS.bat` 더블클릭
   - UNC 경로 문제를 자동으로 해결
   - 임시 폴더에 복사 후 실행

### 방법 2: 일반 배치 파일 사용

1. `run_windows.bat` 더블클릭
   - UNC 경로 자동 처리
   - 가상환경 지원

### 방법 3: PowerShell 사용

1. PowerShell을 관리자 권한으로 실행

2. 프로젝트 디렉토리로 이동:
   ```powershell
   cd \\wsl$\Ubuntu\home\nosky\macro
   ```

3. PowerShell 스크립트 실행:
   ```powershell
   .\run_windows.ps1
   ```

   실행 정책 오류가 발생하면:
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

### 방법 4: 수동 실행

1. 명령 프롬프트 또는 PowerShell 열기

2. 프로젝트 디렉토리로 이동

3. 가상환경 생성 및 활성화:
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

4. 패키지 설치:
   ```cmd
   pip install -r requirements.txt
   ```

5. 애플리케이션 실행:
   ```cmd
   python run_main.py
   ```

## 문제 해결

### UNC 경로 오류
WSL 경로에서 직접 실행 시 발생하는 오류:
```
'\\wsl.localhost\Ubuntu-22.04\...' 위의 경로를 현재 디렉터리로 하여 CMD.EXE가 실행되었습니다.
UNC 경로는 지원되지 않습니다.
```

**해결방법**:
- `RUN_ON_WINDOWS.bat` 사용 (자동으로 로컬 폴더로 복사)
- 프로젝트를 C:\ 드라이브로 복사 후 실행

### Python을 찾을 수 없음
- Python이 PATH에 추가되었는지 확인
- `python --version` 명령으로 설치 확인

### 패키지 설치 오류
- pip 업그레이드: `python -m pip install --upgrade pip`
- 특정 패키지 수동 설치: `pip install PyQt5`

### GUI 관련 문제
- Windows 디스플레이 스케일링 설정 확인
- 그래픽 드라이버 업데이트

### 파일 경로 문제
- WSL 경로 사용 시 `\\wsl$\` 프리픽스 확인
- 경로에 공백이 있으면 따옴표로 감싸기

## 주요 차이점

| 기능 | WSL | Windows Native |
|------|-----|----------------|
| 화면 캡처 | 제한적 | 완전 지원 |
| ROI 선택 | 불안정 | 정상 작동 |
| 클립보드 | 제한적 | 완전 지원 |
| 성능 | 약간 느림 | 빠름 |

## 권장사항

1. **개발**: WSL/VSCode에서 진행
2. **테스트/실행**: Windows PowerShell에서 실행
3. **배포**: Windows 실행 파일로 패키징

## 추가 도구

Windows에서 더 나은 경험을 위해:
- **Windows Terminal**: 향상된 터미널 환경
- **PyInstaller**: 실행 파일 생성 도구

---

문제가 발생하면 프로젝트의 Issue 페이지에 보고해주세요.