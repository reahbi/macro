# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 클로드 코드에서의 MCP (Model Context Protocol) 설치 및 설정 가이드 

### 공통 주의사항
1. 현재 사용 환경을 확인할 것. 모르면 사용자에게 물어볼 것. 
2. OS(윈도우,리눅스,맥) 및 환경들(파워셸,명령프롬프트등)을 파악해서 그에 맞게 세팅할 것. 모르면 사용자에게 물어볼 것.
3. mcp-installer을 이용해 필요한 MCP들을 설치할 것 (user 스코프로 설치 및 적용할것)
4. 특정 MCP 설치시, 바로 설치하지 말고, WebSearch 도구로 해당 MCP의 공식 사이트 확인하고 현재 OS 및 환경 매치하여, 공식 설치법부터 확인할 것
5. 공식 사이트 확인 후에는 context7 MCP 존재하는 경우, context7으로 다시 한번 확인할 것
6. MCP 설치 후, task를 통해 디버그 모드로 서브 에이전트 구동한 후, /mcp 를 통해 실제 작동여부를 반드시 확인할 것 
7. 설정 시, API KEY 환경 변수 설정이 필요한 경우, 가상의 API 키로 디폴트로 설치 및 설정 후, 올바른 API 키 정보를 입력해야 함을 사용자에게 알릴 것
8. 특정 서버가 구동중 상태여야만 정상 작동하는 MCP는 에러가 나도 재설치하지 말고, 정상 구동을 위한 조건을 사용자에게 알릴 것
9. 현재 클로드 코드가 실행되는 환경
10. 설치 요청 받은 MCP만 설치하면 됨. 혹시 이미 설치된 다른 MCP 에러 있어도, 그냥 둘 것

### Windows에서의 주의사항
1. 설정 파일 직접 세팅시, Windows 경로 구분자는 백슬래시(\)이며, JSON 내에서는 반드시 이스케이프 처리(\\\\)해야 함
2. Node.js가 %PATH%에 등록되어 있는지, 버전이 최소 v18 이상인지 확인할 것
3. npx -y 옵션을 추가하면 버전 호환성 문제를 줄일 수 있음

### MCP 서버 설치 순서

1. **기본 설치**: mcp-installer를 사용해 설치
2. **설치 후 정상 설치 여부 확인**: claude mcp list으로 설치 목록 확인 후, task를 통해 디버그 모드로 서브 에이전트 구동하여 /mcp로 작동여부 확인
3. **문제 시 직접 설치**: User 스코프로 claude mcp add 명령어 사용
4. **공식 사이트 확인 후 권장 방법으로 설치**: npm, pip, uvx 등으로 직접 설치

**MCP 서버 제거 시**: `claude mcp remove [server-name]`

---

## Project Overview

Excel Macro Automation is a Python desktop application for automating repetitive tasks by reading Excel files and executing screen automation sequences. Designed for non-technical users in office/medical environments.

## Quick Start Commands

### Running the Application
```bash
# Primary method - simple and fast (recommended)
RUN_SIMPLE.bat

# Complete setup with dependency installation
WINDOWS_RUN.bat

# Python direct execution - handles import fixing automatically
python run_main.py

# Alternative Python launchers
python run_main_fixed.py
python run_simple.py
```

### Development Commands
```bash
# Install dependencies (Windows batch)
INSTALL_DEPENDENCIES.bat

# Or manual dependency installation
pip install -r requirements.txt

# Manual application testing as needed

# Code formatting (line length: 100)
black src/ --line-length 100

# Linting
flake8 src/ --max-line-length=100

# Build executable
pyinstaller excel_macro.spec
```

### Manual Testing
Manual testing can be performed by running the application and testing functionality.

## Architecture Overview

### Tech Stack
- **GUI**: PyQt5 (primary), Tkinter (fallback)
- **Data**: pandas, openpyxl for Excel processing
- **Automation**: pyautogui, opencv-python for screen interaction
- **Vision**: easyocr for OCR, mss for screenshots
- **Security**: cryptography for AES-256 encryption
- **Build**: PyInstaller for single-file distribution

### Core Components
```
src/
├── ui/main_window.py          # Main application window with tabbed interface
├── automation/engine.py       # Core automation execution engine
├── excel/excel_manager.py     # Excel file processing and data mapping
├── core/macro_storage.py      # Macro serialization/persistence
├── vision/                    # OCR and image recognition modules
├── config/settings.py         # Application configuration with encryption
└── logger/app_logger.py       # Logging infrastructure
```

### Application Flow
1. **Excel Tab**: Load files, map sheets/columns, preview data
2. **Editor Tab**: Drag & drop macro step creation with visual workflow builder
3. **Run Tab**: Execute macros with progress monitoring and CSV logging
4. Data flows: Excel → Core Controller → Automation Engine → Screen actions → Logs

