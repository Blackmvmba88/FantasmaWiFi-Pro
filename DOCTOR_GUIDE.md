# 🩺 FantasmaWiFi-Pro Doctor - Diagnostic Tool

The `fantasma doctor` command is a comprehensive system diagnostic tool that checks your system's capabilities, dependencies, and identifies potential issues before running FantasmaWiFi-Pro.

---

## Quick Start

```bash
# Run basic diagnostics
fantasma doctor

# Run with verbose output (includes additional details)
fantasma doctor -v

# Export diagnostics as JSON (for automation/scripting)
fantasma doctor --json

# Disable colored output (for logging)
fantasma doctor --no-color
```

Or run directly:
```bash
python3 fantasma_doctor.py
```

---

## What It Checks

### 1. Platform Information
- Operating system and version
- Python version
- System architecture
- Linux distribution (if applicable)
- Termux environment detection

### 2. Network Interfaces
- Lists all available network interfaces
- Shows interface status (UP/DOWN)
- Identifies WiFi-capable interfaces
- Checks for AP mode support (WiFi hotspot capability)

### 3. System Dependencies

**Linux:**
- `hostapd` - WiFi access point daemon
- `dnsmasq` - DHCP and DNS server
- `iptables` - Packet filtering and NAT
- `nftables` - Modern packet filtering (optional)
- `iw` - WiFi configuration utility

**macOS:**
- Internet Sharing availability
- `networksetup` command
- System permissions

**Windows:**
- `netsh` availability
- Hosted Network support
- WiFi driver capabilities

**Termux/Android:**
- `iptables` availability
- Root access detection
- SELinux status

### 4. Privileges
- Checks for administrative/root privileges
- Provides instructions for elevation if needed

### 5. Capabilities
- **Hotspot Mode**: Can create WiFi access point
- **Bridge Mode**: Can extend existing network
- **Monitor Mode**: Can monitor WiFi traffic (advanced)

### 6. Known Issues
- NetworkManager interference (Linux)
- SELinux enforcement (Linux)
- System Integrity Protection (macOS)
- Service conflicts
- Firewall issues

---

## Understanding the Output

### Status Icons

- ✓ **PASS** (Green): Check passed, everything is good
- ⚠ **WARN** (Yellow): Warning, might need attention but not critical
- ✗ **FAIL** (Red): Critical issue that needs to be resolved
- ℹ **INFO** (Blue): Informational, no action needed

### Example Output

```
🔍 FantasmaWiFi-Pro System Diagnostic
============================================================

Platform Information:
  ℹ System: Linux 22.04
  ℹ Python: 3.10.8
  ℹ Distribution: Ubuntu 22.04.3 LTS

Network Interfaces:
  ✓ wlan0 - UP
  ✓ eth0 - UP
  ⚠ wlan1 - DOWN

System Dependencies:
  ⚠ Privileges: Not running with administrative privileges
      → Run with sudo (Linux/macOS) or as Administrator (Windows)
  ✓ hostapd: Installed: 2.10
  ✓ dnsmasq: Installed: 2.86
  ✓ iptables: Installed: iptables v1.8.7
  ℹ nftables: Not installed (optional alternative to iptables)
  ✓ iw: Installed: iw 5.16

Capabilities:
  ✓ Hotspot Mode: Supported (wlan0)
  ✓ Bridge Mode: Supported

Known Issues:
  ⚠ NetworkManager Active: NetworkManager may interfere with manual network configuration
      → Temporarily stop: sudo systemctl stop NetworkManager

Overall Status:
  ✓ All critical checks passed!
  Ready to use: fantasma start
```

---

## Common Issues and Solutions

### Issue: "Not running with administrative privileges"

**Solution (Linux/macOS):**
```bash
sudo fantasma doctor
```

**Solution (Windows):**
Run Command Prompt or PowerShell as Administrator

### Issue: "hostapd not installed" (Linux)

**Solution (Debian/Ubuntu):**
```bash
sudo apt update
sudo apt install hostapd dnsmasq
```

**Solution (Fedora/RedHat):**
```bash
sudo dnf install hostapd dnsmasq
```

**Solution (Arch):**
```bash
sudo pacman -S hostapd dnsmasq
```

### Issue: "NetworkManager may interfere"

**Temporary Solution:**
```bash
sudo systemctl stop NetworkManager
```

**Permanent Solution (not recommended):**
```bash
sudo systemctl disable NetworkManager
```

**Better Solution:**
Configure NetworkManager to ignore specific interfaces in `/etc/NetworkManager/NetworkManager.conf`:
```ini
[keyfile]
unmanaged-devices=interface-name:wlan0
```

### Issue: "Hosted Network not supported" (Windows)

