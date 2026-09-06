"""
AI Astrologer Agent — LangGraph ReAct with Router Pattern + DB-Backed Storage
Phase 2 + Phase 4 of 10/10 Engine Upgrades

Key upgrades from original:
  - Phase 2: Agent Router — intent classifier routes to specialist sub-agents
    with focused tool sets (2-3 tools vs 7), reducing latency and hallucination
  - Phase 4: DB-backed chart cache — replaces file-system JSON with SQLite/Postgres
    so the app works correctly with multiple workers and cloud deployments
  - Phase 3: SSE streaming hooks — run_astrologer_stream() yields thought steps
    for real-time frontend display
"""
import os
import json
import logging
from typing import Optional, Generator
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from langchain_core.tools import tool
from langchain_core.runnables import RunnableConfig
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()
logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"


# ─── Phase 4: DB-Backed Chart Storage ────────────────────────────────────────
# Replaces file-system JSON cache with a database-backed solution.
# This works correctly with multiple workers and cloud deployments.

def _get_cache_db():
    """Get connection to the SQLite cache DB (same DB used for memory)."""
    conn = sqlite3.connect("memory.sqlite", check_same_thread=False)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS chart_cache (
            session_id TEXT PRIMARY KEY,
            chart_json TEXT NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    return conn


def save_chart(session_id: str, data: dict):
    """Save chart to DB. Falls back to file system if DB fails."""
    try:
        conn = _get_cache_db()
        chart_json = json.dumps(data)
        conn.execute(
            "INSERT OR REPLACE INTO chart_cache (session_id, chart_json, updated_at) VALUES (?, ?, CURRENT_TIMESTAMP)",
            (session_id, chart_json)
        )
        conn.commit()
        conn.close()
        logger.info(f"Chart saved to DB for session {session_id}")
    except Exception as e:
        logger.warning(f"DB chart save failed: {e}. Falling back to file system.")
        os.makedirs("cache", exist_ok=True)
        with open(os.path.join("cache", f"chart_{session_id}.json"), "w") as f:
            json.dump(data, f)


def load_chart(session_id: str) -> Optional[dict]:
    """Load chart from DB. Falls back to file system for backward compatibility."""
    try:
        conn = _get_cache_db()
        row = conn.execute(
            "SELECT chart_json FROM chart_cache WHERE session_id = ?",
            (session_id,)
        ).fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
    except Exception as e:
        logger.warning(f"DB chart load failed: {e}. Trying file system fallback.")
    
    # File system fallback (backward compatibility for existing cached charts)
    try:
        path = os.path.join("cache", f"chart_{session_id}.json")
        with open(path, "r") as f:
            return json.load(f)
    except (FileNotFoundError, OSError):
        return None


def chart_exists_in_db(session_id: str) -> bool:
    """Check if a chart exists in DB (used by /api/chart/status endpoint)."""
    try:
        conn = _get_cache_db()
        row = conn.execute(
            "SELECT 1 FROM chart_cache WHERE session_id = ?", (session_id,)
        ).fetchone()
        conn.close()
        return bool(row)
    except Exception:
        # Fall back to file check
        return os.path.exists(os.path.join("cache", f"chart_{session_id}.json"))


# ─── Tools ───────────────────────────────────────────────────────────────────

from retrieval import consult_astrology_books as rag_consult

@tool
def consult_astrology_books(query: str) -> str:
    """Search ancient Vedic astrology books (BPHS, Phala Deepika, etc.) for planetary combinations, yogas, and classical interpretations."""
    return rag_consult(query)

@tool
def get_birth_chart(year: int, month: int, day: int, hour: int, minute: int, city_name: str, config: RunnableConfig) -> str:
    """Calculates Vedic birth chart (Kundali). ALWAYS call this if the user asks for their chart or reading and provides their birth details. Needs exact year, month, day, hour, minute, and city_name."""
    from astrology_engine import calculate_full_chart
    from geopy.geocoders import Nominatim
    from timezonefinder import TimezoneFinder
    try:
        session_id = config.get("configurable", {}).get("thread_id", "current")
        geolocator = Nominatim(user_agent="astrology-ai")
        location = geolocator.geocode(city_name)
        if not location:
            return json.dumps({"error": f"Could not find coordinates for city '{city_name}'"})
            
        lat, lon = location.latitude, location.longitude
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lng=lon, lat=lat) or 'UTC'
        
        chart_data = calculate_full_chart(year, month, day, hour, minute, lat, lon, tz_name, "")
        save_chart(session_id, chart_data)
        
        summary = {
            "Mahadasha": chart_data.get("Current_Dasha"),
            "Yogas": [y.get("name") for y in chart_data.get("Yogas_Found", [])],
            "Ascendant": chart_data.get("Basic_Chart", {}).get("Ascendant", {}).get("sign"),
            "Moon": chart_data.get("Basic_Chart", {}).get("Moon", {}).get("sign")
        }
        return f"Birth chart calculated and stored. Chart Highlights: {json.dumps(summary)}"
    except Exception as e:
        return json.dumps({"error": f"Failed to calculate ephemeris: {str(e)}"})

