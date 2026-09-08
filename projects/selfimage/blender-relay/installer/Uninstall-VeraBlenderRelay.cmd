@echo off
setlocal
cd /d "%~dp0"
echo.
echo Vera Blender Relay V1 uninstaller
echo.
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0Uninstall-VeraBlenderRunner.ps1"
set "RC=%ERRORLEVEL%"
echo.
if not "%RC%"=="0" (
  echo Uninstall/disable finished with exit code %RC%.
) else (
  echo Local relay startup disabled/uninstalled.
)
echo.
pause
exit /b %RC%
