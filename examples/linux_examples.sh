#!/bin/bash
# FantasmaWiFi-Pro - Linux Examples

echo "=== FantasmaWiFi-Pro Linux Examples ==="
echo ""

PYTHON=$(which python3)
SCRIPT="../fantasma_cli.py"

echo "1. List available interfaces:"
echo "   $PYTHON $SCRIPT list"
echo ""

echo "2. Share Ethernet via WiFi hotspot:"
echo "   sudo $PYTHON $SCRIPT start -s eth0 -t wlan0 --ssid LinuxAP --password SecurePass123"
echo ""

echo "3. Share mobile data via WiFi hotspot:"
echo "   sudo $PYTHON $SCRIPT start -s ppp0 -t wlan0 --ssid MobileAP --password SecurePass123"
echo ""

echo "4. Bridge WiFi and Ethernet (Layer 2 extension):"
echo "   sudo $PYTHON $SCRIPT start -s wlan0 -t eth0 --bridge"
echo ""

echo "5. Share USB tethering:"
echo "   sudo $PYTHON $SCRIPT start -s usb0 -t wlan0 --ssid USBShare --password MyPassword123"
echo ""

echo "6. Stop sharing:"
echo "   sudo $PYTHON $SCRIPT stop"
echo ""

echo "7. Check status:"
echo "   $PYTHON $SCRIPT status"
echo ""

echo "Note: Most operations require root privileges (sudo)"
echo ""
echo "Prerequisites:"
echo "  sudo apt-get install hostapd dnsmasq iptables bridge-utils"