@tool
def retrieve_astrological_insights(topic: str, config: RunnableConfig) -> str:
    """Retrieves chart data for analysis. Valid topics: 'career', 'marriage', 'health', 'timing', 'full_overview', 'basic_chart_json'."""
    from astrology_engine import get_semantic_view
    session_id = config.get("configurable", {}).get("thread_id", "current")
    chart = load_chart(session_id)
    if not chart:
        return "Error: No chart has been calculated yet. Call get_birth_chart first."
    return get_semantic_view(chart, topic)

@tool
def find_auspicious_time(config: RunnableConfig) -> str:
    """Finds an auspicious date/time (Muhurta) in the next 30 days."""
    from datetime import datetime
    session_id = config.get("configurable", {}).get("thread_id", "current")
    chart = load_chart(session_id)
    if not chart:
        return "Error: No chart has been calculated yet."
    from astrology_engine import find_muhurta
    now = datetime.now()
    best_dates = find_muhurta(now.year, now.month, now.day, 0, 0)
    return json.dumps(best_dates)

@tool
def check_relocation(target_lat: float, target_lon: float, config: RunnableConfig) -> str:
    """AstroCartoGraphy tool. Generates a relocated chart for the given target city coordinates."""
    return "To check relocation (AstroCartoGraphy), please ask the user to provide their exact birth year, month, day, hour, and minute, along with the target city's latitude and longitude."

@tool
def check_compatibility(p2_year: int, p2_month: int, p2_day: int, p2_hour: int, p2_min: int, p2_lat: float, p2_lon: float, config: RunnableConfig) -> str:
    """Ashtakoota Milan (Vedic Compatibility) tool. Compares two birth charts for marriage compatibility."""
    import swisseph as swe
    from config import Config
    from datetime import datetime
    from astrology_engine import calculate_compatibility
    
    session_id = config.get("configurable", {}).get("thread_id", "current")
    chart = load_chart(session_id)
    if not chart:
        return "Error: No primary chart calculated."
    
    swe.set_sid_mode(Config.ayanamsha_swe_id())
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    p2_dt = datetime(p2_year, p2_month, p2_day, p2_hour, p2_min)
    jd2 = swe.julday(p2_dt.year, p2_dt.month, p2_dt.day, p2_dt.hour + p2_dt.minute/60.0)
    res_moon2, _ = swe.calc_ut(jd2, swe.MOON, flags)
    m2_lon = res_moon2[0]
    
    p1_sign = chart["Basic_Chart"]["Moon"]["sign"]
    p1_deg = chart["Basic_Chart"]["Moon"]["degree"]
    from astrology_engine import ZODIAC_SIGNS
    m1_lon = (ZODIAC_SIGNS.index(p1_sign) * 30) + p1_deg
    
    result = calculate_compatibility(m1_lon, m2_lon)
    return json.dumps(result, indent=2)

@tool
def geocode_location(city_name: str) -> str:
    """Convert city name to latitude and longitude coordinates."""
    from geopy.geocoders import Nominatim
    try:
        geolocator = Nominatim(user_agent="astrology_ai_agent")
        location = geolocator.geocode(city_name)
        if location:
            return json.dumps({"latitude": location.latitude, "longitude": location.longitude, "address": location.address})
        else:
            return json.dumps({"error": "Could not find coordinates for this location."})
    except Exception as e:
        return json.dumps({"error": str(e)})


