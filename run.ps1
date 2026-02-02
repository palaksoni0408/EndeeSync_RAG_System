# ==============================================================================
# EndeeSync RAG System - Windows PowerShell Startup Script
# ==============================================================================
# This script automates the setup and startup process for Windows users
# ==============================================================================

Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  EndeeSync RAG System - Startup Script (Windows)" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "[1/7] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Python not found! Please install Python 3.8+ from python.org" -ForegroundColor Red
    exit 1
}

# Check if virtual environment exists
Write-Host ""
Write-Host "[2/7] Checking virtual environment..." -ForegroundColor Yellow
if (-Not (Test-Path "venv")) {
    Write-Host "  Creating virtual environment..." -ForegroundColor Cyan
    python -m venv venv
    Write-Host "  ✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "  ✓ Virtual environment exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host ""
Write-Host "[3/7] Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1
Write-Host "  ✓ Virtual environment activated" -ForegroundColor Green

# Install/Update dependencies
Write-Host ""
Write-Host "[4/7] Installing/Updating dependencies..." -ForegroundColor Yellow
if (-Not (Test-Path "venv\.dependencies_installed")) {
    Write-Host "  Installing packages from requirements.txt..." -ForegroundColor Cyan
    pip install --upgrade pip | Out-Null
    pip install -r requirements.txt
    New-Item -Path "venv\.dependencies_installed" -ItemType File | Out-Null
    Write-Host "  ✓ Dependencies installed" -ForegroundColor Green
} else {
    Write-Host "  ✓ Dependencies already installed (delete venv\.dependencies_installed to reinstall)" -ForegroundColor Green
}

# Check .env file
Write-Host ""
Write-Host "[5/7] Checking environment configuration..." -ForegroundColor Yellow
if (-Not (Test-Path ".env")) {
    Write-Host "  ⚠ WARNING: .env file not found!" -ForegroundColor Yellow
    Write-Host "  Creating .env from .env.example..." -ForegroundColor Cyan
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "  ✓ Created .env file - PLEASE EDIT IT WITH YOUR API KEYS!" -ForegroundColor Yellow
    } else {
        Write-Host "  ✗ .env.example not found. Please create .env manually." -ForegroundColor Red
    }
} else {
    Write-Host "  ✓ .env file found" -ForegroundColor Green
}

# Check Endee server connection
Write-Host ""
Write-Host "[6/7] Checking Endee server connection..." -ForegroundColor Yellow
try {
    $endeeUrl = "http://localhost:8080"
    $response = Invoke-WebRequest -Uri $endeeUrl -Method GET -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ✓ Endee server is running at $endeeUrl" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Cannot connect to Endee server at http://localhost:8080" -ForegroundColor Red
    Write-Host "  Please start Endee server using Docker:" -ForegroundColor Yellow
    Write-Host "    docker-compose up -d endee" -ForegroundColor Cyan
    Write-Host ""
    $continue = Read-Host "Continue anyway? (y/n)"
    if ($continue -ne "y") {
        exit 1
    }
}

# Check if documents are ingested
Write-Host ""
Write-Host "[7/7] Checking ingested documents..." -ForegroundColor Yellow
try {
    python -c "from src.store import initialize_endee_index; idx = initialize_endee_index(); print('OK')" 2>&1 | Out-Null
    Write-Host "  ✓ Vector index is ready" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Vector index may need initialization" -ForegroundColor Yellow
    Write-Host "  You can ingest documents later using:" -ForegroundColor Cyan
    Write-Host "    python app.py --ingest" -ForegroundColor Cyan
}

# Start the server
Write-Host ""
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host "  Starting EndeeSync Web Server" -ForegroundColor Cyan
Write-Host "================================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Dashboard will be available at: http://localhost:8000/dashboard" -ForegroundColor Green
Write-Host "  API documentation at:           http://localhost:8000/docs" -ForegroundColor Green
Write-Host ""
Write-Host "  Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start uvicorn
try {
    uvicorn api:app --host 0.0.0.0 --port 8000 --reload
} catch {
    Write-Host ""
    Write-Host "Server stopped." -ForegroundColor Yellow
}
