# Claude Code 작업 가이드

## 프로젝트 개요
Excel Macro Automation - PyQt5 기반 매크로 자동화 도구

## 중요 작업 규칙

### 1. Git Commit 규칙
**⚠️ 중요: 각 작업 완료 시 반드시 Git Commit을 수행해주세요.**

- 기능 추가/수정 완료 시 즉시 commit
- 버그 수정 완료 시 즉시 commit
- 파일 정리나 리팩토링 후 즉시 commit

#### Commit 메시지 형식:
```
feat: 새로운 기능 추가
fix: 버그 수정
refactor: 코드 리팩토링
docs: 문서 수정
style: 코드 스타일 변경
test: 테스트 코드 추가/수정
chore: 빌드 스크립트, 패키지 매니저 설정 등
```

### 2. 테스트 실행
작업 완료 후 다음 명령어 실행:
- Windows: `RUN_ON_WINDOWS.bat`
- 오류 발생 시: `RUN_WITH_AUTOFIX.bat`

### 3. 인코딩 주의사항
- 모든 파일은 UTF-8로 저장
- 한글 주석/문자열 사용 시 인코딩 확인 필수

### 4. 오류 처리
- 자동 오류 복구 시스템 활용
- 오류 발생 시 `COLLECT_ERRORS.bat` 실행하여 오류 수집

## 주요 디렉토리 구조
```
macro/
├── src/
│   ├── core/          # 핵심 기능
│   ├── ui/            # UI 컴포넌트
│   ├── automation/    # 자동화 엔진
│   └── utils/         # 유틸리티
├── resources/         # 리소스 파일
└── logs/             # 로그 파일
```

## 자주 사용하는 배치 파일
- `RUN_ON_WINDOWS.bat`: 일반 실행
- `RUN_WITH_AUTOFIX.bat`: 자동 오류 수정 포함 실행
- `DIAGNOSE_AND_FIX.bat`: 시스템 진단 및 수정
- `COLLECT_ERRORS.bat`: 오류 수집

## 개발 시 주의사항
1. PyQt5 시그널/슬롯 사용 시 스레드 안전성 확인
2. 파일 경로는 항상 Path 객체 사용
3. 로깅은 app_logger 사용
4. 새로운 의존성 추가 시 requirements.txt 업데이트