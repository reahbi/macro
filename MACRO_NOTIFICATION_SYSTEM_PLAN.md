# 매크로 실행 알림 시스템 구현 계획

## 1. 개요

### 1.1 목적
- 매크로 실행 시 메인 창이 작업 화면을 가리는 문제 해결
- 실행 상태를 실시간으로 확인할 수 있는 비침투적 알림 시스템 구축
- 사용자 편의성을 위한 글로벌 단축키 지원

### 1.2 핵심 요구사항
- 동작 준비 모드 지원
- 최소화된 플로팅 위젯으로 상태 표시
- Excel 기반/Standalone 모드별 진행률 계산
- 시스템 트레이 통합

## 2. 시스템 구성

### 2.1 주요 컴포넌트

```
┌─────────────────────────────────────────────────────┐
│                   MainWindow                         │
│  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │ ExecutionWidget │  │   FloatingStatusWidget   │  │
│  │ [동작 준비] 버튼│  │   (독립 플로팅 윈도우)    │  │
│  └─────────────────┘  └─────────────────────────┘  │
│                                                      │
│  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │ HotkeyListener  │  │   SystemTrayManager     │  │
│  │ F5: 시작        │  │   (시스템 트레이 아이콘)  │  │
│  └─────────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────┘
```

### 2.2 컴포넌트별 책임

1. **ExecutionWidget (확장)**
   - 동작 준비 버튼 추가
   - 준비 모드 진입/종료 관리
   - FloatingStatusWidget 생성 및 제어

2. **FloatingStatusWidget (신규)**
   - 플로팅 상태 표시
   - 드래그 가능한 미니 윈도우
   - 진행률 및 상태 정보 표시

3. **SystemTrayManager (신규)**
   - 시스템 트레이 아이콘 관리
   - 컨텍스트 메뉴 제공
   - 상태별 아이콘 변경

4. **HotkeyListener (확장)**
   - F5 시작 단축키 추가
   - 준비 모드 취소 (ESC) 지원

## 3. 진행률 표시 시스템

### 3.1 진행률 계산 방식

#### 3.1.1 Excel 기반 실행
```python
# 주 진행률: Excel 행 기준
main_progress = (completed_rows / total_rows) * 100

# 부 진행률: 현재 행의 단계 진행
sub_progress = (current_step_index / total_steps_in_macro) * 100

# 전체 진행률 (복합 계산)
overall_progress = (completed_rows / total_rows) + 
                   (1 / total_rows) * (current_step_index / total_steps_in_macro)
```

#### 3.1.2 Standalone 실행
```python
# 단일 진행률: 전체 단계 기준
progress = (completed_steps / total_steps) * 100
```

### 3.2 진행률 표시 형식

#### 3.2.1 최소 모드 (Minimal)
```
┌────────────────────┐
│ ▶ 3/10 (30%)      │
│ ████░░░░░░         │
└────────────────────┘
```

#### 3.2.2 일반 모드 (Normal)
```
┌─────────────────────────┐
│ ▶ 행 3/10 - P001       │
│ ████████░░░░░░░░░░░    │
│ 단계 5/8: 저장 중      │
└─────────────────────────┘
```

#### 3.2.3 상세 모드 (Detailed)
```
┌─────────────────────────────┐
│ ▶ Excel 실행 중             │
│ 행: 3/10 (30%) - P001       │
│ ████████░░░░░░░░░░░        │
│ 현재: 검진결과 저장         │
│ 단계: 5/8 | 시간: 00:45    │
│ 성공: 2 | 실패: 0          │
└─────────────────────────────┘
```

### 3.3 특수 케이스 처리

#### 3.3.1 Loop 단계
- Loop 내부 단계는 하위 진행률로 표시
- Loop 반복 횟수를 전체 진행률에 반영

#### 3.3.2 조건부 단계 (If/Else)
- 실행되지 않은 분기는 진행률 계산에서 제외
- 동적으로 총 단계 수 조정

#### 3.3.3 재시도 로직
- 재시도는 동일 단계로 간주
- 재시도 상태는 별도 표시: "(재시도 2/3)"

## 4. UI/UX 디자인

### 4.1 동작 준비 모드

#### 4.1.1 준비 화면
```
┌─────────────────────────┐
│ 🔄 매크로 준비 중...    │
│                         │
│        5                │
│                         │
│ F5: 즉시 시작          │
│ ESC: 취소              │
└─────────────────────────┘
```

