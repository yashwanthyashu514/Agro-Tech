# AgroTech Plugin System & ರೈತಣ್ಣ (Raithanna) AI Chatbot

## 1. Overview
The **AgroTech Plugin Architecture** enables modular, plug-and-play extension of the AgroTech intelligence platform without altering core microservices or existing model pipelines.

The first major plugin implemented under this architecture is **ರೈತಣ್ಣ (Raithanna)** — a complete end-to-end bilingual (Kannada + English) AI Farmer Assistant designed to support Karnataka farmers through:
1. **💬 Conversational Dialogue (Kannada, English & Kanglish):** Intelligent context-aware answers for crop selection, pest management, and cultivation practices.
2. **📷 Leaf Disease & Pest Diagnosis (Photo Upload):** Visual AI computer vision engine analyzing infected leaf photos to detect Fall Armyworm, Rice Blast, Bacterial Blight, and Chlorosis, providing both organic remedies and chemical spray dosages.
3. **🎙️ Voice Speech Interaction:** Real-time speech recognition (Kannada `kn-IN` / Indian English `en-IN`) and Text-to-Speech audio playback for illiterate or semi-literate farmers who prefer listening over reading.
4. **📎 Document & Soil Report Analysis (File Upload):** Instant parsing and recommendation based on uploaded Soil Health Cards, laboratory PDFs, or farm documents.
5. **💰 Karnataka APMC Mandi Rates:** Real-time modal prices for Davanagere, Hubballi, Kalaburagi, Shivamogga, Ballari, and Mysuru markets.
6. **🏛️ Karnataka & Central Government Schemes:** Direct guidance and registration links for PM-KISAN, Raitha Siri (₹10,000/ha for millets), Krishi Bhagya, PMFBY Crop Insurance, and Ganga Kalyana.

---

## 2. Directory Structure

```
d:\Agrotech\plugin\
├── README.md                          # Documentation of plugin architecture
├── __init__.py                        # Plugin package initialization
├── base.py                            # BasePlugin abstract interface
├── loader.py                          # Dynamic discovery & FastAPI mounting loader
│
└── raithanna_bot/                     # ರೈತಣ್ಣ (Raithanna) Plugin Implementation
    ├── __init__.py                    # Exports RaithannaPlugin instance
    ├── plugin_manifest.json           # Plugin metadata, routes & capabilities
    ├── config.py                      # Persona, bilingual greetings & quick action chips
    ├── knowledge_base.py              # Karnataka schemes, APMC mandi rates, disease remedies
    ├── vision_handler.py              # Visual AI leaf disease and chlorosis diagnostics
    ├── voice_handler.py               # Voice audio recording and speech processor
    ├── engine.py                      # Multi-modal bilingual dialogue reasoning brain
    ├── router.py                      # FastAPI REST endpoints (/api/v1/plugin/raithanna/...)
    │
    └── ui/                            # Frontend UI Plugin Bundle
        ├── RaithannaChatWidget.jsx    # React floating interactive chatbot component
        ├── RaithannaChatWidget.css    # Clean, modern glassmorphism styling
        └── index.js                   # React component export
```

---

## 3. API Endpoints

All endpoints are mounted dynamically under `/api/v1/plugin/raithanna/`:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/status` | Plugin health check and capability manifest |
| `POST` | `/chat` | Conversational text input in Kannada, English, or Kanglish |
| `POST` | `/analyze-photo` | Multipart image upload for plant leaf disease diagnosis |
| `POST` | `/voice` | Voice audio note upload & transcription processing |
| `POST` | `/upload-file` | Document & Soil Health Card file upload and agronomic analysis |
| `GET` | `/quick-actions` | Predefined farmer quick action chips in Kannada and English |
| `GET` | `/mandi-rates` | Latest APMC commodity prices across Karnataka markets |
| `GET` | `/schemes` | Complete list of Karnataka agricultural subsidy schemes |

---

## 4. How It Works

### Dynamic Backend Loading
In `backend/app/main.py`:
```python
from plugin.loader import load_plugins
load_plugins(app)
```
The loader automatically scans the `d:\Agrotech\plugin\` directory, reads `plugin_manifest.json`, instantiates `BasePlugin`, and mounts its router with zero manual wiring.

### Frontend Integration
In `frontend/src/App.jsx`:
```jsx
import { RaithannaChatWidget } from './components/RaithannaChatWidget';

// Renders floating mascot button at bottom right
<RaithannaChatWidget />
```
The widget provides real-time Web Speech API transcription, camera capture, file upload, text-to-speech voice playback, and quick action suggestion buttons.
