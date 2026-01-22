# 📚 FantasmaWiFi-Pro Tutorials

Welcome to the FantasmaWiFi-Pro tutorial series! These guides will help you get started with common use cases.

## Table of Contents

1. [Quick Start: Share WiFi in 5 Minutes](#quick-start)
2. [USB Tethering for Mobile Devices](#usb-tethering)
3. [Bridge Mode for Network Extension](#bridge-mode)
4. [Configuration Profiles](#configuration-profiles)
5. [API Integration](#api-integration)
6. [Custom Platform Adapter](#custom-adapter)

---

## Quick Start: Share WiFi in 5 Minutes

**Goal**: Share your WiFi connection with mobile devices via hotspot

### Step 1: Install FantasmaWiFi-Pro

```bash
git clone https://github.com/Blackmvmba88/FantasmaWiFi-Pro.git
cd FantasmaWiFi-Pro
chmod +x fantasma_cli.py start_web_ui.sh
```

### Step 2: Check Available Interfaces

```bash
./fantasma_cli.py list
```

Output example:
```
Available network interfaces:
  ✓ en0 (wifi) - Active - 10.0.0.50
  ✓ en1 (wifi) - Inactive
  ✓ en4 (usb) - Inactive
```

### Step 3: Start Hotspot

```bash
./fantasma_cli.py start -s en0 -t en1 --ssid MyHotspot --password SecurePass123
```

**That's it!** Your mobile devices can now connect to "MyHotspot".

---

## USB Tethering for Mobile Devices

**Goal**: Share internet with your phone via USB cable

### Why USB?
- More stable than WiFi
- No battery drain from WiFi
- Better for gaming/video calls

### Step 1: Connect Phone via USB

Connect your phone to your computer with a USB cable.

### Step 2: Enable USB Tethering on Phone

**Android**: Settings → Network & Internet → Hotspot & tethering → USB tethering  
**iOS**: Settings → Personal Hotspot → Enable "Allow Others to Join"

### Step 3: Find USB Interface

```bash
./fantasma_cli.py list
```

Look for USB interfaces (e.g., `rndis0`, `usb0`, `en4`)

### Step 4: Start Sharing

```bash
./fantasma_cli.py start -s en0 -t usb0 --bridge
```

**Bridge mode** is recommended for USB to avoid double NAT.

---

## Bridge Mode for Network Extension

**Goal**: Extend your network transparently (no separate subnet)

### When to Use Bridge Mode

✅ You want devices to be on the same network  
✅ Avoiding double NAT  
✅ Enterprise/lab environments  
✅ VLANs need to work  

❌ Don't use if you need isolation between networks

### Example: Extend WiFi to Ethernet

```bash
# Share WiFi (en0) through Ethernet (en1)
./fantasma_cli.py start -s en0 -t en1 --bridge
```

### Network Flow

```
Original Network (192.168.1.0/24)
    ↓
Your Computer (en0) 
    ↓
Bridge (transparent)
    ↓
Ethernet Device (en1)
    ↓
Connected Devices (get IPs from 192.168.1.0/24)
```

Connected devices will:
- Get IPs from your original network's DHCP
- Access the same resources
- Appear on the same subnet

---

## Configuration Profiles

**Goal**: Save and reuse common configurations

### Via Web UI

1. Start Web UI:
   ```bash
   ./start_web_ui.sh
   ```

2. Open http://localhost:8080

3. Configure your sharing settings

4. Click "Save Profile" and give it a name

5. Later, load the profile from the dropdown

### Via API

```python
import requests

# Save a profile
profile = {
    "name": "home_usb",
    "config": {
        "source": "en0",
        "target": "usb0",
        "mode": "bridge"
    }
}

response = requests.post(
    "http://localhost:8080/api/profiles",
    json=profile,
    headers={"X-API-Key": "your_api_key"}
)
```

### Use Cases for Profiles

- **home_office**: Wired ethernet to WiFi hotspot for work
- **travel_usb**: USB tethering with mobile devices
- **gaming_lan**: Bridge mode for console gaming
- **iot_network**: Isolated hotspot for IoT devices

---

## API Integration

**Goal**: Control FantasmaWiFi-Pro programmatically

### Starting the API Server

```bash
./fantasma_web.py --host 0.0.0.0 --port 8080
```

### Getting an API Key

The default API key is printed when the server starts. To create additional keys:

```python
from fantasma_api import api_auth

# Create a new API key
key = api_auth.create_key("my_app")
print(f"Your API key: {key}")
```

### Basic Operations

#### 1. List Interfaces

```python
import requests

response = requests.get(
    "http://localhost:8080/api/interfaces",
    headers={"X-API-Key": "fwp_your_key_here"}
)

interfaces = response.json()["interfaces"]
for iface in interfaces:
    print(f"{iface['name']} - {iface['type']}")
```

#### 2. Start Sharing

```python
config = {
    "source": "en0",
    "target": "en1",
    "mode": "hotspot",
    "ssid": "MyAPI_Hotspot",
    "password": "SecurePassword123",
    "channel": 6
}

response = requests.post(
    "http://localhost:8080/api/start",
    json=config,
    headers={"X-API-Key": "fwp_your_key_here"}
)

if response.status_code == 200:
    print("Sharing started!")
```

#### 3. Check Status

```python
response = requests.get(
    "http://localhost:8080/api/status",
    headers={"X-API-Key": "fwp_your_key_here"}
)

status = response.json()
print(f"Active: {status['active']}")
print(f"Mode: {status['mode']}")
```

#### 4. Stop Sharing

```python
response = requests.post(
    "http://localhost:8080/api/stop",
    headers={"X-API-Key": "fwp_your_key_here"}
)
```

### Rate Limiting

The API is rate-limited to 60 requests per minute per API key. Check headers:

```python
limit = response.headers.get('X-RateLimit-Limit')
remaining = response.headers.get('X-RateLimit-Remaining')
print(f"Rate limit: {remaining}/{limit} requests remaining")
```

### Python Client Example

```python
class FantasmaClient:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.headers = {"X-API-Key": api_key}
    
    def get_interfaces(self):
        r = requests.get(f"{self.base_url}/api/interfaces", headers=self.headers)
        return r.json()["interfaces"]
    
    def start_hotspot(self, source, target, ssid, password):
        config = {
            "source": source,
            "target": target,
            "mode": "hotspot",
            "ssid": ssid,
            "password": password
        }
        r = requests.post(f"{self.base_url}/api/start", json=config, headers=self.headers)
        return r.json()
    
    def stop(self):
        r = requests.post(f"{self.base_url}/api/stop", headers=self.headers)
        return r.json()

# Usage
client = FantasmaClient("http://localhost:8080", "fwp_your_key")
interfaces = client.get_interfaces()
client.start_hotspot("en0", "en1", "MyHotspot", "password123")
```

---

## Custom Platform Adapter

**Goal**: Add support for a new platform (e.g., OpenWRT, Raspberry Pi)

### Step 1: Create Adapter Class

```python
# my_custom_adapter.py
from fantasma_core import PlatformAdapter, NetworkInterface, ConnectionType
from fantasma_plugins import register_adapter
import subprocess

@register_adapter('openwrt')
class OpenWRTAdapter(PlatformAdapter):
    """Custom adapter for OpenWRT routers"""
    
    def __init__(self):
        super().__init__()
        self.platform_name = "OpenWRT"
    
    def detect_interfaces(self):
        """Detect network interfaces on OpenWRT"""
        interfaces = []
        
        # Run 'ifconfig' or OpenWRT-specific command
        result = subprocess.run(
            ['ifconfig', '-a'],
            capture_output=True,
            text=True
        )
        
        # Parse output and create NetworkInterface objects
        for line in result.stdout.split('\n'):
            if line and not line.startswith(' '):
                iface_name = line.split()[0].rstrip(':')
                interfaces.append(
                    NetworkInterface(iface_name, ConnectionType.ETHERNET)
                )
        
        return interfaces
    
    def start_hotspot(self, config):
        """Start hotspot on OpenWRT"""
        # Configure wireless using UCI
        commands = [
            f"uci set wireless.@wifi-iface[0].ssid='{config.ssid}'",
            f"uci set wireless.@wifi-iface[0].key='{config.password}'",
            "uci commit wireless",
            "wifi reload"
        ]
        
        for cmd in commands:
            subprocess.run(cmd, shell=True, check=True)
        
        return True
    
    def start_bridge(self, config):
        """Start bridge mode on OpenWRT"""
        # Use OpenWRT bridge configuration
        subprocess.run([
            'brctl', 'addbr', 'br0',
            'brctl', 'addif', 'br0', config.source_interface,
            'brctl', 'addif', 'br0', config.target_interface
        ], check=True)
        return True
    
    def stop_sharing(self):
        """Stop sharing"""
        subprocess.run(['wifi', 'down'], check=True)
        return True
    
    def get_status(self):
        """Get current status"""
        return {
            'active': True,
            'platform': 'OpenWRT'
        }
```

### Step 2: Use Custom Adapter

```python
# main.py
from fantasma_core import FantasmaCore, FantasmaConfig
from fantasma_plugins import plugin_registry
from my_custom_adapter import OpenWRTAdapter

# Get the registered adapter
adapter_class = plugin_registry.get_adapter('openwrt')
adapter = adapter_class()

# Create Fantasma instance with custom adapter
fantasma = FantasmaCore(adapter)

# Use as normal
interfaces = fantasma.list_interfaces()
```

### Step 3: Register Hooks (Optional)

```python
from fantasma_plugins import on_hook

@on_hook('post_start')
def log_start(config):
    print(f"Sharing started: {config.source_interface} → {config.target_interface}")

@on_hook('on_error')
def handle_error(error):
    print(f"Error occurred: {error}")
    # Send notification, log to file, etc.
```

---

## Advanced Topics

### Multi-Interface Sharing

Share one source to multiple targets (future feature):

```python
config = FantasmaConfig(
    source_interface="en0",
    targets=["en1", "usb0", "bluetooth0"],
    mode=NetworkMode.HOTSPOT
)
```

### Bandwidth Monitoring

Monitor bandwidth usage (roadmap feature):

```python
stats = fantasma.get_bandwidth_stats()
print(f"Download: {stats['download_mbps']} Mbps")
print(f"Upload: {stats['upload_mbps']} Mbps")
```

### VPN Integration

Combine with VPN (manual setup):

```bash
# Start VPN first
openvpn --config my_vpn.ovpn

# Then share VPN connection
./fantasma_cli.py start -s tun0 -t wlan1 --ssid "Secure_VPN_Hotspot"
```

---

## Troubleshooting

### Common Issues

**"Interface not found"**
```bash
# Run list to see available interfaces
./fantasma_cli.py list
```

**"Permission denied"**
```bash
# Run with sudo (Linux/Mac) or as Administrator (Windows)
sudo ./fantasma_cli.py start ...
```

**"WiFi adapter doesn't support AP mode"**
- Try USB or Bluetooth instead
- Or use an external WiFi adapter that supports AP mode

### Getting Help

- Check documentation: [README.md](README.md), [ARCHITECTURE.md](ARCHITECTURE.md)
- GitHub Issues: https://github.com/Blackmvmba88/FantasmaWiFi-Pro/issues
- Enable verbose logging: `--verbose` flag

---

## Next Steps

- Explore the [Web UI Guide](WEB_UI_GUIDE.md)
- Read the [Architecture Guide](ARCHITECTURE.md)
- Check out [examples/](examples/) directory
- Join GitHub Discussions

**Happy sharing!** 🕸️
