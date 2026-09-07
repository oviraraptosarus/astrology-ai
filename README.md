# ✦ Astrology AI — Cosmic Guide

> **Live Web Application:** [https://astrology-ai-web-production.up.railway.app](https://astrology-ai-web-production.up.railway.app/)  
> **Repository:** [https://github.com/oviraraptosarus/astrology-ai](https://github.com/oviraraptosarus/astrology-ai)

A premium, modern consumer web application and installable Progressive Web App (PWA) built on top of a 26-layer deterministic Vedic (Jyotiṣa), KP, Jaimini, and Nadi calculation engine.

---

## ✨ Features & User Experience

* **Home Dashboard (`/app`)**: Personalized daily Panchanga, active Vimshottari Mahadasha/Antardasha/Pratyantardasha timeline, active planetary transits (Gochara), and quick life-domain access.
* **Core Chart Experience (`/app/chart`)**: Interactive North Indian whole-sign diamond chart wheel, planetary positions, house lords, and classical yogas with deep inspection sheets.
* **Forward Predictive Forecasting (`/app/forecast`)**: Multi-domain timelines (Career, Relationships, Wealth, Health) layered from Level 1 plain-language guidance down to exact acute zero-orb peak collision dates.
* **Ask Astrologer Chatbot (`/app/chat`)**: Integrated conversational AI Jyotiṣa agent powered by LangGraph ReAct with live thought streaming (SSE) and automatic user birth chart synchronization.
* **Relationships & Synastry (`/app/relationships`)**: Saved partner profiles and 36-point Ashtakoota Guna Milan compatibility breakdown.
* **Calendar & Sky (`/app/calendar`)**: Daily Panchang metrics, planetary transits, auspicious and inauspicious windows recalculated live day-by-day.
* **Apple-Inspired Design System**: Mobile-first spatial design using native system fonts (`-apple-system`, `SF Pro`), 8pt grid, safe-area insets, and seamless Light/Dark mode.
* **Progressive Web App (PWA)**: Installable to the Home Screen on iOS (Safari Add to Home Screen) and Android (Web App Manifest), featuring service worker caching and offline shell.

---

## 🏛️ Architecture & Engine Layers

The application operates as a layered architecture: **Simple Consumer UI $\rightarrow$ Product API Layer $\rightarrow$ 26 Deterministic Mathematical Engine Layers**.

1. **Core Ephemeris & Kundli Math**: Geocentric Lahiri Sidereal positions (`pyswisseph`), D1–D60 Vargas, Bhava Chalit, Shadbala.
2. **Location-Based Drik Panchangam**: Accurate Tithi, Vara, Nakshatra, Yoga, Karana, Choghadiya, and Rahu Kalam.
3. **Sensitive Points & Upagrahas**: 64th Navamsha, 22nd Drekkana (Kharesh), Mandi, Gulika, Bhrigu Bindu, Indu Lagna.
4. **Cancellations & Avasthas**: Neecha Bhanga Raja Yoga (NBRY), Vipareeta Raja Yoga (VRY), Lajjitadi Avasthas, canonical Yogas.
5. **Forward Timing Scanner**: Exact sub-degree micro-trigger collision scanner with K.N. Rao double transits and SAV bindu gating.
6. **Financial Astrology & Gann**: W.D. Gann Square of 9 price-time squaring and harmonic support/resistance.
7. **Numerology & Siddha Systems**: Chaldean & Pythagorean Numerology (Moolank, Bhagyank, Namank) and Tamil Siddha Pancha Pakshi biorhythms.
8. **Prescriptive Remedies**: Classical gemstones, planetary Beeja Mantras, and charity (*Daana*) matrices.
9. **Jaimini Chara Dasha**: 7-Chara Karaka ranking (AK, AmK, BK, MK, PK, GK, DK) and 12-sign period progression.
10. **Tajika Varshaphala**: Annual solar return chart with Muntha, Year Lord, and Sahams.
11. **C.S. Patel Ashtakavarga Kakshya**: 3.5-day transit sub-window evaluation.
12. **Kundali Milan & Synastry**: 36-point Ashtakoota matching, Kuja Dosha (Manglik) analysis with cancellation rules.
13. **Master Sade Sati & Shani Gochara**: Saturn transit phases across natal Moon and Lagna.
14. **Yogini Dasha Engine**: 36-year cycle (8 Yoginis) predictive timing.
15. **Sarvatobhadra Chakra**: 28-Nakshatra Vedha and institutional defense grid.
16. **Bhrigu Nandi Nadi**: Planetary progressions and conjunction networks.
17. **Medical Astrology**: Tridosha constitution diagnostics and physical stress indicators.
18. **Pushkara Navamsha & Bhaga**: Auspicious degree blessings.
19. **Special Wealth Lagnas**: Indu Lagna, Sri Lagna, and Hora Lagna.
20. **KP Cuspal Interlinks**: 12-house Placidus cuspal sub-lord gating.
21. **Jaimini Arudha Padas**: A1–A12 Arudha Padas and Argala interventions.
22. **Navatara Chakra**: 9-fold Tara Bala classification.
23. **Gochara Vedha & Vipareeta Vedha**: Classical transit obstruction mapping.
24. **Discrete Boundary Fragility**: Input time sensitivity diagnostics.
25. **Semantic Synthesis & ReAct Router**: LangGraph ReAct autonomous agent routing with multi-provider fallback (Gemini, Groq, OpenRouter).
26. **70-Node Master Jyotiṣa Question Ontology**: Domain-specific query taxonomy and reasoning graphs.

---

## 📡 Product API Endpoints

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `/api/product/summary` | `GET` | User identity, birth profile status, appearance settings |
| `/api/product/home` | `GET` | Personalized daily insight, active Dasha, and live transits |
| `/api/product/chart` | `GET` | Complete chart summary, houses, planets, and yogas |
| `/api/product/planet/{name}` | `GET` | Detailed analysis sheet for a specific planet |
| `/api/product/forecast` | `GET` | Multi-domain forecast overview across life areas |
| `/api/product/forecast/{domain}` | `GET` | Layered deep dive (L1 plain text $\rightarrow$ L4 engine evidence) |
| `/api/product/relationships` | `GET/POST` | List or create saved relationship profiles |
| `/api/product/relationships/{id}` | `DELETE` | Remove a relationship profile (isolated per user) |
| `/api/product/relationships/{id}/compatibility` | `GET` | 36-point Ashtakoota compatibility analysis |
| `/api/product/calendar` | `GET` | Daily Panchang and auspicious/inauspicious windows |
| `/api/product/preferences` | `GET/POST` | Notification and appearance preferences |
| `/api/chat/stream` | `GET` | SSE real-time streaming endpoint for AI Astrologer |

---

## 🚀 Local Development Setup

```bash
# 1. Clone repository
git clone https://github.com/oviraraptosarus/astrology-ai.git
cd astrology-ai

# 2. Set up virtual environment
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables (.env)
APP_ENV=development
JWT_SECRET=dev-secret-key-32-chars-minimum-here
# Optional: GOOGLE_API_KEY, GROQ_API_KEY, OPENROUTER_API_KEY, DATABASE_URL

# 5. Run test suite
python test_engine_validation.py
python tests/test_master_e2e.py
python -m unittest tests/test_product_api.py

# 6. Launch development server
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

---

## 🚢 Deployment (Railway)

The application is containerized via `Dockerfile` and deploys automatically on Railway:
- **Managed Database**: PostgreSQL on Railway / Supabase
- **Process**: `uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}`
- **Healthcheck**: `GET /health`

---

## ⚖️ License & Advisory Notice

This application and its interpretations are provided for philosophical reflection and personal self-inquiry. Astrological interpretations reflect symbolic planetary archetypes and do not constitute financial, medical, or legal advice. Conscious human action (*Kriyamana Karma / Purushartha*) remains supreme.
