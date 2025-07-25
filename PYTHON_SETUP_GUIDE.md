# Python Setup Guide

## Quick Start

1. **Install Python 3.11**
   - Download from: https://www.python.org/downloads/
   - During installation, check "Add Python to PATH"

2. **Setup Virtual Environment**
   ```bash
   SETUP_VENV311.bat
   ```

3. **Run Application**
   ```bash
   RUN_AUTO_VENV.bat
   ```

## Python Version Requirements

- **Python 3.11** - Recommended (Best performance & full compatibility)
- **Python 3.8-3.10** - Supported (PaddleOCR compatible)
- **Python 3.12-3.13** - Not supported (PaddleOCR incompatible)

## Virtual Environment

The application uses `venv311` as the default virtual environment:
- Located in: `./venv311/`
- Python version: 3.11
- All dependencies including PaddleOCR

## Batch Files

| File | Purpose |
|------|---------|
| `SETUP_VENV311.bat` | Creates Python 3.11 virtual environment |
| `RUN_AUTO_VENV.bat` | Auto-detects and runs with venv |
| `RUN_PY311.bat` | Direct execution with Python 3.11 |
| `INSTALL_DEPENDENCIES.bat` | Installs all dependencies |

## Troubleshooting

### Python 3.11 Not Found
```bash
# Check installed Python versions
CHECK_PYTHON_VERSIONS.bat
```

### Virtual Environment Issues
```bash
# Recreate virtual environment
SETUP_VENV311.bat
```

### Dependency Installation Failed
```bash
# Install dependencies manually
venv311\Scripts\activate
pip install -r requirements.txt
```