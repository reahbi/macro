# PowerShell script to run the macro application on Windows
# This script helps run the WSL-developed app in native Windows environment

Write-Host "=== Excel Macro Automation Tool - Windows Runner ===" -ForegroundColor Cyan

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python is not installed or not in PATH!" -ForegroundColor Red
    Write-Host "Please install Python from python.org" -ForegroundColor Yellow
    exit 1
}

# Get the script directory
$scriptPath = $PSScriptRoot
if (-not $scriptPath) {
    $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
}

# Handle UNC/WSL paths
if ($scriptPath -like "\\wsl*" -or $scriptPath -like "\\\\*") {
    Write-Host "Detected WSL/UNC path. Creating temporary copy..." -ForegroundColor Yellow
    
    $tempDir = Join-Path $env:TEMP "excel_macro_tool"
    if (Test-Path $tempDir) {
        Remove-Item $tempDir -Recurse -Force
    }
    
    # Create the directory first
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    
    Write-Host "Copying files to: $tempDir" -ForegroundColor Yellow
    
    # Copy files and directories separately to avoid errors
    Get-ChildItem -Path $scriptPath -File | ForEach-Object {
        Copy-Item -Path $_.FullName -Destination $tempDir -Force
    }
    
    # Copy src directory
    if (Test-Path (Join-Path $scriptPath "src")) {
        Copy-Item -Path (Join-Path $scriptPath "src") -Destination $tempDir -Recurse -Force
    }
    
    # Copy other important directories if they exist
    @("resources", "captures", "docs") | ForEach-Object {
        $dirPath = Join-Path $scriptPath $_
        if (Test-Path $dirPath) {
            Copy-Item -Path $dirPath -Destination $tempDir -Recurse -Force
        }
    }
    
    $scriptPath = $tempDir
}

# Change to the script directory
Set-Location $scriptPath
Write-Host "Working directory: $(Get-Location)" -ForegroundColor Green

# Check if virtual environment exists
$venvPath = Join-Path $scriptPath "venv"
$venvActivate = Join-Path $venvPath "Scripts\Activate.ps1"

if (Test-Path $venvActivate) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & $venvActivate
} else {
    Write-Host "No virtual environment found. Creating one..." -ForegroundColor Yellow
    python -m venv venv
    & $venvActivate
}

# Install/update dependencies
Write-Host "`nChecking dependencies..." -ForegroundColor Yellow
$requirementsPath = Join-Path $scriptPath "requirements.txt"

if (Test-Path $requirementsPath) {
    Write-Host "Installing requirements..." -ForegroundColor Yellow
    pip install -r requirements.txt --quiet
} else {
    Write-Host "No requirements.txt found. Installing core packages..." -ForegroundColor Yellow
    pip install PyQt5 pandas openpyxl pyautogui pillow screeninfo cryptography --quiet
}

# Set environment variables for better Windows compatibility
$env:QT_AUTO_SCREEN_SCALE_FACTOR = "1"
$env:QT_ENABLE_HIGHDPI_SCALING = "1"

# Run the application
Write-Host "`nStarting Excel Macro Automation Tool..." -ForegroundColor Green
Write-Host "Note: Running in native Windows mode for better GUI compatibility" -ForegroundColor Cyan

try {
    python run_main_fixed.py
} catch {
    Write-Host "`nError running application: $_" -ForegroundColor Red
    Write-Host "Press any key to exit..."
    $null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
}