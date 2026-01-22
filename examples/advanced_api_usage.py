#!/usr/bin/env python3
"""
Advanced API Usage Example
Demonstrates advanced features like profiles, monitoring, and automation
"""

import requests
import time
import json
from typing import Dict, Any


class FantasmaAPIClient:
    """
    Advanced client for FantasmaWiFi-Pro REST API
    
    Features:
    - Automatic retry on failure
    - Rate limit handling
    - Profile management
    - Status monitoring
    """
    
    def __init__(self, base_url: str = "http://localhost:8080", api_key: str = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.session = requests.Session()
        
        if api_key:
            self.session.headers.update({'X-API-Key': api_key})
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            
            # Handle rate limiting
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 60))
                print(f"Rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                return self._make_request(method, endpoint, **kwargs)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            return {'error': str(e)}
    
    def get_interfaces(self):
        """Get available network interfaces"""
        return self._make_request('GET', '/api/interfaces')
    
    def get_status(self):
        """Get current sharing status"""
        return self._make_request('GET', '/api/status')
    
    def start_sharing(self, config: Dict[str, Any]):
        """Start network sharing with given configuration"""
        return self._make_request('POST', '/api/start', json=config)
    
    def stop_sharing(self):
        """Stop network sharing"""
        return self._make_request('POST', '/api/stop')
    
    def list_profiles(self):
        """List saved configuration profiles"""
        return self._make_request('GET', '/api/profiles')
    
    def save_profile(self, name: str, config: Dict[str, Any]):
        """Save a configuration profile"""
        data = {'name': name, 'config': config}
        return self._make_request('POST', '/api/profiles', json=data)
    
    def load_profile(self, name: str):
        """Load a configuration profile"""
        return self._make_request('GET', f'/api/profiles/{name}')
    
    def delete_profile(self, name: str):
        """Delete a configuration profile"""
        return self._make_request('DELETE', f'/api/profiles/{name}')
    
    def monitor_status(self, interval: int = 5, duration: int = None):
        """
        Monitor sharing status continuously
        
        Args:
            interval: Seconds between status checks
            duration: Total monitoring duration (None = forever)
        """
        start_time = time.time()
        
        print("Monitoring status (Ctrl+C to stop)...")
        print("-" * 60)
        
        try:
            while True:
                status = self.get_status()
                
                if 'error' not in status:
                    active = status.get('active', False)
                    mode = status.get('mode', 'none')
                    uptime = status.get('uptime', 0)
                    
                    timestamp = time.strftime('%H:%M:%S')
                    state = "🟢 ACTIVE" if active else "🔴 INACTIVE"
                    
                    print(f"[{timestamp}] {state} | Mode: {mode} | Uptime: {uptime}s")
                else:
                    print(f"Error: {status['error']}")
                
                # Check duration limit
                if duration and (time.time() - start_time) >= duration:
                    break
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\nMonitoring stopped")


def example_basic_usage():
    """Example: Basic API usage"""
    print("=== Basic Usage Example ===\n")
    
    # Create client
    client = FantasmaAPIClient(api_key="fwp_your_api_key_here")
    
    # Get available interfaces
    print("1. Getting interfaces...")
    result = client.get_interfaces()
    if 'interfaces' in result:
        for iface in result['interfaces']:
            print(f"   - {iface['name']} ({iface['type']})")
    
    # Start sharing
    print("\n2. Starting hotspot...")
    config = {
        "source": "en0",
        "target": "en1",
        "mode": "hotspot",
        "ssid": "MyAPIHotspot",
        "password": "SecurePass123",
        "channel": 6
    }
    
    result = client.start_sharing(config)
    print(f"   Result: {result.get('message', result)}")
    
    # Check status
    print("\n3. Checking status...")
    status = client.get_status()
    print(f"   Active: {status.get('active')}")
    print(f"   Mode: {status.get('mode')}")
    
    # Stop after 10 seconds
    print("\n4. Waiting 10 seconds...")
    time.sleep(10)
    
    print("\n5. Stopping sharing...")
    result = client.stop_sharing()
    print(f"   Result: {result.get('message', result)}")


def example_profile_management():
    """Example: Profile management"""
    print("\n=== Profile Management Example ===\n")
    
    client = FantasmaAPIClient(api_key="fwp_your_api_key_here")
    
    # Define profiles
    profiles = {
        "home_usb": {
            "source": "en0",
            "target": "usb0",
            "mode": "bridge"
        },
        "office_wifi": {
            "source": "en0",
            "target": "en1",
            "mode": "hotspot",
            "ssid": "Office_Guest",
            "password": "guest123456"
        },
        "travel_hotspot": {
            "source": "wwan0",
            "target": "wlan0",
            "mode": "hotspot",
            "ssid": "Travel_WiFi",
            "password": "travel2024"
        }
    }
    
    # Save profiles
    print("1. Saving profiles...")
    for name, config in profiles.items():
        result = client.save_profile(name, config)
        print(f"   - {name}: {result.get('message', 'Saved')}")
    
    # List profiles
    print("\n2. Listing profiles...")
    result = client.list_profiles()
    for profile in result.get('profiles', []):
        print(f"   - {profile}")
    
    # Load and use a profile
    print("\n3. Loading 'home_usb' profile...")
    profile_data = client.load_profile('home_usb')
    
    if 'profile' in profile_data:
        print("   Profile loaded successfully")
        print(f"   Config: {json.dumps(profile_data['profile'], indent=2)}")


def example_automated_switching():
    """Example: Automated profile switching based on time"""
    print("\n=== Automated Switching Example ===\n")
    
    client = FantasmaAPIClient(api_key="fwp_your_api_key_here")
    
    # Define schedule
    schedule = {
        "workday_morning": {  # 9 AM - 12 PM
            "hours": (9, 12),
            "profile": "office_wifi"
        },
        "workday_afternoon": {  # 1 PM - 5 PM
            "hours": (13, 17),
            "profile": "office_wifi"
        },
        "evening": {  # 6 PM - 11 PM
            "hours": (18, 23),
            "profile": "home_usb"
        }
    }
    
    print("Starting automated scheduler (demo mode - exits after 30 seconds)...")
    print("In production, this would run continuously")
    
    start_time = time.time()
    current_profile = None
    
    try:
        while time.time() - start_time < 30:  # Demo: run for 30 seconds
            current_hour = time.localtime().tm_hour
            
            # Find matching schedule
            target_profile = None
            for period, config in schedule.items():
                start_hour, end_hour = config['hours']
                if start_hour <= current_hour < end_hour:
                    target_profile = config['profile']
                    break
            
            # Switch profile if needed
            if target_profile and target_profile != current_profile:
                print(f"\n[{time.strftime('%H:%M:%S')}] Switching to profile: {target_profile}")
                
                # Stop current sharing
                if current_profile:
                    client.stop_sharing()
                
                # Load and start new profile
                profile_data = client.load_profile(target_profile)
                if 'profile' in profile_data:
                    client.start_sharing(profile_data['profile'])
                    current_profile = target_profile
                    print(f"   ✓ Now using {target_profile}")
            
            time.sleep(5)  # Check every 5 seconds
            
    except KeyboardInterrupt:
        print("\n\nScheduler stopped")
        if current_profile:
            print("Cleaning up...")
            client.stop_sharing()


def example_monitoring():
    """Example: Status monitoring"""
    print("\n=== Monitoring Example ===\n")
    
    client = FantasmaAPIClient(api_key="fwp_your_api_key_here")
    
    # Start sharing first
    print("Starting sharing for monitoring demo...")
    config = {
        "source": "en0",
        "target": "en1",
        "mode": "hotspot",
        "ssid": "Monitor_Test",
        "password": "test12345"
    }
    client.start_sharing(config)
    
    # Monitor for 30 seconds
    print("\nMonitoring for 30 seconds...\n")
    client.monitor_status(interval=5, duration=30)
    
    # Stop sharing
    print("\nStopping sharing...")
    client.stop_sharing()


def main():
    """Run all examples"""
    print("FantasmaWiFi-Pro Advanced API Examples")
    print("=" * 60)
    
    # Check if API is available
    try:
        response = requests.get("http://localhost:8080/api/status", timeout=2)
        if response.status_code in [200, 500]:  # 500 is ok, means server is running
            print("✓ API server is running\n")
        else:
            print("⚠ API server returned unexpected status")
            return
    except requests.exceptions.RequestException:
        print("✗ API server is not running!")
        print("\nPlease start the server first:")
        print("  ./fantasma_web.py --port 8080")
        return
    
    # Run examples (comment out the ones you don't want to run)
    try:
        example_basic_usage()
        time.sleep(2)
        
        example_profile_management()
        time.sleep(2)
        
        # Uncomment to run these examples:
        # example_automated_switching()
        # example_monitoring()
        
    except KeyboardInterrupt:
        print("\n\nExamples interrupted by user")
    
    print("\n" + "=" * 60)
    print("Examples completed!")


if __name__ == '__main__':
    main()
