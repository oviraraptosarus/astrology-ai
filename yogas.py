"""
Comprehensive Classical Yogas Engine
Detects multi-planet combinations using strict Parashari conditions.
"""

from typing import List, Dict, Any, Optional
from rules_engine import Rule, RuleResult
from vedic_models import Chart, Planet
from text_utils import ordinal

ZODIAC = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

class Yoga(Rule):
    def __init__(self):
        super().__init__()
        self.domain = "general"
        self.polarity = "supporting"
        self.is_technically_present = False
        self.practical_significance = "MODERATE"

    def evaluate(self, chart: Chart, **kwargs) -> RuleResult:
        raise NotImplementedError("Yogas must implement evaluate()")

# --- Pancha Mahapurusha Yogas ---
class PanchaMahapurushaYoga(Yoga):
    def __init__(self, name: str, planet_name: str):
        super().__init__()
        self.name = name
        self.rule_id = f"yoga_{name.lower()}"
        self.planet_name = planet_name
        self.tradition = "Parashara"
        self.provenance = "Brihat Parashara Hora Sastra"

    def evaluate(self, chart: Chart, **kwargs) -> RuleResult:
        p = chart.planets.get(self.planet_name)
        if not p:
            return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=[f"{self.planet_name} not found"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason=f"{self.name} Yoga not present.")
            
        in_kendra = p.house in [1, 4, 7, 10]
        in_dignity = p.dignity in ["Exalted", "Moolatrikona", "Own House"]
        fired = in_kendra and in_dignity
        
        if not fired:
            return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["Not in Kendra or not in high dignity"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason=f"{self.name} Yoga not present.")
            
        return RuleResult(
            rule_id=self.rule_id, name=self.name, domain=self.domain, fired=True,
            polarity=self.polarity, evidence_used=[],
            conditions_satisfied=[f"{self.planet_name} in Kendra (House {p.house})", f"{self.planet_name} in {p.dignity}"],
            conditions_not_satisfied=[], exceptions_encountered=[], modifiers=[],
            provenance=self.provenance, confidence="STRONG",
            reason=f"{self.name} Yoga (Pancha Mahapurusha) formed by {self.planet_name} in Kendra (House {p.house}) and {p.dignity}."
        )

class RuchakaYoga(PanchaMahapurushaYoga):
    def __init__(self): super().__init__("Ruchaka", "Mars")

class BhadraYoga(PanchaMahapurushaYoga):
    def __init__(self): super().__init__("Bhadra", "Mercury")

class HamsaYoga(PanchaMahapurushaYoga):
    def __init__(self): super().__init__("Hamsa", "Jupiter")

class MalavyaYoga(PanchaMahapurushaYoga):
    def __init__(self): super().__init__("Malavya", "Venus")

class ShashaYoga(PanchaMahapurushaYoga):
    def __init__(self): super().__init__("Shasha", "Saturn")


# --- Core Canonical Yogas ---

