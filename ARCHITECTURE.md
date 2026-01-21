# FantasmaWiFi-Pro Architecture

## Overview

FantasmaWiFi-Pro is built on a clean abstraction model that enables the same core logic to work across macOS, Linux, Windows, and Android/Termux.

## Core Abstraction

The entire system is built on one fundamental abstraction:

> **"Interface A consumes internet, Interface B distributes internet"**

Everything else is platform-specific implementation detail ("theater" as we call it).

## Architecture Layers

```
┌─────────────────────────────────────────┐
│         CLI / Future UI Layer           │
│         (fantasma_cli.py)               │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│         Core Logic Layer                │
│         (fantasma_core.py)              │
│                                         │
│  - FantasmaCore: Main controller       │
│  - FantasmaConfig: Configuration       │
│  - NetworkMode: Hotspot/Bridge enum    │
│  - NetworkInterface: Interface model   │
└────────────────┬────────────────────────┘
                 │
┌────────────────▼────────────────────────┐
│      Platform Adapter Interface         │
│      (PlatformAdapter ABC)              │
│                                         │
│  Abstract methods all adapters must    │
│  implement:                             │
│  - detect_interfaces()                  │
│  - start_hotspot()                      │
│  - start_bridge()                       │
│  - stop_sharing()                       │
│  - get_status()                         │
└──────┬──────┬──────┬──────┬────────────┘
       │      │      │      │
    ┌──▼─┐ ┌─▼──┐ ┌─▼──┐ ┌─▼────┐
    │macOS│ │Linux│ │Win │ │Termux│
    └──┬─┘ └─┬──┘ └─┬──┘ └─┬────┘
       │      │      │      │
    ┌──▼──────▼──────▼──────▼────┐
    │   Driver/System Tool Layer  │
    │                             │
    │  macOS: networksetup, pfctl │
    │  Linux: hostapd, iptables   │
    │  Windows: netsh, ICS        │
    │  Termux: svc, iptables      │
    └─────────────────────────────┘
```

## Component Details

### 1. Core Logic Layer (`fantasma_core.py`)

**Purpose**: Platform-independent business logic

**Key Classes**:

- `NetworkMode`: Enum for operation modes (HOTSPOT, BRIDGE)
- `ConnectionType`: Enum for interface types (WIFI, USB, BLUETOOTH, ETHERNET)
- `NetworkInterface`: Represents a network interface
- `FantasmaConfig`: Configuration object for a sharing session
- `PlatformAdapter`: Abstract base class for platform implementations
- `FantasmaCore`: Main controller that orchestrates everything

**Key Responsibilities**:
- Validate configurations
- Coordinate adapter operations
- Maintain sharing state
- Provide unified API

### 2. Platform Adapters (`adapters/`)

Each platform has its own adapter that inherits from `PlatformAdapter` and implements platform-specific logic.

#### macOS Adapter (`macos_adapter.py`)

**Tools Used**:
- `networksetup`: Interface management
- `ifconfig`: Interface configuration
- `pfctl`: Packet filtering and NAT
- `launchctl`: Service management
- System Preferences: Internet Sharing

**Hotspot Implementation**:
- Configures NAT via `defaults` command
- Opens System Preferences for user confirmation
- Uses built-in Internet Sharing daemon

**Bridge Implementation**:
- Creates `bridge0` interface
- Adds member interfaces with `ifconfig bridge0 addm`
- Native macOS bridge support

#### Linux Adapter (`linux_adapter.py`)

**Tools Used**:
- `hostapd`: WiFi access point daemon
- `dnsmasq`: DHCP and DNS server
- `iptables` or `nftables`: Firewall and NAT
- `brctl` or `ip link`: Bridge management
- `ip`: Interface configuration

**Hotspot Implementation** (The "Paradise"):
1. Configure target interface IP
2. Start `dnsmasq` for DHCP
3. Start `hostapd` for WiFi AP (if WiFi target)
4. Enable IP forwarding via sysctl
5. Configure NAT with iptables MASQUERADE
6. Setup FORWARD chain rules

