@echo off
setlocal

set ROOT=%~dp0
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%run-frontend.ps1"

if errorlevel 1 (
  echo.
  echo Frontend launcher failed. Check message above.
  pause
  exit /b 1
)

exit /b 0
