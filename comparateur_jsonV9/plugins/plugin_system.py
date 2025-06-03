"""
Plugin system for the Fault Editor application.

This module implements a plugin system that allows extension of the application's
functionality through external plugins.
"""

import os
import sys
import importlib
import inspect
from typing import Dict, List, Any, Callable, Optional, Type

class Plugin:
    """Base class for all plugins."""

    # Plugin metadata
    name = "Base Plugin"
    version = "1.0.0"
    description = "Base plugin class"
    author = "Unknown"

    def __init__(self, app=None):
        """Initialize the plugin with a reference to the application."""
        self.app = app

    def activate(self):
        """Activate the plugin. Override in subclasses."""
        pass

    def deactivate(self):
        """Deactivate the plugin. Override in subclasses."""
        pass

    def get_settings(self):
        """Return plugin settings. Override in subclasses."""
        return {}

    def update_settings(self, settings):
        """Update plugin settings. Override in subclasses."""
        pass

class PluginManager:
    """Manages plugins for the application."""

    def __init__(self, app=None):
        """Initialize the plugin manager."""
        self.app = app
        self.plugins: Dict[str, Plugin] = {}
        self.active_plugins: Dict[str, Plugin] = {}
        self.plugin_dirs: List[str] = ["plugins"]

    def discover_plugins(self):
        """Discover available plugins in the plugin directories."""
        for plugin_dir in self.plugin_dirs:
            if not os.path.exists(plugin_dir):
                os.makedirs(plugin_dir)
                continue

            # Get Python files in the plugin directory
            try:
                for filename in os.listdir(plugin_dir):
                    if filename.endswith(".py") and not filename.startswith("__"):
                        module_name = os.path.splitext(filename)[0]
                        self._load_plugin_module(plugin_dir, module_name)
            except Exception as e:
                print(f"Error discovering plugins in {plugin_dir}: {e}")

        return self.plugins

    def _load_plugin_module(self, plugin_dir: str, module_name: str):
        """Load a plugin module and register its plugins."""
        try:
            # Prepare import path
            if plugin_dir not in sys.path:
                sys.path.insert(0, plugin_dir)

            # Import the module
            module = importlib.import_module(module_name)

            # Find plugin classes in the module
            for attr_name in dir(module):
                attr = getattr(module, attr_name)

                # Check if it's a Plugin subclass (but not Plugin itself)
                if (inspect.isclass(attr) and
                    issubclass(attr, Plugin) and
                    attr is not Plugin):

                    # Create plugin instance
                    plugin_id = f"{module_name}.{attr_name}"
                    plugin = attr(self.app)
                    self.plugins[plugin_id] = plugin
                    print(f"Registered plugin: {plugin.name} (v{plugin.version})")

        except Exception as e:
            print(f"Error loading plugin {module_name}: {e}")

    def activate_plugin(self, plugin_id: str) -> bool:
        """
        Activate a plugin.

        Args:
            plugin_id: The ID of the plugin to activate

        Returns:
            bool: True if activation was successful, False otherwise
        """
        if plugin_id not in self.plugins:
            return False

        try:
            plugin = self.plugins[plugin_id]
            plugin.activate()
            self.active_plugins[plugin_id] = plugin
            print(f"Activated plugin: {plugin.name}")
            return True
        except Exception as e:
            print(f"Error activating plugin {plugin_id}: {e}")
            return False

    def deactivate_plugin(self, plugin_id: str) -> bool:
        """
        Deactivate a plugin.

        Args:
            plugin_id: The ID of the plugin to deactivate

        Returns:
            bool: True if deactivation was successful, False otherwise
        """
        if plugin_id not in self.active_plugins:
            return False

        try:
            plugin = self.active_plugins[plugin_id]
            plugin.deactivate()
            del self.active_plugins[plugin_id]
            print(f"Deactivated plugin: {plugin.name}")
            return True
        except Exception as e:
            print(f"Error deactivating plugin {plugin_id}: {e}")
            return False

    def get_plugin_info(self, plugin_id: str) -> Dict[str, Any]:
        """
        Get information about a plugin.

        Args:
            plugin_id: The ID of the plugin

        Returns:
            Dict containing plugin metadata
        """
        if plugin_id not in self.plugins:
            return {}

        plugin = self.plugins[plugin_id]
        return {
            "id": plugin_id,
            "name": plugin.name,
            "version": plugin.version,
            "description": plugin.description,
            "author": plugin.author,
            "active": plugin_id in self.active_plugins
        }

    def get_all_plugins(self) -> List[Dict[str, Any]]:
        """
        Get information about all available plugins.

        Returns:
            List of dictionaries containing plugin metadata
        """
        return [self.get_plugin_info(plugin_id) for plugin_id in self.plugins]

    def add_plugin_directory(self, directory: str):
        """
        Add a directory to search for plugins.

        Args:
            directory: The directory path to add
        """
        if directory not in self.plugin_dirs:
            self.plugin_dirs.append(directory)

# Global plugin manager instance
plugin_manager = PluginManager()