**Bridge Implementation**:
- Try `brctl` (bridge-utils) first
- Fall back to `ip link` bridge commands
- Pure Layer 2 forwarding

#### Windows Adapter (`windows_adapter.py`)

**Tools Used**:
- `netsh`: Network shell for configuration
- ICS: Internet Connection Sharing (via GUI/WMI)
- Optional: WiFiDirect for advanced scenarios

**Hotspot Implementation**:
- Uses `netsh wlan set hostednetwork` for WiFi
- Opens Network Connections for ICS configuration
- Requires Administrator privileges

**Bridge Implementation**:
- Opens Network Connections for manual bridge setup
- Windows supports bridging but requires GUI

**Limitations**:
- Full automation requires WMI or PowerShell
- Many operations need user confirmation
- Best suited for interactive use

#### Termux/Android Adapter (`termux_adapter.py`)

**Tools Used**:
- `svc`: Android service control
- `iptables`: NAT and routing
- `ip`: Interface configuration
- Optional: `termux-api` for enhanced control

**Hotspot Implementation**:
- Attempts `termux-api` commands if available
- Falls back to manual instructions
- Configures `iptables` NAT rules with root
- Uses Android's built-in tethering

**Bridge Implementation**:
- Checks for L2 bridge kernel support
- Falls back to **L3 proxy mode** if unsupported
- L3 proxy: IP forwarding + NAT (elegant workaround)

**Why L3 Proxy?**
Most Android kernels don't compile bridge module. L3 proxy provides same functionality at Layer 3:
- Enables IP forwarding
- Uses iptables MASQUERADE
- Transparent to end users
- Works on any Android device

### 3. CLI Layer (`fantasma_cli.py`)

**Purpose**: User interface

**Commands**:
- `list`: Show available interfaces
- `start`: Start sharing (hotspot or bridge)
- `stop`: Stop sharing
- `status`: Show current status

**Features**:
- Colored output with ANSI codes
- Clear help text
- Comprehensive error messages
- Cross-platform compatibility

## Operation Modes Deep Dive

### Hotspot Mode (NAT/Router)

**What it does**:
1. Creates a new subnet (e.g., 192.168.137.0/24)
2. Assigns target interface as gateway (192.168.137.1)
3. Runs DHCP server to assign IPs to clients
4. Performs NAT to translate private IPs to source interface
5. Forwards packets with stateful firewall

**Network Flow**:
```
Client (192.168.137.100)
    ↓
Target Interface (192.168.137.1)
    ↓
NAT Translation
    ↓
Source Interface (10.0.0.50)
    ↓
Internet
```

**Use Cases**:
- Sharing to mobile devices
- Creating isolated networks
- Public WiFi scenarios
- IoT device networks

### Bridge Mode (Layer 2)

**What it does**:
1. Creates bridge interface
2. Adds source and target as bridge members
3. Forwards Ethernet frames directly
4. Clients get IPs from original network's DHCP
5. No NAT, no separate subnet

**Network Flow**:
```
Client
    ↓
Target Interface
    ↓
Bridge (transparent)
    ↓
Source Interface
    ↓
Original Network DHCP/Router
```

**Use Cases**:
- Extending existing networks
- Maintaining VLANs
- Avoiding double NAT
- Enterprise environments
- Network labs and testing

## Design Decisions

### Why Python?

1. **Cross-platform**: Native on all target platforms
2. **Subprocess control**: Excellent for invoking system tools
3. **Rapid development**: Quick iteration and testing
4. **Maintainability**: Easy to understand and modify
5. **Future extensibility**: Can add web UI, APIs, etc.

### Why Abstract Base Class?

1. **Type safety**: Ensures all adapters implement required methods
2. **Documentation**: ABC serves as contract documentation
3. **IDE support**: Better autocomplete and type checking
4. **Maintainability**: Easy to add new platforms

