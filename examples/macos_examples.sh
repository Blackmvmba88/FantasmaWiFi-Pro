#!/bin/bash
# FantasmaWiFi-Pro - macOS Examples

echo "=== FantasmaWiFi-Pro macOS Examples ==="
echo ""

# Get Python path
PYTHON=$(which python3)
SCRIPT="../fantasma_cli.py"

echo "1. List available interfaces:"
echo "   $PYTHON $SCRIPT list"
echo ""

echo "2. Share WiFi (en0) to iPhone via USB (en5):"
echo "   $PYTHON $SCRIPT start -s en0 -t en5"
echo ""

echo "3. Create WiFi hotspot from Ethernet:"
echo "   $PYTHON $SCRIPT start -s en1 -t en0 --ssid MacHotspot --password MyPassword123"
echo ""

echo "4. Bridge two Ethernet interfaces (Layer 2):"
echo "   $PYTHON $SCRIPT start -s en0 -t en1 --bridge"
echo ""

echo "5. Share to Bluetooth PAN:"
echo "   $PYTHON $SCRIPT start -s en0 -t bridge0"
echo ""

echo "6. Stop sharing:"
echo "   $PYTHON $SCRIPT stop"
echo ""

echo "7. Check status:"
echo "   $PYTHON $SCRIPT status"
echo ""

echo "Note: Some operations require sudo privileges"