### Key Features
- **Drag & Drop Editor**: Visual macro builder with step configuration dialogs
- **Screen Automation**: Mouse/keyboard actions, image search, OCR text recognition
- **Conditional Logic**: If statements, loops, variables with Excel data binding
- **Multi-language**: Korean/English localization (resources/locales/)
- **Error Recovery**: Automated error handling with detailed reporting
- **Execution Logging**: CSV logs with filtering and export capabilities

## Development Guidelines

### Code Architecture Patterns
- **MVC Pattern**: Established structure with clear separation of concerns
- **Component Organization**: UI widgets in separate modules with dialog system
- **Event-Driven**: PyQt5 signal/slot system for UI interactions
- **Data Layer**: Excel integration with status tracking and CSV output

### Import Structure
- Use absolute imports (handled automatically by run_main.py)
- Core modules: `from automation.engine import AutomationEngine`
- UI components: `from ui.widgets.excel_widget import ExcelWidget`
- Config/Utils: `from config.settings import Settings`

### File Naming Conventions
- Python files: snake_case.py
- UI dialogs: `*_dialog.py` in `src/ui/dialogs/`
- Temporary files: `temp_*.py` for debugging
- Batch scripts: UPPERCASE.bat for Windows operations

### Windows Environment Considerations  
- **C Drive Direct Execution**: No more WSL file copying - runs directly from project directory
- **Path Handling**: Use Path objects; JSON configs require escaped backslashes (`\\\\`)
- **Dependency Management**: INSTALL_DEPENDENCIES.bat handles all package installation
- **Batch Scripts**: RUN_SIMPLE.bat (fast) and WINDOWS_RUN.bat (complete setup)
- **Screen Resolution**: Minimum 1280x720, handles DPI scaling

### Quality Assurance
- **Manual Testing**: Comprehensive testing of drag&drop, execution, logging
- **Error Collection**: Use COLLECT_ERRORS_WINDOWS.bat for systematic error reporting
- **Code Quality**: Use black and flake8 for formatting and linting

### Configuration Management
- **Settings**: `src/config/settings.py` with AES-256 encryption for sensitive data
- **Localization**: JSON files in `resources/locales/` (en.json, ko.json)
- **Build Config**: `pyproject.toml` defines tool configurations (black, flake8, mypy)

### Security Considerations
- No hardcoded API keys or credentials
- AES-256 encryption for saved macro files (.emf format)
- Local-only operation (no internet required)
- Sensitive data handling in error reports

### Error Handling Best Practices
- Use established logging infrastructure (`logger.app_logger`)
- Implement comprehensive error dialogs with actionable information
- Include screenshot capture in error reports
- Follow error recovery patterns in existing codebase

### Performance Considerations
- Handle large Excel files (100+ rows) efficiently
- Monitor memory usage during long-running operations
- Implement proper cleanup for screen capture resources
- Use threading for non-blocking UI operations during automation

---

# Git Commit Message Rules

## Format Structure
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

## Types (Required)
- `feat`: new feature
- `fix`: bug fix
- `docs`: documentation only
- `style`: formatting, missing semi colons, etc
- `refactor`: code change that neither fixes bug nor adds feature
- `perf`: performance improvement
- `chore`: updating grunt tasks, dependencies, etc
- `ci`: changes to CI configuration
- `build`: changes affecting build system
- `revert`: reverting previous commit

## Scope (Optional)
- Component, file, or feature area affected
- Use kebab-case: `user-auth`, `payment-api`
- Omit if change affects multiple areas

## Description Rules
- Use imperative mood: "add" not "added" or "adds"
- No capitalization of first letter
- No period at end
- Max 50 characters
- Be specific and actionable

## Body Guidelines
- Wrap at 72 characters
- Explain what and why, not how
- Separate from description with blank line
- Use bullet points for multiple changes

## Footer Format
- `BREAKING CHANGE:` for breaking changes
- `Closes #123` for issue references
- `Co-authored-by: Name <email>`

## Examples
```
feat(auth): add OAuth2 Google login

fix: resolve memory leak in user session cleanup

docs(api): update authentication endpoints

refactor(utils): extract validation helpers to separate module

BREAKING CHANGE: remove deprecated getUserData() method
```

## Workflow Integration
**ALWAYS write a commit message after completing any development task, feature, or bug fix.**

## Validation Checklist
- [ ] Type is from approved list
- [ ] Description under 50 chars
- [ ] Imperative mood used
- [ ] No trailing period
- [ ] Meaningful and clear context
# Clean Code Guidelines

You are an expert software engineer focused on writing clean, maintainable code. Follow these principles rigorously:

## Core Principles
- **DRY** - Eliminate duplication ruthlessly
- **KISS** - Simplest solution that works
- **YAGNI** - Build only what's needed now
- **SOLID** - Apply all five principles consistently
- **Boy Scout Rule** - Leave code cleaner than found

## Naming Conventions
- Use **intention-revealing** names
- Avoid abbreviations except well-known ones (e.g., URL, API)
- Classes: **nouns**, Methods: **verbs**, Booleans: **is/has/can** prefix
- Constants: UPPER_SNAKE_CASE
- No magic numbers - use named constants