### Why Not External Dependencies?

1. **Simplicity**: Easier installation
2. **Reliability**: No dependency conflicts
3. **Portability**: Works on minimal systems (Termux)
4. **Security**: Less attack surface

## Error Handling Strategy

### Graceful Degradation

Each adapter handles errors gracefully:
- Missing tools → Clear error messages
- Insufficient permissions → Guidance on fixing
- Unsupported hardware → Fallback suggestions

### User Guidance

Instead of cryptic errors, provide actionable guidance:
```python
self.logger.warning("WiFi adapter doesn't support AP mode")
self.logger.info("Try using USB or Bluetooth instead")
```

## Security Considerations

### Privilege Management

- **macOS**: Some operations require sudo
- **Linux**: Most operations require root
- **Windows**: Requires Administrator
- **Termux**: Root optional but recommended

### Firewall Rules

All adapters configure appropriate firewall rules:
- Allow forwarding between interfaces
- Enable stateful packet inspection
- Maintain security boundaries

### Password Requirements

For WiFi hotspots:
- Minimum 8 characters
- WPA2 encryption
- Clear warnings for weak passwords

## Future Extensions

### Web UI (Planned)

```
┌─────────────────────┐
│   Web UI (Flask)    │
│   Port 8080         │
└──────────┬──────────┘
           │
           ▼
    FantasmaCore API
```

Features:
- Browser-based control panel
- Real-time status monitoring
- Connected devices list
- Bandwidth graphs

### Configuration Profiles

```python
profiles = {
    "home_usb": FantasmaConfig(...),
    "office_wifi": FantasmaConfig(...),
    "travel_bluetooth": FantasmaConfig(...)
}
```

### Multi-Target Support

Share to multiple interfaces simultaneously:
```python
config = FantasmaConfig(
    source=wifi_interface,
    targets=[usb_interface, bluetooth_interface]
)
```

## Testing Strategy

### Unit Tests
- Test each adapter in isolation
- Mock system commands
- Validate configuration logic

### Integration Tests
- Test on actual systems
- Verify network connectivity
- Check firewall rules

### Platform-Specific Tests
- macOS: Test on different macOS versions
- Linux: Test on different distros
- Windows: Test on Windows 10/11
- Termux: Test on different Android versions

## Performance Considerations

### Startup Time
- Interface detection: <1 second
- Hotspot startup: 2-5 seconds
- Bridge startup: 1-2 seconds

### Resource Usage
- CPU: Minimal (mostly idle)
- Memory: <50MB for Python process
- Network: Native speed (no bottleneck)

### Limitations
- Bridge mode: Hardware dependent
- Hotspot mode: WiFi adapter must support AP mode
- Android: L3 proxy slightly slower than L2 bridge

## Troubleshooting Architecture

### Diagnostic Flow

1. **Check platform support**
   - `adapter.is_supported()`

2. **Detect interfaces**
   - `adapter.detect_interfaces()`

3. **Validate configuration**
   - `config.validate()`

4. **Check status**
   - `adapter.get_status()`

5. **Review logs**
   - Enable verbose mode: `--verbose`

### Common Issues

**"Interface not found"**
→ Run `list` command to see available interfaces

**"Permission denied"**
→ Run with sudo/Administrator

**"WiFi adapter doesn't support AP mode"**
→ Use USB or Bluetooth target instead

**"Bridge module not loaded"** (Linux/Android)
→ Use hotspot mode or L3 proxy

## Conclusion

The FantasmaWiFi-Pro architecture achieves:

✅ **Simplicity**: One abstraction, four implementations  
✅ **Maintainability**: Clear separation of concerns  
✅ **Extensibility**: Easy to add new platforms or features  
✅ **Reliability**: Graceful error handling  
✅ **Performance**: Native tool invocation  

This architecture "ages well in the universe" because it's based on fundamental networking concepts that don't change, while adapting to platform-specific quirks that do.
