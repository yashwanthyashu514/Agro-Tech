"""
Raithanna Knowledge Base — Curated Karnataka Agriculture Intelligence.
Contains crop disease diagnostics, government schemes, APMC prices, and agronomic remedies.
"""
from typing import Any, Dict, List, Optional

SCHEMES_DATA = [
    {
        "name_kn": "ಪಿಎಂ-ಕಿಸಾನ್ ಸಮ್ಮಾನ್ ನಿಧಿ + ರಾಜ್ಯ ರೈತ ಸಿರಿ ಟಾಪ್-ಅಪ್",
        "name_en": "PM-KISAN Samman Nidhi + State Support",
        "benefits_kn": "ವರ್ಷಕ್ಕೆ ₹6,000 ಕೇಂದ್ರ ಸರ್ಕಾರದಿಂದ (3 ಕಂತುಗಳಲ್ಲಿ ₹2000) + ರಾಜ್ಯ ಸರ್ಕಾರದ ಕೃಷಿ ಸಹಾಯಧನ ನೇರ ಬ್ಯಾಂಕ್ ಖಾತೆಗೆ (DBT).",
        "benefits_en": "₹6,000/year from Central Govt in 3 installments + State DBT support credited directly to Aadhaar-linked bank account.",
        "eligibility": "All landholding farmer families in Karnataka.",
        "portal": "pmkisan.gov.in / fruits.karnataka.gov.in (FRUITS ID)",
    },
    {
        "name_kn": "ರೈತ ಸಿರಿ ಯೋಜನೆ (ಸಿರಿಧಾನ್ಯ ಪ್ರೋತ್ಸಾಹ)",
        "name_en": "Raitha Siri Scheme (Millet Incentive)",
        "benefits_kn": "ರಾಗಿ, ನವಣೆ, ಸಾಮೆ, ಹಾರಕ, ಕೊರಲೆ, ಸಜ್ಜೆ ಬೆಳೆಯುವ ರೈತರಿಗೆ ಪ್ರತಿ ಹೆಕ್ಟೇರ್‌ಗೆ ₹10,000 ನೇರ ಆರ್ಥಿಕ ಪ್ರೋತ್ಸಾಹ ಧನ.",
        "benefits_en": "Direct incentive of ₹10,000 per hectare for farmers cultivating millets (Ragi, Foxtail, Little, Barnyard millet).",
        "eligibility": "Millet growers registered on Karnataka FRUITS portal.",
        "portal": "fruits.karnataka.gov.in",
    },
    {
        "name_kn": "ಕೃಷಿ ಭಾಗ್ಯ ಯೋಜನೆ (Krishi Bhagya)",
        "name_en": "Krishi Bhagya Scheme (Farm Ponds & Micro-Irrigation)",
        "benefits_kn": "ಕೃಷಿ ಹೊಂಡ (Farm Pond) ನಿರ್ಮಾಣಕ್ಕೆ 80%-90% ಸಬ್ಸಿಡಿ (SC/ST) ಮತ್ತು 50% (ಸಾಮಾನ್ಯ), ಪಾಲಿತೀನ್ ಲೈನಿಂಗ್, ಡೀಸೆಲ್ ಪಂಪ್ ಮತ್ತು ತುಂತುರು ನೀರಾವರಿ ಘಟಕ.",
        "benefits_en": "80-90% subsidy for SC/ST and 50% for general farmers to construct farm ponds, polythene lining, diesel pumps, and sprinkler sets.",
        "eligibility": "Dryland / rainfed farmers across Karnataka dry zones.",
        "portal": "raitamitra.karnataka.gov.in",
    },
    {
        "name_kn": "ಪ್ರಧಾನ ಮಂತ್ರಿ ಫಸಲ್ ಬಿಮಾ ಯೋಜನೆ (PMFBY)",
        "name_en": "Pradhan Mantri Fasal Bima Yojana (Crop Insurance)",
        "benefits_kn": "ಬರಗಾಲ, ಅಕಾಲಿಕ ಮಳೆ, ನೆರೆ ಮತ್ತು ರೋಗಗಳಿಂದ ಬೆಳೆ ನಷ್ಟವಾದರೆ ಗರಿಷ್ಠ ಪರಿಹಾರ. ರೈತರ ಪ್ರೀಮಿಯಂ ಖಾರೀಫ್‌ಗೆ ಕೇವಲ 2%, ರಬಿಗೆ 1.5%.",
        "benefits_en": "Comprehensive insurance against drought, floods, dry-spells, pests. Nominal farmer premium: 2% for Kharif, 1.5% for Rabi.",
        "eligibility": "All notified crop growers in Karnataka through Samrakshane portal.",
        "portal": "samrakshane.karnataka.gov.in",
    },
    {
        "name_kn": "ಗಂಗಾ ಕಲ್ಯಾಣ ಯೋಜನೆ (Ganga Kalyana)",
        "name_en": "Ganga Kalyana Scheme",
        "benefits_kn": "ಸಣ್ಣ ಮತ್ತು ಅತಿ ಸಣ್ಣ ಹಿಂದುಳಿದ/ದಲಿತ ರೈತರಿಗೆ ಉಚಿತ ಕೊಳವೆಬಾವಿ (Borewell) ಕೊರೆಯಿಸಿ ಪಂಪ್‌ಸೆಟ್ ಮತ್ತು ಉಚಿತ ವಿದ್ಯುತ್ ಸಂಪರ್ಕ.",
        "benefits_en": "Free individual or community borewell drilling with pump sets and power energization for small & marginal farmers.",
        "eligibility": "Farmers holding 1.5 to 5 acres belonging to eligible backward categories.",
        "portal": "kmdc.karnataka.gov.in",
    },
    {
        "name_kn": "ಯಶಸ್ವಿನಿ ಆರೋಗ್ಯ ಯೋಜನೆ (Yashaswini Health Scheme)",
        "name_en": "Yashaswini Cooperative Health Scheme",
        "benefits_kn": "ಸಹಕಾರಿ ಸಂಘಗಳ ರೈತ ಸದಸ್ಯರ ಕುಟುಂಬಗಳಿಗೆ ವರ್ಷಕ್ಕೆ ₹5 ಲಕ್ಷದವರೆಗೆ ನಗದು ರಹಿತ (Cashless) ಆಸ್ಪತ್ರೆ ಶಸ್ತ್ರಚಿಕಿತ್ಸೆ ಸೌಲಭ್ಯ.",
        "benefits_en": "Cashless surgical treatment up to ₹5 Lakhs per family per year across empaneled hospitals in Karnataka.",
        "eligibility": "Members of rural cooperative societies in Karnataka.",
        "portal": "yashaswini.karnataka.gov.in",
    },
]

