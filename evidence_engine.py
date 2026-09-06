"""
Structured Evidence & Classical Assertion Engine
Aggregates deterministic findings across:
1. Planetary Dignity, House Placements & Special Aspects
2. Full 5-Point Neecha Bhanga & Vipareeta Raja Yogas
3. Sensitive Vulnerabilities (64th Navamsha, 22nd Drekkana, Mrityu Bhaga, Gandanta)
4. Fortune Anchors (Pushkara Navamsha/Bhagas, Indu Lagna, Bhrigu Bindu)
5. Upagraha Afflictions (Gulika & Mandi)
Normalizes everything into signed assertions (supporting/contradicting/modifier) with strict confidence weights.
"""

import json
from enum import Enum
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from vedic_models import Chart, Planet
from sensitive_points import SensitivePointsEngine
from upagrahas import UpagrahaEngine
from cancellations import CancellationEngine
from text_utils import ordinal

class EvidenceStrength(Enum):
    VERY_STRONG = 5
    STRONG = 4
    MODERATE = 3
    WEAK = 2
    VERY_WEAK = 1

@dataclass
class Evidence:
    id: str
    domain: str
    polarity: str  # 'supporting', 'contradicting', or 'modifier'
    source_rule: str
    subject: str  # e.g. 'Sun', '10th House', '64th Navamsha'
    strength: EvidenceStrength
    reason: str
    timing_relevance: bool = False

    def to_dict(self):
        return {
            "id": self.id,
            "domain": self.domain,
            "polarity": self.polarity,
            "source_rule": self.source_rule,
            "subject": self.subject,
            "strength": self.strength.name,
            "reason": self.reason,
            "timing_relevance": self.timing_relevance
        }

@dataclass
class Contradiction:
    domain: str
    subject: str
    positive_evidence: List[Evidence]
    negative_evidence: List[Evidence]
    resolution_summary: str

    def to_dict(self):
        return {
            "domain": self.domain,
            "subject": self.subject,
            "positive_evidence": [e.to_dict() for e in self.positive_evidence],
            "negative_evidence": [e.to_dict() for e in self.negative_evidence],
            "resolution_summary": self.resolution_summary
        }

