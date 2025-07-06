from typing import Dict, Any, Optional
from PyQt6.QtWidgets import QWidget

class PluginBase(QWidget):
    """Base class for all plugins"""
    
    def __init__(self, name: str, description: str, version: str):
        super().__init__()
        self.name = name
        self.description = description
        self.version = version
        self.enabled = True
        
    def get_plugin_info(self) -> Dict[str, Any]:
        """Get plugin information"""
        return {
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "enabled": self.enabled
        }
        
    def enable(self):
        """Enable the plugin"""
        self.enabled = True
        
    def disable(self):
        """Disable the plugin"""
        self.enabled = False
        
    def is_enabled(self) -> bool:
        """Check if plugin is enabled"""
        return self.enabled 