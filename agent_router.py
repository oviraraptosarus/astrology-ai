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
    "BIRTH_CHART": """You are an elite Vedic astrology chart calculator. Your ONLY job is to:
1. Extract birth details from the user message (year, month, day, hour, minute, city)
2. Call get_birth_chart with those exact parameters
3. Call retrieve_astrological_insights with topic='full_overview'
4. Provide a detailed reading of the chart

If birth details are missing, ask for them specifically. Do not ramble.""",

    "COMPATIBILITY": """You are an elite Vedic compatibility analyst specializing in Ashtakoota Milan and Synastry.
Your job: Calculate and interpret marriage compatibility between two people, and analyze alliance/marriage timing if asked.
Extract BOTH people's birth details, calculate their charts, run compatibility check.""",

    "TIMING": """You are a Muhurta (auspicious timing) and Dasha specialist.
Your job: Find auspicious timings and interpret dasha periods.
If the user provides birth details and the chart is not yet calculated, you MUST use the get_birth_chart tool immediately.
Call find_auspicious_time and retrieve_astrological_insights with topic='timing'.""",

    "TRANSIT": """You are a transit analysis specialist. 
Your job: Analyze current planetary transits and their effects on the natal chart.
If the user provides birth details and the chart is not yet calculated, you MUST use the get_birth_chart tool immediately.
Use retrieve_astrological_insights with topic='timing' and consult_astrology_books.""",

    "COMPOUND": """You are a master Vedic astrologer handling a multi-domain inquiry.
Your job: Analyze multiple facets of the user's inquiry (e.g. compatibility + career timing + life events).
Calculate all necessary charts and synthesize across both domains without omitting any part of the user's question.""",

    "GENERAL": """You are an expert Vedic astrologer and Jyotisha scholar.
If the user provides their birth details, you MUST immediately call the get_birth_chart tool to calculate their chart. This tool is available to you!
Consult classical texts and the user's chart to provide deep, accurate interpretations.
Use consult_astrology_books to find relevant classical references.""",
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
    This shrinks the agent's tool selection space from 7 to 2-3 tools,
    dramatically reducing hallucination and improving speed.
    """
    tool_names = SPECIALIST_TOOL_SETS.get(intent, SPECIALIST_TOOL_SETS["GENERAL"])
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
