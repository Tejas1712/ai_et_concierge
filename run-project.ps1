param(
    [switch]$SetupOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Require-Command {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Name
    )

    if (-not (Get-Command $Name -ErrorAction SilentlyContinue)) {
        throw "Required command '$Name' was not found in PATH. Please install it and retry."
    }
}

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = Join-Path $root "backend"
$frontendDir = Join-Path $root "frontend"
$backendVenvDir = Join-Path $backendDir "venv"
$backendPython = Join-Path $backendVenvDir "Scripts\python.exe"
$backendEnv = Join-Path $backendDir ".env"
$backendEnvExample = Join-Path $backendDir ".env.example"
$frontendEnv = Join-Path $frontendDir ".env"
$frontendEnvExample = Join-Path $frontendDir ".env.example"

Write-Host "=== ET AI Concierge: No-Popup Setup + Run ===" -ForegroundColor Cyan

Require-Command -Name "python"
Require-Command -Name "npm"

if (-not (Test-Path $backendVenvDir)) {
    Write-Host "[1/6] Creating backend virtual environment..." -ForegroundColor Yellow
    python -m venv $backendVenvDir
}

if (-not (Test-Path $backendPython)) {
    throw "Backend Python executable not found at $backendPython"
}

Write-Host "[2/6] Installing backend dependencies..." -ForegroundColor Yellow
& $backendPython -m pip install -r (Join-Path $backendDir "requirements.txt")

if (-not (Test-Path $backendEnv) -and (Test-Path $backendEnvExample)) {
    Write-Host "[3/6] Creating backend .env from template..." -ForegroundColor Yellow
    Copy-Item $backendEnvExample $backendEnv
}

Write-Host "[4/6] Installing frontend dependencies..." -ForegroundColor Yellow
Push-Location $frontendDir
try {
    npm install
} finally {
    Pop-Location
}

if (-not (Test-Path $frontendEnv) -and (Test-Path $frontendEnvExample)) {
    Write-Host "[5/6] Creating frontend .env from template..." -ForegroundColor Yellow
    Copy-Item $frontendEnvExample $frontendEnv
}

if ($SetupOnly) {
    Write-Host "[6/6] Setup complete only (no services started)." -ForegroundColor Green
    return
}

Write-Host "[6/6] Starting backend and frontend in background jobs (no external popup windows)..." -ForegroundColor Yellow

$backendJob = Start-Job -Name "et-backend" -ScriptBlock {
    param($dir, $pythonPath)
    Set-Location $dir
    & $pythonPath main.py
} -ArgumentList $backendDir, $backendPython

$frontendJob = Start-Job -Name "et-frontend" -ScriptBlock {
    param($dir)
    Set-Location $dir
    npm run dev
} -ArgumentList $frontendDir

Write-Host ""
Write-Host "Jobs started in this PowerShell session:" -ForegroundColor Green
Write-Host "- et-backend (Job Id: $($backendJob.Id))"
Write-Host "- et-frontend (Job Id: $($frontendJob.Id))"
Write-Host ""
Write-Host "URLs:" -ForegroundColor Green
Write-Host "- Frontend: http://localhost:3000"
Write-Host "- Backend:  http://127.0.0.1:8000"
Write-Host ""
Write-Host "Useful commands in the same terminal:" -ForegroundColor Magenta
Write-Host "- Get-Job"
Write-Host "- Receive-Job -Name et-backend -Keep"
Write-Host "- Receive-Job -Name et-frontend -Keep"
Write-Host "- Stop-Job -Name et-backend,et-frontend"
Write-Host "- Remove-Job -Name et-backend,et-frontend"
