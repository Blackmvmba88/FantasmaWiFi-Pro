#!/usr/bin/env python3
"""
FantasmaWiFi-Pro - Unified CLI Interface
Version: 7.0 "Multi-Platform Edition"

A command-line interface for cross-platform WiFi sharing
"""

import sys
import argparse
import logging
from typing import Optional

from fantasma_core import (
    FantasmaCore, get_platform_adapter,
    NetworkMode, ConnectionType, NetworkInterface, FantasmaConfig
)


class FantasmaCLI:
    """Command-line interface for FantasmaWiFi-Pro"""
    
    # ANSI color codes
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color

    def __init__(self):
        self.adapter = get_platform_adapter()
        self.core = FantasmaCore(self.adapter)

    def print_banner(self):
        """Print ASCII banner"""
        print(f"{self.PURPLE}{self.BOLD}")
        print("  ███████╗ █████╗ ███╗   ██╗████████╗ █████╗ ███████╗███╗   ███╗ █████╗")
        print("  ██╔════╝██╔══██╗████╗  ██║╚══██╔══╝██╔══██╗██╔════╝████╗ ████║██╔══██╗")
        print("  █████╗  ███████║██╔██╗ ██║   ██║   ███████║███████╗██╔████╔██║███████║")
        print("  ██╔══╝  ██╔══██║██║╚██╗██║   ██║   ██╔══██║╚════██║██║╚██╔╝██║██╔══██║")
        print("  ██║     ██║  ██║██║ ╚████║   ██║   ██║  ██║███████║██║ ╚═╝ ██║██║  ██║")
        print("  ╚═╝     ╚═╝  ╚═╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝╚══════╝╚═╝     ╚═╝╚═╝  ╚═╝")
        print(f"{self.NC}")
        print(f"{self.CYAN}          WiFi Pro - Multi-Platform Edition v7.0{self.NC}")
        print(f"{self.YELLOW}     \"Interface A consumes internet, Interface B distributes it\"{self.NC}\n")

    def list_interfaces(self):
        """List all network interfaces"""
        print(f"{self.CYAN}═══ Detecting Network Interfaces ═══{self.NC}\n")
        
        interfaces = self.core.detect_interfaces()
        
        if not interfaces:
            print(f"{self.RED}No interfaces found{self.NC}")
            return
        
        for i, iface in enumerate(interfaces, 1):
            status = f"{self.GREEN}UP{self.NC}" if iface.is_active else f"{self.RED}DOWN{self.NC}"
            print(f"{self.BOLD}{i}.{self.NC} {iface.name}")
            print(f"   Type: {iface.type.value.upper()}")
            print(f"   Status: {status}")
            if iface.mac_address:
                print(f"   MAC: {iface.mac_address}")
            print()

    def start_sharing(self, args):
        """Start network sharing"""
        print(f"{self.CYAN}═══ Starting FantasmaWiFi ═══{self.NC}\n")
        
        # Get interfaces
        interfaces = self.core.detect_interfaces()
        if not interfaces:
            print(f"{self.RED}Error: No interfaces found{self.NC}")
            return
        
        # Find source interface
        source_iface = self._find_interface(interfaces, args.source)
        if not source_iface:
            print(f"{self.RED}Error: Source interface '{args.source}' not found{self.NC}")
            return
        
        # Find target interface
        target_iface = self._find_interface(interfaces, args.target)
        if not target_iface:
            print(f"{self.RED}Error: Target interface '{args.target}' not found{self.NC}")
            return
        
        # Determine mode
        mode = NetworkMode.BRIDGE if args.bridge else NetworkMode.HOTSPOT
        
        # Create configuration
        config = FantasmaConfig(
            mode=mode,
            source_interface=source_iface,
            target_interface=target_iface,
            ssid=args.ssid,
            password=args.password
        )
        
        # Validate
        if not config.validate():
            print(f"{self.RED}Error: Invalid configuration{self.NC}")
            if mode == NetworkMode.HOTSPOT and target_iface.type == ConnectionType.WIFI:
                print(f"{self.YELLOW}WiFi hotspot requires --ssid and --password{self.NC}")
            return
        
        # Start
        print(f"Mode: {self.BOLD}{mode.value.upper()}{self.NC}")
        print(f"Source: {source_iface.name} ({source_iface.type.value})")
        print(f"Target: {target_iface.name} ({target_iface.type.value})")
        if args.ssid:
            print(f"SSID: {args.ssid}")
        print()
        
        if self.core.start(config):
            print(f"{self.GREEN}✓ FantasmaWiFi started successfully!{self.NC}")
        else:
            print(f"{self.RED}✗ Failed to start FantasmaWiFi{self.NC}")

    def stop_sharing(self):
        """Stop network sharing"""
        print(f"{self.CYAN}═══ Stopping FantasmaWiFi ═══{self.NC}\n")
        
        if self.core.stop():
            print(f"{self.GREEN}✓ FantasmaWiFi stopped{self.NC}")
        else:
            print(f"{self.RED}✗ Failed to stop FantasmaWiFi{self.NC}")

    def show_status(self):
        """Show current status"""
        print(f"{self.CYAN}═══ FantasmaWiFi Status ═══{self.NC}\n")
        
        status = self.core.get_status()
        
        print(f"Platform: {self.BOLD}{status.get('platform', 'Unknown')}{self.NC}")
        print(f"Active: {self.GREEN if self.core.is_active else self.RED}{self.core.is_active}{self.NC}")
        
        if self.core.config:
            print(f"\nCurrent Configuration:")
            print(f"  Mode: {self.core.config.mode.value}")
            print(f"  Source: {self.core.config.source_interface.name}")
            print(f"  Target: {self.core.config.target_interface.name}")
        
        print(f"\nPlatform Details:")
        for key, value in status.items():
            if key not in ['platform', 'is_active', 'config']:
                print(f"  {key}: {value}")

    def _find_interface(self, interfaces: list, name: str) -> Optional[NetworkInterface]:
        """Find interface by name"""
        for iface in interfaces:
            if iface.name == name:
                return iface
        return None


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='FantasmaWiFi-Pro - Multi-platform WiFi sharing tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List interfaces
  %(prog)s list
  
  # Run system diagnostics
  %(prog)s doctor
  
  # Start hotspot mode (macOS USB sharing)
  %(prog)s start -s en0 -t en5 --ssid MyHotspot --password MyPassword123
  
  # Start bridge mode
  %(prog)s start -s en0 -t en1 --bridge
  
  # Stop sharing
  %(prog)s stop
  
  # Show status
  %(prog)s status

