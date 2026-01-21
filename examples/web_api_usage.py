#!/usr/bin/env python3
"""
Example: Using FantasmaWiFi-Pro Web UI API Programmatically

This example demonstrates how to interact with the Web UI's REST API
programmatically for automation or integration purposes.
"""

import requests
import json
import time

# Configuration
BASE_URL = "http://localhost:8080"

def get_interfaces():
    """Get available network interfaces"""
    response = requests.get(f"{BASE_URL}/api/interfaces")
    return response.json()

def get_status():
    """Get current sharing status"""
    response = requests.get(f"{BASE_URL}/api/status")
    return response.json()

def start_hotspot(source, target, ssid, password):
    """Start WiFi sharing in hotspot mode"""
    data = {
        "mode": "hotspot",
        "source": source,
        "target": target,
        "ssid": ssid,
        "password": password,
        "channel": 6,
        "ip_range": "192.168.137.0/24"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/start",
        headers={"Content-Type": "application/json"},
        data=json.dumps(data)
    )
    return response.json()

def start_bridge(source, target):
    """Start WiFi sharing in bridge mode"""
    data = {
        "mode": "bridge",
        "source": source,
        "target": target
    }
    
    response = requests.post(
        f"{BASE_URL}/api/start",
        headers={"Content-Type": "application/json"},
        data=json.dumps(data)
    )
    return response.json()

def stop_sharing():
    """Stop WiFi sharing"""
    response = requests.post(f"{BASE_URL}/api/stop")
    return response.json()

def save_profile(name, config):
    """Save configuration profile"""
    data = {
        "name": name,
        "config": config
    }
    
    response = requests.post(
        f"{BASE_URL}/api/profiles",
        headers={"Content-Type": "application/json"},
        data=json.dumps(data)
    )
    return response.json()

def get_profiles():
    """Get all saved profiles"""
    response = requests.get(f"{BASE_URL}/api/profiles")
    return response.json()

def load_profile(name):
    """Load a specific profile"""
    response = requests.get(f"{BASE_URL}/api/profiles/{name}")
    return response.json()

def main():
    """Example usage"""
    print("=" * 60)
    print("FantasmaWiFi-Pro Web UI API Example")
    print("=" * 60)
    
    # Get available interfaces
    print("\n1. Getting available interfaces...")
    interfaces = get_interfaces()
    print(f"Found {len(interfaces.get('interfaces', []))} interfaces")
    for iface in interfaces.get('interfaces', []):
        print(f"   - {iface['name']} ({iface['type']}): {iface.get('ip', 'No IP')}")
    
    # Get current status
    print("\n2. Checking current status...")
    status = get_status()
    print(f"   Active: {status.get('active', False)}")
    print(f"   Platform: {status.get('platform', 'Unknown')}")
    
    # Example: Start hotspot (commented out to prevent accidental execution)
    # print("\n3. Starting hotspot...")
    # result = start_hotspot(
    #     source="en0",
    #     target="en1",
    #     ssid="FantasmaTest",
    #     password="TestPass123"
    # )
    # print(f"   Result: {result}")
    
    # Wait a bit
    # time.sleep(5)
    
    # Check status again
    # print("\n4. Checking status after start...")
    # status = get_status()
    # print(f"   Active: {status.get('active', False)}")
    # print(f"   Mode: {status.get('mode', 'None')}")
    
    # Save current config as profile
    # print("\n5. Saving configuration profile...")
    # config = {
    #     "mode": "hotspot",
    #     "source": "en0",
    #     "target": "en1",
    #     "ssid": "FantasmaTest",
    #     "password": "TestPass123",
    #     "channel": 6,
    #     "ip_range": "192.168.137.0/24"
    # }
    # result = save_profile("test_profile", config)
    # print(f"   Result: {result}")
    
    # Get all profiles
    print("\n3. Getting saved profiles...")
    profiles = get_profiles()
    print(f"   Profiles: {profiles.get('profiles', [])}")
    
    # Stop sharing (commented out)
    # print("\n7. Stopping sharing...")
    # result = stop_sharing()
    # print(f"   Result: {result}")
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to Web UI server")
        print("Make sure the server is running: ./start_web_ui.sh")
    except Exception as e:
        print(f"\n❌ Error: {e}")
