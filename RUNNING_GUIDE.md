# Excel Macro Automation - 실행 가이드 (C드라이브 버전)

## 📋 개요

프로젝트가 C드라이브로 이동되어 WSL 환경에서 파일 복사 없이 직접 실행할 수 있습니다.

## 🚀 빠른 시작

### 1단계: 의존성 설치 (최초 1회)
```bash
# Windows 배치 파일로 자동 설치
INSTALL_DEPENDENCIES.bat

# 또는 수동 설치
pip install -r requirements.txt
```

### 2단계: 애플리케이션 실행
```bash
# 방법 1: 간단한 실행 (권장)
RUN_SIMPLE.bat

# 방법 2: 완전한 설치 및 실행
WINDOWS_RUN.bat

# 방법 3: Python 직접 실행
python run_main.py
```

## 📁 실행 파일 설명

### 🎯 주요 실행 파일
- **`RUN_SIMPLE.bat`** - 가장 간단한 실행 방법 (추천)
- **`WINDOWS_RUN.bat`** - 의존성 설치 포함 완전 실행
- **`INSTALL_DEPENDENCIES.bat`** - 의존성만 설치

### 🐍 Python 실행 파일
- **`run_main.py`** - 기본 실행 파일 (import 문제 자동 해결)
- **`run_main_fixed.py`** - 대체 실행 파일
- **`run_simple.py`** - 최소 실행 파일

## 🔧 설치 요구사항

### 필수 요구사항
- **Windows 10/11 64-bit**
- **Python 3.8+** (현재 3.13.1 확인됨)
- **최소 화면 해상도**: 1280x720

### Python 설치 확인
```bash
# Python 버전 확인
python --version

# Python 경로 확인  
python -c "import sys; print(sys.executable)"
```

## 📦 의존성 패키지

### 핵심 패키지
- **PyQt5** - GUI 프레임워크
- **pandas, openpyxl** - Excel 파일 처리
- **pyautogui, opencv-python** - 화면 자동화
- **easyocr** - 텍스트 인식 (OCR)
- **cryptography** - 보안/암호화

### 개발 도구 (선택사항)
- **pytest, pytest-qt** - 테스트 프레임워크
- **black, flake8** - 코드 포맷팅/린팅

## 🎮 실행 방법

### 🟢 방법 1: 간단 실행 (권장)
```bash
# 프로젝트 폴더에서
RUN_SIMPLE.bat
```
- Python만 설치되어 있으면 바로 실행
- 의존성이 없으면 오류 메시지 표시

### 🟡 방법 2: 완전 실행
```bash
# 프로젝트 폴더에서  
WINDOWS_RUN.bat
```
- 의존성 자동 설치 포함
- 최초 실행 시 패키지 설치에 시간 소요

### 🔵 방법 3: Python 직접 실행
```bash
# 기본 방법
python run_main.py

# 대체 방법
python run_main_fixed.py
```

## 🔧 트러블슈팅

### Python 관련
```bash
# Python 설치 확인
python --version

# pip 업그레이드
python -m pip install --upgrade pip

# 의존성 재설치
pip install -r requirements.txt --force-reinstall
```

### 일반적인 문제

#### 1. "Python을 찾을 수 없음"
- Python이 설치되지 않았거나 PATH에 등록되지 않음
- https://python.org 에서 Python 설치
- 설치 시 "Add Python to PATH" 체크 필수

#### 2. "PyQt5 import 오류"
```bash
# PyQt5 재설치
pip install PyQt5 --force-reinstall
```

#### 3. "opencv-python 오류" 
```bash
# OpenCV 재설치
pip install opencv-python --force-reinstall
```

#### 4. "easyocr 설치 실패"
- 인터넷 연결 확인 (모델 다운로드 필요)
- 충분한 디스크 공간 확인
- 관리자 권한으로 실행

## 📊 성능 최적화

### 메모리 사용량 줄이기
- 큰 Excel 파일 처리 시 배치 처리 활용
- 실행 후 불필요한 프로그램 종료

### 실행 속도 향상
- SSD 사용 권장
- 안티바이러스 실시간 검사 예외 등록

## 🔒 보안 고려사항

- 매크로 파일(.emf)은 AES-256으로 암호화됨
- 민감한 정보는 로그에 기록되지 않음
- 인터넷 연결 불필요 (완전 오프라인 동작)

## 📝 로그 및 디버깅

### 로그 위치
- **실행 로그**: `uploads/execution_logs/`
- **애플리케이션 로그**: 콘솔 출력
- **오류 로그**: `COLLECT_ERRORS_WINDOWS.bat` 실행

### 디버그 모드
```bash
# 디버그 정보 포함 실행
python run_with_debug.py
```

## 🆘 지원

### 오류 보고
1. `COLLECT_ERRORS_WINDOWS.bat` 실행
2. 생성된 오류 보고서 확인
3. 스크린샷과 함께 문제 보고

### 추가 도움말
- `tests/manual_test_checklist.md` - 수동 테스트 가이드
- `README.md` - 기본 프로젝트 정보
- 소스코드 주석 및 docstring

---

**✅ 모든 준비가 완료되었습니다!**

이제 WSL 환경에서 파일 복사 없이 C드라이브에서 직접 Excel Macro Automation을 실행할 수 있습니다.