# Product Requirements Document: Excel Macro Automation

## Product overview

### Document information
- **Title**: Excel Macro Automation PRD
- **Version**: 2.0.0
- **Date**: January 2025
- **Status**: Active

### Product summary
Excel Macro Automation is a Windows desktop application that automates repetitive tasks by reading data from Excel files and executing screen automation sequences. Built with PyQt5, it provides an intuitive visual drag-and-drop macro editor that enables non-technical users to create complex automation workflows without programming knowledge. The application bridges the gap between Excel data and screen-based repetitive tasks, significantly reducing manual effort and human error in data entry and processing workflows.

## Goals

### Business goals
- Reduce manual data entry time by 80% for repetitive Excel-based workflows
- Eliminate human errors in data transfer between Excel and other applications
- Enable non-technical staff to create and maintain their own automation workflows
- Provide a cost-effective alternative to enterprise RPA solutions for small to medium businesses
- Increase overall productivity by automating routine screen-based tasks

### User goals
- Create automation workflows without programming knowledge
- Automate repetitive data entry from Excel into web forms or desktop applications
- Process large Excel datasets efficiently with minimal manual intervention
- Build reliable macros that handle errors gracefully
- Save and share automation workflows with team members

### Non-goals
- Enterprise-wide orchestration of multiple automation instances
- Cloud-based execution or remote automation
- Web scraping or API integrations
- Mobile application automation
- Cross-platform support (currently Windows-only)

## User personas

### Primary user: Data Entry Specialist
- **Age**: 25-45
- **Technical skill**: Basic to intermediate computer skills
- **Role**: Processes Excel data daily, enters information into various systems
- **Pain points**: Repetitive manual data entry, prone to errors, time-consuming tasks
- **Needs**: Simple way to automate repetitive tasks, visual feedback during execution

### Secondary user: Office Administrator
- **Age**: 30-55
- **Technical skill**: Intermediate computer skills
- **Role**: Manages office workflows, creates reports, processes forms
- **Pain points**: Multiple systems require same data, manual copy-paste workflows
- **Needs**: Reliable automation, error handling, ability to modify workflows

### Tertiary user: Small Business Owner
- **Age**: 35-60
- **Technical skill**: Variable
- **Role**: Oversees business operations, seeks efficiency improvements
- **Pain points**: Limited budget for automation tools, staff time wasted on repetitive tasks
- **Needs**: Affordable automation solution, easy to implement and maintain

### Role-based access
- **Standard User**: Create, edit, and execute macros
- **Power User**: Access to advanced features like OCR configuration and custom scripts
- **Administrator**: Manage application settings, encryption keys, and user preferences

## Functional requirements

### High priority (P0)
- Excel file loading and sheet/column mapping
- Visual drag-and-drop macro editor
- Basic automation steps (mouse click, keyboard input, wait)
- Macro execution with progress tracking
- Error handling and recovery options
- Save/load encrypted macro files
- Variable substitution from Excel data

### Medium priority (P1)
- Image-based element detection
- OCR text recognition and search
- Conditional logic (if-then-else)
- Excel workflow blocks for row iteration
- Multi-language support (English, Korean)
- Execution logging and reporting
- Hotkey controls during execution

### Low priority (P2)
- Advanced image matching with confidence levels
- Custom loop constructs
- Screenshot capture during execution
- Floating status widget
- System tray integration
- Human-like mouse movement simulation
- Macro file encryption with AES-256

## User experience

### Entry points
- Desktop shortcut or Start menu launch
- System tray icon (when minimized)
- File association with .emf (Encrypted Macro File) extension
- Command-line execution for automation

### Core experience
1. **Excel Setup**: User loads Excel file, selects sheet, and maps columns
2. **Macro Creation**: Drag-and-drop steps from palette to create workflow
3. **Configuration**: Configure each step with visual dialogs
4. **Testing**: Preview and test individual steps
5. **Execution**: Run macro with real-time progress feedback
6. **Results**: View execution report and Excel status updates

### Advanced features
- **Excel Workflow Blocks**: Define iteration scope for processing multiple rows
- **Dynamic Text Search**: OCR-based text detection with variable substitution
- **Conditional Execution**: If-then-else logic based on image/text presence
- **Error Recovery**: Configurable retry and error handling per step
- **Variable System**: Use Excel column data as variables in any text field

