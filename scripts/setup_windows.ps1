# AgriSense Edge — Windows Setup Script
# Run from the repo root: .\scripts\setup_windows.ps1

param(
    [switch]$SkipFrontend,
    [switch]$ExportEnv
)

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AgriSense Edge — Windows Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Python not found. Install Python 3.10+ from python.org" -ForegroundColor Red
    exit 1
}
Write-Host "Python: $pythonVersion" -ForegroundColor Green

# Check architecture
$arch = python -c "import struct; print(struct.calcsize('P') * 8)"
Write-Host "Python architecture: ${arch}-bit" -ForegroundColor Green

# Create runtime environment
Write-Host ""
Write-Host "── Creating runtime environment (.venv) ──" -ForegroundColor Yellow

if (-not (Test-Path ".venv")) {
    python -m venv .venv
    Write-Host "Created .venv" -ForegroundColor Green
} else {
    Write-Host ".venv already exists" -ForegroundColor Green
}

# Activate
.\.venv\Scripts\Activate.ps1

# Install runtime dependencies
Write-Host ""
Write-Host "── Installing runtime dependencies ──" -ForegroundColor Yellow
pip install -e ".[all]"

# Try to install QNN support (Windows ARM64 only)
$machine = python -c "import platform; print(platform.machine())"
if ($machine -eq "ARM64") {
    Write-Host ""
    Write-Host "── Installing QNN NPU support ──" -ForegroundColor Yellow
    pip install onnxruntime-qnn
}

# Export environment (if requested)
if ($ExportEnv) {
    Write-Host ""
    Write-Host "── Creating export environment (.venv-export) ──" -ForegroundColor Yellow

    if (-not (Test-Path ".venv-export")) {
        python -m venv .venv-export
    }
    .\.venv-export\Scripts\Activate.ps1
    pip install -e ".[export,dev]"
    Write-Host "Export environment ready. Activate with: .\.venv-export\Scripts\Activate.ps1" -ForegroundColor Green

    # Switch back to runtime env
    .\.venv\Scripts\Activate.ps1
}

# Frontend setup
if (-not $SkipFrontend) {
    Write-Host ""
    Write-Host "── Setting up frontend ──" -ForegroundColor Yellow

    $nodeVersion = node --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "WARNING: Node.js not found. Frontend will not work." -ForegroundColor Yellow
        Write-Host "Install Node.js 18+ from https://nodejs.org" -ForegroundColor Yellow
    } else {
        Write-Host "Node.js: $nodeVersion" -ForegroundColor Green
        Push-Location app/frontend
        npm install
        Pop-Location
        Write-Host "Frontend dependencies installed" -ForegroundColor Green
    }
}

# Run probe
Write-Host ""
Write-Host "── Running device probe ──" -ForegroundColor Yellow
python scripts/probe_device.py

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Setup complete!" -ForegroundColor Cyan
Write-Host "  Run the app: .\scripts\run.bat" -ForegroundColor Cyan
Write-Host "  Run tests:   pytest" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
