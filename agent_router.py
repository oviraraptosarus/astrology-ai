"""
Agent Router — Intent Classification + Specialist Routing
Phase 2 of 10/10 Engine Upgrades

Problem solved:
  The original single-agent pattern forces ONE LLM to read a massive system prompt
  and choose between 7 tools for every query. This causes 60-90s latency and tool
  selection errors.

Solution:
  1. A fast, cheap classifier LLM reads the user's intent in <2s
  2. Routes to a specialist agent that has ONLY the relevant tools
  3. Each specialist has a focused system prompt, reducing hallucination risk

Routes:
  - BIRTH_CHART: "Calculate my chart", "what's my ascendant" 
  - COMPATIBILITY: "Are we compatible", "Ashtakoota milan"
  - TIMING: "When will I get married", "auspicious date", "muhurta"
  - TRANSIT: "What planets are affecting me", "current transits"
  - GENERAL: All other queries (RAG + chat)
"""
import os
import json
import logging
from typing import Literal

logger = logging.getLogger(__name__)

# Intent categories
IntentType = Literal["BIRTH_CHART", "COMPATIBILITY", "TIMING", "TRANSIT", "COMPOUND", "GENERAL"]


INTENT_EXAMPLES = {
    "BIRTH_CHART": [
        "calculate my birth chart", "what is my lagna", "show me my kundali",
        "my ascendant", "planets in my chart", "birth details", "natal chart"
    ],
    "COMPATIBILITY": [
        "are we compatible", "ashtakoota", "milan", "match", "partner compatibility",
        "marriage compatibility", "synastry", "partner chart"
    ],
    "TIMING": [
        "when will", "muhurta", "auspicious", "best time", "dasha", "mahadasha",
        "antardasha", "timing", "prediction for year", "transit period"
    ],
    "TRANSIT": [
        "current planets", "today's transits", "what is affecting me now",
        "current dasha", "sade sati", "rahu ketu transit"
    ],
    "GENERAL": [
        "meaning of", "explain", "what does", "tell me about", "interpret",
        "career", "health", "wealth", "yoga", "dosha"
    ]
}

# Tools for each specialist agent
SPECIALIST_TOOL_SETS = {
    "BIRTH_CHART": ["get_birth_chart", "retrieve_astrological_insights", "geocode_location", "check_critical_sensitivities", "get_remedies_and_gemstones"],
    "COMPATIBILITY": ["check_compatibility", "get_birth_chart", "retrieve_astrological_insights", "scan_forward_event_timing"],
    "TIMING": ["find_auspicious_time", "get_daily_panchang", "scan_forward_event_timing", "check_biorhythm_pakshi", "retrieve_astrological_insights", "get_birth_chart"],
    "TRANSIT": ["retrieve_astrological_insights", "get_daily_panchang", "get_remedies_and_gemstones", "consult_astrology_books", "get_birth_chart", "scan_forward_event_timing"],
    "COMPOUND": ["get_birth_chart", "retrieve_astrological_insights", "check_compatibility", "scan_forward_event_timing", "find_auspicious_time", "get_daily_panchang", "check_critical_sensitivities", "get_remedies_and_gemstones", "consult_astrology_books"],
    "GENERAL": ["retrieve_astrological_insights", "get_remedies_and_gemstones", "scan_forward_event_timing", "check_critical_sensitivities", "check_financial_and_gann", "check_institutional_defense", "check_numerology_profile", "consult_astrology_books", "get_birth_chart"],
}

SPECIALIST_SYSTEM_PROMPTS = {
    "BIRTH_CHART": """You are an authoritative Grandmaster Vedic Astrologer.
Your purpose is to calculate and deliver an exacting, mathematically precise Kundali reading.
- When birth details are given, immediately invoke get_birth_chart and retrieve_astrological_insights with topic='full_overview'.
- Deliver a direct, nuanced synthesis of the Lagna, Chandra Rashi, Nakshatra, functional planetary lordships, and core Yogas.
- Speak with classical depth and authority. Avoid generic LLM filler, artificial cheerleading, and corporate self-help clichés.""",

    "COMPATIBILITY": """You are an authoritative Grandmaster Vedic Compatibility & Synastry Analyst.
- Analyze the 36-point Ashtakoota Guna Milan, Kuja Dosha (Manglik), and planetary synastry between the charts.
- Detail the exact Kootas (Nadi, Bhakoot, Gana, Graha Maitri, Yoni, Tara, Vashya, Varna) with specific karmic dynamics.
- State clear strengths, friction points, and classical remediations directly without robotic table dumps or sugarcoating.""",

    "TIMING": """You are an authoritative Grandmaster Jyotisha Predictive Timing Specialist.
- Interpret active Vimshottari Mahadasha, Antardasha, and Pratyantardasha periods and their direct activation of natal houses.
- Analyze transit activations (K.N. Rao double transit of Jupiter/Saturn, Ashtakavarga bindu support, Gochara Vedha).
- Call retrieve_astrological_insights (topic='timing' or specific domain) and scan_forward_event_timing.
- Provide concrete timing windows with exact peak collision dates and explicit probability percentages (e.g., 'Peak: YYYY-MM-DD (±3 days, 85% probability)').
- Avoid generic corporate advice ('volunteer for projects', 'trust the process'). Focus strictly on classical planetary mechanics, functional lords, and strategic timing.""",

    "TRANSIT": """You are an authoritative Grandmaster Transit & Gochara Specialist.
- Analyze transiting planets relative to the Natal Moon and Lagna (Gochara, Sade Sati, Ashtama Shani, Kantaka Shani).
- Call retrieve_astrological_insights with topic='timing' and consult_astrology_books.
- Detail the exact house transited, kakshya lords, and vedha obstructions with precision.""",

    "COMPOUND": """You are an authoritative Grandmaster Jyotisha Scholar handling a comprehensive multi-domain consultation.
- Synthesize natal promise, active Dasha triads, transits, and divisional confirmations (D9 Navamsha, D10 Dasamsha).
- Deliver a deeply personalized, intellectually rigorous reading with direct authority, zero generic AI boilerplate, and zero conversational filler.""",

    "GENERAL": """You are an authoritative Grandmaster Vedic Astrologer and Jyotisha Scholar.
- Deliver profound, mathematically grounded astrological analysis rooted in Parashari, Jaimini, KP, and classical Nadi principles.
- Use the active chart to detail exact house lordships, planetary dignities, aspects (Drishti), and Nakshatra energies.
- Write with refined, authoritative, and direct tone. Never produce canned corporate advice, repetitive table dumps, or standard chatbot follow-up questions."""
}


