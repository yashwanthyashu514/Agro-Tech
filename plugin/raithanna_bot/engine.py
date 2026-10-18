"""
Raithanna (ರೈತಣ್ಣ) AI Dialogue Engine.
Multi-modal, bilingual reasoning engine tailored for Karnataka farmers.
Supports Kannada, English, and transliterated Kanglish.
"""
from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

from plugin.raithanna_bot.knowledge_base import (
    SCHEMES_DATA, MANDI_RATES_DATA, DISEASE_REMEDIES
)


def is_kannada(text: str) -> bool:
    """Detects if text contains Kannada Unicode characters (U+0C80 to U+0CFF)."""
    return bool(re.search(r'[\u0C80-\u0CFF]', text))


def detect_language(text: str) -> str:
    """Detects 'kn' (Kannada), 'kanglish' (Transliterated), or 'en' (English)."""
    if is_kannada(text):
        return "kn"
    kanglish_words = [
        "jola", "bele", "enu", "yava", "neeru", "gobara", "hulu", "batti",
        "bhatta", "ragi", "adike", "mandi", "male", "bima", "kisan", "yojana",
        "tari", "kushki", "nanna", "holadalli", "namaskara", "raitha"
    ]
    lower = text.lower()
    if any(re.search(r'\b' + re.escape(w) + r'\b', lower) for w in kanglish_words):
        return "kanglish"
    return "en"


