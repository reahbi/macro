# PaddleOCR 최적화 계획 문서

## 개요
이 문서는 Excel Macro Automation 프로젝트에서 PaddleOCR이 영어, 한국어, 숫자를 정확히 인식하고 CPU에서 최적의 성능을 발휘하도록 하는 최적화 계획을 담고 있습니다.

## 현재 구현 분석

### 긍정적인 부분
1. **올바른 언어 설정**: `lang='korean'` 파라미터 사용 ✓
2. **GPU 감지 로직**: GPU 사용 가능 여부를 체크하는 코드 구현 ✓
3. **에러 처리**: 적절한 예외 처리 및 로깅 구현 ✓
4. **싱글톤 패턴**: 리소스 효율적인 인스턴스 관리 ✓

### 개선이 필요한 부분
1. **CPU 최적화 파라미터 누락**
2. **언어 모델 제한**
3. **성능 튜닝 옵션 미사용**

## 최적화 계획

### 1. PaddleOCR 초기화 파라미터 최적화

#### 현재 코드 (line 82-84)
```python
PaddleTextExtractor._ocr = PaddleOCR(
    lang='korean'           # 한국어 모델만 지정
)
```

#### 개선된 코드
```python
PaddleTextExtractor._ocr = PaddleOCR(
    lang='korean',              # 한국어 모델 (영어, 숫자 포함)
    use_gpu=False,             # CPU 사용 명시
    enable_mkldnn=True,        # MKL-DNN 가속 활성화
    cpu_threads=8,             # CPU 스레드 수 최적화
    use_tensorrt=False,        # TensorRT 비활성화 (CPU 모드)
    precision='fp32',          # CPU에서 안정적인 정밀도
    use_doc_orientation_classify=False,  # 문서 방향 분류 비활성화 (속도 향상)
    use_doc_unwarping=False,   # 문서 왜곡 보정 비활성화 (속도 향상)
    use_textline_orientation=False,  # 텍스트 라인 방향 비활성화 (속도 향상)
    det_db_thresh=0.3,         # 텍스트 감지 임계값
    det_db_box_thresh=0.5,     # 텍스트 박스 임계값
    rec_batch_num=6,           # 인식 배치 크기
    max_text_length=25,        # 최대 텍스트 길이
    use_space_char=True        # 공백 문자 인식 활성화
)
```

### 2. 다국어 지원 강화

#### 옵션 A: 한국어 모델 사용 (현재)
- 장점: 한국어에 최적화
- 단점: 영어 인식률이 상대적으로 낮을 수 있음

#### 옵션 B: 다국어 모델 사용 (권장)
```python
# 영어와 한국어를 모두 잘 인식하는 설정
PaddleTextExtractor._ocr = PaddleOCR(
    lang='ch',                 # 중국어 모델 (한글, 영어, 숫자 모두 지원)
    use_angle_cls=True,        # 텍스트 각도 분류 활성화
    cls_model_dir=None,        # 기본 분류 모델 사용
    rec_model_dir=None,        # 기본 인식 모델 사용
    det_model_dir=None,        # 기본 감지 모델 사용
    enable_mkldnn=True,
    cpu_threads=8,
    use_gpu=False
)
```

### 3. CPU 성능 최적화 전략

#### 3.1 MKL-DNN 최적화
```python
# MKL-DNN 캐시 설정
mkldnn_cache_capacity=10,      # MKL-DNN 캐시 용량
```

#### 3.2 스레드 수 동적 할당
```python
import multiprocessing

# CPU 코어 수에 따른 동적 스레드 할당
cpu_count = multiprocessing.cpu_count()
optimal_threads = max(1, min(cpu_count - 1, 8))  # 1~8 사이, CPU-1
```

#### 3.3 메모리 사용 최적화
```python
# 이미지 전처리 최적화
det_limit_side_len=960,        # 감지 이미지 크기 제한
det_limit_type='max',          # 최대 크기 제한 방식
```

### 4. 텍스트 인식 정확도 향상

#### 4.1 전처리 개선
```python
def preprocess_image_for_ocr(self, img_array):
    """OCR 전 이미지 전처리"""
    import cv2
    
    # 그레이스케일 변환
    if len(img_array.shape) == 3:
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
    else:
        gray = img_array
    
    # 노이즈 제거
    denoised = cv2.fastNlMeansDenoising(gray)
    
    # 대비 향상
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
    enhanced = clahe.apply(denoised)
    
    # 다시 RGB로 변환 (PaddleOCR 입력 형식)
    result = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
    
    return result
```

#### 4.2 후처리 개선
```python
def postprocess_text(self, text):
    """인식된 텍스트 후처리"""
    # 일반적인 OCR 오류 수정
    corrections = {
        '0': ['O', 'o'],  # 숫자 0과 알파벳 O 구분
        '1': ['l', 'I'],  # 숫자 1과 알파벳 l, I 구분
        '5': ['S'],       # 숫자 5와 알파벳 S 구분
        '8': ['B'],       # 숫자 8과 알파벳 B 구분
    }
    
    # 컨텍스트 기반 수정 로직
    return text
```

