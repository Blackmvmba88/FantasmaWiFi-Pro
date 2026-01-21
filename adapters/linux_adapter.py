#!/usr/bin/env python3
"""
Linux Platform Adapter for FantasmaWiFi-Pro

Uses:
- hostapd: WiFi access point daemon
- dnsmasq: DHCP and DNS server
- iptables/nftables: NAT and firewall
- brctl/bridge-utils: Bridge management
- ip: Interface configuration
"""

import subprocess
import re
from typing import List, Dict, Optional
import os

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fantasma_core import (
    PlatformAdapter, NetworkInterface, ConnectionType,
    FantasmaConfig, NetworkMode
)


class LinuxAdapter(PlatformAdapter):
    """Linux-specific implementation"""

    def __init__(self):
        super().__init__()
        self.hostapd_conf = "/tmp/fantasma_hostapd.conf"
        self.dnsmasq_conf = "/tmp/fantasma_dnsmasq.conf"
        self.bridge_name = "br-fantasma"

    def detect_interfaces(self) -> List[NetworkInterface]:
        """Detect network interfaces using ip command"""
        interfaces = []
        
        try:
            # Use ip link show
            result = subprocess.run(
                ['ip', 'link', 'show'],
                capture_output=True, text=True, check=True
            )
            
            # Parse output
            for line in result.stdout.split('\n'):
                # Look for interface lines like: "2: eth0: <BROADCAST,MULTICAST,UP,LOWER_UP>"
                match = re.match(r'^\d+:\s+(\S+):\s+<(.+)>', line)
                if match:
                    iface_name = match.group(1).replace(':', '')
                    flags = match.group(2)
                    
                    # Skip loopback and virtual interfaces
                    if iface_name == 'lo' or iface_name.startswith('vir'):
                        continue
                    
                    # Determine type
                    conn_type = self._determine_interface_type(iface_name)
                    
                    # Get MAC address
                    mac = self._get_mac_address(iface_name)
                    
                    interface = NetworkInterface(
                        name=iface_name,
                        type=conn_type,
                        mac_address=mac
                    )
                    
                    # Check if interface is UP
                    interface.is_active = 'UP' in flags
                    interfaces.append(interface)
            
            self.logger.info(f"Detected {len(interfaces)} interfaces")
            return interfaces
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error detecting interfaces: {e}")
            return []

    def _determine_interface_type(self, iface_name: str) -> ConnectionType:
        """Determine interface connection type"""
        if iface_name.startswith('wl') or iface_name.startswith('wlan'):
            return ConnectionType.WIFI
        elif iface_name.startswith('eth') or iface_name.startswith('en'):
            return ConnectionType.ETHERNET
        elif iface_name.startswith('usb') or 'usb' in iface_name.lower():
            return ConnectionType.USB
        elif iface_name.startswith('bnep') or 'bt' in iface_name.lower():
            return ConnectionType.BLUETOOTH
        else:
            return ConnectionType.ETHERNET

    def _get_mac_address(self, interface: str) -> Optional[str]:
        """Get MAC address for interface"""
        try:
            result = subprocess.run(
                ['cat', f'/sys/class/net/{interface}/address'],
                capture_output=True, text=True
            )
            return result.stdout.strip()
        except:
            return None

    def start_hotspot(self, config: FantasmaConfig) -> bool:
        """
        Start hotspot mode using hostapd + dnsmasq + iptables
        
        This is the "paradise" mode for Linux as mentioned in the requirements
        """
        self.logger.info(f"Starting hotspot mode: {config.source_interface.name} -> {config.target_interface.name}")
        
        try:
            # 1. Configure target interface
            self._configure_interface(config.target_interface.name, "192.168.137.1")
            
            # 2. Setup DHCP server (dnsmasq)
            if not self._setup_dnsmasq(config):
                return False
            
            # 3. Setup WiFi AP (hostapd) if target is WiFi
            if config.target_interface.type == ConnectionType.WIFI:
                if not self._setup_hostapd(config):
                    return False
            
            # 4. Enable IP forwarding
            subprocess.run(['sudo', 'sysctl', '-w', 'net.ipv4.ip_forward=1'], check=True)
            
            # 5. Setup NAT with iptables
            if not self._setup_nat_iptables(config.source_interface.name, config.target_interface.name):
                return False
            
            self.logger.info("Hotspot mode started successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting hotspot: {e}")
            self.stop_sharing()
            return False

    def start_bridge(self, config: FantasmaConfig) -> bool:
        """
        Start bridge mode using brctl or ip link
        
        Layer 2 forwarding - no NAT, no DHCP
        """
        self.logger.info(f"Starting bridge mode: {config.source_interface.name} <-> {config.target_interface.name}")
        
        try:
            # Try brctl first (bridge-utils)
            if self._has_command('brctl'):
                return self._bridge_with_brctl(config)
            else:
                return self._bridge_with_ip(config)
                
        except Exception as e:
            self.logger.error(f"Error starting bridge: {e}")
            return False

    def _bridge_with_brctl(self, config: FantasmaConfig) -> bool:
        """Create bridge using brctl"""
        try:
            # Create bridge
            subprocess.run(['sudo', 'brctl', 'addbr', self.bridge_name], check=False)
            
            # Add interfaces to bridge
            subprocess.run(['sudo', 'brctl', 'addif', self.bridge_name, config.source_interface.name], check=True)
            subprocess.run(['sudo', 'brctl', 'addif', self.bridge_name, config.target_interface.name], check=True)
            
            # Bring bridge up
            subprocess.run(['sudo', 'ip', 'link', 'set', self.bridge_name, 'up'], check=True)
            
            self.logger.info("Bridge created with brctl")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error with brctl: {e}")
            return False

    def _bridge_with_ip(self, config: FantasmaConfig) -> bool:
        """Create bridge using ip command"""
        try:
            # Create bridge
            subprocess.run(['sudo', 'ip', 'link', 'add', 'name', self.bridge_name, 'type', 'bridge'], check=False)
            
            # Add interfaces to bridge
            subprocess.run(['sudo', 'ip', 'link', 'set', config.source_interface.name, 'master', self.bridge_name], check=True)
            subprocess.run(['sudo', 'ip', 'link', 'set', config.target_interface.name, 'master', self.bridge_name], check=True)
            
            # Bring bridge up
            subprocess.run(['sudo', 'ip', 'link', 'set', self.bridge_name, 'up'], check=True)
            
            self.logger.info("Bridge created with ip command")
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error with ip command: {e}")
            return False

    def stop_sharing(self) -> bool:
        """Stop all network sharing"""
        self.logger.info("Stopping network sharing")
        
        try:
            # Kill hostapd
            subprocess.run(['sudo', 'killall', 'hostapd'], capture_output=True, check=False)
            
            # Kill dnsmasq
            subprocess.run(['sudo', 'killall', 'dnsmasq'], capture_output=True, check=False)
            
            # Remove iptables rules
            subprocess.run(
                ['sudo', 'iptables', '-t', 'nat', '-F', 'POSTROUTING'],
                capture_output=True, check=False
            )
            subprocess.run(
                ['sudo', 'iptables', '-F', 'FORWARD'],
                capture_output=True, check=False
            )
            
            # Delete bridge
            if self._has_command('brctl'):
                subprocess.run(['sudo', 'ip', 'link', 'set', self.bridge_name, 'down'], check=False)
                subprocess.run(['sudo', 'brctl', 'delbr', self.bridge_name], capture_output=True, check=False)
            else:
                subprocess.run(['sudo', 'ip', 'link', 'delete', self.bridge_name], capture_output=True, check=False)
            
            # Disable IP forwarding
            subprocess.run(['sudo', 'sysctl', '-w', 'net.ipv4.ip_forward=0'], check=False)
            
            self.logger.info("Network sharing stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping sharing: {e}")
            return False

    def get_status(self) -> Dict[str, any]:
        """Get current sharing status"""
        status = {
            'platform': 'Linux',
            'hostapd_running': False,
            'dnsmasq_running': False,
            'bridge_active': False,
            'ip_forward_enabled': False
        }
        
        # Check hostapd
        try:
            result = subprocess.run(['pgrep', 'hostapd'], capture_output=True)
            status['hostapd_running'] = result.returncode == 0
        except:
            pass
        
        # Check dnsmasq
        try:
            result = subprocess.run(['pgrep', 'dnsmasq'], capture_output=True)
            status['dnsmasq_running'] = result.returncode == 0
        except:
            pass
        
        # Check bridge
        try:
            result = subprocess.run(['ip', 'link', 'show', self.bridge_name], capture_output=True)
            status['bridge_active'] = result.returncode == 0
        except:
            pass
        
        # Check IP forwarding
        try:
            with open('/proc/sys/net/ipv4/ip_forward', 'r') as f:
                status['ip_forward_enabled'] = f.read().strip() == '1'
        except:
            pass
        
        return status

    def is_supported(self) -> bool:
        """Check if running on Linux"""
        import platform
        return platform.system() == 'Linux'

    # Helper methods

    def _configure_interface(self, interface: str, ip_address: str):
        """Configure interface with IP address"""
        subprocess.run(['sudo', 'ip', 'addr', 'flush', 'dev', interface], check=False)
        subprocess.run(['sudo', 'ip', 'addr', 'add', f'{ip_address}/24', 'dev', interface], check=True)
        subprocess.run(['sudo', 'ip', 'link', 'set', interface, 'up'], check=True)

    def _setup_dnsmasq(self, config: FantasmaConfig) -> bool:
        """Setup dnsmasq DHCP server"""
        try:
            dnsmasq_config = f"""
interface={config.target_interface.name}
dhcp-range={config.dhcp_start},{config.dhcp_end},12h
dhcp-option=3,192.168.137.1
dhcp-option=6,8.8.8.8,8.8.4.4
"""
            with open(self.dnsmasq_conf, 'w') as f:
                f.write(dnsmasq_config)
            
            subprocess.run(
                ['sudo', 'dnsmasq', '-C', self.dnsmasq_conf, '-d'],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False
            )
            return True
        except Exception as e:
            self.logger.error(f"Error setting up dnsmasq: {e}")
            return False

    def _setup_hostapd(self, config: FantasmaConfig) -> bool:
        """Setup hostapd for WiFi AP"""
        try:
            hostapd_config = f"""
interface={config.target_interface.name}
driver=nl80211
ssid={config.ssid}
hw_mode=g
channel=7
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase={config.password}
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
"""
            with open(self.hostapd_conf, 'w') as f:
                f.write(hostapd_config)
            
            subprocess.Popen(
                ['sudo', 'hostapd', self.hostapd_conf],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except Exception as e:
            self.logger.error(f"Error setting up hostapd: {e}")
            return False

    def _setup_nat_iptables(self, source: str, target: str) -> bool:
        """Setup NAT using iptables"""
        try:
            # Enable masquerading
            subprocess.run(
                ['sudo', 'iptables', '-t', 'nat', '-A', 'POSTROUTING', '-o', source, '-j', 'MASQUERADE'],
                check=True
            )
            
            # Allow forwarding
            subprocess.run(
                ['sudo', 'iptables', '-A', 'FORWARD', '-i', source, '-o', target, '-m', 'state', 
                 '--state', 'RELATED,ESTABLISHED', '-j', 'ACCEPT'],
                check=True
            )
            subprocess.run(
                ['sudo', 'iptables', '-A', 'FORWARD', '-i', target, '-o', source, '-j', 'ACCEPT'],
                check=True
            )
            
            return True
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error setting up iptables: {e}")
            return False

    def _has_command(self, command: str) -> bool:
        """Check if command exists"""
        try:
            subprocess.run(['which', command], capture_output=True, check=True)
            return True
        except:
            return False


if __name__ == "__main__":
    # Test adapter
    import logging
    logging.basicConfig(level=logging.INFO)
    
    adapter = LinuxAdapter()
    print(f"Supported: {adapter.is_supported()}")
    print(f"\nInterfaces:")
    for iface in adapter.detect_interfaces():
        print(f"  {iface}")
    print(f"\nStatus: {adapter.get_status()}")
