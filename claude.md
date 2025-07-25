# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Excel Macro Automation is a Python desktop application for Windows that automates repetitive tasks by reading Excel files and executing screen automation sequences. Built with PyQt5, it provides a visual drag-and-drop macro editor for non-technical users.

## Quick Start Commands

### Running the Application
```bash
# Primary method - simple and fast (recommended)
RUN_SIMPLE.bat

# Python direct execution - handles import fixing automatically
python run_main.py

# Alternative launchers
RUN_PY311.bat  # Python 3.11 (Direct)
RUN_AUTO_VENV.bat  # Auto-detect venv (Recommended)
```

### Development Commands
```bash
# Install dependencies
INSTALL_DEPENDENCIES.bat

# Code formatting (line length: 100)
black src/ --line-length 100

# Linting
flake8 src/ --max-line-length=100

# Build executable
pyinstaller excel_macro.spec

# Run specific tests
run_single_test.bat test_name
RUN_WORKFLOW_TESTS.bat  # Workflow-specific tests
RUN_NOTIFICATION_TESTS.bat  # Notification tests
```

## High-Level Architecture

### Application Structure
The application follows an MVC pattern with three main tabs:
1. **Excel Tab** (`excel_widget_redesigned.py`) - Excel file loading and column mapping
2. **Editor Tab** (`macro_editor.py`) - Drag-and-drop macro creation with step palette
3. **Run Tab** (`execution_widget.py`) - Macro execution with progress monitoring

### Core Execution Flow
```
Excel Data → ExcelManager → Variables → StepExecutor → Screen Actions
     ↓                                         ↑
MacroEditor → Macro (steps) → ExecutionEngine ─┘
```

### Key Components

#### Execution Engine (`automation/engine.py`)
- Manages macro execution lifecycle and state machine
- Handles Excel row iteration and standalone execution
- Supports Excel workflow blocks (EXCEL_ROW_START/END)
- Emits signals for progress updates and row completion

#### Step System (`core/macro_types.py`)
- Base `MacroStep` class with common properties (enabled, error_handling, retry_count)
- `StepType` enum defining all available step types
- `StepFactory` for creating step instances
- Each step type has its own dialog class in `ui/dialogs/`

#### Excel Integration (`excel/excel_manager.py`)
- Handles Excel file loading via pandas/openpyxl
- Manages sheet/column mapping and status tracking
- Provides row data as variables for step execution
- Supports completion status updates

#### Variable System
- Excel column data automatically available as `${column_name}` variables
- Text substitution in keyboard input and other text fields
- Row-specific data binding during execution

### Step Execution Architecture
1. **StepExecutor** (`automation/executor.py`) - Executes individual steps
2. **Step Handlers** - Each StepType maps to a handler method
3. **Vision Module** (`vision/`) - Image matching and OCR capabilities
4. **Error Recovery** - Configurable per step (stop/continue/retry)

### Dialog System
- Each step type has a dedicated configuration dialog
- Dialogs inherit from QDialog and follow consistent patterns
- Excel column variables are passed to dialogs for dropdown population

### Excel Workflow Feature
- **Excel Blocks**: Special paired steps (EXCEL_ROW_START/END) that define iteration scope
- **Repeat Modes**: incomplete_only, specific_count, range, all
- **Auto Tab Switch**: Adding Excel blocks switches to Excel tab automatically
- **Pair ID System**: Start/end steps linked by unique pair_id

## Critical Implementation Details

### Import Handling
- `run_main.py` sets up proper Python path for absolute imports
- Always use absolute imports: `from automation.engine import ExecutionEngine`
- Import fixing is automatic when using run scripts

### PyQt5 Signal/Slot Pattern
```python
# Signal definition
stepAdded = pyqtSignal(MacroStep, int)  # step, index

# Connection
self.flow_widget.stepAdded.connect(self._on_change)

# Emission
self.stepAdded.emit(new_step, drop_index)
```

