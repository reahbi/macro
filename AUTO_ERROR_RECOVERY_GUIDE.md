# 자동 오류 복구 시스템 가이드

## 📋 목차
1. [개요](#개요)
2. [시스템 구성](#시스템-구성)
3. [사용 방법](#사용-방법)
4. [동작 원리](#동작-원리)
5. [모니터링 시스템](#모니터링-시스템)
6. [문제 해결](#문제-해결)
7. [고급 설정](#고급-설정)

## 개요

Excel Macro Automation의 자동 오류 복구 시스템은 Windows 환경에서 발생하는 다양한 오류를 자동으로 감지하고 복구하여 작업 중단을 최소화합니다.

### 주요 기능
- 🔧 **자동 오류 복구**: 일반적인 오류를 자동으로 해결
- 🏥 **자가 진단**: 시스템 상태를 사전에 점검하고 문제 예방
- 📊 **실시간 모니터링**: 시스템 리소스와 애플리케이션 상태 감시
- 📝 **상세한 로깅**: 모든 오류와 복구 시도 기록

## 시스템 구성

### 1. 오류 복구 매니저 (`error_recovery.py`)
자동으로 오류를 감지하고 복구하는 핵심 컴포넌트입니다.

**지원하는 오류 유형:**
- 인코딩 오류 (UTF-8, CP949)
- 모듈 임포트 오류
- 파일 경로 오류
- 권한 오류
- Qt 관련 오류
- 메모리/리소스 부족

### 2. 자가 진단 도구 (`self_diagnosis.py`)
시스템 환경을 점검하고 문제를 사전에 해결합니다.

**진단 항목:**
- Python 버전 및 환경
- 필수/선택 패키지 설치 상태
- 파일 시스템 무결성
- 인코딩 설정
- Qt 환경 설정
- 시스템 리소스

### 3. 백그라운드 모니터 (`background_monitor.py`)
실시간으로 시스템 상태를 감시하고 문제를 예방합니다.

**모니터링 항목:**
- CPU 사용률
- 메모리 사용률
- 디스크 공간
- 스레드 수
- 로그 파일 크기
- 임시 파일

### 4. 오류 데코레이터 (`error_decorator.py`)
기존 코드에 쉽게 오류 복구 기능을 추가할 수 있는 도구입니다.

## 사용 방법

### 기본 실행 (자동 복구 포함)
```batch
RUN_WITH_AUTOFIX.bat
```
- 시작 시 자동으로 시스템 진단 실행
- 오류 발생 시 자동 복구 시도
- 복구 통계 표시

### 시스템 진단만 실행
```batch
DIAGNOSE_AND_FIX.bat
```
- 전체 시스템 점검
- 발견된 문제 자동 수정
- 상세한 진단 리포트 생성

### Python에서 직접 사용
```python
# 진단 실행
from utils.self_diagnosis import run_diagnosis
run_diagnosis()

# 모니터링 시작
from utils.background_monitor import get_monitor
monitor = get_monitor()
monitor.start()
```

## 동작 원리

### 1. 오류 감지 및 복구 프로세스

```
오류 발생
    ↓
오류 패턴 분석
    ↓
복구 전략 선택
    ↓
자동 복구 시도
    ↓
성공 → 작업 계속
실패 → 사용자 알림
```

### 2. 오류 패턴 매칭

시스템은 오류 메시지와 스택 트레이스를 분석하여 알려진 패턴과 매칭합니다:

```python
# 예: 인코딩 오류 패턴
patterns = [
    "UnicodeDecodeError",
    "UnicodeEncodeError", 
    "codec can't decode"
]
```

### 3. 복구 전략

각 오류 유형에 맞는 복구 전략이 적용됩니다:

#### 인코딩 오류
1. 파일 인코딩 자동 감지
2. UTF-8로 변환
3. 시스템 로케일 설정

#### 임포트 오류
1. 모듈명 추출
2. pip로 자동 설치
3. 재시도

#### 경로 오류
1. 경로 정규화
2. 디렉토리 자동 생성
3. Windows 경로 형식 변환

### 4. 데코레이터 사용

기존 함수에 쉽게 적용할 수 있습니다:

```python
from utils.error_decorator import auto_recover

@auto_recover(retry_count=2)
def load_file(path):
    # 파일 로드 로직
    pass
```

## 모니터링 시스템

### 실시간 모니터링

백그라운드 모니터는 5초마다 시스템을 체크합니다:

```
CPU 사용률 → 80% 이상 시 가비지 컬렉션
메모리 사용률 → 85% 이상 시 메모리 정리
디스크 공간 → 90% 이상 시 임시 파일 정리
스레드 수 → 100개 이상 시 누수 경고
```

### 모니터링 규칙 추가

커스텀 규칙을 추가할 수 있습니다:

```python
monitor.add_rule(
    name="custom_check",
    check_func=lambda: get_some_metric(),
    threshold=100,
    action_func=handle_violation,
    check_interval=30  # 초
)
```

### 알림 시스템

문제 감지 시:
1. 로그에 기록
2. UI에 알림 표시
3. 3회 연속 위반 시 자동 액션 실행

## 문제 해결

### 자주 발생하는 문제

#### 1. "관리자 권한이 필요합니다"
- 해결: 배치 파일을 관리자 권한으로 실행

#### 2. "모듈을 찾을 수 없습니다"
- 해결: `DIAGNOSE_AND_FIX.bat` 실행으로 자동 설치

#### 3. "인코딩 오류가 계속 발생합니다"
- 해결: 환경 변수 설정
  ```batch
  set PYTHONUTF8=1
  ```

### 로그 확인

복구 시도 기록:
```
%USERPROFILE%\.excel_macro_automation\error_recovery_history.json
```

진단 결과:
```
%USERPROFILE%\.excel_macro_automation\diagnosis_results.json
```

모니터링 리포트:
```
%USERPROFILE%\.excel_macro_automation\monitor_report.json
```

## 고급 설정

### 환경 변수

시스템 동작을 제어하는 환경 변수:

```batch
REM UTF-8 강제 사용
set PYTHONUTF8=1

REM Qt 플랫폼 설정
set QT_QPA_PLATFORM=windows

REM 디버그 모드
set MACRO_DEBUG=1
```

### 복구 정책 커스터마이징

`error_recovery.py`에서 새로운 패턴 추가:

```python
recovery_manager.register_pattern(
    name="custom_error",
    patterns=["MyCustomError"],
    recovery_func=my_recovery_function,
    priority=10
)
```

### 모니터링 임계값 조정

리소스 사용률 임계값 변경:

```python
# CPU 임계값을 90%로 변경
monitor.rules[0].threshold = 90.0
```

### 자동 시작 설정

Windows 시작 시 모니터링 자동 시작:
1. `WIN+R` → `shell:startup`
2. `START_MONITOR.bat` 파일 생성:
   ```batch
   @echo off
   cd /d "C:\path\to\macro"
   start /min python -c "from utils.background_monitor import get_monitor; get_monitor().start()"
   ```

## 성능 최적화

### 메모리 사용 줄이기
- 모니터링 주기 늘리기: `monitor_timer.start(10000)` # 10초
- 히스토리 크기 줄이기: `SystemMetrics(history_size=50)`

### 로그 관리
- 자동 정리 주기: 7일 → 3일로 변경
- 로그 레벨 조정: WARNING 이상만 기록

## 마무리

이 시스템은 지속적으로 학습하고 개선됩니다:
- 오류 패턴이 누적될수록 복구 성공률 향상
- 사용자 환경에 맞게 자동 최적화
- 새로운 오류 유형도 점진적으로 대응

문제가 지속되면 GitHub 이슈로 보고해주세요!