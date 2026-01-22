# ⚡ Quick Reference Guide

Fast reference for common FantasmaWiFi-Pro operations and configurations.

## Quick Commands

### CLI Quick Start
```bash
# List interfaces
./fantasma_cli.py list

# Start WiFi hotspot
./fantasma_cli.py start -s en0 -t wlan1 --ssid MyWiFi --password Pass1234

# Start bridge mode
./fantasma_cli.py start -s en0 -t en1 --bridge

# Stop sharing
./fantasma_cli.py stop

# Check status
./fantasma_cli.py status
```

### Web UI Quick Start
```bash
# Start web interface
./start_web_ui.sh

# Or manually
./fantasma_web.py --host 0.0.0.0 --port 8080

# Access at: http://localhost:8080
```

## Common Configurations

### 1. Share WiFi to Mobile via WiFi
```bash
./fantasma_cli.py start \
  -s en0 \           # WiFi interface (internet source)
  -t wlan1 \         # Second WiFi adapter (creates hotspot)
  --ssid "MyHotspot" \
  --password "SecurePass123"
```

### 2. Share WiFi to Phone via USB
```bash
./fantasma_cli.py start \
  -s en0 \           # WiFi interface (internet source)
  -t usb0 \          # USB tethering interface
  --bridge           # Bridge mode (no NAT)
```

### 3. Share Ethernet to WiFi
```bash
./fantasma_cli.py start \
  -s eth0 \          # Ethernet (internet source)
  -t wlan0 \         # WiFi adapter (creates hotspot)
  --ssid "Office_Guest" \
  --password "guest2024"
```

### 4. Extend WiFi Network (Bridge)
```bash
./fantasma_cli.py start \
  -s wlan0 \         # Main WiFi
  -t wlan1 \         # Second WiFi adapter
  --bridge           # Bridge mode (same network)
```

### 5. Share Mobile Data (Termux/Android)
```bash
./fantasma_cli.py start \
  -s rmnet_data0 \   # Mobile data interface
  -t wlan0 \         # WiFi adapter
  --ssid "MobileShare" \
  --password "mobile123"
```

## API Quick Reference

### Authentication
```bash
# Include API key in header
curl -H "X-API-Key: fwp_your_key_here" http://localhost:8080/api/status
```

### List Interfaces
```bash
curl -H "X-API-Key: your_key" \
  http://localhost:8080/api/interfaces
```

### Start Sharing
```bash
curl -X POST \
  -H "X-API-Key: your_key" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "en0",
    "target": "en1",
    "mode": "hotspot",
    "ssid": "MyAPI_Hotspot",
    "password": "SecurePass123"
  }' \
  http://localhost:8080/api/start
```

### Stop Sharing
```bash
curl -X POST \
  -H "X-API-Key: your_key" \
  http://localhost:8080/api/stop
```

### Check Status
```bash
curl -H "X-API-Key: your_key" \
  http://localhost:8080/api/status
```

## Python Quick Examples

### Basic Usage
```python
from fantasma_core import FantasmaCore, FantasmaConfig, get_platform_adapter

# Initialize
adapter = get_platform_adapter()
fantasma = FantasmaCore(adapter)

# List interfaces
interfaces = fantasma.list_interfaces()

# Start sharing
config = FantasmaConfig(
    source_interface="en0",
    target_interface="en1",
    mode="hotspot",
    ssid="MyHotspot",
    password="SecurePass123"
)
fantasma.start_sharing(config)

# Stop sharing
fantasma.stop_sharing()
```

### API Client
```python
import requests

base_url = "http://localhost:8080"
headers = {"X-API-Key": "your_api_key"}

# Start sharing
response = requests.post(
    f"{base_url}/api/start",
    json={
        "source": "en0",
        "target": "en1",
        "mode": "hotspot",
        "ssid": "MyHotspot",
        "password": "Pass123"
    },
    headers=headers
)
```

## Common Interface Names

### macOS
- `en0` - Built-in WiFi
- `en1` - Second WiFi adapter
- `en4`, `en5` - USB adapters
- `bridge0` - Bridge interface

### Linux
- `wlan0`, `wlan1` - WiFi adapters
- `eth0`, `eth1` - Ethernet
- `usb0` - USB tethering
- `br0` - Bridge interface

### Windows
- `Wi-Fi` - Built-in WiFi
- `Ethernet` - Wired connection
- `Local Area Connection` - Various adapters

