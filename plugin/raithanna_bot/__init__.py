"""
Raithanna (ರೈತಣ್ಣ) AI Farmer Assistant Plugin.
"""
from pathlib import Path
from fastapi import APIRouter
from plugin.base import BasePlugin
from plugin.raithanna_bot.router import router


class RaithannaPlugin(BasePlugin):
    """Raithanna AI Farmer Assistant Plugin Implementation."""

    plugin_id = "raithanna"
    name = "ರೈತಣ್ಣ (Raithanna) - AI Farmer Assistant"
    version = "1.0.0"
    description = (
        "Bilingual (Kannada & English) farmer assistant with photo plant disease analysis, "
        "voice speech interactions, document file analysis, mandi prices, and government schemes."
    )
    capabilities = [
        "chat",
        "voice_speech",
        "photo_disease_diagnosis",
        "document_file_analysis",
        "mandi_rates",
        "govt_schemes",
        "fertilizer_guide",
        "weather_advisory"
    ]

    def __init__(self):
        super().__init__(plugin_dir=Path(__file__).parent)

    def get_router(self) -> APIRouter:
        return router


# Export singleton instance for the plugin loader
plugin = RaithannaPlugin()

__all__ = ["plugin", "RaithannaPlugin"]
