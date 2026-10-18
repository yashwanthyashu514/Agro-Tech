"""
AgroTech Plugin Architecture.
"""
from plugin.base import BasePlugin
from plugin.loader import load_plugins, get_loaded_plugins

__all__ = ["BasePlugin", "load_plugins", "get_loaded_plugins"]
