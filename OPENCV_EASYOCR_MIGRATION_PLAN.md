# OpenCV/EasyOCR 중심 아키텍처 마이그레이션 계획

## 📋 개요

이 문서는 Excel Macro Automation 프로젝트를 pyautogui 의존성에서 벗어나 OpenCV, NumPy, EasyOCR을 핵심으로 하는 정확하고 강력한 자동화 시스템으로 전환하는 계획을 담고 있습니다.

## 🎯 목표

1. **pyautogui 완전 제거**: 모든 화면 제어를 OpenCV 기반으로 전환
2. **이미지/텍스트 인식 필수화**: 폴백 없이 정확한 인식 기능 제공
3. **Python 3.13 완벽 호환**: 최신 환경에서 모든 기능 정상 작동
4. **성능 및 정확도 향상**: GPU 가속 지원, 멀티스레딩 최적화

## 🔧 기술 스택 변경

### 제거할 라이브러리
- **pyautogui**: 모든 마우스/키보드 제어 및 이미지 검색
- **pillow** (단독 사용): OpenCV로 통합

### 필수 라이브러리 및 버전
```
numpy==2.2.1          # Python 3.13 호환, OpenCV 의존성 충족
opencv-python==5.0.0.xxx  # NumPy 2.x 빌드 (커스텀 빌드 필요)
easyocr==1.7.2       # 최신 버전
torch==2.5.0         # Python 3.13 지원
pynput==1.7.7        # 마우스/키보드 제어 (pyautogui 대체)
mss==9.0.2           # 고속 스크린샷
python-xlib==0.33    # Linux X11 제어 (옵션)
pywin32==308         # Windows 네이티브 API
```

## 🏗️ 아키텍처 재설계

### 1. 화면 캡처 레이어
```python
# src/core/screen_capture.py
class ScreenCapture:
    """MSS 기반 고속 화면 캡처"""
    def __init__(self):
        self.sct = mss.mss()
        self.monitors = self._detect_monitors_with_dpi()
    
    def capture_region(self, region: Tuple[int, int, int, int]) -> np.ndarray:
        """지정 영역을 NumPy 배열로 캡처"""
        # BGR to RGB 변환 포함
        # DPI 스케일링 자동 처리
```

### 2. 입력 제어 레이어
```python
# src/core/input_controller.py
class InputController:
    """pynput 기반 정밀 입력 제어"""
    def __init__(self):
        self.mouse = pynput.mouse.Controller()
        self.keyboard = pynput.keyboard.Controller()
        
    def click(self, x: int, y: int, button: str = 'left'):
        """DPI 인식 마우스 클릭"""
        # 멀티모니터 좌표 변환
        # 정밀 타이밍 제어
```

### 3. 이미지 인식 엔진
```python
# src/vision/opencv_matcher.py
class OpenCVMatcher:
    """순수 OpenCV 기반 이미지 매칭"""
    def __init__(self):
        self.template_cache = {}
        self.feature_detector = cv2.SIFT_create()  # 또는 ORB
        
    def find_image(self, template: np.ndarray, 
                   screenshot: np.ndarray,
                   method: str = 'TM_CCOEFF_NORMED') -> MatchResult:
        """다중 알고리즘 지원 이미지 검색"""
        # Template Matching
        # Feature Matching (SIFT/ORB)
        # Multi-scale detection
```

### 4. OCR 엔진
```python
# src/vision/ocr_engine.py
class OCREngine:
    """EasyOCR 기반 텍스트 인식"""
    def __init__(self, languages=['ko', 'en'], gpu=True):
        self.reader = easyocr.Reader(languages, gpu=gpu)
        self.text_cache = LRUCache(maxsize=100)
        
    def extract_text(self, image: np.ndarray, 
                     region: Optional[Tuple] = None) -> List[TextResult]:
        """고속 텍스트 추출 with 캐싱"""
        # 전처리 최적화
        # 병렬 처리
        # 결과 후처리
```

### 5. 통합 실행 엔진
```python
# src/automation/vision_executor.py
class VisionExecutor:
    """비전 기반 자동화 실행기"""
    def __init__(self):
        self.screen = ScreenCapture()
        self.input = InputController()
        self.matcher = OpenCVMatcher()
        self.ocr = OCREngine()
        
    async def execute_step(self, step: MacroStep):
        """비동기 단계 실행"""
        # 병렬 처리 지원
        # 실시간 피드백
        # 정확도 기반 재시도
```

## 📝 구현 단계

### Phase 1: 기반 구축 (1-2주)
1. **환경 설정**
   - Python 3.13용 OpenCV 커스텀 빌드
   - 의존성 관리 시스템 구축
   - 가상환경 템플릿 생성

2. **코어 모듈 개발**
   - ScreenCapture 클래스 구현
   - InputController 클래스 구현
   - 기본 테스트 작성

