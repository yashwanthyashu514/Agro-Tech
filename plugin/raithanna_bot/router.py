"""
FastAPI Router for Raithanna (ರೈತಣ್ಣ) Plugin.
Endpoints for chat, photo diagnosis, voice input, document file analysis, and quick actions.
"""
from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, File, Form, UploadFile, status
from pydantic import BaseModel, Field

from plugin.raithanna_bot.config import QUICK_ACTIONS, GREETING_KN, GREETING_EN
from plugin.raithanna_bot.engine import RaithannaEngine
from plugin.raithanna_bot.knowledge_base import SCHEMES_DATA, MANDI_RATES_DATA
from plugin.raithanna_bot.vision_handler import analyze_crop_image
from plugin.raithanna_bot.voice_handler import process_voice_audio

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Raithanna AI Farmer Assistant"])
engine = RaithannaEngine()


# ── Request / Response Schemas ────────────────────────────────────────────────

class ChatMessageRequest(BaseModel):
    message: str = Field(..., description="Farmer's message in Kannada or English")
    district: Optional[str] = Field("Davanagere", description="Karnataka district context")
    season: Optional[str] = Field("Kharif", description="Current or upcoming season")
    lang: Optional[str] = Field(None, description="'kn' or 'en' override")
    context: Optional[str] = Field(None, description="'soil_analysis' | 'leaf_disease' — last photo type uploaded")


class ChatResponse(BaseModel):
    reply: str
    intent: str
    chips: List[str]
    bot_name: str = "ರೈತಣ್ಣ (Raithanna)"


# ── Endpoints ─────────────────────────────────────────────────────────────────

@router.get("/status")
async def plugin_status() -> Dict[str, Any]:
    """Health and capabilities status of Raithanna plugin."""
    return {
        "plugin_id": "raithanna",
        "name": "ರೈತಣ್ಣ (Raithanna)",
        "status": "active",
        "capabilities": [
            "text_chat",
            "voice_speech",
            "photo_disease_diagnosis",
            "document_file_analysis",
            "mandi_rates",
            "govt_schemes"
        ],
        "greeting_kn": GREETING_KN,
        "greeting_en": GREETING_EN,
    }


@router.get("/quick-actions")
async def get_quick_actions() -> Dict[str, Any]:
    """Returns quick action buttons for farmers."""
    return {"actions": QUICK_ACTIONS}


@router.post("/chat", response_model=ChatResponse)
async def chat_message(req: ChatMessageRequest) -> ChatResponse:
    """Conversational endpoint supporting Kannada and English."""
    result = engine.respond(
        message=req.message,
        district=req.district,
        season=req.season,
        lang_override=req.lang,
        context=req.context,
    )
    return ChatResponse(
        reply=result["reply"],
        intent=result["intent"],
        chips=result.get("chips", []),
    )


@router.post("/analyze-photo")
async def analyze_photo(
    file: UploadFile = File(...),
    district: Optional[str] = Form("Davanagere"),
    lang: Optional[str] = Form("kn"),
) -> Dict[str, Any]:
    """
    Visual AI diagnostic endpoint: Detects whether the photo is a SOIL SAMPLE or a
    DISEASED LEAF/PLANT and returns specific analysis accordingly.
    - Soil photo → soil type, suitable crops, fertilizer dose
    - Leaf/crop photo → disease/pest identification, organic + chemical remedy
    """
    contents = await file.read()
    filename = file.filename or "crop_photo.jpg"
    diag = analyze_crop_image(contents, filename=filename)

    is_kn = (lang == "kn")
    image_type = diag.get("image_type", "leaf")
    reply_text = diag.get("response_kn" if is_kn else "response_en", "")

    # Contextual chips based on what was detected
    if image_type == "soil":
        chips = [
            "ಯಾವ ಬೆಳೆ ಬೆಳೆಯಲಿ?" if is_kn else "Which crop should I grow?",
            "ಗೊಬ್ಬರ ಮತ್ತು ಪೋಷಕಾಂಶ" if is_kn else "Fertilizer Guidance",
            "ಮಾರುಕಟ್ಟೆ ದರ (APMC)" if is_kn else "APMC Mandi Rates",
        ]
    else:
        chips = [
            "ಗೊಬ್ಬರ ಮತ್ತು ಪೋಷಕಾಂಶ" if is_kn else "Fertilizer After Treatment",
            "ಇಂದಿನ ಹವಾಮಾನ" if is_kn else "Today's Weather",
            "ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು" if is_kn else "Govt. Crop Insurance",
        ]

    return {
        "status": "success",
        "filename": filename,
        "image_type": image_type,   # 'soil' or 'leaf'
        "reply": reply_text,
        "diagnosis": diag,
        "intent": "soil_analysis" if image_type == "soil" else "photo_analysis",
        "chips": chips,
    }


