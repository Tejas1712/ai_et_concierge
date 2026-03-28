@echo off
setlocal

set ROOT=%~dp0
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%run-project-no-popup.ps1"

if errorlevel 1 (
  echo.
  echo No-popup launcher failed. Check message above.
  pause
  exit /b 1
)

exit /b 0
