"""
Raithanna (ರೈತಣ್ಣ) Plugin Configuration.
Defines persona, bilingual greetings, and farmer quick actions.
"""
from typing import Dict, List, Any

BOT_NAME_KN = "ರೈತಣ್ಣ"
BOT_NAME_EN = "Raithanna"
TAGLINE_KN = "ಕರ್ನಾಟಕದ ರೈತರ ನೆಚ್ಚಿನ AI ಕೃಷಿ ಮಿತ್ರ"
TAGLINE_EN = "Karnataka's Trusted AI Farmer Companion"

GREETING_KN = (
    "ನಮಸ್ಕಾರ ರೈತ ಬಂಧುವೇ! 🙏 ನಾನು ನಿಮ್ಮ ರೈತಣ್ಣ (Raithanna).\n"
    "ಬೆಳೆ ಶಿಫಾರಸು, ಹವಾಮಾನ ಮುನ್ಸೂಚನೆ, ರೋಗ-ಕೀಟ ಬಾಧೆ, ಗೊಬ್ಬರದ ಪ್ರಮಾಣ, "
    "ಮಾರುಕಟ್ಟೆ ಎಪಿಎಂಸಿ ದರ ಅಥವಾ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳ ಬಗ್ಗೆ ಯಾವುದೇ ಪ್ರಶ್ನೆ ಇದ್ದರೂ ಕೇಳಿ. "
    "ನೀವು ಕನ್ನಡದಲ್ಲೇ ಮಾತನಾಡಬಹುದು (Voice), ನಿಮ್ಮ ಬೆಳೆಯ ಎಲೆಯ ಫೋಟೋ (Photo) ಕಳುಹಿಸಬಹುದು ಅಥವಾ ಫೈಲ್ ಲಗತ್ತಿಸಬಹುದು!"
)

GREETING_EN = (
    "Namaskara Farmer Friend! 🙏 I am your Raithanna (ರೈತಣ್ಣ).\n"
    "Ask me anything about crop choices, weather forecast, pest & disease remedies, "
    "fertilizer dosage, APMC mandi rates, or Karnataka government schemes. "
    "You can speak via voice (🎙️), upload photos of infected leaves (📷), or attach soil reports (📎)!"
)

QUICK_ACTIONS: List[Dict[str, Any]] = [
    {
        "id": "weather",
        "icon": "🌦️",
        "title_kn": "ಇಂದಿನ ಹವಾಮಾನ",
        "title_en": "Today's Weather",
        "prompt_kn": "ನನ್ನ ಜಿಲ್ಲೆಯ ಇಂದಿನ ಹವಾಮಾನ ಮತ್ತು ಮಳೆಯ ಮುನ್ಸೂಚನೆ ಹೇಗಿದೆ?",
        "prompt_en": "What is the weather and rain forecast for my district?",
    },
    {
        "id": "disease",
        "icon": "🍃",
        "title_kn": "ಬೆಳೆ ರೋಗ ಪರೀಕ್ಷೆ",
        "title_en": "Leaf Disease Check",
        "prompt_kn": "ನನ್ನ ಬೆಳೆಯ ಎಲೆಗಳು ಹಳದಿಯಾಗುತ್ತಿವೆ / ಚುಕ್ಕೆಗಳಾಗಿವೆ, ಏನು ಪರಿಹಾರ?",
        "prompt_en": "My crop leaves have yellow spots/blight, what is the remedy?",
    },
    {
        "id": "schemes",
        "icon": "🏛️",
        "title_kn": "ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು",
        "title_en": "Govt Schemes",
        "prompt_kn": "ಕರ್ನಾಟಕ ರೈತರಿಗೆ ಸಿಗುವ ಪ್ರಮುಖ ಸರ್ಕಾರಿ ಸಬ್ಸಿಡಿ ಮತ್ತು ಯೋಜನೆಗಳು ಯಾವುವು?",
        "prompt_en": "What are the key Karnataka government farmer schemes and subsidies?",
    },
    {
        "id": "mandi",
        "icon": "💰",
        "title_kn": "ಮಾರುಕಟ್ಟೆ ದರ (APMC)",
        "title_en": "Mandi Rates",
        "prompt_kn": "ಕರ್ನಾಟಕ ಎಪಿಎಂಸಿ ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಇಂದಿನ ಪ್ರಮುಖ ಬೆಳೆಗಳ ಕ್ವಿಂಟಾಲ್ ದರ ಎಷ್ಟು?",
        "prompt_en": "What are the latest APMC mandi rates for major crops in Karnataka?",
    },
    {
        "id": "fertilizer",
        "icon": "🧪",
        "title_kn": "ಗೊಬ್ಬರ ಮತ್ತು ಪೋಷಕಾಂಶ",
        "title_en": "Fertilizer Guide",
        "prompt_kn": "ಜೋಳ ಮತ್ತು ಹತ್ತಿ ಬೆಳೆಗೆ ಸರಿಯಾದ ಯೂರಿಯಾ, ಡಿಎಪಿ, ಪೊಟ್ಯಾಷ್ ಪ್ರಮಾಣ ತಿಳಿಸಿ.",
        "prompt_en": "What is the recommended NPK/Urea/DAP fertilizer dosage for maize and cotton?",
    },
    {
        "id": "crops",
        "icon": "🌾",
        "title_kn": "ಉತ್ತಮ ಬೆಳೆ ಶಿಫಾರಸು",
        "title_en": "Best Crop Advice",
        "prompt_kn": "ಕಡಿಮೆ ಖರ್ಚಿನಲ್ಲಿ ಹೆಚ್ಚು ಲಾಭ ಕೊಡುವ ಮತ್ತು ಸುಲಭವಾಗಿ ಬೆಳೆಯಬಹುದಾದ ಬೆಳೆ ಯಾವುದು?",
        "prompt_en": "Which crop is easy to grow, profitable, and suited for my soil?",
    },
]
