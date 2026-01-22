#!/usr/bin/env python3
"""
Custom Adapter Example
Demonstrates how to create a custom platform adapter for FantasmaWiFi-Pro
This example shows a Raspberry Pi adapter
"""

import subprocess
import logging
from typing import List, Dict, Any

from fantasma_core import (
    PlatformAdapter,
    NetworkInterface,
    ConnectionType,
    FantasmaConfig,
    FantasmaCore
)
from fantasma_plugins import register_adapter, on_hook


@register_adapter('raspberry_pi')
class RaspberryPiAdapter(PlatformAdapter):
    """
    Custom adapter for Raspberry Pi
    
    Features:
    - Optimized for Raspberry Pi hardware
    - Supports built-in WiFi and ethernet
    - Uses raspbian-specific tools
    """
    
    def __init__(self):
        super().__init__()
        self.platform_name = "Raspberry Pi"
        self.logger = logging.getLogger(__name__)
        
        # Raspberry Pi specific settings
        self.default_wifi = "wlan0"
        self.default_eth = "eth0"
        self.hostapd_conf = "/etc/hostapd/hostapd.conf"
        self.dnsmasq_conf = "/etc/dnsmasq.conf"
    
    def detect_interfaces(self) -> List[NetworkInterface]:
        """
        Detect network interfaces on Raspberry Pi
        """
        interfaces = []
        
        try:
            # Use 'ip link' to list interfaces
            result = subprocess.run(
                ['ip', 'link', 'show'],
                capture_output=True,
                text=True,
                check=True
            )
            
            for line in result.stdout.split('\n'):
                if ':' in line and not line.startswith(' '):
                    # Parse interface name
                    parts = line.split(':')
                    if len(parts) >= 2:
                        iface_name = parts[1].strip()
                        
                        # Skip loopback
                        if iface_name == 'lo':
                            continue
                        
                        # Determine type
                        if iface_name.startswith('wlan'):
                            conn_type = ConnectionType.WIFI
                        elif iface_name.startswith('eth'):
                            conn_type = ConnectionType.ETHERNET
                        elif 'usb' in iface_name:
                            conn_type = ConnectionType.USB
                        else:
                            conn_type = ConnectionType.ETHERNET
                        
                        # Get MAC address
                        mac = self._get_mac_address(iface_name)
                        
                        interfaces.append(
                            NetworkInterface(iface_name, conn_type, mac)
                        )
            
            self.logger.info(f"Detected {len(interfaces)} interfaces")
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to detect interfaces: {e}")
        
        return interfaces
    
    def _get_mac_address(self, interface: str) -> str:
        """Get MAC address for an interface"""
        try:
            result = subprocess.run(
                ['cat', f'/sys/class/net/{interface}/address'],
                capture_output=True,
                text=True
            )
            return result.stdout.strip()
        except:
            return "unknown"
    
    def start_hotspot(self, config: FantasmaConfig) -> bool:
        """
        Start hotspot mode on Raspberry Pi
        
        Uses hostapd and dnsmasq
        """
        self.logger.info("Starting Raspberry Pi hotspot...")
        
        try:
            # 1. Configure target interface IP
            self._configure_interface_ip(
                config.target_interface,
                config.gateway_ip
            )
            
            # 2. Configure and start dnsmasq
            self._configure_dnsmasq(config)
            
            # 3. Configure and start hostapd (if WiFi)
            if config.target_interface.startswith('wlan'):
                self._configure_hostapd(config)
            
            # 4. Enable IP forwarding
            self._enable_ip_forwarding()
            
            # 5. Configure NAT with iptables
            self._configure_nat(config)
            
            self.logger.info("✓ Raspberry Pi hotspot started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start hotspot: {e}")
            return False
    
    def _configure_interface_ip(self, interface: str, ip: str):
        """Configure IP address for interface"""
        commands = [
            ['ip', 'addr', 'flush', 'dev', interface],
            ['ip', 'addr', 'add', f'{ip}/24', 'dev', interface],
            ['ip', 'link', 'set', interface, 'up']
        ]
        
        for cmd in commands:
            subprocess.run(cmd, check=True)
    
    def _configure_dnsmasq(self, config: FantasmaConfig):
        """Configure dnsmasq for DHCP"""
        # Create dnsmasq config
        dnsmasq_config = f"""
# FantasmaWiFi-Pro dnsmasq configuration
interface={config.target_interface}
dhcp-range=192.168.137.50,192.168.137.150,12h
dhcp-option=3,{config.gateway_ip}
dhcp-option=6,8.8.8.8,8.8.4.4
"""
        
        # Write config
        with open('/tmp/fantasma_dnsmasq.conf', 'w') as f:
            f.write(dnsmasq_config)
        
        # Start dnsmasq
        subprocess.run([
            'dnsmasq',
            '-C', '/tmp/fantasma_dnsmasq.conf',
            '-k'  # Keep in foreground (or use -d for daemon)
        ], check=False)  # Don't fail if already running
    
    def _configure_hostapd(self, config: FantasmaConfig):
        """Configure hostapd for WiFi AP"""
        # Create hostapd config
        hostapd_config = f"""
# FantasmaWiFi-Pro hostapd configuration
interface={config.target_interface}
driver=nl80211
ssid={config.ssid}
hw_mode=g
channel={config.channel}
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={config.password}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
"""
        
        # Write config
        with open('/tmp/fantasma_hostapd.conf', 'w') as f:
            f.write(hostapd_config)
        
        # Start hostapd
        subprocess.Popen([
            'hostapd',
            '/tmp/fantasma_hostapd.conf'
        ])
    
    def _enable_ip_forwarding(self):
        """Enable IP forwarding"""
        subprocess.run([
            'sysctl', '-w', 'net.ipv4.ip_forward=1'
        ], check=True)
    
    def _configure_nat(self, config: FantasmaConfig):
        """Configure NAT with iptables"""
        commands = [
            # Clear existing rules
            ['iptables', '-t', 'nat', '-F'],
            ['iptables', '-F'],
            
            # Add NAT rule
            ['iptables', '-t', 'nat', '-A', 'POSTROUTING',
             '-o', config.source_interface, '-j', 'MASQUERADE'],
            
            # Add forward rules
            ['iptables', '-A', 'FORWARD',
             '-i', config.source_interface,
             '-o', config.target_interface,
             '-m', 'state', '--state', 'RELATED,ESTABLISHED',
             '-j', 'ACCEPT'],
            
            ['iptables', '-A', 'FORWARD',
             '-i', config.target_interface,
             '-o', config.source_interface,
             '-j', 'ACCEPT']
        ]
        
        for cmd in commands:
            subprocess.run(cmd, check=True)
    
    def start_bridge(self, config: FantasmaConfig) -> bool:
        """
        Start bridge mode on Raspberry Pi
        """
        self.logger.info("Starting Raspberry Pi bridge...")
        
        try:
            # Create bridge
            subprocess.run(['brctl', 'addbr', 'br0'], check=False)
            
            # Add interfaces to bridge
            subprocess.run([
                'brctl', 'addif', 'br0',
                config.source_interface
            ], check=True)
            
            subprocess.run([
                'brctl', 'addif', 'br0',
                config.target_interface
            ], check=True)
            
            # Bring up bridge
            subprocess.run(['ip', 'link', 'set', 'br0', 'up'], check=True)
            
            self.logger.info("✓ Raspberry Pi bridge started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to start bridge: {e}")
            return False
    
    def stop_sharing(self) -> bool:
        """Stop sharing on Raspberry Pi"""
        self.logger.info("Stopping Raspberry Pi sharing...")
        
        try:
            # Kill dnsmasq and hostapd
            subprocess.run(['killall', 'dnsmasq'], check=False)
            subprocess.run(['killall', 'hostapd'], check=False)
            
            # Clear iptables
            subprocess.run(['iptables', '-t', 'nat', '-F'], check=False)
            subprocess.run(['iptables', '-F'], check=False)
            
            # Remove bridge if exists
            subprocess.run(['ip', 'link', 'set', 'br0', 'down'], check=False)
            subprocess.run(['brctl', 'delbr', 'br0'], check=False)
            
            self.logger.info("✓ Sharing stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to stop sharing: {e}")
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status"""
        # Check if hostapd or dnsmasq is running
        try:
            result = subprocess.run(
                ['pgrep', 'hostapd'],
                capture_output=True
            )
            hostapd_running = result.returncode == 0
            
            result = subprocess.run(
                ['pgrep', 'dnsmasq'],
                capture_output=True
            )
            dnsmasq_running = result.returncode == 0
            
            active = hostapd_running or dnsmasq_running
            
            return {
                'active': active,
                'platform': self.platform_name,
                'hostapd_running': hostapd_running,
                'dnsmasq_running': dnsmasq_running
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get status: {e}")
            return {
                'active': False,
                'error': str(e)
            }


# Example: Register hooks for Raspberry Pi specific actions
@on_hook('post_start')
def log_raspberry_pi_start(config):
    """Log when sharing starts on Raspberry Pi"""
    print(f"🍓 Raspberry Pi sharing started!")
    print(f"   Source: {config.source_interface}")
    print(f"   Target: {config.target_interface}")
    print(f"   Mode: {config.mode.value}")


@on_hook('post_stop')
def log_raspberry_pi_stop():
    """Log when sharing stops on Raspberry Pi"""
    print(f"🍓 Raspberry Pi sharing stopped")


def main():
    """Example usage of Raspberry Pi adapter"""
    logging.basicConfig(level=logging.INFO)
    
    print("=" * 60)
    print("Raspberry Pi Custom Adapter Example")
    print("=" * 60)
    
    # Create adapter instance
    adapter = RaspberryPiAdapter()
    
    # Create Fantasma instance with custom adapter
    fantasma = FantasmaCore(adapter)
    
    # List interfaces
    print("\n1. Detecting interfaces...")
    interfaces = fantasma.list_interfaces()
    for iface in interfaces:
        print(f"   {iface}")
    
    # Example configuration
    print("\n2. Example: Starting hotspot...")
    config = FantasmaConfig(
        source_interface="eth0",
        target_interface="wlan0",
        mode="hotspot",
        ssid="RaspberryPi_WiFi",
        password="raspberry123",
        channel=6
    )
    
    print("   (Not actually starting - run as root to test)")
    print(f"   Would start: {config.source_interface} → {config.target_interface}")
    
    print("\n3. Custom adapter registered!")
    print("   Platform:", adapter.platform_name)
    print("   Hooks: post_start, post_stop")
    
    print("\n" + "=" * 60)
    print("To use this adapter:")
    print("  1. Save this file as 'raspberry_pi_adapter.py'")
    print("  2. Import it in your main script")
    print("  3. Use it with FantasmaCore")
    print("=" * 60)


if __name__ == '__main__':
    main()
