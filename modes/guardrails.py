"""
ASTROLOGY AI GUARDRAILS & QUERY SAFETY MODULE
=============================================
Provides deterministic query safety, ethical filtering, and output framing
for public/client deployments while respecting the active execution mode.
"""

import re
from typing import Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class SafetyDecision:
    allowed: bool
    violation_type: Optional[str] = None
    response: Optional[str] = None
    disclaimer: Optional[str] = None
    category: Optional[str] = None


# Patterns that indicate crisis / self-harm / suicide (always blocked in all modes)
SELF_HARM_PATTERNS = [
    r"\b(how\s+(can|do|should|to)\s+i\s+)?(kill|hang|shoot|poison|cut|drown|end)\s+(my\s*self|my\s+life)\b",
    r"\b(suicide|suicidal|commit\s+suicide|ending\s+my\s+life)\b",
    r"\b(best|right|easiest|quickest)\s+way\s+to\s+(die|kill\s+myself|commit\s+suicide)\b",
    r"\bwhen\s+will\s+i\s+(die\s+by\s+suicide|kill\s+myself)\b",
    r"\bi\s+want\s+to\s+(die|disappear|kill\s+myself|end\s+it\s+all)\b",
]

# Patterns for malicious harm / curses / black magic targeting others
MALICIOUS_PATTERNS = [
    r"\b(how\s+to|can\s+you)\s+(curse|hex|destroy|kill|harm|ruin|attack)\s+(someone|somebody|my\s+enemy|my\s+boss|my\s+ex|my\s+partner|others)\b",
    r"\b(black\s+magic|marana\s+mantra|vashikaran\s+to\s+destroy|evil\s+spell|curse)\s+to\s+(kill|harm|punish|ruin|destroy|damage)\b",
    r"\bwhen\s+will\s+(my\s+(enemy|boss|father|mother|spouse|partner|ex|husband|wife)|he|she|they|someone)\s+die\s+so\s+i\s+(get|inherit|take|collect)\b",
]

# Patterns for exact fatal death timestamping (bounded in client_safe mode)
FATAL_TIMESTAMP_PATTERNS = [
    r"\b(exact\s+date|exact\s+day|exact\s+time|what\s+day)\s+(will\s+i|of\s+my)\s+die\b",
    r"\bwhen\s+exactly\s+(will|am\s+i\s+going\s+to)\s+die\b",
    r"\bpredict\s+my\s+(exact\s+death\s+date|day\s+of\s+death)\b",
]

ADVISORY_DISCLAIMER = (
    "\n\n---\n*✦ Advisory Notice: Astrological readings reflect classical symbolic potentials and planetary cycles. "
    "Jyotisha emphasizes Kriyamana Karma (free will, conscious choice, and proactive discipline). "
    "For medical, psychological, legal, or major financial decisions, always consult qualified licensed professionals.*"
)

CRISIS_SUPPORT_RESPONSE = """### 💛 Support & Crisis Resources

If you are experiencing overwhelming feelings, distress, or thoughts of self-harm, please know that support is available right now. Astrological consultations cannot evaluate mental health crises, but dedicated professionals are available 24/7:

- **United States & Canada:** Call or text **988** (National Suicide & Crisis Lifeline) or chat at [988lifeline.org](https://988lifeline.org)
- **United Kingdom:** Call **111** (NHS Mental Health Services) or call **116 123** (Samaritans)
- **India:** Call **1800-599-0019** (KIRAN National Mental Health Helpline) or **9152987821** (AASRA)
- **International:** Find local emergency support worldwide at [findahelpline.com](https://findahelpline.com) or [befrienders.org](https://www.befrienders.org)

Please reach out to a professional or a trusted person in your life. You do not have to carry this alone."""

MALICIOUS_INTENT_RESPONSE = """### 🛡️ Ethical Astrology Directive

Classical Jyotisha (*Brihat Parashara Hora Shastra* and *Vedanga Jyotisha*) is a sacred science of illumination (*Jyoti* = Light), self-knowledge, and dharmic alignment. 

The system does not generate destructive spells, curses, or predictive weaponization against others. Consultations are strictly oriented toward self-awareness, personal karma management, and ethical life navigation."""


def check_query_safety(query: str, mode: str = "client_safe") -> SafetyDecision:
    """
    Evaluates incoming user query against safety & ethics boundaries.
    
    In all modes: Self-harm / suicide queries are immediately redirected to crisis support.
    In client_safe mode: Malicious intent is refused; fatal timestamp queries receive bounded advice.
    In unconstrained mode: Legitimate astrological questions proceed with unmoderated astronomical calculations.
    """
    if not query or not query.strip():
        return SafetyDecision(allowed=True)
        
    q_lower = query.strip().lower()
    
    # 1. Absolute Self-Harm / Crisis Check (Universal across ALL modes)
    for pat in SELF_HARM_PATTERNS:
        if re.search(pat, q_lower):
            return SafetyDecision(
                allowed=False,
                violation_type="SELF_HARM",
                response=CRISIS_SUPPORT_RESPONSE,
                category="CRISIS_INTERVENTION"
            )
            
    # 2. Malicious Intent / Cursing Check
    for pat in MALICIOUS_PATTERNS:
        if re.search(pat, q_lower):
            return SafetyDecision(
                allowed=False,
                violation_type="MALICIOUS_INTENT",
                response=MALICIOUS_INTENT_RESPONSE,
                category="ETHICAL_BOUNDARY"
            )
            
    # 3. Exact Fatal Date Request in Client-Safe Mode
    if mode == "client_safe":
        for pat in FATAL_TIMESTAMP_PATTERNS:
            if re.search(pat, q_lower):
                # We allow the query to proceed, but flag it for bounded vitality framing
                return SafetyDecision(
                    allowed=True,
                    violation_type=None,
                    disclaimer=ADVISORY_DISCLAIMER,
                    category="BOUNDED_LONGEVITY"
                )
                
    return SafetyDecision(allowed=True, disclaimer=ADVISORY_DISCLAIMER if mode == "client_safe" else None)


def apply_output_guardrails(response_text: str, mode: str = "client_safe") -> str:
    """
    Applies mode-specific output formatting and disclaimers.
    In client_safe mode: Appends standard advisory disclaimer if not already present.
    In unconstrained mode: Returns raw text without disclaimer padding.
    """
    if not response_text:
        return ""
        
    if mode == "client_safe":
        if "✦ Advisory Notice" not in response_text and "Advisory Notice:" not in response_text:
            return response_text.rstrip() + ADVISORY_DISCLAIMER
            
    return response_text


def get_client_disclaimer() -> str:
    """Return the client-safe advisory disclaimer."""
    return ADVISORY_DISCLAIMER