**Cause**: Your WiFi adapter doesn't support Windows Hosted Network feature.

**Solution**: 
1. Update WiFi driver to latest version
2. Check manufacturer website for driver updates
3. Consider using an external WiFi adapter that supports Hosted Network

### Issue: "No WiFi interface detected"

**Possible Causes:**
1. No WiFi adapter present
2. WiFi adapter disabled
3. Driver not loaded

**Solutions:**
- Check if WiFi is enabled in system settings
- Verify WiFi adapter is connected (if USB)
- Check if driver is loaded: `lsmod | grep wifi` (Linux)
- Try reloading the driver: `sudo modprobe <driver_name>`

---

## JSON Output Format

When using `--json` flag, the output is structured data suitable for automation:

```json
{
  "platform_info": {
    "system": "Linux",
    "release": "6.2.0-39-generic",
    "version": "#40-Ubuntu SMP...",
    "machine": "x86_64",
    "python": "3.10.8",
    "distribution": "Ubuntu 22.04.3 LTS"
  },
  "interfaces": [
    {"name": "wlan0", "status": "UP"},
    {"name": "eth0", "status": "UP"}
  ],
  "dependencies": [
    {
      "name": "hostapd",
      "status": "PASS",
      "message": "Installed: 2.10",
      "details": null,
      "fix_suggestion": null
    }
  ],
  "capabilities": [...],
  "known_issues": [...],
  "overall_status": "PASS"
}
```

---

## Integration with Scripts

### Bash Example

```bash
#!/bin/bash

# Check if system is ready
if fantasma doctor --no-color > /dev/null 2>&1; then
    echo "System ready, starting FantasmaWiFi..."
    fantasma start -s eth0 -t wlan0 --ssid MyHotspot --password SecurePass123
else
    echo "System not ready. Running diagnostics..."
    fantasma doctor
    exit 1
fi
```

### Python Example

```python
import subprocess
import json

# Run diagnostics and get JSON output
result = subprocess.run(
    ['fantasma', 'doctor', '--json'],
    capture_output=True,
    text=True
)

# Parse results
if result.returncode == 0:
    report = json.loads(result.stdout)
    
    # Check for WiFi interfaces
    wifi_interfaces = [
        iface for iface in report['interfaces']
        if 'wlan' in iface['name'] or 'wifi' in iface['name'].lower()
    ]
    
    if wifi_interfaces:
        print(f"Found {len(wifi_interfaces)} WiFi interface(s)")
    else:
        print("No WiFi interfaces found")
else:
    print("Diagnostics failed")
```

---

## Exit Codes

- `0` - All critical checks passed
- `1` - One or more critical checks failed

---

## Verbose Mode

Use `-v` or `--verbose` flag for additional details:

```bash
fantasma doctor -v
```

This will show:
- Extended details for each check
- Additional diagnostic information
- More verbose error messages

---

## Tips

1. **Run Before First Use**: Always run `fantasma doctor` before using FantasmaWiFi for the first time on a new system.

2. **After System Updates**: Run diagnostics after major system updates or driver changes.

3. **Troubleshooting**: When encountering issues, `fantasma doctor -v` output is helpful for bug reports.

4. **Automation**: Use `--json` flag when integrating with automation tools or monitoring systems.

5. **Save Output**: Save diagnostic output for reference:
   ```bash
   fantasma doctor > diagnostics.txt
   fantasma doctor --json > diagnostics.json
   ```

---

## When to Run Doctor

- ✅ First installation on a new system
- ✅ Before reporting a bug
- ✅ After system/driver updates
- ✅ When experiencing connection issues
- ✅ When setting up automated deployments
- ✅ To verify system capabilities

---

## Advanced Usage

### Check Specific Interface Capabilities

While doctor checks all interfaces automatically, you can use system tools for more detailed info:

**Linux:**
```bash
# Check WiFi interface capabilities
sudo iw dev wlan0 info
sudo iw phy phy0 info

# Check supported modes
sudo iw phy phy0 info | grep -A 10 "Supported interface modes"
```

**macOS:**
```bash
# Check WiFi interface info
networksetup -listallhardwareports
system_profiler SPNetworkDataType
```

**Windows:**
```cmd
# Check hosted network support
netsh wlan show drivers
```

---

## Contributing

If you encounter an issue that `fantasma doctor` doesn't detect, please:

1. Run `fantasma doctor -v --json > report.json`
2. Open an issue on GitHub with the report
3. Describe the issue you encountered
4. Help us improve the diagnostic tool!

---

**Related Documentation:**
- [Main README](README.md)
- [Tutorials](TUTORIALS.md)
- [Troubleshooting](CONTRIBUTING.md#troubleshooting)
- [Roadmap 2026](ROADMAP_2026.md)