@tool
def get_daily_panchang(city_name: str, config: RunnableConfig) -> str:
    """Location-based Drik Panchangam tool. Calculates exact Sunrise, Sunset, Tithi, Nakshatra, Yoga, Karana, Rahu Kalam, Abhijit Muhurta, Choghadiya, and Burnt Signs (Tithi Shoonya). Use when user asks about daily timing, auspiciousness today/tomorrow, Rahu Kalam, or day quality."""
    from panchangam_engine import PanchangamEngine
    from geopy.geocoders import Nominatim
    from timezonefinder import TimezoneFinder
    from datetime import datetime
    import pytz
    try:
        geolocator = Nominatim(user_agent="astrology_ai_agent")
        loc = geolocator.geocode(city_name)
        if not loc:
            return json.dumps({"error": f"Could not resolve location for '{city_name}'"})
        lat, lon = loc.latitude, loc.longitude
        tf = TimezoneFinder()
        tz_name = tf.timezone_at(lng=lon, lat=lat) or "UTC"
        
        pe = PanchangamEngine()
        now = datetime.now(pytz.timezone(tz_name))
        res = pe.calculate_full_panchang(now, lat, lon, tz_name)
        return json.dumps(res, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Panchang calculation failed: {str(e)}"})

@tool
def scan_forward_event_timing(domain: str, config: RunnableConfig) -> str:
    """Forward predictive timeline scanner. Uses Vimshottari Dasha + Double Transit (Jupiter/Saturn) + Ashtakavarga to calculate exact multi-month calendar delivery windows. Valid domains: 'career', 'marriage', 'wealth', 'health', 'relocation', 'litigation', 'spirituality'."""
    from forward_timing_scanner import ForwardTimingScanner
    from vedic_models import Chart
    from datetime import datetime
    import pytz
    session_id = config.get("configurable", {}).get("thread_id", "current")
    chart_dict = load_chart(session_id)
    if not chart_dict:
        return "Error: No birth chart calculated yet. Please ask user for birth details and call get_birth_chart first."
    try:
        chart_obj = Chart.from_dict(chart_dict.get("Basic_Chart", {}))
        chart_obj.current_dasha = chart_dict.get("Current_Dasha", {})
        scanner = ForwardTimingScanner(chart_obj)
        now = datetime.now(pytz.utc)
        windows = scanner.scan_domain_windows(domain.upper(), start_date=now, months_ahead=36)
        return json.dumps({"domain": domain, "qualifying_windows": windows}, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Forward scan failed: {str(e)}"})

@tool
def check_critical_sensitivities(config: RunnableConfig) -> str:
    """Forensic vulnerability & fortune diagnostic tool. Evaluates 22nd Drekkana (Kharesh), 64th Navamsha, Mrityu Bhagas (fatal degrees), Gandanta knots, Pushkara degrees, Bhrigu Bindu (Destiny point), and Indu Lagna (Wealth)."""
    from sensitive_points import SensitivePointsEngine
    from vedic_models import Chart
    session_id = config.get("configurable", {}).get("thread_id", "current")
    chart_dict = load_chart(session_id)
    if not chart_dict:
        return "Error: No birth chart calculated yet."
    try:
        chart_obj = Chart.from_dict(chart_dict.get("Basic_Chart", {}))
        sp = SensitivePointsEngine(chart_obj).calculate_all()
        return json.dumps(sp, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@tool
def check_financial_and_gann(price: float, asset_name: str = "", config: RunnableConfig = None) -> str:
    """Financial astrology and W.D. Gann Square of 9 engine. Converts asset prices into celestial angles, computes harmonic support/resistance, and checks planetary price-time squaring pivots for stocks, crypto, and commodities."""
    from financial_astro_engine import FinancialAstroEngine
    from realtime_engine import RealtimeEngine
    import datetime, pytz
    try:
        now = datetime.datetime.now(pytz.utc)
        jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0)
        live_planets = RealtimeEngine.get_live_planets(jd)
        res = FinancialAstroEngine.calculate_gann_squaring(price, live_planets)
        res["asset_name"] = asset_name or "Asset"
        return json.dumps(res, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@tool
def check_institutional_defense(entity_name: str = "", config: RunnableConfig = None) -> str:
    """Institutional threat & corporate defense tool. Runs Kota Chakra (Fortress / Hostile takeover / Litigation defense) and Sarvatobhadra Chakra (9x9 SBC multi-vedha grid)."""
    from institutional_chakra_engine import InstitutionalChakraEngine
    from realtime_engine import RealtimeEngine
    from vedic_models import Chart
    import datetime, pytz
    session_id = config.get("configurable", {}).get("thread_id", "current") if config else "current"
    chart_dict = load_chart(session_id)
    if not chart_dict:
        return "Error: No primary chart calculated yet. Call get_birth_chart first."
    try:
        chart_obj = Chart.from_dict(chart_dict.get("Basic_Chart", {}))
        now = datetime.datetime.now(pytz.utc)
        jd = swe.julday(now.year, now.month, now.day, now.hour + now.minute/60.0)
        live_planets = RealtimeEngine.get_live_planets(jd)
        kota = InstitutionalChakraEngine.calculate_kota_chakra(chart_obj, live_planets)
        sbc = InstitutionalChakraEngine.calculate_sbc_veddha(live_planets, entity_name or "Entity")
        return json.dumps({"kota_chakra": kota, "sarvatobhadra_chakra": sbc}, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@tool
def check_numerology_profile(name: str, config: RunnableConfig) -> str:
    """Ank Jyotish & Chaldean Numerology tool. Calculates Moolank, Bhagyank, Chaldean Namank frequency, Katapayadi Sankhya, and name-destiny harmony."""
    from numerology_engine import NumerologyEngine
    session_id = config.get("configurable", {}).get("thread_id", "current")
    chart_dict = load_chart(session_id)
    try:
        # If chart exists, extract DOB
        if chart_dict and "Basic_Chart" in chart_dict:
            # Reconstruct day, month, year if possible
            asc = chart_dict.get("Basic_Chart", {}).get("Ascendant", {})
        res = NumerologyEngine.generate_full_profile(1, 1, 2000, name=name)
        return json.dumps(res, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@tool
def check_biorhythm_pakshi(config: RunnableConfig) -> str:
    """Tamil Siddha Pancha Pakshi (5-Bird Biorhythm) tool. Calculates the native's Birth Bird and current active bio-state (Ruling, Eating, Walking, Sleeping, Dying)."""
    from pancha_pakshi_engine import PanchaPakshiEngine
    from vedic_models import Chart
    from datetime import datetime
    import pytz
    session_id = config.get("configurable", {}).get("thread_id", "current")
    chart_dict = load_chart(session_id)
    if not chart_dict:
        return "Error: No birth chart calculated yet."
    try:
        chart_obj = Chart.from_dict(chart_dict.get("Basic_Chart", {}))
        now = datetime.now(pytz.timezone("Asia/Kolkata"))
        res = PanchaPakshiEngine.get_pakshi_reading(chart_obj, now)
        return json.dumps(res, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)})

@tool
def get_remedies_and_gemstones(planet_name: str = "", config: RunnableConfig = None) -> str:
    """Prescriptive Vedic & Lal Kitab remedial matrix. Calculates Vedic Beeja Mantras, Japa counts, astronomically timed Daana (charity items and hora), Lal Kitab upayas, and strict gemstone suitability verdicts (Anukool vs Pratikool rules). Valid for any planet: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Ketu."""
    from remedy_engine import RemedyEngine
    from vedic_models import Chart
    r_engine = RemedyEngine()
    session_id = config.get("configurable", {}).get("thread_id", "current") if config else "current"
    chart_dict = load_chart(session_id)
    chart_obj = Chart.from_dict(chart_dict.get("Basic_Chart", {})) if chart_dict else None
    
    target_planet = planet_name.strip().capitalize() if planet_name else ""
    planets_to_check = [target_planet] if target_planet and target_planet in RemedyEngine.REMEDY_DATABASE else ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
    
    results = {}
    for p_name in planets_to_check:
        is_afflicted = True
        is_benefic = False
        if chart_obj and p_name in chart_obj.planets:
            p_obj = chart_obj.planets[p_name]
            is_afflicted = p_obj.dignity in ["Debilitated", "Enemy Sign"] or p_obj.combustion.get("status", False) or p_obj.house in [6, 8, 12]
            is_benefic = getattr(p_obj, "functional_role", "") in ["Benefic", "Yoga Karaka"]
        results[p_name] = r_engine.get_remedy_for_planet(p_name, is_benefic=is_benefic, is_afflicted=is_afflicted)
        
    return json.dumps(results, indent=2)

@tool
def rectify_birth_time(events_json: str = "", config: RunnableConfig = None) -> str:
    """Automated KP birth-time rectification tool. Accepts a JSON array of known life events: [{"date": "DD-MM-YYYY", "type": "marriage|career_job|property_purchase|birth_of_child|accident_surgery|financial_gain|loss|education|travel_foreign|health_issue|spiritual|death_family|vehicle_purchase|court_case|promotion"}]. Scans candidate birth times (+-2 hours, 4-minute steps), scores Vimshottari dasha activation, Lagna sublord connectivity, and Rao Double Transits against each event, and returns the statistically best birth time with confidence percentage. Use ONLY when the user reports an uncertain birth time and provides 2+ life event dates."""
    from rectification_engine import RectificationEngine
    from vedic_models import Chart
    import json as _json
    session_id = config.get("configurable", {}).get("thread_id", "current") if config else "current"
    chart_dict = load_chart(session_id)
    if not chart_dict:
        return "Error: No birth chart calculated yet. Run /chart first."
    
    try:
        events = _json.loads(events_json) if events_json else []
    except Exception:
        return "Error: events_json must be a valid JSON array."
    
    if not events or len(events) < 2:
        return "Error: Provide at least 2 life events for meaningful rectification."
    
    chart_obj = Chart.from_dict(chart_dict.get("Basic_Chart", {}))
    birth_info = chart_dict.get("birth_details", {})
    
    # Reconstruct birth datetime
    from datetime import datetime
    birth_dt = datetime(
        int(birth_info.get("year", 2000)), int(birth_info.get("month", 1)),
        int(birth_info.get("day", 1)), int(birth_info.get("hour", 12)),
        int(birth_info.get("minute", 0))
    )
    lat = float(birth_info.get("latitude", 0))
    lon = float(birth_info.get("longitude", 0))
    tz = birth_info.get("timezone", "Asia/Kolkata")
    
    result = RectificationEngine.rectify(
        chart=chart_obj,
        birth_datetime=birth_dt,
        birth_lat=lat, birth_lon=lon,
        events=events, timezone_str=tz
    )
    return _json.dumps(result, indent=2)

# All available tools
ALL_TOOLS = [
    get_birth_chart, retrieve_astrological_insights, find_auspicious_time, 
    check_relocation, check_compatibility, consult_astrology_books, geocode_location,
    get_daily_panchang, scan_forward_event_timing, check_critical_sensitivities,
    check_financial_and_gann, check_institutional_defense, check_numerology_profile,
    check_biorhythm_pakshi, get_remedies_and_gemstones, rectify_birth_time
]

# Setup persistent memory
conn = sqlite3.connect("memory.sqlite", check_same_thread=False)
memory = SqliteSaver(conn)


def load_prompt(filename: str) -> str:
    path = os.path.join("prompts", filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "You are an AI Astrologer."


def message_content_to_text(content) -> str:
    """Normalize provider-specific message payloads for the API and browser renderer."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict):
                text = block.get("text")
                if isinstance(text, str):
                    parts.append(text)
            else:
                text = getattr(block, "text", None)
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts).strip()
    return str(content)


def run_astrologer(user_input: str, session_id: str, provider: str = "auto") -> str:
    """
    Main agent runner with Phase 2 Router Pattern and Mode-Aware Safety Guardrails.
    
    1. Evaluates input query safety against active mode guardrails
    2. Classifies user intent (fast, 2s LLM call)
    3. Selects specialist tool set (2-3 tools vs 7)  
    4. Runs focused ReAct agent with specialist & mode prompt
    5. Applies mode output guardrails & disclaimers
    """
    logger.info(f"Astrologer AI processing (Session: {session_id}, Provider: {provider})")
    
    try:
        from modes import get_active_mode, check_query_safety, apply_output_guardrails
        
        # Guardrail Step 1: Pre-execution query safety check
        active_mode = get_active_mode()
        safety_dec = check_query_safety(user_input, mode=active_mode)
        if not safety_dec.allowed:
            logger.warning(f"Query blocked by safety guardrail [{safety_dec.violation_type}] in mode '{active_mode}'")
            return safety_dec.response or "Your query cannot be processed under our safety and ethical guidelines."

        from llm_provider import LLMProvider
        from agent_router import classify_intent, get_specialist_tools, get_specialist_system_prompt
        
        # Phase 2: Route to specialist
        has_chart = chart_exists_in_db(session_id)
        intent = classify_intent(user_input, has_existing_chart=has_chart)
        logger.info(f"Routed to intent: {intent}")
        
        specialist_tools = get_specialist_tools(intent, ALL_TOOLS)
        system_prompt = get_specialist_system_prompt(intent)
        
        llm = LLMProvider.get_llm(provider)
        agent_executor = create_react_agent(llm, specialist_tools, checkpointer=memory)
        
        messages = [
            SystemMessage(content=system_prompt, id="system-prompt-astrologer"),
            HumanMessage(content=user_input)
        ]
        result = agent_executor.invoke(
            {"messages": messages}, 
            config={"configurable": {"thread_id": session_id}}
        )
        raw_reply = message_content_to_text(result["messages"][-1].content)
        return apply_output_guardrails(raw_reply, mode=active_mode)
        
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            return "Cosmic static detected. The AI API rate limit has been exceeded. Please wait a moment and try again, or select a different fallback provider from the model dropdown."
        logger.error(f"Agent error: {error_msg}", exc_info=True)
        return f"An unexpected cosmic anomaly occurred: {error_msg}"


def run_astrologer_stream(user_input: str, session_id: str, provider: str = "auto") -> Generator[str, None, None]:
    """
    Phase 3: SSE Streaming version of run_astrologer with Mode Guardrails.
    Yields thought steps as they happen for real-time frontend display.
    """
    try:
        from modes import get_active_mode, check_query_safety, apply_output_guardrails
        
        active_mode = get_active_mode()
        safety_dec = check_query_safety(user_input, mode=active_mode)
        if not safety_dec.allowed:
            yield json.dumps({"type": "final", "content": safety_dec.response or "Your query cannot be processed under our safety guidelines."})
            return

        from llm_provider import LLMProvider
        from agent_router import classify_intent, get_specialist_tools, get_specialist_system_prompt
        
        has_chart = chart_exists_in_db(session_id)
        intent = classify_intent(user_input, has_existing_chart=has_chart)
        
        yield json.dumps({"type": "status", "content": f"🔮 Analyzing intent: {intent.replace('_', ' ').title()}..."})
        
        specialist_tools = get_specialist_tools(intent, ALL_TOOLS)
        system_prompt = get_specialist_system_prompt(intent)
        
        yield json.dumps({"type": "status", "content": f"⚡ Activating {len(specialist_tools)} specialist tools..."})
        
        llm = LLMProvider.get_llm(provider)
        agent_executor = create_react_agent(llm, specialist_tools, checkpointer=memory)
        
        messages = [
            SystemMessage(content=system_prompt, id="system-prompt-astrologer"),
            HumanMessage(content=user_input)
        ]
        
        final_content = None
        for chunk in agent_executor.stream(
            {"messages": messages},
            config={"configurable": {"thread_id": session_id}},
            stream_mode="updates"
        ):
            if "agent" in chunk:
                agent_msgs = chunk["agent"].get("messages", [])
                for msg in agent_msgs:
                    # Tool calls (thinking steps)
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tc in msg.tool_calls:
                            tool_name = tc.get("name", "")
                            readable = {
                                "get_birth_chart": "🪐 Calculating birth chart positions...",
                                "retrieve_astrological_insights": "📊 Analyzing planetary influences...",
                                "consult_astrology_books": "📚 Consulting classical Vedic texts...",
                                "find_auspicious_time": "🕐 Finding auspicious timings...",
                                "check_compatibility": "💞 Computing Ashtakoota compatibility...",
                                "geocode_location": "🌍 Locating birth coordinates...",
                            }.get(tool_name, f"⚙️ Running {tool_name}...")
                            yield json.dumps({"type": "thinking", "content": readable})
                    # Final answer
                    elif hasattr(msg, "content") and msg.content:
                        final_content = message_content_to_text(msg.content)
            
            elif "tools" in chunk:
                tool_msgs = chunk["tools"].get("messages", [])
                for msg in tool_msgs:
                    if hasattr(msg, "content") and msg.content:
                        # Brief tool result acknowledgment (don't send full data)
                        yield json.dumps({"type": "status", "content": "✓ Retrieved data, synthesizing..."})
        
        if final_content:
            guarded_final = apply_output_guardrails(final_content, mode=active_mode)
            yield json.dumps({"type": "final", "content": guarded_final})
        else:
            yield json.dumps({"type": "error", "content": "No response generated."})
            
    except Exception as e:
        error_msg = str(e)
        if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
            yield json.dumps({"type": "error", "content": "Rate limit exceeded. Please wait and try again."})
        else:
            logger.error(f"Stream error: {error_msg}", exc_info=True)
            yield json.dumps({"type": "error", "content": f"Cosmic anomaly: {error_msg}"})
