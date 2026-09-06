from typing import Dict, List, Any, Optional
import re
from dataclasses import dataclass, field
import json
from jyotisha_ontology import JyotishaOntology, OntologyRoutingResult

@dataclass
class MethodologyProfile:
    name: str
    preferred_techniques: List[str]
    timing_methods: List[str]
    relevant_vargas: List[str]
    karakas: List[str]
    special_methods: List[str]
    known_variants: List[str] = field(default_factory=list)
    source_material: List[str] = field(default_factory=list)

class MethodologyRouter:
    """
    Analyzes the user's question and routes it to the appropriate Jyotisha methodologies,
    determining which Vargas, Dashas, and strength systems need to be calculated.
    """
    
    PROFILES = {
        "PARASHARI": MethodologyProfile(
            name="PARASHARI",
            preferred_techniques=["Shadbala", "Bhava Bala", "Yogas", "Lordships", "Drishti"],
            timing_methods=["Vimshottari Dasha", "Transits", "Ashtakavarga"],
            relevant_vargas=["D1", "D9", "D10", "D7", "D24"],
            karakas=["Natural Karakas"],
            special_methods=["Neechabhanga", "Combustion", "Retrogression", "Avasthas"],
            source_material=["Brihat Parashara Hora Shastra"]
        ),
        "JAIMINI": MethodologyProfile(
            name="JAIMINI",
            preferred_techniques=["Chara Karakas", "Arudhas", "Jaimini Aspects", "Yogadas"],
            timing_methods=["Chara Dasha", "Narayana Dasha"],
            relevant_vargas=["D1", "D9"],
            karakas=["Atmakaraka", "Amatyakaraka", "Darakaraka"],
            special_methods=["Argala", "Pada Lagna"],
            source_material=["Jaimini Sutras"]
        ),
        "K.N. RAO": MethodologyProfile(
            name="K.N. RAO",
            preferred_techniques=["Composite Approach", "Double Transit", "PAC (Posited, Aspected, Conjunct)"],
            timing_methods=["Vimshottari Dasha", "Chara Dasha", "Double Transit of Saturn & Jupiter"],
            relevant_vargas=["D1", "D9", "D10", "D7", "D24"],
            karakas=["Natural Karakas", "Chara Karakas"],
            special_methods=["PAC Analysis", "Dasha Chidra", "Varga Synthesis"],
            source_material=["Timing Events Through Vimshottari Dasha", "Predicting Through Jaimini's Chara Dasha"]
        ),
        "P.V.R. NARASIMHA RAO": MethodologyProfile(
            name="P.V.R. NARASIMHA RAO",
            preferred_techniques=["Integrated Parashari/Jaimini", "Arudhas in Vargas", "Tajaka"],
            timing_methods=["Vimshottari", "Narayana Dasha", "Conditional Dashas", "Tajaka Annual Chart"],
            relevant_vargas=["D1", "D9", "D10", "D7", "D24", "D60", "D20"],
            karakas=["Natural Karakas", "Chara Karakas (8 Karaka variant)"],
            special_methods=["Arudha Padas in Divisional Charts", "Sahams"],
            source_material=["Vedic Astrology: An Integrated Approach"]
        ),
        "B.V. RAMAN": MethodologyProfile(
            name="B.V. RAMAN",
            preferred_techniques=["Shadbala", "Bhava Bala", "Ashtakavarga", "Classical Yogas"],
            timing_methods=["Vimshottari Dasha", "Ashtakavarga Transits"],
            relevant_vargas=["D1", "D9"],
            karakas=["Natural Karakas"],
            special_methods=["Mathematical Strength Weighting", "Prashna"],
            source_material=["How to Judge a Horoscope", "Three Hundred Important Combinations"]
        ),
        "SANJAY RATH": MethodologyProfile(
            name="SANJAY RATH",
            preferred_techniques=["Narayana Dasha", "Varga synthesis", "Upadesa Sutras"],
            timing_methods=["Narayana Dasha", "Vimshottari from different seeds"],
            relevant_vargas=["ALL"],
            karakas=["Chara Karakas (8)"],
            special_methods=["Varga Chakras", "Brihat Nakshatra"],
            source_material=["Crux of Vedic Astrology", "Jaimini Maharishi's Upadesa Sutra"]
        )
    }
    
    DOMAINS = {
        "BUSINESS": ["business", "startup", "entrepreneur", "venture", "shop", "company", "firm"],
        "CAREER": ["career", "careers", "job", "jobs", "work", "working", "promotion", "boss", "profession", "professional", "employed", "employment", "office", "occupation", "vocation"],
        "MARRIAGE": ["marriage", "marry", "married", "marrying", "wife", "husband", "spouse", "wedding", "divorce", "relationship", "partner", "love", "romance", "mate"],
        "WEALTH": ["money", "wealth", "finance", "finances", "financial", "financially", "rich", "richer", "income", "debt", "investment", "investing", "invest", "gains", "assets", "savings", "salary", "earn", "earnings"],
        "CHILDREN": ["child", "children", "kids", "kid", "pregnancy", "pregnant", "son", "daughter", "progeny", "childbirth"],
        "HEALTH": ["health", "disease", "diseases", "sick", "illness", "surgery", "recovery", "longevity", "death", "maraka", "ayurdaya", "medical"],
        "EDUCATION": ["education", "educational", "study", "studies", "studying", "exam", "exams", "examination", "degree", "university", "college", "school", "academic", "academics", "student"],
        "PROPERTY": ["property", "house", "home", "real estate", "land", "vehicle", "car", "buy house", "purchase"],
        "RELOCATION": ["abroad", "relocation", "relocate", "moving", "move", "foreign", "overseas", "visa", "immigration", "migration"],
        "SPIRITUALITY": ["spirituality", "spiritual", "moksha", "dharma", "religion", "guru", "peace", "purpose", "meditation"]
    }

    @staticmethod
    def _is_timing_question(question: str) -> bool:
        """Year-ahead / 'when' questions are timing questions regardless of domain."""
        q = question.lower().strip()
        return (q.startswith("when") or any(w in q for w in [
            "when will", "when am i", "when is", "what time", "good time", "best time",
            "next year", "coming year", "year ahead", "year hold", "this year",
            "timing", "how long"]))

    @staticmethod
    def identify_domain(question: str) -> str:
        q_lower = question.lower()
        # First match wins: domains are ordered so the more SPECIFIC domain
        # (BUSINESS, RELOCATION) is checked before the broad one (CAREER).
        for domain, keywords in MethodologyRouter.DOMAINS.items():
            for kw in keywords:
                if re.search(r'\b' + kw + r'\b', q_lower):
                    return domain
        # No topical keyword: a timing question is a general_timing question,
        # everything else is GENERAL.
        if MethodologyRouter._is_timing_question(question):
            return "general_timing"
        return "GENERAL"

    @staticmethod
    def decompose_question(question: str, domain: str) -> List[Dict[str, Any]]:
        """
        Decomposes a generic question into specific predictive sub-questions:
        A: Is the event structurally supported? (Natal Promise)
        B: Is the timing favorable? (Activation)
        C: What risks or constraints exist? (Contradiction)
        D: What approach is better supported? (Guidance)
        """
        return [
            {
                "id": "A",
                "focus": "STRUCTURAL_SUPPORT",
                "question": f"Is {domain.lower()} structurally supported in the natal chart?"
            },
            {
                "id": "B",
                "focus": "TIMING",
                "question": f"Is the requested time horizon favorable for {domain.lower()}?"
            },
            {
                "id": "C",
                "focus": "CONSTRAINTS",
                "question": f"What risks, constraints, or contradictory evidence exist for {domain.lower()}?"
            },
            {
                "id": "D",
                "focus": "GUIDANCE",
                "question": f"What approach or type of {domain.lower()} is best supported?"
            }
        ]

    @staticmethod
    def route_question(question: str) -> Dict[str, Any]:
        domain = MethodologyRouter.identify_domain(question)
        
        # Base requirements for all questions
        route = {
            "question": question,
            "domain": domain,
            "primary_methodology": "PARASHARI",
            "secondary_methodologies": [],
            "required_vargas": ["D1", "D9"],
            "required_dashas": ["VIMSHOTTARI_ANTARDASHA"],
            "cross_checks": ["ASHTAKAVARGA", "TRANSITS"],
            "focus_houses": [],
            "focus_karakas": []
        }
        
        if domain == "BUSINESS":
            route["primary_methodology"] = "K.N. RAO"
            route["required_vargas"].append("D10")
            route["focus_houses"] = [10, 7, 2, 11, 3]
            route["focus_karakas"] = ["Mercury", "Saturn", "Mars", "Sun"]
            route["secondary_methodologies"].extend(["JAIMINI", "P.V.R. NARASIMHA RAO"])

        elif domain == "CAREER":
            route["primary_methodology"] = "K.N. RAO"
            route["required_vargas"].append("D10")
            route["focus_houses"] = [10, 2, 6, 11]
            route["focus_karakas"] = ["Amatyakaraka", "Sun", "Mercury", "Saturn"]
            route["secondary_methodologies"].extend(["JAIMINI", "P.V.R. NARASIMHA RAO"])
            
        elif domain == "MARRIAGE":
            route["primary_methodology"] = "K.N. RAO"
            route["secondary_methodologies"].extend(["JAIMINI", "SANJAY RATH"])
            route["required_vargas"].append("D9")
            route["focus_houses"] = [7, 2, 4, 8, 12]
            route["focus_karakas"] = ["Darakaraka", "Venus", "Jupiter"]
            
        elif domain == "WEALTH":
            route["primary_methodology"] = "PARASHARI"
            route["secondary_methodologies"].append("B.V. RAMAN")
            route["focus_houses"] = [2, 11, 5, 9]
            route["focus_karakas"] = ["Jupiter", "Venus"]
            
        elif domain == "CHILDREN":
            route["primary_methodology"] = "SANJAY RATH"
            route["required_vargas"].append("D7")
            route["focus_houses"] = [5, 9]
            route["focus_karakas"] = ["Putrakaraka", "Jupiter"]
            
        elif domain == "HEALTH":
            route["primary_methodology"] = "PARASHARI"
            route["secondary_methodologies"].append("SANJAY RATH")
            route["required_vargas"].extend(["D3", "D30", "D6"])
            route["focus_houses"] = [6, 8, 12, 1]
            route["focus_karakas"] = ["Sun", "Saturn"]
            
        elif domain == "EDUCATION":
            route["primary_methodology"] = "K.N. RAO"
            route["required_vargas"].append("D24")
            route["focus_houses"] = [4, 5, 9]
            route["focus_karakas"] = ["Jupiter", "Mercury"]
            
        elif domain == "PROPERTY":
            route["primary_methodology"] = "PARASHARI"
            route["required_vargas"].append("D4")
            route["focus_houses"] = [4, 11]
            route["focus_karakas"] = ["Mars", "Venus"]

        elif domain == "RELOCATION":
            route["primary_methodology"] = "K.N. RAO"
            route["secondary_methodologies"].append("JAIMINI")
            route["required_vargas"].append("D4")
            route["focus_houses"] = [12, 9, 3, 7]
            route["focus_karakas"] = ["Moon", "Rahu", "Sun"]
            
        elif domain == "SPIRITUALITY":
            route["primary_methodology"] = "JAIMINI"
            route["secondary_methodologies"].append("P.V.R. NARASIMHA RAO")
            route["required_vargas"].extend(["D20", "D60"])
            route["focus_houses"] = [9, 12, 5]
            route["focus_karakas"] = ["Atmakaraka", "Ketu", "Jupiter"]

        # Deep 70-Node Jyotiṣa Decision & Interpretation Ontology integration
        try:
            onto_res = JyotishaOntology.classify_question(question)
            route["ontology"] = onto_res.to_dict()
            route["query_mode"] = onto_res.query_mode
            route["query_mode_id"] = onto_res.query_mode_id
            route["cross_domain_links"] = onto_res.cross_domain_links
            route["falsification_checks"] = onto_res.falsification_checks
            
            # If domain was unmapped or generic, enrich with ontology factors
            if domain == "GENERAL" or not route["focus_houses"]:
                route["focus_houses"] = onto_res.primary_houses
                route["focus_karakas"] = onto_res.primary_karakas
                for v in onto_res.primary_vargas:
                    if v not in route["required_vargas"]:
                        route["required_vargas"].append(v)
                if onto_res.system_priority:
                    route["primary_methodology"] = onto_res.system_priority[0]
                    route["secondary_methodologies"] = onto_res.system_priority[1:]
        except Exception:
            pass

        return route
