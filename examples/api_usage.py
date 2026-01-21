#!/usr/bin/env python3
"""
Example: Using FantasmaWiFi-Pro API directly

This example shows how to use the FantasmaCore API
programmatically instead of using the CLI.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from fantasma_core import (
    FantasmaCore,
    get_platform_adapter,
    FantasmaConfig,
    NetworkMode,
    ConnectionType,
    NetworkInterface
)

# Setup logging
logging.basicConfig(level=logging.INFO)

def main():
    # Get platform adapter
    adapter = get_platform_adapter()
    core = FantasmaCore(adapter)
    
    print(f"Platform: {adapter.__class__.__name__}")
    
    # List interfaces
    print("\nAvailable interfaces:")
    interfaces = core.detect_interfaces()
    for iface in interfaces:
        print(f"  - {iface.name} ({iface.type.value}): {'UP' if iface.is_active else 'DOWN'}")
    
    # Example configuration for hotspot mode
    # Adjust interface names for your system
    if len(interfaces) >= 2:
        source = interfaces[0]
        target = interfaces[1]
        
        print(f"\nExample configuration:")
        print(f"  Source (internet): {source.name}")
        print(f"  Target (sharing): {target.name}")
        
        # Create configuration
        config = FantasmaConfig(
            mode=NetworkMode.HOTSPOT,
            source_interface=source,
            target_interface=target,
            ssid="FantasmaWiFi",
            password="SecurePassword123"
        )
        
        print(f"\nTo start sharing, uncomment the following line:")
        print(f"# core.start(config)")
        print(f"\nTo stop sharing:")
        print(f"# core.stop()")
    
    # Show status
    status = core.get_status()
    print(f"\nCurrent status:")
    for key, value in status.items():
        print(f"  {key}: {value}")

if __name__ == "__main__":
    main()
