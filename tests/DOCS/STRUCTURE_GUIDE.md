# Excel Macro Automation - 앱 구조 가이드

## 📁 프로젝트 구조

```
excel_macro/
├── src/                        # 소스 코드 루트
│   ├── automation/            # 자동화 엔진
│   ├── config/               # 설정 관리
│   ├── core/                 # 핵심 비즈니스 로직
│   ├── excel/                # Excel 데이터 처리
│   ├── logger/               # 로깅 시스템
│   ├── ui/                   # 사용자 인터페이스
│   ├── utils/                # 유틸리티 함수
│   └── vision/               # 이미지/텍스트 인식
├── resources/                 # 리소스 파일
│   ├── locales/              # 다국어 지원 (ko/en)
│   └── icons/                # 아이콘 파일
├── logs/                     # 실행 로그
├── screenshots/              # 스크린샷 저장
└── tests/                    # 테스트 파일

```

## 🏗️ 아키텍처 개요

### MVC 패턴 구조
```
┌─────────────────────────────────────────────────┐
│                  MainWindow                      │
│               (ui/main_window.py)               │
├─────────────┬─────────────┬────────────────────┤
│  Excel Tab  │ Editor Tab  │   Run Tab          │
│  (Model)    │   (View)    │ (Controller)       │
└─────────────┴─────────────┴────────────────────┘
```

### 데이터 흐름
```
Excel File → ExcelManager → Variables → StepExecutor → Actions
     ↓                                       ↑
  Columns                                 Macro Steps
     ↓                                       ↑
Variables Dict ← ← ← ← MacroEditor → → → Macro Object
```

## 📦 주요 모듈 설명

### 1. **automation/** - 자동화 엔진
- **engine.py**: 매크로 실행 엔진 (상태 머신 패턴)
  - `ExecutionEngine`: 매크로 실행 생명주기 관리
  - Excel 행 반복 처리
  - 단계별 실행 제어
  
- **executor.py**: 개별 단계 실행기
  - `StepExecutor`: 각 단계 타입별 핸들러
  - 변수 치환 처리
  - 실행 오류 처리

- **progress_calculator.py**: 진행률 계산
  - 중첩 루프 고려
  - Excel 행 수 기반 계산

### 2. **core/** - 핵심 타입과 로직
- **macro_types.py**: 기본 타입 정의
  - `MacroStep`: 모든 단계의 기본 클래스
  - `StepType`: 단계 타입 열거형
  - `Macro`: 매크로 컨테이너 클래스
  - `StepFactory`: 단계 생성 팩토리

- **excel_workflow_steps.py**: Excel 워크플로우
  - `ExcelRowStartStep`: Excel 반복 시작
  - `ExcelRowEndStep`: Excel 반복 종료
  - 쌍(pair_id)으로 연결

- **macro_storage.py**: 매크로 저장/불러오기
  - AES-256 암호화
  - JSON 직렬화/역직렬화

### 3. **excel/** - Excel 데이터 처리
- **excel_manager.py**: Excel 파일 관리
  - pandas/openpyxl 기반
  - 시트/열 매핑
  - 행 데이터 추출
  - 상태 추적 (완료/미완료)

- **models.py**: Excel 데이터 모델
  - `ExcelData`: 로드된 데이터
  - `ColumnMapping`: 열 매핑 정보

### 4. **ui/** - 사용자 인터페이스

#### 4.1 **ui/widgets/** - 위젯 컴포넌트
- **excel_widget_redesigned.py**: Excel 탭 UI
  - 파일 로드/저장
  - 시트 선택
  - 열 매핑 설정
  - 상태 토글 (개별/배치)

- **macro_editor.py**: 편집기 탭 UI
  - 드래그 앤 드롭 인터페이스
  - 단계 팔레트
  - 매크로 플로우 위젯
  - 변수 팔레트

- **execution_widget.py**: 실행 탭 UI
  - 실행/중지 제어
  - 진행률 표시
  - 실시간 로그
  - 실행 통계

#### 4.2 **ui/dialogs/** - 대화상자
각 단계 타입별 설정 대화상자:
- `MouseClickStepDialog`: 마우스 클릭 설정
- `KeyboardTypeStepDialog`: 키보드 입력 설정
- `TextSearchStepDialog`: 텍스트 검색 설정
- `ImageStepDialog`: 이미지 검색 설정
- 기타 각 단계별 대화상자

### 5. **vision/** - 이미지/텍스트 인식
- **image_matcher.py**: 이미지 매칭
  - OpenCV 기반 템플릿 매칭
  - PyAutoGUI 폴백

