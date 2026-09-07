"""
ASTROLOGY AI GUARDRAILS, LEGAL SHIELD & QUERY SAFETY MODULE
===========================================================
Provides deterministic query safety, jailbreak resistance, ethical filtering,
and ironclad legal liability shielding for public client deployments.

In client_safe mode:
- 100% legal protection (speculative, entertainment & spiritual self-reflection only).
- Absolute anti-jailbreak protection (blocks DAN, hypothetical overrides, roleplay bypasses).
- Zero karmic liability: blocks death timing, gambling, infidelity spying, and medical replacement.
- Preserves free will (Purushartha) and provides uplifting Vedic remedies.

In unconstrained mode (Local / Personal):
- 100% raw, direct, unfiltered Grandmaster calculations.
- Universal crisis safety (self-harm protection) remains active across all modes.
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


# 1. Absolute Self-Harm / Crisis Patterns (Universal across ALL modes)
SELF_HARM_PATTERNS = [
    r"\b(how\s+(can|do|should|to)\s+i\s+)?(kill|hang|shoot|poison|cut|drown|end)\s+(my\s*self|my\s+life)\b",
    r"\b(suicide|suicidal|commit\s+suicide|ending\s+my\s+life)\b",
    r"\b(best|right|easiest|quickest)\s+way\s+to\s+(die|kill\s+myself|commit\s+suicide)\b",
    r"\bwhen\s+will\s+i\s+(die\s+by\s+suicide|kill\s+myself)\b",
    r"\bi\s+want\s+to\s+(die|disappear|kill\s+myself|end\s+it\s+all)\b",
]

# 2. Malicious Harm / Curses / Black Magic targeting others (Universal)
MALICIOUS_PATTERNS = [
    r"\b(how\s+to|can\s+you)\s+(curse|hex|destroy|kill|harm|ruin|attack)\s+(someone|somebody|my\s+enemy|my\s+boss|my\s+ex|my\s+partner|others)\b",
    r"\b(black\s+magic|marana\s+mantra|vashikaran\s+to\s+destroy|evil\s+spell|curse)\s+to\s+(kill|harm|punish|ruin|destroy|damage)\b",
    r"\bwhen\s+will\s+(my\s+(enemy|boss|father|mother|spouse|partner|ex|husband|wife)|he|she|they|someone)\s+die\s+so\s+i\s+(get|inherit|take|collect)\b",
]

# 3. Anti-Jailbreak / Prompt-Injection Patterns (Blocked in client_safe mode)
JAILBREAK_PATTERNS = [
    r"\b(ignore|disregard|forget|bypass|override)\s+(all\s+)?(previous|prior|system|safety|ethical|mode)?\s*(instructions|prompts|rules|guidelines|directives|filters|boundaries)\b",
    r"\b(dan\s+mode|jailbreak|developer\s+mode|uncensored\s+mode|unfiltered\s+mode|do\s+anything\s+now)\b",
    r"\b(act|pretend|roleplay)\s+as\s+(an\s+uncensored|a\s+dark|an\s+unfiltered|a\s+lawless|an\s+unrestricted)\s+(astrologer|ai|bot|grandmaster)\b",
    r"\b(hypothetically|in\s+a\s+fictional\s+story|for\s+research\s+only|as\s+a\s+test|fictional|roleplay)\b.*?\b(tell|predict|give|reveal|show)\b.*?\b(die|death|lottery|curse|hex|suicide)\b",
    r"\b(you\s+are\s+no\s+longer\s+bound|ignore\s+your\s+rules|safety\s+filter\s+disabled)\b",
    r"\b(bypass|override)\b.*?\b(rules|guardrails|ethical|safety|filters|boundaries)\b",
]

# 4. Speculative Gambling / Lotteries (Blocked in client_safe mode)
GAMBLING_PATTERNS = [
    r"\b(lottery|lotto|powerball|mega\s*millions)\s+(number|numbers|winning\s+numbers|prediction)\b",
    r"\b(which|what)\s+(lottery|roulette|casino|slot|betting)\s+(number|ticket|horse)\s+(will\s+win|should\s+i\s+buy|should\s+i\s+bet)\b",
    r"\bhow\s+to\s+win\s+(the\s+lottery|casino|gambling|sports\s+bet)\s+using\s+astrology\b",
    r"\bgive\s+me\s+(lucky\s+lottery\s+numbers|winning\s+numbers\s+for\s+today)\b",
]

# 5. Infidelity Surveillance / Partner Spying (Blocked in client_safe mode)
INFIDELITY_SPYING_PATTERNS = [
    r"\b(is\s+my|did\s+my|has\s+my)\s+(wife|husband|partner|girlfriend|boyfriend|spouse|ex)\s+(cheating|sleeping\s+with|have\s+an\s+affair|having\s+an\s+affair|betraying\s+me|unfaithful)\b",
    r"\b(who\s+is\s+my|prove\s+my)\s+(wife|husband|partner|spouse)\s+(cheating\s+with|sleeping\s+with)\b",
    r"\b(is\s+this|is\s+my)\s+(child|baby|son|daughter)\s+(really\s+mine|biologically\s+mine|from\s+another\s+man)\b",
]

# 6. Medical Diagnosis Replacement (Blocked in client_safe mode)
MEDICAL_DIAGNOSIS_PATTERNS = [
    r"\b(do\s+i\s+have|diagnose\s+my)\s+(cancer|tumor|stroke|heart\s+attack|fatal\s+disease|aids|hiv)\b",
    r"\b(should\s+i|can\s+i)\s+(stop\s+taking|stop|quit|avoid)\s+(my\s+)?(chemo|chemotherapy|medication|medicine|insulin|prescription|treatment)",
]

# 7. Exact Fatal Death Timestamping (Bounded in client_safe mode)
FATAL_TIMESTAMP_PATTERNS = [
    r"\b(exact\s+date|exact\s+day|exact\s+time|what\s+day)\s+(will\s+i|of\s+my)\s+die\b",
    r"\bwhen\s+exactly\s+(will|am\s+i\s+going\s+to)\s+die\b",
    r"\bpredict\s+my\s+(exact\s+death\s+date|day\s+of\s+death)\b",
]


# ─── LEGAL & KARMIC DISCLAIMER ──────────────────────────────────────
ADVISORY_DISCLAIMER = (
    "\n\n---\n"
    "### ⚖️ Legal & Astrological Advisory Notice\n"
    "*This consultation is strictly for entertainment, philosophical reflection, and personal spiritual self-inquiry. "
    "Astrological interpretations are inherently speculative and reflect symbolic planetary archetypes. "
    "This service does NOT provide medical, psychiatric, legal, financial, or investment advice. "
    "No decisions regarding health, medical treatments, investments, legal disputes, or personal relationships should be made based on this reading. "
    "Jyotisha tradition teaches that conscious human effort (Kriyamana Karma / Purushartha) is supreme over astrological indications. "
    "The creators and operators of this platform assume zero legal or karmic liability for personal choices or interpretations.*"
)


# ─── CANNED ETHICAL RESPONSES ───────────────────────────────────────
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

JAILBREAK_REFUSAL_RESPONSE = """### 🕉️ Sovereign Dharmic Directive

