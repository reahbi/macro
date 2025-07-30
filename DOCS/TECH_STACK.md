# Excel Macro Automation - 기술 스택 및 의존성

## 개요
Excel Macro Automation은 Windows 환경에서 동작하는 PyQt5 기반의 데스크톱 애플리케이션입니다. 
Excel 파일을 읽어 반복적인 작업을 자동화하는 스크린 자동화 솔루션입니다.

## 기술 스택

### 1. 프로그래밍 언어
- **Python 3.8+** (권장: Python 3.8 ~ 3.11)
  - Python 3.13은 일부 의존성 호환성 문제로 권장하지 않음

### 2. GUI 프레임워크
- **PyQt5** (>=5.15.0)
  - 메인 GUI 프레임워크
  - 시그널/슬롯 패턴 사용
  - MVC 아키텍처 구현

### 3. 데이터 처리
- **pandas** (>=1.3.0)
  - Excel 파일 읽기/쓰기
  - 데이터프레임 처리
- **openpyxl** (>=3.0.0)
  - Excel 파일 포맷 지원
  - .xlsx 파일 처리
- **numpy** (>=1.21.0)
  - 배열 처리 및 이미지 연산

### 4. 화면 자동화
- **pyautogui** (>=0.9.53)
  - 마우스/키보드 자동화
  - 스크린샷 캡처
  - 이미지 매칭 (fallback)
- **pynput** (>=1.7.0)
  - 키보드/마우스 이벤트 감지
  - 낮은 수준의 입력 제어
- **mss** (>=6.1.0)
  - 고성능 스크린 캡처
  - 멀티 모니터 지원

### 5. 이미지 처리
- **opencv-python** (>=4.5.0)
  - 고급 이미지 매칭
  - 이미지 전처리
  - 템플릿 매칭
- **Pillow** (>=8.3.0)
  - 이미지 포맷 변환
  - 기본 이미지 처리

### 6. OCR (텍스트 인식)
- **paddleocr** (>=2.7.0)
  - 한국어 텍스트 인식 특화
  - GPU 가속 지원 (선택사항)
  - 경량화된 모델
  - paddlepaddle (>=2.5.0) 필요

### 7. 보안
- **cryptography** (>=3.4.0)
  - AES-256 암호화
  - 설정 파일 암호화
  - 매크로 파일 보호

### 8. 기타 도구
- **screeninfo** (>=0.8.0)
  - 모니터 정보 조회
  - 멀티 모니터 좌표 계산

## 필수 pip 패키지 설치

### 기본 설치 (필수)
```bash
pip install -r requirements.txt
```

### 패키지별 개별 설치
```bash
# GUI 프레임워크
pip install PyQt5>=5.15.0

# 데이터 처리
pip install pandas>=1.3.0 openpyxl>=3.0.0 numpy>=1.21.0

# 화면 자동화
pip install pyautogui>=0.9.53 pillow>=8.3.0 opencv-python>=4.5.0 pynput>=1.7.0

# 스크린 정보
pip install screeninfo>=0.8.0 mss>=6.1.0

# OCR (텍스트 인식)
pip install paddlepaddle>=2.5.0 paddleocr>=2.7.0

# 보안
pip install cryptography>=3.4.0
```

### 개발 도구 (선택사항)
```bash
# 코드 포맷팅
pip install black>=21.0

# 코드 린팅
pip install flake8>=3.9.0
```

## 시스템 요구사항

### 운영체제
- Windows 10/11 (필수)
- 64비트 권장

### Python 버전
- Python 3.8 이상
- Python 3.11 이하 권장
- Python 3.13은 호환성 문제 있음

### 하드웨어
- 최소 RAM: 4GB
- 권장 RAM: 8GB 이상
- GPU: CUDA 지원 GPU (OCR 가속용, 선택사항)

## 주요 의존성 관계

### OCR 스택
```
paddleocr
├── paddlepaddle
├── opencv-python
├── numpy
└── pillow
```

### GUI 스택
```
PyQt5
├── Qt5 Core
├── Qt5 Widgets
└── Qt5 Gui
```

### 이미지 처리 스택
```
opencv-python
├── numpy
└── pillow (PIL)
```

## 알려진 이슈

1. **Python 3.13 호환성**
   - 일부 패키지가 Python 3.13과 호환되지 않음
   - Python 3.11 이하 버전 사용 권장

2. **OCR 한글 인식**
   - PaddleOCR 사용으로 한글 인식률 개선

3. **PyQt5 의존성**
   - Windows에서 Qt5 런타임 필요
   - 일부 시스템에서 추가 Visual C++ 재배포 패키지 필요

## 빌드 및 배포

### 실행 파일 생성
```bash
pyinstaller excel_macro.spec
```

### 개발 환경 설정
```bash
# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

## 라이선스
- 프로젝트: MIT License
- 의존성 패키지들은 각각의 라이선스를 따름