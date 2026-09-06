from typing import Dict, List, Any
from dataclasses import dataclass, field

@dataclass
class CasePrecedent:
    event_id: str
    case_name: str
    natal_inspection: List[str] # What the astrologer observed in the chart
    astrological_rationale: str # The deeper reasoning connecting the observations
    timing_factors: List[str]   # The Dasha/Transit conditions that triggered the event
    outcome: str
    teaching_point: str
    
    def to_dict(self):
        return {
            "case_name": self.case_name,
            "natal_inspection": self.natal_inspection,
            "astrological_rationale": self.astrological_rationale,
            "timing_factors": self.timing_factors,
            "outcome": self.outcome,
            "teaching_point": self.teaching_point
        }

class CaseLibrary:
    """
    Provides structured, canonical astrological case studies for few-shot learning.
    This helps the LLM ground its synthesis in actual astrological precedent.
    Now structured around specific EventProtocols.
    """
    
    CASES = [
        # CAREER EVENTS
        CasePrecedent(
            event_id="career_promotion",
            case_name="Late Bloomer Executive",
            natal_inspection=[
                "Saturn powerfully aspecting the 10th house",
                "Lord of 10th placed in the 8th house",
                "Ruchaka Yoga (Mars in Kendra in own sign) present but not activated until later"
            ],
            astrological_rationale="Saturn's aspect introduces immense early-career friction and delay. The 10th lord in the 8th indicates a career involving hidden forces, research, or sudden shifts. However, the underlying Ruchaka Yoga ensures that once Saturn matures, executive authority is granted.",
            timing_factors=[
                "Mahadasha of Mars (activating Ruchaka Yoga)",
                "Jupiter transit over natal 10th lord"
            ],
            outcome="Early career struggles and delays. However, tremendous success and promotion to C-level in the mid-30s during Mars Dasha.",
            teaching_point="Do not read 10th lord in 8th simply as 'career failure'. Saturn delays but does not deny if Mars provides structural strength."
        ),
        CasePrecedent(
            event_id="job_change",
            case_name="Sudden Industry Shift",
            natal_inspection=[
                "10th lord conjunct Ketu in the 5th house",
                "Mercury (AmK) in retrograde in the 12th house"
            ],
            astrological_rationale="Ketu brings detachment and sudden endings to the signification it conjuncts. The 10th lord with Ketu suggests a career that suddenly changes direction. Retrograde AmK in 12th points to foreign environments or behind-the-scenes work.",
            timing_factors=[
                "Antardasha of Ketu",
                "Saturn transit over natal Moon (Sade Sati)"
            ],
            outcome="Unexpected resignation from a stable job, followed by a pivot into a completely different industry (foreign tech startup).",
            teaching_point="Ketu AD often brings sudden detachments. A job change here is not necessarily a 'loss' but a karmic pivot."
        ),
        
        # MARRIAGE EVENTS
        CasePrecedent(
            event_id="marriage_delay",
            case_name="Delayed but Stable Marriage",
            natal_inspection=[
                "Saturn placed in the 7th house",
                "7th lord is Exalted in Navamsha (D9)",
                "Upapada Lagna (UL) aspected by Jupiter"
            ],
            astrological_rationale="Saturn in the 7th inherently slows down the maturation of relationships. However, the exalted 7th lord in D9 and Jupiter's blessing on UL guarantee a high-quality partner, provided the native waits.",
            timing_factors=[
                "Mahadasha of 7th lord",
                "Jupiter transit over 7th house"
            ],
            outcome="Marriage occurred late (after age 30), but was highly stable and enduring.",
            teaching_point="Saturn in 7th causes delay. Do not predict denial unless the 7th lord is severely afflicted in both D1 and D9."
        ),
        CasePrecedent(
            event_id="marriage",
            case_name="Sudden Explosive Marriage",
            natal_inspection=[
                "Mars and Rahu conjunct in the 7th house",
                "7th lord debilitated in D1 and enemy sign in D9",
                "Darakaraka (DK) conjunct Ketu"
            ],
            astrological_rationale="Mars (aggression) and Rahu (unorthodoxy/suddenness) in the 7th cause volatile, impulsive dynamics. The weak 7th lord offers no structural support to sustain the marriage through hardship.",
            timing_factors=[
                "Mahadasha of Rahu, Antardasha of Mars"
            ],
            outcome="Sudden, passionate marriage that quickly devolved into intense friction and early separation.",
            teaching_point="Rahu/Mars in 7th creates sudden events. Without a strong 7th lord in D9, the structural integrity of the relationship is weak."
        )
    ]
    
    @staticmethod
    def get_cases_for_event(event_id: str) -> List[Dict[str, Any]]:
        """Returns relevant cases for the specified event protocol to be injected into the prompt."""
        return [c.to_dict() for c in CaseLibrary.CASES if c.event_id == event_id]