MANDI_RATES_DATA = {
    "Davanagere": [
        {"crop": "Maize (ಮೆಕ್ಕೆಜೋಳ)", "variety": "Hybrid Yellow", "min": 2180, "max": 2450, "modal": 2320, "unit": "₹ / Quintal"},
        {"crop": "Cotton (ಹತ್ತಿ)", "variety": "DCH-32 / Bunny", "min": 7200, "max": 7850, "modal": 7520, "unit": "₹ / Quintal"},
        {"crop": "Paddy (ಭತ್ತ)", "variety": "Bhadra / RNR", "min": 2350, "max": 2800, "modal": 2550, "unit": "₹ / Quintal"},
        {"crop": "Ragi (ರಾಗಿ)", "variety": "Local / GPU-28", "min": 3600, "max": 4050, "modal": 3846, "unit": "₹ / Quintal"},
    ],
    "Kalaburagi": [
        {"crop": "Red Gram / Tur (ತೊಗರಿ)", "variety": "Gulyal / Maruthi (GI)", "min": 9400, "max": 10800, "modal": 10250, "unit": "₹ / Quintal"},
        {"crop": "Green Gram (ಹೆಸರು)", "variety": "Shining Moong", "min": 7600, "max": 8400, "modal": 8050, "unit": "₹ / Quintal"},
        {"crop": "Bengal Gram (ಕಡಲೆ)", "variety": "Annigeri-1", "min": 5700, "max": 6250, "modal": 5980, "unit": "₹ / Quintal"},
    ],
    "Hubballi / Dharwad": [
        {"crop": "Cotton (ಹತ್ತಿ)", "variety": "Medium Staple", "min": 7100, "max": 7750, "modal": 7450, "unit": "₹ / Quintal"},
        {"crop": "Bengal Gram (ಕಡಲೆ)", "variety": "Desi Chickpea", "min": 5650, "max": 6200, "modal": 5950, "unit": "₹ / Quintal"},
        {"crop": "Onion (ಈರುಳ್ಳಿ)", "variety": "Bellary Red", "min": 1900, "max": 2800, "modal": 2350, "unit": "₹ / Quintal"},
        {"crop": "Chilli (ಬ್ಯಾಡಗಿ ಮೆಣಸಿನಕಾಯಿ)", "variety": "Byadagi Kaddi / Dabbi", "min": 32000, "max": 46000, "modal": 39500, "unit": "₹ / Quintal"},
    ],
    "Shivamogga": [
        {"crop": "Arecanut (ಅಡಿಕೆ)", "variety": "Rashi (ರಾಶಿ)", "min": 49000, "max": 54200, "modal": 51800, "unit": "₹ / Quintal"},
        {"crop": "Arecanut (ಅಡಿಕೆ)", "variety": "Bette (ಬೆಟ್ಟೆ)", "min": 52000, "max": 57500, "modal": 54600, "unit": "₹ / Quintal"},
        {"crop": "Paddy (ಭತ್ತ)", "variety": "Jyothi / Jaya", "min": 2400, "max": 2950, "modal": 2680, "unit": "₹ / Quintal"},
        {"crop": "Ginger (ಶುಂಠಿ)", "variety": "Fresh Green", "min": 5200, "max": 7100, "modal": 6300, "unit": "₹ / Quintal"},
    ],
    "Ballari": [
        {"crop": "Cotton (ಹತ್ತಿ)", "variety": "Bt Cotton", "min": 7150, "max": 7800, "modal": 7480, "unit": "₹ / Quintal"},
        {"crop": "Maize (ಮೆಕ್ಕೆಜೋಳ)", "variety": "Yellow Grain", "min": 2150, "max": 2400, "modal": 2280, "unit": "₹ / Quintal"},
        {"crop": "Paddy (ಸೋನಾ ಮಸೂರಿ)", "variety": "BPT-5204", "min": 2700, "max": 3300, "modal": 3050, "unit": "₹ / Quintal"},
    ],
    "Mysuru / Mandya": [
        {"crop": "Ragi (ರಾಗಿ)", "variety": "Indaf-9 / ML-365", "min": 3700, "max": 4100, "modal": 3846, "unit": "₹ / Quintal"},
        {"crop": "Paddy (ಭತ್ತ)", "variety": "IR-64 / Sona", "min": 2350, "max": 2850, "modal": 2600, "unit": "₹ / Quintal"},
        {"crop": "Banana (ಬಾಳೆ)", "variety": "Elakki (ಏಲಕ್ಕಿ ಬಾಳೆ)", "min": 2200, "max": 3400, "modal": 2800, "unit": "₹ / Quintal"},
        {"crop": "Coconut (ತೆಂಗಿನಕಾಯಿ)", "variety": "Tiptur Tall", "min": 26000, "max": 34000, "modal": 30500, "unit": "₹ / 1000 nuts"},
    ],
}

