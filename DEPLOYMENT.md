# 🚀 FantasmaWiFi-Pro Deployment Guide

Complete guide for deploying FantasmaWiFi-Pro in various environments.

## Table of Contents

1. [Production Deployment](#production-deployment)
2. [Docker Deployment](#docker-deployment)
3. [Cloud Deployment](#cloud-deployment)
4. [Raspberry Pi Deployment](#raspberry-pi-deployment)
5. [Security Considerations](#security-considerations)
6. [Monitoring & Logging](#monitoring--logging)
7. [Performance Tuning](#performance-tuning)

---

## Production Deployment

### Requirements

- Python 3.7+
- Root/Administrator privileges
- Network interfaces configured
- Dependencies installed

### Installation

#### From PyPI (Coming Soon)

```bash
pip install fantasmawifi-pro
```

#### From Source

```bash
git clone https://github.com/Blackmvmba88/FantasmaWiFi-Pro.git
cd FantasmaWiFi-Pro
pip install -r requirements.txt
pip install .
```

### Running as System Service

#### Linux (systemd)

Create `/etc/systemd/system/fantasma-web.service`:

```ini
[Unit]
Description=FantasmaWiFi-Pro Web Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/FantasmaWiFi-Pro
ExecStart=/usr/bin/python3 /opt/FantasmaWiFi-Pro/fantasma_web.py --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable fantasma-web
sudo systemctl start fantasma-web
sudo systemctl status fantasma-web
```

#### macOS (launchd)

Create `~/Library/LaunchAgents/com.fantasmawifi.web.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.fantasmawifi.web</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/path/to/FantasmaWiFi-Pro/fantasma_web.py</string>
        <string>--host</string>
        <string>0.0.0.0</string>
        <string>--port</string>
        <string>8080</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load service:

```bash
launchctl load ~/Library/LaunchAgents/com.fantasmawifi.web.plist
```

### Reverse Proxy Setup (Nginx)

For production, use Nginx as reverse proxy:

```nginx
server {
    listen 80;
    server_name fantasma.example.com;

    location / {
        proxy_pass http://localhost:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    
    # WebSocket support
    location /socket.io/ {
        proxy_pass http://localhost:8080/socket.io/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

Enable HTTPS with Let's Encrypt:

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d fantasma.example.com
```

---

## Docker Deployment

### Dockerfile

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    hostapd \
    dnsmasq \
    iptables \
    iproute2 \
    wireless-tools \
    bridge-utils \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8080

# Run as root (required for network operations)
USER root

# Start web server
CMD ["python", "fantasma_web.py", "--host", "0.0.0.0", "--port", "8080"]
```

### Docker Compose

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  fantasma:
    build: .
    container_name: fantasmawifi-pro
    privileged: true
    network_mode: host
    restart: unless-stopped
    volumes:
      - ./data:/app/data
    environment:
      - FANTASMA_PORT=8080
      - FANTASMA_HOST=0.0.0.0
```

Build and run:

```bash
docker-compose up -d
```

### Network Configuration

Docker requires `--privileged` and `network_mode: host` for network operations:

```bash
docker run -d \
  --name fantasmawifi \
  --privileged \
  --network host \
  -v $(pwd)/data:/app/data \
  fantasmawifi-pro
```

---

## Cloud Deployment

### AWS EC2

1. **Launch Instance**
   - Ubuntu 22.04 LTS
   - t3.small or larger
   - Security group: Allow port 8080

2. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip hostapd dnsmasq
   ```

3. **Deploy Application**
   ```bash
   git clone https://github.com/Blackmvmba88/FantasmaWiFi-Pro.git
   cd FantasmaWiFi-Pro
   pip3 install -r requirements.txt
   ```

4. **Configure Network Interfaces**
   - Primary interface: Internet connection
   - Secondary interface: WiFi or additional ethernet

5. **Run as Service** (see systemd section above)

### DigitalOcean

Similar to AWS, but:
- Use Droplet with Ubuntu
- Enable private networking
- Configure firewall rules

### Google Cloud Platform

- Use Compute Engine VM
- Configure VPC networking
- Set up firewall rules for port 8080

---

## Raspberry Pi Deployment

Perfect for portable WiFi sharing device!

### Hardware Requirements

- Raspberry Pi 3/4/5
- SD card (16GB+)
- USB WiFi adapter (optional, for dual WiFi)
- Power supply

### Setup

1. **Install Raspberry Pi OS**
   ```bash
   # Use Raspberry Pi Imager
   # Choose Raspberry Pi OS Lite (64-bit)
   ```

2. **Initial Configuration**
   ```bash
   sudo raspi-config
   # Configure locale, timezone, WiFi country
   ```

3. **Install Dependencies**
   ```bash
   sudo apt update
   sudo apt upgrade -y
   sudo apt install -y python3 python3-pip hostapd dnsmasq git
   ```

4. **Clone and Install**
   ```bash
   cd /opt
   sudo git clone https://github.com/Blackmvmba88/FantasmaWiFi-Pro.git
   cd FantasmaWiFi-Pro
   sudo pip3 install -r requirements.txt
   ```

5. **Configure Autostart**
   Use systemd service (see above)

6. **Optional: Headless Access**
   ```bash
   # Enable SSH
   sudo systemctl enable ssh
   sudo systemctl start ssh
   ```

### Use Case: Portable Travel Router

Configure Raspberry Pi to automatically:
1. Connect to hotel WiFi
2. Create secure hotspot
3. Share connection with your devices

---

## Security Considerations

### API Key Management

```bash
# Generate strong API keys
python3 -c "from fantasma_api import api_auth; print(api_auth.create_key('production'))"
```

Store keys securely:
- Use environment variables
- Never commit to git
- Rotate regularly

### Firewall Configuration

```bash
# Allow only specific IPs
sudo ufw allow from 192.168.1.0/24 to any port 8080

# Or specific IP
sudo ufw allow from 192.168.1.100 to any port 8080
```

### HTTPS Configuration

Always use HTTPS in production:

```bash
# Generate self-signed certificate (development)
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout key.pem -out cert.pem -days 365

# Use in production with Let's Encrypt (see Nginx section)
```

### Password Requirements

For hotspots:
- Minimum 8 characters
- Mix of letters, numbers, symbols
- Avoid common words
- Change regularly

### Network Isolation

Isolate shared network from main network:
- Use separate subnet for hotspot
- Configure firewall rules
- Monitor connected devices

---

## Monitoring & Logging

### Application Logs

```bash
# View logs
tail -f /var/log/fantasma.log

# With systemd
journalctl -u fantasma-web -f
```

### Configure Logging

Add to `fantasma_web.py`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/fantasma.log'),
        logging.StreamHandler()
    ]
)
```

### Monitoring Tools

#### Prometheus + Grafana

Expose metrics:

```python
from prometheus_client import Counter, Gauge, start_http_server

# Metrics
requests_total = Counter('fantasma_requests_total', 'Total requests')
active_connections = Gauge('fantasma_active_connections', 'Active connections')

# Start metrics server
start_http_server(9090)
```

#### Simple Status Monitoring

```bash
# Create monitoring script
cat > /usr/local/bin/fantasma-monitor.sh << 'EOF'
#!/bin/bash
while true; do
    if ! curl -f http://localhost:8080/api/status > /dev/null 2>&1; then
        echo "$(date): Fantasma not responding, restarting..."
        systemctl restart fantasma-web
    fi
    sleep 60
done
EOF

chmod +x /usr/local/bin/fantasma-monitor.sh
```

---

## Performance Tuning

### System Limits

```bash
# Increase file descriptors
sudo sysctl -w fs.file-max=100000
sudo sysctl -w net.core.somaxconn=1024

# Make permanent
echo "fs.file-max = 100000" | sudo tee -a /etc/sysctl.conf
```

### Network Optimization

```bash
# Enable TCP optimizations
sudo sysctl -w net.ipv4.tcp_fin_timeout=30
sudo sysctl -w net.ipv4.tcp_keepalive_time=300
sudo sysctl -w net.ipv4.tcp_window_scaling=1

# Increase buffer sizes
sudo sysctl -w net.core.rmem_max=16777216
sudo sysctl -w net.core.wmem_max=16777216
```

### Application Tuning

```python
# Use production WSGI server
# Install gunicorn
pip install gunicorn

# Run with multiple workers
gunicorn -w 4 -b 0.0.0.0:8080 \
  --worker-class eventlet \
  fantasma_web:app
```

### Database for Profiles (Optional)

For large-scale deployments:

```python
import sqlite3

# Store profiles in SQLite instead of memory
conn = sqlite3.connect('fantasma.db')
```

---

## Backup & Recovery

### Backup Configuration

```bash
#!/bin/bash
# backup-fantasma.sh

BACKUP_DIR="/backup/fantasma"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup profiles
cp -r /opt/FantasmaWiFi-Pro/data $BACKUP_DIR/data_$DATE

# Backup configuration
cp /etc/systemd/system/fantasma-web.service $BACKUP_DIR/service_$DATE

echo "Backup completed: $BACKUP_DIR"
```

### Disaster Recovery

1. Reinstall system
2. Restore from backup
3. Restart services

```bash
# Restore
cp -r /backup/fantasma/data_latest /opt/FantasmaWiFi-Pro/data
systemctl restart fantasma-web
```

---

## Troubleshooting Deployment

### Port Already in Use

```bash
# Find process using port
sudo lsof -i :8080

# Kill process
sudo kill -9 <PID>
```

### Permission Denied

```bash
# Run with sudo
sudo python3 fantasma_web.py

# Or configure capabilities (Linux)
sudo setcap cap_net_admin=eip /usr/bin/python3
```

### Service Won't Start

```bash
# Check status
systemctl status fantasma-web

# Check logs
journalctl -u fantasma-web -n 50

# Validate configuration
python3 fantasma_web.py --debug
```

---

## Production Checklist

- [ ] Install dependencies
- [ ] Configure system service
- [ ] Set up reverse proxy (Nginx)
- [ ] Enable HTTPS
- [ ] Configure firewall
- [ ] Set strong API keys
- [ ] Enable logging
- [ ] Set up monitoring
- [ ] Configure backups
- [ ] Test failover
- [ ] Document deployment
- [ ] Create runbook

---

## Support

For deployment issues:
- GitHub Issues: https://github.com/Blackmvmba88/FantasmaWiFi-Pro/issues
- Documentation: [README.md](README.md)
- Community: GitHub Discussions

---

**Happy deploying!** 🚀
