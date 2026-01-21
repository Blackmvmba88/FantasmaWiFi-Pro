@echo off
REM FantasmaWiFi-Pro - Windows Examples

echo === FantasmaWiFi-Pro Windows Examples ===
echo.

set PYTHON=python
set SCRIPT=..\fantasma_cli.py

echo 1. List available interfaces:
echo    %PYTHON% %SCRIPT% list
echo.

echo 2. Create WiFi hotspot from Ethernet:
echo    %PYTHON% %SCRIPT% start -s "Ethernet" -t "Wi-Fi" --ssid WindowsHotspot --password MyPassword123
echo.

echo 3. Share mobile broadband via WiFi:
echo    %PYTHON% %SCRIPT% start -s "Mobile Broadband" -t "Wi-Fi" --ssid MobileShare --password SecurePass123
echo.

echo 4. Stop sharing:
echo    %PYTHON% %SCRIPT% stop
echo.

echo 5. Check status:
echo    %PYTHON% %SCRIPT% status
echo.

echo Note: Run Command Prompt as Administrator
echo Note: Interface names may contain spaces, use quotes
