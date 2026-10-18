"""
AgroTech Plugin Loader — Discovers and mounts plugins dynamically.
"""
from __future__ import annotations

import importlib
import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional
from fastapi import FastAPI

# API prefix — mirrors backend/app/config.py so the plugin package
# stays independent of the backend package at import time.
API_PREFIX = "/api/v1"

from plugin.base import BasePlugin

logger = logging.getLogger(__name__)

# Registered active plugins
LOADED_PLUGINS: Dict[str, BasePlugin] = {}


def load_plugins(app: FastAPI, plugins_root: Optional[Path] = None) -> List[BasePlugin]:
    """
    Scans the plugins_root directory for subdirectories containing plugins,
    instantiates them, mounts their routers onto FastAPI under /api/v1/plugin/<id>,
    and invokes their on_startup hooks.
    """
    if plugins_root is None:
        plugins_root = Path(__file__).resolve().parent

    # Ensure parent dir is in sys.path
    workspace_root = plugins_root.parent
    if str(workspace_root) not in sys.path:
        sys.path.insert(0, str(workspace_root))
    if str(plugins_root) not in sys.path:
        sys.path.insert(0, str(plugins_root))

    loaded = []
    for item in plugins_root.iterdir():
        if item.is_dir() and (item / "__init__.py").exists():
            pkg_name = f"plugin.{item.name}"
            try:
                mod = importlib.import_module(pkg_name)
                plugin_instance = getattr(mod, "plugin", None)
                if not plugin_instance:
                    # Look for any instance or subclass of BasePlugin
                    for attr_name in dir(mod):
                        val = getattr(mod, attr_name)
                        if isinstance(val, BasePlugin):
                            plugin_instance = val
                            break

                if isinstance(plugin_instance, BasePlugin):
                    prefix = f"{API_PREFIX}/plugin/{plugin_instance.plugin_id}"
                    router = plugin_instance.get_router()
                    app.include_router(router, prefix=prefix)
                    plugin_instance.on_startup(app)
                    LOADED_PLUGINS[plugin_instance.plugin_id] = plugin_instance
                    loaded.append(plugin_instance)
                    logger.info(
                        "🌾 Plugin '%s' (%s v%s) mounted at %s with capabilities: %s",
                        plugin_instance.plugin_id,
                        plugin_instance.name,
                        plugin_instance.version,
                        prefix,
                        ", ".join(plugin_instance.capabilities)
                    )
                else:
                    logger.debug("Directory '%s' did not export a BasePlugin instance.", item.name)
            except Exception as e:
                logger.error("Failed to load plugin '%s': %s", item.name, e, exc_info=True)

    return loaded


def get_loaded_plugins() -> Dict[str, BasePlugin]:
    return LOADED_PLUGINS
