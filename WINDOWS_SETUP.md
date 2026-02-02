# Windows Setup Guide - Using run.ps1

This guide shows you how to run EndeeSync on Windows using the `run.ps1` PowerShell script.

## Prerequisites

1. **Python 3.8+** installed from [python.org](https://www.python.org/downloads/)
2. **Endee Server** running (see below)
3. **PowerShell** (comes with Windows)

## Quick Start

### Step 1: Start Endee Server (One-time setup)

**Option A: Using Docker (Recommended)**
```powershell
# Install Docker Desktop for Windows first
# Then run:
docker-compose up -d endee
```

**Option B: Using Docker without docker-compose**
```powershell
docker run -d `
  --name endee-server `
  -p 8080:8080 `
  -v endee-data:/data `
  endeeio/endee-server:latest
```

### Step 2: Run the PowerShell Script

1. **Open PowerShell** in the project folder
   - Right-click the folder → "Open in Terminal" or "Open PowerShell window here"

2. **Enable script execution** (first time only):
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
   ```

3. **Run the script**:
   ```powershell
   .\run.ps1
   ```

### Step 3: Open Dashboard

The script will automatically start the server. Open your browser to:
- **Dashboard**: http://localhost:8000/dashboard

## What the Script Does

The `run.ps1` script automatically:
- ✅ Checks if Python is installed
- ✅ Creates a virtual environment (if needed)
- ✅ Installs dependencies from `requirements.txt`
- ✅ Checks Endee server connection
- ✅ Verifies the database is ready
- ✅ Starts the web server on port 8000

## Script Output Example

```
================================================================================
  EndeeSync RAG System - Startup Script (Windows)
================================================================================

[1/7] Checking Python installation...
  ✓ Found: Python 3.11.0

[2/7] Checking virtual environment...
  ✓ Virtual environment exists

[3/7] Activating virtual environment...
  ✓ Virtual environment activated

[4/7] Installing/Updating dependencies...
  ✓ Dependencies already installed

[5/7] Checking environment configuration...
  ✓ .env file found

[6/7] Checking Endee server connection...
  ✓ Endee server is running at http://localhost:8080

[7/7] Checking ingested documents...
  ✓ Vector index is ready

================================================================================
  Starting EndeeSync Web Server
================================================================================

  Dashboard will be available at: http://localhost:8000/dashboard
  API documentation at:           http://localhost:8000/docs

  Press Ctrl+C to stop the server

INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

## Troubleshooting

### "Script cannot be loaded because running scripts is disabled"
**Solution**: Enable script execution
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### "Python not found"
**Solution**: Install Python from [python.org](https://www.python.org/downloads/) and make sure "Add Python to PATH" is checked during installation.

### "Cannot connect to Endee server"
**Solution**: Start the Endee server first:
```powershell
docker-compose up -d endee
# OR
docker run -d --name endee-server -p 8080:8080 endeeio/endee-server:latest
```

### Port 8000 already in use
**Solution**: Stop other applications using port 8000, or modify the script to use a different port:
- Open `run.ps1` in a text editor
- Change line: `uvicorn api:app --host 0.0.0.0 --port 8000 --reload`
- To: `uvicorn api:app --host 0.0.0.0 --port 8001 --reload`

## Stopping the Server

Press **Ctrl+C** in the PowerShell window where the script is running.

## Alternative: Using Docker Compose (Easier!)

If you prefer not to deal with Python environments, use Docker Compose instead:

```powershell
# Start everything (backend + database)
docker-compose up --build -d

# Open dashboard
start http://localhost:8000/dashboard

# View logs
docker-compose logs -f

# Stop everything
docker-compose down
```

This method doesn't need Python installed and is more reliable!

## Need Help?

- Check the main [README.md](README.md) for detailed documentation
- Review the [.env.example](.env.example) for configuration options
- Make sure Docker Desktop is running if using Endee via Docker
