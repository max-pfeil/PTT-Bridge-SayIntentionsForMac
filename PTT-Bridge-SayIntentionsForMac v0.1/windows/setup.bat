@echo off
:: One-time dependency setup (Windows VM side).
:: Double-click to run.

where python >nul 2>&1
if errorlevel 1 (
    echo Python not found.
    echo Install the 64-bit Python from https://www.python.org/downloads/windows/
    echo ^(use the "Windows installer (64-bit)" option, not ARM64^), then re-run this setup.
    pause
    exit /b 1
)

echo Installing vgamepad...
pip install vgamepad

echo.
echo Checking for the ViGEmBus driver...
powershell -NoProfile -Command "if (Get-PnpDevice -FriendlyName '*Virtual Gamepad Emulation Bus*' -ErrorAction SilentlyContinue) { Write-Host 'Found: ViGEmBus driver is installed.' } else { Write-Host 'NOT FOUND: ViGEmBus driver is missing.'; Write-Host 'Download and install it from:'; Write-Host '  https://github.com/nefarius/ViGEmBus/releases'; Write-Host '(pick the installer with arm64 in the filename, then reboot the VM)' }"

echo.
echo Setup complete.
echo Next: double-click start_ptt_receiver.bat to begin.
pause