### UI/UX highlights
- Three-tab interface (Excel, Editor, Run) for clear workflow separation
- Visual step palette with icons and descriptions
- Drag-and-drop reordering with visual feedback
- Real-time validation and error highlighting
- Progress visualization during execution
- Contextual help and tooltips

## Narrative
Sarah, a data entry specialist at a medical clinic, starts her day by opening Excel Macro Automation. She loads the patient appointment spreadsheet and quickly maps the patient name, ID, and appointment time columns. Using the visual editor, she drags in steps to open the clinic's scheduling system, search for each patient by ID, and update their appointment times. She adds image recognition steps to handle different screen states and includes error handling for missing patients. After testing with a few rows, she runs the macro on all 200 appointments, watching the progress bar as the tool automatically processes each row, updating the Excel file with completion status. What used to take her 3 hours now completes in 20 minutes, and she can focus on more meaningful patient care tasks while the automation runs in the background.

## Success metrics

### User-centric metrics
- Task completion time reduction: >75%
- Error rate reduction: >90%
- User satisfaction score: >4.5/5
- Time to create first macro: <30 minutes
- Successful macro execution rate: >95%

### Business metrics
- Number of active users per month
- Average macros created per user
- Total automation hours saved
- ROI through time savings
- User retention rate: >80%

### Technical metrics
- Application startup time: <3 seconds
- Step execution accuracy: >99%
- Memory usage: <500MB during execution
- Crash rate: <0.1%
- OCR accuracy: >95% for standard fonts

## Technical considerations

### Integration points
- Windows OS APIs for screen capture and input simulation
- PyAutoGUI for cross-application automation
- Excel file formats via pandas/openpyxl
- PaddleOCR for text recognition
- OpenCV for image matching (optional)

### Data storage/privacy
- Local-only data storage (no cloud connectivity)
- AES-256 encryption for saved macro files
- User-specific encryption keys
- No credential storage in application
- Sensitive data masked in logs

### Scalability/performance
- Handle Excel files up to 10,000 rows
- Support for multi-monitor setups
- DPI scaling awareness
- Chunked processing for large datasets
- Threading for non-blocking UI

### Potential challenges
- Screen resolution dependencies
- Application UI changes breaking image recognition
- OCR accuracy on non-standard fonts
- Performance on older hardware
- Anti-automation software detection

## Milestones & sequencing

### Project estimate
- Total development time: 6 months
- Maintenance and updates: Ongoing

### Team size
- 2 developers (1 senior, 1 mid-level)
- 1 UI/UX designer (part-time)
- 1 QA engineer (part-time)
- 1 technical writer (contract)

### Suggested phases

#### Phase 1: Core Foundation (2 months)
- Basic UI framework with three tabs
- Excel file loading and parsing
- Simple macro editor with basic steps
- Mouse and keyboard automation
- Save/load functionality

#### Phase 2: Advanced Features (2 months)
- Image recognition integration
- OCR text search functionality
- Conditional logic implementation
- Excel workflow blocks
- Error handling system

#### Phase 3: Polish & Optimization (1 month)
- UI/UX refinements
- Performance optimization
- Multi-language support
- Documentation and help system
- Installer creation

#### Phase 4: Enhanced Features (1 month)
- Floating status widget
- System tray integration
- Advanced reporting
- Encryption implementation
- Beta testing and bug fixes

## User stories

### Core Functionality
**US-001**: Load Excel File
- **Title**: User loads Excel file for automation
- **Description**: As a user, I want to load an Excel file so that I can use its data in my automation workflow
- **Acceptance criteria**:
  - User can browse and select Excel files (.xlsx, .xls)
  - Application displays all sheets in the file
  - User can select specific sheet to work with
  - Column headers are automatically detected and displayed
  - File path is remembered for quick reload

**US-002**: Map Excel Columns
- **Title**: User maps Excel columns to variables
- **Description**: As a user, I want to map Excel columns to named variables so that I can use the data in my macro steps
- **Acceptance criteria**:
  - All columns from selected sheet are shown
  - User can assign friendly names to columns
  - System validates column mappings
  - Mappings are saved with the macro
  - Preview shows sample data from mapped columns

