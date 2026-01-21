# 🕸️ FantasmaWiFi-Pro v7.0

> **"Interface A consumes internet, Interface B distributes internet"**  
> *The rest is theater.*

**FantasmaWiFi-Pro** is a multi-platform network sharing tool that transforms your computer into a powerful WiFi hotspot or network bridge. Designed for situations where WiFi is weak for mobile devices but your computer can still connect.

---

## 🚀 Features

### Multi-Platform Support
- ✅ **macOS** - Native Internet Sharing + bridge support
- ✅ **Linux** - Full hostapd + dnsmasq + iptables/nftables
- ✅ **Windows** - Hosted Network + ICS
- ✅ **Termux/Android** - Tethering + iptables (with L3 proxy fallback)

### Dual Operation Modes

#### 1. Hotspot Mode (NAT/Router)
The machine becomes a router:
- Creates its own network
- Provides DHCP (IP assignment)
- Performs NAT (Network Address Translation)
- Stateful firewall forwarding

**Perfect for:**
- Mobile devices
- Gaming consoles
- IoT devices
- Public spaces

#### 2. Bridge Mode (Layer 2 Forwarding)
The machine becomes a transparent switch:
- Extends existing network
- No separate network creation
- No NAT overhead
- Direct MAC-to-MAC forwarding

**Perfect for:**
- Extending existing networks
- Maintaining VLANs
- Avoiding double NAT
- Industrial/Enterprise environments
- Network labs

---

## 📦 Architecture

```
   [Core Fantasma]
         |
 ┌───────┴───────┐
 | Platform      |
 | Adapter       |
 └───────┬───────┘
   mac  linux  win  termux
         |
    [Driver Layer]
```

- **Core**: Platform-independent logic
- **Adapter**: OS-specific command translation
- **Drivers**: System tool invocation

---

## 🔧 Installation

### Requirements
- Python 3.7+
- Platform-specific tools (installed automatically on first run)

### Quick Install

```bash
# Clone the repository
git clone https://github.com/Blackmvmba88/FantasmaWiFi-Pro.git
cd FantasmaWiFi-Pro

# Make CLI executable
chmod +x fantasma_cli.py

# Run
./fantasma_cli.py list
```

### Platform-Specific Requirements

#### macOS
```bash
# No additional requirements - uses built-in tools:
# - networksetup
# - pfctl
# - ifconfig
```

#### Linux
```bash
# Install required tools
sudo apt-get install hostapd dnsmasq iptables bridge-utils

# Or on Fedora/RHEL
sudo dnf install hostapd dnsmasq iptables bridge-utils
```

#### Windows
```bash
# Run as Administrator
# Uses built-in tools:
# - netsh
# - ICS (Internet Connection Sharing)
```

#### Termux (Android)
```bash
# Install in Termux
pkg install python root-repo
pkg install termux-api (optional)

# Root access recommended for full functionality
```

---

## 📖 Usage

### List Available Interfaces

```bash
./fantasma_cli.py list
```

Output:
```
═══ Detecting Network Interfaces ═══

1. en0
   Type: WIFI
   Status: UP
   MAC: aa:bb:cc:dd:ee:ff

2. en5
   Type: USB
   Status: DOWN
```

### Start Hotspot Mode

#### WiFi Hotspot
```bash
./fantasma_cli.py start \
  --source en0 \
  --target wlan1 \
  --ssid MyFantasmaWiFi \
  --password SecurePass123
```

#### USB Sharing (iPhone/Android)
```bash
./fantasma_cli.py start \
  --source en0 \
  --target en5
```

#### Bluetooth Sharing
```bash
./fantasma_cli.py start \
  --source en0 \
  --target bluetooth-pan
```

### Start Bridge Mode

```bash
./fantasma_cli.py start \
  --source en0 \
  --target en1 \
  --bridge
```

### Stop Sharing

```bash
./fantasma_cli.py stop
```

### Check Status

```bash
./fantasma_cli.py status
```

---

## 🎯 Platform-Specific Examples

### macOS
```bash
# Share WiFi (en0) to iPhone via USB (en5)
./fantasma_cli.py start -s en0 -t en5

# Create WiFi hotspot from Ethernet
./fantasma_cli.py start -s en1 -t en0 \
  --ssid MacHotspot --password MyPassword123

# Bridge two Ethernet interfaces
./fantasma_cli.py start -s en0 -t en1 --bridge
```

### Linux (Ubuntu/Debian)
```bash
# Share wired connection via WiFi hotspot
sudo ./fantasma_cli.py start \
  -s eth0 -t wlan0 \
  --ssid LinuxAP --password SecurePass123

# Bridge WiFi and Ethernet (transparent extension)
sudo ./fantasma_cli.py start -s wlan0 -t eth0 --bridge
```

### Windows (Run as Administrator)
```bash
# Create WiFi hotspot
fantasma_cli.py start ^
  -s "Ethernet" -t "Wi-Fi" ^
  --ssid WindowsHotspot --password MyPassword123
```

