# PaddleOCR 한국어 사용 가이드

## 개요

이 문서는 Excel Macro Automation 프로젝트에서 PaddleOCR을 사용하여 한국어 텍스트를 인식하는 방법을 설명합니다.

## 현재 사용 버전

- **PaddleOCR**: 2.7.0
- **모델**: `korean_PP-OCRv5_mobile_rec`
- **정확도**: 88%
- **지원 언어**: 한국어, 영어, 숫자

## 올바른 사용 방법

### 1. 기본 초기화

```python
from paddleocr import PaddleOCR

# PP-OCRv5 한국어 모델 자동 사용
ocr = PaddleOCR(
    lang='korean',              # 한국어 모델 (korean_PP-OCRv5_mobile_rec)
    use_angle_cls=True         # 텍스트 각도 분류 활성화
)
```

**주의**: `ocr_version='PP-OCRv4'` 파라미터는 PaddleOCR 2.7.0에서 지원하지 않습니다.

### 2. 실제 동작 방식

`lang='korean'`을 지정하면:
1. 자동으로 `korean_PP-OCRv5_mobile_rec` 모델이 다운로드됩니다
2. PP-OCRv5 detection 모델과 함께 사용됩니다
3. 한국어, 영어, 숫자를 모두 인식할 수 있습니다

### 3. 결과 형식

PP-OCRv5는 다음과 같은 딕셔너리 형식으로 결과를 반환합니다:

```python
{
    'rec_texts': ['인식된 텍스트1', '인식된 텍스트2', ...],
    'rec_scores': [0.95, 0.94, ...],  # 신뢰도 점수
    'rec_polys': [[[x1,y1], [x2,y2], [x3,y3], [x4,y4]], ...],  # 텍스트 위치
    'rec_boxes': [[x, y, width, height], ...]  # 바운딩 박스
}
```

## 프로젝트에서의 구현

### text_extractor_paddle.py

```python
# PaddleOCR 초기화
PaddleTextExtractor._ocr = PaddleOCR(
    lang='korean',              # 한국어 모델 사용
    use_angle_cls=True         # 텍스트 각도 분류 활성화
)
```

### 결과 파싱

PP-OCRv5의 딕셔너리 형식 결과를 처리하는 로직이 구현되어 있습니다:

```python
# PP-OCRv5 형식 처리
if 'rec_texts' in line and 'rec_polys' in line:
    texts = line.get('rec_texts', [])
    scores = line.get('rec_scores', [])
    polys = line.get('rec_polys', [])
    
    # 각 텍스트에 대해 TextResult 생성
    for text_idx, text in enumerate(texts):
        # ... 좌표 계산 및 TextResult 생성
```

## 성능 최적화

### 1. GPU 사용 (자동 감지)
PaddleOCR은 GPU가 사용 가능하면 자동으로 GPU를 사용합니다.

### 2. 이미지 전처리
```python
text_extractor.set_preprocessing(True)  # 정확도 향상
text_extractor.set_preprocessing(False) # 속도 향상 (기본값)
```

### 3. 메모리 사용량 관리
대용량 이미지 처리 시 이미지 크기를 제한할 수 있습니다.

## 문제 해결

### 1. "Unknown argument" 오류
- 원인: 구버전 파라미터 사용
- 해결: `use_gpu`, `show_log` 등의 파라미터 제거

### 2. 텍스트 인식 실패
- 원인: 결과 파싱 로직 오류
- 해결: PP-OCRv5 형식에 맞는 파싱 로직 사용

### 3. 한국어 인식 안 됨
- 원인: 잘못된 언어 설정
- 해결: `lang='korean'` 명시적 지정

## 지원되는 한국어 예시

- 이름: 홍길동, 김철수, 이영희, 박민수, 최지우
- 날짜: 2025년 7월 25일
- 숫자: 주문번호 12345, 금액 50,000원
- 상태: 처리완료, 대기중, 진행중

## 참고 사항

1. PP-OCRv5는 PP-OCRv4보다 더 높은 정확도를 제공합니다
2. 한국어 모델은 영어와 숫자도 함께 인식합니다
3. 첫 실행 시 모델 다운로드로 시간이 걸릴 수 있습니다
4. 모델은 `~/.paddlex/official_models/`에 저장됩니다

---

*최종 업데이트: 2025년 7월 25일*