### Step Creation Pattern
```python
# In StepFactory
@staticmethod
def create_step(step_type: StepType) -> MacroStep:
    if step_type == StepType.MOUSE_CLICK:
        return MouseClickStep()
    # ... other types
```

### Error Handling Pattern
- All exceptions logged via `logger.app_logger`
- User-facing errors shown via QMessageBox
- Execution errors tracked in CSV logs

### Drag & Drop Implementation
- MIME types: `application/x-steptype`, `application/x-macrostep`, `application/x-excelblock`
- Drop position calculation via `_get_drop_index()`
- Visual feedback during drag operations

## File Organization

### Naming Conventions
- **Python files**: snake_case.py
- **Dialog classes**: `*StepDialog` in `ui/dialogs/*_step_dialog.py`
- **Widget classes**: `*Widget` in `ui/widgets/*_widget.py`
- **Batch scripts**: UPPERCASE.bat

### Key File Locations
- **Main entry**: `main.py`, `run_main.py`
- **Settings**: `src/config/settings.py` (AES-256 encrypted)
- **Localization**: `resources/locales/{en,ko}.json`
- **Logs**: `logs/` directory (execution logs, error reports)
- **Saved macros**: `.emf` files (encrypted)

## Windows-Specific Considerations
- Paths require double backslashes in JSON: `C:\\\\path\\\\to\\\\file`
- Screen coordinates are absolute (multi-monitor aware)
- DPI scaling handled automatically
- PyAutoGUI failsafe enabled (move mouse to corner to abort)

## Testing Approach
- Manual testing via GUI interaction
- Test batch files for specific features
- Error simulation through invalid inputs
- Multi-monitor and DPI scaling verification

## Performance Considerations
- Large Excel files (100+ rows) handled via pandas chunking
- Image matching uses OpenCV when available, falls back to PyAutoGUI
- Threading for non-blocking UI during execution
- Progress calculation optimized for nested loops

## Security Model
- Local-only operation (no network features)
- Macro files encrypted with user-specific key
- No credential storage in code
- Sensitive data masked in logs

## CRITICAL CODING PRINCIPLES - MUST FOLLOW

### 절대 금지 사항
1. **임시방편 코드 금지** - 현재 순간만 모면하기 위한 코드는 절대 사용하지 않습니다
2. **Quick Fix 금지** - 근본 원인을 해결하지 않고 증상만 가리는 수정은 하지 않습니다
3
### 필수 준수 사항
1. **근본적 해결** - 모든 문제는 근본 원인을 찾아 해결합니다
4. **명확한 문서화** - 변경 사항과 이유를 명확히 문서화합니다
5. **이전 버전 호환성** - 기존 기능을 깨뜨리지 않도록 주의합니다

### 코드 품질 기준
1. **가독성** - 복잡한 로직보다 읽기 쉬운 코드를 우선시합니다
2. **유지보수성** - 나중에 수정하기 쉬운 구조로 작성합니다
3. **재사용성** - 중복 코드를 피하고 재사용 가능한 컴포넌트로 만듭니다
4. **예외 처리** - 모든 예외 상황을 고려하여 처리합니다
5. **로깅** - 디버깅에 필요한 충분한 로그를 남깁니다

## OCR 엔진 정보

### PaddleOCR
- 한국어 텍스트 인식에 최적화
- 빠르고 가벼운 성능
- Python 3.8 ~ 3.11 지원 (Python 3.11 권장)
- 자동 설치 지원

## Python 버전 정보

### 지원 버전
- **권장**: Python 3.11 (최적 성능 및 완전 호환)
- **지원**: Python 3.8, 3.9, 3.10
- **미지원**: Python 3.12, 3.13 (PaddleOCR 미지원)

### 가상환경 설정
```bash
# Python 3.11 가상환경 생성 (권장)
SETUP_VENV311.bat

# 가상환경으로 실행
RUN_AUTO_VENV.bat
```