# 📦 Installation Guide - FantasmaWiFi-Pro

Complete installation instructions for all supported platforms.

---

## 🐧 Linux

### Method 1: PyPI (Recommended)

```bash
# Install from PyPI
pip install fantasmawifi-pro

# Or with user install (no sudo needed)
pip install --user fantasmawifi-pro

# Verify installation
fantasma doctor
```

### Method 2: From Source

```bash
# Clone repository
git clone https://github.com/Blackmvmba88/FantasmaWiFi-Pro.git
cd FantasmaWiFi-Pro

# Install dependencies
pip install -r requirements.txt

# Run directly
python3 fantasma_cli.py doctor

# Or install system-wide
sudo python3 setup.py install
```

### System Dependencies

**Debian/Ubuntu:**
```bash
sudo apt update
sudo apt install python3 python3-pip hostapd dnsmasq iptables iw
```

**Fedora/RedHat/CentOS:**
```bash
sudo dnf install python3 python3-pip hostapd dnsmasq iptables iw
```

**Arch Linux:**
```bash
sudo pacman -S python python-pip hostapd dnsmasq iptables iw
```

### Post-Installation

Run diagnostics to verify everything is working:
```bash
sudo fantasma doctor
```

---

## 🍎 macOS

### Method 1: Homebrew (Coming Soon)

```bash
# Will be available soon
brew install fantasmawifi-pro
```

### Method 2: PyPI

```bash
# Install Python 3 if not already installed
# You can use Homebrew: brew install python3

# Install FantasmaWiFi-Pro
pip3 install fantasmawifi-pro

# Verify installation
fantasma doctor
```

### Method 3: From Source

```bash
# Clone repository
git clone https://github.com/Blackmvmba88/FantasmaWiFi-Pro.git
cd FantasmaWiFi-Pro

# Install dependencies
pip3 install -r requirements.txt

# Run directly
python3 fantasma_cli.py doctor

# Or install
python3 setup.py install
```

### System Requirements

- macOS 10.15 (Catalina) or later
- Python 3.7 or later
- Administrator privileges for network operations

### Post-Installation

Run diagnostics:
```bash
fantasma doctor
```

---

## 🪟 Windows

### Method 1: Windows Installer (Coming Soon)

