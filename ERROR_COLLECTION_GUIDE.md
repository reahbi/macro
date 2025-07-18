# 오류 수집 시스템 가이드

## 개요
오류 수집 시스템은 애플리케이션에서 발생한 모든 오류를 자동으로 수집하고 JSON 파일로 저장합니다.

## 주요 기능

### 1. 오류 수집
- 오류 복구 히스토리
- 매크로 실행 로그
- 애플리케이션 로그

### 2. 저장 위치
```
%USERPROFILE%\.excel_macro_automation\collected_errors\
├── errors_20241219_143022.json   # 타임스탬프별 오류 파일
├── errors_20241219_150512.json
└── latest_errors.json            # 최신 오류 파일 링크
```

## 사용 방법

### Python에서 사용
```python
from utils.error_report_generator import ErrorCollector

# 오류 수집기 생성
collector = ErrorCollector()

# 최근 7일간의 오류 수집 및 저장
errors = collector.collect_errors(days=7)
print(f"수집된 오류: {len(errors)}개")

# 오류 요약 통계 확인
summary = collector.get_error_summary()
print(f"총 오류: {summary['total_errors']}개")
print(f"오류 유형: {summary['error_types']}")

# 최신 오류 10개 확인
recent_errors = collector.get_latest_errors(count=10)
for error in recent_errors:
    print(f"{error['timestamp']}: {error['type']} - {error['message']}")

# 30일 이상 된 오류 파일 정리
collector.clear_old_errors(days=30)
```

### 명령줄에서 사용
```python
# 오류 수집 스크립트 (collect_errors.py)
from utils.error_report_generator import collect_and_save_errors

# 최근 7일간의 오류 수집
count = collect_and_save_errors(days=7)
print(f"{count}개의 오류가 수집되었습니다.")
```

## 오류 파일 형식

### errors_YYYYMMDD_HHMMSS.json
```json
[
    {
        "timestamp": "2024-12-19T14:30:22.123456",
        "type": "UnicodeDecodeError",
        "message": "'cp949' codec can't decode byte 0xec",
        "source": "recovery_system",
        "pattern": "encoding_error",
        "context": {}
    },
    {
        "timestamp": "2024-12-19T14:25:10.654321",
        "type": "ExecutionError",
        "message": "Step execution failed",
        "source": "execution_log",
        "context": {
            "step": "텍스트 입력",
            "row": "2"
        }
    }
]
```

### latest_errors.json
```json
{
    "file": "errors_20241219_143022.json",
    "timestamp": "20241219_143022",
    "count": 15,
    "days_collected": 7
}
```

## 오류 소스별 설명

### 1. recovery_system
- 자동 오류 복구 시스템에서 감지된 오류
- 복구 시도 실패 기록

### 2. execution_log
- 매크로 실행 중 발생한 오류
- 실행 단계와 Excel 행 정보 포함

### 3. app_log
- 일반 애플리케이션 오류
- ERROR 레벨 로그만 수집

## 클로드에 전달하기

수집된 오류를 클로드에 전달할 때:

1. 최신 오류 파일 찾기:
   ```
   %USERPROFILE%\.excel_macro_automation\collected_errors\latest_errors.json
   ```

2. 해당 파일에서 실제 오류 파일명 확인

3. 오류 파일 내용을 복사하여 클로드에 전달

## 자동화 팁

### 배치 파일로 오류 수집
```batch
@echo off
python -c "from utils.error_report_generator import collect_and_save_errors; print(f'{collect_and_save_errors()} errors collected')"
pause
```

### 주기적 오류 정리
```python
# 매주 실행할 스크립트
from utils.error_report_generator import ErrorCollector

collector = ErrorCollector()
collector.clear_old_errors(days=30)  # 30일 이상 된 파일 삭제
```

## 주의사항

1. 오류 파일은 시간이 지나면 누적되므로 주기적인 정리 필요
2. 민감한 정보가 오류 메시지에 포함될 수 있으므로 주의
3. 디스크 공간을 고려하여 적절한 보관 기간 설정