Modes:
  hotspot (default): Creates own network with NAT (router mode)
  bridge:           Layer 2 forwarding, extends existing network
        """
    )
    
    parser.add_argument(
        'command',
        choices=['list', 'start', 'stop', 'status', 'doctor'],
        help='Command to execute'
    )
    
    parser.add_argument(
        '-s', '--source',
        help='Source interface (consumes internet)'
    )
    
    parser.add_argument(
        '-t', '--target',
        help='Target interface (distributes internet)'
    )
    
    parser.add_argument(
        '--bridge',
        action='store_true',
        help='Use bridge mode instead of hotspot/NAT mode'
    )
    
    parser.add_argument(
        '--ssid',
        help='WiFi SSID (required for WiFi hotspot)'
    )
    
    parser.add_argument(
        '--password',
        help='WiFi password (required for WiFi hotspot)'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create CLI
    cli = FantasmaCLI()
    
    # Print banner
    cli.print_banner()
    
    # Execute command
    try:
        if args.command == 'list':
            cli.list_interfaces()
        elif args.command == 'doctor':
            # Run doctor diagnostics
            from fantasma_doctor import FantasmaDoctor
            doctor = FantasmaDoctor(verbose=args.verbose, no_color=False)
            report = doctor.generate_report()
            doctor.print_report(report)
            sys.exit(0 if report.overall_status.name == 'PASS' else 1)
        elif args.command == 'start':
            if not args.source or not args.target:
                print(f"{cli.RED}Error: --source and --target are required for start command{cli.NC}")
                parser.print_help()
                sys.exit(1)
            cli.start_sharing(args)
        elif args.command == 'stop':
            cli.stop_sharing()
        elif args.command == 'status':
            cli.show_status()
    except KeyboardInterrupt:
        print(f"\n{cli.YELLOW}Interrupted by user{cli.NC}")
        sys.exit(0)
    except Exception as e:
        print(f"{cli.RED}Error: {e}{cli.NC}")
        if args.verbose:
            raise
        sys.exit(1)


if __name__ == '__main__':
    main()
