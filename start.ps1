# NEURYX - One-Click Launcher

Write-Host ""
Write-Host "  NEURYX - Local Neural Speech Engine" -ForegroundColor Magenta
Write-Host ""

$projectRoot = $PSScriptRoot
$pythonExe = Join-Path $projectRoot "venv\Scripts\python.exe"

# Check venv exists
if (-not (Test-Path $pythonExe)) {
    Write-Host "  [ERROR] Python venv not found." -ForegroundColor Red
    Write-Host "  Create it first: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

# Start Backend in a new terminal window
Write-Host "  [..] Starting Backend (port 8000)..." -ForegroundColor Cyan
$backendCmd = "Set-Location '$projectRoot'; & '$pythonExe' -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendCmd

Start-Sleep -Seconds 3

# Start Frontend in a new terminal window
Write-Host "  [..] Starting Frontend (port 5173)..." -ForegroundColor Cyan
$frontendCmd = "Set-Location '$projectRoot\frontend'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendCmd

Start-Sleep -Seconds 5

# Open browser
Write-Host "  [OK] Opening browser..." -ForegroundColor Green
Start-Process "http://localhost:5173"

Write-Host ""
Write-Host "  Neuryx is running!" -ForegroundColor Green
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor DarkGray
Write-Host "  Backend:  http://localhost:8000" -ForegroundColor DarkGray
Write-Host ""
