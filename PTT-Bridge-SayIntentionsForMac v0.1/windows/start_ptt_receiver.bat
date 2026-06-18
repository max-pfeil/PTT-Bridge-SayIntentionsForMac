@echo off
:: Starts the PTT receiver (Windows VM side).
:: Double-click to run. Requires Administrator rights for the
:: virtual gamepad, so this relaunches itself elevated if needed.

net session >nul 2>&1
if %errorLevel% == 0 goto run

echo Requesting administrator rights...
powershell -Command "Start-Process -FilePath '%~f0' -Verb RunAs"
exit /b

:run
cd /d "%~dp0scripts"
python ptt_receiver_win.py
pause