**US-003**: Create Basic Mouse Click Step
- **Title**: User creates mouse click automation step
- **Description**: As a user, I want to create a mouse click step so that I can automate clicking on screen elements
- **Acceptance criteria**:
  - User can capture click coordinates
  - Preview shows click location
  - User can set click type (single/double/right)
  - User can test the click action
  - Click coordinates work across different screen resolutions

**US-004**: Create Keyboard Input Step
- **Title**: User creates keyboard typing step
- **Description**: As a user, I want to create a keyboard input step so that I can automate typing text
- **Acceptance criteria**:
  - User can enter text to type
  - Support for variable substitution from Excel
  - User can set typing speed
  - Special keys are supported (Tab, Enter, etc.)
  - Preview shows the text with variables resolved

**US-005**: Execute Macro
- **Title**: User executes complete macro
- **Description**: As a user, I want to execute my macro so that the automation runs through all defined steps
- **Acceptance criteria**:
  - Clear start button to begin execution
  - Real-time progress indicator
  - Current step highlighting
  - Pause/stop controls available
  - Execution completes successfully

### Excel Integration
**US-006**: Process Multiple Excel Rows
- **Title**: User processes multiple Excel rows in sequence
- **Description**: As a user, I want to process multiple rows from my Excel file so that I can automate repetitive tasks for entire datasets
- **Acceptance criteria**:
  - User can select which rows to process
  - Each row's data is available as variables
  - Progress shows current row being processed
  - Failed rows are marked in Excel
  - Completed rows show success status

**US-007**: Excel Workflow Blocks
- **Title**: User creates Excel workflow blocks
- **Description**: As a user, I want to define start and end of Excel row processing so that I can control which steps repeat for each row
- **Acceptance criteria**:
  - Drag Excel Start/End blocks from palette
  - Steps between blocks repeat for each row
  - Can configure row selection (all/incomplete/range)
  - Visual indication of block boundaries
  - Nested blocks are prevented

**US-008**: Update Excel Status
- **Title**: System updates Excel row status
- **Description**: As a user, I want the system to update Excel rows with completion status so that I can track progress
- **Acceptance criteria**:
  - Status column is automatically added if missing
  - Each row shows completion status after processing
  - Failed rows show error information
  - User can re-run only failed rows
  - Status persists between sessions

### Advanced Automation
**US-009**: Image Recognition Click
- **Title**: User clicks based on image recognition
- **Description**: As a user, I want to click on elements identified by image matching so that I can automate dynamic interfaces
- **Acceptance criteria**:
  - User can capture reference image
  - System finds matching image on screen
  - Confidence threshold is configurable
  - Click occurs at image center or offset
  - Error handling for image not found

**US-010**: OCR Text Search
- **Title**: User searches and clicks text using OCR
- **Description**: As a user, I want to find and click on text elements using OCR so that I can automate text-based interfaces
- **Acceptance criteria**:
  - User can define search text or use Excel variable
  - OCR runs on specified screen region
  - Found text is highlighted in preview
  - User can click on found text
  - Handles partial text matches

**US-011**: Conditional Execution
- **Title**: User creates conditional logic
- **Description**: As a user, I want to create if-then-else logic so that my macro can handle different scenarios
- **Acceptance criteria**:
  - User can set conditions (image exists, text exists, etc.)
  - True and false branches are clearly indicated
  - Steps can be added to each branch
  - Conditions can use Excel variables
  - Visual flow diagram shows logic

**US-012**: Wait Conditions
- **Title**: User adds dynamic wait conditions
- **Description**: As a user, I want to wait for specific conditions so that my macro handles timing issues
- **Acceptance criteria**:
  - Wait for fixed time duration
  - Wait for image to appear
  - Wait for text to appear
  - Configurable timeout values
  - Clear indication when waiting

### Error Handling
**US-013**: Configure Error Handling
- **Title**: User configures error handling per step
- **Description**: As a user, I want to configure how each step handles errors so that my macro is resilient
- **Acceptance criteria**:
  - Each step has error handling options
  - Options include: stop, continue, retry
  - Retry count is configurable
  - Error details are logged
  - User can set global error defaults

