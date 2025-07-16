# Excel Macro Automation

Excel-based task automation macro desktop application for Windows.

## Overview

This application allows users to automate repetitive tasks by reading task lists from Excel files and executing predefined sequences of mouse, keyboard, and screen recognition actions.

## Features

- Excel file integration with sheet/column mapping
- Drag & drop macro editor
- Mouse and keyboard automation
- Image search and OCR capabilities
- Conditional logic and loops
- Execution logging
- Multi-language support (Korean/English)

## Requirements

- Windows 10/11 64-bit
- Python 3.8+
- 1280x720 minimum screen resolution

## Installation

1. Clone the repository:
```bash
git clone https://github.com/reahbi/macro.git
cd macro
```

2. Create virtual environment (requires python3-venv package):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Development

Run the application:
```bash
python main.py
```

Run tests:
```bash
pytest
```

Build executable:
```bash
pyinstaller excel_macro.spec
```

## Project Structure

```
macro/
├── src/
│   ├── excel/        # Excel integration modules
│   ├── ui/           # PyQt5 GUI components
│   ├── automation/   # Automation engine
│   ├── core/         # Core business logic
│   ├── plugin/       # Plugin system
│   ├── utils/        # Utilities (encryption, etc.)
│   ├── config/       # Configuration management
│   └── logger/       # Logging system
├── tests/            # Test suites
├── resources/        # Icons, templates, locales
├── docs/             # Documentation
└── main.py           # Application entry point
```

## License

MIT License