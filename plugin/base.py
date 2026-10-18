"""
AgroTech Plugin System — Base Plugin Definition.
All plugins implement this interface to be dynamically discovered and mounted.
"""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, FastAPI


class BasePlugin(ABC):
    """Abstract base class for all AgroTech plugins."""

    plugin_id: str
    name: str
    version: str
    description: str
    capabilities: List[str]

    def __init__(self, plugin_dir: Optional[Path] = None):
        self.plugin_dir = plugin_dir or Path(__file__).parent
        self._manifest = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        manifest_path = self.plugin_dir / "plugin_manifest.json"
        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.plugin_id = data.get("id", getattr(self, "plugin_id", "plugin"))
                    self.name = data.get("name", getattr(self, "name", "Plugin"))
                    self.version = data.get("version", getattr(self, "version", "1.0.0"))
                    self.description = data.get("description", getattr(self, "description", ""))
                    self.capabilities = data.get("capabilities", getattr(self, "capabilities", []))
                    return data
            except Exception:
                pass
        return {}

    @abstractmethod
    def get_router(self) -> APIRouter:
        """Return the FastAPI router for this plugin."""
        raise NotImplementedError

    def on_startup(self, app: FastAPI) -> None:
        """Lifecycle hook executed when FastAPI starts up."""
        pass

    def on_shutdown(self, app: FastAPI) -> None:
        """Lifecycle hook executed when FastAPI shuts down."""
        pass

    def get_info(self) -> Dict[str, Any]:
        return {
            "id": getattr(self, "plugin_id", "plugin"),
            "name": getattr(self, "name", "Plugin"),
            "version": getattr(self, "version", "1.0.0"),
            "description": getattr(self, "description", ""),
            "capabilities": getattr(self, "capabilities", []),
        }
