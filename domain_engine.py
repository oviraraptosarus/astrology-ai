from vedic_models import Chart
from rules_engine import RuleEvaluator
from typing import List, Dict, Any
from dataclasses import dataclass, field
from house_engine import HouseEngine
from planet_engine import PlanetEngine
from event_protocols import ProtocolRegistry, EventProtocol

@dataclass
class DomainAnalysis:
    domain: str
    event_id: str
    relevant_houses: List[int]
    relevant_planets: List[str]
    relevant_lords: List[str]
    supporting_evidence: List[Dict]
    contradicting_evidence: List[Dict]
    missing_evidence: List[str]
    varga_confirmation: Dict[str, str] # e.g. {"D10": "CONFIRMATION", "D9": "NEUTRAL"}
    confidence: str # STRONG, MODERATE, WEAK
    house_analysis: Dict[int, Any] = field(default_factory=dict)
    planet_analysis: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "domain": self.domain,
            "event_id": self.event_id,
            "relevant_houses": self.relevant_houses,
            "relevant_planets": self.relevant_planets,
            "relevant_lords": self.relevant_lords,
            "supporting_evidence": self.supporting_evidence,
            "contradicting_evidence": self.contradicting_evidence,
            "missing_evidence": self.missing_evidence,
            "varga_confirmation": self.varga_confirmation,
            "confidence": self.confidence,
            "house_analysis": self.house_analysis,
            "planet_analysis": self.planet_analysis
        }

