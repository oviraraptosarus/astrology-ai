from typing import List, Dict, Any
from dataclasses import dataclass, field
from domain_engine import DomainAnalysis
from activation_engine import ActivationProfile
from vedic_models import Chart
from analysis_models import EventAnalysis

class CancellationRule:
    @staticmethod
    def detect_neechabhanga(chart: Chart, contradicting_evidence: List[Dict]) -> List[Dict]:
        cancellations = []
        
        exalt_lords = {
            "Sun": "Mars", "Moon": "Venus", "Mars": "Saturn", 
            "Mercury": "Mercury", "Jupiter": "Moon", "Venus": "Jupiter", "Saturn": "Venus"
        }

        moon = chart.planets.get("Moon")
        
        for ev in contradicting_evidence:
            if ev.get("source_rule") == "dignity" and "debilitated" in ev.get("reason", "").lower():
                planet_name = ev.get("subject")
                planet = chart.planets.get(planet_name)
                
                if not planet:
                    continue
                    
                bhanga_reasons = []
                
                if planet.dispositor:
                    dispositor = chart.planets.get(planet.dispositor)
                    if dispositor:
                        if dispositor.house in [1, 4, 7, 10]:
                            bhanga_reasons.append(f"Dispositor {dispositor.name} is in a Kendra from Ascendant (House {dispositor.house})")
                        if moon:
                            dist_from_moon = (dispositor.house - moon.house) % 12
                            if dist_from_moon in [0, 3, 6, 9]:
                                bhanga_reasons.append(f"Dispositor {dispositor.name} is in a Kendra from Moon")
                                
                        if dispositor.name in planet.aspected_by:
                            bhanga_reasons.append(f"Debilitated planet is aspected by its own dispositor {dispositor.name}")

                exalt_lord_name = exalt_lords.get(planet.name)
                if exalt_lord_name:
                    exalt_lord = chart.planets.get(exalt_lord_name)
                    if exalt_lord:
                        if exalt_lord.house in [1, 4, 7, 10]:
                            bhanga_reasons.append(f"Exaltation lord {exalt_lord.name} is in a Kendra from Ascendant")
                        if moon:
                            dist_from_moon = (exalt_lord.house - moon.house) % 12
                            if dist_from_moon in [0, 3, 6, 9]:
                                bhanga_reasons.append(f"Exaltation lord {exalt_lord.name} is in a Kendra from Moon")
                
                if planet.retrograde:
                    bhanga_reasons.append(f"{planet.name} is retrograde, which reverses debilitation according to some texts (Uttara Kalamrita)")
                    
                if bhanga_reasons:
                    cancellations.append({
                        "type": "CANCELLATION",
                        "original_condition": ev,
                        "cancellation_condition": "; ".join(bhanga_reasons),
                        "result": "Debilitation is cancelled (Neechabhanga Raja Yoga). Instead of failure, it indicates initial struggle followed by rise and success.",
                        "provenance": "Phaladeepika & Uttara Kalamrita"
                    })
        return cancellations