1. Download `FantasmaWiFi-Pro-Setup.exe` from [Releases](https://github.com/Blackmvmba88/FantasmaWiFi-Pro/releases)
2. Run the installer
3. Follow the installation wizard
4. Launch from Start Menu or Desktop shortcut

### Method 2: PyPI

```powershell
# Install Python 3 from python.org if not already installed

# Install FantasmaWiFi-Pro
pip install fantasmawifi-pro

# Verify installation (run as Administrator)
fantasma doctor
```

### Method 3: From Source

```powershell
# Clone repository
git clone https://github.com/Blackmvmba88/FantasmaWiFi-Pro.git
cd FantasmaWiFi-Pro

# Install dependencies
pip install -r requirements.txt

# Run directly (as Administrator)
python fantasma_cli.py doctor
```

### System Requirements

- Windows 10 or later
- Python 3.7 or later
- WiFi adapter that supports Hosted Network
- Administrator privileges

### Checking WiFi Adapter Compatibility

```powershell
# Run as Administrator
netsh wlan show drivers
```

Look for: `Hosted network supported  : Yes`

### Post-Installation

Run diagnostics as Administrator:
```powershell
fantasma doctor
```

---

## 🤖 Android (Termux)

### Method 1: Termux Package (Coming Soon)

```bash
# Will be available soon
pkg install fantasmawifi-pro
```

### Method 2: PyPI

```bash
# Update packages
pkg update && pkg upgrade

# Install dependencies
pkg install python python-pip iptables

# Install FantasmaWiFi-Pro
pip install fantasmawifi-pro

# Verify installation
fantasma doctor
```

### Method 3: From Source

```bash
# Install git
pkg install git

# Clone repository
git clone https://github.com/Blackmvmba88/FantasmaWiFi-Pro.git
cd FantasmaWiFi-Pro

# Install dependencies
pip install -r requirements.txt

# Run directly
python fantasma_cli.py doctor
```

### System Requirements

- Android 7.0 or later
- Termux app installed
- Root access (optional, but recommended for full functionality)

### Granting Permissions

Some features require root access:
```bash
# Test root access
su -c "id"

# If successful, you have root access
```

### Post-Installation

Run diagnostics:
```bash
fantasma doctor
```

---

## 🐳 Docker (Coming Soon)

```bash
# Pull official image
docker pull fantasmawifi/fantasmawifi-pro

# Run with web UI
docker run -d \
  --name fantasma \
  --network host \
  --cap-add NET_ADMIN \
  -v /path/to/config:/config \
  fantasmawifi/fantasmawifi-pro

# Access web UI at http://localhost:8080
```

---

## 🔧 Development Installation

For contributors and developers:

```bash
# Clone repository
git clone https://github.com/Blackmvmba88/FantasmaWiFi-Pro.git
cd FantasmaWiFi-Pro

# Install in development mode
pip install -e .

# Or with development dependencies
pip install -e ".[dev]"

# Run tests (when available)
pytest

# Run linters (when available)
flake8 .
pylint *.py
```

---

## 🚀 Quick Start After Installation

### 1. Run Diagnostics
```bash
sudo fantasma doctor
```

### 2. List Network Interfaces
```bash
fantasma list
```

### 3. Start Sharing

**Hotspot Mode (WiFi):**
```bash
sudo fantasma start -s eth0 -t wlan0 --ssid MyHotspot --password SecurePass123
```

**Bridge Mode:**
```bash
sudo fantasma start -s eth0 -t en1 --bridge
```

### 4. Or Use Web UI
```bash
# Start web interface
fantasma-web

# Access at http://localhost:8080
```

---

## 🔄 Updating

### PyPI Installation
```bash
pip install --upgrade fantasmawifi-pro
```

### Source Installation
```bash
cd FantasmaWiFi-Pro
git pull origin main
pip install --upgrade -r requirements.txt
```

---

## 🗑️ Uninstalling

### PyPI Installation
```bash
pip uninstall fantasmawifi-pro
```

### System Dependencies (Optional)

**Linux:**
```bash
# Only if you want to remove the system tools
sudo apt remove hostapd dnsmasq  # Debian/Ubuntu
sudo dnf remove hostapd dnsmasq  # Fedora/RedHat
sudo pacman -R hostapd dnsmasq   # Arch
```

---

## 🐛 Troubleshooting

### "Command not found: fantasma"

**Solution 1:** Ensure pip bin directory is in PATH
```bash
# Linux/macOS
export PATH="$HOME/.local/bin:$PATH"

# Windows
# Add %APPDATA%\Python\PythonXX\Scripts to PATH
```

**Solution 2:** Use full path
```bash
python3 -m fantasma_cli doctor
```

### "Permission denied"

Make sure to run with appropriate privileges:
```bash
# Linux/macOS
sudo fantasma doctor

# Windows (run PowerShell/CMD as Administrator)
fantasma doctor
```

### "Module not found"

Reinstall dependencies:
```bash
pip install -r requirements.txt
```

### Platform-Specific Issues

See [DOCTOR_GUIDE.md](DOCTOR_GUIDE.md) for detailed troubleshooting.

---

## 📚 Next Steps

After installation:

1. ✅ Read [Quick Reference](QUICKREF.md)
2. ✅ Follow [Tutorials](TUTORIALS.md)
3. ✅ Check [Web UI Guide](WEB_UI_GUIDE.md)
4. ✅ Join community on [GitHub Discussions](https://github.com/Blackmvmba88/FantasmaWiFi-Pro/discussions)

---

## 🆘 Getting Help

- 📖 [Documentation](README.md)
- 🩺 [Doctor Guide](DOCTOR_GUIDE.md)
- 🐛 [Report Issues](https://github.com/Blackmvmba88/FantasmaWiFi-Pro/issues)
- 💬 [Discussions](https://github.com/Blackmvmba88/FantasmaWiFi-Pro/discussions)
- 📧 Contact: See repository

---

**Last Updated**: Q1 2026
