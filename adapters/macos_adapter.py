#!/usr/bin/env python3
"""
macOS Platform Adapter for FantasmaWiFi-Pro

Uses:
- networksetup: interface management
- pfctl: packet filtering and NAT
- ifconfig: interface configuration
- defaults/launchctl: Internet Sharing service
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


class MacOSAdapter(PlatformAdapter):
    """macOS-specific implementation"""

    def __init__(self):
        super().__init__()
        self.sharing_plist = "/Library/Preferences/SystemConfiguration/com.apple.nat.plist"
        self.daemon_plist = "/System/Library/LaunchDaemons/com.apple.InternetSharing.plist"

    def detect_interfaces(self) -> List[NetworkInterface]:
        """Detect network interfaces using networksetup"""
        interfaces = []
        
        try:
            # Get all hardware ports
            result = subprocess.run(
                ['networksetup', '-listallhardwareports'],
                capture_output=True, text=True, check=True
            )
            
            lines = result.stdout.split('\n')
            current_type = None
            current_device = None
            
            for line in lines:
                if 'Hardware Port' in line:
                    # Extract port name
                    match = re.search(r'Hardware Port: (.+)', line)
                    if match:
                        port_name = match.group(1).strip()
                        # Determine connection type
                        if 'Wi-Fi' in port_name or 'AirPort' in port_name:
                            current_type = ConnectionType.WIFI
                        elif 'Bluetooth' in port_name:
                            current_type = ConnectionType.BLUETOOTH
                        elif 'Ethernet' in port_name:
                            current_type = ConnectionType.ETHERNET
                        elif 'USB' in port_name or 'iPhone' in port_name:
                            current_type = ConnectionType.USB
                        else:
                            current_type = ConnectionType.ETHERNET
                            
                elif 'Device' in line:
                    match = re.search(r'Device: (.+)', line)
                    if match and current_type:
                        current_device = match.group(1).strip()
                        
                        # Get MAC address
                        mac = self._get_mac_address(current_device)
                        
                        interface = NetworkInterface(
                            name=current_device,
                            type=current_type,
                            mac_address=mac
                        )
                        
                        # Check if interface is active
                        interface.is_active = self._is_interface_active(current_device)
                        interfaces.append(interface)
                        
                        current_type = None
                        current_device = None
            
            self.logger.info(f"Detected {len(interfaces)} interfaces")
            return interfaces
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error detecting interfaces: {e}")
            return []

    def _get_mac_address(self, interface: str) -> Optional[str]:
        """Get MAC address for interface"""
        try:
            result = subprocess.run(
                ['ifconfig', interface],
                capture_output=True, text=True
            )
            match = re.search(r'ether ([0-9a-f:]+)', result.stdout)
            if match:
                return match.group(1)
        except:
            pass
        return None

    def _is_interface_active(self, interface: str) -> bool:
        """Check if interface is active"""
        try:
            result = subprocess.run(
                ['ifconfig', interface],
                capture_output=True, text=True
            )
            return 'status: active' in result.stdout or 'inet ' in result.stdout
        except:
            return False

    def start_hotspot(self, config: FantasmaConfig) -> bool:
        """
        Start hotspot mode using macOS Internet Sharing
        
        For macOS, we use the built-in Internet Sharing feature
        which can be configured via defaults and launchctl
        """
        self.logger.info(f"Starting hotspot mode: {config.source_interface.name} -> {config.target_interface.name}")
        
        try:
            # Configure Internet Sharing preferences
            # Note: Full automation requires elevated privileges
            
            # Method 1: Use defaults to configure NAT
            cmd = [
                'sudo', 'defaults', 'write',
                '/Library/Preferences/SystemConfiguration/com.apple.nat',
                'NAT', '-dict-add', 'Enabled', '-int', '1'
            ]
            subprocess.run(cmd, check=False)
            
            # Method 2: For WiFi hotspot, we can use airport utility
            if config.target_interface.type == ConnectionType.WIFI and config.ssid:
                self.logger.info(f"Configuring WiFi: SSID={config.ssid}")
                # Note: Full WiFi AP configuration requires private APIs or System Preferences
                # For production, open System Preferences for user confirmation
                self._open_sharing_preferences()
            
            # Method 3: For USB/Bluetooth, configure sharing
            elif config.target_interface.type in [ConnectionType.USB, ConnectionType.BLUETOOTH]:
                self._configure_sharing(config.source_interface.name, config.target_interface.name)
            
            self.logger.info("Hotspot mode started (may require manual confirmation)")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting hotspot: {e}")
            return False

    def start_bridge(self, config: FantasmaConfig) -> bool:
        """
        Start bridge mode (Layer 2 forwarding)
        
        macOS supports bridging via bridge0 interface
        """
        self.logger.info(f"Starting bridge mode: {config.source_interface.name} <-> {config.target_interface.name}")
        
        try:
            # Create bridge interface
            # sudo ifconfig bridge0 create
            subprocess.run(
                ['sudo', 'ifconfig', 'bridge0', 'create'],
                check=False  # May already exist
            )
            
            # Add members to bridge
            subprocess.run(
                ['sudo', 'ifconfig', 'bridge0', 'addm', config.source_interface.name],
                check=True
            )
            subprocess.run(
                ['sudo', 'ifconfig', 'bridge0', 'addm', config.target_interface.name],
                check=True
            )
            
            # Bring bridge up
            subprocess.run(
                ['sudo', 'ifconfig', 'bridge0', 'up'],
                check=True
            )
            
            self.logger.info("Bridge mode started successfully")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error starting bridge: {e}")
            return False

    def stop_sharing(self) -> bool:
        """Stop all network sharing"""
        self.logger.info("Stopping network sharing")
        
        try:
            # Stop Internet Sharing daemon
            subprocess.run(
                ['sudo', 'launchctl', 'unload', '-w', self.daemon_plist],
                capture_output=True, check=False
            )
            
            # Destroy bridge if exists
            subprocess.run(
                ['sudo', 'ifconfig', 'bridge0', 'destroy'],
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
            'platform': 'macOS',
            'internet_sharing_active': False,
            'bridge_active': False
        }
        
        # Check Internet Sharing
        try:
            result = subprocess.run(
                ['launchctl', 'list'],
                capture_output=True, text=True
            )
            status['internet_sharing_active'] = 'InternetSharing' in result.stdout
        except:
            pass
        
        # Check bridge
        try:
            result = subprocess.run(
                ['ifconfig', 'bridge0'],
                capture_output=True, text=True
            )
            status['bridge_active'] = result.returncode == 0 and 'UP' in result.stdout
        except:
            pass
        
        return status

    def is_supported(self) -> bool:
        """Check if running on macOS"""
        import platform
        return platform.system() == 'Darwin'

    def _configure_sharing(self, source: str, target: str):
        """Configure Internet Sharing for specific interfaces"""
        # This requires modifying system preferences
        # Opening System Preferences for user confirmation
        self._open_sharing_preferences()

    def _open_sharing_preferences(self):
        """Open Sharing preferences pane"""
        try:
            subprocess.run([
                'open',
                'x-apple.systempreferences:com.apple.Sharing-Settings.extension?Sharing'
            ])
        except:
            pass


if __name__ == "__main__":
    # Test adapter
    import logging
    logging.basicConfig(level=logging.INFO)
    
    adapter = MacOSAdapter()
    print(f"Supported: {adapter.is_supported()}")
    print(f"\nInterfaces:")
    for iface in adapter.detect_interfaces():
        print(f"  {iface}")
    print(f"\nStatus: {adapter.get_status()}")