class RuleGenerators:
    @staticmethod
    def eval_dignity(chart: Chart, domain: str, planet_name: str) -> List[Evidence]:
        evidence_list = []
        planet = next((p for p in chart.planets.values() if p.name == planet_name), None)
        if not planet:
            return []

        if "Exalted" in planet.dignity or "Moolatrikona" in planet.dignity or "Own House" in planet.dignity:
            evidence_list.append(Evidence(
                id=f"{planet_name.lower()}_strong_dignity",
                domain=domain,
                polarity="supporting",
                source_rule="dignity",
                subject=planet_name,
                strength=EvidenceStrength.VERY_STRONG if "Exalted" in planet.dignity else EvidenceStrength.STRONG,
                reason=f"{planet_name} has high dignity ({planet.dignity})."
            ))
        elif "Debilitated" in planet.dignity:
            evidence_list.append(Evidence(
                id=f"{planet_name.lower()}_debilitated",
                domain=domain,
                polarity="contradicting",
                source_rule="dignity",
                subject=planet_name,
                strength=EvidenceStrength.STRONG,
                reason=f"{planet_name} is debilitated, indicating inherent structural weakness."
            ))
        return evidence_list

    @staticmethod
    def eval_house_lord_placement(chart: Chart, domain: str, house_num: int) -> List[Evidence]:
        evidence_list = []
        lord = next((p for p in chart.planets.values() if house_num in p.owns_houses), None)
        if not lord:
            return []

        if lord.house in [1, 4, 5, 7, 9, 10]:
            evidence_list.append(Evidence(
                id=f"lord_of_{house_num}_in_{lord.house}",
                domain=domain,
                polarity="supporting",
                source_rule="house_lordship",
                subject=f"Lord of {house_num}",
                strength=EvidenceStrength.STRONG,
                reason=f"The lord of the {ordinal(house_num)} house ({lord.name}) is placed well in Kendra/Trikona (House {lord.house})."
            ))
        elif lord.house in [6, 8, 12]:
            evidence_list.append(Evidence(
                id=f"lord_of_{house_num}_in_{lord.house}",
                domain=domain,
                polarity="contradicting",
                source_rule="house_lordship",
                subject=f"Lord of {house_num}",
                strength=EvidenceStrength.STRONG,
                reason=f"The lord of the {ordinal(house_num)} house ({lord.name}) is placed in a difficult Dusthana house ({lord.house})."
            ))
        return evidence_list

    @staticmethod
    def eval_house_aspects(chart: Chart, domain: str, house_num: int) -> List[Evidence]:
        evidence_list = []
        for planet in chart.planets.values():
            if house_num in planet.aspects_houses:
                if planet.name in ["Jupiter", "Venus"]:
                    evidence_list.append(Evidence(
                        id=f"{planet.name.lower()}_aspects_{house_num}",
                        domain=domain,
                        polarity="supporting",
                        source_rule="graha_drishti",
                        subject=f"House {house_num}",
                        strength=EvidenceStrength.STRONG if planet.name == "Jupiter" else EvidenceStrength.MODERATE,
                        reason=f"Benefic {planet.name} casts auspicious aspect on the {ordinal(house_num)} house."
                    ))
                elif planet.name in ["Saturn", "Mars", "Rahu", "Ketu"]:
                    # UPACHAYA RULE (classical Parashari): malefics GROW STRONGER and
                    # give constructive results in the houses of growth — 3 (effort/
                    # courage), 6 (defeating competition), 10 (career/karma), 11
                    # (gains). A malefic aspect on an Upachaya is a PLUS for those
                    # significations, not "friction". Only non-Upachaya houses take
                    # the affliction reading. This corrects the "Literal Malefic
                    # Over-weighting" failure that flooded every chart with false
                    # contradictions and mislabeled net-positive charts as MIXED.
                    if house_num in (3, 6, 10, 11):
                        evidence_list.append(Evidence(
                            id=f"{planet.name.lower()}_aspects_{house_num}",
                            domain=domain,
                            polarity="supporting",
                            source_rule="graha_drishti",
                            subject=f"House {house_num}",
                            strength=EvidenceStrength.MODERATE,
                            reason=f"Malefic {planet.name} aspects the {ordinal(house_num)} house (Upachaya), fueling drive, competitive edge and growth in this domain."
                        ))
                    else:
                        evidence_list.append(Evidence(
                            id=f"{planet.name.lower()}_aspects_{house_num}",
                            domain=domain,
                            polarity="contradicting",
                            source_rule="graha_drishti",
                            subject=f"House {house_num}",
                            strength=EvidenceStrength.MODERATE,
                            reason=f"Malefic {planet.name} aspects the {ordinal(house_num)} house, causing friction or delay."
                        ))
        return evidence_list

    @staticmethod
    def eval_condition_and_strength(chart: Chart, domain: str, planet_name: str) -> List[Evidence]:
        evidence_list = []
        planet = next((p for p in chart.planets.values() if p.name == planet_name), None)
        if not planet:
            return []

        # Combustion
        if planet.combustion.get("status"):
            evidence_list.append(Evidence(
                id=f"{planet_name.lower()}_combust",
                domain=domain,
                polarity="contradicting",
                source_rule="combustion",
                subject=planet_name,
                strength=EvidenceStrength.STRONG,
                reason=f"{planet_name} is Combust (Astangata) by Sun, weakening outward manifestation."
            ))

        # Dig Bala
        dig_bala = planet.shadbala.get("dig_bala", 0)
        if dig_bala >= 50:
            evidence_list.append(Evidence(
                id=f"{planet_name.lower()}_high_dig_bala",
                domain=domain,
                polarity="supporting",
                source_rule="shadbala",
                subject=planet_name,
                strength=EvidenceStrength.STRONG,
                reason=f"{planet_name} possesses powerful Directional Strength (Dig Bala: {dig_bala})."
            ))
        elif dig_bala <= 10:
            evidence_list.append(Evidence(
                id=f"{planet_name.lower()}_low_dig_bala",
                domain=domain,
                polarity="contradicting",
                source_rule="shadbala",
                subject=planet_name,
                strength=EvidenceStrength.MODERATE,
                reason=f"{planet_name} lacks Directional Strength (Dig Bala: {dig_bala})."
            ))

        return evidence_list