#### 4.1.2 카운트다운 애니메이션
- 숫자가 크게 표시되며 페이드 아웃
- 원형 프로그레스 바 옵션
- 소리 알림 (옵션)

### 4.2 플로팅 위젯 디자인

#### 4.2.1 시각적 요소
- 반투명 배경 (opacity: 0.8)
- 둥근 모서리 (border-radius: 8px)
- 그림자 효과
- 상태별 색상 테마
  - 정상: 초록색 계열
  - 일시정지: 주황색 계열
  - 오류: 빨간색 계열

#### 4.2.2 인터랙션
- 마우스 오버: 확장 모드로 전환
- 드래그: 위치 이동 (위치 저장)
- c더블클릭: 메인 창 복원
- 우클릭: 컨텍스트 메뉴

### 4.3 시스템 트레이

#### 4.3.1 아이콘 상태
- 🟢 대기 중 (Idle)
- 🟡 준비 중 (Ready)
- 🔵 실행 중 (Running) - 애니메이션
- ⏸️ 일시정지 (Paused)
- 🔴 오류 (Error)

#### 4.3.2 컨텍스트 메뉴
```
┌─────────────────────┐
│ ▶ 시작/재개        │
│ ⏸ 일시정지         │
│ ⏹ 정지             │
│ ─────────────────── │
│ 📊 로그 보기        │
│ ⚙️ 설정             │
│ ─────────────────── │
│ 🔼 창 보이기        │
│ ❌ 종료             │
└─────────────────────┘
```

## 5. 구현 계획

### 5.1 Phase 1: 핵심 기능 (1주)

1. **ExecutionWidget 확장**
   - `prepare_execution()` 메서드 추가
   - 동작 준비 버튼 UI 추가
   - 카운트다운 타이머 구현

2. **FloatingStatusWidget 기본 구현**
   - QWidget 기반 플로팅 윈도우
   - 기본 진행률 표시
   - 최소/일반 모드 전환

3. **HotkeyListener 확장**
   - F5 시작 키 추가
   - 준비 모드 지원

### 5.2 Phase 2: 진행률 시스템 (1주)

1. **ProgressCalculator 클래스**
   - Excel/Standalone 모드 구분
   - 복합 진행률 계산
   - 특수 케이스 처리

2. **FloatingStatusWidget 고도화**
   - 상세 모드 추가
   - 드래그 & 드롭
   - 위치 저장/복원

3. **실행 엔진 통합**
   - 진행률 신호 추가
   - 단계별 상태 전달

### 5.3 Phase 3: 시스템 통합 (1주)

1. **SystemTrayManager 구현**
   - QSystemTrayIcon 활용
   - 상태별 아이콘 관리
   - 컨텍스트 메뉴

2. **설정 시스템 확장**
   - 알림 관련 설정 추가
   - 위젯 투명도/크기
   - 표시 모드 선택

3. **테스트 및 최적화**
   - 다중 모니터 테스트
   - 성능 최적화
   - 사용자 피드백 반영

## 6. 기술 구현 상세

### 6.1 FloatingStatusWidget 구현

```python
class FloatingStatusWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowOpacity(0.8)
        
        # 드래그 지원
        self.old_pos = None
        
        # 모드 관리
        self.display_mode = DisplayMode.MINIMAL
        self.is_expanded = False
        
        self.init_ui()
        self.load_position()
    
    def init_ui(self):
        # 레이아웃 구성
        self.layout = QVBoxLayout()
        
        # 진행률 바
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(False)
        
        # 상태 레이블
        self.status_label = QLabel("대기 중")
        
        # 상세 정보 (확장 모드)
        self.detail_widget = QWidget()
        self.detail_widget.hide()
        
    def update_progress(self, progress_data):
        """진행률 업데이트"""
        if progress_data.mode == ExecutionMode.EXCEL:
            text = f"행 {progress_data.current_row}/{progress_data.total_rows}"
            if progress_data.row_identifier:
                text += f" - {progress_data.row_identifier}"
        else:
            text = f"단계 {progress_data.current_step}/{progress_data.total_steps}"
        
        self.status_label.setText(text)
        self.progress_bar.setValue(int(progress_data.percentage))
```

### 6.2 진행률 계산 시스템

