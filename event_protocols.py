from typing import List, Dict, Optional
from dataclasses import dataclass, field

@dataclass
class EventProtocol:
    event_id: str
    event_name: str
    primary_houses: List[int]
    secondary_houses: List[int]
    primary_karakas: List[str]
    primary_vargas: List[str]
    secondary_vargas: List[str] = field(default_factory=list)
    optional_vargas: List[str] = field(default_factory=list)
    # Specific rules or criteria that must be checked for this event
    required_conditions: List[str] = field(default_factory=list)
    # The minimum Dasha lords that can activate this event
    activating_lords: List[str] = field(default_factory=list) # e.g. ["10th lord", "AmK"]

class ProtocolRegistry:
    PROTOCOLS = {
        # CAREER EVENTS
        "career_promotion": EventProtocol(
            event_id="career_promotion",
            event_name="Promotion / Status Elevation",
            primary_houses=[10, 11], # Status and Gain
            secondary_houses=[2, 9], # Wealth and Fortune
            primary_karakas=["Sun", "Jupiter"], # Authority and Expansion
            primary_vargas=["D10"],
            secondary_vargas=["D9"],
            optional_vargas=["D60"],
            activating_lords=["10th lord", "11th lord", "9th lord"]
        ),
        "job_change": EventProtocol(
            event_id="job_change",
            event_name="Job Change / Career Transition",
            primary_houses=[10, 5, 9], # 5 and 9 are 8th and 12th from 10th (change/loss of old job)
            secondary_houses=[3], # Effort, short travels
            primary_karakas=["Mercury", "Saturn", "Rahu"], # Change, Routine, Sudden disruption
            primary_vargas=["D10"],
            secondary_vargas=["D9"],
            activating_lords=["10th lord", "5th lord", "9th lord"]
        ),
        "unemployment": EventProtocol(
            event_id="unemployment",
            event_name="Loss of Job / Unemployment",
            primary_houses=[10, 8, 12], # 10th and Dusthanas
            secondary_houses=[5, 9], # 8th and 12th from 10th
            primary_karakas=["Saturn", "Rahu", "Ketu"], # Obstacles, sudden loss, detachment
            primary_vargas=["D10", "D30"],
            secondary_vargas=["D9"],
            activating_lords=["8th lord", "12th lord"]
        ),
        
        # MARRIAGE EVENTS
        "marriage": EventProtocol(
            event_id="marriage",
            event_name="Marriage / Wedding",
            primary_houses=[7, 2, 11], # Spouse, Family, Gain
            secondary_houses=[9], # Dharma, fortune
            primary_karakas=["Venus", "Jupiter"], # Wife/Husband
            primary_vargas=["D9"],
            activating_lords=["7th lord", "Venus", "Jupiter", "Darakaraka"]
        ),
        "marriage_delay": EventProtocol(
            event_id="marriage_delay",
            event_name="Delay or Obstacles in Marriage",
            primary_houses=[7, 8, 12], # 7th and Dusthanas
            secondary_houses=[6], # Dispute
            primary_karakas=["Saturn", "Ketu", "Venus"], # Delay, detachment, relationships
            primary_vargas=["D9"],
            secondary_vargas=["D30"],
            activating_lords=["Saturn", "6th lord", "8th lord"]
        ),
        
        # WEALTH EVENTS
        "wealth_gain": EventProtocol(
            event_id="wealth_gain",
            event_name="Significant Financial Gain",
            primary_houses=[2, 11, 9], # Wealth, Gain, Fortune
            secondary_houses=[5], # Speculation
            primary_karakas=["Jupiter", "Venus", "Mercury"], # Expansion, luxury, commerce
            primary_vargas=["D2", "D16"],
            secondary_vargas=["D9"],
            activating_lords=["2nd lord", "11th lord", "9th lord"]
        ),
        "financial_loss": EventProtocol(
            event_id="financial_loss",
            event_name="Financial Loss / Debt",
            primary_houses=[2, 6, 12], # Wealth, Debt, Loss
            secondary_houses=[8], # Sudden disruptions
            primary_karakas=["Mars", "Saturn", "Rahu"], # Debt, scarcity, sudden shock
            primary_vargas=["D2"],
            secondary_vargas=["D30"],
            activating_lords=["6th lord", "12th lord", "8th lord"]
        ),
        
        # EDUCATION EVENTS
        "education_success": EventProtocol(
            event_id="education_success",
            event_name="Educational Success / Admissions",
            primary_houses=[4, 5, 9], # Basic, Intellect, Higher Education
            secondary_houses=[2, 11], # Speech/learning, fulfillment
            primary_karakas=["Jupiter", "Mercury"], # Wisdom, intellect
            primary_vargas=["D24"],
            secondary_vargas=["D9"],
            activating_lords=["4th lord", "5th lord", "9th lord", "Jupiter", "Mercury"]
        ),

        # GENERAL / TIMING EVENTS (previously every unknown question defaulted
        # to career_promotion — a bug: relationship/health/timing questions got
        # career protocols with wrong houses and karakas)
        "general_timing": EventProtocol(
            event_id="general_timing",
            event_name="General Life Outlook / Year Ahead",
            primary_houses=[1, 9, 10, 11], # Self, fortune, karma, gains
            secondary_houses=[5, 7],
            primary_karakas=["Sun", "Moon", "Jupiter", "Saturn"],
            primary_vargas=["D1", "D9"],
            secondary_vargas=["D10"],
            activating_lords=["Lagna lord", "9th lord", "10th lord", "11th lord"]
        ),
        "business_start": EventProtocol(
            event_id="business_start",
            event_name="Starting a Business / Entrepreneurship",
            primary_houses=[10, 7, 2, 3], # Karma, business partnerships, assets, initiative
            secondary_houses=[11, 9],
            primary_karakas=["Mercury", "Saturn", "Mars", "Sun"],
            primary_vargas=["D10"],
            secondary_vargas=["D9"],
            activating_lords=["10th lord", "7th lord", "3rd lord", "Mercury", "Saturn"]
        ),
        "business_timing": EventProtocol(
            event_id="business_timing",
            event_name="Auspicious Timing for Business Decisions",
            primary_houses=[10, 7, 2, 3, 11],
            secondary_houses=[9],
            primary_karakas=["Mercury", "Saturn", "Jupiter"],
            primary_vargas=["D10"],
            secondary_vargas=["D9"],
            activating_lords=["10th lord", "Mercury", "Saturn", "Jupiter"]
        ),
        "marriage_timing": EventProtocol(
            event_id="marriage_timing",
            event_name="Timing of Marriage",
            primary_houses=[7, 2, 11],
            secondary_houses=[9],
            primary_karakas=["Venus", "Jupiter", "Darakaraka"],
            primary_vargas=["D9"],
            secondary_vargas=["D7"],
            activating_lords=["7th lord", "Venus", "Jupiter", "Darakaraka", "2nd lord"]
        ),
        "wealth_general": EventProtocol(
            event_id="wealth_general",
            event_name="General Financial Outlook",
            primary_houses=[2, 11, 9, 5],
            secondary_houses=[8],
            primary_karakas=["Jupiter", "Venus", "Mercury"],
            primary_vargas=["D2", "D11"],
            secondary_vargas=["D9"],
            activating_lords=["2nd lord", "11th lord", "9th lord", "Jupiter"]
        ),
        "education_general": EventProtocol(
            event_id="education_general",
            event_name="General Education Outlook",
            primary_houses=[4, 5, 9],
            secondary_houses=[2, 11],
            primary_karakas=["Jupiter", "Mercury"],
            primary_vargas=["D24"],
            secondary_vargas=["D9"],
            activating_lords=["4th lord", "5th lord", "9th lord", "Jupiter", "Mercury"]
        ),
        "relocation_abroad": EventProtocol(
            event_id="relocation_abroad",
            event_name="Moving Abroad / Foreign Relocation",
            primary_houses=[12, 9, 3, 7],
            secondary_houses=[4, 8],
            primary_karakas=["Moon", "Rahu", "Sun", "Saturn"],
            primary_vargas=["D4"],
            secondary_vargas=["D9"],
            activating_lords=["12th lord", "9th lord", "3rd lord", "Rahu"]
        )
    }

    @staticmethod
    def get_protocol(event_id: str) -> Optional[EventProtocol]:
        if event_id in ProtocolRegistry.PROTOCOLS:
            return ProtocolRegistry.PROTOCOLS[event_id]
        
        # Dynamic protocol generation from 70-Node Jyotiṣa Question Ontology
        try:
            from jyotisha_ontology import JyotishaOntology
            res = JyotishaOntology.classify_question(event_id)
            node = JyotishaOntology.get_node(res.node_id)
            if node and (node.primary_houses or node.primary_karakas):
                return EventProtocol(
                    event_id=event_id,
                    event_name=node.title,
                    primary_houses=node.primary_houses if node.primary_houses else [1, 10],
                    secondary_houses=node.secondary_houses if node.secondary_houses else [9, 11],
                    primary_karakas=node.primary_karakas if node.primary_karakas else ["Jupiter", "Sun"],
                    primary_vargas=node.primary_vargas if node.primary_vargas else ["D1", "D9"],
                    secondary_vargas=node.secondary_vargas,
                    activating_lords=[f"{h}th lord" for h in node.primary_houses] + node.primary_karakas
                )
        except Exception:
            pass
        return None
        
    @staticmethod
    def match_event_to_protocol(user_question: str) -> str:
        """
        Heuristic router for LLM bypass.
        Order matters: (1) specific loss/unemployment events, (2) domain detection,
        (3) whether the question asks WHEN (timing) or asks about the topic in
        general. Unknown questions fall back to general_timing — NOT career_promotion
        (defaulting everything to career protocols with wrong houses/karakas was a bug).
        """
        q = user_question.lower()

        def has(*words):
            return any(w in q for w in words)

        # Specific high-signal events first
        if has("fired", "unemployed", "lose my job", "lost my job"):
            return "unemployment"
        if has("change job", "new job", "transition", "quit"):
            return "job_change"
        if has("promotion", "raise", "hike"):
            return "career_promotion"
        if has("delay") and has("marri"):
            return "marriage_delay"
        if has("loss", "debt", "bankrupt"):
            return "financial_loss"

        # Domain detection (specific -> general)
        is_business = has("business", "startup", "entrepreneur", "venture", "firm")
        is_marriage = has("marriage", "marry", "married", "wedding", "spouse",
                          "husband", "wife")
        is_wealth = has("wealth", "money", "rich", "finance", "financial", "income",
                        "salary", "earn", "gains", "assets", "savings")
        # General-outlook phrasing ("how is my X") vs specific gain/exam events
        is_general_outlook = has("how is my", "how are my", "what about my",
                                 "tell me about my", "overall") or q.strip().startswith("is my")
        is_education = has("education", "study", "studies", "studying", "exam",
                           "exams", "college", "admission", "university", "academic",
                           "student")
        is_career = has("career", "job", "work", "profession", "promotion", "boss",
                        "office", "employment")
        is_relocation = has("abroad", "relocate", "relocation", "foreign", "overseas",
                            "visa", "immigration", "moving to", "move to")
        is_marriage_likely = has("likely to get married", "when will i get married",
                                 "when am i getting married")

        # Timing questions ("when...", "what does next year hold", "good time")
        is_timing = (q.strip().startswith("when") or has("when will", "when am i",
                        "when is", "what time", "good time", "best time",
                        "next year", "coming year", "year ahead", "year hold",
                        "this year", "timing", "how long"))

        # Match: specific timing event ids where the test/protocol set demands them
        if is_marriage_likely or (is_timing and is_marriage and not has("delay")):
            return "marriage_timing"
        if is_business and is_timing:
            return "business_timing"
        if is_business:
            return "business_start"
        if is_relocation:
            return "relocation_abroad"
        if is_marriage:
            return "marriage"
        if is_wealth and (is_timing or is_general_outlook):
            return "wealth_general"
        if is_wealth:
            return "wealth_gain"
        if is_education and (is_timing or is_general_outlook):
            return "education_general"
        if is_education:
            return "education_success"
        if is_career and is_timing:
            return "career_promotion"
        if is_career:
            return "job_change" if has("change", "new job", "switch") else "career_promotion"

        # Generic outlook / year-ahead / unknown
        if is_timing:
            return "general_timing"
        return "general_timing"