class DomainEngine:
    def __init__(self, chart: Chart, rule_evaluator: RuleEvaluator):
        self.chart = chart
        self.rule_evaluator = rule_evaluator

    def analyze_domain(self, domain_or_event: str) -> DomainAnalysis:
        # Check if they passed an explicit event_id or a broad domain
        protocol = ProtocolRegistry.get_protocol(domain_or_event)
        
        if not protocol:
            # Fallback heuristic mapping if they just passed "career"
            event_id = ProtocolRegistry.match_event_to_protocol(domain_or_event)
            protocol = ProtocolRegistry.get_protocol(event_id)
            
        if not protocol:
            # Absolute fallback
            protocol = ProtocolRegistry.get_protocol("career_promotion")
            
        relevant_houses = protocol.primary_houses + protocol.secondary_houses
        relevant_planets = protocol.primary_karakas
        relevant_lords = []
        
        for h in relevant_houses:
            lord = next((p.name for p in self.chart.planets.values() if h in p.owns_houses), None)
            if lord and lord not in relevant_lords:
                relevant_lords.append(lord)
                if lord not in relevant_planets:
                    relevant_planets.append(lord)
                    
        # Pull evidence from Rules and Evidence Engine
        from evidence_engine import RuleGenerators
        from cancellations import CancellationEngine
        cancellation_engine = CancellationEngine(self.chart)
        
        generated_evidence = []
        for h in relevant_houses:
            generated_evidence.extend(RuleGenerators.eval_house_lord_placement(self.chart, protocol.event_name, h))
            generated_evidence.extend(RuleGenerators.eval_house_aspects(self.chart, protocol.event_name, h))
        for p in relevant_planets + relevant_lords:
            generated_evidence.extend(RuleGenerators.eval_dignity(self.chart, protocol.event_name, p))
            generated_evidence.extend(RuleGenerators.eval_condition_and_strength(self.chart, protocol.event_name, p))
        
        cancellations = cancellation_engine.evaluate_all_cancellations()
        for c in cancellations.get("neechabhanga_results", []):
            if c.get("is_neechabhanga"):
                from evidence_engine import Evidence, EvidenceStrength
                generated_evidence.append(Evidence(
                    id=f"{c['debilitated_planet'].lower()}_nbry",
                    domain=protocol.event_name,
                    polarity="supporting",
                    source_rule="neechabhanga",
                    subject=c["debilitated_planet"],
                    strength=EvidenceStrength.VERY_STRONG,
                    reason=f"Neecha Bhanga Raja Yoga (NBRY) formed for {c['debilitated_planet']}: {'; '.join(c.get('cancelling_factors', []))}"
                ))
        
        rule_results = self.rule_evaluator.evaluate_all(protocol.event_id.split('_')[0])
        
        supporting = [r.to_dict() for r in rule_results if r.polarity == "supporting" and r.fired]
        contradicting = [r.to_dict() for r in rule_results if r.polarity == "contradicting" and r.fired]
        
        # Add generated evidence
        for ge in generated_evidence:
            if ge.polarity == "supporting":
                supporting.append(ge.to_dict())
            elif ge.polarity == "contradicting":
                contradicting.append(ge.to_dict())
        
        # Deep Domain Engine Generation
        house_analysis_results = {}
        for h in relevant_houses:
            house_analysis_results[h] = HouseEngine.analyze_house(self.chart, h)
            
        planet_analysis_results = {}
        for p in relevant_planets + relevant_lords:
            if p not in planet_analysis_results:
                planet_analysis_results[p] = PlanetEngine.analyze_planet(self.chart, p)

        # Natal Promise Classification
        score = len(supporting) - len(contradicting)
        if len(supporting) > 3 and score >= 2:
            promise_status = "VERY STRONG"
        elif len(supporting) > 1 and score >= 1:
            promise_status = "STRONG"
        elif len(supporting) == 0 and len(contradicting) > 1:
            promise_status = "WEAK"
        elif len(supporting) > 0 and len(contradicting) > 0 and score == 0:
            promise_status = "MIXED"
        elif not supporting and not contradicting:
            promise_status = "INSUFFICIENT"
        else:
            promise_status = "MODERATE"

        from varga_engine import VargaEngine
        
        varga_conf = {}
        all_vargas_to_check = protocol.primary_vargas + protocol.secondary_vargas
        
        for v in all_vargas_to_check:
            # Check reliability first
            reliability_meta = VargaEngine.get_varga_reliability(v, is_birth_time_precise=False) # In a real app this flag comes from user profile
            if reliability_meta["reliability"] == "LOW":
                varga_conf[v] = "UNRELIABLE"
                continue
                
            varga_dignities = VargaEngine.assess_dignity(self.chart, v, relevant_planets)
            
            # Classification Logic: CONFIRMS, SUPPORTS, MODIFIES, CONTRADICTS, NEUTRAL, UNAVAILABLE, UNRELIABLE
            if all(d == "UNAVAILABLE" for d in varga_dignities.values()):
                varga_conf[v] = "UNAVAILABLE"
                continue
                
            has_strong = any(d in ["Exalted", "Own House"] for d in varga_dignities.values())
            has_moderate = any(d in ["Friendly Sign"] for d in varga_dignities.values())
            has_weak = any(d in ["Debilitated", "Enemy Sign"] for d in varga_dignities.values())
            
            if has_strong and not has_weak:
                # Strong Varga + Strong D1 = CONFIRMS
                # Strong Varga + Weak D1 = MODIFIES (lifts it up)
                if promise_status in ["STRONG", "VERY STRONG"]:
                    varga_conf[v] = "CONFIRMS"
                elif promise_status in ["WEAK", "INSUFFICIENT"]:
                    varga_conf[v] = "MODIFIES (Lifts)"
                else:
                    varga_conf[v] = "SUPPORTS"
                    
            elif has_weak and not has_strong:
                # Weak Varga + Strong D1 = MODIFIES/CONTRADICTS (pulls it down)
                # Weak Varga + Weak D1 = CONFIRMS (confirms the negative)
                if promise_status in ["STRONG", "VERY STRONG"]:
                    varga_conf[v] = "CONTRADICTS"
                elif promise_status in ["WEAK"]:
                    varga_conf[v] = "CONFIRMS (Negative)"
                else:
                    varga_conf[v] = "MODIFIES (Challenges)"
                    
            elif has_strong and has_weak:
                varga_conf[v] = "MIXED"
            elif has_moderate and not has_weak:
                varga_conf[v] = "SUPPORTS"
            else:
                varga_conf[v] = "NEUTRAL"
                
                
        missing = []
        if any(v == "UNAVAILABLE" for v in varga_conf.values()):
            missing.append("Varga structural dignity missing or incomplete for required Vargas")
            
        return DomainAnalysis(
            domain=protocol.event_name,
            event_id=protocol.event_id,
            relevant_houses=relevant_houses,
            relevant_planets=relevant_planets,
            relevant_lords=relevant_lords,
            supporting_evidence=supporting,
            contradicting_evidence=contradicting,
            missing_evidence=missing,
            varga_confirmation=varga_conf,
            confidence=promise_status,
            house_analysis=house_analysis_results,
            planet_analysis=planet_analysis_results
        )
