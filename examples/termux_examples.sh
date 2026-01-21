#!/data/data/com.termux/files/usr/bin/bash
# FantasmaWiFi-Pro - Termux/Android Examples

echo "=== FantasmaWiFi-Pro Termux/Android Examples ==="
echo ""

PYTHON=$(which python3)
SCRIPT="../fantasma_cli.py"

echo "1. List available interfaces:"
echo "   $PYTHON $SCRIPT list"
echo ""

echo "2. Bridge WiFi to USB (with root):"
echo "   $PYTHON $SCRIPT start -s wlan0 -t rndis0 --bridge"
echo ""

echo "3. L3 Proxy mode (no bridge support):"
echo "   $PYTHON $SCRIPT start -s wlan0 -t rndis0 --bridge"
echo "   (Automatically uses L3 proxy if L2 bridge not supported)"
echo ""

echo "4. Stop sharing:"
echo "   $PYTHON $SCRIPT stop"
echo ""

echo "5. Check status:"
echo "   $PYTHON $SCRIPT status"
echo ""

echo "Note: Most operations require root access"
echo ""
echo "Prerequisites:"
echo "  pkg install python root-repo"
echo "  pkg install termux-api (optional)"
echo ""
echo "Root access:"
echo "  Install Magisk or similar root solution"
echo "  Grant Termux root access"
