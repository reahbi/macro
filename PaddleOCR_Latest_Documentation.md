# PaddleOCR 최신 버전 문서 (2024-2025)

## 목차
1. [최신 버전 정보](#최신-버전-정보)
2. [주요 기능 및 개선사항](#주요-기능-및-개선사항)
3. [API 파라미터 가이드](#api-파라미터-가이드)
4. [한국어 지원 현황](#한국어-지원-현황)
5. [초기화 파라미터](#초기화-파라미터)
6. [성능 최적화 파라미터](#성능-최적화-파라미터)
7. [사용 예제](#사용-예제)

## 최신 버전 정보

### PaddleOCR 3.0 (2025년 5월 20일 출시)
- **최신 버전**: PaddleOCR 3.0.3 (2025년 6월 26일)
- **호환성**: PaddlePaddle 3.0 프레임워크와 완전 호환

### 주요 모델 버전
- **PP-OCRv5**: 최신 OCR 모델로 13% 정확도 향상
- **PP-StructureV3**: 고정밀 다중 레이아웃 PDF 파싱
- **PP-ChatOCRv4**: 핵심 정보 추출 특화

## 주요 기능 및 개선사항

### PP-OCRv5 특징
1. **단일 모델로 5가지 텍스트 타입 지원**
   - 중국어 간체
   - 중국어 번체
   - 영어
   - 일본어
   - 병음(Pinyin)

2. **성능 향상**
   - PP-OCRv4 대비 13% 정확도 향상
   - 복잡한 손글씨 인식 지원

3. **모델 구성 변경**
   - 기본 모델이 모바일에서 서버 모델로 변경 (정확도 우선)
   - `limit_side_len` 파라미터 기본값: 736 → 64

## API 파라미터 가이드

### 기본 초기화 (Python)

```python
from paddleocr import PaddleOCR

# 최소 파라미터로 초기화
ocr = PaddleOCR(
    lang='korean',              # 한국어 모델 (영어, 숫자 포함)
    use_angle_cls=True         # 텍스트 각도 분류 활성화
)

# OCR 실행
result = ocr.ocr("image.jpg")
```

### 지원되는 주요 파라미터

#### 필수 파라미터
- `lang`: 언어 설정 (예: 'korean', 'en', 'ch')
- `use_angle_cls`: 텍스트 각도 분류 활성화 여부 (bool)

#### 제거된 파라미터 (최신 버전에서 미지원)
- ❌ `use_gpu` - GPU는 자동 감지
- ❌ `show_log` - 로그 표시 제어 불가
- ❌ `use_space_char` - 공백 문자 인식 제어 불가
- ❌ `enable_mkldnn` - MKL-DNN 자동 적용
- ❌ `cpu_threads` - CPU 스레드 자동 관리

## 한국어 지원 현황

### 현재 상태 (2025년 기준)
- ✅ **PaddleOCR 2.x**: 한국어 완전 지원
- ❌ **PP-OCRv5**: 한국어 미지원 (향후 업데이트 예정)

### 한국어 OCR 사용법 (PaddleOCR 2.x)

```python
from paddleocr import PaddleOCR, draw_ocr
from PIL import Image

# 한국어 OCR 초기화
ocr = PaddleOCR(lang='korean')

# 이미지 처리
img_path = 'korean_text.jpg'
result = ocr.ocr(img_path)

# 결과 출력
for line in result[0]:
    print(f"텍스트: {line[1][0]}, 신뢰도: {line[1][1]:.3f}")

# 시각화 (한글 폰트 필요)
image = Image.open(img_path).convert('RGB')
boxes = [line[0] for line in result[0]]
txts = [line[1][0] for line in result[0]]
scores = [line[1][1] for line in result[0]]
im_show = draw_ocr(image, boxes, txts, scores, font_path='NanumGothic.ttf')
```

## 초기화 파라미터

### PaddleOCR() 생성자 파라미터

```python
PaddleOCR(
    # 언어 및 모델 설정
    lang='korean',                        # 언어 설정
    use_angle_cls=True,                  # 텍스트 각도 분류
    
    # 모델 경로 (선택사항)
    text_detection_model_dir=None,       # 텍스트 감지 모델 경로
    text_recognition_model_dir=None,     # 텍스트 인식 모델 경로
    
    # 배치 크기 설정
    text_recognition_batch_size=1,       # 텍스트 인식 배치 크기
    
    # 문서 처리 옵션
    use_doc_orientation_classify=False,  # 문서 방향 분류
    use_doc_unwarping=False,            # 텍스트 이미지 왜곡 보정
    use_textline_orientation=False       # 텍스트 라인 방향 분류
)
```

## 성능 최적화 파라미터

### 텍스트 감지 파라미터

```python
# 텍스트 감지 최적화
text_det_limit_side_len=960      # 이미지 크기 제한
text_det_limit_type='max'        # 크기 제한 타입 ('min' 또는 'max')
text_det_thresh=0.3              # 텍스트 감지 임계값
text_det_box_thresh=0.6          # 텍스트 박스 임계값
text_det_unclip_ratio=2.0        # 텍스트 영역 확장 계수
```

### 텍스트 인식 파라미터

```python
# 텍스트 인식 최적화
text_rec_score_thresh=0.0        # 텍스트 인식 임계값 (0=필터링 없음)
```

## 사용 예제

### 기본 OCR 실행

```python
from paddleocr import PaddleOCR

# 1. OCR 엔진 초기화
ocr = PaddleOCR(lang='korean', use_angle_cls=True)

# 2. 이미지에서 텍스트 추출
result = ocr.ocr('image.jpg')

# 3. 결과 처리
for idx in range(len(result)):
    for line in result[idx]:
        bbox = line[0]  # 텍스트 위치
        text = line[1][0]  # 인식된 텍스트
        score = line[1][1]  # 신뢰도
        print(f'텍스트: {text}, 신뢰도: {score:.3f}')
```

### 대용량 이미지 처리

```python
# 슬라이딩 윈도우를 사용한 대용량 이미지 처리
result = ocr.ocr(
    'large_image.jpg',
    slice={
        'horizontal_stride': 300,    # 수평 이동 크기
        'vertical_stride': 300,      # 수직 이동 크기
        'merge_x_thres': 50,        # X축 병합 임계값
        'merge_y_thres': 50         # Y축 병합 임계값
    }
)
```

### PDF 처리

```python
# PDF 파일 OCR
result = ocr.ocr('document.pdf', page_num=2)  # 처음 2페이지만 처리
```

## 일반적인 문제 해결

### 1. "Unknown argument" 오류
최신 버전에서 제거된 파라미터를 사용할 때 발생합니다.
해결: 위의 "제거된 파라미터" 섹션을 확인하고 해당 파라미터를 제거하세요.

### 2. IndexError: string index out of range
OCR 결과 파싱 시 발생하는 오류입니다.

```python
# 안전한 결과 파싱
if results and results[0]:
    for line in results[0]:
        try:
            if isinstance(line[1], (list, tuple)) and len(line[1]) >= 2:
                text = line[1][0]
                confidence = line[1][1]
            elif isinstance(line[1], str):
                text = line[1]
                confidence = 1.0
        except (IndexError, TypeError) as e:
            print(f"파싱 오류: {e}")
            continue
```

### 3. 한국어 텍스트 인식 불가
- PP-OCRv5는 한국어를 지원하지 않습니다.
- PaddleOCR 2.x 버전을 사용하거나 향후 업데이트를 기다려야 합니다.

## 권장 설정

### 한국어 텍스트 인식용 (현재 시점)

```python
# PaddleOCR 2.x 사용 권장
from paddleocr import PaddleOCR

ocr = PaddleOCR(
    lang='korean',
    use_angle_cls=True,
    # 기타 파라미터는 기본값 사용
)
```

### 향후 PP-OCRv5 한국어 지원 시

```python
# 향후 지원 예정
ocr = PaddleOCR(
    lang='korean',
    use_angle_cls=True,
    ocr_version='PP-OCRv5'  # 향후 지원 시
)
```

## 참고 자료

- [PaddleOCR 공식 문서](https://paddlepaddle.github.io/PaddleOCR/main/en/index.html)
- [PaddleOCR GitHub](https://github.com/PaddlePaddle/PaddleOCR)
- [PaddleOCR PyPI](https://pypi.org/project/paddleocr/)

---

*최종 업데이트: 2025년 7월 25일*