DISEASE_REMEDIES = {
    "fall_armyworm": {
        "name_kn": "ಮೆಕ್ಕೆಜೋಳದ ಸೈನಿಕ ಹುಳು (Fall Armyworm)",
        "name_en": "Maize Fall Armyworm (Spodoptera frugiperda)",
        "symptoms_kn": "ಎಲೆಗಳ ಮೇಲೆ ಕಿಂಡಿಗಳು, ಸುಳಿಯೊಳಗೆ ಹಿಕ್ಕೆ ಹಾಗೂ ಎಲೆಗಳು ಜರಡಿಯಂತಾಗುವುದು.",
        "symptoms_en": "Pin-holes on whorl leaves, sawdust-like fecal matter inside funnel, chewed margins.",
        "remedy_organic_kn": "ಬೇವಿನ ಕಷಾಯ (Neem Seed Kernel Extract 5%) ಅಥವಾ 10,000 ppm ಬೇವಿನ ಎಣ್ಣೆ 2 ಮಿ.ಲೀ / ಲೀಟರ್ ನೀರಿಗೆ ಬೆರೆಸಿ ಸಿಂಪಡಿಸಿ. ಸುಳಿಯೊಳಗೆ ಒಣ ಮರಳು ಮತ್ತು ಬೂದಿಯ ಮಿಶ್ರಣ ಹಾಕಿ.",
        "remedy_organic_en": "Spray Neem Seed Kernel Extract (NSKE 5%) or 10,000 ppm Neem Oil @ 2 ml/L water. Apply fine sand + wood ash inside leaf whorls.",
        "remedy_chemical_kn": "ಎಮಾಮೆಕ್ಟಿನ್ ಬೆಂಜೋಯೇಟ್ 5% ಎಸ್.ಜಿ (Emamectin Benzoate) 0.4 ಗ್ರಾಂ/ಲೀಟರ್ ಅಥವಾ ಸ್ಪಿನೆಟೋರಾಮ್ 11.7% ಎಸ್.ಸಿ (Spinetoram) 0.5 ಮಿ.ಲೀ/ಲೀಟರ್ ನೀರಿಗೆ ಬೆರೆಸಿ ಸುಳಿಗೆ ಬೀಳುವಂತೆ ಸಿಂಪಡಿಸಿ.",
        "remedy_chemical_en": "Spray Emamectin Benzoate 5% SG @ 0.4 g/L or Spinetoram 11.7% SC @ 0.5 ml/L water directed into plant whorls.",
    },
    "rice_blast": {
        "name_kn": "ಭತ್ತದ ಕತ್ತರಿ ರೋಗ / ಬೆಂಕಿ ರೋಗ (Rice Blast)",
        "name_en": "Rice Blast (Pyricularia oryzae)",
        "symptoms_kn": "ಎಲೆಗಳ ಮೇಲೆ ಕಣ್ಣಿನ ಆಕಾರದ (ಸ್ಪೈಂಡಲ್) ಕಂದು ಬಣ್ಣದ ಚುಕ್ಕೆಗಳು, ಕುತ್ತಿಗೆ ಮುರಿತ.",
        "symptoms_en": "Spindle/eye-shaped elliptical lesions with gray centers and brown margins, neck blast.",
        "remedy_organic_kn": "ಬೀಜೋಪಚಾರಕ್ಕೆ ಟ್ರೈಕೋಡರ್ಮಾ ವಿರಿಡೆ 10 ಗ್ರಾಂ/ಕೆ.ಜಿ ಬಳಸಿ. ಜೀವಾಮೃತವನ್ನು ವಾರಕ್ಕೊಮ್ಮೆ ಸಿಂಪಡಿಸಿ.",
        "remedy_organic_en": "Seed treatment with Trichoderma viride @ 10 g/kg seed. Spray Jeevamrutha 10% weekly.",
        "remedy_chemical_kn": "ಟ್ರೈಸೈಕ್ಲಾಜೋಲ್ 75% ಡಬ್ಲ್ಯೂ.ಪಿ (Tricyclazole) 0.6 ಗ್ರಾಂ/ಲೀಟರ್ ಅಥವಾ ಕಸುಗಾಮೈಸಿನ್ 3% ಎಸ್.ಎಲ್ (Kasugamycin) 1.5 ಮಿ.ಲೀ/ಲೀಟರ್ ನೀರಿಗೆ ಸಿಂಪಡಿಸಿ.",
        "remedy_chemical_en": "Spray Tricyclazole 75% WP @ 0.6 g/L or Kasugamycin 3% SL @ 1.5 ml/L water at first symptom onset.",
    },
    "cotton_bollworm": {
        "name_kn": "ಹತ್ತಿಯ ಗುಲಾಬಿ ಕಾಯಿ ಹುಳು (Pink Bollworm)",
        "name_en": "Cotton Pink Bollworm (Pectinophora gossypiella)",
        "symptoms_kn": "ಹೂಗಳು ಅರಳದೆ ರೋಸೆಟ್ ಆಕಾರವಾಗುವುದು, ಕಾಯಿಗಳಲ್ಲಿ ಹುಳು ಕೊರೆದ ರಂಧ್ರಗಳು.",
        "symptoms_en": "Rosette flowers, stained lint, premature boll opening with larval bore holes.",
        "remedy_organic_kn": "ಪ್ರತಿ ಎಕರೆಗೆ 5 ರಿಂದ 8 ಗಂಡು ಪತಂಗ ಮೋಹಕ ಬಲೆ (Pheromone traps) ಅಳವಡಿಸಿ. ಟ್ರೈಕೋಗ್ರಾಮಾ ಪರಾವಲಂಬಿ ಕಾರ್ಡ್‌ಗಳನ್ನು ಬಿಡಿ.",
        "remedy_organic_en": "Install 5-8 Pheromone traps per acre. Release Trichogramma parasitoid cards @ 60,000 eggs/acre.",
        "remedy_chemical_kn": "ಕ್ಲೋರಾಂಟ್ರಾನಿಲಿಪ್ರೋಲ್ 18.5% ಎಸ್.ಸಿ (Coragen) 0.3 ಮಿ.ಲೀ/ಲೀಟರ್ ಅಥವಾ ಪ್ರೊಫೆನೋಫಾಸ್ 50% ಇ.ಸಿ 2 ಮಿ.ಲೀ/ಲೀಟರ್ ಸಿಂಪಡಿಸಿ.",
        "remedy_chemical_en": "Spray Chlorantraniliprole 18.5% SC @ 0.3 ml/L or Profenofos 50% EC @ 2 ml/L water.",
    },
    "pomegranate_blight": {
        "name_kn": "ದಾಳಿಂಬೆ ದುಂಡಾಣು ಅಂಗಮಾರಿ / ಎಣ್ಣೆ ಚುಕ್ಕೆ ರೋಗ",
        "name_en": "Pomegranate Bacterial Blight (Xanthomonas axonopodis)",
        "symptoms_kn": "ಎಲೆ, ಕಾಂಡ ಹಾಗೂ ಕಾಯಿಗಳ ಮೇಲೆ ಕಪ್ಪು ಎಣ್ಣೆಯುಕ್ತ ಚುಕ್ಕೆಗಳು (L-ಆಕಾರದ ಬಿರುಕುಗಳು).",
        "symptoms_en": "Water-soaked dark lesions on leaves, stems, and fruits turning into black cracking spots.",
        "remedy_organic_kn": "ಸೋಂಕಿತ ರೆಂಬೆಗಳನ್ನು ಕತ್ತರಿಸಿ ಬೋರ್ಡೋ ಮುಲಾಮು ಹಚ್ಚಿ ಸುಟ್ಟುಹಾಕಿ. 1% ಬೋರ್ಡೋ ದ್ರಾವಣ ಸಿಂಪಡಿಸಿ.",
        "remedy_organic_en": "Prune infected twigs, apply Bordeaux paste on cuts, burn infected leaves. Spray 1% Bordeaux mixture.",
        "remedy_chemical_kn": "ಸ್ಟ್ರೆಪ್ಟೊಸೈಕ್ಲಿನ್ 0.5 ಗ್ರಾಂ + ತಾಮ್ರದ ಆಕ್ಸಿಕ್ಲೋರೈಡ್ (COC) 2.5 ಗ್ರಾಂ ಪ್ರತಿ ಲೀಟರ್ ನೀರಿಗೆ ಬೆರೆಸಿ 15 ದಿನಗಳ ಅಂತರದಲ್ಲಿ ಸಿಂಪಡಿಸಿ.",
        "remedy_chemical_en": "Spray Streptocycline @ 0.5 g + Copper Oxychloride (COC) @ 2.5 g per liter of water at 15-day intervals.",
    },
    "yellow_leaf_disease": {
        "name_kn": "ಎಲೆ ಹಳದಿಯಾಗುವಿಕೆ / ಸಾರಜನಕ ಮತ್ತು ಕೀಟ ಬಾಧೆ",
        "name_en": "Yellow Leaf Disease / Chlorosis & Sucking Pests",
        "symptoms_kn": "ಕೆಳಗಿನ ಎಲೆಗಳು ಹಳದಿಯಾಗುವುದು (ಸಾರಜನಕ ಕೊರತೆ) ಅಥವಾ ಎಲೆಗಳು ಮುದುರಿಕೊಳ್ಳುವುದು (ಹೇನು/ಥ್ರಿಪ್ಸ್).",
        "symptoms_en": "Uniform yellowing of older leaves (N deficiency) or leaf curling and mottled yellowing (sucking pests/mites).",
        "remedy_organic_kn": "ಬೇವಿನ ಎಣ್ಣೆ 3 ಮಿ.ಲೀ + ಸಾಬೂನು ನೀರು ಸಿಂಪಡಿಸಿ. ಹಳದಿ ಅಂಟಿನ ಬಲೆಗಳನ್ನು ಎಕರೆಗೆ 10-12 ಅಳವಡಿಸಿ.",
        "remedy_organic_en": "Spray Neem Oil 3 ml/L + mild soap solution. Install 10-12 yellow sticky traps per acre.",
        "remedy_chemical_kn": "ಇಮಿಡಾಕ್ಲೋಪ್ರಿಡ್ 17.8% ಎಸ್.ಎಲ್ 0.3 ಮಿ.ಲೀ/ಲೀಟರ್ ಅಥವಾ ಥಯಾಮೆಥಾಕ್ಸಮ್ 25% ಡಬ್ಲ್ಯೂ.ಜಿ 0.3 ಗ್ರಾಂ/ಲೀಟರ್ ಸಿಂಪಡಿಸಿ. 19:19:19 ನೀರಿನಲ್ಲಿ ಕರಗುವ ಗೊಬ್ಬರ 5 ಗ್ರಾಂ/ಲೀಟರ್ ಸಿಂಪಡಿಸಿ.",
        "remedy_chemical_en": "Spray Imidacloprid 17.8% SL @ 0.3 ml/L or Thiamethoxam 25% WG @ 0.3 g/L. Apply water-soluble 19:19:19 fertilizer @ 5 g/L.",
    },
    "tomato_early_blight": {
        "name_kn": "ಟೊಮೆಟೊ ಮುಂಚಿನ ಅಂಗಮಾರಿ ರೋಗ (Early Blight)",
        "name_en": "Tomato / Vegetable Early Blight (Alternaria solani)",
        "symptoms_kn": "ಕೆಳಗಿನ ಎಲೆಗಳ ಮೇಲೆ ಕಂದು-ಕಪ್ಪು ಬಣ್ಣದ ವೃತ್ತಾಕಾರದ ಉಂಗುರದಂತಹ ಚುಕ್ಕೆಗಳು (Target board spots), ಎಲೆಗಳು ಉದುರುವುದು.",
        "symptoms_en": "Brown-black concentric target-like rings on lower leaves, leaf yellowing and premature defoliation.",
        "remedy_organic_kn": "ಬೇವಿನ ಎಣ್ಣೆ 3 ಮಿ.ಲೀ/ಲೀಟರ್ ಸಿಂಪಡಿಸಿ. ಸೋಂಕಿತ ಎಲೆಗಳನ್ನು ತೆಗೆದು ನಾಶಮಾಡಿ. ಬುಡಕ್ಕೆ ತೇವಾಂಶ ನಿಲ್ಲದಂತೆ ನೋಡಿಕೊಳ್ಳಿ.",
        "remedy_organic_en": "Spray 10,000 ppm Neem Oil @ 3 ml/L. Remove lower infected leaves and avoid splash irrigation.",
        "remedy_chemical_kn": "ಮ್ಯಾಂಕೋಜೆಬ್ 75% ಡಬ್ಲ್ಯೂ.ಪಿ (Mancozeb) 2.5 ಗ್ರಾಂ/ಲೀಟರ್ ಅಥವಾ ಅಜಾಕ್ಸಿಸ್ಟ್ರೋಬಿನ್ + ಡೈಫೆನೊಕೊನಜೋಲ್ (Amistar Top) 1 ಮಿ.ಲೀ/ಲೀಟರ್ ಸಿಂಪಡಿಸಿ.",
        "remedy_chemical_en": "Spray Mancozeb 75% WP @ 2.5 g/L or Azoxystrobin + Difenoconazole @ 1 ml/L water on first sign.",
    },
    "leaf_rust": {
        "name_kn": "ಎಲೆ ತುಕ್ಕು ರೋಗ (Leaf Rust / Puccinia)",
        "name_en": "Cereal / Pulse Leaf Rust (Puccinia spp.)",
        "symptoms_kn": "ಎಲೆಗಳ ಕೆಳಭಾಗದಲ್ಲಿ ಕಿತ್ತಳೆ-ಕಂದು ಬಣ್ಣದ ಪುಡಿಯಂತಹ ಉಬ್ಬುಗಳು (Pustules), ಎಲೆಗಳು ಬೇಗನೆ ಒಣಗುವುದು.",
        "symptoms_en": "Small orange-brown to reddish powdery pustules on underside of leaves, premature leaf drying.",
        "remedy_organic_kn": "ಹುದುಗಿಸಿದ ಮಜ್ಜಿಗೆ ದ್ರಾವಣ (50 ಮಿ.ಲೀ/ಲೀಟರ್) ಸಿಂಪಡಿಸಿ. ಜೀವಾಮೃತವನ್ನು ಮಣ್ಣಿಗೆ ಹಾಯಿಸಿ.",
        "remedy_organic_en": "Spray fermented sour buttermilk solution @ 50 ml/L water. Apply Jeevamrutha to soil.",
        "remedy_chemical_kn": "ಪ್ರೊಪಿಕೊನಜೋಲ್ 25% ಇ.ಸಿ (Tilt) 1 ಮಿ.ಲೀ/ಲೀಟರ್ ಅಥವಾ ಹೆಕ್ಸಾಕೊನಜೋಲ್ 5% ಇ.ಸಿ (Contaf) 2 ಮಿ.ಲೀ/ಲೀಟರ್ ಸಿಂಪಡಿಸಿ.",
        "remedy_chemical_en": "Spray Propiconazole 25% EC (Tilt) @ 1 ml/L or Hexaconazole 5% EC @ 2 ml/L water.",
    },
}
