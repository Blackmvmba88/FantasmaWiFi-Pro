#!/usr/bin/env python3
"""
Windows Platform Adapter for FantasmaWiFi-Pro

Uses:
- netsh: Network shell for WiFi hotspot
- ICS (Internet Connection Sharing): Via WMI
- WiFiDirect: Optional advanced mode
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


class WindowsAdapter(PlatformAdapter):
    """Windows-specific implementation"""

    def __init__(self):
        super().__init__()

    def detect_interfaces(self) -> List[NetworkInterface]:
        """Detect network interfaces using netsh"""
        interfaces = []
        
        try:
            # Get all interfaces
            result = subprocess.run(
                ['netsh', 'interface', 'show', 'interface'],
                capture_output=True, text=True, check=True, encoding='utf-8'
            )
            
            # Parse output
            lines = result.stdout.split('\n')
            for line in lines[3:]:  # Skip header
                if not line.strip():
                    continue
                
                parts = line.split()
                if len(parts) >= 4:
                    admin_state = parts[0]
                    state = parts[1]
                    type_str = parts[2]
                    name = ' '.join(parts[3:])
                    
                    # Determine connection type
                    conn_type = self._determine_interface_type(name, type_str)
                    
                    interface = NetworkInterface(
                        name=name,
                        type=conn_type,
                        mac_address=None  # Could get via getmac
                    )
                    
                    interface.is_active = state.lower() == 'connected'
                    interfaces.append(interface)
            
            self.logger.info(f"Detected {len(interfaces)} interfaces")
            return interfaces
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error detecting interfaces: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error parsing interfaces: {e}")
            return []

    def _determine_interface_type(self, name: str, type_str: str) -> ConnectionType:
        """Determine interface connection type"""
        name_lower = name.lower()
        type_lower = type_str.lower()
        
        if 'wi-fi' in name_lower or 'wireless' in name_lower or 'wlan' in type_lower:
            return ConnectionType.WIFI
        elif 'bluetooth' in name_lower:
            return ConnectionType.BLUETOOTH
        elif 'ethernet' in name_lower or 'eth' in type_lower:
            return ConnectionType.ETHERNET
        else:
            return ConnectionType.ETHERNET

    def start_hotspot(self, config: FantasmaConfig) -> bool:
        """
        Start hotspot mode using netsh and ICS
        
        Windows uses Hosted Network feature for WiFi hotspot
        """
        self.logger.info(f"Starting hotspot mode: {config.source_interface.name} -> {config.target_interface.name}")
        
        try:
            if config.target_interface.type == ConnectionType.WIFI:
                return self._start_wifi_hotspot(config)
            else:
                return self._start_ics(config)
                
        except Exception as e:
            self.logger.error(f"Error starting hotspot: {e}")
            return False

    def _start_wifi_hotspot(self, config: FantasmaConfig) -> bool:
        """Start WiFi hotspot using netsh hosted network"""
        try:
            # Set up hosted network
            subprocess.run(
                ['netsh', 'wlan', 'set', 'hostednetwork', 
                 'mode=allow', f'ssid={config.ssid}', f'key={config.password}'],
                check=True
            )
            
            # Start hosted network
            subprocess.run(
                ['netsh', 'wlan', 'start', 'hostednetwork'],
                check=True
            )
            
            self.logger.info("WiFi hotspot started")
            self.logger.warning("Note: You may need to enable ICS manually in Network Connections")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Error starting WiFi hotspot: {e}")
            return False

    def _start_ics(self, config: FantasmaConfig) -> bool:
        """
        Start Internet Connection Sharing
        
        Note: Full automation requires WMI or registry manipulation
        This is a simplified version
        """
        self.logger.warning("ICS configuration on Windows requires administrator privileges")
        self.logger.info("Please enable Internet Connection Sharing manually:")
        self.logger.info(f"1. Open Network Connections (ncpa.cpl)")
        self.logger.info(f"2. Right-click on {config.source_interface.name}")
        self.logger.info(f"3. Properties -> Sharing tab")
        self.logger.info(f"4. Check 'Allow other network users...'")
        self.logger.info(f"5. Select {config.target_interface.name}")
        
        # Open network connections
        try:
            subprocess.run(['control', 'ncpa.cpl'], check=False)
        except:
            pass
        
        return True

    def start_bridge(self, config: FantasmaConfig) -> bool:
        """
        Start bridge mode
        
        Windows supports bridging but it's hidden in network settings
        """
        self.logger.info(f"Starting bridge mode: {config.source_interface.name} <-> {config.target_interface.name}")
        
        self.logger.warning("Bridge mode on Windows requires manual configuration:")
        self.logger.info("1. Open Network Connections (ncpa.cpl)")
        self.logger.info(f"2. Select {config.source_interface.name} and {config.target_interface.name}")
        self.logger.info("3. Right-click and choose 'Bridge Connections'")
        
        # Open network connections
        try:
            subprocess.run(['control', 'ncpa.cpl'], check=False)
        except:
            pass
        
        return True

    def stop_sharing(self) -> bool:
        """Stop all network sharing"""
        self.logger.info("Stopping network sharing")
        
        try:
            # Stop hosted network
            subprocess.run(
                ['netsh', 'wlan', 'stop', 'hostednetwork'],
                capture_output=True, check=False
            )
            
            self.logger.info("Network sharing stopped")
            self.logger.warning("Note: ICS may need to be disabled manually")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping sharing: {e}")
            return False

    def get_status(self) -> Dict[str, any]:
        """Get current sharing status"""
        status = {
            'platform': 'Windows',
            'hosted_network_status': 'unknown'
        }
        
        # Check hosted network status
        try:
            result = subprocess.run(
                ['netsh', 'wlan', 'show', 'hostednetwork'],
                capture_output=True, text=True, encoding='utf-8'
            )
            
            if 'Status' in result.stdout:
                for line in result.stdout.split('\n'):
                    if 'Status' in line:
                        status['hosted_network_status'] = line.split(':')[-1].strip()
                        break
        except:
            pass
        
        return status

    def is_supported(self) -> bool:
        """Check if running on Windows"""
        import platform
        return platform.system() == 'Windows'


if __name__ == "__main__":
    # Test adapter
    import logging
    logging.basicConfig(level=logging.INFO)
    
    adapter = WindowsAdapter()
    print(f"Supported: {adapter.is_supported()}")
    print(f"\nInterfaces:")
    for iface in adapter.detect_interfaces():
        print(f"  {iface}")
    print(f"\nStatus: {adapter.get_status()}")