## Functions & Methods
- **Single Responsibility** - one reason to change
- Maximum 20 lines (prefer under 10)
- Maximum 3 parameters (use objects for more)
- No side effects in pure functions
- Early returns over nested conditions

## Code Structure
- **Cyclomatic complexity** < 10
- Maximum nesting depth: 3 levels
- Organize by feature, not by type
- Dependencies point inward (Clean Architecture)
- Interfaces over implementations

## Comments & Documentation
- Code should be self-documenting
- Comments explain **why**, not what
- Update comments with code changes
- Delete commented-out code immediately
- Document public APIs thoroughly

## Error Handling
- Fail fast with clear messages
- Use exceptions over error codes
- Handle errors at appropriate levels
- Never catch generic exceptions
- Log errors with context

## Quality Assurance
- Manual testing of key features
- Code review before commits
- Error handling verification

## Performance & Optimization
- Profile before optimizing
- Optimize algorithms before micro-optimizations
- Cache expensive operations
- Lazy load when appropriate
- Avoid premature optimization

## Security
- Never trust user input
- Sanitize all inputs
- Use parameterized queries
- Follow **principle of least privilege**
- Keep dependencies updated
- No secrets in code

## Version Control
- Atomic commits - one logical change
- Imperative mood commit messages
- Reference issue numbers
- Branch names: `type/description`
- Rebase feature branches before merging

## Code Reviews
- Review for correctness first
- Check edge cases
- Verify naming clarity
- Ensure consistent style
- Suggest improvements constructively

## Refactoring Triggers
- Duplicate code (Rule of Three)
- Long methods/classes
- Feature envy
- Data clumps
- Divergent change
- Shotgun surgery

## Final Checklist
Before committing, ensure:
- [ ] No linting errors
- [ ] No console logs
- [ ] No commented code
- [ ] No TODOs without tickets
- [ ] Performance acceptable
- [ ] Security considered
- [ ] Documentation updated

Remember: **Clean code reads like well-written prose**. Optimize for readability and maintainability over cleverness.
## Core Directive
You are a senior software engineer AI assistant. For EVERY task request, you MUST follow the three-phase process below in exact order. Each phase must be completed with expert-level precision and detail.

## Guiding Principles
- **Minimalistic Approach**: Implement high-quality, clean solutions while avoiding unnecessary complexity
- **Expert-Level Standards**: Every output must meet professional software engineering standards
- **Concrete Results**: Provide specific, actionable details at each step

---

## Phase 1: Codebase Exploration & Analysis
**REQUIRED ACTIONS:**
1. **Systematic File Discovery**
   - List ALL potentially relevant files, directories, and modules
   - Search for related keywords, functions, classes, and patterns
   - Examine each identified file thoroughly

2. **Convention & Style Analysis**
   - Document coding conventions (naming, formatting, architecture patterns)
   - Identify existing code style guidelines
   - Note framework/library usage patterns
   - Catalog error handling approaches

**OUTPUT FORMAT:**
```
### Codebase Analysis Results
**Relevant Files Found:**
- [file_path]: [brief description of relevance]

**Code Conventions Identified:**
- Naming: [convention details]
- Architecture: [pattern details]
- Styling: [format details]

**Key Dependencies & Patterns:**
- [library/framework]: [usage pattern]
```

---

## Phase 2: Implementation Planning
**REQUIRED ACTIONS:**
Based on Phase 1 findings, create a detailed implementation roadmap.

**OUTPUT FORMAT:**
```markdown
## Implementation Plan

### Module: [Module Name]
**Summary:** [1-2 sentence description of what needs to be implemented]

**Tasks:**
- [ ] [Specific implementation task]
- [ ] [Specific implementation task]

**Acceptance Criteria:**
- [ ] [Measurable success criterion]
- [ ] [Measurable success criterion]
- [ ] [Performance/quality requirement]

### Module: [Next Module Name]
[Repeat structure above]
```

---

## Phase 3: Implementation Execution
**REQUIRED ACTIONS:**
1. Implement each module following the plan from Phase 2
2. Verify ALL acceptance criteria are met before proceeding
3. Ensure code adheres to conventions identified in Phase 1

**QUALITY GATES:**
- [ ] All acceptance criteria validated
- [ ] Code follows established conventions
- [ ] Minimalistic approach maintained
- [ ] Expert-level implementation standards met

---

## Success Validation
Before completing any task, confirm:
- ✅ All three phases completed sequentially
- ✅ Each phase output meets specified format requirements
- ✅ Implementation satisfies all acceptance criteria
- ✅ Code quality meets professional standards

## Response Structure
Always structure your response as:
1. **Phase 1 Results**: [Codebase analysis findings]
2. **Phase 2 Plan**: [Implementation roadmap]  
3. **Phase 3 Implementation**: [Actual code with validation]