class SynthesisEngine:
    def __init__(self, chart: Chart):
        self.chart = chart
        
    def synthesize(self, domain_analysis: DomainAnalysis, activation_profile: ActivationProfile, question: str = "", time_horizon: str = "", contradiction_analysis: Dict = None) -> EventAnalysis:
        from convergence_engine import ConvergenceEngine
        supporting = domain_analysis.supporting_evidence
        contradicting = domain_analysis.contradicting_evidence
        missing = domain_analysis.missing_evidence
        
        all_evidence = supporting + contradicting
        parashari_convergence = ConvergenceEngine.evaluate(domain_analysis.domain, all_evidence)
        
        # Priority 6: Independent Jaimini Analysis
        from jaimini_engine import JaiminiEngine
        jaimini_analysis = JaiminiEngine.analyze_domain_jaimini(self.chart, domain_analysis.domain)

        # Priority 7: Multi-Tradition Arbitration (KP, Nadi, Tajaka join Parashari & Jaimini)
        arbitration = None
        try:
            from tradition_arbiter import run_full_arbitration
            arbitration = run_full_arbitration(
                self.chart,
                domain=domain_analysis.domain,
                question=question,
                domain_analysis=domain_analysis,
                target_date=None,
                birth_local=getattr(self, "_birth_local", None),
                birth_dt_utc=getattr(self, "_birth_utc", None),
                lat=getattr(self, "_lat", None), lon=getattr(self, "_lon", None))
        except Exception:
            arbitration = None

        secondary_methodologies = ["JAIMINI"]
        if arbitration:
            for v in arbitration.get("verdicts", []):
                t = v.get("tradition")
                if t and t not in secondary_methodologies and t != "PARASHARI":
                    secondary_methodologies.append(t)
        disagreements = [parashari_convergence.get("summary", "")] if parashari_convergence else []
        
        # Compare Parashari (Natal Promise) vs Jaimini Confidence
        p_conf = domain_analysis.confidence
        j_conf = jaimini_analysis.get("confidence", "MODERATE")
        
        if (p_conf in ["STRONG", "VERY_STRONG"] and j_conf in ["WEAK", "VERY_WEAK"]) or \
           (j_conf in ["STRONG", "VERY_STRONG"] and p_conf in ["WEAK", "VERY_WEAK"]):
            methodology_convergence = "DISAGREEMENT"
            disagreements.append(f"Methodological Conflict: Parashari indicates {p_conf}, but Jaimini indicates {j_conf}.")
        else:
            methodology_convergence = parashari_convergence.get("status", "N/A")
            
        # Add textual contradiction analysis from RAG
        if contradiction_analysis and contradiction_analysis.get("has_contradictions"):
            disagreements.append(f"Textual Contradictions: {contradiction_analysis.get('contradiction_analysis')}")
            
        from cancellations import CancellationEngine
        from sensitive_points import SensitivePointsEngine
        from advanced_avasthas import AdvancedAvasthaEngine
        from dosha_engine import DoshaEngine
        
        canc_engine = CancellationEngine(self.chart)
        cancellations = canc_engine.evaluate_all()
        
        sp_data = SensitivePointsEngine(self.chart).calculate_all()
        avasthas_data = AdvancedAvasthaEngine(self.chart).combine_all()
        dosha_data = DoshaEngine(self.chart).evaluate_all()
        
        dasha_ev = [e.to_dict() for e in activation_profile.dasha_evidence]
        transit_ev = [e.to_dict() for e in activation_profile.transit_evidence]
        timing_windows = [w.to_dict() if hasattr(w, "to_dict") else w for w in getattr(activation_profile, "timing_windows", [])]
        
        # Build Final Judgment
        final_judgment_text = f"Natal Promise is {domain_analysis.confidence}. Jaimini is {j_conf}. Timing is {activation_profile.timing_status}."
        if arbitration:
            final_judgment_text += (
                f"\n\nMulti-Tradition Arbitration: final verdict '{arbitration['final_verdict']}' "
                f"(weighted score {arbitration['weighted_total']:+.2f}, ladder {' > '.join(arbitration['priority_ladder'])}). "
                f"{arbitration['explanation']}")
            if arbitration.get("dissent_register"):
                final_judgment_text += "\nDissenting opinions preserved: " + "; ".join(
                    f"[{d['tradition']} says {d['verdict']} ({d['confidence']})]"
                    for d in arbitration["dissent_register"])
        if contradiction_analysis and contradiction_analysis.get("has_contradictions"):
            final_judgment_text += f"\n\nMeta-Synthesis of Contradictions: {contradiction_analysis.get('contradiction_analysis')}"
        
        # Compile EventAnalysis
        return EventAnalysis(
            event=domain_analysis.domain,
            domain=domain_analysis.domain,
            event_id=getattr(domain_analysis, "event_id", ""),
            question=question,
            time_horizon=time_horizon,
            primary_significators=domain_analysis.relevant_planets,
            secondary_significators=domain_analysis.relevant_lords,
            natal_promise_status=domain_analysis.confidence,
            supporting_factors=supporting,
            contradicting_factors=contradicting,
            cancellations=cancellations,
            varga_confirmation=domain_analysis.varga_confirmation,
            dasha_activation={"evidence": dasha_ev, "status": activation_profile.timing_status},
            transit_activation={"evidence": transit_ev},
            primary_methodology="PARASHARI",
            secondary_methodology=secondary_methodologies,
            methodology_convergence=methodology_convergence,
            methodology_disagreement_details=disagreements,
            missing_evidence=missing,
            final_judgment=final_judgment_text,
            timing_windows=timing_windows,
            sensitive_points=sp_data,
            avasthas=avasthas_data,
            doshas=dosha_data
        )
