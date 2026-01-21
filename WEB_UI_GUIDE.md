# 🌐 FantasmaWiFi-Pro Web UI Guide

## Overview

The FantasmaWiFi-Pro Web UI provides a modern, browser-based control panel for managing WiFi sharing. It offers an intuitive interface for users who prefer graphical controls over command-line tools.

## Features

### 🎯 Core Functionality
- **Visual Interface**: Modern, responsive web dashboard
- **Real-Time Updates**: Live status monitoring via WebSockets
- **Easy Configuration**: Form-based setup for both hotspot and bridge modes
- **Profile Management**: Save and load configuration profiles
- **Multi-Device Access**: Control from any device on your network

### 📊 Dashboard Components

1. **Status Card**
   - Current sharing status (active/inactive)
   - Platform information
   - Operation mode (hotspot/bridge)
   - Source and target interfaces
   - Uptime tracking

2. **Control Panel**
   - Mode selection (Hotspot/Bridge)
   - Interface selection (source/target)
   - Hotspot configuration (SSID, password, channel)
   - Start/stop controls

3. **Interfaces Display**
   - All available network interfaces
   - Interface types (WiFi, Ethernet, USB, Bluetooth)
   - IP and MAC addresses
   - Status indicators

4. **Configuration Profiles**
   - Save current configurations
   - Load saved profiles
   - Delete profiles
   - Quick setup switching

## Installation

### Prerequisites

```bash
# Python 3.7+ required
python3 --version

# Install dependencies
pip3 install flask flask-socketio python-socketio
```

Or use the requirements.txt:

```bash
pip3 install -r requirements.txt
```

## Usage

### Starting the Web UI

#### Method 1: Quick Start Script (Recommended)

```bash
./start_web_ui.sh
```

The script will:
1. Check Python installation
2. Install dependencies if needed
3. Start the web server

#### Method 2: Direct Python

```bash
python3 fantasma_web.py
```

#### Method 3: Custom Configuration

```bash
# Custom host and port
python3 fantasma_web.py --host 0.0.0.0 --port 8080

# Debug mode
python3 fantasma_web.py --debug

# Different port
python3 fantasma_web.py --port 5000
```

### Accessing the Web UI

Once started, open your web browser and navigate to:

- **Local access**: http://localhost:8080
- **Network access**: http://YOUR_IP:8080

The server listens on `0.0.0.0` by default, allowing access from other devices on your network.

## Using the Web Interface

### Starting WiFi Sharing

1. **Select Operation Mode**
   - **Hotspot Mode**: Creates a new WiFi network with NAT
   - **Bridge Mode**: Extends existing network transparently

2. **Choose Source Interface**
   - Select the interface that has internet connection
   - Usually your Ethernet or WiFi connection

3. **Choose Target Interface**
   - Select the interface to share internet through
   - Can be WiFi, USB, Bluetooth, or another Ethernet

4. **Configure Hotspot Settings** (Hotspot mode only)
   - **SSID**: Network name (default: FantasmaWiFi)
   - **Password**: Minimum 8 characters (leave empty for open network)
   - **Channel**: WiFi channel (1, 6, or 11)
   - **IP Range**: Subnet for clients (default: 192.168.137.0/24)

5. **Click "Start Sharing"**
   - The system will start the sharing process
   - Status will update to "Active"
   - You'll see live information about the connection

### Stopping WiFi Sharing

1. When sharing is active, the "Stop Sharing" button appears
2. Click it to stop sharing
3. System cleans up all configurations automatically

### Managing Configuration Profiles

#### Saving a Profile

1. Configure your desired settings
2. Click "Save Current Config"
3. Enter a profile name
4. Profile is saved for future use

#### Loading a Profile

1. Click "Load Profile"
2. Select from available profiles
3. Configuration is applied automatically

#### Deleting a Profile

1. Find the profile in the list
2. Click the "Delete" button
3. Confirm deletion

## API Reference

The Web UI exposes a REST API that can be used programmatically:

### GET /api/interfaces

List all available network interfaces.

```bash
curl http://localhost:8080/api/interfaces
```

Response:
```json
{
  "interfaces": [
    {
      "name": "en0",
      "type": "wifi",
      "status": "up",
      "ip": "192.168.1.100",
      "mac": "00:11:22:33:44:55"
    }
  ]
}
```

### GET /api/status

Get current sharing status.

```bash
curl http://localhost:8080/api/status
```

Response:
```json
{
  "active": true,
  "mode": "hotspot",
  "source_interface": "en0",
  "target_interface": "en1",
  "uptime": 3600,
  "platform": "macOS"
}
```

### POST /api/start

Start WiFi sharing.

```bash
curl -X POST http://localhost:8080/api/start \
  -H "Content-Type: application/json" \
  -d '{
    "mode": "hotspot",
    "source": "en0",
    "target": "en1",
    "ssid": "MyWiFi",
    "password": "SecurePass123",
    "channel": 6,
    "ip_range": "192.168.137.0/24"
  }'
```

### POST /api/stop