class GajaKesariYoga(Yoga):
    def __init__(self):
        super().__init__()
        self.rule_id = "yoga_gajakesari"
        self.name = "Gajakesari"
        self.tradition = "Parashara"
        self.provenance = "Brihat Parashara Hora Sastra"

    def evaluate(self, chart: Chart, **kwargs) -> RuleResult:
        jup = chart.planets.get("Jupiter")
        moon = chart.planets.get("Moon")
        if not jup or not moon:
            return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["Jupiter or Moon missing"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Gajakesari Yoga not present.")
            
        diff = (jup.house - moon.house) % 12
        if diff in [0, 3, 6, 9]:
            return RuleResult(
                rule_id=self.rule_id, name=self.name, domain=self.domain, fired=True,
                polarity=self.polarity, evidence_used=[],
                conditions_satisfied=[f"Jupiter is in Kendra from Moon (House offset {diff+1})"],
                conditions_not_satisfied=[], exceptions_encountered=[], modifiers=[],
                provenance=self.provenance, confidence="STRONG",
                reason="Gajakesari Yoga is present. Imparts intellect, high reputation, and sustained success."
            )
        return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["Jupiter not in Kendra from Moon"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Gajakesari Yoga not present.")

class GajakesariYoga(GajaKesariYoga):
    pass

class BudhadityaYoga(Yoga):
    def __init__(self):
        super().__init__()
        self.rule_id = "yoga_budhaditya"
        self.name = "Budhaditya"
        self.tradition = "Parashara"
        self.provenance = "Brihat Parashara Hora Sastra"

    def evaluate(self, chart: Chart, **kwargs) -> RuleResult:
        sun = chart.planets.get("Sun")
        mer = chart.planets.get("Mercury")
        if not sun or not mer:
            return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["Sun or Mercury missing"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Budhaditya Yoga not present.")
            
        if sun.house == mer.house:
            return RuleResult(
                rule_id=self.rule_id, name=self.name, domain=self.domain, fired=True,
                polarity=self.polarity, evidence_used=[],
                conditions_satisfied=[f"Sun and Mercury conjunct in House {sun.house}"],
                conditions_not_satisfied=[], exceptions_encountered=[], modifiers=[],
                provenance=self.provenance, confidence="MODERATE",
                reason=f"Budhaditya Yoga is present in House {sun.house}. Enhances intellect, communication, and executive ability."
            )
        return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["Sun and Mercury not in same house"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Budhaditya Yoga not present.")

class KemadrumaYoga(Yoga):
    def __init__(self):
        super().__init__()
        self.rule_id = "yoga_kemadruma"
        self.name = "Kemadruma"
        self.polarity = "challenging"
        self.tradition = "Parashara"
        self.provenance = "Brihat Parashara Hora Sastra"

    def evaluate(self, chart: Chart, **kwargs) -> RuleResult:
        moon = chart.planets.get("Moon")
        if not moon:
            return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["Moon missing"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Kemadruma Yoga not present.")
            
        house_2 = (moon.house % 12) + 1
        house_12 = ((moon.house - 2) % 12) + 1
        
        has_planet_in_2 = False
        has_planet_in_12 = False
        
        for p_name, p in chart.planets.items():
            if p_name in ["Sun", "Moon", "Rahu", "Ketu", "Ascendant"]:
                continue
            if p.house == house_2: has_planet_in_2 = True
            if p.house == house_12: has_planet_in_12 = True
            
        fired = not (has_planet_in_2 or has_planet_in_12)
        if not fired:
            return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["Planets exist in 2nd or 12th from Moon"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Kemadruma Yoga not present.")
            
        # Check cancellation by Kendra planets
        kendra_planets = [p_name for p_name, p in chart.planets.items() if p.house in [1, 4, 7, 10] and p_name not in ["Rahu", "Ketu", "Ascendant"]]
        if kendra_planets:
            return RuleResult(
                rule_id=self.rule_id, name=self.name, domain=self.domain, fired=True,
                polarity="modifier", evidence_used=[], conditions_satisfied=["Moon is isolated"],
                conditions_not_satisfied=[], exceptions_encountered=[f"Cancelled by Kendra planets ({', '.join(kendra_planets)})"],
                modifiers=[], provenance=self.provenance, confidence="WEAK",
                reason="Kemadruma Yoga is present but cancelled by Kendra planets. Causes intermittent mental isolation."
            )
        return RuleResult(
            rule_id=self.rule_id, name=self.name, domain=self.domain, fired=True,
            polarity="contradicting", evidence_used=[], conditions_satisfied=["Moon is isolated without planets in 2nd or 12th"],
            conditions_not_satisfied=[], exceptions_encountered=[], modifiers=[],
            provenance=self.provenance, confidence="STRONG",
            reason="Kemadruma Yoga is present. Indicates psychological isolation, mental anxiety, and lack of support."
        )

class RajaYoga(Yoga):
    def __init__(self):
        super().__init__()
        self.rule_id = "yoga_raja"
        self.name = "Raja Yoga"
        self.tradition = "Parashara"
        self.provenance = "Brihat Parashara Hora Sastra"

    def evaluate(self, chart: Chart, **kwargs) -> RuleResult:
        kendras = [1, 4, 7, 10]
        trikonas = [1, 5, 9]
        
        kendra_lords = {}
        trikona_lords = {}
        
        for p_name, p in chart.planets.items():
            if p_name in ["Rahu", "Ketu", "Ascendant"]: continue
            for h in p.owns_houses:
                if h in kendras: kendra_lords[p_name] = p
                if h in trikonas: trikona_lords[p_name] = p
                
        formed_yogas = []
        for k_name, k_planet in kendra_lords.items():
            for t_name, t_planet in trikona_lords.items():
                if k_name != t_name and k_planet.house == t_planet.house:
                    msg = f"Raja Yoga formed by {k_name} (Kendra lord) and {t_name} (Trikona lord) conjunct in House {k_planet.house}."
                    if msg not in formed_yogas:
                        formed_yogas.append(msg)
                        
        if formed_yogas:
            return RuleResult(
                rule_id=self.rule_id, name=self.name, domain=self.domain, fired=True,
                polarity="supporting", evidence_used=[], conditions_satisfied=formed_yogas,
                conditions_not_satisfied=[], exceptions_encountered=[], modifiers=formed_yogas,
                provenance=self.provenance, confidence="STRONG",
                reason=f"Raja Yoga is active. {len(formed_yogas)} Kendra-Trikona conjunction(s) found. Conveys authority, status, and leadership."
            )
        return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["No Kendra-Trikona lord conjunctions"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Raja Yoga not present.")

class DhanaYoga(Yoga):
    def __init__(self):
        super().__init__()
        self.rule_id = "yoga_dhana"
        self.name = "Dhana Yoga"
        self.tradition = "Parashara"
        self.provenance = "Brihat Parashara Hora Sastra"

    def evaluate(self, chart: Chart, **kwargs) -> RuleResult:
        wealth_houses = [2, 11]
        fortune_houses = [1, 5, 9]
        
        wealth_lords = {}
        fortune_lords = {}
        
        for p_name, p in chart.planets.items():
            if p_name in ["Rahu", "Ketu", "Ascendant"]: continue
            for h in p.owns_houses:
                if h in wealth_houses: wealth_lords[p_name] = p
                if h in fortune_houses: fortune_lords[p_name] = p
                
        formed = []
        for w_name, w_planet in wealth_lords.items():
            for f_name, f_planet in fortune_lords.items():
                if w_name != f_name and w_planet.house == f_planet.house:
                    msg = f"Dhana Yoga formed by {w_name} (Wealth lord) and {f_name} (Fortune lord) conjunct in House {w_planet.house}."
                    if msg not in formed:
                        formed.append(msg)
                        
        if formed:
            return RuleResult(
                rule_id=self.rule_id, name=self.name, domain=self.domain, fired=True,
                polarity="supporting", evidence_used=[], conditions_satisfied=formed,
                conditions_not_satisfied=[], exceptions_encountered=[], modifiers=formed,
                provenance=self.provenance, confidence="STRONG",
                reason=f"Dhana Yoga is active: {len(formed)} combination(s) found. Bestows financial accumulation, liquidity, and material assets."
            )
        return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["No wealth-fortune lord conjunctions"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Dhana Yoga not present.")

class VesiYoga(Yoga):
    def __init__(self):
        super().__init__()
        self.rule_id = "yoga_vesi"
        self.name = "Vesi"
        self.provenance = "BPHS"

    def evaluate(self, chart: Chart, **kwargs) -> RuleResult:
        sun = chart.planets.get("Sun")
        if not sun: return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["Sun missing"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Vesi Yoga not present.")
        house_2 = (sun.house % 12) + 1
        planets = [p_n for p_n, p in chart.planets.items() if p_n not in ["Moon", "Sun", "Rahu", "Ketu", "Ascendant"] and p.house == house_2]
        if planets:
            return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=True, polarity="supporting", evidence_used=[], conditions_satisfied=[f"Planets in 2nd from Sun: {', '.join(planets)}"], conditions_not_satisfied=[], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="STRONG", reason=f"Vesi Yoga: {', '.join(planets)} in 2nd from Sun. Bestows steady effort, truthful conduct, and balanced fortune.")
        return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["No planets in 2nd from Sun"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Vesi Yoga not present.")

class VosiYoga(Yoga):
    def __init__(self):
        super().__init__()
        self.rule_id = "yoga_vosi"
        self.name = "Vosi"
        self.provenance = "BPHS"

    def evaluate(self, chart: Chart, **kwargs) -> RuleResult:
        sun = chart.planets.get("Sun")
        if not sun: return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["Sun missing"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Vosi Yoga not present.")
        house_12 = ((sun.house - 2) % 12) + 1
        planets = [p_n for p_n, p in chart.planets.items() if p_n not in ["Moon", "Sun", "Rahu", "Ketu", "Ascendant"] and p.house == house_12]
        if planets:
            return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=True, polarity="supporting", evidence_used=[], conditions_satisfied=[f"Planets in 12th from Sun: {', '.join(planets)}"], conditions_not_satisfied=[], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="STRONG", reason=f"Vosi Yoga: {', '.join(planets)} in 12th from Sun. Gives skill, charitable temperament, and wisdom.")
        return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["No planets in 12th from Sun"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Vosi Yoga not present.")

class SunaphaYoga(Yoga):
    def __init__(self):
        super().__init__()
        self.rule_id = "yoga_sunapha"
        self.name = "Sunapha"
        self.provenance = "BPHS"

    def evaluate(self, chart: Chart, **kwargs) -> RuleResult:
        moon = chart.planets.get("Moon")
        if not moon: return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["Moon missing"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Sunapha Yoga not present.")
        house_2 = (moon.house % 12) + 1
        planets = [p_n for p_n, p in chart.planets.items() if p_n not in ["Sun", "Moon", "Rahu", "Ketu", "Ascendant"] and p.house == house_2]
        if planets:
            return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=True, polarity="supporting", evidence_used=[], conditions_satisfied=[f"Planets in 2nd from Moon: {', '.join(planets)}"], conditions_not_satisfied=[], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="STRONG", reason=f"Sunapha Yoga: {', '.join(planets)} in 2nd from Moon. Bestows independent earnings, intelligence, and fame.")
        return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["No planets in 2nd from Moon"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Sunapha Yoga not present.")

class AnaphaYoga(Yoga):
    def __init__(self):
        super().__init__()
        self.rule_id = "yoga_anapha"
        self.name = "Anapha"
        self.provenance = "BPHS"

    def evaluate(self, chart: Chart, **kwargs) -> RuleResult:
        moon = chart.planets.get("Moon")
        if not moon: return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["Moon missing"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Anapha Yoga not present.")
        house_12 = ((moon.house - 2) % 12) + 1
        planets = [p_n for p_n, p in chart.planets.items() if p_n not in ["Sun", "Moon", "Rahu", "Ketu", "Ascendant"] and p.house == house_12]
        if planets:
            return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=True, polarity="supporting", evidence_used=[], conditions_satisfied=[f"Planets in 12th from Moon: {', '.join(planets)}"], conditions_not_satisfied=[], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="STRONG", reason=f"Anapha Yoga: {', '.join(planets)} in 12th from Moon. Bestows good morals, self-control, and physical vitality.")
        return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["No planets in 12th from Moon"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Anapha Yoga not present.")

class ViparitaRajaYoga(Yoga):
    def __init__(self):
        super().__init__()
        self.rule_id = "yoga_viparita_raja"
        self.name = "Viparita Raja"
        self.provenance = "BPHS"

    def evaluate(self, chart: Chart, **kwargs) -> RuleResult:
        from cancellations import CancellationEngine
        canc = CancellationEngine(chart).evaluate_vipareeta_raja_yoga()
        if canc:
            reasons = [c["description"] for c in canc]
            return RuleResult(
                rule_id=self.rule_id, name=self.name, domain=self.domain, fired=True,
                polarity="supporting", evidence_used=[], conditions_satisfied=reasons,
                conditions_not_satisfied=[], exceptions_encountered=[], modifiers=[],
                provenance=self.provenance, confidence="STRONG",
                reason="; ".join(reasons)
            )
        return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["No 6/8/12 lords isolated in Dusthanas"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Viparita Raja Yoga not present.")

class DaridraYoga(Yoga):
    def __init__(self):
        super().__init__()
        self.rule_id = "yoga_daridra"
        self.name = "Daridra"
        self.polarity = "challenging"
        self.provenance = "BPHS"

    def evaluate(self, chart: Chart, **kwargs) -> RuleResult:
        lord_11 = next((p for p in chart.planets.values() if 11 in p.owns_houses), None)
        if lord_11 and lord_11.house in [6, 8, 12]:
            return RuleResult(
                rule_id=self.rule_id, name=self.name, domain=self.domain, fired=True,
                polarity="contradicting", evidence_used=[], conditions_satisfied=[f"11th lord {lord_11.name} in House {lord_11.house}"],
                conditions_not_satisfied=[], exceptions_encountered=[], modifiers=[],
                provenance=self.provenance, confidence="MODERATE",
                reason=f"Daridra Yoga: 11th lord ({lord_11.name}) placed in {ordinal(lord_11.house)} Dusthana, causing financial friction."
            )
        return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["11th lord not in Dusthana"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Daridra Yoga not present.")

class NeechabhangaRajaYoga(Yoga):
    def __init__(self):
        super().__init__()
        self.rule_id = "yoga_neechabhanga"
        self.name = "Neechabhanga Raja"
        self.provenance = "BPHS"

    def evaluate(self, chart: Chart, **kwargs) -> RuleResult:
        from cancellations import CancellationEngine
        nb = CancellationEngine(chart).evaluate_neecha_bhanga()
        active = [n for n in nb if n["is_cancelled"]]
        if active:
            reasons = [f"{n['planet']} ({'; '.join(n['conditions_met'])})" for n in active]
            return RuleResult(
                rule_id=self.rule_id, name=self.name, domain=self.domain, fired=True,
                polarity="supporting", evidence_used=[], conditions_satisfied=reasons,
                conditions_not_satisfied=[], exceptions_encountered=[], modifiers=[],
                provenance=self.provenance, confidence="STRONG",
                reason=f"Neechabhanga Raja Yoga formed: {'; '.join(reasons)}"
            )
        return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["No cancelled debilitated planets"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Neechabhanga Raja Yoga not present.")

class ChamaraYoga(Yoga):
    """
    Chamara Yoga (BPHS Ch 35.15):
    Formed when Lagna is aspected/occupied by benefics, or two benefics occupy 7th, 9th, or 10th.
    Ascribed Results: Deerghayu (Long-lived), scholarly, eloquent, learned in many arts.
    """
    def __init__(self):
        super().__init__()
        self.rule_id = "yoga_chamara"
        self.name = "Chaamara"
        self.provenance = "BPHS"

    def evaluate(self, chart: Chart, **kwargs) -> RuleResult:
        benefics = ["Jupiter", "Venus", "Mercury", "Moon"]
        kendra_benefics = [p.name for p in chart.planets.values() if p.house in [1, 7, 9, 10] and p.name in benefics]
        if len(kendra_benefics) >= 2:
            return RuleResult(
                rule_id=self.rule_id, name=self.name, domain=self.domain, fired=True,
                polarity="supporting", evidence_used=[], conditions_satisfied=[f"Benefics {', '.join(kendra_benefics)} in Kendra/Trikona"],
                conditions_not_satisfied=[], exceptions_encountered=[], modifiers=[],
                provenance=self.provenance, confidence="STRONG",
                reason=f"Chaamara Yoga: Benefics ({', '.join(kendra_benefics)}) in Kendra/Trikona. Bestows Deerghayu (long lifespan), deep intellect, and eloquence."
            )
        return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["Less than 2 benefics in Kendra/Trikona"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Chaamara Yoga not present.")

class SoolaYoga(Yoga):
    """
    Soola Yoga (Naabhasa Yoga - BPHS Ch 35):
    Formed when all 7 physical planets are distributed in exactly 3 signs throughout the chart.
    """
    def __init__(self):
        super().__init__()
        self.rule_id = "yoga_soola"
        self.name = "Soola"
        self.provenance = "BPHS"

    def evaluate(self, chart: Chart, **kwargs) -> RuleResult:
        occupied_signs = set(p.sign for name, p in chart.planets.items() if name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"])
        if len(occupied_signs) == 3:
            return RuleResult(
                rule_id=self.rule_id, name=self.name, domain=self.domain, fired=True,
                polarity="supporting", evidence_used=[], conditions_satisfied=[f"7 planets in 3 signs: {', '.join(occupied_signs)}"],
                conditions_not_satisfied=[], exceptions_encountered=[], modifiers=[],
                provenance=self.provenance, confidence="MODERATE",
                reason=f"Soola Yoga (Naabhasa): All 7 planets concentrated in 3 signs ({', '.join(occupied_signs)}). Sharp intellect, valiant drive, intense focus."
            )
        return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["Planets occupy more than 3 signs"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Soola Yoga not present.")

class RajaSambandhaYoga(Yoga):
    """
    Raja Sambandha Yogas (Jaimini / BPHS):
    Amatyakaraka in own sign, or in Kendra/Trikona from Atmakaraka, or connected to 10th lord.
    """
    def __init__(self):
        super().__init__()
        self.rule_id = "yoga_raja_sambandha"
        self.name = "Raja Sambandha"
        self.provenance = "Jaimini Sutras"

    def evaluate(self, chart: Chart, **kwargs) -> RuleResult:
        amk = next((p for p in chart.planets.values() if getattr(p, "chara_karaka", "") == "AmK"), None)
        ak = next((p for p in chart.planets.values() if getattr(p, "chara_karaka", "") == "AK"), None)
        reasons = []
        if amk and amk.dignity in ["Own House", "Moolatrikona", "Exalted"]:
            reasons.append(f"Amatyakaraka {amk.name} in {amk.dignity} ({amk.sign})")
        if ak and amk:
            diff = (ZODIAC.index(amk.sign) - ZODIAC.index(ak.sign)) % 12 + 1
            if diff in [1, 4, 5, 7, 9, 10]:
                reasons.append(f"Amatyakaraka {amk.name} in Kendra/Trikona ({diff}th) from Atmakaraka {ak.name}")
        if reasons:
            return RuleResult(
                rule_id=self.rule_id, name=self.name, domain=self.domain, fired=True,
                polarity="supporting", evidence_used=[], conditions_satisfied=reasons,
                conditions_not_satisfied=[], exceptions_encountered=[], modifiers=[],
                provenance=self.provenance, confidence="STRONG",
                reason=f"Raja Sambandha Yoga: {'; '.join(reasons)}. Gives high executive post, royal/institutional alliances, and elite advisory rank."
            )
        return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["AmK not in dignity or Kendra/Trikona from AK"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Raja Sambandha Yoga not present.")

class JaiminiRajaYogaAKPK(Yoga):
    """
    Jaimini Raja Yoga (AK-PK Conjunction or Mutual Kendra/Trikona):
    Atmakaraka (AK) and Putrakaraka (PK) / Bhratrikaraka in mutual Kendra/Trikona or conjunction.
    """
    def __init__(self):
        super().__init__()
        self.rule_id = "yoga_jaimini_ak_pk"
        self.name = "Raja (AK-PK)"
        self.provenance = "Jaimini Sutras"

    def evaluate(self, chart: Chart, **kwargs) -> RuleResult:
        ak = next((p for p in chart.planets.values() if getattr(p, "chara_karaka", "") == "AK"), None)
        pk = next((p for p in chart.planets.values() if getattr(p, "chara_karaka", "") in ["PK", "PiK"]), None)
        if ak and pk:
            diff = (ZODIAC.index(pk.sign) - ZODIAC.index(ak.sign)) % 12 + 1
            if diff in [1, 4, 5, 7, 9, 10]:
                return RuleResult(
                    rule_id=self.rule_id, name=self.name, domain=self.domain, fired=True,
                    polarity="supporting", evidence_used=[], conditions_satisfied=[f"AK {ak.name} & PK {pk.name} in {ordinal(diff)} mutual relation"],
                    conditions_not_satisfied=[], exceptions_encountered=[], modifiers=[],
                    provenance=self.provenance, confidence="STRONG",
                    reason=f"Jaimini Raja Yoga (AK-PK): Atmakaraka ({ak.name}) and Putrakaraka ({pk.name}) in Kendra/Trikona. Gives loyal following, authority, and power."
                )
        return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["AK and PK not in Kendra/Trikona"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="AK-PK Raja Yoga not present.")

class YogadaYoga(Yoga):
    """
    Yogada Yoga (Jaimini / BPHS):
    Planets aspecting both Lagna and Hora Lagna (HL) or Ghatika Lagna (GL).
    """
    def __init__(self):
        super().__init__()
        self.rule_id = "yoga_yogada"
        self.name = "Yogada (HL)"
        self.provenance = "Jaimini / BPHS"

    def evaluate(self, chart: Chart, **kwargs) -> RuleResult:
        from wealth_lagnas_engine import WealthLagnasEngine
        wl = WealthLagnasEngine(chart).calculate_special_lagnas()
        hl_sign = wl.get("hora_lagna", {}).get("sign")
        lagna_sign = chart.ascendant_sign
        yogada_planets = []
        for pname, p in chart.planets.items():
            if p.sign in [lagna_sign, hl_sign] or lagna_sign in p.aspects_houses or hl_sign in p.aspects_houses:
                yogada_planets.append(pname)
        if yogada_planets:
            return RuleResult(
                rule_id=self.rule_id, name=self.name, domain=self.domain, fired=True,
                polarity="supporting", evidence_used=[], conditions_satisfied=[f"Planets {', '.join(yogada_planets)} associated with Lagna & HL"],
                conditions_not_satisfied=[], exceptions_encountered=[], modifiers=[],
                provenance=self.provenance, confidence="STRONG",
                reason=f"Yogada Yoga (HL): {', '.join(yogada_planets)} associate with Lagna ({lagna_sign}) & Hora Lagna ({hl_sign}). Bestows lasting wealth, liquid capital, and commercial prosperity."
            )
        return RuleResult(rule_id=self.rule_id, name=self.name, domain=self.domain, fired=False, polarity="neutral", evidence_used=[], conditions_satisfied=[], conditions_not_satisfied=["No planets aspecting both Lagna and HL"], exceptions_encountered=[], modifiers=[], provenance=self.provenance, confidence="INSUFFICIENT", reason="Yogada Yoga not present.")

def evaluate_all_yogas(chart: Chart) -> List[Dict[str, Any]]:
    all_yoga_classes = [
        RuchakaYoga(), BhadraYoga(), HamsaYoga(), MalavyaYoga(), ShashaYoga(),
        GajaKesariYoga(), BudhadityaYoga(), KemadrumaYoga(),
        RajaYoga(), DhanaYoga(), VesiYoga(), VosiYoga(),
        SunaphaYoga(), AnaphaYoga(), ViparitaRajaYoga(), DaridraYoga(), NeechabhangaRajaYoga(),
        ChamaraYoga(), SoolaYoga(), RajaSambandhaYoga(), JaiminiRajaYogaAKPK(), YogadaYoga()
    ]
    results = []
    for y in all_yoga_classes:
        res = y.evaluate(chart)
        if res and res.fired:
            results.append(res.to_dict())
    return results
