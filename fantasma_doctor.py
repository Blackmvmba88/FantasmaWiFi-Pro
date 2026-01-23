#!/usr/bin/env python3
"""
FantasmaWiFi-Pro Doctor - System Diagnostic Tool
Checks system capabilities, dependencies, and identifies potential issues
"""

import sys
import os
import platform
import subprocess
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class CheckStatus(Enum):
    """Status of a diagnostic check"""
    PASS = "✓"
    WARN = "⚠"
    FAIL = "✗"
    INFO = "ℹ"


@dataclass
class DiagnosticCheck:
    """Result of a single diagnostic check"""
    name: str
    status: CheckStatus
    message: str
    details: Optional[str] = None
    fix_suggestion: Optional[str] = None


@dataclass
class DiagnosticReport:
    """Complete diagnostic report"""
    platform_info: Dict[str, str]
    interfaces: List[Dict[str, str]]
    dependencies: List[DiagnosticCheck]
    capabilities: List[DiagnosticCheck]
    known_issues: List[DiagnosticCheck]
    overall_status: CheckStatus


class FantasmaDoctor:
    """System diagnostic tool for FantasmaWiFi-Pro"""
    
    # ANSI color codes
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    BOLD = '\033[1m'
    NC = '\033[0m'  # No Color
    
    def __init__(self, verbose: bool = False, no_color: bool = False):
        self.verbose = verbose
        self.no_color = no_color
        
        if no_color:
            self.RED = self.GREEN = self.YELLOW = ''
            self.BLUE = self.CYAN = self.BOLD = self.NC = ''
    
    def run_command(self, cmd: List[str], check: bool = False) -> Tuple[bool, str]:
        """Run a command and return success status and output"""
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            if check and result.returncode != 0:
                return False, result.stderr
            return True, result.stdout
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            return False, str(e)
    
    def check_command_exists(self, cmd: str) -> Tuple[bool, str]:
        """Check if a command exists and get its version"""
        # Try 'which' or 'where' depending on platform
        check_cmd = 'where' if platform.system() == 'Windows' else 'which'
        success, output = self.run_command([check_cmd, cmd])
        
        if not success:
            return False, ""
        
        # Try to get version
        for version_flag in ['--version', '-v', '-V', 'version']:
            ver_success, ver_output = self.run_command([cmd, version_flag])
            if ver_success and ver_output:
                # Extract first line which usually has version
                version = ver_output.split('\n')[0].strip()
                if version and len(version) < 100:
                    return True, version
        
        return True, "installed"
    
    def detect_platform(self) -> Dict[str, str]:
        """Detect platform information"""
        info = {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'python': platform.python_version(),
        }
        
        # Add distribution info for Linux
        if platform.system() == 'Linux':
            try:
                with open('/etc/os-release', 'r') as f:
                    for line in f:
                        if line.startswith('PRETTY_NAME='):
                            info['distribution'] = line.split('=')[1].strip().strip('"')
                            break
            except (FileNotFoundError, PermissionError, OSError):
                pass
        
        # Check if running in Termux
        if os.path.exists('/data/data/com.termux'):
            info['environment'] = 'Termux'
        
        return info
    
    def check_privileges(self) -> DiagnosticCheck:
        """Check if running with appropriate privileges"""
        is_admin = False
        
        if platform.system() == 'Windows':
            try:
                import ctypes
                is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
            except:
                pass
        else:
            is_admin = os.geteuid() == 0 if hasattr(os, 'geteuid') else False
        
        if is_admin:
            return DiagnosticCheck(
                name="Privileges",
                status=CheckStatus.PASS,
                message="Running with administrative privileges"
            )
        else:
            return DiagnosticCheck(
                name="Privileges",
                status=CheckStatus.WARN,
                message="Not running with administrative privileges",
                details="Some operations may require elevated privileges",
                fix_suggestion="Run with sudo (Linux/macOS) or as Administrator (Windows)"
            )
    
    def detect_interfaces(self) -> List[Dict[str, str]]:
        """Detect network interfaces"""
        interfaces = []
        
        try:
            # Try using 'ip' command (Linux)
            success, output = self.run_command(['ip', 'link', 'show'])
            if success:
                for line in output.split('\n'):
                    if ': ' in line and not line.startswith(' '):
                        parts = line.split(': ')
                        if len(parts) >= 2:
                            name = parts[1].split('@')[0]
                            if name and name != 'lo':
                                state = 'UP' if 'state UP' in line else 'DOWN'
                                interfaces.append({'name': name, 'status': state})
                return interfaces
        except:
            pass
        
        try:
            # Try using 'ifconfig' (macOS/BSD)
            success, output = self.run_command(['ifconfig', '-a'])
            if success:
                for line in output.split('\n'):
                    if line and not line.startswith('\t') and not line.startswith(' '):
                        parts = line.split(':')
                        if len(parts) >= 2:
                            name = parts[0].strip()
                            if name and name != 'lo0':
                                # Check next lines for status
                                status = 'UP' if 'UP' in line else 'DOWN'
                                interfaces.append({'name': name, 'status': status})
                return interfaces
        except:
            pass
        
        try:
            # Windows - try ipconfig
            success, output = self.run_command(['ipconfig', '/all'])
            if success:
                current_adapter = None
                for line in output.split('\n'):
                    if 'adapter' in line.lower() and ':' in line:
                        name = line.split(':')[0].strip()
                        current_adapter = name
                        interfaces.append({'name': name, 'status': 'UP'})
                return interfaces
        except:
            pass
        
        # Fallback: try psutil if available
        try:
            import psutil
            for iface, addrs in psutil.net_if_addrs().items():
                if iface != 'lo':
                    stats = psutil.net_if_stats().get(iface)
                    status = 'UP' if stats and stats.isup else 'DOWN'
                    interfaces.append({'name': iface, 'status': status})
            return interfaces
        except ImportError:
            pass
        
        return interfaces
    
    def check_wifi_ap_capability(self, interface: str) -> bool:
        """Check if a WiFi interface supports AP mode"""
        # This is Linux-specific using iw
        success, output = self.run_command(['iw', interface, 'info'])
        if not success:
            return False
        
        # Check supported interface modes
        success, output = self.run_command(['iw', 'phy'])
        if success and 'AP' in output:
            return True
        
        return False
    
    def check_linux_dependencies(self) -> List[DiagnosticCheck]:
        """Check Linux-specific dependencies"""
        checks = []
        
        # hostapd
        exists, version = self.check_command_exists('hostapd')
        if exists:
            checks.append(DiagnosticCheck(
                name="hostapd",
                status=CheckStatus.PASS,
                message=f"Installed: {version}"
            ))
        else:
            checks.append(DiagnosticCheck(
                name="hostapd",
                status=CheckStatus.FAIL,
                message="Not installed",
                fix_suggestion="Install: sudo apt install hostapd (Debian/Ubuntu) or sudo yum install hostapd (RedHat/Fedora)"
            ))
        
        # dnsmasq
        exists, version = self.check_command_exists('dnsmasq')
        if exists:
            checks.append(DiagnosticCheck(
                name="dnsmasq",
                status=CheckStatus.PASS,
                message=f"Installed: {version}"
            ))
        else:
            checks.append(DiagnosticCheck(
                name="dnsmasq",
                status=CheckStatus.FAIL,
                message="Not installed",
                fix_suggestion="Install: sudo apt install dnsmasq (Debian/Ubuntu) or sudo yum install dnsmasq (RedHat/Fedora)"
            ))
        
        # iptables
        exists, version = self.check_command_exists('iptables')
        if exists:
            checks.append(DiagnosticCheck(
                name="iptables",
                status=CheckStatus.PASS,
                message=f"Installed: {version}"
            ))
        else:
            checks.append(DiagnosticCheck(
                name="iptables",
                status=CheckStatus.WARN,
                message="Not installed",
                fix_suggestion="Install: sudo apt install iptables"
            ))
        
        # nftables (optional)
        exists, version = self.check_command_exists('nft')
        if exists:
            checks.append(DiagnosticCheck(
                name="nftables",
                status=CheckStatus.PASS,
                message=f"Installed: {version} (optional)"
            ))
        else:
            checks.append(DiagnosticCheck(
                name="nftables",
                status=CheckStatus.INFO,
                message="Not installed (optional alternative to iptables)"
            ))
        
        # iw (for WiFi management)
        exists, version = self.check_command_exists('iw')
        if exists:
            checks.append(DiagnosticCheck(
                name="iw",
                status=CheckStatus.PASS,
                message=f"Installed: {version}"
            ))
        else:
            checks.append(DiagnosticCheck(
                name="iw",
                status=CheckStatus.WARN,
                message="Not installed (needed for WiFi diagnostics)",
                fix_suggestion="Install: sudo apt install iw"
            ))
        
        return checks
    
    def check_macos_dependencies(self) -> List[DiagnosticCheck]:
        """Check macOS-specific dependencies"""
        checks = []
        
        # Check if Internet Sharing is available (built-in)
        checks.append(DiagnosticCheck(
            name="Internet Sharing",
            status=CheckStatus.PASS,
            message="macOS built-in feature available"
        ))
        
        # Check for networksetup command
        exists, _ = self.check_command_exists('networksetup')
        if exists:
            checks.append(DiagnosticCheck(
                name="networksetup",
                status=CheckStatus.PASS,
                message="Available (built-in)"
            ))
        
        return checks
    
    def check_windows_dependencies(self) -> List[DiagnosticCheck]:
        """Check Windows-specific dependencies"""
        checks = []
        
        # Check netsh
        exists, _ = self.check_command_exists('netsh')
        if exists:
            checks.append(DiagnosticCheck(
                name="netsh",
                status=CheckStatus.PASS,
                message="Available (built-in)"
            ))
        
        # Check if Hosted Network is supported
        success, output = self.run_command(['netsh', 'wlan', 'show', 'drivers'])
        if success and 'Hosted network supported  : Yes' in output:
            checks.append(DiagnosticCheck(
                name="Hosted Network",
                status=CheckStatus.PASS,
                message="Supported by WiFi driver"
            ))
        else:
            checks.append(DiagnosticCheck(
                name="Hosted Network",
                status=CheckStatus.FAIL,
                message="Not supported by WiFi driver",
                details="Your WiFi adapter may not support Windows Hosted Network"
            ))
        
        return checks
    
    def check_termux_dependencies(self) -> List[DiagnosticCheck]:
        """Check Termux/Android-specific dependencies"""
        checks = []
        
        # Check for iptables
        exists, version = self.check_command_exists('iptables')
        if exists:
            checks.append(DiagnosticCheck(
                name="iptables",
                status=CheckStatus.PASS,
                message=f"Installed: {version}"
            ))
        else:
            checks.append(DiagnosticCheck(
                name="iptables",
                status=CheckStatus.FAIL,
                message="Not installed",
                fix_suggestion="Install: pkg install iptables"
            ))
        
        # Check for root access
        success, _ = self.run_command(['su', '-c', 'id'])
        if success:
            checks.append(DiagnosticCheck(
                name="Root Access",
                status=CheckStatus.PASS,
                message="Available (device is rooted)"
            ))
        else:
            checks.append(DiagnosticCheck(
                name="Root Access",
                status=CheckStatus.WARN,
                message="Not available",
                details="Some features require root access on Android"
            ))
        
        return checks
    
    def check_known_issues(self, platform_name: str) -> List[DiagnosticCheck]:
        """Check for known issues on the platform"""
        issues = []
        
        if platform_name == 'Linux':
            # Check for NetworkManager
            success, output = self.run_command(['systemctl', 'is-active', 'NetworkManager'])
            if success and 'active' in output:
                issues.append(DiagnosticCheck(
                    name="NetworkManager Active",
                    status=CheckStatus.WARN,
                    message="NetworkManager may interfere with manual network configuration",
                    fix_suggestion="Temporarily stop: sudo systemctl stop NetworkManager"
                ))
            
            # Check SELinux
            if os.path.exists('/etc/selinux/config'):
                success, output = self.run_command(['getenforce'])
                if success and 'Enforcing' in output:
                    issues.append(DiagnosticCheck(
                        name="SELinux",
                        status=CheckStatus.WARN,
                        message="SELinux is enforcing",
                        details="May require policy adjustments for network operations",
                        fix_suggestion="Temporarily set permissive: sudo setenforce 0"
                    ))
        
        elif platform_name == 'Darwin':  # macOS
            # Check System Integrity Protection (informational)
            success, output = self.run_command(['csrutil', 'status'])
            if success and 'enabled' in output:
                issues.append(DiagnosticCheck(
                    name="System Integrity Protection",
                    status=CheckStatus.INFO,
                    message="SIP is enabled (normal)",
                    details="Some low-level operations may be restricted"
                ))
        
        return issues
    
    def generate_report(self) -> DiagnosticReport:
        """Generate complete diagnostic report"""
        # Platform information
        platform_info = self.detect_platform()
        platform_name = platform_info['system']
        
        # Network interfaces
        interfaces = self.detect_interfaces()
        
        # Check privileges
        priv_check = self.check_privileges()
        
        # Dependencies based on platform
        dependencies = [priv_check]
        
        if platform_name == 'Linux':
            dependencies.extend(self.check_linux_dependencies())
        elif platform_name == 'Darwin':
            dependencies.extend(self.check_macos_dependencies())
        elif platform_name == 'Windows':
            dependencies.extend(self.check_windows_dependencies())
        elif platform_info.get('environment') == 'Termux':
            dependencies.extend(self.check_termux_dependencies())
        
        # Capabilities
        capabilities = []
        
        # Check hotspot capability
        has_wifi = any('wlan' in iface['name'].lower() or 'wifi' in iface['name'].lower() 
                      for iface in interfaces)
        
        if has_wifi:
            capabilities.append(DiagnosticCheck(
                name="Hotspot Mode",
                status=CheckStatus.PASS if platform_name in ['Linux', 'Windows', 'Darwin'] else CheckStatus.WARN,
                message="Supported" if platform_name in ['Linux', 'Windows', 'Darwin'] else "Partially supported"
            ))
        else:
            capabilities.append(DiagnosticCheck(
                name="Hotspot Mode",
                status=CheckStatus.INFO,
                message="No WiFi interface detected"
            ))
        
        # Check bridge capability
        capabilities.append(DiagnosticCheck(
            name="Bridge Mode",
            status=CheckStatus.PASS,
            message="Supported on all interfaces"
        ))
        
        # Known issues
        known_issues = self.check_known_issues(platform_name)
        
        # Determine overall status
        has_critical = any(check.status == CheckStatus.FAIL for check in dependencies)
        overall_status = CheckStatus.FAIL if has_critical else CheckStatus.PASS
        
        return DiagnosticReport(
            platform_info=platform_info,
            interfaces=interfaces,
            dependencies=dependencies,
            capabilities=capabilities,
            known_issues=known_issues,
            overall_status=overall_status
        )
    
    def print_report(self, report: DiagnosticReport):
        """Print diagnostic report in human-readable format"""
        print(f"\n{self.CYAN}{self.BOLD}🔍 FantasmaWiFi-Pro System Diagnostic{self.NC}")
        print("=" * 60)
        
        # Platform information
        print(f"\n{self.BOLD}Platform Information:{self.NC}")
        print(f"  {CheckStatus.INFO.value} System: {report.platform_info['system']} {report.platform_info['release']}")
        print(f"  {CheckStatus.INFO.value} Python: {report.platform_info['python']}")
        if 'distribution' in report.platform_info:
            print(f"  {CheckStatus.INFO.value} Distribution: {report.platform_info['distribution']}")
        if 'environment' in report.platform_info:
            print(f"  {CheckStatus.INFO.value} Environment: {report.platform_info['environment']}")
        
        # Network interfaces
        print(f"\n{self.BOLD}Network Interfaces:{self.NC}")
        if report.interfaces:
            for iface in report.interfaces:
                status_color = self.GREEN if iface['status'] == 'UP' else self.RED
                status_icon = CheckStatus.PASS if iface['status'] == 'UP' else CheckStatus.WARN
                print(f"  {status_icon.value} {iface['name']} - {status_color}{iface['status']}{self.NC}")
        else:
            print(f"  {self.YELLOW}{CheckStatus.WARN.value} No interfaces detected{self.NC}")
        
        # Dependencies
        print(f"\n{self.BOLD}System Dependencies:{self.NC}")
        for check in report.dependencies:
            self._print_check(check)
        
        # Capabilities
        print(f"\n{self.BOLD}Capabilities:{self.NC}")
        for check in report.capabilities:
            self._print_check(check)
        
        # Known issues
        if report.known_issues:
            print(f"\n{self.BOLD}Known Issues:{self.NC}")
            for check in report.known_issues:
                self._print_check(check)
        
        # Overall status
        print(f"\n{self.BOLD}Overall Status:{self.NC}")
        if report.overall_status == CheckStatus.PASS:
            print(f"  {self.GREEN}{CheckStatus.PASS.value} All critical checks passed!{self.NC}")
            print(f"  {self.GREEN}Ready to use: fantasma start{self.NC}")
        else:
            print(f"  {self.RED}{CheckStatus.FAIL.value} Some critical checks failed{self.NC}")
            print(f"  {self.YELLOW}Please resolve issues above before using FantasmaWiFi-Pro{self.NC}")
        
        print()
    
    def _print_check(self, check: DiagnosticCheck):
        """Print a single diagnostic check"""
        # Determine color based on status
        if check.status == CheckStatus.PASS:
            color = self.GREEN
        elif check.status == CheckStatus.WARN:
            color = self.YELLOW
        elif check.status == CheckStatus.FAIL:
            color = self.RED
        else:
            color = self.BLUE
        
        # Print main check line
        print(f"  {color}{check.status.value}{self.NC} {check.name}: {check.message}")
        
        # Print details if in verbose mode
        if self.verbose and check.details:
            print(f"      {check.details}")
        
        # Print fix suggestion
        if check.fix_suggestion:
            print(f"      {self.CYAN}→ {check.fix_suggestion}{self.NC}")
    
    def export_json(self, report: DiagnosticReport) -> str:
        """Export report as JSON"""
        # Convert report to dict
        report_dict = {
            'platform_info': report.platform_info,
            'interfaces': report.interfaces,
            'dependencies': [
                {
                    'name': check.name,
                    'status': check.status.name,
                    'message': check.message,
                    'details': check.details,
                    'fix_suggestion': check.fix_suggestion
                }
                for check in report.dependencies
            ],
            'capabilities': [
                {
                    'name': check.name,
                    'status': check.status.name,
                    'message': check.message,
                    'details': check.details,
                    'fix_suggestion': check.fix_suggestion
                }
                for check in report.capabilities
            ],
            'known_issues': [
                {
                    'name': check.name,
                    'status': check.status.name,
                    'message': check.message,
                    'details': check.details,
                    'fix_suggestion': check.fix_suggestion
                }
                for check in report.known_issues
            ],
            'overall_status': report.overall_status.name
        }
        
        return json.dumps(report_dict, indent=2)


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='FantasmaWiFi-Pro System Diagnostic Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  fantasma doctor              # Run basic diagnostics
  fantasma doctor -v           # Run with verbose output
  fantasma doctor --json       # Output as JSON
  fantasma doctor --no-color   # Disable colored output
        """
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )
    
    parser.add_argument(
        '--no-color',
        action='store_true',
        help='Disable colored output'
    )
    
    args = parser.parse_args()
    
    # Create doctor instance
    doctor = FantasmaDoctor(verbose=args.verbose, no_color=args.no_color)
    
    # Generate report
    report = doctor.generate_report()
    
    # Output
    if args.json:
        print(doctor.export_json(report))
    else:
        doctor.print_report(report)
    
    # Exit with appropriate code
    sys.exit(0 if report.overall_status == CheckStatus.PASS else 1)


if __name__ == '__main__':
    main()
