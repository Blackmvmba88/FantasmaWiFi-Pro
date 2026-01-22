"""
FantasmaWiFi-Pro Plugin System
Allows registration of custom platform adapters and extensions
"""

from typing import Dict, Type, Callable, Any, Optional
import logging
from abc import ABC

from fantasma_core import PlatformAdapter

logger = logging.getLogger(__name__)


class PluginRegistry:
    """Registry for custom platform adapters and extensions"""
    
    def __init__(self):
        self._adapters: Dict[str, Type[PlatformAdapter]] = {}
        self._hooks: Dict[str, list] = {
            'pre_start': [],
            'post_start': [],
            'pre_stop': [],
            'post_stop': [],
            'on_error': []
        }
        self._custom_validators: Dict[str, Callable] = {}
        logger.info("Plugin registry initialized")
    
    def register_adapter(self, platform_name: str, adapter_class: Type[PlatformAdapter]) -> None:
        """
        Register a custom platform adapter
        
        Args:
            platform_name: Name of the platform (e.g., 'raspberry_pi', 'openwrt')
            adapter_class: Class that inherits from PlatformAdapter
        """
        if not issubclass(adapter_class, PlatformAdapter):
            raise ValueError(f"{adapter_class.__name__} must inherit from PlatformAdapter")
        
        self._adapters[platform_name] = adapter_class
        logger.info(f"Registered adapter: {platform_name} -> {adapter_class.__name__}")
    
    def get_adapter(self, platform_name: str) -> Optional[Type[PlatformAdapter]]:
        """Get a registered adapter by platform name"""
        return self._adapters.get(platform_name)
    
    def list_adapters(self) -> Dict[str, str]:
        """List all registered adapters"""
        return {
            name: adapter.__name__
            for name, adapter in self._adapters.items()
        }
    
    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """
        Register a hook callback
        
        Available hooks:
        - pre_start: Called before starting sharing
        - post_start: Called after successfully starting sharing
        - pre_stop: Called before stopping sharing
        - post_stop: Called after successfully stopping sharing
        - on_error: Called when an error occurs
        
        Args:
            hook_name: Name of the hook
            callback: Function to call when hook is triggered
        """
        if hook_name not in self._hooks:
            raise ValueError(f"Unknown hook: {hook_name}")
        
        self._hooks[hook_name].append(callback)
        logger.info(f"Registered hook: {hook_name} -> {callback.__name__}")
    
    def trigger_hook(self, hook_name: str, *args, **kwargs) -> None:
        """Trigger all callbacks for a specific hook"""
        if hook_name not in self._hooks:
            logger.warning(f"Unknown hook: {hook_name}")
            return
        
        for callback in self._hooks[hook_name]:
            try:
                callback(*args, **kwargs)
            except Exception as e:
                logger.error(f"Error in hook {hook_name} -> {callback.__name__}: {e}")
    
    def register_validator(self, name: str, validator: Callable[[Any], bool]) -> None:
        """
        Register a custom configuration validator
        
        Args:
            name: Name of the validator
            validator: Function that takes config and returns True if valid
        """
        self._custom_validators[name] = validator
        logger.info(f"Registered validator: {name}")
    
    def validate(self, name: str, value: Any) -> bool:
        """Run a registered validator"""
        validator = self._custom_validators.get(name)
        if validator:
            try:
                return validator(value)
            except Exception as e:
                logger.error(f"Validator {name} failed: {e}")
                return False
        return True


# Global plugin registry instance
plugin_registry = PluginRegistry()


# Decorator for easy adapter registration
def register_adapter(platform_name: str):
    """
    Decorator to register a custom adapter
    
    Example:
        @register_adapter('openwrt')
        class OpenWRTAdapter(PlatformAdapter):
            ...
    """
    def decorator(adapter_class: Type[PlatformAdapter]):
        plugin_registry.register_adapter(platform_name, adapter_class)
        return adapter_class
    return decorator


# Decorator for easy hook registration
def on_hook(hook_name: str):
    """
    Decorator to register a hook callback
    
    Example:
        @on_hook('post_start')
        def my_callback(config):
            print(f"Started sharing with config: {config}")
    """
    def decorator(callback: Callable):
        plugin_registry.register_hook(hook_name, callback)
        return callback
    return decorator


# Example: Custom adapter template
class CustomAdapterTemplate(PlatformAdapter):
    """
    Template for creating custom platform adapters
    
    To create a custom adapter:
    1. Inherit from PlatformAdapter
    2. Implement all required abstract methods
    3. Register with @register_adapter decorator or plugin_registry.register_adapter()
    
    Example:
        @register_adapter('my_platform')
        class MyPlatformAdapter(PlatformAdapter):
            def detect_interfaces(self):
                # Your implementation
                pass
            
            def start_hotspot(self, config):
                # Your implementation
                pass
            
            # ... implement other required methods
    """
    
    def __init__(self):
        super().__init__()
        self.platform_name = "custom"
    
    def detect_interfaces(self):
        """Detect available network interfaces on this platform"""
        raise NotImplementedError("Must implement detect_interfaces()")
    
    def start_hotspot(self, config):
        """Start hotspot mode"""
        raise NotImplementedError("Must implement start_hotspot()")
    
    def start_bridge(self, config):
        """Start bridge mode"""
        raise NotImplementedError("Must implement start_bridge()")
    
    def stop_sharing(self):
        """Stop sharing"""
        raise NotImplementedError("Must implement stop_sharing()")
    
    def get_status(self):
        """Get current status"""
        raise NotImplementedError("Must implement get_status()")