def classify_intent(user_message: str, has_existing_chart: bool = False) -> IntentType:
    """
    Classify user intent into a specialist category or COMPOUND multi-intent.
    """
    msg_lower = user_message.lower()
    
    # Check for ontology cross-domain signals
    try:
        from jyotisha_ontology import JyotishaOntology
        cross_links = JyotishaOntology.detect_cross_domain(user_message)
        if len(cross_links) >= 1 and any(kw in msg_lower for kw in ["when", "timing", "how", "partner", "career", "wealth"]):
            logger.info(f"Ontology cross-domain detected {cross_links} -> routing to COMPOUND")
            return "COMPOUND"
    except Exception:
        pass

    detected_intents = []
    if any(kw in msg_lower for kw in ["birth chart", "calculate chart", "kundali", "kundli", "natal chart", "my ascendant", "my lagna", "show my chart"]):
        detected_intents.append("BIRTH_CHART")
    if any(kw in msg_lower for kw in ["compatible", "compatibility", "ashtakoota", "milan", "match making", "synastry", "partner", "relationship"]):
        detected_intents.append("COMPATIBILITY")
    if any(kw in msg_lower for kw in ["muhurta", "auspicious", "best time", "when will", "timing", "future", "next year", "upcoming", "dasha period", "timeline"]):
        detected_intents.append("TIMING")
    if any(kw in msg_lower for kw in ["transit", "sade sati", "current period", "affecting me now", "gochara", "current planets"]):
        detected_intents.append("TRANSIT")
    
    # If multiple distinct intents detected, route to COMPOUND to avoid dropping tools
    if len(detected_intents) >= 2:
        logger.info(f"Multi-intent query detected {detected_intents} -> routing to COMPOUND")
        return "COMPOUND"
    elif len(detected_intents) == 1:
        return detected_intents[0]
    
    return "GENERAL"


def get_specialist_tools(intent: IntentType, all_tools: list) -> list:
    """
    Return only the relevant tools for the given intent.
    In client_safe mode, excludes sensitive or institutional raid tools to prevent abuse.
    In unconstrained mode, allows the full suite of diagnostic tools.
    """
    tool_names = list(SPECIALIST_TOOL_SETS.get(intent, SPECIALIST_TOOL_SETS["GENERAL"]))
    
    # Public Mode Safety Filter: In client_safe mode, omit hostile/institutional defense tools
    try:
        from modes import is_client_safe
        if is_client_safe():
            restricted_tools = {"check_institutional_defense"}
            tool_names = [name for name in tool_names if name not in restricted_tools]
    except Exception:
        pass

    tool_map = {t.name: t for t in all_tools}
    specialist_tools = [tool_map[name] for name in tool_names if name in tool_map]
    
    if not specialist_tools:
        logger.warning(f"No tools found for intent {intent}, using all tools")
        return all_tools
    
    logger.info(f"Router selected {len(specialist_tools)} tools for intent '{intent}': {[t.name for t in specialist_tools]}")
    return specialist_tools


def get_specialist_system_prompt(intent: IntentType) -> str:
    """Return the focused system prompt for this specialist, incorporating active mode directives."""
    base = SPECIALIST_SYSTEM_PROMPTS.get(intent, SPECIALIST_SYSTEM_PROMPTS["GENERAL"])
    
    # Load mode directive
    mode_directive = ""
    try:
        from modes import get_mode_config
        cfg = get_mode_config()
        if hasattr(cfg, "SYSTEM_DIRECTIVE") and cfg.SYSTEM_DIRECTIVE:
            mode_directive = f"### ACTIVE OPERATIONAL DIRECTIVE ({getattr(cfg, 'MODE_NAME', 'MODE')}):\n{cfg.SYSTEM_DIRECTIVE.strip()}\n\n---\n"
    except Exception:
        mode_directive = ""

    # Load the full system prompt and prepend the specialist context
    try:
        prompt_path = os.path.join("prompts", "SYSTEM.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            full_system = f.read()
        # Mode directive + specialist focus first, then full knowledge base
        return f"{mode_directive}{base}\n\n---\n{full_system}"
    except Exception:
        return f"{mode_directive}{base}" if mode_directive else base
