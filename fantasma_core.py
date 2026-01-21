#!/usr/bin/env python3
"""
FantasmaWiFi-Pro - Core Abstraction Layer
Version: 7.0 "Multi-Platform Edition"

Architecture:
    [Core Fantasma] - Platform-independent logic
          |
    [Platform Adapter] - OS-specific implementations
          |
    [Driver Layer] - System tools invocation

Abstraction: "Interface A consumes internet, Interface B distributes internet"
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional, List, Dict
import logging
import platform


class NetworkMode(Enum):
    """Network operation modes"""
    HOTSPOT = "hotspot"  # NAT/Router mode - creates own network
    BRIDGE = "bridge"    # Layer 2 forwarding - extends existing network


class ConnectionType(Enum):
    """Connection types for sharing"""
    USB = "usb"
    BLUETOOTH = "bluetooth"
    WIFI = "wifi"
    ETHERNET = "ethernet"


class NetworkInterface:
    """Represents a network interface"""
    def __init__(self, name: str, type: ConnectionType, mac_address: Optional[str] = None):
        self.name = name
        self.type = type
        self.mac_address = mac_address
        self.is_active = False

    def __repr__(self):
        return f"NetworkInterface(name={self.name}, type={self.type.value}, active={self.is_active})"


class FantasmaConfig:
    """Configuration for Fantasma operation"""
    def __init__(
        self,
        mode: NetworkMode,
        source_interface: NetworkInterface,
        target_interface: NetworkInterface,
        ssid: Optional[str] = None,
        password: Optional[str] = None,
        ip_range: str = "192.168.137.0/24",
        dhcp_start: str = "192.168.137.100",
        dhcp_end: str = "192.168.137.200"
    ):
        self.mode = mode
        self.source_interface = source_interface  # Interface consuming internet
        self.target_interface = target_interface  # Interface distributing internet
        self.ssid = ssid
        self.password = password
        self.ip_range = ip_range
        self.dhcp_start = dhcp_start
        self.dhcp_end = dhcp_end

    def validate(self) -> bool:
        """Validate configuration"""
        if self.mode == NetworkMode.HOTSPOT and self.target_interface.type == ConnectionType.WIFI:
            if not self.ssid or not self.password:
                return False
        return True


class PlatformAdapter(ABC):
    """
    Abstract base class for platform-specific implementations.
    Each platform (macOS, Linux, Windows, Termux) must implement these methods.
    """

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def detect_interfaces(self) -> List[NetworkInterface]:
        """Detect available network interfaces on the system"""
        pass

    @abstractmethod
    def start_hotspot(self, config: FantasmaConfig) -> bool:
        """
        Start hotspot/NAT mode
        - Create own network
        - Setup DHCP server
        - Configure NAT/masquerading
        - Setup firewall rules for stateful forwarding
        """
        pass

    @abstractmethod
    def start_bridge(self, config: FantasmaConfig) -> bool:
        """
        Start bridge mode (Layer 2 forwarding)
        - Create bridge interface
        - Add source and target to bridge
        - Forward Ethernet frames (MAC to MAC)
        - No NAT, no DHCP
        """
        pass

    @abstractmethod
    def stop_sharing(self) -> bool:
        """Stop all network sharing"""
        pass

    @abstractmethod
    def get_status(self) -> Dict[str, any]:
        """Get current sharing status"""
        pass

    @abstractmethod
    def is_supported(self) -> bool:
        """Check if current platform is supported"""
        pass


class FantasmaCore:
    """
    Core controller - platform-independent logic
    Delegates OS-specific operations to platform adapters
    """

    def __init__(self, adapter: PlatformAdapter):
        self.adapter = adapter
        self.config: Optional[FantasmaConfig] = None
        self.is_active = False
        self.logger = logging.getLogger("FantasmaCore")

    def detect_interfaces(self) -> List[NetworkInterface]:
        """Detect available network interfaces"""
        return self.adapter.detect_interfaces()

    def start(self, config: FantasmaConfig) -> bool:
        """
        Start network sharing with given configuration
        
        Args:
            config: FantasmaConfig object with mode and interface settings
            
        Returns:
            bool: True if started successfully
        """
        if not config.validate():
            self.logger.error("Invalid configuration")
            return False

        if self.is_active:
            self.logger.warning("Fantasma is already active. Stop it first.")
            return False

        self.config = config
        
        try:
            if config.mode == NetworkMode.HOTSPOT:
                success = self.adapter.start_hotspot(config)
            elif config.mode == NetworkMode.BRIDGE:
                success = self.adapter.start_bridge(config)
            else:
                self.logger.error(f"Unknown mode: {config.mode}")
                return False

            if success:
                self.is_active = True
                self.logger.info(f"Fantasma started in {config.mode.value} mode")
            return success

        except Exception as e:
            self.logger.error(f"Error starting Fantasma: {e}")
            return False

    def stop(self) -> bool:
        """Stop network sharing"""
        if not self.is_active:
            self.logger.warning("Fantasma is not active")
            return True

        try:
            success = self.adapter.stop_sharing()
            if success:
                self.is_active = False
                self.config = None
                self.logger.info("Fantasma stopped")
            return success
        except Exception as e:
            self.logger.error(f"Error stopping Fantasma: {e}")
            return False

    def get_status(self) -> Dict[str, any]:
        """Get current status"""
        status = self.adapter.get_status()
        status['is_active'] = self.is_active
        status['config'] = self.config
        return status


def get_platform_adapter() -> PlatformAdapter:
    """
    Factory function to get the appropriate platform adapter
    
    Returns:
        PlatformAdapter: Platform-specific adapter instance
    """
    system = platform.system().lower()
    
    if system == 'darwin':
        from adapters.macos_adapter import MacOSAdapter
        return MacOSAdapter()
    elif system == 'linux':
        # Check if running in Termux
        try:
            with open('/proc/version', 'r') as f:
                if 'android' in f.read().lower():
                    from adapters.termux_adapter import TermuxAdapter
                    return TermuxAdapter()
        except:
            pass
        from adapters.linux_adapter import LinuxAdapter
        return LinuxAdapter()
    elif system == 'windows':
        from adapters.windows_adapter import WindowsAdapter
        return WindowsAdapter()
    else:
        raise NotImplementedError(f"Platform {system} not supported")


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    adapter = get_platform_adapter()
    core = FantasmaCore(adapter)
    
    interfaces = core.detect_interfaces()
    print(f"Detected interfaces: {interfaces}")