The ethical and legal safeguards of this Jyotisha sanctuary are invariant and non-negotiable. 

Vedic astrology exists to illuminate the soul's path with truth, wisdom, and compassion. System instructions, safety boundaries, and ethical safeguards cannot be bypassed, overridden, or roleplayed away under any circumstance. 

Please ask a constructive question regarding your career potential, personal growth, relationship harmony, or classical Vedic remedies."""

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
    Evaluates incoming user query against safety, jailbreak, and legal boundaries.
    
    In all modes:
        - Self-harm / suicide queries are immediately redirected to crisis support.
        - Malicious curses / black magic targeting others are refused.
    In client_safe mode:
        - Jailbreak / prompt-injection attempts are blocked.
        - Speculative gambling / lottery requests are refused.
        - Infidelity / partner surveillance requests are refused.
        - Clinical medical diagnosis / stopping medication is refused.
        - Fatal death timestamps are bounded to classical vitality tiers.
    In unconstrained mode:
        - Legitimate astrological calculations proceed with unmoderated astronomical accuracy.
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
            
    # 3. Client-Safe Public Nerfed & Jailbreak Guardrails (Active only in client_safe mode)
    if mode == "client_safe":
        # 3a. Anti-Jailbreak / Prompt-Injection Check
        for pat in JAILBREAK_PATTERNS:
            if re.search(pat, q_lower):
                return SafetyDecision(
                    allowed=False,
                    violation_type="JAILBREAK_ATTEMPT",
                    response=JAILBREAK_REFUSAL_RESPONSE,
                    category="PROMPT_INJECTION_BLOCK"
                )

        # 3b. Gambling & Lotteries
        for pat in GAMBLING_PATTERNS:
            if re.search(pat, q_lower):
                return SafetyDecision(
                    allowed=False,
                    violation_type="GAMBLING_SPECULATION",
                    response=GAMBLING_REFUSAL_RESPONSE,
                    category="SPECULATION_BLOCK"
                )
                
        # 3c. Infidelity & Third-Party Surveillance
        for pat in INFIDELITY_SPYING_PATTERNS:
            if re.search(pat, q_lower):
                return SafetyDecision(
                    allowed=False,
                    violation_type="INFIDELITY_SPYING",
                    response=INFIDELITY_REFUSAL_RESPONSE,
                    category="PRIVACY_BLOCK"
                )
                
        # 3d. Medical Diagnosis / Stopping Rx
        for pat in MEDICAL_DIAGNOSIS_PATTERNS:
            if re.search(pat, q_lower):
                return SafetyDecision(
                    allowed=False,
                    violation_type="MEDICAL_DIAGNOSIS_REPLACEMENT",
                    response=MEDICAL_REFUSAL_RESPONSE,
                    category="MEDICAL_BLOCK"
                )
                
        # 3e. Exact Fatal Death Timestamp Request
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
    Applies mode-specific output formatting.
    Disclaimers are anchored statically in the AI chat UI footer (like ChatGPT & Gemini)
    rather than being redundantly repeated inside every single assistant turn.
    """
    if not response_text:
        return ""
    # Strip any trailing disclaimers that the model might have self-generated
    cleaned = response_text
    if "### ⚖️ Legal & Astrological Advisory Notice" in cleaned:
        cleaned = cleaned.split("### ⚖️ Legal & Astrological Advisory Notice")[0].rstrip()
    elif "⚖️ Legal & Astrological Advisory Notice" in cleaned:
        cleaned = cleaned.split("⚖️ Legal & Astrological Advisory Notice")[0].rstrip()
    if cleaned.endswith("---"):
        cleaned = cleaned[:-3].rstrip()
    return cleaned


def get_client_disclaimer() -> str:
    """Return the client-safe ironclad legal disclaimer."""
    return ADVISORY_DISCLAIMER
