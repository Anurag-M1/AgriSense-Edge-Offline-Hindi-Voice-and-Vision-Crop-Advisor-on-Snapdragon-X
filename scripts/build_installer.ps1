# AgriSense Edge — Build Installer Script
# Creates a standalone distribution using PyInstaller

param(
    [string]$OutputDir = "dist\agrisense-edge"
)

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  AgriSense Edge — Build Installer" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Ensure we're in the repo root
if (-not (Test-Path "pyproject.toml")) {
    Write-Host "ERROR: Run this script from the repo root" -ForegroundColor Red
    exit 1
}

# Activate venv
.\.venv\Scripts\Activate.ps1

# Install PyInstaller if not present
pip install pyinstaller

# Build frontend
Write-Host ""
Write-Host "── Building frontend ──" -ForegroundColor Yellow
Push-Location app/frontend
npm run build
Pop-Location

# Create output directory
if (Test-Path $OutputDir) {
    Remove-Item -Recurse -Force $OutputDir
}
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null

# Copy necessary files
Write-Host ""
Write-Host "── Copying application files ──" -ForegroundColor Yellow

# Copy backend
Copy-Item -Recurse app/backend $OutputDir/backend
# Copy frontend build
Copy-Item -Recurse app/frontend/dist $OutputDir/frontend
# Copy models manifest
Copy-Item -Recurse models $OutputDir/models
# Copy knowledge base
Copy-Item -Recurse kb $OutputDir/kb

# Create run script for the distribution
@"
@echo off
echo Starting AgriSense Edge...
cd /d %~dp0
python -m backend.main
"@ | Out-File -FilePath "$OutputDir/run.bat" -Encoding ascii

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  Build complete!" -ForegroundColor Cyan
Write-Host "  Output: $OutputDir" -ForegroundColor Cyan
Write-Host "  Run:    $OutputDir\run.bat" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
