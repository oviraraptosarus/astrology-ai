"""
Master Jyotiṣa Question & Interpretation Ontology (70 Core Nodes)
==================================================================
Hierarchical ontology mapping user questions across 70 master nodes,
their complete sub-node trees, astrological significator factors,
cross-domain links, system priority routing, and falsification gates.

Universal Layer Pipeline:
  QUESTION
     ↓
  DOMAIN DETECTION & ONTOLOGY CLASSIFICATION (Nodes 1-70, Query Mode 70.1-70.24)
     ↓
  REQUIRED ASTROLOGICAL FACTORS (Houses, Lords, Karakas, Vargas, Jaimini, KP, Transits)
     ↓
  SYSTEM SPECIALIZATION ROUTER (Parāśari, Jaimini, KP, Vargas, Transits, Daśā)
     ↓
  BAYESIAN SYNTHESIS & QUALITY CONTROL (Gate Verification, Contradiction Check, Confidence)
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
import re

@dataclass
class OntologyNode:
    node_id: int
    title: str
    category: str
    subnodes: Dict[str, str]
    primary_houses: List[int] = field(default_factory=list)
    secondary_houses: List[int] = field(default_factory=list)
    primary_karakas: List[str] = field(default_factory=list)
    primary_vargas: List[str] = field(default_factory=list)
    secondary_vargas: List[str] = field(default_factory=list)
    jaimini_factors: List[str] = field(default_factory=list)
    kp_significators: List[int] = field(default_factory=list)
    timing_methods: List[str] = field(default_factory=list)
    system_priority: List[str] = field(default_factory=list)
    special_engines: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "title": self.title,
            "category": self.category,
            "subnodes": self.subnodes,
            "primary_houses": self.primary_houses,
            "secondary_houses": self.secondary_houses,
            "primary_karakas": self.primary_karakas,
            "primary_vargas": self.primary_vargas,
            "secondary_vargas": self.secondary_vargas,
            "jaimini_factors": self.jaimini_factors,
            "kp_significators": self.kp_significators,
            "timing_methods": self.timing_methods,
            "system_priority": self.system_priority,
            "special_engines": self.special_engines,
            "keywords": self.keywords,
        }

@dataclass
class OntologyRoutingResult:
    node_id: int
    node_title: str
    subnode_id: str
    subnode_title: str
    category: str
    query_mode_id: str
    query_mode: str
    primary_houses: List[int]
    secondary_houses: List[int]
    primary_karakas: List[str]
    primary_vargas: List[str]
    secondary_vargas: List[str]
    jaimini_factors: List[str]
    kp_significators: List[int]
    timing_methods: List[str]
    system_priority: List[str]
    special_engines: List[str]
    cross_domain_links: List[str] = field(default_factory=list)
    falsification_checks: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "node_id": self.node_id,
            "node_title": self.node_title,
            "subnode_id": self.subnode_id,
            "subnode_title": self.subnode_title,
            "category": self.category,
            "query_mode_id": self.query_mode_id,
            "query_mode": self.query_mode,
            "primary_houses": self.primary_houses,
            "secondary_houses": self.secondary_houses,
            "primary_karakas": self.primary_karakas,
            "primary_vargas": self.primary_vargas,
            "secondary_vargas": self.secondary_vargas,
            "jaimini_factors": self.jaimini_factors,
            "kp_significators": self.kp_significators,
            "timing_methods": self.timing_methods,
            "system_priority": self.system_priority,
            "special_engines": self.special_engines,
            "cross_domain_links": self.cross_domain_links,
            "falsification_checks": self.falsification_checks,
        }

# Query Modes (Node 70)
QUERY_MODES: Dict[str, str] = {
    "70.1": "What",
    "70.2": "Why",
    "70.3": "How",
    "70.4": "When",
    "70.5": "Where",
    "70.6": "Who",
    "70.7": "With whom",
    "70.8": "Whether",
    "70.9": "How much",
    "70.10": "How strong",
    "70.11": "How long",
    "70.12": "What causes it",
    "70.13": "What improves it",
    "70.14": "What harms it",
    "70.15": "What should I avoid",
    "70.16": "What should I pursue",
    "70.17": "What are the likely outcomes",
    "70.18": "What are alternative outcomes",
    "70.19": "What is the strongest period",
    "70.20": "What is the weakest period",
    "70.21": "What confirms this",
    "70.22": "What contradicts this",
    "70.23": "How confident are you",
    "70.24": "What data is missing",
}

# Cross-Domain Couplings (Node 68)
CROSS_DOMAIN_COUPLINGS: Dict[str, Dict[str, Any]] = {
    "68.1": {"name": "Career → Marriage", "houses": [10, 7, 2, 11], "vargas": ["D10", "D9"], "karakas": ["Sun", "Venus", "AmK", "DK"]},
    "68.2": {"name": "Marriage → Career", "houses": [7, 10, 2, 11], "vargas": ["D9", "D10"], "karakas": ["Venus", "Sun", "DK", "AmK"]},
    "68.3": {"name": "Marriage → Wealth", "houses": [7, 2, 8, 11], "vargas": ["D9", "D2"], "karakas": ["Venus", "Jupiter", "DK", "A2"]},
    "68.4": {"name": "Spouse → Wealth", "houses": [7, 8, 2, 11], "vargas": ["D9", "D2"], "karakas": ["Venus", "Jupiter", "UL", "A11"]},
    "68.5": {"name": "Spouse → Status", "houses": [7, 10, 1, 11], "vargas": ["D9", "D10"], "karakas": ["Venus", "Sun", "UL", "A10"]},
    "68.6": {"name": "Business → Marriage", "houses": [7, 10, 11], "vargas": ["D10", "D9"], "karakas": ["Mercury", "Venus"]},
    "68.7": {"name": "Network → Business", "houses": [11, 7, 10, 3], "vargas": ["D10", "D11"], "karakas": ["Mercury", "Rahu", "A11", "A10"]},
    "68.8": {"name": "Network → Wealth", "houses": [11, 2, 9, 5], "vargas": ["D2", "D11"], "karakas": ["Jupiter", "Mercury", "A11", "Indu_Lagna"]},
    "68.9": {"name": "Foreign Relocation → Career", "houses": [12, 9, 10, 7], "vargas": ["D10", "D4"], "karakas": ["Rahu", "Saturn", "AmK"]},
    "68.10": {"name": "Foreign Relocation → Marriage", "houses": [12, 9, 7, 4], "vargas": ["D9", "D4"], "karakas": ["Rahu", "Venus", "DK", "UL"]},
    "68.11": {"name": "Education → Career", "houses": [5, 9, 10, 2], "vargas": ["D24", "D10"], "karakas": ["Jupiter", "Mercury", "Sun", "AmK"]},
    "68.12": {"name": "Education → Wealth", "houses": [5, 9, 2, 11], "vargas": ["D24", "D2"], "karakas": ["Jupiter", "Mercury", "A2", "A11"]},
    "68.13": {"name": "Children → Career", "houses": [5, 10, 11], "vargas": ["D7", "D10"], "karakas": ["Jupiter", "Sun", "PK", "AmK"]},
    "68.14": {"name": "Children → Wealth", "houses": [5, 2, 11, 9], "vargas": ["D7", "D2"], "karakas": ["Jupiter", "PK", "A5", "A11"]},
    "68.15": {"name": "Family → Wealth", "houses": [2, 4, 11, 9], "vargas": ["D2", "D12"], "karakas": ["Jupiter", "Moon", "A2"]},
    "68.16": {"name": "Family → Career", "houses": [2, 4, 10, 9], "vargas": ["D10", "D12"], "karakas": ["Sun", "Moon", "AmK"]},
    "68.17": {"name": "Property → Wealth", "houses": [4, 2, 11, 9], "vargas": ["D4", "D2"], "karakas": ["Mars", "Saturn", "Jupiter", "A4"]},
    "68.18": {"name": "Property → Family", "houses": [4, 2, 12], "vargas": ["D4", "D12"], "karakas": ["Mars", "Moon"]},
    "68.19": {"name": "Spirituality → Life Direction", "houses": [9, 12, 1, 5], "vargas": ["D20", "D9"], "karakas": ["Jupiter", "Ketu", "AK", "Karakamsha"]},
    "68.20": {"name": "Career → Purpose", "houses": [10, 9, 1, 5], "vargas": ["D10", "D9", "D60"], "karakas": ["Sun", "Jupiter", "AK", "AmK"]},
    "68.21": {"name": "Wealth → Social Status", "houses": [2, 11, 10, 1], "vargas": ["D2", "D10"], "karakas": ["Jupiter", "Sun", "AL", "GL"]},
    "68.22": {"name": "Status → Network", "houses": [10, 11, 1], "vargas": ["D10", "D11"], "karakas": ["Sun", "Mercury", "A10", "A11"]},
    "68.23": {"name": "Network → Spouse", "houses": [11, 7, 3], "vargas": ["D9", "D11"], "karakas": ["Venus", "Mercury", "DK", "UL"]},
    "68.24": {"name": "Spouse → Foreign Relocation", "houses": [7, 12, 9, 4], "vargas": ["D9", "D4"], "karakas": ["Venus", "Rahu", "DK"]},
    "68.25": {"name": "Business Partner → Wealth", "houses": [7, 2, 11, 10], "vargas": ["D10", "D2"], "karakas": ["Mercury", "Jupiter", "A7", "A11"]},
    "68.26": {"name": "Investor → Business", "houses": [8, 11, 7, 10], "vargas": ["D10", "D2"], "karakas": ["Mercury", "Rahu", "Saturn"]},
    "68.27": {"name": "Mentor → Career", "houses": [9, 10, 1, 11], "vargas": ["D10", "D9"], "karakas": ["Jupiter", "Sun", "BK", "AmK"]},
    "68.28": {"name": "Institution → Career", "houses": [10, 9, 11, 6], "vargas": ["D10"], "karakas": ["Sun", "Saturn", "AmK"]},
    "68.29": {"name": "Reputation → Business", "houses": [10, 7, 11, 1], "vargas": ["D10"], "karakas": ["Sun", "Mercury", "AL", "A10"]},
    "68.30": {"name": "Crisis → Transformation", "houses": [8, 1, 9, 12], "vargas": ["D8", "D30", "D9"], "karakas": ["Saturn", "Mars", "Ketu", "AK"]},
}

# The Master 70-Node Catalog
MASTER_ONTOLOGY_NODES: Dict[int, OntologyNode] = {
    0: OntologyNode(
        node_id=0,
        title="Universal Meta-Nodes",
        category="META",
        subnodes={
            "0.1": "Birth-data validation", "0.2": "Birth-time accuracy", "0.3": "Birth-place validation",
            "0.4": "Time-zone validation", "0.5": "DST correction", "0.6": "Ayanāṃśa selection",
            "0.7": "Sidereal framework", "0.8": "House-system methodology", "0.9": "Rāśi calculation",
            "0.10": "Bhava calculation", "0.11": "Nakṣatra calculation", "0.12": "Pada calculation",
            "0.13": "Planetary degrees", "0.14": "Retrograde status", "0.15": "Combustion",
            "0.16": "Planetary war", "0.17": "Planetary dignity", "0.18": "Vargottama",
            "0.19": "Shadbala", "0.20": "Aṣṭakavarga", "0.21": "Divisional-chart integrity",
            "0.22": "Daśā calculation integrity", "0.23": "Transit-data integrity", "0.24": "KP cusp integrity",
            "0.25": "KP sub-lord integrity", "0.26": "Jaimini Karaka calculation integrity",
            "0.27": "Arudha calculation integrity", "0.28": "Rāśi Dṛṣṭi calculation",
            "0.29": "Conflicting-calculation detection", "0.30": "Source/version tracking",
            "0.31": "Calculation confidence", "0.32": "Interpretation confidence",
            "0.33": "Data insufficiency detection", "0.34": "Contradiction detection",
            "0.35": "False-positive detection", "0.36": "Hallucination prevention",
            "0.37": "System-specific methodology lock", "0.38": "Natal promise vs timing distinction",
            "0.39": "Potential vs manifestation distinction", "0.40": "Event vs psychological tendency distinction"
        },
        primary_houses=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        primary_karakas=["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"],
        primary_vargas=["D1", "D9", "D10", "D60"],
        system_priority=["PARASHARI", "JAIMINI", "KP", "NADI", "TAJAKA"],
        special_engines=["boundary_fragility_engine", "uncertainty_engine", "cancellations"],
        keywords=["validation", "accuracy", "integrity", "verification", "confidence", "ayanamsa", "meta"]
    ),
    1: OntologyNode(
        node_id=1,
        title="Self / Identity / Personality",
        category="LIFE_SELF",
        subnodes={
            "1.1": "Core personality", "1.2": "Temperament", "1.3": "Self-image", "1.4": "Ego structure",
            "1.5": "Confidence", "1.6": "Self-esteem", "1.7": "Initiative", "1.8": "Independence",
            "1.9": "Dependence", "1.10": "Assertiveness", "1.11": "Passivity", "1.12": "Willpower",
            "1.13": "Persistence", "1.14": "Discipline", "1.15": "Ambition", "1.16": "Competitiveness",
            "1.17": "Adaptability", "1.18": "Flexibility", "1.19": "Conservatism", "1.20": "Risk tolerance",
            "1.21": "Decision-making", "1.22": "Leadership tendency", "1.23": "Followership tendency",
            "1.24": "Social orientation", "1.25": "Introversion/extroversion symbolism", "1.26": "Public personality",
            "1.27": "Private personality", "1.28": "Hidden personality", "1.29": "Strengths", "1.30": "Weaknesses",
            "1.31": "Natural talents", "1.32": "Behavioral patterns", "1.33": "Recurring life patterns",
            "1.34": "Personal identity development", "1.35": "Self-mastery", "1.36": "Personal branding",
            "1.37": "Charisma", "1.38": "Magnetism", "1.39": "Personal authority", "1.40": "Personal agency"
        },
        primary_houses=[1, 5, 9],
        secondary_houses=[3, 10],
        primary_karakas=["Sun", "Moon", "Mars"],
        primary_vargas=["D1", "D9"],
        secondary_vargas=["D3", "D60"],
        jaimini_factors=["AK", "Karakamsha", "Swamsha", "AL"],
        kp_significators=[1],
        timing_methods=["Vimshottari Dasha", "Chara Dasha"],
        system_priority=["PARASHARI", "JAIMINI", "KP", "NADI"],
        keywords=["personality", "temperament", "identity", "ego", "confidence", "willpower", "strengths", "self", "character"]
    ),
    2: OntologyNode(
        node_id=2,
        title="Life Purpose / Dharma",
        category="LIFE_SELF",
        subnodes={
            "2.1": "Life direction", "2.2": "Dharma", "2.3": "Purpose", "2.4": "Duty", "2.5": "Life mission",
            "2.6": "Natural calling", "2.7": "Meaning", "2.8": "Values", "2.9": "Moral orientation",
            "2.10": "Spiritual purpose", "2.11": "Social contribution", "2.12": "Legacy purpose",
            "2.13": "Karmic themes", "2.14": "Repeating life lessons", "2.15": "Major life lessons",
            "2.16": "Purpose vs career distinction", "2.17": "Purpose vs relationship distinction",
            "2.18": "Dharma conflicts", "2.19": "Fulfillment through work", "2.20": "Fulfillment through relationships",
            "2.21": "Fulfillment through service", "2.22": "Renunciation tendencies", "2.23": "Worldly vs spiritual orientation"
        },
        primary_houses=[1, 5, 9, 10],
        secondary_houses=[12, 4, 8],
        primary_karakas=["Sun", "Jupiter", "Saturn"],
        primary_vargas=["D1", "D9", "D20", "D60"],
        jaimini_factors=["AK", "Karakamsha", "BK", "AL"],
        kp_significators=[1, 9, 10],
        timing_methods=["Vimshottari Dasha", "Narayana Dasha", "Chara Dasha"],
        system_priority=["JAIMINI", "PARASHARI", "NADI", "KP"],
        keywords=["purpose", "dharma", "mission", "calling", "karmic", "lessons", "meaning", "values", "legacy"]
    ),
    3: OntologyNode(
        node_id=3,
        title="Career / Vocation",
        category="CAREER",
        subnodes={
            "3.1": "Career direction", "3.2": "Vocation", "3.3": "Profession", "3.4": "Occupation",
            "3.5": "Means of livelihood", "3.6": "Career strengths", "3.7": "Career weaknesses",
            "3.8": "Best career environment", "3.9": "Corporate career", "3.10": "Government career",
            "3.11": "Private-sector career", "3.12": "Public-sector career", "3.13": "Self-employment",
            "3.14": "Entrepreneurship", "3.15": "Business ownership", "3.16": "Consulting", "3.17": "Freelancing",
            "3.18": "Commission-based work", "3.19": "Sales", "3.20": "Management", "3.21": "Leadership",
            "3.22": "Technical work", "3.23": "Creative work", "3.24": "Academic career", "3.25": "Research career",
            "3.26": "Medical professions", "3.27": "Legal professions", "3.28": "Finance professions",
            "3.29": "Technology professions", "3.30": "Media professions", "3.31": "Entertainment",
            "3.32": "Communications", "3.33": "Writing", "3.34": "Teaching", "3.35": "Spiritual profession",
            "3.36": "Political career", "3.37": "Administrative career", "3.38": "Military/security career",
            "3.39": "Entrepreneurship type", "3.40": "Career specialization", "3.41": "Career diversification",
            "3.42": "Career stability", "3.43": "Career volatility", "3.44": "Career changes", "3.45": "Career breaks",
            "3.46": "Career restart", "3.47": "Promotion", "3.48": "Demotion", "3.49": "Recognition",
            "3.50": "Authority", "3.51": "Responsibility", "3.52": "Professional reputation", "3.53": "Career peak",
            "3.54": "Career decline", "3.55": "Retirement", "3.56": "Second career", "3.57": "Late-life career",
            "3.58": "Career fulfillment", "3.59": "Career mismatch", "3.60": "Career transition"
        },
        primary_houses=[10, 1, 2, 6, 11],
        secondary_houses=[9, 3, 7],
        primary_karakas=["Sun", "Saturn", "Mercury", "Jupiter"],
        primary_vargas=["D10", "D9"],
        secondary_vargas=["D1", "D60"],
        jaimini_factors=["AmK", "A10", "AL", "Karakamsha"],
        kp_significators=[2, 6, 10, 11],
        timing_methods=["Vimshottari Dasha", "KP Sub-Lord", "Double Transit", "Kakshya"],
        system_priority=["PARASHARI", "JAIMINI", "KP", "NADI"],
        special_engines=["forward_timing_scanner", "kp_engine"],
        keywords=["career", "profession", "vocation", "job", "work", "corporate", "promotion", "recognition", "status", "10th house"]
    ),
    4: OntologyNode(
        node_id=4,
        title="Job / Employment",
        category="CAREER",
        subnodes={
            "4.1": "Getting a job", "4.2": "First job", "4.3": "Government job", "4.4": "Private job",
            "4.5": "Corporate job", "4.6": "Startup job", "4.7": "Remote job", "4.8": "International job",
            "4.9": "Job stability", "4.10": "Job satisfaction", "4.11": "Job stress", "4.12": "Workplace environment",
            "4.13": "Coworkers", "4.14": "Boss", "4.15": "Subordinates", "4.16": "Employment relationships",
            "4.17": "Job security", "4.18": "Job loss", "4.19": "Resignation", "4.20": "Job switch",
            "4.21": "Promotion", "4.22": "Transfer", "4.23": "Posting", "4.24": "Workload", "4.25": "Competition",
            "4.26": "Workplace politics", "4.27": "Workplace conflict", "4.28": "Recognition at work",
            "4.29": "Salary growth", "4.30": "Benefits", "4.31": "Organizational hierarchy",
            "4.32": "Authority over others", "4.33": "Working under authority", "4.34": "Employee vs independent worker",
            "4.35": "Employment longevity"
        },
        primary_houses=[6, 10, 11, 2],
        secondary_houses=[5, 9, 3],
        primary_karakas=["Saturn", "Mercury", "Sun"],
        primary_vargas=["D10", "D9"],
        secondary_vargas=["D6"],
        jaimini_factors=["AmK", "A6", "A10"],
        kp_significators=[6, 10, 11, 2],
        timing_methods=["KP Sub-Lord", "Vimshottari Dasha", "Transits"],
        system_priority=["KP", "PARASHARI", "JAIMINI", "TAJAKA"],
        keywords=["job", "employment", "service", "salary", "boss", "coworkers", "transfer", "layoff", "resignation", "switch"]
    ),
    5: OntologyNode(
        node_id=5,
        title="Business / Entrepreneurship",
        category="CAREER",
        subnodes={
            "5.1": "Business potential", "5.2": "Business ownership", "5.3": "Business model",
            "5.4": "Entrepreneurial temperament", "5.5": "Founder potential", "5.6": "Cofounder potential",
            "5.7": "Partnership business", "5.8": "Solo business", "5.9": "Family business", "5.10": "Startup",
            "5.11": "Bootstrapping", "5.12": "Scaling", "5.13": "Business expansion", "5.14": "Business contraction",
            "5.15": "Business diversification", "5.16": "Business exit", "5.17": "Acquisition", "5.18": "Merger",
            "5.19": "Franchise", "5.20": "Licensing", "5.21": "Consulting business", "5.22": "Agency",
            "5.23": "SaaS/software business", "5.24": "Digital business", "5.25": "E-commerce",
            "5.26": "Media business", "5.27": "Education business", "5.28": "Real-estate business",
            "5.29": "Finance business", "5.30": "Manufacturing", "5.31": "Trading", "5.32": "Import/export",
            "5.33": "Professional practice", "5.34": "Client-based business", "5.35": "Subscription business",
            "5.36": "Recurring revenue", "5.37": "Business scalability", "5.38": "Business resilience",
            "5.39": "Founder-market fit", "5.40": "Business timing", "5.41": "Business launch timing",
            "5.42": "Expansion timing", "5.43": "Exit timing", "5.44": "Business failure risk", "5.45": "Business dispute risk"
        },
        primary_houses=[7, 10, 11, 2, 3],
        secondary_houses=[9, 12, 8],
        primary_karakas=["Mercury", "Mars", "Sun", "Rahu"],
        primary_vargas=["D10", "D9"],
        secondary_vargas=["D2", "D11"],
        jaimini_factors=["AmK", "A7", "A10", "A11", "AL"],
        kp_significators=[2, 7, 10, 11],
        timing_methods=["Vimshottari Dasha", "KP Sub-Lord", "Double Transit", "Muhurta"],
        system_priority=["PARASHARI", "KP", "JAIMINI", "TAJAKA"],
        special_engines=["financial_astro_engine", "forward_timing_scanner"],
        keywords=["business", "startup", "entrepreneur", "agency", "saas", "client", "revenue", "partnership", "founder", "trade"]
    ),
    6: OntologyNode(
        node_id=6,
        title="Money / Wealth / Finance",
        category="MONEY",
        subnodes={
            "6.1": "Earning ability", "6.2": "Income", "6.3": "Salary", "6.4": "Business income",
            "6.5": "Passive income", "6.6": "Multiple income streams", "6.7": "Savings", "6.8": "Accumulation",
            "6.9": "Wealth", "6.10": "Net-worth trajectory", "6.11": "Financial stability", "6.12": "Financial volatility",
            "6.13": "Wealth-building mechanism", "6.14": "Wealth ceiling", "6.15": "Wealth scalability",
            "6.16": "Financial independence", "6.17": "High-income potential", "6.18": "Affluence",
            "6.19": "Exceptional wealth potential", "6.20": "Family wealth", "6.21": "Self-made wealth",
            "6.22": "Spouse-derived wealth", "6.23": "Partnership wealth", "6.24": "Network-derived wealth",
            "6.25": "Institutional wealth", "6.26": "Foreign wealth", "6.27": "Inheritance", "6.28": "Windfalls",
            "6.29": "Sudden gains", "6.30": "Sudden losses", "6.31": "Financial setbacks", "6.32": "Debt",
            "6.33": "Loans", "6.34": "Credit", "6.35": "Lending", "6.36": "Borrowing", "6.37": "Debt repayment",
            "6.38": "Financial obligations", "6.39": "Expense patterns", "6.40": "Financial leakage",
            "6.41": "Wealth preservation", "6.42": "Wealth compounding", "6.43": "Asset accumulation",
            "6.44": "Liquidity", "6.45": "Financial risk", "6.46": "Financial greed/overreach symbolism",
            "6.47": "Money psychology", "6.48": "Relationship with money", "6.49": "Wealth after marriage",
            "6.50": "Wealth before marriage", "6.51": "Wealth through career", "6.52": "Wealth through business",
            "6.53": "Wealth through investments", "6.54": "Wealth through property", "6.55": "Wealth through other people's capital"
        },
        primary_houses=[2, 11, 9, 1, 5],
        secondary_houses=[6, 8, 12, 4],
        primary_karakas=["Jupiter", "Venus", "Mercury"],
        primary_vargas=["D2", "D9"],
        secondary_vargas=["D11", "D16"],
        jaimini_factors=["Indu_Lagna", "Hora_Lagna", "A2", "A11", "AmK"],
        kp_significators=[2, 6, 11],
        timing_methods=["Vimshottari Dasha", "KP Sub-Lord", "Double Transit", "Indu Lagna Activation"],
        system_priority=["PARASHARI", "KP", "JAIMINI", "NADI"],
        special_engines=["wealth_lagnas_engine", "financial_astro_engine"],
        keywords=["money", "wealth", "finance", "income", "savings", "debt", "loan", "rich", "net worth", "dhana yoga", "indu lagna"]
    ),
    7: OntologyNode(
        node_id=7,
        title="Investments / Speculation",
        category="MONEY",
        subnodes={
            "7.1": "Investment temperament", "7.2": "Long-term investment", "7.3": "Short-term speculation",
            "7.4": "Trading", "7.5": "Speculation", "7.6": "Equity-market symbolism", "7.7": "Venture investment",
            "7.8": "Private investment", "7.9": "Capital deployment", "7.10": "Risk appetite",
            "7.11": "Investment discipline", "7.12": "Investment losses", "7.13": "Sudden gains",
            "7.14": "Speculative gains", "7.15": "Speculative losses", "7.16": "Compounding capacity",
            "7.17": "Timing investments", "7.18": "Investment diversification", "7.19": "Wealth preservation",
            "7.20": "Other people's money", "7.21": "Joint investments"
        },
        primary_houses=[5, 9, 11, 2],
        secondary_houses=[8, 12, 3],
        primary_karakas=["Mercury", "Jupiter", "Rahu", "Mars"],
        primary_vargas=["D2", "D9", "D5"],
        jaimini_factors=["PK", "A5", "A11", "Hora_Lagna"],
        kp_significators=[2, 5, 11],
        timing_methods=["Vimshottari Dasha", "Transits", "Gann Cycles"],
        system_priority=["PARASHARI", "KP", "TAJAKA", "JAIMINI"],
        special_engines=["financial_astro_engine"],
        keywords=["investment", "speculation", "stocks", "trading", "crypto", "equity", "shares", "5th house", "gann"]
    ),
    8: OntologyNode(
        node_id=8,
        title="Property / Real Estate / Vehicles",
        category="PROPERTY",
        subnodes={
            "8.1": "Buying property", "8.2": "Selling property", "8.3": "Property ownership",
            "8.4": "First property", "8.5": "Multiple properties", "8.6": "Land", "8.7": "Agricultural land",
            "8.8": "Commercial property", "8.9": "Residential property", "8.10": "Rental property",
            "8.11": "Property investment", "8.12": "Construction", "8.13": "Renovation",
            "8.14": "Property inheritance", "8.15": "Family property", "8.16": "Property dispute",
            "8.17": "Property litigation", "8.18": "Mortgage", "8.19": "Real-estate gains",
            "8.20": "Real-estate losses", "8.21": "Property timing", "8.22": "House quality",
            "8.23": "Home ownership", "8.24": "Residence change", "8.25": "Vehicle purchase",
            "8.26": "Vehicle ownership", "8.27": "Vehicle problems", "8.28": "Vehicle upgrades",
            "8.29": "Luxury assets"
        },
        primary_houses=[4, 11, 2, 9],
        secondary_houses=[12, 6, 8, 3],
        primary_karakas=["Mars", "Venus", "Saturn", "Moon"],
        primary_vargas=["D4", "D16"],
        secondary_vargas=["D9", "D1"],
        jaimini_factors=["MK", "A4", "AL"],
        kp_significators=[4, 11, 12],
        timing_methods=["KP Sub-Lord", "Vimshottari Dasha", "Double Transit"],
        system_priority=["PARASHARI", "KP", "JAIMINI", "TAJAKA"],
        keywords=["property", "house", "real estate", "land", "plot", "car", "vehicle", "flat", "apartment", "4th house"]
    ),
    9: OntologyNode(
        node_id=9,
        title="Marriage",
        category="RELATIONSHIPS",
        subnodes={
            "9.1": "Whether marriage is indicated", "9.2": "Marriage promise", "9.3": "Marriage timing",
            "9.4": "Early marriage", "9.5": "Late marriage", "9.6": "Marriage delay", "9.7": "Marriage stability",
            "9.8": "Marriage satisfaction", "9.9": "Marriage quality", "9.10": "Nature of marriage",
            "9.11": "Arranged marriage", "9.12": "Love marriage", "9.13": "Love-cum-arranged",
            "9.14": "Intercultural marriage", "9.15": "Interfaith marriage", "9.16": "Intercaste marriage",
            "9.17": "Long-distance relationship leading to marriage", "9.18": "Foreign marriage",
            "9.19": "Marriage after career establishment", "9.20": "Marriage impact on career",
            "9.21": "Marriage impact on wealth", "9.22": "Separation risk", "9.23": "Divorce symbolism",
            "9.24": "Re-marriage", "9.25": "Second marriage", "9.26": "Marital conflict", "9.27": "Marital intimacy",
            "9.28": "Marital friendship", "9.29": "Emotional compatibility", "9.30": "Sexual compatibility",
            "9.31": "Domestic compatibility", "9.32": "Financial compatibility", "9.33": "Family compatibility",
            "9.34": "In-laws", "9.35": "Marriage responsibilities", "9.36": "Marriage longevity",
            "9.37": "Spouse support", "9.38": "Spouse obstruction", "9.39": "Partner's career", "9.40": "Partner's wealth"
        },
        primary_houses=[7, 2, 11],
        secondary_houses=[9, 5, 8, 12, 6],
        primary_karakas=["Venus", "Jupiter"],
        primary_vargas=["D9"],
        secondary_vargas=["D1", "D30"],
        jaimini_factors=["DK", "UL", "A7", "Upapada"],
        kp_significators=[2, 7, 11],
        timing_methods=["Vimshottari Dasha", "KP Sub-Lord", "Double Transit", "Chara Dasha"],
        system_priority=["JAIMINI", "PARASHARI", "KP", "NADI"],
        special_engines=["kundali_milan_synastry_engine"],
        keywords=["marriage", "wedding", "marry", "spouse", "wife", "husband", "divorce", "separation", "7th house", "upapada"]
    ),
    10: OntologyNode(
        node_id=10,
        title="Spouse Profile",
        category="RELATIONSHIPS",
        subnodes={
            "10.1": "Personality of spouse", "10.2": "Appearance symbolism", "10.3": "Temperament",
            "10.4": "Intelligence", "10.5": "Education", "10.6": "Profession", "10.7": "Wealth",
            "10.8": "Social status", "10.9": "Family background", "10.10": "Cultural background",
            "10.11": "Nationality", "10.12": "Foreign connection", "10.13": "Religion/culture symbolism",
            "10.14": "Emotional nature", "10.15": "Communication style", "10.16": "Romantic style",
            "10.17": "Sexual temperament", "10.18": "Loyalty symbolism", "10.19": "Independence",
            "10.20": "Ambition", "10.21": "Leadership", "10.22": "Age difference symbolism", "10.23": "Maturity",
            "10.24": "Family orientation", "10.25": "Spirituality", "10.26": "Partner's family",
            "10.27": "Partner's social network", "10.28": "Partner's professional environment",
            "10.29": "How the spouse enters life", "10.30": "Where/through what context spouse may be encountered",
            "10.31": "What the native learns through spouse", "10.32": "Spouse's impact on wealth",
            "10.33": "Spouse's impact on status", "10.34": "Spouse's impact on relocation"
        },
        primary_houses=[7, 2, 8, 12],
        secondary_houses=[9, 10, 4],
        primary_karakas=["Venus", "Jupiter"],
        primary_vargas=["D9"],
        jaimini_factors=["DK", "UL", "A7"],
        kp_significators=[7, 2, 11],
        timing_methods=["Vimshottari Dasha", "Chara Dasha"],
        system_priority=["JAIMINI", "PARASHARI", "KP", "NADI"],
        keywords=["spouse persona", "partner profile", "future wife", "future husband", "spouse profession", "spouse looks"]
    ),
    11: OntologyNode(
        node_id=11,
        title="Love / Romance",
        category="RELATIONSHIPS",
        subnodes={
            "11.1": "Romantic temperament", "11.2": "How person gives love", "11.3": "How person receives love",
            "11.4": "Emotional needs", "11.5": "Relationship security", "11.6": "Affection needs",
            "11.7": "Physical affection", "11.8": "Intimacy needs", "11.9": "Communication needs",
            "11.10": "Reassurance needs", "11.11": "Commitment needs", "11.12": "Freedom needs",
            "11.13": "Closeness vs independence", "11.14": "Romance preferences", "11.15": "Courtship",
            "11.16": "Dating", "11.17": "Attraction", "11.18": "Crushes", "11.19": "Infatuation",
            "11.20": "Love attachment", "11.21": "Emotional vulnerability", "11.22": "Jealousy symbolism",
            "11.23": "Possessiveness symbolism", "11.24": "Trust", "11.25": "Betrayal symbolism",
            "11.26": "Relationship conflict", "11.27": "Breakup symbolism", "11.28": "Relationship healing",
            "11.29": "Relationship lessons", "11.30": "Ideal relationship environment"
        },
        primary_houses=[5, 7, 11],
        secondary_houses=[12, 8, 3],
        primary_karakas=["Venus", "Moon", "Mars"],
        primary_vargas=["D9", "D1"],
        jaimini_factors=["PK", "DK", "A5", "A7"],
        kp_significators=[5, 7, 11],
        timing_methods=["Vimshottari Dasha", "Transits"],
        system_priority=["PARASHARI", "JAIMINI", "KP"],
        keywords=["love", "romance", "dating", "relationship", "breakup", "crush", "attraction", "infatuation", "5th house"]
    ),
    12: OntologyNode(
        node_id=12,
        title="Children / Progeny",
        category="CHILDREN",
        subnodes={
            "12.1": "Childbirth promise", "12.2": "Number of children — only where methodology supports it",
            "12.3": "Timing of childbirth", "12.4": "First child", "12.5": "Subsequent children",
            "12.6": "Child-related delays", "12.7": "Child-related challenges", "12.8": "Child's temperament",
            "12.9": "Child's intelligence", "12.10": "Child's education", "12.11": "Child's career",
            "12.12": "Child's wealth", "12.13": "Child's relationship with parent", "12.14": "Parent-child bond",
            "12.15": "Child-related happiness", "12.16": "Child-related responsibilities",
            "12.17": "Adoption symbolism", "12.18": "Fertility-related symbolism", "12.19": "Progeny obstacles",
            "12.20": "Pregnancy timing", "12.21": "Childbirth timing", "12.22": "Children's future",
            "12.23": "Legacy through children"
        },
        primary_houses=[5, 2, 11],
        secondary_houses=[9, 1, 8],
        primary_karakas=["Jupiter", "Sun", "Moon"],
        primary_vargas=["D7", "D9"],
        jaimini_factors=["PK", "A5", "Saptamsha"],
        kp_significators=[2, 5, 11],
        timing_methods=["KP Sub-Lord", "Vimshottari Dasha", "Double Transit", "D7 Saptamsha"],
        system_priority=["PARASHARI", "JAIMINI", "KP"],
        special_engines=["kundali_milan_synastry_engine"],
        keywords=["children", "child", "progeny", "son", "daughter", "childbirth", "kids", "5th house", "saptamsha", "d7"]
    ),
    13: OntologyNode(
        node_id=13,
        title="Pregnancy / Maternity / Paternity",
        category="CHILDREN",
        subnodes={
            "13.1": "Conception timing", "13.2": "Pregnancy symbolism", "13.3": "Childbirth timing",
            "13.4": "Pregnancy complications symbolism", "13.5": "Fertility symbolism",
            "13.6": "IVF/assisted-reproduction timing questions", "13.7": "Childbirth method symbolism",
            "13.8": "Maternal transition", "13.9": "Paternal transition", "13.10": "Pregnancy-related travel",
            "13.11": "Pregnancy-related medical decisions"
        },
        primary_houses=[5, 2, 11, 8],
        secondary_houses=[12, 6],
        primary_karakas=["Moon", "Jupiter", "Venus", "Mars"],
        primary_vargas=["D7", "D9"],
        jaimini_factors=["PK", "A5"],
        kp_significators=[2, 5, 11],
        timing_methods=["KP Sub-Lord", "Vimshottari Dasha", "Transits"],
        system_priority=["KP", "PARASHARI", "TAJAKA"],
        keywords=["pregnancy", "conception", "maternity", "paternity", "ivf", "fertility", "beeja sphuta", "kshetra sphuta"]
    ),
    14: OntologyNode(
        node_id=14,
        title="Parents / Family",
        category="FAMILY",
        subnodes={
            "14.1": "Mother", "14.2": "Father", "14.3": "Parents' relationship", "14.4": "Mother's wellbeing",
            "14.5": "Father's wellbeing", "14.6": "Relationship with mother", "14.7": "Relationship with father",
            "14.8": "Parental influence", "14.9": "Family background", "14.10": "Family wealth",
            "14.11": "Family responsibilities", "14.12": "Family conflict", "14.13": "Family support",
            "14.14": "Family expectations", "14.15": "Family reputation", "14.16": "Ancestral themes",
            "14.17": "Family property", "14.18": "Family business", "14.19": "Family obligations",
            "14.20": "Leaving family home"
        },
        primary_houses=[4, 9, 2],
        secondary_houses=[10, 12, 1],
        primary_karakas=["Sun", "Moon", "Jupiter"],
        primary_vargas=["D12", "D9"],
        jaimini_factors=["MK", "BK", "A4", "A9", "Dwadasamsha"],
        kp_significators=[4, 9, 2],
        timing_methods=["Vimshottari Dasha", "Chara Dasha"],
        system_priority=["PARASHARI", "JAIMINI", "KP"],
        keywords=["mother", "father", "parents", "family", "ancestors", "lineage", "4th house", "9th house", "d12"]
    ),
    15: OntologyNode(
        node_id=15,
        title="Siblings / Extended Family",
        category="FAMILY",
        subnodes={
            "15.1": "Younger siblings", "15.2": "Elder siblings", "15.3": "Sibling relationship",
            "15.4": "Sibling support", "15.5": "Sibling rivalry", "15.6": "Sibling wealth",
            "15.7": "Sibling career", "15.8": "Sibling marriage", "15.9": "Sibling conflict",
            "15.10": "Sibling business", "15.11": "Extended relatives", "15.12": "Cousins", "15.13": "Family network"
        },
        primary_houses=[3, 11],
        secondary_houses=[2, 9],
        primary_karakas=["Mars", "Jupiter", "Mercury"],
        primary_vargas=["D3"],
        jaimini_factors=["BK", "A3", "A11", "Drekkana"],
        kp_significators=[3, 11],
        timing_methods=["Vimshottari Dasha", "Transits"],
        system_priority=["PARASHARI", "JAIMINI", "KP"],
        keywords=["brother", "sister", "sibling", "younger sibling", "elder sibling", "cousin", "3rd house", "d3"]
    ),
    16: OntologyNode(
        node_id=16,
        title="Friends / Network / Social Circle",
        category="NETWORK",
        subnodes={
            "16.1": "Number/size of network", "16.2": "Quality of network", "16.3": "Influential friends",
            "16.4": "Wealthy friends", "16.5": "Mentor network", "16.6": "Professional network",
            "16.7": "Client network", "16.8": "Business network", "16.9": "Political network",
            "16.10": "Institutional network", "16.11": "Foreign network", "16.12": "Online network",
            "16.13": "Community belonging", "16.14": "Social status through network", "16.15": "Gains through friends",
            "16.16": "Losses through friends", "16.17": "Betrayal symbolism", "16.18": "Toxic associations",
            "16.19": "Strategic alliances", "16.20": "Social mobility", "16.21": "Elite circles",
            "16.22": "Introductions/referrals", "16.23": "Audience building", "16.24": "Network growth timing",
            "16.25": "Network contraction", "16.26": "Network quality over quantity"
        },
        primary_houses=[11, 3, 7],
        secondary_houses=[10, 2, 9],
        primary_karakas=["Mercury", "Jupiter", "Rahu"],
        primary_vargas=["D11", "D10", "D9"],
        jaimini_factors=["A11", "A3", "AL"],
        kp_significators=[11, 3, 7],
        timing_methods=["Vimshottari Dasha", "Transits"],
        system_priority=["PARASHARI", "JAIMINI", "KP"],
        keywords=["friends", "network", "social circle", "alliances", "referrals", "community", "audience", "11th house"]
    ),
    17: OntologyNode(
        node_id=17,
        title="Public Image / Fame / Reputation",
        category="STATUS",
        subnodes={
            "17.1": "Public reputation", "17.2": "Professional reputation", "17.3": "Fame", "17.4": "Recognition",
            "17.5": "Visibility", "17.6": "Celebrity potential symbolism", "17.7": "Authority", "17.8": "Prestige",
            "17.9": "Social status", "17.10": "Leadership status", "17.11": "Public criticism",
            "17.12": "Scandal symbolism", "17.13": "Reputation recovery", "17.14": "Personal brand",
            "17.15": "Internet reputation", "17.16": "Media visibility", "17.17": "Institutional prestige",
            "17.18": "Legacy", "17.19": "Public influence", "17.20": "Audience size"
        },
        primary_houses=[10, 1, 11, 7],
        secondary_houses=[9, 5, 8],
        primary_karakas=["Sun", "Moon", "Jupiter", "Rahu"],
        primary_vargas=["D10", "D9", "D60"],
        jaimini_factors=["AL", "A10", "GL", "Karakamsha"],
        kp_significators=[10, 1, 11],
        timing_methods=["Vimshottari Dasha", "Chara Dasha", "Transits"],
        system_priority=["JAIMINI", "PARASHARI", "KP"],
        special_engines=["wealth_lagnas_engine"],
        keywords=["fame", "reputation", "public image", "status", "celebrity", "recognition", "personal brand", "arudha lagna", "10th house"]
    ),
    18: OntologyNode(
        node_id=18,
        title="Education",
        category="EDUCATION",
        subnodes={
            "18.1": "Basic education", "18.2": "Schooling", "18.3": "Higher education", "18.4": "University",
            "18.5": "Engineering", "18.6": "Medicine", "18.7": "Law", "18.8": "Commerce", "18.9": "Arts",
            "18.10": "Humanities", "18.11": "Sciences", "18.12": "Technology", "18.13": "Vocational education",
            "18.14": "Professional certification", "18.15": "Master's degree", "18.16": "Doctorate",
            "18.17": "Research", "18.18": "Academic success", "18.19": "Academic obstacles",
            "18.20": "Study abroad", "18.21": "Education loans", "18.22": "Educational institutions",
            "18.23": "Teacher relationships", "18.24": "Examinations", "18.25": "Competitive exams",
            "18.26": "Results", "18.27": "Admission", "18.28": "Scholarship", "18.29": "Dropout",
            "18.30": "Re-entry into education"
        },
        primary_houses=[5, 9, 4],
        secondary_houses=[2, 10, 6, 12],
        primary_karakas=["Jupiter", "Mercury", "Sun"],
        primary_vargas=["D24", "D9"],
        secondary_vargas=["D1", "D4"],
        jaimini_factors=["PK", "A5", "A9", "Siddhamsha"],
        kp_significators=[4, 9, 11],
        timing_methods=["KP Sub-Lord", "Vimshottari Dasha", "Transits"],
        system_priority=["PARASHARI", "KP", "JAIMINI"],
        keywords=["education", "degree", "university", "college", "exam", "studies", "academic", "scholarship", "5th house", "9th house", "d24"]
    ),
    19: OntologyNode(
        node_id=19,
        title="Skills / Talents",
        category="EDUCATION",
        subnodes={
            "19.1": "Writing", "19.2": "Speaking", "19.3": "Sales", "19.4": "Negotiation", "19.5": "Leadership",
            "19.6": "Programming", "19.7": "Engineering", "19.8": "Mathematics", "19.9": "Science",
            "19.10": "Research", "19.11": "Art", "19.12": "Music", "19.13": "Performance", "19.14": "Design",
            "19.15": "Strategy", "19.16": "Management", "19.17": "Entrepreneurship", "19.18": "Teaching",
            "19.19": "Languages", "19.20": "Public speaking", "19.21": "Marketing", "19.22": "Media",
            "19.23": "Diplomacy", "19.24": "Technical craftsmanship", "19.25": "Analytical ability",
            "19.26": "Intuition", "19.27": "Concentration", "19.28": "Memory", "19.29": "Learning speed",
            "19.30": "Adaptability"
        },
        primary_houses=[3, 5, 10],
        secondary_houses=[2, 1, 9],
        primary_karakas=["Mercury", "Mars", "Venus", "Jupiter"],
        primary_vargas=["D3", "D10", "D9"],
        jaimini_factors=["AmK", "PK", "Karakamsha"],
        kp_significators=[3, 5, 10],
        timing_methods=["Vimshottari Dasha"],
        system_priority=["PARASHARI", "JAIMINI", "NADI"],
        keywords=["skills", "talents", "programming", "writing", "speaking", "coding", "art", "strategy", "3rd house", "5th house"]
    ),
    20: OntologyNode(
        node_id=20,
        title="Foreign Travel / International Life",
        category="TRAVEL_LOCATION",
        subnodes={
            "20.1": "Foreign travel", "20.2": "Long-distance travel", "20.3": "Migration", "20.4": "Relocation",
            "20.5": "Permanent settlement abroad", "20.6": "Foreign education", "20.7": "Foreign employment",
            "20.8": "Foreign clients", "20.9": "Foreign business", "20.10": "International partnerships",
            "20.11": "Foreign marriage", "20.12": "Foreign spouse", "20.13": "Foreign income",
            "20.14": "Foreign assets", "20.15": "International recognition", "20.16": "Remote global work",
            "20.17": "Multiple-country life", "20.18": "Returning home", "20.19": "Living between countries",
            "20.20": "Travel frequency", "20.21": "Travel for career", "20.22": "Travel for relationships",
            "20.23": "Spiritual pilgrimage", "20.24": "Foreign institutional connections"
        },
        primary_houses=[12, 9, 3, 7],
        secondary_houses=[4, 10, 11],
        primary_karakas=["Rahu", "Saturn", "Moon", "Jupiter"],
        primary_vargas=["D4", "D9", "D12"],
        jaimini_factors=["A12", "A9", "AK", "AL"],
        kp_significators=[3, 9, 12],
        timing_methods=["KP Sub-Lord", "Vimshottari Dasha", "Transits"],
        system_priority=["KP", "PARASHARI", "JAIMINI"],
        keywords=["foreign", "abroad", "overseas", "travel", "international", "visa", "immigration", "foreign settlement", "12th house", "9th house"]
    ),
    21: OntologyNode(
        node_id=21,
        title="Relocation / Geographic Astrology",
        category="TRAVEL_LOCATION",
        subnodes={
            "21.1": "Best country", "21.2": "Best city", "21.3": "Best region", "21.4": "Career location",
            "21.5": "Wealth location", "21.6": "Relationship location", "21.7": "Marriage location",
            "21.8": "Education location", "21.9": "Business location", "21.10": "Spiritual location",
            "21.11": "Place to live", "21.12": "Place to work", "21.13": "Place to invest",
            "21.14": "Place to launch business", "21.15": "Place to retire", "21.16": "Temporary vs permanent relocation",
            "21.17": "Relocation timing", "21.18": "Relocation consequences"
        },
        primary_houses=[4, 12, 9, 3],
        secondary_houses=[10, 7, 1],
        primary_karakas=["Moon", "Rahu", "Saturn"],
        primary_vargas=["D4", "D10"],
        jaimini_factors=["A4", "A12"],
        kp_significators=[3, 9, 12, 4],
        timing_methods=["KP Sub-Lord", "Vimshottari Dasha", "Transits"],
        system_priority=["PARASHARI", "KP", "TAJAKA"],
        keywords=["relocation", "city", "country", "best place", "where to move", "relocate", "geographic"]
    ),
    22: OntologyNode(
        node_id=22,
        title="Home / Domestic Life",
        category="PROPERTY",
        subnodes={
            "22.1": "Home environment", "22.2": "Emotional peace", "22.3": "Domestic happiness",
            "22.4": "Family atmosphere", "22.5": "Living alone", "22.6": "Living with family",
            "22.7": "Living with spouse", "22.8": "Shared household", "22.9": "Home ownership",
            "22.10": "Home location", "22.11": "Home changes", "22.12": "Moving houses",
            "22.13": "Luxury home", "22.14": "Private space", "22.15": "Domestic conflict",
            "22.16": "Mother/home link"
        },
        primary_houses=[4, 2],
        secondary_houses=[12, 8, 1],
        primary_karakas=["Moon", "Venus", "Mars"],
        primary_vargas=["D4", "D16"],
        jaimini_factors=["MK", "A4"],
        kp_significators=[4, 2],
        timing_methods=["Vimshottari Dasha", "Transits"],
        system_priority=["PARASHARI", "JAIMINI", "KP"],
        keywords=["home", "domestic", "peace", "household", "living", "family atmosphere", "moving house", "4th house"]
    ),
    23: OntologyNode(
        node_id=23,
        title="Health / Wellbeing",
        category="HEALTH",
        subnodes={
            "23.1": "General vitality", "23.2": "Constitution", "23.3": "Physical resilience",
            "23.4": "Chronic tendencies", "23.5": "Acute illness symbolism", "23.6": "Recovery symbolism",
            "23.7": "Injury symbolism", "23.8": "Surgery symbolism", "23.9": "Stress symbolism",
            "23.10": "Sleep", "23.11": "Mental peace", "23.12": "Energy", "23.13": "Lifestyle",
            "23.14": "Hospitalization symbolism", "23.15": "Long-term wellbeing"
        },
        primary_houses=[1, 6, 8, 12],
        secondary_houses=[5, 3],
        primary_karakas=["Sun", "Mars", "Saturn", "Moon"],
        primary_vargas=["D6", "D30", "D9"],
        jaimini_factors=["GK", "A6", "A8"],
        kp_significators=[1, 6, 8, 12],
        timing_methods=["Vimshottari Dasha", "Yogini Dasha", "Double Transit", "Mars Triggers"],
        system_priority=["PARASHARI", "NADI", "JAIMINI", "KP"],
        special_engines=["medical_astrology_engine", "longevity_engine", "sensitive_points"],
        keywords=["health", "disease", "illness", "vitality", "constitution", "surgery", "hospital", "stress", "6th house", "8th house"]
    ),
    24: OntologyNode(
        node_id=24,
        title="Longevity",
        category="HEALTH",
        subnodes={
            "24.1": "Longevity assessment", "24.2": "Life-force strength", "24.3": "Vulnerable periods",
            "24.4": "Health-sensitive periods", "24.5": "Recovery periods", "24.6": "Accident symbolism",
            "24.7": "Major transition periods"
        },
        primary_houses=[8, 1, 3, 12],
        secondary_houses=[2, 7, 6],
        primary_karakas=["Saturn", "Jupiter", "Sun"],
        primary_vargas=["D8", "D30", "D3"],
        jaimini_factors=["Jaimini_3_Pairs", "GK", "Marakas", "Badhakas"],
        kp_significators=[1, 8, 12, 2, 7],
        timing_methods=["Jaimini Ayurdaya", "Vimshottari Dasha", "Maraka/Badhaka Periods", "Sula Dasha"],
        system_priority=["JAIMINI", "PARASHARI", "NADI"],
        special_engines=["longevity_engine", "sensitive_points"],
        keywords=["longevity", "ayurdaya", "lifespan", "maraka", "badhaka", "22nd drekkana", "64th navamsha", "8th house"]
    ),
    25: OntologyNode(
        node_id=25,
        title="Spirituality",
        category="SPIRITUALITY",
        subnodes={
            "25.1": "Spiritual inclination", "25.2": "Religious inclination", "25.3": "Meditation",
            "25.4": "Mantra", "25.5": "Devotion", "25.6": "Yoga", "25.7": "Guru connection",
            "25.8": "Temple/pilgrimage", "25.9": "Renunciation", "25.10": "Mysticism",
            "25.11": "Occult studies", "25.12": "Esoteric interests", "25.13": "Spiritual discipline",
            "25.14": "Spiritual crisis", "25.15": "Spiritual transformation", "25.16": "Moksha orientation"
        },
        primary_houses=[9, 12, 5, 8],
        secondary_houses=[1, 4],
        primary_karakas=["Jupiter", "Ketu", "Saturn", "Sun"],
        primary_vargas=["D20", "D9", "D60"],
        jaimini_factors=["AK", "Karakamsha", "Ketu_in_12th_from_Karakamsha", "A9", "A12"],
        kp_significators=[9, 12, 5],
        timing_methods=["Vimshottari Dasha", "Chara Dasha", "Narayana Dasha"],
        system_priority=["JAIMINI", "NADI", "PARASHARI", "KP"],
        keywords=["spirituality", "spiritual", "moksha", "meditation", "guru", "mantra", "devotion", "temple", "renunciation", "9th house", "12th house", "d20"]
    ),
    26: OntologyNode(
        node_id=26,
        title="Religion / Philosophy / Belief",
        category="SPIRITUALITY",
        subnodes={
            "26.1": "Religious orientation", "26.2": "Philosophy", "26.3": "Faith", "26.4": "Skepticism",
            "26.5": "Guru", "26.6": "Teacher", "26.7": "Tradition", "26.8": "Religious institutions",
            "26.9": "Pilgrimage", "26.10": "Dharma", "26.11": "Moral philosophy", "26.12": "Spiritual worldview"
        },
        primary_houses=[9, 5, 1],
        secondary_houses=[12, 4],
        primary_karakas=["Jupiter", "Sun"],
        primary_vargas=["D9", "D20"],
        jaimini_factors=["AK", "BK", "A9"],
        kp_significators=[9, 5],
        timing_methods=["Vimshottari Dasha"],
        system_priority=["PARASHARI", "JAIMINI"],
        keywords=["religion", "philosophy", "belief", "faith", "tradition", "morals", "pilgrimage", "dharma", "9th house"]
    ),
    27: OntologyNode(
        node_id=27,
        title="Occult / Esoteric",
        category="SPIRITUALITY",
        subnodes={
            "27.1": "Astrology", "27.2": "Jyotiṣa aptitude", "27.3": "Tantra symbolism", "27.4": "Mantra",
            "27.5": "Meditation", "27.6": "Mysticism", "27.7": "Hidden knowledge", "27.8": "Research",
            "27.9": "Occult curiosity", "27.10": "Psychic-symbolism questions", "27.11": "Past-life symbolism",
            "27.12": "Karmic symbolism", "27.13": "Spiritual transformation"
        },
        primary_houses=[8, 5, 9, 12],
        secondary_houses=[3, 10],
        primary_karakas=["Mercury", "Ketu", "Jupiter", "Saturn", "Rahu"],
        primary_vargas=["D8", "D20", "D9", "D60"],
        jaimini_factors=["AK", "Karakamsha", "A8"],
        kp_significators=[8, 5, 9, 12],
        timing_methods=["Vimshottari Dasha", "Chara Dasha"],
        system_priority=["JAIMINI", "PARASHARI", "NADI"],
        keywords=["occult", "esoteric", "astrology aptitude", "jyotish", "tantra", "mysticism", "hidden knowledge", "past life", "8th house"]
    ),
    28: OntologyNode(
        node_id=28,
        title="Legal / Litigation / Disputes",
        category="LEGAL_CONFLICT",
        subnodes={
            "28.1": "Lawsuits", "28.2": "Court cases", "28.3": "Litigation outcome", "28.4": "Civil disputes",
            "28.5": "Criminal-law situations", "28.6": "Business disputes", "28.7": "Contract disputes",
            "28.8": "Property disputes", "28.9": "Family disputes", "28.10": "Workplace disputes",
            "28.11": "Competition", "28.12": "Enemies", "28.13": "Opponents", "28.14": "Victory/loss symbolism",
            "28.15": "Settlement", "28.16": "Arbitration", "28.17": "Legal timing"
        },
        primary_houses=[6, 8, 12, 7],
        secondary_houses=[11, 10, 1],
        primary_karakas=["Mars", "Saturn", "Jupiter", "Rahu"],
        primary_vargas=["D6", "D30", "D9"],
        jaimini_factors=["GK", "A6", "A8"],
        kp_significators=[6, 8, 12, 11],
        timing_methods=["KP Sub-Lord", "Prashna", "Vimshottari Dasha", "Transits"],
        system_priority=["KP", "PARASHARI", "TAJAKA"],
        keywords=["lawsuit", "court", "litigation", "dispute", "settlement", "legal", "arbitration", "case", "6th house", "8th house"]
    ),
    29: OntologyNode(
        node_id=29,
        title="Competition / Enemies / Rivals",
        category="LEGAL_CONFLICT",
        subnodes={
            "29.1": "Competition", "29.2": "Competitors", "29.3": "Enemies", "29.4": "Hidden opponents",
            "29.5": "Workplace rivals", "29.6": "Business competitors", "29.7": "Political rivals",
            "29.8": "Social rivals", "29.9": "Defeating competitors", "29.10": "Losing to competitors",
            "29.11": "Strategic competition", "29.12": "Conflict resolution"
        },
        primary_houses=[6, 11, 3],
        secondary_houses=[8, 12, 7],
        primary_karakas=["Mars", "Saturn", "Sun", "Rahu"],
        primary_vargas=["D6", "D10"],
        jaimini_factors=["GK", "A6"],
        kp_significators=[6, 11],
        timing_methods=["KP Sub-Lord", "Vimshottari Dasha", "Transits"],
        system_priority=["PARASHARI", "KP", "JAIMINI"],
        keywords=["competition", "enemies", "rivals", "opponents", "conflict", "shatru", "victory", "6th house"]
    ),
    30: OntologyNode(
        node_id=30,
        title="Government / Politics / Power",
        category="POLITICS_POWER",
        subnodes={
            "30.1": "Government service", "30.2": "Administrative authority", "30.3": "Political career",
            "30.4": "Political leadership", "30.5": "Public office", "30.6": "Power", "30.7": "Authority",
            "30.8": "Bureaucracy", "30.9": "Government connections", "30.10": "Political network",
            "30.11": "Public influence", "30.12": "Institutional power", "30.13": "Election success",
            "30.14": "Political opposition", "30.15": "Public legitimacy", "30.16": "Governance roles"
        },
        primary_houses=[10, 5, 9, 1],
        secondary_houses=[11, 6, 7],
        primary_karakas=["Sun", "Mars", "Jupiter", "Rahu"],
        primary_vargas=["D10", "D9", "D5"],
        jaimini_factors=["AK", "AmK", "GL", "A10"],
        kp_significators=[10, 11, 6, 9],
        timing_methods=["Vimshottari Dasha", "Chara Dasha", "Double Transit"],
        system_priority=["PARASHARI", "JAIMINI", "KP"],
        special_engines=["wealth_lagnas_engine"],
        keywords=["government", "politics", "power", "election", "authority", "bureaucracy", "public office", "sun", "ghatika lagna"]
    ),
    31: OntologyNode(
        node_id=31,
        title="Social Status / Class Mobility",
        category="STATUS",
        subnodes={
            "31.1": "Social status", "31.2": "Rise in status", "31.3": "Fall in status", "31.4": "Elite access",
            "31.5": "Institutional recognition", "31.6": "Wealth-driven status", "31.7": "Marriage-driven status",
            "31.8": "Career-driven status", "31.9": "Network-driven status", "31.10": "Social mobility",
            "31.11": "Prestige", "31.12": "Honor", "31.13": "Public respect"
        },
        primary_houses=[10, 1, 11, 9],
        secondary_houses=[2, 7, 5],
        primary_karakas=["Sun", "Jupiter", "Moon"],
        primary_vargas=["D10", "D9"],
        jaimini_factors=["AL", "GL", "AmK", "A10"],
        kp_significators=[10, 11, 1],
        timing_methods=["Vimshottari Dasha", "Chara Dasha"],
        system_priority=["JAIMINI", "PARASHARI", "KP"],
        keywords=["social status", "class mobility", "prestige", "honor", "respect", "elite", "arudha lagna", "10th house"]
    ),
    32: OntologyNode(
        node_id=32,
        title="Personal Relationships Beyond Marriage",
        category="RELATIONSHIPS",
        subnodes={
            "32.1": "Friendship", "32.2": "Best friend", "32.3": "Social belonging", "32.4": "Mentor",
            "32.5": "Protégé", "32.6": "Colleague relationship", "32.7": "Business relationship",
            "32.8": "Boss relationship", "32.9": "Client relationship", "32.10": "Employee relationship",
            "32.11": "Sibling relationship", "32.12": "Parent relationship", "32.13": "Child relationship",
            "32.14": "Extended-family relationship", "32.15": "Community relationship"
        },
        primary_houses=[11, 7, 3, 9],
        secondary_houses=[5, 6, 10],
        primary_karakas=["Mercury", "Jupiter", "Moon"],
        primary_vargas=["D9", "D3", "D10"],
        jaimini_factors=["BK", "A11", "A7"],
        kp_significators=[11, 7, 3],
        timing_methods=["Vimshottari Dasha", "Transits"],
        system_priority=["PARASHARI", "JAIMINI", "KP"],
        keywords=["mentor", "colleague", "boss", "client", "friendship", "relationship", "networking"]
    ),
    33: OntologyNode(
        node_id=33,
        title="Sexuality / Intimacy",
        category="RELATIONSHIPS",
        subnodes={
            "33.1": "Sexual temperament", "33.2": "Intimacy needs", "33.3": "Passion", "33.4": "Sensuality",
            "33.5": "Sexual compatibility", "33.6": "Emotional-sexual connection", "33.7": "Privacy",
            "33.8": "Intimacy satisfaction", "33.9": "Sexual conflict symbolism", "33.10": "Marriage intimacy",
            "33.11": "Desire patterns"
        },
        primary_houses=[7, 8, 12, 5],
        secondary_houses=[1, 2],
        primary_karakas=["Venus", "Mars", "Moon", "Rahu"],
        primary_vargas=["D9", "D30"],
        jaimini_factors=["DK", "A7", "A8"],
        kp_significators=[7, 8, 12, 5],
        timing_methods=["Vimshottari Dasha", "Transits"],
        system_priority=["PARASHARI", "JAIMINI"],
        keywords=["sexuality", "intimacy", "passion", "sensuality", "desire", "compatibility", "7th house", "8th house", "12th house"]
    ),
    34: OntologyNode(
        node_id=34,
        title="Psychological / Emotional Patterns",
        category="PSYCHOLOGY",
        subnodes={
            "34.1": "Emotional regulation symbolism", "34.2": "Emotional security", "34.3": "Anxiety symbolism",
            "34.4": "Fear patterns", "34.5": "Attachment tendencies", "34.6": "Trust", "34.7": "Vulnerability",
            "34.8": "Emotional resilience", "34.9": "Rejection sensitivity", "34.10": "Need for control",
            "34.11": "Need for freedom", "34.12": "Isolation", "34.13": "Emotional support",
            "34.14": "Inner peace", "34.15": "Self-sabotage symbolism", "34.16": "Repeating emotional patterns"
        },
        primary_houses=[4, 1, 5, 8],
        secondary_houses=[12, 6],
        primary_karakas=["Moon", "Mercury", "Saturn", "Rahu", "Ketu"],
        primary_vargas=["D1", "D9", "D30"],
        jaimini_factors=["AK", "Moon_in_Navamsha", "Karakamsha"],
        kp_significators=[4, 1, 8],
        timing_methods=["Vimshottari Dasha", "Transits"],
        system_priority=["PARASHARI", "JAIMINI"],
        special_engines=["advanced_avasthas"],
        keywords=["psychology", "emotional", "anxiety", "fear", "trust", "mental peace", "attachment", "moon", "4th house"]
    ),
    35: OntologyNode(
        node_id=35,
        title="Life Events",
        category="EVENTS",
        subnodes={
            "35.1": "First major success", "35.2": "First major failure", "35.3": "First income",
            "35.4": "First job", "35.5": "Major career change", "35.6": "First major relationship",
            "35.7": "Marriage", "35.8": "First child", "35.9": "Major relocation",
            "35.10": "Property purchase", "35.11": "Major financial gain", "35.12": "Major financial loss",
            "35.13": "Major education milestone", "35.14": "Major recognition", "35.15": "Major crisis",
            "35.16": "Spiritual turning point", "35.17": "Retirement", "35.18": "Late-life transformation"
        },
        primary_houses=[10, 7, 5, 4, 12, 2],
        secondary_houses=[1, 8, 9, 11],
        primary_karakas=["Jupiter", "Saturn", "Sun", "Venus", "Mars", "Rahu"],
        primary_vargas=["D1", "D9", "D10", "D7", "D4"],
        jaimini_factors=["AK", "AmK", "DK", "AL"],
        kp_significators=[10, 7, 5, 4, 2, 11],
        timing_methods=["Vimshottari Dasha", "Chara Dasha", "Double Transit", "KP Sub-Lord"],
        system_priority=["PARASHARI", "JAIMINI", "KP", "TAJAKA"],
        special_engines=["forward_timing_scanner", "event_analysis"],
        keywords=["life events", "milestone", "breakthrough", "crisis", "turning point", "marriage event", "first job"]
    ),
    36: OntologyNode(
        node_id=36,
        title="Timing Engine",
        category="DYNAMIC_TIMING",
        subnodes={
            "36.1": "Vimśottarī Mahādaśā", "36.2": "Antardaśā", "36.3": "Pratyantardaśā",
            "36.4": "Other relevant Vimśottari subperiods", "36.5": "Jaimini Chara Daśā",
            "36.6": "Narayana Daśā", "36.7": "Mandooka Daśā", "36.8": "Sthira Daśā",
            "36.9": "Śūla Daśā", "36.10": "Brahma/Rudra/Maheśvara techniques where relevant",
            "36.11": "KP Vimshottari", "36.12": "KP sub-period timing", "36.13": "Transit timing",
            "36.14": "Transit conjunctions", "36.15": "Transit aspects", "36.16": "Transit activation of natal lords",
            "36.17": "Transit activation of houses", "36.18": "Jupiter transit", "36.19": "Saturn transit",
            "36.20": "Rahu/Ketu transit", "36.21": "Mars transit", "36.22": "Venus transit",
            "36.23": "Mercury transit", "36.24": "Solar transit", "36.25": "Eclipse activation",
            "36.26": "Retrograde return/re-entry", "36.27": "Stationary periods", "36.28": "Transit windows",
            "36.29": "Event clustering", "36.30": "Multi-system timing convergence"
        },
        primary_houses=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        primary_karakas=["Jupiter", "Saturn", "Mars", "Rahu", "Ketu", "Moon"],
        primary_vargas=["D1", "D9", "D10"],
        system_priority=["KP", "TAJAKA", "NADI", "PARASHARI", "JAIMINI"],
        special_engines=["forward_timing_scanner", "dasha_engine", "ashtakavarga_kakshya_engine", "gochara_vedha_engine"],
        keywords=["timing", "when", "dasha", "transit", "mahadasha", "antardasha", "pratyantardasha", "chara dasha", "kakshya", "double transit"]
    ),
    37: OntologyNode(
        node_id=37,
        title="Praśna / Horary",
        category="HORARY",
        subnodes={
            "37.1": "Will I get the job?", "37.2": "Should I accept this offer?", "37.3": "Should I start this business?",
            "37.4": "Will this business succeed?", "37.5": "Will I get the client?", "37.6": "Will I receive payment?",
            "37.7": "Will I recover money?", "37.8": "Will this relationship continue?", "37.9": "Will marriage happen?",
            "37.10": "Will this proposal work?", "37.11": "Will I pass?", "37.12": "Will I get admission?",
            "37.13": "Should I travel?", "37.14": "Should I relocate?", "37.15": "Should I buy this property?",
            "37.16": "Will property purchase complete?", "37.17": "Will lawsuit succeed?", "37.18": "Should I settle?",
            "37.19": "Will loan be approved?", "37.20": "Will lost object be recovered?", "37.21": "Was something stolen?",
            "37.22": "Where is lost property?", "37.23": "Should I invest?", "37.24": "Will money arrive?",
            "37.25": "Will a person contact me?", "37.26": "Should I contact someone?", "37.27": "Will a contract be signed?",
            "37.28": "Will an election succeed?", "37.29": "Will government approval arrive?", "37.30": "General question"
        },
        primary_houses=[1, 7, 10, 11, 2, 6],
        primary_karakas=["Moon", "Jupiter", "Mercury"],
        primary_vargas=["D1", "D9"],
        kp_significators=[1, 2, 6, 7, 10, 11],
        timing_methods=["KP 249 Ruling Planets", "Prashna Kundli", "Tajaka Ithasala/Easarpha"],
        system_priority=["KP", "TAJAKA", "PARASHARI"],
        special_engines=["kp_engine", "panchangam_engine", "tajika_engine"],
        keywords=["prashna", "horary", "will i", "should i", "will it happen", "lost object", "yes or no", "ruling planets"]
    ),
    38: OntologyNode(
        node_id=38,
        title="Muhūrta / Electional Astrology",
        category="ELECTIONAL",
        subnodes={
            "38.1": "Business launch", "38.2": "Company registration", "38.3": "Product launch",
            "38.4": "Website launch", "38.5": "App launch", "38.6": "Software launch", "38.7": "Contract signing",
            "38.8": "Partnership signing", "38.9": "Marriage", "38.10": "Engagement", "38.11": "First meeting",
            "38.12": "Job joining", "38.13": "Job resignation", "38.14": "House purchase",
            "38.15": "Property registration", "38.16": "Vehicle purchase", "38.17": "Travel",
            "38.18": "Education enrollment", "38.19": "Examination", "38.20": "Investment",
            "38.21": "Bank account opening", "38.22": "Company incorporation", "38.23": "Construction commencement",
            "38.24": "Foundation ceremony", "38.25": "Medical procedure — with medical advice taking priority",
            "38.26": "Religious ceremony", "38.27": "Puja", "38.28": "Homa", "38.29": "Naming ceremony",
            "38.30": "Festival event", "38.31": "Important signing", "38.32": "Major negotiation"
        },
        primary_houses=[1, 11, 10, 9, 4, 2],
        primary_karakas=["Jupiter", "Venus", "Mercury", "Moon"],
        primary_vargas=["D1", "D9"],
        timing_methods=["Panchanga Suddhi", "Tarabala", "Chandrabala", "Choghadiya", "Abhijit Muhurta", "Hora"],
        system_priority=["PARASHARI", "TAJAKA"],
        special_engines=["panchangam_engine", "pancha_pakshi_engine", "navatara_chakra_engine"],
        keywords=["muhurta", "auspicious time", "good time to start", "launch date", "signing date", "griha pravesh", "wedding date"]
    ),
    39: OntologyNode(
        node_id=39,
        title="Panchāṅga Engine",
        category="ASTRONOMY",
        subnodes={
            "39.1": "Tithi", "39.2": "Vara", "39.3": "Nakṣatra", "39.4": "Yoga", "39.5": "Karaṇa",
            "39.6": "Sunrise", "39.7": "Sunset", "39.8": "Moonrise", "39.9": "Moonset",
            "39.10": "Rāhu Kāla", "39.11": "Yamaganda", "39.12": "Gulika", "39.13": "Abhijit",
            "39.14": "Choghadiya", "39.15": "Durmuhurta", "39.16": "Varjyam", "39.17": "Amrita Siddhi",
            "39.18": "Siddha Yoga", "39.19": "Festivals", "39.20": "Ekādaśī", "39.21": "Pūrṇimā",
            "39.22": "Amāvasyā", "39.23": "Saṅkrānti", "39.24": "Eclipses", "39.25": "Regional calendrical differences"
        },
        primary_houses=[1],
        primary_karakas=["Sun", "Moon"],
        timing_methods=["Drik Ganita Ephemeris"],
        system_priority=["PARASHARI"],
        special_engines=["panchangam_engine"],
        keywords=["panchang", "tithi", "nakshatra", "rahu kalam", "abhijit", "choghadiya", "karana", "amavasya", "purnima"]
    ),
    40: OntologyNode(
        node_id=40,
        title="Compatibility",
        category="RELATIONSHIPS",
        subnodes={
            "40.1": "Marriage compatibility", "40.2": "Romantic compatibility", "40.3": "Emotional compatibility",
            "40.4": "Sexual compatibility", "40.5": "Communication compatibility", "40.6": "Intellectual compatibility",
            "40.7": "Financial compatibility", "40.8": "Family compatibility", "40.9": "Lifestyle compatibility",
            "40.10": "Religious compatibility", "40.11": "Cultural compatibility", "40.12": "Geographic compatibility",
            "40.13": "Long-distance compatibility", "40.14": "Business compatibility", "40.15": "Cofounder compatibility",
            "40.16": "Investor-founder compatibility", "40.17": "Employer-employee compatibility",
            "40.18": "Manager-subordinate compatibility", "40.19": "Friendship compatibility", "40.20": "Team compatibility",
            "40.21": "Partnership compatibility", "40.22": "Parent-child compatibility", "40.23": "Sibling compatibility"
        },
        primary_houses=[7, 1, 5, 11],
        secondary_houses=[2, 4, 8, 12],
        primary_karakas=["Venus", "Moon", "Jupiter", "Mars", "Mercury"],
        primary_vargas=["D9", "D1"],
        jaimini_factors=["AK_DK_harmony", "Upapada_harmony"],
        timing_methods=["Shared Dasha/Transit activation"],
        system_priority=["JAIMINI", "PARASHARI", "KP"],
        special_engines=["kundali_milan_synastry_engine"],
        keywords=["compatibility", "match", "ashtakoota", "guna milan", "synastry", "cofounder compatibility", "partner match"]
    ),
    41: OntologyNode(
        node_id=41,
        title="Synastry / Relationship Dynamics",
        category="RELATIONSHIPS",
        subnodes={
            "41.1": "Person A's Moon vs B's Moon", "41.2": "Venus-to-Mars", "41.3": "Moon-to-Venus",
            "41.4": "Moon-to-Mars", "41.5": "Venus-to-Saturn", "41.6": "Venus-to-Jupiter",
            "41.7": "Mars-to-Saturn", "41.8": "7th-lord interconnection", "41.9": "Lagna interconnection",
            "41.10": "Navamsha relationship", "41.11": "Jaimini Karaka interaction", "41.12": "AK-DK dynamics",
            "41.13": "Darakaraka interaction", "41.14": "Upapada interaction", "41.15": "Arudha interaction",
            "41.16": "KP marriage significators", "41.17": "Shared timing", "41.18": "Relationship activation periods",
            "41.19": "Marriage activation", "41.20": "Separation activation"
        },
        primary_houses=[7, 1, 5, 8],
        secondary_houses=[2, 11, 12],
        primary_karakas=["Venus", "Moon", "Mars", "Jupiter"],
        primary_vargas=["D9"],
        jaimini_factors=["AK", "DK", "UL", "AL"],
        kp_significators=[2, 7, 11],
        timing_methods=["Shared Vimshottari Timeline", "Double Transit"],
        system_priority=["JAIMINI", "PARASHARI", "KP"],
        special_engines=["kundali_milan_synastry_engine"],
        keywords=["synastry", "interconnection", "ak-dk", "upapada interaction", "cross-chart", "venus mars"]
    ),
    42: OntologyNode(
        node_id=42,
        title="KP Specialized Questions",
        category="SYSTEM_KP",
        subnodes={
            "42.1": "Job", "42.2": "Promotion", "42.3": "Transfer", "42.4": "Business", "42.5": "Marriage",
            "42.6": "Divorce", "42.7": "Childbirth", "42.8": "Education", "42.9": "Finance", "42.10": "Property",
            "42.11": "Litigation", "42.12": "Travel", "42.13": "Foreign settlement", "42.14": "Recovery of money",
            "42.15": "Loan", "42.16": "Election", "42.17": "Contract", "42.18": "Career change",
            "42.19": "Business profit", "42.20": "Specific-event timing"
        },
        primary_houses=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        primary_karakas=["Ruling_Planets"],
        kp_significators=[2, 6, 7, 10, 11],
        timing_methods=["KP Cuspal Sub-Lord (CSL)", "KP 249 Sub-Lords", "4-Fold ABCD Significators"],
        system_priority=["KP"],
        special_engines=["kp_engine", "kp_interlinks_engine"],
        keywords=["kp", "cusp", "sub lord", "csl", "significator", "ruling planets", "kp timing", "249"]
    ),
    43: OntologyNode(
        node_id=43,
        title="Jaimini Specialized Engine",
        category="SYSTEM_JAIMINI",
        subnodes={
            "43.1": "Chara Karakas", "43.2": "Atmakaraka", "43.3": "Amatyakaraka", "43.4": "Bhratrikaraka",
            "43.5": "Matrikaraka", "43.6": "Putrakaraka", "43.7": "Gnatikaraka", "43.8": "Darakaraka",
            "43.9": "Karakamsha", "43.10": "Swamsha", "43.11": "Arudha Lagna", "43.12": "A2", "43.13": "A3",
            "43.14": "A4", "43.15": "A5", "43.16": "A6", "43.17": "A7", "43.18": "A8", "43.19": "A9",
            "43.20": "A10", "43.21": "A11", "43.22": "Upapada Lagna", "43.23": "Rāśi Dṛṣṭi", "43.24": "Argala",
            "43.25": "Virodhargala", "43.26": "Jaimini Raja Yoga", "43.27": "Jaimini Dhana indicators",
            "43.28": "Career", "43.29": "Marriage", "43.30": "Wealth", "43.31": "Status", "43.32": "Children",
            "43.33": "Spiritual purpose", "43.34": "Chara Daśā", "43.35": "Narayana Daśā", "43.36": "Mandooka",
            "43.37": "Sthira", "43.38": "Śūla", "43.39": "Brahma", "43.40": "Rudra", "43.41": "Maheśvara"
        },
        primary_houses=[1, 5, 9, 10, 7, 2, 11],
        primary_vargas=["D1", "D9"],
        jaimini_factors=["AK", "AmK", "BK", "MK", "PK", "GK", "DK", "AL", "UL", "A1-A12", "Argala", "Karakamsha"],
        timing_methods=["Chara Dasha", "Narayana Dasha", "Sula Dasha"],
        system_priority=["JAIMINI"],
        special_engines=["jaimini_engine", "jaimini_chara_dasha_engine", "jaimini_arudha_argala_engine"],
        keywords=["jaimini", "atmakaraka", "amatyakaraka", "darakaraka", "chara karaka", "arudha lagna", "upapada", "argala", "chara dasha"]
    ),
    44: OntologyNode(
        node_id=44,
        title="Remedies",
        category="REMEDIES",
        subnodes={
            "44.1": "Mantra", "44.2": "Japa", "44.3": "Puja", "44.4": "Homa/Havan", "44.5": "Dāna",
            "44.6": "Fasting", "44.7": "Seva", "44.8": "Temple practice", "44.9": "Pilgrimage",
            "44.10": "Yantra", "44.11": "Deity practice", "44.12": "Behavioral discipline",
            "44.13": "Lifestyle remedy", "44.14": "Planetary remedy", "44.15": "Daśā-specific remedy",
            "44.16": "Transit-specific remedy", "44.17": "Career remedy", "44.18": "Relationship remedy",
            "44.19": "Financial remedy", "44.20": "Property remedy", "44.21": "Spiritual remedy"
        },
        primary_houses=[1, 5, 9, 12, 6, 8],
        primary_karakas=["Jupiter", "Sun", "Saturn", "Ketu", "Rahu"],
        timing_methods=["Planetary Horas", "Panchanga", "Vara from Sunrise"],
        system_priority=["PARASHARI", "NADI"],
        special_engines=["remedy_engine"],
        keywords=["remedy", "mantra", "japa", "dana", "puja", "homa", "charity", "fasting", "upaya", "lal kitab"]
    ),
    45: OntologyNode(
        node_id=45,
        title="Gemstones / Ratna",
        category="REMEDIES",
        subnodes={
            "45.1": "Suitable gemstone", "45.2": "Unsuitable gemstone", "45.3": "Functional benefic",
            "45.4": "Yogakāraka", "45.5": "Planetary strength", "45.6": "D1 suitability",
            "45.7": "D9 confirmation", "45.8": "Daśā suitability", "45.9": "Transit suitability",
            "45.10": "Gemstone risks", "45.11": "Metal", "45.12": "Finger", "45.13": "Weight",
            "45.14": "Mantra", "45.15": "Day/time", "45.16": "Trial period", "45.17": "Alternative stones"
        },
        primary_houses=[1, 5, 9],
        secondary_houses=[6, 8, 12, 2, 7],
        primary_karakas=["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"],
        primary_vargas=["D1", "D9"],
        timing_methods=["Functional Benefic Evaluation", "Gemstone Contraindication Matrix"],
        system_priority=["PARASHARI"],
        special_engines=["functional_benefic_engine", "remedy_engine"],
        keywords=["gemstone", "ratna", "ruby", "pearl", "emerald", "yellow sapphire", "blue sapphire", "diamond", "anukool"]
    ),
    46: OntologyNode(
        node_id=46,
        title="Vāstu",
        category="SPATIAL_VASTU",
        subnodes={
            "46.1": "Entrance", "46.2": "Bedroom", "46.3": "Sleep direction", "46.4": "Head direction",
            "46.5": "Study desk", "46.6": "Work desk", "46.7": "Office entrance", "46.8": "Cash area",
            "46.9": "Kitchen", "46.10": "Prayer room", "46.11": "Bathrooms", "46.12": "Staircase",
            "46.13": "Property orientation", "46.14": "Plot shape", "46.15": "Office layout",
            "46.16": "Business premises", "46.17": "Residential premises", "46.18": "Productivity",
            "46.19": "Wealth-oriented spatial questions", "46.20": "Relationship-oriented spatial questions"
        },
        primary_houses=[4, 2, 10, 11],
        primary_karakas=["Mars", "Sun", "Venus", "Jupiter", "Mercury"],
        timing_methods=["Directional Astrometrics"],
        system_priority=["PARASHARI"],
        keywords=["vastu", "direction", "entrance", "bedroom", "office layout", "north east", "south west", "cash locker"]
    ),
    47: OntologyNode(
        node_id=47,
        title="Financial / Business Location",
        category="STRATEGIC_EXPANSION",
        subnodes={
            "47.1": "Best country for business", "47.2": "Best city for business", "47.3": "Best city for career",
            "47.4": "Best country for wealth", "47.5": "Best location for clients",
            "47.6": "Best location for headquarters", "47.7": "Best place to register business",
            "47.8": "Best place to invest", "47.9": "Best place for property", "47.10": "Best place to retire",
            "47.11": "Best place for relationships", "47.12": "Best place for education"
        },
        primary_houses=[7, 10, 11, 12, 9, 4],
        primary_karakas=["Mercury", "Jupiter", "Rahu", "Saturn"],
        primary_vargas=["D10", "D4"],
        jaimini_factors=["A10", "A11", "AL"],
        kp_significators=[7, 10, 11, 12],
        system_priority=["PARASHARI", "KP", "TAJAKA"],
        keywords=["business location", "best city for business", "headquarters location", "incorporate location", "overseas clients"]
    ),
    48: OntologyNode(
        node_id=48,
        title="Organizational Astrology",
        category="STRATEGIC_EXPANSION",
        subnodes={
            "48.1": "Founder profile", "48.2": "Cofounder profile", "48.3": "Leadership compatibility",
            "48.4": "Employee compatibility", "48.5": "Team composition", "48.6": "Executive hiring",
            "48.7": "Investor-founder compatibility", "48.8": "Partner selection", "48.9": "Organizational culture",
            "48.10": "Leadership succession", "48.11": "Company founding chart", "48.12": "Company launch chart",
            "48.13": "Corporate timing", "48.14": "Expansion timing", "48.15": "Acquisition timing",
            "48.16": "Product-launch timing", "48.17": "Office opening", "48.18": "Major contract timing"
        },
        primary_houses=[10, 7, 11, 1, 6],
        secondary_houses=[9, 3, 2],
        primary_karakas=["Sun", "Mercury", "Jupiter", "Mars", "Saturn"],
        primary_vargas=["D10", "D11"],
        jaimini_factors=["AmK", "AL", "A10", "A11"],
        timing_methods=["Muhurta", "Entity Kundli", "Double Transit"],
        system_priority=["PARASHARI", "KP", "TAJAKA"],
        special_engines=["institutional_chakra_engine", "kundali_milan_synastry_engine"],
        keywords=["founder", "cofounder", "executive hiring", "team composition", "investor compatibility", "company founding", "corporate timing"]
    ),
    49: OntologyNode(
        node_id=49,
        title="Company / Event Charts",
        category="STRATEGIC_EXPANSION",
        subnodes={
            "49.1": "Company incorporation chart", "49.2": "Business launch chart", "49.3": "Partnership formation chart",
            "49.4": "Marriage event chart", "49.5": "Contract chart", "49.6": "Property-registration chart",
            "49.7": "Product launch chart", "49.8": "IPO/listing symbolism", "49.9": "Website launch",
            "49.10": "Project launch", "49.11": "Organization restructuring"
        },
        primary_houses=[1, 10, 7, 11, 2],
        primary_karakas=["Mercury", "Sun", "Jupiter", "Rahu"],
        primary_vargas=["D10", "D1"],
        timing_methods=["Muhurta Selection", "Event Ingress Kundli"],
        system_priority=["PARASHARI", "TAJAKA", "KP"],
        special_engines=["institutional_chakra_engine"],
        keywords=["company chart", "incorporation chart", "event chart", "ipo chart", "launch chart", "kota chakra"]
    ),
    50: OntologyNode(
        node_id=50,
        title="Career × Network × Wealth",
        category="STRATEGIC_EXPANSION",
        subnodes={
            "50.1": "Career through network", "50.2": "Wealth through network", "50.3": "Clients through network",
            "50.4": "Investors through network", "50.5": "Mentors through network",
            "50.6": "Foreign opportunities through network", "50.7": "Partnerships through network",
            "50.8": "Status through network", "50.9": "Business expansion through network",
            "50.10": "Network-driven career transition", "50.11": "Network-driven wealth acceleration",
            "50.12": "Network-driven risks"
        },
        primary_houses=[10, 11, 2, 7],
        secondary_houses=[9, 12, 1],
        primary_karakas=["Mercury", "Jupiter", "Sun", "Rahu"],
        primary_vargas=["D10", "D2", "D11"],
        jaimini_factors=["AmK", "A10", "A11", "AL", "Indu_Lagna"],
        kp_significators=[2, 7, 10, 11],
        timing_methods=["Vimshottari Dasha", "Double Transit", "Indu Lagna Activation"],
        system_priority=["PARASHARI", "JAIMINI", "KP"],
        special_engines=["wealth_lagnas_engine", "forward_timing_scanner"],
        keywords=["career network wealth", "network scaling", "referral business", "investor network", "high net worth network", "11th house"]
    ),
    51: OntologyNode(
        node_id=51,
        title="Life-Cycle Analysis",
        category="TIMELINE_TRANSITION",
        subnodes={
            "51.1": "Childhood", "51.2": "Adolescence", "51.3": "Education years", "51.4": "Early adulthood",
            "51.5": "Career formation", "51.6": "Relationship formation", "51.7": "Marriage period",
            "51.8": "Family-building period", "51.9": "Wealth-building period", "51.10": "Peak career",
            "51.11": "Midlife transformation", "51.12": "Later-life stability", "51.13": "Retirement", "51.14": "Legacy"
        },
        primary_houses=[1, 4, 5, 9, 10, 11],
        primary_karakas=["Sun", "Moon", "Saturn", "Jupiter"],
        primary_vargas=["D1", "D9", "D60"],
        jaimini_factors=["AK", "AmK", "AL"],
        timing_methods=["Vimshottari Mahadasha Eras", "Bhrigu Nandi Nadi Progressions"],
        system_priority=["PARASHARI", "JAIMINI", "NADI"],
        special_engines=["bhrigu_nandi_nadi_engine", "dasha_engine"],
        keywords=["lifecycle", "eras", "decades", "childhood", "peak career", "midlife", "retirement", "30-year cycle"]
    ),
    52: OntologyNode(
        node_id=52,
        title="Major Life Transitions",
        category="TIMELINE_TRANSITION",
        subnodes={
            "52.1": "Leaving home", "52.2": "Starting university", "52.3": "Entering workforce",
            "52.4": "First serious relationship", "52.5": "Marriage", "52.6": "First child",
            "52.7": "Career switch", "52.8": "Starting business", "52.9": "Moving abroad",
            "52.10": "Returning home", "52.11": "Major wealth event", "52.12": "Major loss",
            "52.13": "Spiritual awakening symbolism", "52.14": "Retirement", "52.15": "Legacy transition"
        },
        primary_houses=[1, 10, 7, 5, 4, 12, 8],
        primary_karakas=["Saturn", "Jupiter", "Rahu", "Ketu"],
        primary_vargas=["D1", "D9", "D10"],
        jaimini_factors=["AK", "AmK", "AL"],
        timing_methods=["Dasha Sandhi", "Dasha Chidra", "Major Ingresses"],
        system_priority=["PARASHARI", "JAIMINI", "KP"],
        keywords=["transition", "major shift", "dasha change", "crossroads", "leaving home", "turning point"]
    ),
    53: OntologyNode(
        node_id=53,
        title="Questions About Other People",
        category="RELATIONAL_SENSING",
        subnodes={
            "53.1": "Who is this person?", "53.2": "What role do they play?", "53.3": "Are they beneficial?",
            "53.4": "Are they harmful?", "53.5": "Can I trust them?", "53.6": "Will they help my career?",
            "53.7": "Will they become a partner?", "53.8": "Will they become spouse?",
            "53.9": "Will they remain in my life?", "53.10": "Will they contact me?",
            "53.11": "Is this person a mentor?", "53.12": "Is this person a competitor?",
            "53.13": "What is the relationship dynamic?"
        },
        primary_houses=[7, 11, 6, 9, 3],
        primary_karakas=["Mercury", "Venus", "Jupiter", "Rahu"],
        timing_methods=["Prashna", "Synastry", "Transits"],
        system_priority=["KP", "TAJAKA", "JAIMINI"],
        keywords=["who is this person", "can i trust them", "will they contact me", "are they harmful", "mentor or competitor"]
    ),
    54: OntologyNode(
        node_id=54,
        title="Decision Support",
        category="DECISION_SUPPORT",
        subnodes={
            "54.1": "Which career?", "54.2": "Which job?", "54.3": "Which business?", "54.4": "Which partner?",
            "54.5": "Which university?", "54.6": "Which country?", "54.7": "Which city?", "54.8": "Which property?",
            "54.9": "Which date?", "54.10": "Which business partner?", "54.11": "Which investor?",
            "54.12": "Whether to quit", "54.13": "Whether to relocate", "54.14": "Whether to invest",
            "54.15": "Whether to launch", "54.16": "Whether to marry", "54.17": "Whether to sign",
            "54.18": "Whether to pursue"
        },
        primary_houses=[1, 10, 7, 5, 9, 4],
        primary_karakas=["Mercury", "Jupiter", "Sun"],
        timing_methods=["KP Sub-Lord", "Prashna Horary", "Muhurta", "Transit Activation"],
        system_priority=["KP", "PARASHARI", "TAJAKA"],
        keywords=["which career", "which job", "whether to quit", "whether to launch", "should i do this", "decision"]
    ),
    55: OntologyNode(
        node_id=55,
        title="Lost / Unknown Objects",
        category="HORARY",
        subnodes={
            "55.1": "Lost object", "55.2": "Stolen object", "55.3": "Missing document", "55.4": "Missing money",
            "55.5": "Missing phone", "55.6": "Missing vehicle", "55.7": "Recovery possibility",
            "55.8": "Location symbolism", "55.9": "Time of recovery"
        },
        primary_houses=[2, 4, 7, 8, 12],
        primary_karakas=["Mercury", "Moon", "Mars"],
        timing_methods=["Prashna Horary Direction & Signs", "KP 249 Sub-Lord"],
        system_priority=["KP", "TAJAKA", "PARASHARI"],
        keywords=["lost object", "stolen", "missing", "where is it", "will i recover it", "lost money", "lost phone"]
    ),
    56: OntologyNode(
        node_id=56,
        title="Documents / Approvals / Administration",
        category="ADMIN_APPROVALS",
        subnodes={
            "56.1": "Visa", "56.2": "Passport", "56.3": "Immigration approval", "56.4": "Government approval",
            "56.5": "License", "56.6": "Registration", "56.7": "Legal document", "56.8": "Bank approval",
            "56.9": "Loan approval", "56.10": "University admission", "56.11": "Employment documentation",
            "56.12": "Contract signing", "56.13": "Business registration"
        },
        primary_houses=[3, 9, 10, 6, 11, 12],
        primary_karakas=["Mercury", "Sun", "Jupiter", "Rahu"],
        primary_vargas=["D10", "D9"],
        kp_significators=[3, 9, 11, 6],
        timing_methods=["KP Sub-Lord", "Prashna", "Transits"],
        system_priority=["KP", "PARASHARI", "TAJAKA"],
        keywords=["visa", "passport", "immigration", "approval", "license", "permit", "contract signing", "registration"]
    ),
    57: OntologyNode(
        node_id=57,
        title="Travel",
        category="TRAVEL_LOCATION",
        subnodes={
            "57.1": "Short travel", "57.2": "Long travel", "57.3": "Foreign travel", "57.4": "Business travel",
            "57.5": "Education travel", "57.6": "Religious travel", "57.7": "Marriage-related travel",
            "57.8": "Relocation travel", "57.9": "Travel timing", "57.10": "Travel problems",
            "57.11": "Travel benefit", "57.12": "Return journey"
        },
        primary_houses=[3, 9, 12, 7],
        secondary_houses=[4, 10],
        primary_karakas=["Moon", "Rahu", "Mercury", "Jupiter"],
        primary_vargas=["D4", "D9"],
        kp_significators=[3, 9, 12],
        timing_methods=["KP Sub-Lord", "Panchanga", "Transits"],
        system_priority=["KP", "PARASHARI"],
        keywords=["travel", "journey", "trip", "flight", "short travel", "pilgrimage travel", "business trip", "3rd house", "9th house"]
    ),
    58: OntologyNode(
        node_id=58,
        title="Lifestyle / Material Comfort",
        category="MATERIAL_LIFE",
        subnodes={
            "58.1": "Luxury", "58.2": "Comfort", "58.3": "Vehicles", "58.4": "Home quality",
            "58.5": "Clothing/style symbolism", "58.6": "Food", "58.7": "Entertainment",
            "58.8": "Travel lifestyle", "58.9": "Social lifestyle", "58.10": "Consumption",
            "58.11": "Materialism", "58.12": "Simplicity", "58.13": "Financial freedom"
        },
        primary_houses=[4, 2, 11, 12],
        secondary_houses=[1, 9],
        primary_karakas=["Venus", "Moon", "Jupiter"],
        primary_vargas=["D16", "D4", "D2"],
        jaimini_factors=["A4", "A11", "Shodashamsha"],
        kp_significators=[4, 11, 2],
        timing_methods=["Vimshottari Dasha"],
        system_priority=["PARASHARI", "JAIMINI"],
        keywords=["luxury", "comfort", "lifestyle", "vehicles", "wealth comfort", "materialism", "4th house", "16th varga", "d16"]
    ),
    59: OntologyNode(
        node_id=59,
        title="Legacy / Long-Term Impact",
        category="LIFE_SELF",
        subnodes={
            "59.1": "Legacy", "59.2": "Reputation after life", "59.3": "Family legacy", "59.4": "Business legacy",
            "59.5": "Wealth inheritance", "59.6": "Children as legacy", "59.7": "Public contribution",
            "59.8": "Intellectual legacy", "59.9": "Institutional legacy", "59.10": "Spiritual legacy",
            "59.11": "Social impact"
        },
        primary_houses=[9, 10, 5, 8, 12],
        secondary_houses=[1, 2, 11],
        primary_karakas=["Sun", "Jupiter", "Saturn"],
        primary_vargas=["D9", "D10", "D60"],
        jaimini_factors=["AK", "AmK", "AL"],
        kp_significators=[9, 10, 5],
        timing_methods=["Vimshottari Dasha", "Narayana Dasha"],
        system_priority=["JAIMINI", "PARASHARI"],
        keywords=["legacy", "impact", "long-term impact", "inheritance", "after life", "institution", "contribution"]
    ),
    60: OntologyNode(
        node_id=60,
        title="Age / Phase / Period Questions",
        category="DYNAMIC_TIMING",
        subnodes={
            "60.1": "At what age?", "60.2": "Which Mahādaśā?", "60.3": "Which Antardaśā?",
            "60.4": "Which Chara Daśā?", "60.5": "Which KP period?", "60.6": "Which transit?",
            "60.7": "How long?", "60.8": "What triggers it?", "60.9": "When does it peak?",
            "60.10": "When does it decline?"
        },
        primary_houses=[1, 10, 7, 5, 2, 11],
        primary_karakas=["Saturn", "Jupiter", "Mars"],
        timing_methods=["Vimshottari Dasha", "Chara Dasha", "Double Transit", "Kakshya"],
        system_priority=["KP", "TAJAKA", "PARASHARI", "JAIMINI"],
        special_engines=["forward_timing_scanner", "dasha_engine"],
        keywords=["at what age", "which year", "which mahadasha", "how long will it last", "when will it peak"]
    ),
    61: OntologyNode(
        node_id=61,
        title="“What Happens If…” Scenarios",
        category="DECISION_SUPPORT",
        subnodes={
            "61.1": "If I start a business", "61.2": "If I stay employed", "61.3": "If I move abroad",
            "61.4": "If I stay home", "61.5": "If I marry this person", "61.6": "If I delay marriage",
            "61.7": "If I change career", "61.8": "If I take this job", "61.9": "If I invest",
            "61.10": "If I start a partnership", "61.11": "If I work alone", "61.12": "If I enter public life",
            "61.13": "If I pursue education", "61.14": "If I relocate", "61.15": "If I launch now vs later"
        },
        primary_houses=[1, 10, 7, 6, 12, 4, 5, 11],
        primary_karakas=["Mercury", "Jupiter", "Sun", "Saturn"],
        timing_methods=["Comparative Scenario Evaluation", "Prashna", "KP Sub-Lord"],
        system_priority=["KP", "PARASHARI", "JAIMINI"],
        keywords=["what happens if", "if i start", "if i move", "if i stay", "scenario", "comparative"]
    ),
    62: OntologyNode(
        node_id=62,
        title="“Why Is This Happening?” Questions",
        category="ROOT_CAUSE",
        subnodes={
            "62.1": "Why career is blocked", "62.2": "Why money is unstable", "62.3": "Why relationships fail",
            "62.4": "Why marriage is delayed", "62.5": "Why business fails", "62.6": "Why opportunities disappear",
            "62.7": "Why family conflict repeats", "62.8": "Why relocation keeps happening",
            "62.9": "Why people betray/leave", "62.10": "Why success comes late", "62.11": "Why wealth doesn't accumulate",
            "62.12": "Why career changed suddenly", "62.13": "Why spiritual interest increased",
            "62.14": "Why life changed during a specific period"
        },
        primary_houses=[6, 8, 12, 10, 7, 2, 4],
        primary_karakas=["Saturn", "Rahu", "Ketu", "Mars"],
        primary_vargas=["D1", "D9", "D30", "D60"],
        jaimini_factors=["GK", "A8", "A6", "Badhakas"],
        timing_methods=["Affliction Root Diagnosis", "Sade Sati", "Dusthana Lords", "Lajjitadi Avasthas"],
        system_priority=["PARASHARI", "JAIMINI", "NADI"],
        special_engines=["dosha_engine", "advanced_avasthas", "sensitive_points"],
        keywords=["why is this happening", "why am i stuck", "why delayed", "why blocked", "root cause", "curse", "dosha"]
    ),
    63: OntologyNode(
        node_id=63,
        title="“What Should I Optimize?” Questions",
        category="OPTIMIZATION",
        subnodes={
            "63.1": "Career", "63.2": "Money", "63.3": "Network", "63.4": "Marriage", "63.5": "Education",
            "63.6": "Business", "63.7": "Location", "63.8": "Timing", "63.9": "Spiritual practice",
            "63.10": "Lifestyle", "63.11": "Leadership", "63.12": "Communication", "63.13": "Risk management",
            "63.14": "Saving", "63.15": "Relationship behavior"
        },
        primary_houses=[1, 10, 11, 2, 9],
        primary_karakas=["Jupiter", "Sun", "Mercury", "Mars"],
        timing_methods=["High-Leverage Functional Benefics", "Yogakaraka Activation"],
        system_priority=["PARASHARI", "JAIMINI"],
        keywords=["what should i optimize", "how to maximize", "highest leverage", "optimization", "where to focus"]
    ),
    64: OntologyNode(
        node_id=64,
        title="“What Should I Avoid?” Questions",
        category="OPTIMIZATION",
        subnodes={
            "64.1": "Career traps", "64.2": "Financial traps", "64.3": "Business traps", "64.4": "Partnership traps",
            "64.5": "Relationship traps", "64.6": "Toxic networks", "64.7": "Bad investments",
            "64.8": "Bad timing", "64.9": "Unfavorable locations", "64.10": "Excessive risk",
            "64.11": "Overexpansion", "64.12": "Debt", "64.13": "Conflict", "64.14": "Reputation risks"
        },
        primary_houses=[6, 8, 12, 7, 2],
        primary_karakas=["Rahu", "Saturn", "Mars", "Ketu"],
        timing_methods=["Dusthana Risk Gates", "Maraka & Badhaka Vulnerability Windows"],
        system_priority=["PARASHARI", "KP", "JAIMINI"],
        keywords=["what should i avoid", "traps", "bad investments", "risks", "dangers", "pitfalls", "warnings"]
    ),
    65: OntologyNode(
        node_id=65,
        title="Special Event Prediction",
        category="EVENTS",
        subnodes={
            "65.1": "Job offer", "65.2": "Promotion", "65.3": "Business launch", "65.4": "Client acquisition",
            "65.5": "Major contract", "65.6": "Marriage proposal", "65.7": "Engagement", "65.8": "Marriage",
            "65.9": "Pregnancy", "65.10": "Childbirth", "65.11": "Property purchase", "65.12": "Property sale",
            "65.13": "Migration", "65.14": "Visa", "65.15": "University admission", "65.16": "Exam result",
            "65.17": "Lawsuit", "65.18": "Financial gain", "65.19": "Financial loss", "65.20": "Recognition",
            "65.21": "Public event", "65.22": "Major trip", "65.23": "Career change"
        },
        primary_houses=[10, 11, 7, 2, 5, 4, 12, 9, 6, 8],
        primary_karakas=["Jupiter", "Saturn", "Mercury", "Sun", "Venus", "Mars"],
        primary_vargas=["D10", "D9", "D7", "D4", "D2", "D24"],
        kp_significators=[10, 11, 7, 2, 5, 4, 9, 12],
        timing_methods=["Vimshottari D-A-P Triad", "Double Transit", "KP Sub-Lord", "Kakshya"],
        system_priority=["KP", "TAJAKA", "PARASHARI", "JAIMINI"],
        special_engines=["forward_timing_scanner", "kp_engine"],
        keywords=["predict event", "special event", "when will i get job offer", "when will i get promoted", "when will i buy house"]
    ),
    66: OntologyNode(
        node_id=66,
        title="Event Backtesting",
        category="CALIBRATION",
        subnodes={
            "66.1": "Past marriage timing", "66.2": "Past job timing", "66.3": "Past promotion",
            "66.4": "Past relocation", "66.5": "Past exam result", "66.6": "Past financial event",
            "66.7": "Past relationship event", "66.8": "Past childbirth", "66.9": "Past property acquisition",
            "66.10": "Past major crisis"
        },
        primary_houses=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        primary_karakas=["Jupiter", "Saturn", "Sun", "Venus", "Mars", "Mercury"],
        timing_methods=["Retrodictive Vimshottari Verification", "Past Transit Reconstruction", "Rectification Anchor"],
        system_priority=["KP", "PARASHARI", "JAIMINI"],
        special_engines=["rectification_engine", "dual_track_benchmarks"],
        keywords=["backtest", "past event", "verify timeline", "check accuracy with past", "rectification", "historical events"]
    ),
    67: OntologyNode(
        node_id=67,
        title="Prediction Quality Control",
        category="CALIBRATION",
        subnodes={
            "67.1": "Natal promise", "67.2": "Dasha activation", "67.3": "Transit activation",
            "67.4": "KP confirmation", "67.5": "Jaimini confirmation", "67.6": "Vargas confirmation",
            "67.7": "Repetition of indication", "67.8": "Contradiction count", "67.9": "Timing convergence",
            "67.10": "Confidence score", "67.11": "Alternative interpretation", "67.12": "Failure conditions",
            "67.13": "What would falsify the prediction", "67.14": "Precision limit", "67.15": "Unknowns"
        },
        primary_houses=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        timing_methods=["Bayesian Gate Check", "Negative Control Verification", "Falsification Testing"],
        system_priority=["PARASHARI", "JAIMINI", "KP", "NADI", "TAJAKA"],
        special_engines=["convergence_engine", "tradition_arbiter", "uncertainty_engine"],
        keywords=["quality control", "confidence score", "falsification", "contradiction check", "accuracy check", "reliability"]
    ),
    68: OntologyNode(
        node_id=68,
        title="The Really Important Cross-Domain Questions",
        category="CROSS_DOMAIN",
        subnodes={
            "68.1": "Career → marriage", "68.2": "Marriage → career", "68.3": "Marriage → wealth",
            "68.4": "Spouse → wealth", "68.5": "Spouse → status", "68.6": "Business → marriage",
            "68.7": "Network → business", "68.8": "Network → wealth", "68.9": "Foreign relocation → career",
            "68.10": "Foreign relocation → marriage", "68.11": "Education → career", "68.12": "Education → wealth",
            "68.13": "Children → career", "68.14": "Children → wealth", "68.15": "Family → wealth",
            "68.16": "Family → career", "68.17": "Property → wealth", "68.18": "Property → family",
            "68.19": "Spirituality → life direction", "68.20": "Career → purpose", "68.21": "Wealth → social status",
            "68.22": "Status → network", "68.23": "Network → spouse", "68.24": "Spouse → foreign relocation",
            "68.25": "Business partner → wealth", "68.26": "Investor → business", "68.27": "Mentor → career",
            "68.28": "Institution → career", "68.29": "Reputation → business", "68.30": "Crisis → transformation"
        },
        primary_houses=[10, 7, 2, 11, 9, 12, 4, 5, 8],
        primary_karakas=["Sun", "Venus", "Jupiter", "Mercury", "Saturn", "Rahu"],
        primary_vargas=["D10", "D9", "D2", "D4", "D7", "D24"],
        jaimini_factors=["AK", "AmK", "DK", "AL", "UL", "A10", "A11"],
        kp_significators=[2, 7, 10, 11, 9, 12],
        timing_methods=["Vimshottari Dasha", "Double Transit", "KP Sub-Lord"],
        system_priority=["PARASHARI", "JAIMINI", "KP"],
        keywords=["career to marriage", "marriage to wealth", "network to business", "foreign relocation to career", "cross-domain"]
    ),
    69: OntologyNode(
        node_id=69,
        title="Astrological System Router",
        category="ROUTING",
        subnodes={
            "69.1": "Parāśari", "69.2": "Jaimini", "69.3": "KP", "69.4": "Transits", "69.5": "Vargas"
        },
        primary_houses=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        system_priority=["PARASHARI", "JAIMINI", "KP", "NADI", "TAJAKA"],
        special_engines=["methodology_router", "tradition_arbiter"],
        keywords=["system router", "parashari", "jaimini", "kp", "transits", "vargas"]
    ),
    70: OntologyNode(
        node_id=70,
        title="Question Types Your AI Should Recognize",
        category="QUERY_MODES",
        subnodes=QUERY_MODES,
        primary_houses=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
        system_priority=["PARASHARI", "JAIMINI", "KP"],
        keywords=["what", "why", "how", "when", "where", "who", "whether", "how much", "how strong", "how long", "confidence"]
    )
}

class JyotishaOntology:
    """
    Master engine for routing questions to the 70-node Jyotiṣa Decision & Interpretation Ontology.
    """

    @classmethod
    def get_node(cls, node_id: int) -> Optional[OntologyNode]:
        return MASTER_ONTOLOGY_NODES.get(node_id)

    @classmethod
    def list_all_nodes(cls) -> List[Dict[str, Any]]:
        return [node.to_dict() for node in MASTER_ONTOLOGY_NODES.values()]

    @classmethod
    def detect_query_mode(cls, query: str) -> Tuple[str, str]:
        """Detect the Query Mode (Node 70: 70.1 to 70.24) from question text."""
        q = query.lower().strip()
        
        # High-specificity action & intent modes first
        if re.search(r'\b(avoid|trap|traps|pitfall|pitfalls|risk|risks|danger|dangers|warning|warnings)\b', q):
            return "70.15", "What should I avoid"
        if re.search(r'\b(optimize|pursue|focus on|maximize|best move|highest leverage)\b', q):
            return "70.16", "What should I pursue"
        if re.search(r'\b(confidence|how sure|accuracy|falsify|contradict)\b', q):
            return "70.23", "How confident are you"
        if re.search(r'\b(when|timing|which year|which month|how soon|what date|what time|at what age)\b', q):
            return "70.4", "When"
        if re.search(r'\b(why|what causes|reason for|why is|why am)\b', q):
            return "70.2", "Why"
        if re.search(r'\b(how to|how can|how should|mechanism)\b', q):
            return "70.3", "How"
        if re.search(r'\b(where|which city|which country|location|place)\b', q):
            return "70.5", "Where"
        if re.search(r'\b(who is|with whom|who will|which person)\b', q):
            return "70.6", "Who"
        if re.search(r'\b(how much|how many|quantity|ceiling)\b', q):
            return "70.9", "How much"
        if re.search(r'\b(how strong|strength|potency|magnitude)\b', q):
            return "70.10", "How strong"
        if re.search(r'\b(how long|duration|span|how many years)\b', q):
            return "70.11", "How long"
        if re.search(r'\b(whether|will i|should i|is it possible|is there)\b', q):
            return "70.8", "Whether"
            
        return "70.1", "What"

    @classmethod
    def detect_cross_domain(cls, query: str) -> List[str]:
        """Detect cross-domain vector links from Node 68."""
        q = query.lower().strip()
        detected = []
        
        # Check specific cross-domain pairings
        if ("network" in q or "client" in q or "referral" in q) and ("business" in q or "agency" in q or "startup" in q):
            detected.append("68.7: Network → Business")
        if ("network" in q or "connections" in q) and ("wealth" in q or "money" in q or "rich" in q):
            detected.append("68.8: Network → Wealth")
        if ("foreign" in q or "abroad" in q or "relocation" in q or "international" in q) and ("career" in q or "job" in q or "work" in q):
            detected.append("68.9: Foreign Relocation → Career")
        if ("foreign" in q or "abroad" in q) and ("marriage" in q or "spouse" in q or "wife" in q or "husband" in q):
            detected.append("68.10: Foreign Relocation → Marriage")
        if ("career" in q or "job" in q) and ("marriage" in q or "spouse" in q):
            detected.append("68.1: Career → Marriage")
        if ("marriage" in q or "spouse" in q) and ("wealth" in q or "money" in q or "rich" in q):
            detected.append("68.3: Marriage → Wealth")
        if ("education" in q or "degree" in q or "study" in q) and ("career" in q or "job" in q):
            detected.append("68.11: Education → Career")
        if ("education" in q or "degree" in q) and ("wealth" in q or "money" in q):
            detected.append("68.12: Education → Wealth")
        if ("property" in q or "real estate" in q or "land" in q) and ("wealth" in q or "money" in q):
            detected.append("68.17: Property → Wealth")
        if ("spirituality" in q or "dharma" in q or "moksha" in q) and ("purpose" in q or "direction" in q):
            detected.append("68.19: Spirituality → Life Direction")
            
        return detected

    @classmethod
    def classify_question(cls, query: str) -> OntologyRoutingResult:
        """
        Classifies an inquiry across the 70-node ontology and maps exact astrological requirements.
        """
        q = query.lower().strip()
        mode_id, mode_name = cls.detect_query_mode(query)
        cross_links = cls.detect_cross_domain(query)
        
        best_node_id = 1
        best_subnode_id = "1.1"
        best_subnode_title = "Core personality"
        
        # High-specificity pattern matching rules
        if re.search(r'\b(prashna|horary|will i get the job|will i get the client|will payment arrive|will lawsuit succeed|will lost object)\b', q):
            best_node_id = 37
            best_subnode_id = "37.1"
            best_subnode_title = "Prashna Focused Question"
        elif re.search(r'\b(muhurta|auspicious time|best date to launch|launch date|signing date|griha pravesh|election)\b', q):
            best_node_id = 38
            best_subnode_id = "38.1"
            best_subnode_title = "Muhūrta Business/Event Timing"
        elif re.search(r'\b(panchang|tithi|rahu kalam|abhijit|choghadiya|karana|nakshatra today)\b', q):
            best_node_id = 39
            best_subnode_id = "39.1"
            best_subnode_title = "Panchāṅga Engine"
        elif re.search(r'\b(gemstone|ratna|ruby|emerald|sapphire|pearl|diamond|ring finger|anukool)\b', q):
            best_node_id = 45
            best_subnode_id = "45.1"
            best_subnode_title = "Suitable gemstone / Ratna"
        elif re.search(r'\b(remedy|mantra|japa|puja|homa|charity|dana|upaya|lal kitab)\b', q):
            best_node_id = 44
            best_subnode_id = "44.1"
            best_subnode_title = "Remedies & Mantras"
        elif re.search(r'\b(vastu|entrance|bedroom direction|sleep direction|office layout|study desk|cash area)\b', q):
            best_node_id = 46
            best_subnode_id = "46.1"
            best_subnode_title = "Vāstu Spatial Alignment"
        elif re.search(r'\b(ashtakoota|synastry|compatibility|guna milan|partner match|cofounder compatibility)\b', q):
            best_node_id = 40
            best_subnode_id = "40.1"
            best_subnode_title = "Marriage/Entity Compatibility"
        elif re.search(r'\b(longevity|ayurdaya|lifespan|maraka|badhaka|accident|22nd drekkana|64th navamsha)\b', q):
            best_node_id = 24
            best_subnode_id = "24.1"
            best_subnode_title = "Longevity & Ayurdaya Assessment"
        elif re.search(r'\b(health|disease|illness|surgery|vitality|constitution|hospital|medical|tridosha)\b', q):
            best_node_id = 23
            best_subnode_id = "23.1"
            best_subnode_title = "Health & Wellbeing"
        elif re.search(r'\b(agency|saas|startup|business|entrepreneur|client|revenue|b2b|retainer|e-commerce|trading|ecommerce)\b', q):
            best_node_id = 5
            best_subnode_id = "5.22" if "agency" in q else ("5.23" if "saas" in q else "5.1")
            best_subnode_title = "Agency / Software Business / Commercial Potential"
        elif re.search(r'\b(foreign|abroad|overseas|visa|relocation|relocate|immigration|migration|international)\b', q):
            best_node_id = 20
            best_subnode_id = "20.5" if "settlement" in q or "permanent" in q else "20.1"
            best_subnode_title = "Foreign Travel / International Life / Relocation"
        elif re.search(r'\b(spouse|wife|husband|partner profile|future wife|future husband|who will i marry)\b', q):
            best_node_id = 10
            best_subnode_id = "10.1"
            best_subnode_title = "Spouse Profile & Persona"
        elif re.search(r'\b(marriage|wedding|marry|married|divorce|separation|second marriage)\b', q):
            best_node_id = 9
            best_subnode_id = "9.3" if "when" in q else "9.1"
            best_subnode_title = "Marriage Promise & Timing"
        elif re.search(r'\b(love|romance|dating|relationship|crush|breakup|infatuation)\b', q):
            best_node_id = 11
            best_subnode_id = "11.1"
            best_subnode_title = "Love & Romance"
        elif re.search(r'\b(children|child|kid|pregnancy|progeny|son|daughter|childbirth|ivf)\b', q):
            best_node_id = 12
            best_subnode_id = "12.1"
            best_subnode_title = "Children & Progeny"
        elif re.search(r'\b(property|real estate|house|flat|apartment|land|plot|buy property|vehicle|car)\b', q):
            best_node_id = 8
            best_subnode_id = "8.1"
            best_subnode_title = "Property, Real Estate & Vehicles"
        elif re.search(r'\b(invest|investing|speculation|stocks|crypto|shares|trading|equity)\b', q):
            best_node_id = 7
            best_subnode_id = "7.4" if "trading" in q else "7.1"
            best_subnode_title = "Investments & Speculation"
        elif re.search(r'\b(money|wealth|finance|rich|savings|debt|loan|net worth|income|salary|dhana)\b', q):
            best_node_id = 6
            best_subnode_id = "6.9"
            best_subnode_title = "Money, Wealth & Net-Worth Trajectory"
        elif re.search(r'\b(job|employment|boss|coworker|salary|switch job|layoff|promotion|corporate)\b', q):
            best_node_id = 4
            best_subnode_id = "4.21" if "promotion" in q else "4.1"
            best_subnode_title = "Job, Employment & Promotion"
        elif re.search(r'\b(career|profession|vocation|occupation|work|livelihood)\b', q):
            best_node_id = 3
            best_subnode_id = "3.1"
            best_subnode_title = "Career Direction & Vocation"
        elif re.search(r'\b(education|university|college|school|exam|studies|degree|scholarship)\b', q):
            best_node_id = 18
            best_subnode_id = "18.3"
            best_subnode_title = "Higher Education & Academic Milestones"
        elif re.search(r'\b(lawsuit|court|litigation|dispute|legal|settlement|case)\b', q):
            best_node_id = 28
            best_subnode_id = "28.3"
            best_subnode_title = "Legal, Litigation & Dispute Outcomes"
        elif re.search(r'\b(spirituality|spiritual|moksha|meditation|guru|mantra|dharma)\b', q):
            best_node_id = 25
            best_subnode_id = "25.1"
            best_subnode_title = "Spirituality, Dharma & Moksha"
        elif re.search(r'\b(fame|reputation|celebrity|personal brand|recognition|public image)\b', q):
            best_node_id = 17
            best_subnode_id = "17.1"
            best_subnode_title = "Public Image, Fame & Personal Brand"
        elif re.search(r'\b(avoid|trap|pitfall|mistake|risk)\b', q):
            best_node_id = 64
            best_subnode_id = "64.1"
            best_subnode_title = "Astrological Traps to Avoid"
        elif re.search(r'\b(optimize|leverage|maximize|focus)\b', q):
            best_node_id = 63
            best_subnode_id = "63.1"
            best_subnode_title = "High-Leverage Astrological Optimization"
        elif re.search(r'\b(why is|why am|why blocked|why stuck|why delayed)\b', q):
            best_node_id = 62
            best_subnode_id = "62.1"
            best_subnode_title = "Root Cause Diagnostic"
        elif re.search(r'\b(if i|what happens if|scenario)\b', q):
            best_node_id = 61
            best_subnode_id = "61.1"
            best_subnode_title = "Scenario Comparison"
        elif re.search(r'\b(purpose|life purpose|calling|meaning|mission)\b', q):
            best_node_id = 2
            best_subnode_id = "2.1"
            best_subnode_title = "Life Purpose & Dharma"
        else:
            best_node_id = 1
            best_subnode_id = "1.1"
            best_subnode_title = "Self / Personality / Core Operating System"

        node = MASTER_ONTOLOGY_NODES.get(best_node_id, MASTER_ONTOLOGY_NODES[1])
        
        # Build falsification checks (Node 67)
        falsification = [
            f"Gate 1 (Natal Promise): Evaluated across houses {node.primary_houses} and karakas {node.primary_karakas}",
            f"Gate 2 (Daśā Authorization): Confirmed via active Mahadasha/Antardasha lords",
            f"Gate 3 (Transit Trigger): Double Transit (Saturn+Jupiter) + Kakshya Bindu defense evaluated",
            f"Gate 4 (Cross-Tradition Check): Priority order {node.system_priority}"
        ]

        return OntologyRoutingResult(
            node_id=node.node_id,
            node_title=node.title,
            subnode_id=best_subnode_id,
            subnode_title=best_subnode_title,
            category=node.category,
            query_mode_id=mode_id,
            query_mode=mode_name,
            primary_houses=node.primary_houses,
            secondary_houses=node.secondary_houses,
            primary_karakas=node.primary_karakas,
            primary_vargas=node.primary_vargas,
            secondary_vargas=node.secondary_vargas,
            jaimini_factors=node.jaimini_factors,
            kp_significators=node.kp_significators,
            timing_methods=node.timing_methods,
            system_priority=node.system_priority,
            special_engines=node.special_engines,
            cross_domain_links=cross_links,
            falsification_checks=falsification
        )