### Android/Termux
- `wlan0` - WiFi
- `rmnet_data0` - Mobile data
- `rndis0` - USB tethering

## Troubleshooting Quick Fixes

### Interface not found
```bash
# List all interfaces
./fantasma_cli.py list

# Or check system tools
# macOS
networksetup -listallhardwareports

# Linux
ip link show

# Windows
ipconfig /all
```

### Permission denied
```bash
# Linux/Mac
sudo ./fantasma_cli.py start ...

# Windows
# Run PowerShell as Administrator
```

### Port already in use
```bash
# Find process using port 8080
lsof -i :8080  # Mac/Linux
netstat -ano | findstr :8080  # Windows

# Kill process
kill -9 <PID>  # Mac/Linux
taskkill /F /PID <PID>  # Windows
```

### WiFi adapter doesn't support AP mode
```bash
# Check WiFi capabilities (Linux)
iw list | grep "Supported interface modes" -A 10

# Solutions:
# 1. Use USB tethering instead
# 2. Get an external WiFi adapter that supports AP mode
# 3. Use bridge mode if available
```

## Configuration Presets

### Home Office
```json
{
  "source": "en0",
  "target": "en1",
  "mode": "hotspot",
  "ssid": "HomeOffice",
  "password": "WorkFromHome2024",
  "channel": 6
}
```

### Travel Router
```json
{
  "source": "wlan0",
  "target": "wlan1",
  "mode": "hotspot",
  "ssid": "TravelWiFi",
  "password": "SecureTravel123",
  "channel": 11
}
```

### Gaming Setup
```json
{
  "source": "eth0",
  "target": "en1",
  "mode": "bridge"
}
```

### IoT Network
```json
{
  "source": "en0",
  "target": "usb0",
  "mode": "hotspot",
  "ssid": "IoT_Network",
  "password": "IoTSecure2024",
  "ip_range": "192.168.100.0/24"
}
```

## Platform-Specific Notes

### macOS
- System Preferences may open automatically
- Bridge requires admin password
- Some operations need sudo

### Linux
- Install: `hostapd`, `dnsmasq`, `iptables`
- Most operations require root
- Check firewall rules

### Windows
- Run as Administrator
- May need manual ICS configuration
- Check "Network Connections" settings

### Termux/Android
- Install: `termux-api` (optional)
- Root recommended but not required
- L3 proxy used if bridge unavailable

## Environment Variables

```bash
# Set default interfaces
export FANTASMA_SOURCE_INTERFACE="en0"
export FANTASMA_TARGET_INTERFACE="en1"

# Set API configuration
export FANTASMA_API_KEY="your_key_here"
export FANTASMA_PORT="8080"
```

## Useful Scripts

### Auto-start on Boot (Linux)
```bash
# Add to /etc/rc.local
/path/to/fantasma_web.py --host 0.0.0.0 --port 8080 &
```

### Monitor Status
```bash
# Watch status continuously
watch -n 5 './fantasma_cli.py status'
```

### Log to File
```bash
# Redirect output
./fantasma_web.py 2>&1 | tee fantasma.log
```

## Performance Tips

1. **Use Bridge Mode** when possible (less overhead)
2. **Choose Good WiFi Channel** (1, 6, or 11 for 2.4GHz)
3. **Close Unnecessary Apps** (reduce CPU/memory usage)
4. **Update Drivers** (better performance and stability)
5. **Use Wired Connection** as source when possible

## Security Tips

1. **Strong Passwords** (min 8 chars, mix of types)
2. **Change Default API Key** after first use
3. **Use HTTPS** in production
4. **Enable Firewall** rules
5. **Monitor Connected Devices**

## Getting Help

- **Documentation**: [README.md](README.md), [TUTORIALS.md](TUTORIALS.md)
- **API Docs**: http://localhost:8080/api/docs
- **GitHub Issues**: Report bugs and request features
- **Discussions**: Ask questions and share tips

## Version Information

Check version:
```bash
./fantasma_cli.py --version
python -c "from _version import __version__; print(__version__)"
```

Current version: **7.5.0**

---

**Pro Tip**: Save commonly used commands as shell aliases:

```bash
# Add to ~/.bashrc or ~/.zshrc
alias fw-start='./fantasma_cli.py start -s en0 -t en1 --ssid MyWiFi --password Pass123'
alias fw-stop='./fantasma_cli.py stop'
alias fw-status='./fantasma_cli.py status'
alias fw-web='./fantasma_web.py'
```
