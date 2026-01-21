#!/usr/bin/env python3
"""
Termux/Android Platform Adapter for FantasmaWiFi-Pro

Uses:
- svc (Android service control): WiFi tethering
- iptables/nftables: NAT and routing
- ip: Interface configuration

Note: Many Android devices have restricted bridge support (kernel limitations)
For devices without L2 bridge support, we use L3 proxy as elegant workaround
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


class TermuxAdapter(PlatformAdapter):
    """Termux/Android-specific implementation"""

    def __init__(self):
        super().__init__()
        self.tether_interface = "wlan0"  # Default Android tethering interface

    def detect_interfaces(self) -> List[NetworkInterface]:
        """Detect network interfaces using ip command"""
        interfaces = []
        
        try:
            # Use ip link show (available in Termux)
            result = subprocess.run(
                ['ip', 'link', 'show'],
                capture_output=True, text=True, check=True
            )
            
            # Parse output
            for line in result.stdout.split('\n'):
                match = re.match(r'^\d+:\s+(\S+):\s+<(.+)>', line)
                if match:
                    iface_name = match.group(1).replace(':', '')
                    flags = match.group(2)
                    
                    # Skip loopback
                    if iface_name == 'lo':
                        continue
                    
                    # Determine type
                    conn_type = self._determine_interface_type(iface_name)
                    
                    interface = NetworkInterface(
                        name=iface_name,
                        type=conn_type,
                        mac_address=self._get_mac_address(iface_name)
                    )
                    
                    interface.is_active = 'UP' in flags
                    interfaces.append(interface)
            
            self.logger.info(f"Detected {len(interfaces)} interfaces")
            return interfaces
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error detecting interfaces: {e}")
            return []

    def _determine_interface_type(self, iface_name: str) -> ConnectionType:
        """Determine interface connection type"""
        if iface_name.startswith('wlan'):
            return ConnectionType.WIFI
        elif iface_name.startswith('rmnet') or iface_name.startswith('ccmni'):
            # Mobile data interfaces
            return ConnectionType.ETHERNET
        elif iface_name.startswith('rndis') or 'usb' in iface_name:
            return ConnectionType.USB
        elif iface_name.startswith('bt-pan'):
            return ConnectionType.BLUETOOTH
        else:
            return ConnectionType.ETHERNET

    def _get_mac_address(self, interface: str) -> Optional[str]:
        """Get MAC address for interface"""
        try:
            result = subprocess.run(
                ['ip', 'link', 'show', interface],
                capture_output=True, text=True
            )
            match = re.search(r'link/ether ([0-9a-f:]+)', result.stdout)
            if match:
                return match.group(1)
        except:
            pass
        return None

    def start_hotspot(self, config: FantasmaConfig) -> bool:
        """
        Start hotspot mode using Android tethering
        
        Uses svc wifi enable + tethering configuration
        """
        self.logger.info(f"Starting hotspot mode on Android/Termux")
        
        try:
            # Method 1: Try using termux-api if available
            if self._has_termux_api():
                return self._start_hotspot_termux_api(config)
            
            # Method 2: Try direct svc commands (requires root)
            else:
                return self._start_hotspot_svc(config)
                
        except Exception as e:
            self.logger.error(f"Error starting hotspot: {e}")
            return False

    def _has_termux_api(self) -> bool:
        """Check if termux-api is available"""
        try:
            subprocess.run(['which', 'termux-wifi-enable'], capture_output=True, check=True)
            return True
        except:
            return False

    def _start_hotspot_termux_api(self, config: FantasmaConfig) -> bool:
        """Start hotspot using termux-api"""
        self.logger.info("Using termux-api for tethering")
        
        # termux-api doesn't have direct hotspot control
        # User needs to enable it manually or use root methods
        self.logger.warning("Please enable WiFi hotspot manually in Android settings:")
        self.logger.info("Settings -> Network & Internet -> Hotspot & tethering -> WiFi hotspot")
        
        if config.ssid:
            self.logger.info(f"Configure SSID: {config.ssid}")
        if config.password:
            self.logger.info(f"Configure password: {config.password}")
        
        return True

    def _start_hotspot_svc(self, config: FantasmaConfig) -> bool:
        """Start hotspot using svc commands (requires root)"""
        self.logger.info("Attempting to use svc commands (requires root)")
        
        try:
            # Enable WiFi
            subprocess.run(['su', '-c', 'svc wifi enable'], check=False)
            
            # Note: Direct tethering control via svc is limited
            # Most Android devices require using settings or root apps
            self.logger.warning("Direct tethering control requires root access")
            self.logger.info("For full automation, consider using apps like:")
            self.logger.info("- Tasker + AutoInput")
            self.logger.info("- Root-enabled tethering apps")
            
            # Setup iptables for NAT (if we get tethering working)
            if self._has_root():
                self._setup_nat_android(config.source_interface.name, self.tether_interface)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error with svc: {e}")
            return False

    def start_bridge(self, config: FantasmaConfig) -> bool:
        """
        Start bridge mode - or L3 proxy if L2 bridge not supported
        
        Many Android kernels don't support L2 bridging, so we use L3 proxy
        """
        self.logger.info(f"Starting bridge/proxy mode on Android")
        
        # Check if kernel supports bridging
        if not self._check_bridge_support():
            self.logger.warning("Kernel doesn't support L2 bridging, using L3 proxy mode")
            return self._start_l3_proxy(config)
        
        # Try actual bridge if supported
        return self._start_l2_bridge(config)

    def _check_bridge_support(self) -> bool:
        """Check if kernel supports bridging"""
        try:
            result = subprocess.run(
                ['cat', '/proc/modules'],
                capture_output=True, text=True
            )
            return 'bridge' in result.stdout
        except:
            return False

    def _start_l2_bridge(self, config: FantasmaConfig) -> bool:
        """Start L2 bridge (if supported)"""
        self.logger.info("Starting L2 bridge")
        
        try:
            # Create bridge
            subprocess.run(
                ['su', '-c', f'ip link add name br0 type bridge'],
                check=False
            )
            
            # Add interfaces
            subprocess.run(
                ['su', '-c', f'ip link set {config.source_interface.name} master br0'],
                check=True
            )
            subprocess.run(
                ['su', '-c', f'ip link set {config.target_interface.name} master br0'],
                check=True
            )
            
            # Bring up
            subprocess.run(['su', '-c', 'ip link set br0 up'], check=True)
            
            self.logger.info("L2 bridge started")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error starting L2 bridge: {e}")
            return False

    def _start_l3_proxy(self, config: FantasmaConfig) -> bool:
        """
        Start L3 proxy mode - elegant workaround for devices without bridge support
        
        This uses IP forwarding + NAT to create transparent routing
        """
        self.logger.info("Starting L3 proxy mode (elegant bridge alternative)")
        
        try:
            if not self._has_root():
                self.logger.error("L3 proxy mode requires root access")
                return False
            
            # Enable IP forwarding
            subprocess.run(
                ['su', '-c', 'echo 1 > /proc/sys/net/ipv4/ip_forward'],
                shell=True, check=True
            )
            
            # Setup NAT
            self._setup_nat_android(config.source_interface.name, config.target_interface.name)
            
            self.logger.info("L3 proxy mode started")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting L3 proxy: {e}")
            return False

    def stop_sharing(self) -> bool:
        """Stop all network sharing"""
        self.logger.info("Stopping network sharing")
        
        try:
            if self._has_root():
                # Clear iptables rules
                subprocess.run(
                    ['su', '-c', 'iptables -t nat -F'],
                    capture_output=True, check=False
                )
                subprocess.run(
                    ['su', '-c', 'iptables -F FORWARD'],
                    capture_output=True, check=False
                )
                
                # Delete bridge if exists
                subprocess.run(
                    ['su', '-c', 'ip link delete br0'],
                    capture_output=True, check=False
                )
            
            self.logger.info("Network sharing stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping sharing: {e}")
            return False

    def get_status(self) -> Dict[str, any]:
        """Get current sharing status"""
        status = {
            'platform': 'Android/Termux',
            'has_root': self._has_root(),
            'has_termux_api': self._has_termux_api(),
            'bridge_support': self._check_bridge_support()
        }
        
        return status

    def is_supported(self) -> bool:
        """Check if running on Android/Termux"""
        try:
            # Check for Android in /proc/version
            with open('/proc/version', 'r') as f:
                return 'android' in f.read().lower()
        except:
            return False

    # Helper methods

    def _has_root(self) -> bool:
        """Check if root access is available"""
        try:
            result = subprocess.run(
                ['su', '-c', 'id'],
                capture_output=True, timeout=2
            )
            return 'uid=0' in result.stdout.decode()
        except:
            return False

    def _setup_nat_android(self, source: str, target: str):
        """Setup NAT using iptables"""
        try:
            subprocess.run(
                ['su', '-c', f'iptables -t nat -A POSTROUTING -o {source} -j MASQUERADE'],
                check=True
            )
            subprocess.run(
                ['su', '-c', f'iptables -A FORWARD -i {source} -o {target} -m state --state RELATED,ESTABLISHED -j ACCEPT'],
                check=True
            )
            subprocess.run(
                ['su', '-c', f'iptables -A FORWARD -i {target} -o {source} -j ACCEPT'],
                check=True
            )
        except Exception as e:
            self.logger.error(f"Error setting up NAT: {e}")


if __name__ == "__main__":
    # Test adapter
    import logging
    logging.basicConfig(level=logging.INFO)
    
    adapter = TermuxAdapter()
    print(f"Supported: {adapter.is_supported()}")
    print(f"\nInterfaces:")
    for iface in adapter.detect_interfaces():
        print(f"  {iface}")
    print(f"\nStatus: {adapter.get_status()}")