### Phase 2: 비전 엔진 구현 (2-3주)
1. **OpenCV 매처 개발**
   - Template matching 구현
   - Feature matching 구현
   - Multi-scale detection

2. **OCR 엔진 최적화**
   - EasyOCR 통합
   - 전처리 파이프라인
   - 캐싱 시스템

### Phase 3: 기존 코드 마이그레이션 (3-4주)
1. **Executor 재구현**
   - pyautogui 호출 제거
   - 새로운 API로 교체
   - 에러 처리 강화

2. **UI 다이얼로그 업데이트**
   - 이미지 캡처 로직 변경
   - 실시간 미리보기 개선
   - 정확도 표시 추가

### Phase 4: 성능 최적화 (4-5주)
1. **병렬 처리**
   - 비동기 실행 구현
   - 멀티스레딩 최적화
   - GPU 가속 활용

2. **메모리 최적화**
   - 이미지 캐싱 전략
   - 메모리 풀 구현
   - 가비지 컬렉션 튜닝

### Phase 5: 테스트 및 안정화 (5-6주)
1. **종합 테스트**
   - 단위 테스트 100% 커버리지
   - 통합 테스트 시나리오
   - 성능 벤치마크

2. **문서화**
   - API 문서 작성
   - 마이그레이션 가이드
   - 사용자 매뉴얼 업데이트

## 🚀 핵심 개선사항

### 1. 정확도 향상
- **이미지 매칭**: 99%+ 정확도 (SIFT/ORB 특징점)
- **OCR 인식**: 95%+ 정확도 (EasyOCR 최적화)
- **좌표 정밀도**: 서브픽셀 수준 정확도

### 2. 성능 개선
- **화면 캡처**: 10ms 이하 (MSS 사용)
- **이미지 검색**: 50ms 이하 (GPU 가속)
- **OCR 처리**: 100ms 이하 (배치 처리)

### 3. 안정성 강화
- **에러 복구**: 자동 재시도 메커니즘
- **메모리 관리**: 누수 방지 설계
- **크래시 방지**: 예외 처리 강화

## 🔄 마이그레이션 전략

### 1. 호환성 레이어
```python
# src/compatibility/pyautogui_compat.py
class PyAutoGUICompat:
    """기존 코드를 위한 임시 호환성 레이어"""
    def click(self, x, y):
        return input_controller.click(x, y)
    
    def locateOnScreen(self, image):
        return opencv_matcher.find_image(image)
```

### 2. 점진적 전환
1. 새로운 기능부터 신규 아키텍처 적용
2. 기존 기능은 호환성 레이어 통해 작동
3. 단계별로 레거시 코드 제거

### 3. 롤백 계획
- Git 브랜치 전략으로 안전한 전환
- 기능별 feature flag 도입
- A/B 테스트를 통한 검증

## 📊 예상 결과

### Before (pyautogui)
- 이미지 검색 성공률: 70-80%
- OCR 인식률: 사용 불가
- 실행 속도: 느림
- 멀티모니터: 제한적

### After (OpenCV/EasyOCR)
- 이미지 검색 성공률: 95-99%
- OCR 인식률: 90-95%
- 실행 속도: 5-10배 향상
- 멀티모니터: 완벽 지원

## 🛠️ 필요 리소스

1. **개발 환경**
   - CUDA 지원 GPU (선택사항)
   - 16GB+ RAM
   - Visual Studio 2022 (Windows)

2. **빌드 도구**
   - CMake 3.20+
   - Python 3.13 개발 헤더
   - OpenCV 소스 코드

3. **테스트 환경**
   - 다중 모니터 설정
   - 다양한 DPI 설정
   - 한국어/영어 혼합 텍스트

## 📅 일정표

| 주차 | 작업 내용 | 산출물 |
|------|-----------|---------|
| 1-2 | 기반 구축 | 코어 모듈, 빌드 시스템 |
| 3-4 | 비전 엔진 | OpenCV/OCR 통합 |
| 5-6 | 마이그레이션 | 기존 코드 전환 |
| 7-8 | 최적화 | 성능 개선 |
| 9-10 | 테스트 | 안정화 및 문서화 |

## 🎯 성공 지표

1. **기능적 지표**
   - 모든 기존 기능 100% 작동
   - 새로운 OCR 기능 추가
   - 이미지 인식 정확도 95%+

2. **성능 지표**
   - 실행 속도 5배 향상
   - 메모리 사용량 50% 감소
   - CPU 사용률 30% 감소

3. **품질 지표**
   - 코드 커버리지 90%+
   - 버그 발생률 80% 감소
   - 사용자 만족도 향상

---

이 계획을 통해 Excel Macro Automation은 더 정확하고, 빠르고, 안정적인 자동화 도구로 진화할 것입니다.