class EvidenceAggregator:
    def __init__(self, chart: Chart):
        self.chart = chart
        self.sensitive_engine = SensitivePointsEngine(chart)
        self.cancellation_engine = CancellationEngine(chart)
        self.upagraha_engine = UpagrahaEngine(chart)

    def get_domain_config(self, domain: str):
        configs = {
            "career": {"houses": [10, 2, 6, 11], "karakas": ["Saturn", "Sun", "Mercury", "Jupiter"]},
            "marriage": {"houses": [7, 2, 11], "karakas": ["Venus", "Jupiter"]},
            "health": {"houses": [1, 6, 8, 12], "karakas": ["Sun", "Mars", "Saturn"]},
            "wealth": {"houses": [2, 11, 5, 9, 1], "karakas": ["Jupiter", "Mercury", "Venus"]},
            "relocation": {"houses": [4, 9, 12, 3], "karakas": ["Moon", "Rahu"]},
            "litigation": {"houses": [6, 8, 12], "karakas": ["Mars", "Saturn", "Rahu"]},
            "spirituality": {"houses": [9, 12, 8, 5], "karakas": ["Jupiter", "Ketu"]}
        }
        return configs.get(domain, configs["career"])

    def gather_evidence(self, domain: str) -> Dict[str, Any]:
        domain = domain.lower()
        config = self.get_domain_config(domain)

        all_evidence: List[Evidence] = []

        # 1. House placements & aspects
        for house in config["houses"]:
            all_evidence.extend(RuleGenerators.eval_house_lord_placement(self.chart, domain, house))
            all_evidence.extend(RuleGenerators.eval_house_aspects(self.chart, domain, house))

        # 2. Planetary dignities & strengths
        for karaka in config["karakas"]:
            all_evidence.extend(RuleGenerators.eval_dignity(self.chart, domain, karaka))
            all_evidence.extend(RuleGenerators.eval_condition_and_strength(self.chart, domain, karaka))

        # 3. Sensitive Points & Pushkaras
        sp_data = self.sensitive_engine.calculate_all()
        for mb in sp_data.get("mrityu_bhagas", []):
            if mb["entity"] in config["karakas"] or mb["entity"] == "Ascendant":
                all_evidence.append(Evidence(
                    id=f"{mb['entity'].lower()}_mrityu_bhaga",
                    domain=domain,
                    polarity="contradicting",
                    source_rule="mrityu_bhaga",
                    subject=mb["entity"],
                    strength=EvidenceStrength.VERY_STRONG,
                    reason=f"{mb['entity']} sits on exact fatal degree Mrityu Bhaga ({mb['degree']}° {mb['sign']})."
                ))

        for gand in sp_data.get("gandanta_points", []):
            all_evidence.append(Evidence(
                id=f"{gand['entity'].lower()}_gandanta",
                domain=domain,
                polarity="contradicting",
                source_rule="gandanta",
                subject=gand["entity"],
                strength=EvidenceStrength.VERY_STRONG,
                reason=f"{gand['entity']} is entrapped in {gand['knot']} ({gand['type']})."
            ))

        for p_info in sp_data.get("pushkara_status", {}).get("planets", []):
            if p_info["planet"] in config["karakas"]:
                all_evidence.append(Evidence(
                    id=f"{p_info['planet'].lower()}_pushkara",
                    domain=domain,
                    polarity="supporting",
                    source_rule="pushkara",
                    subject=p_info["planet"],
                    strength=EvidenceStrength.VERY_STRONG,
                    reason=f"{p_info['planet']} occupies auspicious Pushkara zone ({p_info['sign']} {p_info['degree']}°)."
                ))

        # 4. Classical Cancellations (Neecha Bhanga & Vipareeta)
        cancellations = self.cancellation_engine.evaluate_all()
        for nb in cancellations.get("neecha_bhanga_raja_yogas", []):
            if nb["is_cancelled"]:
                all_evidence.append(Evidence(
                    id=f"{nb['planet'].lower()}_neecha_bhanga",
                    domain=domain,
                    polarity="modifier",
                    source_rule="cancellation_nbry",
                    subject=nb["planet"],
                    strength=EvidenceStrength.VERY_STRONG if nb["grade"] == "FULL_RAJA_YOGA" else EvidenceStrength.STRONG,
                    reason=f"Neecha Bhanga Raja Yoga confirmed for {nb['planet']}: {'; '.join(nb['conditions_met'])}"
                ))

        for vry in cancellations.get("vipareeta_raja_yogas", []):
            all_evidence.append(Evidence(
                id=f"vry_{vry['lord'].lower()}",
                domain=domain,
                polarity="supporting" if vry["is_pure"] else "modifier",
                source_rule="vipareeta_raja_yoga",
                subject=vry["lord"],
                strength=EvidenceStrength.STRONG if vry["is_pure"] else EvidenceStrength.MODERATE,
                reason=vry["description"]
            ))

        for yb in cancellations.get("yoga_bhangas", []):
            all_evidence.append(Evidence(
                id=f"yoga_bhanga_{yb['planet'].lower()}",
                domain=domain,
                polarity="contradicting",
                source_rule="yoga_bhanga",
                subject=yb["planet"],
                strength=EvidenceStrength.STRONG,
                reason=yb["detail"]
            ))

        # Separate polarities
        supporting = [e for e in all_evidence if e.polarity == "supporting"]
        contradicting = [e for e in all_evidence if e.polarity == "contradicting"]
        modifiers = [e for e in all_evidence if e.polarity == "modifier"]

        # Dynamic Contradictions
        contradictions = []
        subjects = set([e.subject for e in all_evidence])
        for subject in subjects:
            subj_sup = [e for e in supporting if e.subject == subject]
            subj_con = [e for e in contradicting if e.subject == subject]
            if subj_sup and subj_con:
                contradictions.append(Contradiction(
                    domain=domain,
                    subject=subject,
                    positive_evidence=subj_sup,
                    negative_evidence=subj_con,
                    resolution_summary=f"Contradictory factors on {subject}: Positive indications vs Negative tensions. Requires synthesis weighting."
                ))

        return {
            "supporting_evidence": [e.to_dict() for e in supporting],
            "contradicting_evidence": [e.to_dict() for e in contradicting],
            "modifiers_and_cancellations": [e.to_dict() for e in modifiers],
            "contradictions": [c.to_dict() for c in contradictions],
            "sensitive_points": sp_data,
            "missing_evidence": []
        }