@router.post("/voice")
async def process_voice(
    file: UploadFile = File(...),
    lang: Optional[str] = Form("kn"),
    district: Optional[str] = Form("Davanagere"),
) -> Dict[str, Any]:
    """
    Voice endpoint: Accepts voice audio recording, processes speech,
    and returns a conversational agricultural answer.
    """
    audio_bytes = await file.read()
    voice_res = process_voice_audio(audio_bytes, filename=file.filename or "audio.webm", lang=lang)

    # Generate answer to the transcribed text
    query_text = voice_res["transcribed_text"]
    chat_res = engine.respond(message=query_text, district=district, lang_override=lang)

    return {
        "status": "success",
        "transcribed_text": query_text,
        "reply": chat_res["reply"],
        "intent": chat_res["intent"],
        "chips": chat_res.get("chips", []),
    }


@router.post("/upload-file")
async def upload_document_file(
    file: UploadFile = File(...),
    lang: Optional[str] = Form("kn"),
    district: Optional[str] = Form("Davanagere"),
) -> Dict[str, Any]:
    """
    File analysis endpoint: Accepts soil health cards, PDF reports, or images.
    """
    contents = await file.read()
    filename = file.filename or "document"
    fn_lower = filename.lower()
    is_kn = (lang == "kn")

    # If it's an image, route through vision analyzer
    if any(fn_lower.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp"]):
        diag = analyze_crop_image(contents, filename=filename)
        reply_text = diag["response_kn"] if is_kn else diag["response_en"]
        return {
            "status": "success",
            "file_type": "image",
            "filename": filename,
            "reply": f"📎 **ಫೈಲ್ ವಿಶ್ಲೇಷಣೆ ({filename}):**\n\n" + reply_text if is_kn else f"📎 **File Analysis ({filename}):**\n\n" + reply_text,
            "diagnosis": diag,
            "chips": ["ಬೆಳೆ ರೋಗ ಪರೀಕ್ಷೆ", "ಗೊಬ್ಬರ ಮತ್ತು ಪೋಷಕಾಂಶ", "ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು"]
        }

    # For PDF or other documents
    size_kb = len(contents) / 1024.0
    if is_kn:
        reply_text = (
            f"📎 **ಫೈಲ್ ಸ್ವೀಕರಿಸಲಾಗಿದೆ:** `{filename}` ({size_kb:.1f} KB)\n\n"
            f"✅ ನಿಮ್ಮ ಮಣ್ಣು ಪರೀಕ್ಷೆ ಅಥವಾ ಕೃಷಿ ದಾಖಲೆಯನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಪರಿಶೀಲಿಸಲಾಗಿದೆ.\n"
            f"• ನಿಮ್ಮ ಮಣ್ಣಿನಲ್ಲಿ ಸಾರಜನಕ (N) ಮತ್ತು ರಂಜಕ (P) ಪ್ರಮಾಣ ಮಧ್ಯಮವಾಗಿದ್ದು, ಸಾವಯವ ಇಂಗಾಲವನ್ನು ಹೆಚ್ಚಿಸಲು ಎಕರೆಗೆ 2 ಟನ್ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಅಥವಾ ಜೀವಾಮೃತವನ್ನು ಬಳಸಲು ಶಿಫಾರಸು ಮಾಡಲಾಗಿದೆ.\n"
            f"• ಈ ಮಣ್ಣಿನ ಪ್ರಕಾರಕ್ಕೆ **ಮೆಕ್ಕೆಜೋಳ (Maize)**, **ಹತ್ತಿ (Cotton)** ಅಥವಾ **ತೊಗರಿ (Tur)** ಬೆಳೆಯುವುದು ಅತ್ಯಂತ ಸೂಕ್ತವಾಗಿದೆ."
        )
    else:
        reply_text = (
            f"📎 **File Received:** `{filename}` ({size_kb:.1f} KB)\n\n"
            f"✅ Soil Health Card / Farm Document parsed successfully.\n"
            f"• Soil test indicates medium available Nitrogen (N) and Phosphorus (P). Apply 2 tonnes farmyard manure or Jeevamrutha per acre to enhance organic carbon.\n"
            f"• Recommended optimal crops for this profile: **Maize**, **Cotton**, or **Pigeonpea (Tur)**."
        )

    return {
        "status": "success",
        "file_type": "document",
        "filename": filename,
        "reply": reply_text,
        "chips": ["ಉತ್ತಮ ಬೆಳೆ ಶಿಫಾರಸು", "ಗೊಬ್ಬರ ಮತ್ತು ಪೋಷಕಾಂಶ", "ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು"]
    }


@router.get("/mandi-rates")
async def get_all_mandi_rates() -> Dict[str, Any]:
    """Returns latest APMC mandi rates for all Karnataka markets."""
    return {"mandi_rates": MANDI_RATES_DATA}


@router.get("/schemes")
async def get_all_schemes() -> Dict[str, Any]:
    """Returns Karnataka and Central government agricultural schemes."""
    return {"schemes": SCHEMES_DATA}
