# 🕸️ FantasmaWiFi-Pro v7.5

> **"Interface A consumes internet, Interface B distributes internet"**  
> *The rest is theater.*

**FantasmaWiFi-Pro** is a multi-platform network sharing tool that transforms your computer into a powerful WiFi hotspot or network bridge. Born from the need to share weak WiFi signals with mobile devices, it has evolved into a comprehensive cross-platform solution with both CLI and Web UI.

---

## 🚀 What's New in v7.5

### Web UI Control Panel 🌐
- ✅ **Browser-Based Interface** - Modern, intuitive web dashboard
- ✅ **Real-Time Monitoring** - Live status updates via WebSocket
- ✅ **Configuration Profiles** - Save and load settings
- ✅ **Multi-Device Access** - Control from any device on your network
- ✅ **Visual Interface** - No command-line knowledge required

### Multi-Platform Support 🌍
- ✅ **macOS** - Native Internet Sharing + bridge support
- ✅ **Linux** - Full hostapd + dnsmasq + iptables/nftables
- ✅ **Windows** - Hosted Network + ICS
- ✅ **Termux/Android** - Tethering + iptables (with L3 proxy fallback)

### Dual Operation Modes 🔀

**Hotspot Mode (NAT/Router)**
- Creates own network with DHCP
- Perfect for mobile devices, IoT, consoles
- NAT + stateful firewall

**Bridge Mode (Layer 2)**
- Transparent network extension
- Avoids double NAT
- Enterprise/lab use cases

### Clean Architecture 🏗️
```
[Core Fantasma] → [Platform Adapter] → [Driver Layer]
    Python            mac/linux/win/termux    System Tools
```

---

## 📦 Quick Start

### Installation
```bash
git clone https://github.com/Blackmvmba88/FantasmaWiFi-Pro.git
cd FantasmaWiFi-Pro
chmod +x fantasma_cli.py start_web_ui.sh
```

### Web UI (Recommended for Most Users)
```bash
# Start the web interface
./start_web_ui.sh

# Access in your browser
# → http://localhost:8080
```

The Web UI provides:
- Visual interface for all operations
- Real-time status monitoring
- Configuration profile management
- Easy setup for non-technical users

See [WEB_UI_GUIDE.md](WEB_UI_GUIDE.md) for detailed Web UI documentation.

### CLI (For Power Users & Automation)
```bash
# List interfaces
./fantasma_cli.py list

# Start hotspot (WiFi)
./fantasma_cli.py start -s en0 -t wlan1 --ssid MyWiFi --password SecurePass123

# Start bridge mode
./fantasma_cli.py start -s en0 -t en1 --bridge

# Stop sharing
./fantasma_cli.py stop

# Check status
./fantasma_cli.py status
```

---

## 📚 Documentation

- **[Web UI Guide](WEB_UI_GUIDE.md)** - Complete Web UI documentation
- **[Complete README](README_NEW.md)** - Full CLI documentation with examples
- **[Architecture Guide](ARCHITECTURE.md)** - Technical deep dive
- **Legacy Scripts** - Original bash scripts (`phantom_*.sh`) for macOS

---

## 🛠️ Legacy Versions

### Fase 1-2: El Puente Espectral ⚡ (Completed)
The original macOS-only bash scripts are still available:
- `phantom_control.sh` - Basic control panel
- `phantom_operator.sh` - Advanced "AI brain" interface with themes

These scripts provided the foundation for the multi-platform architecture.

### Fase 3: Multi-Platform Architecture 🌐 (v7.0 - Completed)
Complete rewrite in Python with:
- Cross-platform support (4 platforms)
- Dual operation modes (Hotspot + Bridge)
- Clean adapter-based architecture
- Unified CLI interface

### Fase 4: Web UI 🌐 (v7.5 - Current)
Modern web-based control panel with:
- Browser-based interface
- Real-time monitoring
- Configuration profiles
- Multi-device access

---

## 🧙‍♂️ Filosofía de Uso

Esta herramienta no es solo un ajuste de red; es una declaración de **Soberanía Digital**. 

*This tool is not just a network script; it's a declaration of **Digital Sovereignty**.*

Don't accept WiFi dead zones. Create your own infrastructure.

---

## 🗺️ Roadmap

- [x] **Phase 1-2**: macOS bash scripts (Completed)
- [x] **Phase 3**: Multi-platform architecture (v7.0 - Completed)
- [x] **Phase 4**: Web UI local control panel (v7.5 - Current) ✨
- [ ] **Phase 5**: Advanced features (Q2 2026)
  - Bandwidth monitoring
  - Connected devices management
  - Advanced firewall rules
  - VPN integration
- [ ] **Phase 6**: Commercialization (Q3 2026)

---

## 📄 License

Licensed under the Sovereignty License - see [LICENSE_SOVEREIGNTY.md](LICENSE_SOVEREIGNTY.md) for details.

**Developed with ❤️ for the ecosystem of Iyari Cancino Gomez**

---

*Version 7.5 "Web Edition" - The interface that makes digital sovereignty accessible to everyone* 🌌
