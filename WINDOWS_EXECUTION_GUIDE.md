# Windows 실행 환경 가이드

## 개요
이 애플리케이션은 WSL에서 개발되었지만 Windows 환경에서 실행됩니다.

## 실행 구조

### 1. 파일 복사 과정
```
WSL 경로: \\wsl.localhost\Ubuntu-22.04\home\nosky\macro
     ↓ (복사)
Windows: C:\macro
```

### 2. 주요 배치 파일

#### RUN_ON_WINDOWS.bat
- 기본 실행 파일
- WSL에서 C:\macro로 파일 복사
- Python 환경 확인 및 패키지 설치
- 애플리케이션 실행

#### RUN_WITH_AUTOFIX_WINDOWS.bat
- 자동 오류 복구 모드 실행
- 시스템 자가 진단 포함
- 오류 발생 시 자동 수정 시도
- 환경 변수 자동 설정 (UTF-8, Qt)

#### DIAGNOSE_AND_FIX_WINDOWS.bat
- 시스템 진단 전용
- Python 환경 검사
- 필수 패키지 확인 및 설치
- 로그 디렉토리 생성

#### COLLECT_ERRORS_WINDOWS.bat
- 오류 수집 및 저장
- 최근 7일간의 오류 수집
- JSON 형식으로 저장
- 오류 요약 표시

## 디렉토리 구조

### Windows 실행 시
```
C:\macro\
├── src/                    # 소스 코드
├── resources/              # 리소스 파일
├── run_main_fixed.py      # 메인 실행 파일
└── run_with_recovery.py   # 자동 복구 실행 파일

%USERPROFILE%\.excel_macro_automation\
├── logs/                   # 실행 로그
├── collected_errors/       # 수집된 오류
├── error_recovery_history.json
└── diagnosis_results.json
```

## 환경 변수 설정

배치 파일에서 자동 설정:
```batch
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
set QT_QPA_PLATFORM=windows
set BATCH_MODE=1
```

## 문제 해결

### 1. "UNC 경로는 지원되지 않습니다" 오류
- WSL 경로에서 직접 실행 시 발생
- 해결: 배치 파일이 자동으로 C:\macro로 복사 후 실행

### 2. 인코딩 오류
- 환경 변수가 자동 설정됨
- 모든 파일은 UTF-8로 처리

### 3. 모듈을 찾을 수 없음
- DIAGNOSE_AND_FIX_WINDOWS.bat 실행
- 필수 패키지 자동 설치

### 4. Qt 플랫폼 오류
- QT_QPA_PLATFORM=windows 자동 설정
- PyQt5 재설치로 해결

## 실행 순서 권장

1. 첫 실행:
   ```
   DIAGNOSE_AND_FIX_WINDOWS.bat
   ```

2. 일반 실행:
   ```
   RUN_ON_WINDOWS.bat
   ```

3. 오류 발생 시:
   ```
   RUN_WITH_AUTOFIX_WINDOWS.bat
   ```

4. 오류 수집:
   ```
   COLLECT_ERRORS_WINDOWS.bat
   ```

## 주의사항

1. **관리자 권한**: 일부 기능은 관리자 권한 필요
2. **백신 프로그램**: pyautogui 등이 차단될 수 있음
3. **Python 경로**: PATH에 Python이 포함되어야 함
4. **파일 경로**: 공백이 있는 경로 주의

## 개발 시 참고

1. 모든 경로는 Windows 스타일 사용
2. UTF-8 인코딩 필수
3. 배치 파일에서 실행 시 BATCH_MODE 환경 변수 활용
4. 오류는 자동으로 수집되어 분석 가능