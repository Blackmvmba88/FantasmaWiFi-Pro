"""
FantasmaWiFi-Pro REST API Module
Enhanced API with authentication and rate limiting
"""

from functools import wraps
from flask import request, jsonify
import time
import hashlib
import secrets
from typing import Dict, Callable
import logging

logger = logging.getLogger(__name__)


class APIAuth:
    """Simple API authentication system"""
    
    def __init__(self):
        self.api_keys: Dict[str, dict] = {}
        self.default_key = self._generate_key()
        self.api_keys[self.default_key] = {
            'name': 'default',
            'created': time.time(),
            'enabled': True
        }
        logger.info(f"Default API key generated: {self.default_key}")
    
    def _generate_key(self) -> str:
        """Generate a secure API key"""
        return f"fwp_{secrets.token_urlsafe(32)}"
    
    def create_key(self, name: str) -> str:
        """Create a new API key"""
        key = self._generate_key()
        self.api_keys[key] = {
            'name': name,
            'created': time.time(),
            'enabled': True
        }
        return key
    
    def validate_key(self, key: str) -> bool:
        """Validate an API key"""
        if key in self.api_keys:
            return self.api_keys[key].get('enabled', False)
        return False
    
    def revoke_key(self, key: str) -> bool:
        """Revoke an API key"""
        if key in self.api_keys:
            self.api_keys[key]['enabled'] = False
            return True
        return False
    
    def list_keys(self) -> list:
        """List all API keys"""
        return [
            {
                'key': key[:20] + '...',  # Mask the key
                'name': info['name'],
                'created': info['created'],
                'enabled': info['enabled']
            }
            for key, info in self.api_keys.items()
        ]


class RateLimiter:
    """Simple rate limiting system"""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.request_history: Dict[str, list] = {}
    
    def _get_client_id(self, request) -> str:
        """Get client identifier from request"""
        # Use API key if present, otherwise IP address
        api_key = request.headers.get('X-API-Key', '')
        if api_key:
            return hashlib.sha256(api_key.encode()).hexdigest()[:16]
        return request.remote_addr or 'unknown'
    
    def _cleanup_history(self, client_id: str):
        """Remove old requests from history"""
        if client_id in self.request_history:
            current_time = time.time()
            # Keep only requests from the last minute
            self.request_history[client_id] = [
                t for t in self.request_history[client_id]
                if current_time - t < 60
            ]
    
    def is_allowed(self, request) -> bool:
        """Check if request is allowed based on rate limit"""
        client_id = self._get_client_id(request)
        self._cleanup_history(client_id)
        
        if client_id not in self.request_history:
            self.request_history[client_id] = []
        
        # Check if limit exceeded
        if len(self.request_history[client_id]) >= self.requests_per_minute:
            return False
        
        # Record this request
        self.request_history[client_id].append(time.time())
        return True
    
    def get_remaining(self, request) -> int:
        """Get remaining requests for client"""
        client_id = self._get_client_id(request)
        self._cleanup_history(client_id)
        used = len(self.request_history.get(client_id, []))
        return max(0, self.requests_per_minute - used)


# Global instances
api_auth = APIAuth()
rate_limiter = RateLimiter(requests_per_minute=60)


def require_api_key(f: Callable) -> Callable:
    """Decorator to require API key authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                'error': 'API key required',
                'message': 'Include X-API-Key header with your API key'
            }), 401
        
        if not api_auth.validate_key(api_key):
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is invalid or has been revoked'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function


def rate_limit(f: Callable) -> Callable:
    """Decorator to apply rate limiting"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not rate_limiter.is_allowed(request):
            return jsonify({
                'error': 'Rate limit exceeded',
                'message': f'Maximum {rate_limiter.requests_per_minute} requests per minute',
                'retry_after': 60
            }), 429
        
        # Add rate limit headers
        response = f(*args, **kwargs)
        if isinstance(response, tuple):
            response_obj, status_code = response[0], response[1]
        else:
            response_obj, status_code = response, 200
        
        # Add headers if response is a Flask response object
        if hasattr(response_obj, 'headers'):
            response_obj.headers['X-RateLimit-Limit'] = str(rate_limiter.requests_per_minute)
            response_obj.headers['X-RateLimit-Remaining'] = str(rate_limiter.get_remaining(request))
        
        return response if isinstance(response, tuple) else (response_obj, status_code)
    
    return decorated_function


def optional_auth(f: Callable) -> Callable:
    """Decorator for optional authentication (doesn't block if no key)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if api_key and not api_auth.validate_key(api_key):
            return jsonify({
                'error': 'Invalid API key',
                'message': 'The provided API key is invalid or has been revoked'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function
