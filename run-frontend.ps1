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
$frontendDir = Join-Path $root "frontend"
$frontendEnv = Join-Path $frontendDir ".env"
$frontendEnvExample = Join-Path $frontendDir ".env.example"

Write-Host "=== ET AI Concierge Frontend: Setup + Run ===" -ForegroundColor Cyan

Require-Command -Name "npm"

Write-Host "[1/2] Installing frontend dependencies..." -ForegroundColor Yellow
Push-Location $frontendDir
try {
    npm install
} finally {
    Pop-Location
}

if (-not (Test-Path $frontendEnv) -and (Test-Path $frontendEnvExample)) {
    Write-Host "[2/2] Creating frontend .env from template..." -ForegroundColor Yellow
    Copy-Item $frontendEnvExample $frontendEnv
}

if ($SetupOnly) {
    Write-Host "Setup complete only (frontend not started)." -ForegroundColor Green
    return
}

Write-Host "Starting frontend in this terminal (Ctrl+C to stop)..." -ForegroundColor Green
Push-Location $frontendDir
try {
    npm run dev
} finally {
    Pop-Location
}
