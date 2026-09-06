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

# Patterns for speculative gambling / lotteries (blocked in client_safe mode)
GAMBLING_PATTERNS = [
    r"\b(lottery|lotto|powerball|mega\s*millions)\s+(number|numbers|winning\s+numbers|prediction)\b",
    r"\b(which|what)\s+(lottery|roulette|casino|slot|betting)\s+(number|ticket|horse)\s+(will\s+win|should\s+i\s+buy|should\s+i\s+bet)\b",
    r"\bhow\s+to\s+win\s+(the\s+lottery|casino|gambling|sports\s+bet)\s+using\s+astrology\b",
    r"\bgive\s+me\s+(lucky\s+lottery\s+numbers|winning\s+numbers\s+for\s+today)\b",
]

# Patterns for infidelity surveillance / partner spying (blocked in client_safe mode)
INFIDELITY_SPYING_PATTERNS = [
    r"\b(is\s+my|did\s+my|has\s+my)\s+(wife|husband|partner|girlfriend|boyfriend|spouse|ex)\s+(cheating|sleeping\s+with|have\s+an\s+affair|having\s+an\s+affair|betraying\s+me|unfaithful)\b",
    r"\b(who\s+is\s+my|prove\s+my)\s+(wife|husband|partner|spouse)\s+(cheating\s+with|sleeping\s+with)\b",
    r"\b(is\s+this|is\s+my)\s+(child|baby|son|daughter)\s+(really\s+mine|biologically\s+mine|from\s+another\s+man)\b",
]

# Patterns for medical diagnosis replacement (blocked in client_safe mode)
MEDICAL_DIAGNOSIS_PATTERNS = [
    r"\b(do\s+i\s+have|diagnose\s+my)\s+(cancer|tumor|stroke|heart\s+attack|fatal\s+disease|aids|hiv)\b",
    r"\b(should\s+i|can\s+i)\s+(stop\s+taking|stop|quit|avoid)\s+(my\s+)?(chemo|chemotherapy|medication|medicine|insulin|prescription|treatment)",
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

GAMBLING_REFUSAL_RESPONSE = """### ⚖️ Dharmic Wealth Principle

Classical Jyotisha strictly discourages speculative gambling, random lottery guessing, or game-of-chance prediction. 

In Vedic tradition, genuine prosperity (*Lakshmi*) is earned through **Dharma and Artha**—skill mastery, disciplined enterprise, righteous contracts, and patient long-term timing. The system evaluates business growth windows and financial accumulation cycles, not gambling bets."""

INFIDELITY_REFUSAL_RESPONSE = """### 🕊️ Relationship Guidance & Privacy Policy

Vedic astrology evaluates mutual astrological synastry, emotional temperament, and communication dynamics between consenting charts. 

The system does not perform surveillance, make infidelity accusations, or judge the private personal conduct of third parties. If you are experiencing relationship distress, we encourage honest communication or licensed relationship counseling."""

MEDICAL_REFUSAL_RESPONSE = """### 🩺 Medical Health Advisory

Astrological analysis evaluates elemental balances (*Ayurvedic Tridoshas: Vata, Pitta, Kapha*) and anatomical sensitivities from a classical preventive perspective.

Astrology cannot diagnose clinical illnesses, replace pathology testing, or advise on altering medical prescriptions. For any physical or medical concern, please consult a qualified licensed healthcare physician immediately."""


def check_query_safety(query: str, mode: str = "client_safe") -> SafetyDecision:
    """
    Evaluates incoming user query against safety & ethics boundaries.
    
    In all modes: Self-harm / suicide queries are immediately redirected to crisis support.
    In client_safe mode:
        - Malicious curses / black magic are refused.
        - Speculative gambling / lottery requests are refused.
        - Infidelity / partner surveillance requests are refused.
        - Clinical medical diagnosis / stopping medication is refused.
        - Fatal death timestamps are bounded to classical vitality tiers.
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
            
    # 2. Malicious Intent / Cursing Check (Universal across ALL modes)
    for pat in MALICIOUS_PATTERNS:
        if re.search(pat, q_lower):
            return SafetyDecision(
                allowed=False,
                violation_type="MALICIOUS_INTENT",
                response=MALICIOUS_INTENT_RESPONSE,
                category="ETHICAL_BOUNDARY"
            )
            
    # 3. Client-Safe Public Nerfed Guardrails (Active only in client_safe mode)
    if mode == "client_safe":
        # 3a. Gambling & Lotteries
        for pat in GAMBLING_PATTERNS:
            if re.search(pat, q_lower):
                return SafetyDecision(
                    allowed=False,
                    violation_type="GAMBLING_SPECULATION",
                    response=GAMBLING_REFUSAL_RESPONSE,
                    category="SPECULATION_BLOCK"
                )
                
        # 3b. Infidelity & Third-Party Surveillance
        for pat in INFIDELITY_SPYING_PATTERNS:
            if re.search(pat, q_lower):
                return SafetyDecision(
                    allowed=False,
                    violation_type="INFIDELITY_SPYING",
                    response=INFIDELITY_REFUSAL_RESPONSE,
                    category="PRIVACY_BLOCK"
                )
                
        # 3c. Medical Diagnosis / Stopping Rx
        for pat in MEDICAL_DIAGNOSIS_PATTERNS:
            if re.search(pat, q_lower):
                return SafetyDecision(
                    allowed=False,
                    violation_type="MEDICAL_DIAGNOSIS_REPLACEMENT",
                    response=MEDICAL_REFUSAL_RESPONSE,
                    category="MEDICAL_BLOCK"
                )
                
        # 3d. Exact Fatal Death Timestamp Request
        for pat in FATAL_TIMESTAMP_PATTERNS:
            if re.search(pat, q_lower):
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
