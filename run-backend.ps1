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
$backendVenvDir = Join-Path $backendDir "venv"
$backendPython = Join-Path $backendVenvDir "Scripts\python.exe"
$backendEnv = Join-Path $backendDir ".env"
$backendEnvExample = Join-Path $backendDir ".env.example"

Write-Host "=== ET AI Concierge Backend: Setup + Run ===" -ForegroundColor Cyan

Require-Command -Name "python"

if (-not (Test-Path $backendVenvDir)) {
    Write-Host "[1/3] Creating backend virtual environment..." -ForegroundColor Yellow
    python -m venv $backendVenvDir
}

if (-not (Test-Path $backendPython)) {
    throw "Backend Python executable not found at $backendPython"
}

Write-Host "[2/3] Installing backend dependencies..." -ForegroundColor Yellow
& $backendPython -m pip install -r (Join-Path $backendDir "requirements.txt")

if (-not (Test-Path $backendEnv) -and (Test-Path $backendEnvExample)) {
    Write-Host "[3/3] Creating backend .env from template..." -ForegroundColor Yellow
    Copy-Item $backendEnvExample $backendEnv
}

if ($SetupOnly) {
    Write-Host "Setup complete only (backend not started)." -ForegroundColor Green
    return
}

Write-Host "Starting backend in this terminal (Ctrl+C to stop)..." -ForegroundColor Green
Push-Location $backendDir
try {
    & $backendPython main.py
} finally {
    Pop-Location
}