```python
class ProgressCalculator:
    def __init__(self, execution_mode: ExecutionMode):
        self.mode = execution_mode
        self.total_rows = 0
        self.total_steps = 0
        self.completed_rows = 0
        self.current_step_index = 0
        
    def calculate_progress(self) -> ProgressData:
        if self.mode == ExecutionMode.EXCEL:
            # Excel 모드: 복합 진행률
            row_progress = self.completed_rows / self.total_rows
            step_progress = self.current_step_index / self.total_steps
            
            # 전체 진행률 = 완료된 행 + 현재 행의 진행도
            overall = (self.completed_rows + step_progress) / self.total_rows
            
            return ProgressData(
                mode=self.mode,
                percentage=overall * 100,
                current_row=self.completed_rows + 1,
                total_rows=self.total_rows,
                current_step=self.current_step_index + 1,
                total_steps=self.total_steps
            )
        else:
            # Standalone 모드: 단순 진행률
            progress = self.current_step_index / self.total_steps
            
            return ProgressData(
                mode=self.mode,
                percentage=progress * 100,
                current_step=self.current_step_index + 1,
                total_steps=self.total_steps
            )
```

### 6.3 시스템 트레이 통합

```python
class SystemTrayManager(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.tray_icon = QSystemTrayIcon(self)
        
        # 아이콘 설정
        self.icons = {
            ExecutionState.IDLE: QIcon("icons/idle.png"),
            ExecutionState.READY: QIcon("icons/ready.png"),
            ExecutionState.RUNNING: QIcon("icons/running.png"),
            ExecutionState.PAUSED: QIcon("icons/paused.png"),
            ExecutionState.ERROR: QIcon("icons/error.png")
        }
        
        self.create_menu()
        self.tray_icon.show()
    
    def create_menu(self):
        menu = QMenu()
        
        # 실행 제어
        self.start_action = menu.addAction("시작/재개")
        self.pause_action = menu.addAction("일시정지")
        self.stop_action = menu.addAction("정지")
        
        menu.addSeparator()
        
        # 기타 기능
        menu.addAction("로그 보기")
        menu.addAction("설정")
        
        menu.addSeparator()
        
        menu.addAction("창 보이기")
        menu.addAction("종료")
        
        self.tray_icon.setContextMenu(menu)
```

## 7. 설정 및 사용자 옵션

### 7.1 설정 항목

```json
{
  "notification": {
    "floating_widget": {
      "enabled": true,
      "opacity": 0.8,
      "display_mode": "normal",
      "position": {"x": -1, "y": -1},
      "auto_hide": false,
      "always_on_top": true
    },
    "system_tray": {
      "enabled": true,
      "show_notifications": true,
      "minimize_to_tray": true
    },
    "preparation": {
      "countdown_seconds": 5,
      "show_countdown": true,
      "play_sound": false
    },
    "hotkeys": {
      "start": "F5",
      "pause": "F9",
      "stop": "Escape"
    }
  }
}
```

### 7.2 사용자 시나리오

1. **기본 워크플로우**
   - 매크로 설정 → 동작 준비 → 카운트다운 → 실행 → 완료

2. **빠른 실행**
   - 매크로 설정 → F5 → 즉시 실행

3. **백그라운드 모니터링**
   - 실행 중 → 메인 창 최소화 → 플로팅 위젯으로 확인

## 8. 테스트 계획

### 8.1 단위 테스트
- ProgressCalculator 정확도
- FloatingStatusWidget 렌더링
- 단축키 인식

### 8.2 통합 테스트
- Excel/Standalone 모드 전환
- 다중 모니터 환경
- 시스템 트레이 동작

### 8.3 사용성 테스트
- 5명의 테스트 사용자
- 실제 업무 시나리오
- 피드백 수집 및 반영

## 9. 향후 확장 계획

1. **모바일 연동**
   - 스마트폰 알림 지원
   - 원격 제어 기능

2. **AI 기반 진행률 예측**
   - 과거 실행 데이터 학습
   - 남은 시간 예측

3. **다중 매크로 관리**
   - 동시 실행 지원
   - 대시보드 뷰

## 10. 예상 일정

- **Week 1**: Phase 1 구현 (핵심 기능)
- **Week 2**: Phase 2 구현 (진행률 시스템)
- **Week 3**: Phase 3 구현 (시스템 통합)
- **Week 4**: 테스트 및 안정화

총 예상 기간: 4주