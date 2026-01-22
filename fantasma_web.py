#!/usr/bin/env python3
"""
FantasmaWiFi-Pro Web UI Server
Web-based control panel for managing WiFi sharing
"""

from flask import Flask, render_template, jsonify, request, Response
from flask_socketio import SocketIO, emit
import threading
import time
import logging
from typing import Dict, Any

from fantasma_core import (
    FantasmaCore,
    FantasmaConfig,
    NetworkMode,
    get_platform_adapter
)
from fantasma_api import api_auth, rate_limiter, require_api_key, rate_limit, optional_auth
from fantasma_openapi import OPENAPI_SPEC, get_openapi_html

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'fantasma-wifi-pro-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global Fantasma instance
fantasma = None
config_profiles = {}

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def initialize_fantasma():
    """Initialize Fantasma core instance"""
    global fantasma
    try:
        adapter = get_platform_adapter()
        fantasma = FantasmaCore(adapter)
        logger.info(f"Fantasma initialized with {adapter.__class__.__name__}")
    except Exception as e:
        logger.error(f"Failed to initialize Fantasma: {e}")
        fantasma = None


# Web Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


# API Documentation
@app.route('/api/docs')
def api_docs():
    """Swagger UI for API documentation"""
    return get_openapi_html()


@app.route('/api/openapi.json')
def openapi_spec():
    """OpenAPI specification"""
    return jsonify(OPENAPI_SPEC)


@app.route('/api/interfaces', methods=['GET'])
@optional_auth
@rate_limit
def get_interfaces():
    """Get available network interfaces"""
    if not fantasma:
        return jsonify({'error': 'Fantasma not initialized'}), 500
    
    try:
        interfaces = fantasma.list_interfaces()
        return jsonify({
            'interfaces': [
                {
                    'name': iface.name,
                    'type': iface.type.value,
                    'status': iface.status,
                    'ip': iface.ip_address,
                    'mac': iface.mac_address
                }
                for iface in interfaces
            ]
        })
    except Exception as e:
        logger.error(f"Error getting interfaces: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/status', methods=['GET'])
@optional_auth
def get_status():
    """Get current sharing status"""
    if not fantasma:
        return jsonify({'error': 'Fantasma not initialized'}), 500
    
    try:
        status = fantasma.get_status()
        return jsonify({
            'active': status.get('active', False),
            'mode': status.get('mode', 'none'),
            'source_interface': status.get('source_interface', ''),
            'target_interface': status.get('target_interface', ''),
            'uptime': status.get('uptime', 0),
            'platform': status.get('platform', 'unknown')
        })
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/start', methods=['POST'])
@require_api_key
@rate_limit
def start_sharing():
    """Start WiFi sharing"""
    if not fantasma:
        return jsonify({'error': 'Fantasma not initialized'}), 500
    
    try:
        data = request.json
        
        # Parse mode
        mode = NetworkMode.HOTSPOT if data.get('mode') == 'hotspot' else NetworkMode.BRIDGE
        
        # Create configuration
        config = FantasmaConfig(
            source_interface=data.get('source'),
            target_interface=data.get('target'),
            mode=mode,
            ssid=data.get('ssid', 'FantasmaWiFi'),
            password=data.get('password', ''),
            channel=int(data.get('channel', 6)),
            ip_range=data.get('ip_range', '192.168.137.0/24')
        )
        
        # Start sharing
        success = fantasma.start_sharing(config)
        
        if success:
            # Emit status update via WebSocket
            socketio.emit('status_update', {'active': True, 'mode': mode.value})
            return jsonify({'success': True, 'message': 'Sharing started successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to start sharing'}), 500
            
    except Exception as e:
        logger.error(f"Error starting sharing: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stop', methods=['POST'])
@require_api_key
@rate_limit
def stop_sharing():
    """Stop WiFi sharing"""
    if not fantasma:
        return jsonify({'error': 'Fantasma not initialized'}), 500
    
    try:
        success = fantasma.stop_sharing()
        
        if success:
            # Emit status update via WebSocket
            socketio.emit('status_update', {'active': False})
            return jsonify({'success': True, 'message': 'Sharing stopped successfully'})
        else:
            return jsonify({'success': False, 'message': 'Failed to stop sharing'}), 500
            
    except Exception as e:
        logger.error(f"Error stopping sharing: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/profiles', methods=['GET'])
@optional_auth
def get_profiles():
    """Get saved configuration profiles"""
    return jsonify({'profiles': list(config_profiles.keys())})


@app.route('/api/profiles', methods=['POST'])
@require_api_key
@rate_limit
def save_profile():
    """Save a configuration profile"""
    try:
        data = request.json
        profile_name = data.get('name')
        config_data = data.get('config')
        
        if not profile_name or not config_data:
            return jsonify({'error': 'Missing profile name or config'}), 400
        
        config_profiles[profile_name] = config_data
        return jsonify({'success': True, 'message': f'Profile "{profile_name}" saved'})
        
    except Exception as e:
        logger.error(f"Error saving profile: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/profiles/<name>', methods=['GET'])
@optional_auth
def get_profile(name):
    """Get a specific configuration profile"""
    if name in config_profiles:
        return jsonify({'profile': config_profiles[name]})
    else:
        return jsonify({'error': 'Profile not found'}), 404


@app.route('/api/profiles/<name>', methods=['DELETE'])
@require_api_key
def delete_profile(name):
    """Delete a configuration profile"""
    if name in config_profiles:
        del config_profiles[name]
        return jsonify({'success': True, 'message': f'Profile "{name}" deleted'})
    else:
        return jsonify({'error': 'Profile not found'}), 404


# WebSocket Events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected')
    emit('connected', {'message': 'Connected to Fantasma server'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected')


@socketio.on('request_status')
def handle_status_request():
    """Handle status request from client"""
    if fantasma:
        try:
            status = fantasma.get_status()
            emit('status_update', status)
        except Exception as e:
            logger.error(f"Error sending status: {e}")


# Background task for periodic status updates
def status_broadcast_task():
    """Periodically broadcast status to all connected clients"""
    while True:
        time.sleep(5)  # Update every 5 seconds
        if fantasma:
            try:
                status = fantasma.get_status()
                socketio.emit('status_update', status)
            except Exception as e:
                logger.error(f"Error broadcasting status: {e}")


def main():
    """Main entry point for web server"""
    import argparse
    
    parser = argparse.ArgumentParser(description='FantasmaWiFi-Pro Web UI')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8080, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Initialize Fantasma
    initialize_fantasma()
    
    # Start background status broadcast thread
    status_thread = threading.Thread(target=status_broadcast_task, daemon=True)
    status_thread.start()
    
    # Print startup info
    print("=" * 60)
    print("🕸️  FantasmaWiFi-Pro Web UI v7.5")
    print("=" * 60)
    print(f"Starting server on http://{args.host}:{args.port}")
    print("\nAccess the control panel at:")
    print(f"  → http://localhost:{args.port}")
    print(f"  → http://127.0.0.1:{args.port}")
    print("\nAPI Documentation:")
    print(f"  → http://localhost:{args.port}/api/docs")
    print("\nDefault API Key (save this!):")
    print(f"  → {api_auth.default_key}")
    print("\nPress Ctrl+C to stop the server")
    print("=" * 60)
    
    # Run server
    socketio.run(app, host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
