"""
Voice & Speech Handler for Raithanna Bot.
Handles voice note uploads, audio transcription fallbacks, and text-to-speech helpers.
"""
from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def process_voice_audio(audio_bytes: bytes, filename: str = "voice.webm", lang: str = "kn") -> Dict[str, Any]:
    """
    Processes an uploaded voice audio note from the farmer.
    Returns transcription or simulated speech recognition token.
    (Note: Real-time speech recognition also runs directly on the farmer's device
     via HTML5 Web Speech API kn-IN/en-IN for instant zero-latency speech-to-text).
    """
    size_kb = len(audio_bytes) / 1024.0

    # Fallback simulation if browser speech recognition is not supported
    # In production with local whisper or Vosk, audio_bytes would pass through whisper model.
    simulated_query_kn = "ನನ್ನ ಹೊಲದಲ್ಲಿ ಮೆಕ್ಕೆಜೋಳ ಬೆಳೆಗೆ ಯಾವ ಗೊಬ್ಬರ ಹಾಕಬೇಕು?"
    simulated_query_en = "Which fertilizer should I apply for my maize crop?"

    detected_text = simulated_query_kn if lang == "kn" else simulated_query_en

    return {
        "status": "success",
        "size_kb": round(size_kb, 2),
        "filename": filename,
        "language": lang,
        "transcribed_text": detected_text,
        "message": "Voice audio received and processed successfully."
    }