### 5. 영역별 최적화 설정

```python
class OCRConfig:
    """OCR 설정 관리 클래스"""
    
    # 일반 텍스트 설정
    GENERAL_CONFIG = {
        'det_db_thresh': 0.3,
        'det_db_box_thresh': 0.5,
        'rec_batch_num': 6,
        'max_text_length': 25
    }
    
    # 숫자 전용 설정
    NUMBER_CONFIG = {
        'det_db_thresh': 0.2,      # 더 민감한 감지
        'det_db_box_thresh': 0.4,
        'rec_batch_num': 10,       # 더 많은 배치
        'max_text_length': 15      # 짧은 텍스트
    }
    
    # 한글 텍스트 설정
    KOREAN_CONFIG = {
        'det_db_thresh': 0.35,
        'det_db_box_thresh': 0.55,
        'rec_batch_num': 4,        # 복잡한 문자를 위한 작은 배치
        'max_text_length': 30
    }
```

### 6. 성능 모니터링 및 로깅

```python
import time
from functools import wraps

def measure_performance(func):
    """성능 측정 데코레이터"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        elapsed_time = time.time() - start_time
        
        # 성능 로깅
        logger = get_logger(__name__)
        logger.info(f"{func.__name__} 실행 시간: {elapsed_time:.3f}초")
        
        # 느린 작업 경고
        if elapsed_time > 2.0:
            logger.warning(f"{func.__name__}이 {elapsed_time:.3f}초 걸렸습니다. 최적화가 필요할 수 있습니다.")
        
        return result
    return wrapper
```

### 7. 캐싱 전략

```python
from functools import lru_cache
import hashlib

class OCRCache:
    """OCR 결과 캐싱"""
    
    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size
    
    def get_hash(self, img_array):
        """이미지 해시 생성"""
        return hashlib.md5(img_array.tobytes()).hexdigest()
    
    def get(self, img_array):
        """캐시에서 결과 가져오기"""
        hash_key = self.get_hash(img_array)
        return self.cache.get(hash_key)
    
    def set(self, img_array, result):
        """캐시에 결과 저장"""
        if len(self.cache) >= self.max_size:
            # LRU 정책으로 오래된 항목 제거
            oldest = min(self.cache.items(), key=lambda x: x[1]['timestamp'])
            del self.cache[oldest[0]]
        
        hash_key = self.get_hash(img_array)
        self.cache[hash_key] = {
            'result': result,
            'timestamp': time.time()
        }
```

### 8. 배치 처리 최적화

```python
def batch_ocr_process(self, images, batch_size=5):
    """여러 이미지를 배치로 처리"""
    results = []
    
    for i in range(0, len(images), batch_size):
        batch = images[i:i + batch_size]
        
        # 배치 처리
        batch_results = self._ocr.ocr(batch, cls=True)
        
        # 결과 정리
        for result in batch_results:
            if result:
                results.extend(result)
    
    return results
```

## 구현 우선순위

### Phase 1: 즉시 적용 (높은 우선순위)
1. **CPU 최적화 파라미터 추가**
   - `enable_mkldnn=True`
   - `cpu_threads` 최적화
   - `use_gpu=False` 명시

2. **불필요한 기능 비활성화**
   - 문서 방향 분류 비활성화
   - 문서 왜곡 보정 비활성화
   - 텍스트 라인 방향 분류 비활성화

### Phase 2: 단기 개선 (중간 우선순위)
1. **이미지 전처리 파이프라인 구현**
2. **성능 모니터링 시스템 추가**
3. **기본 캐싱 메커니즘 구현**

### Phase 3: 장기 최적화 (낮은 우선순위)
1. **고급 후처리 로직 개발**
2. **영역별 최적화 설정 구현**
3. **배치 처리 시스템 구축**

## 테스트 계획

### 1. 성능 벤치마크
- 100개 샘플 이미지로 처리 시간 측정
- CPU 사용률 모니터링
- 메모리 사용량 추적

### 2. 정확도 테스트
- 한글 텍스트: 95% 이상 정확도 목표
- 영문 텍스트: 98% 이상 정확도 목표
- 숫자: 99% 이상 정확도 목표

### 3. 안정성 테스트
- 장시간 실행 테스트 (1시간 이상)
- 다양한 이미지 크기 및 품질 테스트
- 동시 처리 스트레스 테스트

## 예상 효과

1. **성능 향상**
   - OCR 처리 속도 30-50% 향상 예상
   - CPU 사용률 20% 감소 예상

2. **정확도 향상**
   - 한글 인식률 5-10% 향상
   - 영문/숫자 인식률 3-5% 향상

3. **안정성 향상**
   - 메모리 누수 방지
   - 장시간 실행 안정성 확보

## 참고 자료

- PaddleOCR 공식 문서: https://github.com/PaddlePaddle/PaddleOCR
- PaddleOCR Python SDK: https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/ppocr/quick_start.md
- 성능 최적화 가이드: https://github.com/PaddlePaddle/PaddleOCR/blob/main/docs/optimization.md