class RaithannaEngine:
    """Core conversational AI engine for Raithanna."""

    def __init__(self):
        self.name_kn = "ರೈತಣ್ಣ"
        self.name_en = "Raithanna"

    def respond(
        self,
        message: str,
        district: Optional[str] = "Davanagere",
        season: Optional[str] = "Kharif",
        lang_override: Optional[str] = None,
        context: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Generates a comprehensive response to a farmer's message.
        context: 'soil_analysis' | 'leaf_disease' | None — tracks what was just uploaded.
        """
        clean_text = message.strip()
        detected_lang = lang_override or detect_language(clean_text)
        is_kn = (detected_lang in ("kn", "kanglish"))
        lower = clean_text.lower()
        # Normalize whitespace (handles double spaces like 'which type of  soil ')
        norm_text = " ".join(lower.split())

        # ── 0. Context-aware follow-up (after photo upload) ───────────────────
        if context == "soil_analysis" and any(w in norm_text for w in [
            "type", "which", "what", "mannu", "enu", "yava", "crop", "grow",
            "ಯಾವ", "ಯಾವು", "ಮಣ್ಣು", "ಮಣ್ಣಿನ", "ಬೆಳೆ"
        ]):
            return self._handle_soil_query(district, is_kn)

        if context == "leaf_disease" and any(w in norm_text for w in [
            "disease", "what", "which", "identify", "hulu", "roga", "enu", "remedy",
            "spray", "cure", "medicine", "do", "suggest",
            "ಯಾವ", "ರೋಗ", "ಏನು", "ಕೀಟ", "ಔಷಧ", "ಪರಿಹಾರ", "ಸಿಂಪಡಣೆ"
        ]):
            return self._handle_disease(norm_text, is_kn)

        # ── 1. Intent: Government Schemes (ಯೋಜನೆಗಳು / ಸಬ್ಸಿಡಿ) ───────────────
        if any(w in norm_text for w in [
            "scheme", "yojana", "subsidy", "pm kisan", "pm-kisan", "raitha siri",
            "krishi bhagya", "fasal bima", "insurance", "ganga kalyana", "ಸಬ್ಸಿಡಿ",
            "ಯೋಜನೆ", "ಕಿಸಾನ್", "ಭಾಗ್ಯ", "ವಿಮೆ", "ಸಹಾಯಧನ"
        ]):
            return self._handle_schemes(is_kn)

        # ── 2. Intent: Mandi & Market Prices (ಮಾರುಕಟ್ಟೆ ದರ) ───────────────────
        if any(w in norm_text for w in [
            "mandi", "price", "rate", "apmc", "market", "dar", "bele bele",
            "ಮಾರುಕಟ್ಟೆ", "ದರ", "ರೇಟ್", "ಎಪಿಎಂಸಿ", "ಕ್ವಿಂಟಾಲ್"
        ]):
            return self._handle_mandi(district, is_kn)

        # ── 3. Intent: Disease, Pest & Symptoms (ರೋಗ / ಕೀಟ / ಔಷಧಿ / ಸಿಂಪಡಣೆ) ─────
        if any(w in norm_text for w in [
            "disease", "pest", "worm", "insect", "yellow", "spot", "blight", "rot",
            "blast", "armyworm", "hulu", "roga", "kide", "chukke", "haladi",
            "remedy", "remedies", "spray", "cure", "treatment", "medicine", "sick",
            "deseased", "diseased", "fungus", "bacterial", "infection",
            "ರೋಗ", "ಹುಳು", "ಕೀಟ", "ಎಲೆ", "ಹಳದಿ", "ಚುಕ್ಕೆ", "ಅಂಗಮಾರಿ", "ಕತ್ತರಿಸುವ",
            "ರೋಗ ಹೇಳು", "ರೋಗ ಏನು", "ಯಾವ ರೋಗ", "ಔಷಧ", "ಪರಿಹಾರ", "ಸಿಂಪಡಿಸು"
        ]):
            return self._handle_disease(norm_text, is_kn)

        # ── 4. Intent: Soil Type & Testing Query (ಮಣ್ಣಿನ ಪ್ರಕಾರ / ಪರೀಕ್ಷೆ) ──────────
        has_soil_word = any(w in norm_text for w in ["soil", "mannu", "mitti", "ಮಣ್ಣು", "ಮಣ್ಣಿನ"])
        is_soil_asking = any(w in norm_text for w in [
            "type", "which", "what", "kind", "report", "test", "health", "sample",
            "tell", "check", "info", "red", "black", "sandy", "clay", "laterite",
            "kempu", "kappu", "is this", "it is", "ಇದು", "ಯಾವ", "ಪ್ರಕಾರ", "ಹೇಳು", "ಗುಣ", "ಪರೀಕ್ಷೆ"
        ])
        if (has_soil_word and is_soil_asking) or norm_text in ["soil", "mannu", "ಮಣ್ಣು", "which type of soil", "what type of soil", "type of soil", "red soil", "black soil", "it is red soil", "hey it is red soil"]:
            return self._handle_soil_query(district, is_kn, query=norm_text)

        # ── 4b. Intent: Fertilizer & Nutrition (ಗೊಬ್ಬರ / ಪೋಷಕಾಂಶ) ─────────────
        if any(w in norm_text for w in [
            "fertilizer", "urea", "dap", "potash", "npk", "manure", "jeevamrutha",
            "compost", "gobara", "poshakansha", "ಗೊಬ್ಬರ", "ಯೂರಿಯಾ", "ಪೋಷಕಾಂಶ",
            "ಜೀವಾಮೃತ", "ಡಿಎಪಿ"
        ]):
            return self._handle_fertilizer(is_kn)

        # ── 5. Intent: Weather & Rain (ಹವಾಮಾನ / ಮಳೆ) ─────────────────────────
        if any(w in norm_text for w in [
            "weather", "rain", "forecast", "climate", "monsoon", "temperature",
            "male", "havamana", "bisilu", "sheeta", "ಮಳೆ", "ಹವಾಮಾನ", "ಮುನ್ಸೂಚನೆ", "ಉಷ್ಣಾಂಶ"
        ]):
            return self._handle_weather(district, season, is_kn)

        # ── 6. Intent: Crop Choice & Profitability (ಯಾವ ಬೆಳೆ / ಲಾಭ) ──────────
        if any(w in norm_text for w in [
            "crop", "grow", "recommend", "profit", "best crop", "easy", "sow",
            "bele", "yava bele", "labha", "sutta", "ಬೆಳೆ", "ಯಾವ ಬೆಳೆ", "ಲಾಭ", "ಶಿಫಾರಸು"
        ]):
            return self._handle_crop_advice(district, season, is_kn)

        # ── 7. Greetings (ನಮಸ್ಕಾರ / Hello - strict match to avoid false triggers) ─
        pure_greetings = ["hi", "hello", "hey", "namaskara", "namaste", "raithanna", "ಹಲೋ", "ನಮಸ್ಕಾರ", "ನಮಸ್ತೆ", "ರೈತಣ್ಣ"]
        tokens = norm_text.split()
        if len(tokens) <= 3 and any(tok in pure_greetings for tok in tokens):
            return self._handle_greeting(district, is_kn)

        # ── 7b. If Gemini is available, pass conversational follow-up to Gemini Chat ──
        try:
            from plugin.raithanna_bot.gemini_service import is_gemini_available, chat_with_gemini
            if is_gemini_available():
                gem_res = chat_with_gemini(message=clean_text, district=district or "Davanagere", season=season or "Kharif", lang="kn" if is_kn else "en")
                if gem_res.get("status") == "success":
                    return {
                        "intent": "gemini_chat",
                        "reply": gem_res["reply"],
                        "chips": gem_res.get("chips", []),
                    }
        except Exception as e:
            logger.warning("Gemini chat fallback error: %s", e)

        # ── 8. Default Agricultural Guidance ─────────────────────────────────
        return self._handle_default(clean_text, district, is_kn)

    # ── Handlers ─────────────────────────────────────────────────────────────

    def _handle_schemes(self, is_kn: bool) -> Dict[str, Any]:
        if is_kn:
            lines = [
                "🏛️ **ಕರ್ನಾಟಕ ರೈತರಿಗೆ ಸಿಗುವ ಪ್ರಮುಖ ಸರ್ಕಾರಿ ಸಬ್ಸಿಡಿ ಮತ್ತು ಯೋಜನೆಗಳು:**\n",
            ]
            for s in SCHEMES_DATA[:4]:
                lines.append(f"📌 **{s['name_kn']}**")
                lines.append(f"• ವಿವರ: {s['benefits_kn']}")
                lines.append(f"• ಅರ್ಜಿ ಪೋರ್ಟಲ್: `{s['portal']}`\n")
            lines.append("💡 **ಸಲಹೆ:** ನಿಮ್ಮ FRUITS ID ಲಿಂಕ್ ಆಗಿದೆಯೇ ಎಂದು ಪರಿಶೀಲಿಸಿಕೊಳ್ಳಿ. ಗ್ರಾಮ ಒನ್ ಅಥವಾ ರೈತ ಸಂಪರ್ಕ ಕೇಂದ್ರದಲ್ಲಿ ಸುಲಭವಾಗಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಬಹುದು.")
            text = "\n".join(lines)
        else:
            lines = [
                "🏛️ **Key Government Schemes & Subsidies for Karnataka Farmers:**\n",
            ]
            for s in SCHEMES_DATA[:4]:
                lines.append(f"📌 **{s['name_en']}**")
                lines.append(f"• Benefits: {s['benefits_en']}")
                lines.append(f"• Portal: `{s['portal']}`\n")
            lines.append("💡 **Tip:** Ensure your land records are seeded with Karnataka FRUITS ID to receive direct DBT benefits without delay.")
            text = "\n".join(lines)

        return {
            "intent": "govt_schemes",
            "reply": text,
            "chips": ["ಇಂದಿನ ಹವಾಮಾನ", "ಬೆಳೆ ರೋಗ ಪರೀಕ್ಷೆ", "ಮಾರುಕಟ್ಟೆ ದರ (APMC)"]
        }

    def _handle_mandi(self, district: Optional[str], is_kn: bool) -> Dict[str, Any]:
        target_dist = district or "Davanagere"
        matched_dist = None
        for k in MANDI_RATES_DATA.keys():
            if target_dist.lower() in k.lower() or k.lower() in target_dist.lower():
                matched_dist = k
                break
        if not matched_dist:
            matched_dist = "Davanagere"

        items = MANDI_RATES_DATA[matched_dist]
        if is_kn:
            lines = [f"💰 **{matched_dist} ಎಪಿಎಂಸಿ ಇಂದಿನ ಪ್ರಮುಖ ಬೆಳೆಗಳ ಮಾರುಕಟ್ಟೆ ದರ (Quintal Rate):**\n"]
            for it in items:
                lines.append(f"• **{it['crop']}** ({it['variety']}): ₹{it['modal']} (ಕನಿಷ್ಠ: ₹{it['min']} – ಗರಿಷ್ಠ: ₹{it['max']})")
            lines.append("\n📈 **ಮಾರುಕಟ್ಟೆ ಸಲಹೆ:** ಹತ್ತಿ ಹಾಗೂ ಮೆಕ್ಕೆಜೋಳಕ್ಕೆ ಉತ್ತಮ ಧಾರಣೆ ಇದೆ. ಮಳೆ ತೇವಾಂಶ 12% ಕ್ಕಿಂತ ಕಡಿಮೆ ಇರುವಾಗ ಮಾರಾಟ ಮಾಡಿದರೆ ಹೆಚ್ಚಿನ ದರ ಸಿಗುತ್ತದೆ.")
        else:
            lines = [f"💰 **Latest APMC Mandi Rates for {matched_dist} Market (₹ / Quintal):**\n"]
            for it in items:
                lines.append(f"• **{it['crop']}** ({it['variety']}): Modal ₹{it['modal']} (Min: ₹{it['min']} – Max: ₹{it['max']})")
            lines.append("\n📈 **Market Tip:** Moisture level should be under 12% for maize and grains to fetch maximum market price without mandi deductions.")

        return {
            "intent": "mandi_rates",
            "reply": "\n".join(lines),
            "chips": ["ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು", "ಬೆಳೆ ರೋಗ ಪರೀಕ್ಷೆ", "ಗೊಬ್ಬರ ಮತ್ತು ಪೋಷಕಾಂಶ"]
        }

    def _handle_soil_query(self, district: Optional[str], is_kn: bool, query: Optional[str] = None) -> Dict[str, Any]:
        """Handles a text-only soil type question with specialized answers for Red Soil, Black Soil, or District breakdown."""
        dist = district or "Davanagere"
        q_lower = (query or "").lower()

        # ── Case A: Farmer specifies or asks about Red Soil (ಕೆಂಪು ಮಣ್ಣು) ─────────
        if any(w in q_lower for w in ["red", "kempu", "ಕೆಂಪು"]):
            if is_kn:
                reply = (
                    "🔴 **ಹೌದು ರೈತ ಬಂಧುವೇ! ನಿಮ್ಮ ಹೊಲದ ಮಣ್ಣು ಕೆಂಪು ಮಣ್ಣು (Red Laterite / Sandy Loam Soil):**\n\n"
                    "🧪 **ಮಣ್ಣಿನ ಮುಖ್ಯ ಲಕ್ಷಣಗಳು:**\n"
                    "• ಶಿಲೆಗಳ ನೈಸರ್ಗಿಕ ಸವೆತದಿಂದ ರೂಪುಗೊಂಡ ಕಬ್ಬಿಣ ಮತ್ತು ಅಲ್ಯೂಮಿನಿಯಂ ಸಮೃದ್ಧ ಮಣ್ಣು.\n"
                    "• pH ಮಟ್ಟ: 5.5 ರಿಂದ 6.8 (ಸ್ವಲ್ಪ ಆಮ್ಲೀಯದಿಂದ ತಟಸ್ಥ).\n"
                    "• ಹಗುರವಾದ ವಿನ್ಯಾಸ, ನೀರು ಸರಾಗವಾಗಿ ಬಸಿದು ಹೋಗುವ (Good Drainage) ಗುಣ ಹೊಂದಿದೆ.\n\n"
                    "✅ **ಕೆಂಪು ಮಣ್ಣಿಗೆ ಅತ್ಯಂತ ಸೂಕ್ತವಾದ ಬೆಳೆಗಳು:**\n"
                    "1. **ರಾಗಿ (Ragi / Finger Millet):** ಕರ್ನಾಟಕದ ಅತ್ಯುತ್ತಮ ಪೋಷಕಾಂಶ ಬೆಳೆ.\n"
                    "2. **ಶೇಂಗಾ / ಕಡಲೆಕಾಯಿ (Groundnut):** ಮಣ್ಣು ಹಗುರವಾಗಿರುವುದರಿಂದ ಕಾಯಿ ಕಟ್ಟಲು ಅತ್ಯುತ್ತಮ.\n"
                    "3. **ಟೊಮೆಟೊ, ಮೆಣಸಿನಕಾಯಿ ಮತ್ತು ತರಕಾರಿಗಳು:** ನೀರಾವರಿ ಸೌಲಭ್ಯವಿದ್ದರೆ ಭರ್ಜರಿ ಇಳುವರಿ.\n"
                    "4. **ತೋಟಗಾರಿಕೆ ಬೆಳೆಗಳು:** ಮಾವು, ಅಡಿಕೆ ಮತ್ತು ಬಾಳೆ ತೋಟಗಳಿಗೆ ಸೂಕ್ತ.\n\n"
                    "💡 **ಪೋಷಕಾಂಶ ಶಿಫಾರಸು:** ಕೆಂಪು ಮಣ್ಣಿನಲ್ಲಿ ರಂಜಕದ (Phosphorus) ಕೊರತೆ ಇರುತ್ತದೆ. "
                    "ಡಿಎಪಿ ಬದಲು ಸಿಂಗಲ್ ಸೂಪರ್ ಫಾಸ್ಫೇಟ್ (SSP) ಬಳಸಿ. ಎಕರೆಗೆ 2 ಟನ್ ಕೊಟ್ಟಿಗೆ ಗೊಬ್ಬರ ಮತ್ತು ಮಣ್ಣು ಆಮ್ಲೀಯವಾಗಿದ್ದರೆ 150-200 ಕೆ.ಜಿ ಕೃಷಿ ಸುಣ್ಣ (Agricultural Lime) ಹಾಕಿ."
                )
            else:
                reply = (
                    "🔴 **Yes, Farmer Friend! Your field soil is Red Soil (Red Laterite / Sandy Loam Soil):**\n\n"
                    "🧪 **Key Soil Characteristics:**\n"
                    "• Formed by ancient rock weathering, naturally rich in iron oxides giving it the vibrant reddish-brown color.\n"
                    "• pH Range: 5.5 to 6.8 (Slightly acidic to neutral).\n"
                    "• Well-drained, light texture, does not hold stagnant water around roots.\n\n"
                    "✅ **Top Recommended Crops for Red Soil in Karnataka:**\n"
                    "1. **Ragi (Finger Millet):** Highest yielding and staple Karnataka millets.\n"
                    "2. **Groundnut (Peanut):** Loose sandy loam allows great pod development.\n"
                    "3. **Tomato, Chilli & Vegetables:** Excellent response with drip irrigation.\n"
                    "4. **Horticulture:** Mango, Arecanut, and Banana flourish with proper manure.\n\n"
                    "💡 **Fertilizer & Soil Management:** Red soils often fix Phosphorus. "
                    "Use Single Super Phosphate (SSP) instead of DAP for better P availability. Apply 2 tonnes FYM/compost per acre and 150-200 kg agricultural lime if soil is acidic."
                )
            return {
                "intent": "soil_info",
                "reply": reply,
                "chips": ["ಯಾವ ಬೆಳೆ ಬೆಳೆಯಲಿ?", "ಗೊಬ್ಬರ ಮತ್ತು ಪೋಷಕಾಂಶ", "ಮಾರುಕಟ್ಟೆ ದರ (APMC)"] if is_kn else ["Which crop should I grow?", "Fertilizer Guidance", "APMC Mandi Rates"]
            }

        # ── Case B: Farmer specifies Black Soil (ಕಪ್ಪು ಮಣ್ಣು) ─────────────────────
        if any(w in q_lower for w in ["black", "kappu", "ಕಪ್ಪು"]):
            from plugin.raithanna_bot.vision_handler import SOIL_COLOR_PROFILES
            info = SOIL_COLOR_PROFILES["Black cotton soil (ಕಪ್ಪು ಮಣ್ಣು)"]
            return {
                "intent": "soil_info",
                "reply": info["desc_kn"] if is_kn else info["desc_en"],
                "chips": ["ಯಾವ ಬೆಳೆ ಬೆಳೆಯಲಿ?", "ಗೊಬ್ಬರ ಮತ್ತು ಪೋಷಕಾಂಶ", "ಮಾರುಕಟ್ಟೆ ದರ (APMC)"] if is_kn else ["Which crop should I grow?", "Fertilizer Guidance", "APMC Mandi Rates"]
            }

        # ── Case C: General District Soil Profile ────────────────────────────────
        if is_kn:
            reply = (
                f"🌍 **{dist} ಜಿಲ್ಲೆಯ ಮಣ್ಣಿನ ಮಾಹಿತಿ ಮತ್ತು ವಿಶ್ಲೇಷಣೆ:**\n\n"
                f"📍 **{dist} ಜಿಲ್ಲೆಯಲ್ಲಿ ಮುಖ್ಯವಾಗಿ ಕಂಡುಬರುವ ಮಣ್ಣುಗಳು:**\n"
                f"• 🖤 **ಕಪ್ಪು ಹತ್ತಿ ಮಣ್ಣು (Black Cotton Soil):** ಹರಿಹರ, ದಾವಣಗೆರೆ ಮತ್ತು ಹೊನ್ನಾಳಿ ತಾಲೂಕುಗಳಲ್ಲಿ ಹೆಚ್ಚಾಗಿದೆ. "
                f"ನೀರು ಹಿಡಿದಿಡುವ ಶಕ್ತಿ ಹೆಚ್ಚು. **ಮೆಕ್ಕೆಜೋಳ, ಹತ್ತಿ, ಕಡಲೆ ಮತ್ತು ತೊಗರಿ** ಬೆಳೆಗೆ ಅತ್ಯುತ್ತಮ.\n"
                f"• 🔴 **ಕೆಂಪು ಮರಳು ಮಿಶ್ರಿತ ಲೋಮ್ ಮಣ್ಣು (Red Sandy Loam):** ಚನ್ನಗಿರಿ ಮತ್ತು ಜಗಳೂರು ತಾಲೂಕುಗಳಲ್ಲಿ ಕಂಡುಬರುತ್ತದೆ. "
                f"**ರಾಗಿ, ಶೇಂಗಾ ಮತ್ತು ಅಡಿಕೆ** ತೋಟಗಳಿಗೆ ಸೂಕ್ತ.\n\n"
                f"📷 **ನಿಮ್ಮ ಹೊಲದ ನಿಖರ ಮಣ್ಣಿನ ಪರೀಕ್ಷೆಗಾಗಿ:**\n"
                f"ನಿಮ್ಮ ಕೈಯಲ್ಲಿ ಮಣ್ಣಿನ ಮಾದರಿ ಹಿಡಿದು ಕೆಳಗಿನ **ಕ್ಯಾಮರಾ (📷)** ಬಟನ್ ಒತ್ತಿ ಫೋಟೋ ಕಳುಹಿಸಿ! \n"
                f"ನಾನು ತಕ್ಷಣ ಮಣ್ಣಿನ ಪ್ರಕಾರ, pH ಗುಣ ಮತ್ತು ಶಿಫಾರಸು ಗೊಬ್ಬರದ ಪ್ರಮಾಣವನ್ನು ಹೇಳುತ್ತೇನೆ."
            )
        else:
            reply = (
                f"🌍 **Soil Profile & Analysis for {dist} District:**\n\n"
                f"📍 **Dominant Soil Types in {dist}:**\n"
                f"• 🖤 **Black Cotton Soil (Vertisol):** Widely distributed across Harihara, Davanagere, and Honnali taluks. "
                f"High water-holding capacity, optimal for **Maize, Cotton, Chickpea (Bengal gram), and Pigeonpea**.\n"
                f"• 🔴 **Red Sandy Loam:** Prevalent in Channagiri and Jagalur taluks. "
                f"Good drainage, ideal for **Ragi (Finger Millet), Groundnut, and Arecanut**.\n\n"
                f"📷 **To Test Your Exact Field Sample:**\n"
                f"Click the **Camera (📷)** button below and upload a clear photo of your field soil! \n"
                f"I will instantly classify the soil type, estimate pH, and recommend the best fertilizer dosage."
            )
        return {
            "intent": "soil_info",
            "reply": reply,
            "chips": ["📷 ಮಣ್ಣಿನ ಫೋಟೋ ಕಳುಹಿಸಿ", "ಯಾವ ಬೆಳೆ ಬೆಳೆಯಲಿ?", "ಗೊಬ್ಬರ ಮತ್ತು ಪೋಷಕಾಂಶ"]
        }

    def _handle_disease(self, query: str, is_kn: bool) -> Dict[str, Any]:
        key = "yellow_leaf_disease"
        if any(w in query for w in ["jola", "maize", "armyworm", "hulu", "ಸೈನಿಕ", "ಕತ್ತರಿಸುವ"]):
            key = "fall_armyworm"
        elif any(w in query for w in ["rice", "paddy", "blast", "bhatta", "ಕತ್ತರಿ", "ಬೆಂಕಿ"]):
            key = "rice_blast"
        elif any(w in query for w in ["cotton", "bollworm", "batti", "ಗುಲಾಬಿ"]):
            key = "cotton_bollworm"
        elif any(w in query for w in ["pomegranate", "dalimbe", "blight", "ದಾಳಿಂಬೆ", "ಅಂಗಮಾರಿ"]):
            key = "pomegranate_blight"

        diag = DISEASE_REMEDIES[key]
        if is_kn:
            reply = (
                f"🔬 **ರೋಗ/ಕೀಟ ಮಾಹಿತಿ:** {diag['name_kn']}\n\n"
                f"⚠️ **ಮುಖ್ಯ ಲಕ್ಷಣಗಳು:** {diag['symptoms_kn']}\n\n"
                f"🌿 **ನೈಸರ್ಗಿಕ / ಸಾವಯವ ಚಿಕಿತ್ಸೆ:**\n{diag['remedy_organic_kn']}\n\n"
                f"🧪 **ಶಿಫಾರಸು ಮಾಡಿದ ರಾಸಾಯನಿಕ ಸಿಂಪರಣೆ:**\n{diag['remedy_chemical_kn']}\n\n"
                f"📷 **ಸಲಹೆ:** ನಿಮ್ಮ ಬೆಳೆಯ ಎಲೆಯ ಫೋಟೋವನ್ನು ಕೆಳಗಿನ ಕ್ಯಾಮರಾ (Photo) ಬಟನ್ ಒತ್ತಿ ಕಳುಹಿಸಿದರೆ ನಾನು ನಿಖರವಾಗಿ ಪರೀಕ್ಷಿಸಿ ಹೇಳಬಲ್ಲೆ!"
            )
        else:
            reply = (
                f"🔬 **Pest/Disease Diagnosis:** {diag['name_en']}\n\n"
                f"⚠️ **Key Symptoms:** {diag['symptoms_en']}\n\n"
                f"🌿 **Natural & Organic Remedy:**\n{diag['remedy_organic_en']}\n\n"
                f"🧪 **Recommended Chemical Spray:**\n{diag['remedy_chemical_en']}\n\n"
                f"📷 **Pro Tip:** You can also click the Camera / Photo button below to upload a clear leaf photo for automatic visual AI diagnosis!"
            )

        return {
            "intent": "crop_disease",
            "reply": reply,
            "chips": ["ಗೊಬ್ಬರ ಮತ್ತು ಪೋಷಕಾಂಶ", "ಇಂದಿನ ಹವಾಮಾನ", "ಮಾರುಕಟ್ಟೆ ದರ (APMC)"]
        }

    def _handle_fertilizer(self, is_kn: bool) -> Dict[str, Any]:
        if is_kn:
            reply = (
                "🧪 **ಪ್ರಮುಖ ಬೆಳೆಗಳಿಗೆ ವೈಜ್ಞಾನಿಕ ಗೊಬ್ಬರ ನಿರ್ವಹಣೆ (ಎಕರೆಗೆ):**\n\n"
                "🌽 **ಮೆಕ್ಕೆಜೋಳ (Maize):**\n"
                "• ಬಿತ್ತನೆ ವೇಳೆ: 1 ಬ್ಯಾಗ್ ಡಿಎಪಿ (DAP) + 20 ಕೆ.ಜಿ ಪೊಟ್ಯಾಷ್ (MOP) + 10 ಕೆ.ಜಿ ಜಿಂಕ್ ಸಲ್ಫೇಟ್.\n"
                "• 30 ದಿನಗಳ ನಂತರ (ಮೊಣಕಾಲು ಎತ್ತರ): 1 ಬ್ಯಾಗ್ ಯೂರಿಯಾ ಮೇಲುಗೊಬ್ಬರವಾಗಿ ಕೊಡಿ.\n"
                "• 45 ದಿನಗಳ ನಂತರ (ತೆನೆ ಬರುವ ಮುನ್ನ): ಅರ್ಧ ಬ್ಯಾಗ್ ಯೂರಿಯಾ ಕೊಡಿ.\n\n"
                "🌸 **ಹತ್ತಿ (Cotton):**\n"
                "• ಆರಂಭದಲ್ಲಿ: 1 ಬ್ಯಾಗ್ 20:20:0:13 ಅಥವಾ 15:15:15.\n"
                "• ಹೂ ಮೊಗ್ಗು ಮತ್ತು ಕಾಯಿ ಕಟ್ಟುವಾಗ: 19:19:19 ನೀರಿನಲ್ಲಿ ಕರಗುವ ಗೊಬ್ಬರ (5g/L) 2 ಬಾರಿ ಸಿಂಪಡಿಸಿ.\n\n"
                "🌿 **ಸಾವಯವ ಬಲವರ್ಧನೆ:** 200 ಲೀಟರ್ ನೀರಿಗೆ 10 ಕೆ.ಜಿ ದೇಸಿ ಹಸುವಿನ ಸಗಣಿ + 10 ಲೀಟರ್ ಗೋಮೂತ್ರ + 2 ಕೆ.ಜಿ ಬೆಲ್ಲ + 2 ಕೆ.ಜಿ ಕಡಲೆ ಹಿಟ್ಟು ಬೆರೆಸಿ ತಯಾರಿಸಿದ **ಜೀವಾಮೃತ**ವನ್ನು ತಿಂಗಳಿಗೊಮ್ಮೆ ಹಾಯಿಸಿ."
            )
        else:
            reply = (
                "🧪 **Scientific Fertilizer Application Guide (Per Acre):**\n\n"
                "🌽 **Maize (Corn):**\n"
                "• At Sowing (Basal): 1 bag DAP (50kg) + 20 kg Potash (MOP) + 10 kg Zinc Sulphate.\n"
                "• At 30 Days (Knee-high stage): 1 bag Urea as top dressing.\n"
                "• At 45 Days (Tasseling stage): 0.5 bag Urea.\n\n"
                "🌸 **Cotton:**\n"
                "• Basal: 1 bag complex fertilizer (20:20:0:13 or 17:17:17).\n"
                "• Flowering/Boll stage: Foliar spray of water-soluble 19:19:19 (5g/L) or Boron (1g/L).\n\n"
                "🌿 **Organic Boost:** Apply 200L Jeevamrutha per acre monthly to boost soil microbiology and nutrient uptake."
            )

        return {
            "intent": "fertilizer_guide",
            "reply": reply,
            "chips": ["ಬೆಳೆ ರೋಗ ಪರೀಕ್ಷೆ", "ಉತ್ತಮ ಬೆಳೆ ಶಿಫಾರಸು", "ಇಂದಿನ ಹವಾಮಾನ"]
        }

    def _handle_weather(self, district: Optional[str], season: Optional[str], is_kn: bool) -> Dict[str, Any]:
        dist = district or "Davanagere"
        seas = season or "Kharif"
        if is_kn:
            reply = (
                f"🌦️ **{dist} ಜಿಲ್ಲೆಯ ಕೃಷಿ ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ ({seas} ಸೀಸನ್):**\n\n"
                f"• **ಸರಾಸರಿ ಉಷ್ಣಾಂಶ:** 24°C ರಿಂದ 31°C (ಬೆಳವಣಿಗೆಗೆ ಅನುಕೂಲಕರ)\n"
                f"• **ಆರ್ದ್ರತೆ (Humidity):** 65% – 80%\n"
                f"• **ಮಳೆಯ ಪ್ರವೃತ್ತಿ:** ಮುಂಗಾರು ಮಳೆಯು ಸಾಮಾನ್ಯವಾಗಿ ಸಾಧಾರಣದಿಂದ ಉತ್ತಮವಾಗಿರಲಿದೆ.\n\n"
                f"⚠️ **ಕೃಷಿ ಸಲಹೆ:** ಕೀಟನಾಶಕ ಸಿಂಪಡಿಸುವ ಮುನ್ನ ಮಳೆ ಮುನ್ಸೂಚನೆ ಗಮನಿಸಿ. ಭಾರಿ ಮಳೆಯ ಸಂಭವವಿದ್ದರೆ ಹೊಲದಲ್ಲಿ ಹೆಚ್ಚುವರಿ ನೀರು ಬಸಿದು ಹೋಗಲು ಬಸಿಗಾಲುವೆ (Drainage) ಮಾಡಿಕೊಳ್ಳಿ."
            )
        else:
            reply = (
                f"🌦️ **Agro-Weather Forecast for {dist} District ({seas} Season):**\n\n"
                f"• **Average Temperature:** 24°C to 31°C (Optimal for crop growth)\n"
                f"• **Relative Humidity:** 65% to 80%\n"
                f"• **Rainfall Trend:** Upcoming monsoon pattern indicates moderate-to-good rainfall spells.\n\n"
                f"⚠️ **Field Advisory:** Avoid pesticide spraying immediately before rains. Ensure field drainage trenches to prevent water stagnation around roots."
            )

        return {
            "intent": "weather_advisory",
            "reply": reply,
            "chips": ["ಉತ್ತಮ ಬೆಳೆ ಶಿಫಾರಸು", "ಮಾರುಕಟ್ಟೆ ದರ (APMC)", "ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು"]
        }

    def _handle_crop_advice(self, district: Optional[str], season: Optional[str], is_kn: bool) -> Dict[str, Any]:
        dist = district or "Davanagere"
        seas = season or "Kharif"
        if is_kn:
            reply = (
                f"🌾 **{dist} ಜಿಲ್ಲೆಗೆ {seas} ಹಂಗಾಮಿನಲ್ಲಿ ಹೆಚ್ಚು ಲಾಭದಾಯಕ ಮತ್ತು ಸುಲಭ ಬೆಳೆಗಳು:**\n\n"
                f"1. **ಮೆಕ್ಕೆಜೋಳ (Maize):**\n"
                f"   • ಅತ್ಯಂತ ಸುಲಭ ಬೆಳೆ, ಕನಿಷ್ಠ ರೋಗ ಬಾಧೆ, ದಾವಣಗೆರೆ ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ನೇರ ಖರೀದಿ.\n"
                f"   • ನಿರೀಕ್ಷಿತ ಇಳುವರಿ: ಎಕರೆಗೆ 25-35 ಕ್ವಿಂಟಾಲ್. ಅಂದಾಜು ಲಾಭ: ₹50,000 – ₹80,000 / ಹೆಕ್ಟೇರ್.\n\n"
                f"2. **ಹತ್ತಿ (Cotton):**\n"
                f"   • ಕಪ್ಪು ಮಣ್ಣಿಗೆ ಅತ್ಯುತ್ತಮ ವಾಣಿಜ್ಯ ಬೆಳೆ, ಪ್ರಸ್ತುತ ಎಪಿಎಂಸಿ ಕ್ವಿಂಟಾಲ್ ದರ ₹7,500+.\n"
                f"   • ಅಂದಾಜು ಲಾಭ: ₹75,000 – ₹1,30,000 / ಹೆಕ್ಟೇರ್.\n\n"
                f"3. **ತೊಗರಿ (Pigeonpea / Tur):**\n"
                f"   • ಬರ ನಿರೋಧಕ ದ್ವಿದಳ ಧಾನ್ಯ, ಮಣ್ಣಿನ ಫಲವತ್ತತೆ ಹೆಚ್ಚಿಸುತ್ತದೆ. ಮಾರುಕಟ್ಟೆ ದರ ₹10,000+.\n\n"
                f"💡 ವಿವರವಾದ ಹಂತ ಹಂತದ ಬೆಳವಣಿಗೆ ವೇಳಾಪಟ್ಟಿಯನ್ನು ನಮ್ಮ **Smart Crop Recommendation** ಪುಟದಲ್ಲಿ ಪರಿಶೀಲಿಸಬಹುದು!"
            )
        else:
            reply = (
                f"🌾 **Most Profitable & Easy-to-Grow Crops for {dist} ({seas}):**\n\n"
                f"1. **Maize (Corn):**\n"
                f"   • Highly resilient, low pest stress, instant liquidity in local mandis.\n"
                f"   • Net Profit: ₹50,000 – ₹80,000 / hectare.\n\n"
                f"2. **Cotton:**\n"
                f"   • Highest value commercial crop on black soils. Current APMC rates ₹7,500+/qtl.\n"
                f"   • Net Profit: ₹75,000 – ₹1,30,000 / hectare.\n\n"
                f"3. **Pigeonpea (Tur / Arhar):**\n"
                f"   • Drought-hardy pulse, enriches soil nitrogen, high market demand (₹10,000+/qtl).\n\n"
                f"💡 For exact soil chemistry match and 100-day stage timeline, visit the **Smart Crop Recommendation** tab above!"
            )

        return {
            "intent": "crop_advice",
            "reply": reply,
            "chips": ["ಇಂದಿನ ಹವಾಮಾನ", "ಮಾರುಕಟ್ಟೆ ದರ (APMC)", "ಗೊಬ್ಬರ ಮತ್ತು ಪೋಷಕಾಂಶ"]
        }

    def _handle_greeting(self, district: Optional[str], is_kn: bool) -> Dict[str, Any]:
        if is_kn:
            reply = (
                f"ನಮಸ್ಕಾರ ರೈತ ಬಂಧುವೇ! 🙏 ನಾನು ನಿಮ್ಮ ರೈತಣ್ಣ.\n"
                f"ಇಂದು ನಿಮ್ಮ {district or 'ಹೊಲ'}ದ ಕೃಷಿಗೆ ಸಂಬಂಧಿಸಿದಂತೆ ನಾನು ಹೇಗೆ ಸಹಾಯ ಮಾಡಲಿ?\n"
                f"ನೀವು ನೇರವಾಗಿ ಧ್ವನಿ ಮೂಲಕ ಮಾತನಾಡಬಹುದು (🎙️), ಬೆಳೆಯ ಎಲೆಯ ಫೋಟೋ ಕಳುಹಿಸಬಹುದು (📷) ಅಥವಾ ಕೆಳಗಿನ ಬಟನ್‌ಗಳನ್ನು ಕ್ಲಿಕ್ ಮಾಡಬಹುದು."
            )
        else:
            reply = (
                f"Namaskara Farmer Friend! 🙏 I am your Raithanna.\n"
                f"How can I assist your farming in {district or 'Karnataka'} today?\n"
                f"You can speak by voice (🎙️), take a photo of an infected leaf (📷), or choose any topic below."
            )

        return {
            "intent": "greeting",
            "reply": reply,
            "chips": ["ಇಂದಿನ ಹವಾಮಾನ", "ಬೆಳೆ ರೋಗ ಪರೀಕ್ಷೆ", "ಮಾರುಕಟ್ಟೆ ದರ (APMC)", "ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು"]
        }

    def _handle_default(self, message: str, district: Optional[str], is_kn: bool) -> Dict[str, Any]:
        if is_kn:
            reply = (
                f"ರೈತ ಬಂಧುವೇ, ನಿಮ್ಮ ಪ್ರಶ್ನೆ: *\"{message}\"*\n\n"
                f"ನಾನು ನಿಮಗೆ ಈ ಕೆಳಗಿನ ವಿಷಯಗಳಲ್ಲಿ ತಕ್ಷಣ ಸಹಾಯ ಮಾಡಬಲ್ಲೆ:\n"
                f"• 🌦️ **ಹವಾಮಾನ ಮತ್ತು ಮಳೆ ಮುನ್ಸೂಚನೆ**\n"
                f"• 🍃 **ಬೆಳೆ ರೋಗ ಮತ್ತು ಕೀಟ ಪರಿಹಾರ (ಫೋಟೋ ಅಪ್ಲೋಡ್ ಮಾಡಬಹುದು)**\n"
                f"• 💰 **ಎಪಿಎಂಸಿ ಮಾರುಕಟ್ಟೆ ದರಗಳು**\n"
                f"• 🏛️ **ಪಿಎಂ-ಕಿಸಾನ್, ರೈತ ಸಿರಿ ಹಾಗೂ ಕೃಷಿ ಭಾಗ್ಯ ಸರ್ಕಾರಿ ಸಬ್ಸಿಡಿಗಳು**\n"
                f"• 🧪 **ಯೂರಿಯಾ, ಡಿಎಪಿ, ಪೊಟ್ಯಾಷ್ ಹಾಗೂ ಜೀವಾಮೃತ ಪ್ರಮಾಣ**\n\n"
                f"ದಯವಿಟ್ಟು ಕೆಳಗಿನ ಬಟನ್ ಒತ್ತಿ ಅಥವಾ ನೇರವಾಗಿ ಕನ್ನಡದಲ್ಲೇ ಧ್ವನಿ ಮುಖಾಂತರ ಕೇಳಿ!"
            )
        else:
            reply = (
                f"Farmer Friend, regarding your question: *\"{message}\"*\n\n"
                f"I can assist you with:\n"
                f"• 🌦️ **Weather & Rain Forecasts for Karnataka Districts**\n"
                f"• 🍃 **Crop Disease Diagnostics (Upload a photo anytime!)**\n"
                f"• 💰 **APMC Mandi Commodity Rates**\n"
                f"• 🏛️ **PM-KISAN, Krishi Bhagya & Raitha Siri Subsidies**\n"
                f"• 🧪 **Fertilizer Dosage & Organic Farming Tips**\n\n"
                f"Please choose an action below or speak in Kannada/English!"
            )

        return {
            "intent": "general",
            "reply": reply,
            "chips": ["ಇಂದಿನ ಹವಾಮಾನ", "ಬೆಳೆ ರೋಗ ಪರೀಕ್ಷೆ", "ಮಾರುಕಟ್ಟೆ ದರ (APMC)", "ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು"]
        }