### Termux (Android)
```bash
# L3 proxy mode (works without bridge support)
./fantasma_cli.py start -s wlan0 -t rndis0 --bridge

# Note: May require root for full functionality
```

---

## 🛠️ Advanced Configuration

### Custom IP Range (Hotspot Mode)

Edit `fantasma_core.py`:
```python
config = FantasmaConfig(
    mode=NetworkMode.HOTSPOT,
    source_interface=source,
    target_interface=target,
    ip_range="192.168.100.0/24",
    dhcp_start="192.168.100.100",
    dhcp_end="192.168.100.200"
)
```

### Verbose Logging

```bash
./fantasma_cli.py start -s en0 -t en1 --verbose
```

---

## 🔐 Security Notes

- **Hotspot Mode**: Always use strong passwords (8+ characters)
- **Bridge Mode**: Exposes devices to source network - ensure trust
- **Permissions**: Some operations require root/administrator privileges
- **Firewall**: Adapters configure firewalls automatically but review rules

---

## 🐛 Troubleshooting

### macOS: "Operation not permitted"
```bash
# Grant Full Disk Access to Terminal in System Preferences
# Or run with sudo:
sudo ./fantasma_cli.py start -s en0 -t en1
```

### Linux: "hostapd failed"
```bash
# Check if WiFi adapter supports AP mode
iw list | grep "Supported interface modes" -A 8

# Stop NetworkManager from interfering
sudo systemctl stop NetworkManager
```

### Windows: "Hosted network couldn't be started"
```bash
# Check if adapter supports hosted network
netsh wlan show drivers

# Look for "Hosted network supported: Yes"
```

### Android: "Bridge not supported"
```
# Normal - most Android kernels don't support L2 bridging
# FantasmaWiFi automatically falls back to L3 proxy mode
# This works just as well for most use cases
```

---

## 📚 Technical Details

### Abstraction Model
All four platforms share one abstraction:
> "Interface A consumes internet, Interface B distributes internet"

### Hotspot vs Bridge - Technical Comparison

| Feature | Hotspot (NAT) | Bridge (L2) |
|---------|---------------|-------------|
| Network Layer | Layer 3 (IP) | Layer 2 (MAC) |
| IP Assignment | Creates new subnet | Uses existing subnet |
| NAT Required | Yes | No |
| DHCP Server | Required | Optional (passthrough) |
| VLAN Support | No | Yes |
| Double NAT | Creates double NAT | Avoids double NAT |
| Use Case | Mobile/IoT sharing | Network extension |

### Platform Implementation Details

**macOS**:
- Hotspot: `defaults` + `launchctl` + System Preferences
- Bridge: `ifconfig bridge0` native support

**Linux** (The Paradise 🐧):
- Hotspot: `hostapd` + `dnsmasq` + `iptables`
- Bridge: `brctl` or `ip link` + bridge module

**Windows**:
- Hotspot: `netsh wlan set hostednetwork` + ICS
- Bridge: Network Connections GUI + manual setup

**Termux/Android**:
- Hotspot: `svc wifi` + manual settings + `iptables`
- Bridge: L3 proxy mode (elegant workaround for kernel limitations)

---

## 🗺️ Roadmap

### Phase 1: Core Architecture ✅ (Current)
- [x] Multi-platform adapter system
- [x] Hotspot and Bridge modes
- [x] CLI interface
- [x] All four platforms supported

### Phase 2: Enhancement (Q1 2026)
- [ ] Web UI (local control panel at 192.168.x.x)
- [ ] Configuration profiles
- [ ] Auto-detection and one-click setup
- [ ] Bandwidth monitoring
- [ ] Connected devices list

### Phase 3: Advanced Features (Q2 2026)
- [ ] VPN integration
- [ ] Advanced firewall rules
- [ ] QoS (Quality of Service)
- [ ] Multi-target support (share to multiple interfaces)
- [ ] Mobile app for Termux control

### Phase 4: Commercialization (Q3 2026)
- [ ] Premium features
- [ ] Enterprise version
- [ ] Cloud management portal
- [ ] White-label licensing

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
```bash
# Clone and create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Run tests (coming soon)
python -m pytest
```

---

## 📄 License

This project is licensed under the Sovereignty License - see [LICENSE_SOVEREIGNTY.md](LICENSE_SOVEREIGNTY.md) for details.

**Developed with ❤️ for the ecosystem of Iyari Cancino Gomez**

---

## 🎓 Philosophy

This tool is not just a network script; it's a declaration of **Digital Sovereignty**. 

In a world where connectivity is control, having the ability to:
- Share internet on your terms
- Extend networks without corporate restrictions  
- Run your own infrastructure

...is a form of freedom.

**Don't accept WiFi dead zones. Create your own infrastructure.**

---

## 💬 Support

- **Issues**: [GitHub Issues](https://github.com/Blackmvmba88/FantasmaWiFi-Pro/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Blackmvmba88/FantasmaWiFi-Pro/discussions)

---

*Version 7.0 "Multi-Platform Edition" - The architecture that aged well in the universe* 🌌