**US-014**: View Execution Logs
- **Title**: User views detailed execution logs
- **Description**: As a user, I want to view execution logs so that I can debug issues and verify successful runs
- **Acceptance criteria**:
  - Logs show timestamp for each step
  - Success/failure status is clear
  - Error messages are descriptive
  - Logs can be filtered by date/status
  - Export logs to file option

### File Management
**US-015**: Save Macro File
- **Title**: User saves macro configuration
- **Description**: As a user, I want to save my macro so that I can reuse it later
- **Acceptance criteria**:
  - Save dialog with name and description
  - File is encrypted for security
  - Overwrites require confirmation
  - Recent files list is updated
  - Save location is configurable

**US-016**: Load Macro File
- **Title**: User loads saved macro
- **Description**: As a user, I want to load a previously saved macro so that I can run or modify it
- **Acceptance criteria**:
  - File browser shows .emf files
  - Macro loads with all settings intact
  - Excel file path is validated
  - Missing Excel columns are highlighted
  - User can update file paths

### Security
**US-017**: Secure Macro Storage
- **Title**: System encrypts macro files
- **Description**: As a user, I want my macro files encrypted so that sensitive information is protected
- **Acceptance criteria**:
  - Files use AES-256 encryption
  - Encryption is transparent to user
  - Corrupted files show clear error
  - No passwords stored in files
  - Each user has unique encryption key

### UI/UX Features
**US-018**: Drag and Drop Editor
- **Title**: User arranges steps via drag and drop
- **Description**: As a user, I want to drag and drop steps so that I can easily build and modify my macro
- **Acceptance criteria**:
  - Steps can be dragged from palette
  - Drop zones are clearly indicated
  - Steps can be reordered by dragging
  - Invalid drops are prevented
  - Undo/redo is supported

**US-019**: Visual Step Configuration
- **Title**: User configures steps through dialogs
- **Description**: As a user, I want visual dialogs for step configuration so that setup is intuitive
- **Acceptance criteria**:
  - Double-click opens configuration
  - All options have clear labels
  - Help text explains each option
  - Preview shows configuration effect
  - Validation prevents invalid settings

**US-020**: Multi-language Support
- **Title**: User selects interface language
- **Description**: As a user, I want to use the application in my preferred language
- **Acceptance criteria**:
  - Language selection in settings
  - All UI text is translated
  - Currently supports English and Korean
  - Language change takes effect immediately
  - Date/number formats follow locale

### Execution Control
**US-021**: Pause and Resume Execution
- **Title**: User pauses and resumes macro execution
- **Description**: As a user, I want to pause execution so that I can handle unexpected situations
- **Acceptance criteria**:
  - Hotkey (F9) pauses execution
  - Visual indication of paused state
  - Resume continues from paused step
  - UI remains responsive when paused
  - Can modify macro while paused

**US-022**: Emergency Stop
- **Title**: User performs emergency stop
- **Description**: As a user, I want an emergency stop function so that I can immediately halt problematic executions
- **Acceptance criteria**:
  - ESC key stops execution immediately
  - Mouse to corner triggers failsafe
  - Clear confirmation of stop
  - Partial results are preserved
  - Can resume from last successful step

### Monitoring
**US-023**: Floating Status Widget
- **Title**: User monitors execution via floating widget
- **Description**: As a user, I want a floating status widget so that I can monitor progress while using other applications
- **Acceptance criteria**:
  - Widget shows current step and progress
  - Always-on-top option
  - Minimal/normal/detailed view modes
  - Click-through when inactive
  - Auto-hide after completion

**US-024**: System Tray Integration
- **Title**: Application runs from system tray
- **Description**: As a user, I want system tray integration so that the application doesn't clutter my taskbar
- **Acceptance criteria**:
  - Minimize to system tray option
  - Tray icon shows execution status
  - Right-click menu for quick actions
  - Balloon notifications for events
  - Double-click restores window

### Authentication and Access Control
**US-025**: Secure Application Access
- **Title**: User accesses application securely
- **Description**: As a user with sensitive data, I want secure access to the application so that my automation workflows are protected
- **Acceptance criteria**:
  - Application requires Windows user authentication
  - Encryption keys are tied to user profile
  - No separate login required for local use
  - Settings are user-specific
  - Shared macros require explicit file sharing