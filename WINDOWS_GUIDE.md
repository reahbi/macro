# Windows 실행 가이드

이 문서는 Excel 매크로 자동화 도구를 Windows 환경에서 실행하는 방법을 설명합니다.

## Windows 네이티브 실행의 장점

Windows에서 직접 실행하면 다음과 같은 모든 기능이 완전하게 작동합니다:
- 화면 캡처 및 이미지 인식
- 마우스/키보드 자동화
- 투명 오버레이 렌더링  
- 클립보드 접근
- 멀티모니터 지원

## 사전 준비사항

1. **Python 설치**
   - [python.org](https://www.python.org/downloads/)에서 Python 3.8 이상 버전 다운로드
   - 설치 시 "Add Python to PATH" 옵션 체크 필수

2. **프로젝트 위치**
   - 프로젝트는 C:\mag\macro에 위치
   - C드라이브에서 직접 실행으로 최적화됨

## 실행 방법

### 방법 1: 간단 실행 (권장)

1. Windows 탐색기에서 프로젝트 폴더 열기:
   ```
   C:\mag\macro
   ```

2. `RUN_SIMPLE.bat` 더블클릭
   - 즉시 실행
   - 의존성이 설치되어 있어야 함

### 방법 2: 완전 설치 실행

1. `WINDOWS_RUN.bat` 더블클릭
   - 의존성 자동 설치 포함
   - 최초 실행 시 권장

### 방법 3: 의존성 별도 설치

1. `INSTALL_DEPENDENCIES.bat` 더블클릭
   - 패키지만 설치

2. 이후 `RUN_SIMPLE.bat`로 실행

### 방법 4: Python 직접 실행

1. 명령 프롬프트에서 프로젝트 디렉토리로 이동:
   ```cmd
   cd C:\mag\macro
   ```

2. Python으로 직접 실행:
   ```cmd
   python run_main.py
   ```

### 방법 5: 수동 설치 및 실행

1. 가상환경 생성 (선택사항):
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

2. 패키지 설치:
   ```cmd
   pip install -r requirements.txt
   ```

5. 애플리케이션 실행:
   ```cmd
   python run_main.py
   ```

## 문제 해결

### 경로 관련 오류
프로젝트 경로가 잘못된 경우:

**해결방법**:
- 프로젝트가 C:\mag\macro에 있는지 확인
- 배치 파일을 프로젝트 폴더에서 실행

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
- 경로에 공백이 있으면 따옴표로 감싸기
- 절대 경로 사용 권장

## Windows 네이티브 실행의 장점

| 기능 | 장점 |
|------|------|
| 화면 캡처 | 완전 지원 |
| ROI 선택 | 정상 작동 |
| 클립보드 | 완전 지원 |
| 성능 | 빠른 실행 |
| 멀티모니터 | 완전 지원 |

## 권장사항

1. **실행**: C드라이브에서 직접 실행
2. **테스트**: 배치 파일 사용으로 간편화
3. **배포**: Windows 실행 파일로 패키징

## 추가 도구

Windows에서 더 나은 경험을 위해:
- **Windows Terminal**: 향상된 터미널 환경
- **PyInstaller**: 실행 파일 생성 도구

---

문제가 발생하면 프로젝트의 Issue 페이지에 보고해주세요.