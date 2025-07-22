"""
Setup Python 3.13 virtual environment with compatible packages
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a command and print status"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] {description} - Success")
            if result.stdout:
                print(result.stdout)
        else:
            print(f"[FAIL] {description} - Failed")
            if result.stderr:
                print(f"Error: {result.stderr}")
        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] {description} - Exception: {e}")
        return False

def main():
    print("Python 3.13 Virtual Environment Setup")
    print("=" * 50)
    
    # Check Python version
    print(f"Current Python: {sys.version}")
    
    # Check if venv313 exists
    venv_path = os.path.join(os.path.dirname(__file__), "venv313")
    
    if os.path.exists(venv_path):
        print(f"\nvenv313 already exists at: {venv_path}")
    else:
        print(f"\nvenv313 not found. Please create it first with:")
        print("python -m venv venv313")
        return
    
    # Python executable in venv
    if sys.platform == "win32":
        python_exe = os.path.join(venv_path, "Scripts", "python.exe")
        pip_exe = os.path.join(venv_path, "Scripts", "pip.exe")
    else:
        python_exe = os.path.join(venv_path, "bin", "python")
        pip_exe = os.path.join(venv_path, "bin", "pip")
    
    if not os.path.exists(python_exe):
        print(f"Error: Python executable not found at {python_exe}")
        return
    
    # Upgrade pip
    run_command(f'"{python_exe}" -m pip install --upgrade pip', "Upgrading pip")
    
    # Install packages in order
    packages = [
        ("PyQt5>=5.15.0", "GUI Framework"),
        ("pandas>=2.0.0 openpyxl>=3.0.0", "Data Processing"),
        ("numpy==2.3.0", "NumPy 2.3.0 (Python 3.13 compatible)"),
        ("opencv-python==4.12.0.88", "OpenCV 4.12.0.88 (NumPy 2.x compatible)"),
        ("pyautogui>=0.9.53 pillow>=10.0.0 pynput>=1.7.0", "Screen Automation"),
        ("screeninfo>=0.8.0 mss>=9.0.0", "Screen Utilities"),
        ("cryptography>=41.0.0 chardet>=5.0.0 psutil>=5.9.0", "Security & Utils"),
    ]
    
    for package, description in packages:
        run_command(f'"{pip_exe}" install {package}', f"Installing {description}")
    
    # Install PyTorch CPU version for Windows
    print("\nInstalling PyTorch (CPU version)...")
    run_command(
        f'"{pip_exe}" install torch torchvision --index-url https://download.pytorch.org/whl/cpu',
        "Installing PyTorch CPU"
    )
    
    # Install EasyOCR
    run_command(f'"{pip_exe}" install easyocr>=1.7.0', "Installing EasyOCR")
    
    # Verify installations
    print("\n" + "=" * 50)
    print("Verifying installations...")
    print("=" * 50)
    
    modules_to_check = [
        ("numpy", "NumPy"),
        ("cv2", "OpenCV"),
        ("PyQt5.QtCore", "PyQt5"),
        ("pandas", "Pandas"),
        ("easyocr", "EasyOCR"),
        ("torch", "PyTorch"),
    ]
    
    for module, name in modules_to_check:
        try:
            result = subprocess.run(
                [python_exe, "-c", f"import {module}; print(f'{name}: ' + {module}.__version__ if hasattr({module}, '__version__') else 'installed')"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print(result.stdout.strip())
            else:
                print(f"{name}: Not installed")
        except:
            print(f"{name}: Error checking")
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print(f"To activate the environment, run:")
    print(f"venv313\\Scripts\\activate")
    print(f"\nTo run the application with Python 3.13:")
    print(f"RUN_PY313.bat")

if __name__ == "__main__":
    main()