- **text_extractor_optimized.py**: OCR 처리
  - EasyOCR 기반
  - 이미지 전처리 최적화
  - 한국어/영어 지원

### 6. **utils/** - 유틸리티
- **encryption.py**: 암호화 처리
- **monitor_utils.py**: 모니터 정보
- **ocr_manager.py**: OCR 설치/관리
- **error_recovery.py**: 오류 복구
- **path_utils.py**: 경로 처리

### 7. **config/** - 설정 관리
- **settings.py**: 전역 설정
  - 암호화된 설정 파일
  - 사용자 설정
  - 기본값 관리

### 8. **logger/** - 로깅 시스템
- **app_logger.py**: 애플리케이션 로깅
- **execution_logger.py**: 실행 로그 (CSV)

## 🔄 실행 흐름

### 1. 매크로 생성 흐름
```
1. Excel 파일 로드 (Excel Tab)
   ↓
2. 열 매핑 설정
   ↓
3. 매크로 편집기로 이동 (Editor Tab)
   ↓
4. 단계 추가 (드래그 앤 드롭)
   ↓
5. 단계 설정 (대화상자)
   ↓
6. 매크로 저장 (.emf 파일)
```

### 2. 매크로 실행 흐름
```
1. 매크로 로드
   ↓
2. Excel 데이터 준비
   ↓
3. ExecutionEngine 시작
   ↓
4. Excel 행 반복
   ├─→ 행 데이터를 변수로 변환
   ├─→ StepExecutor로 각 단계 실행
   └─→ 상태 업데이트
   ↓
5. 실행 완료 리포트
```

## 🎯 주요 디자인 패턴

### 1. **팩토리 패턴**
- `StepFactory`: 단계 타입별 인스턴스 생성
- 새 단계 타입 추가 시 확장 용이

### 2. **싱글톤 패턴**
- `OptimizedTextExtractor`: OCR 리더 재사용
- `Settings`: 전역 설정 관리

### 3. **옵저버 패턴**
- PyQt5 시그널/슬롯
- 실행 진행률 업데이트
- UI 상태 동기화

### 4. **상태 머신 패턴**
- `ExecutionEngine`: 실행 상태 관리
- IDLE → PREPARING → RUNNING → COMPLETED/STOPPED

## 🔌 확장 포인트

### 새로운 단계 타입 추가
1. `StepType` 열거형에 추가
2. 단계 클래스 생성 (MacroStep 상속)
3. `StepFactory`에 생성 로직 추가
4. 대화상자 클래스 생성
5. `StepExecutor`에 핸들러 추가

### 새로운 OCR 엔진 추가
1. `vision/` 디렉토리에 추출기 클래스 생성
2. `TextExtractor` 인터페이스 구현
3. `executor.py`에서 초기화 로직 수정

## 📋 주요 파일 관계도

```
main.py / run_main.py
    ↓
MainWindow
    ├── ExcelWidgetRedesigned (Excel 탭)
    │   └── ExcelManager
    ├── MacroEditor (편집기 탭)
    │   ├── StepPalette
    │   ├── MacroFlowWidget
    │   └── VariablePalette
    └── ExecutionWidget (실행 탭)
        └── ExecutionEngine
            └── StepExecutor
                ├── ImageMatcher
                └── TextExtractor
```

## 🛠️ 개발 가이드라인

### 1. 코딩 스타일
- PEP 8 준수
- 줄 길이: 100자
- 타입 힌트 사용 권장

### 2. 임포트 규칙
- 절대 경로 임포트 사용
- 예: `from automation.engine import ExecutionEngine`

### 3. 시그널/슬롯 패턴
```python
# 시그널 정의
stepAdded = pyqtSignal(MacroStep, int)

# 연결
self.widget.stepAdded.connect(self.handler)

# 발생
self.stepAdded.emit(step, index)
```

### 4. 오류 처리
- 모든 예외는 로깅
- 사용자 대면 오류는 QMessageBox
- 실행 오류는 CSV 로그 기록

## 🔐 보안 고려사항

1. **매크로 파일 암호화**
   - AES-256 암호화
   - 사용자별 고유 키

2. **민감 정보 보호**
   - 로그에서 마스킹 옵션
   - 설정 파일 암호화

3. **로컬 전용 실행**
   - 네트워크 기능 없음
   - 파일 시스템 접근만

## 🚀 성능 최적화

1. **대용량 Excel 처리**
   - pandas 청크 처리
   - 메모리 효율적 로딩

2. **이미지 매칭**
   - OpenCV 우선 사용
   - 멀티스케일 매칭

3. **UI 반응성**
   - 실행은 별도 스레드
   - 비동기 UI 업데이트