@echo off
setlocal
cd /d "%~dp0"
echo.
echo Vera Blender Relay V1 installer
echo This will register a private repository-scoped GitHub runner for this Windows user.
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Install-VeraBlenderRunner.ps1"
set "RC=%ERRORLEVEL%"
echo.
if not "%RC%"=="0" (
  echo Installation failed with exit code %RC%.
) else (
  echo Installation completed.
)
echo.
pause
exit /b %RC%
