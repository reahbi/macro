# 🚀 자동 오류 복구 시스템 - 빠른 참조

## 🎯 즉시 실행 명령어

### 오류 발생 시
```batch
RUN_WITH_AUTOFIX.bat
```

### 시스템 점검
```batch
DIAGNOSE_AND_FIX.bat
```

### 일반 실행
```batch
RUN_ON_WINDOWS.bat
```

## 🔧 자동으로 해결되는 문제들

| 오류 유형 | 자동 해결 방법 |
|---------|-------------|
| 인코딩 오류 | UTF-8로 자동 변환 |
| 모듈 없음 | pip로 자동 설치 |
| 경로 오류 | 디렉토리 자동 생성 |
| Qt 플랫폼 | Windows 설정 자동 적용 |
| 메모리 부족 | 가비지 컬렉션 실행 |
| 디스크 부족 | 임시 파일 자동 정리 |

## 📊 시스템 상태 확인

### 건강 상태 표시
- 🟢 **정상**: 모든 시스템 정상
- 🟡 **주의**: 일부 지표 임계값 근접
- 🔴 **위험**: 즉시 조치 필요

### 모니터링 지표
- CPU < 80%
- 메모리 < 85%
- 디스크 < 90%
- 스레드 < 100개

## 🛠️ 문제별 해결법

### "파일을 찾을 수 없습니다"
→ 자동으로 경로 생성됨

### "권한이 거부되었습니다"
→ 관리자 권한으로 재실행

### "모듈이 설치되지 않았습니다"
→ 자동으로 pip 설치 시도

### "인코딩 오류"
→ 파일 인코딩 자동 감지 및 변환

## 💡 유용한 팁

### 1. 예방이 최선
- 주기적으로 `DIAGNOSE_AND_FIX.bat` 실행
- 디스크 공간 10GB 이상 유지

### 2. 로그 확인
```
%USERPROFILE%\.excel_macro_automation\
├── logs\              # 실행 로그
├── error_recovery_history.json  # 복구 기록
└── monitor_report.json         # 모니터링 리포트
```

### 3. 성능 최적화
- 불필요한 프로그램 종료
- 임시 파일 정기 정리
- 가상환경 사용 권장

## 🆘 긴급 상황 대처

### 프로그램이 시작되지 않을 때
1. `DIAGNOSE_AND_FIX.bat` 실행
2. Python 재설치 고려
3. 가상환경 재생성

### 반복적인 오류
1. 오류 패턴 확인
2. `error_recovery_history.json` 검토
3. GitHub 이슈 등록

## 📞 추가 도움말

- 문서: `AUTO_ERROR_RECOVERY_GUIDE.md`
- 로그 위치: `%USERPROFILE%\.excel_macro_automation\`
- 지원: GitHub Issues

---
💪 **Remember**: 대부분의 오류는 자동으로 해결됩니다!