Stop WiFi sharing.

```bash
curl -X POST http://localhost:8080/api/stop
```

### Configuration Profiles

```bash
# List profiles
curl http://localhost:8080/api/profiles

# Save profile
curl -X POST http://localhost:8080/api/profiles \
  -H "Content-Type: application/json" \
  -d '{
    "name": "home_wifi",
    "config": {...}
  }'

# Get profile
curl http://localhost:8080/api/profiles/home_wifi

# Delete profile
curl -X DELETE http://localhost:8080/api/profiles/home_wifi
```

## WebSocket Events

The Web UI uses WebSocket for real-time updates:

### Client → Server

- `connect`: Client connected
- `disconnect`: Client disconnected
- `request_status`: Request status update

### Server → Client

- `connected`: Connection confirmed
- `status_update`: Status information broadcast

## Security Considerations

### Local Network Only

By default, the Web UI is designed for local network use:
- No authentication required
- Assumes trusted network environment
- Uses HTTP (not HTTPS)

### Production Deployment

For production use, consider:

1. **Add Authentication**
   ```python
   # Add to fantasma_web.py
   from flask_httpauth import HTTPBasicAuth
   auth = HTTPBasicAuth()
   ```

2. **Use HTTPS**
   ```bash
   # Generate self-signed certificate
   openssl req -x509 -newkey rsa:4096 -nodes \
     -out cert.pem -keyout key.pem -days 365
   
   # Run with SSL
   socketio.run(app, ssl_context=('cert.pem', 'key.pem'))
   ```

3. **Restrict Access**
   ```bash
   # Bind to localhost only
   python3 fantasma_web.py --host 127.0.0.1
   ```

4. **Use Firewall**
   ```bash
   # Linux: Allow only local subnet
   sudo ufw allow from 192.168.1.0/24 to any port 8080
   ```

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 8080
lsof -i :8080  # macOS/Linux
netstat -ano | findstr :8080  # Windows

# Use different port
python3 fantasma_web.py --port 8888
```

### Cannot Access from Other Devices

1. Check firewall settings
2. Verify server is listening on 0.0.0.0
3. Use correct IP address (not localhost)

### WebSocket Connection Failed

1. Check browser console for errors
2. Verify Socket.IO version compatibility
3. Check for proxy/firewall blocking WebSocket

### Interface Detection Issues

The Web UI relies on the core Fantasma adapter:
1. Ensure platform adapter is working
2. Check CLI works: `./fantasma_cli.py list`
3. Review server logs for errors

## Platform-Specific Notes

### macOS
- May need sudo for some operations
- System Preferences may open for Internet Sharing confirmation

### Linux
- Requires root for most operations
- Install dependencies: hostapd, dnsmasq, iptables

### Windows
- Requires Administrator privileges
- Some operations open Network Connections GUI

### Termux/Android
- Limited to IP forwarding mode
- Requires root for full functionality

## Development

### Running in Debug Mode

```bash
python3 fantasma_web.py --debug
```

Debug mode enables:
- Auto-reload on code changes
- Verbose error messages
- Better error pages

### Custom Styling

Edit `/static/css/style.css` to customize appearance:
- Dark theme by default
- CSS variables for easy customization
- Responsive design for mobile devices

### Adding Features

The Web UI is built with:
- **Backend**: Flask + Flask-SocketIO
- **Frontend**: Vanilla JavaScript + Socket.IO client
- **Styling**: Custom CSS with CSS Grid/Flexbox

## Performance

### Resource Usage
- **Memory**: ~50-100MB for Python + Flask
- **CPU**: Minimal when idle
- **Network**: Low bandwidth (status updates every 5 seconds)

### Concurrent Users
- Designed for single-user/small team use
- Can handle multiple browser connections
- WebSocket updates broadcast to all clients

## Comparison with CLI

| Feature | CLI | Web UI |
|---------|-----|--------|
| **Setup Speed** | Faster | Slightly slower |
| **Ease of Use** | Technical users | All users |
| **Remote Access** | SSH required | Browser-based |
| **Resource Usage** | Minimal | Moderate |
| **Status Monitoring** | Manual refresh | Real-time |
| **Profile Management** | Manual | Built-in |
| **Best For** | Automation, scripting | Interactive use |

## Future Enhancements

Planned features for future versions:

- [ ] User authentication
- [ ] HTTPS support
- [ ] Bandwidth monitoring graphs
- [ ] Connected devices list
- [ ] Traffic statistics
- [ ] Advanced firewall rules
- [ ] VPN integration
- [ ] Multi-language support
- [ ] Mobile app companion

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/Blackmvmba88/FantasmaWiFi-Pro/issues
- Documentation: See README.md and ARCHITECTURE.md

## License

FantasmaWiFi-Pro Web UI is part of the FantasmaWiFi-Pro project.
See LICENSE_SOVEREIGNTY.md for details.

---

**Version 7.5 "Web Edition"** - Phase 4 Complete

*"Interface A consumes internet, Interface B distributes internet - now with a beautiful UI"* 🕸️
