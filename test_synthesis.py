import unittest
import json
from vedic_models import Chart, Planet
from rules_engine import RuleEvaluator
from domain_engine import DomainEngine
from activation_engine import ActivationEngine
from synthesis_engine import SynthesisEngine

class TestSynthesisEngine(unittest.TestCase):
    def setUp(self):
        self.chart = Chart(ascendant_sign="Aries", ascendant_degree=15)
        
        # Scenario: Strong Career Indicators (Exalted Saturn in 10th)
        self.chart.add_planet(Planet("Saturn", "Capricorn", 15, False))
        self.chart.planets["Saturn"].dignity = "Own House" # Simplified
        self.chart.planets["Saturn"].house = 10
        self.chart.planets["Saturn"].owns_houses = [10, 11]
        
        # Affliction: Sun also in 10th (Combusting Saturn)
        self.chart.add_planet(Planet("Sun", "Capricorn", 14, False))
        self.chart.planets["Sun"].house = 10
        self.chart.planets["Sun"].owns_houses = [5]
        
        # Run condition engine logic manually for test
        self.chart.planets["Saturn"].combustion = {"status": True, "sun_distance": 1.0, "threshold": 15}
        
        # Dasha Timing: Saturn Mahadasha
        self.chart.current_dasha = {"mahadasha": "Saturn", "antardasha": "Sun"}
        self.chart.current_transits = {}
        
        # Setup rules
        self.rule_eval = RuleEvaluator(self.chart)
        # Note: In a real run, evidence_engine/rules would populate the domain_engine.
        # Since we haven't ported the base dignities to Rules yet, we will inject mock evidence into the DomainAnalysis.
        
    def test_synthesis_conflict_resolution(self):
        domain_engine = DomainEngine(self.chart, self.rule_eval)
        domain_analysis = domain_engine.analyze_domain("career")
        
        # Inject mock evidence for the test
        domain_analysis.supporting_evidence = [
            {"source_rule": "dignity", "reason": "Saturn is in Own House in 10th."}
        ]
        domain_analysis.contradicting_evidence = [
            {"source_rule": "combustion", "reason": "Saturn is combust by the Sun."}
        ]
        
        activation_engine = ActivationEngine(self.chart)
        activation_profile = activation_engine.assess_activation("career", ["Saturn"], [10])
        
        synthesis_engine = SynthesisEngine(self.chart)
        result = synthesis_engine.synthesize(domain_analysis, activation_profile)
        
        # Since 1 support and 1 contradiction, natal promise should not be STRONG
        self.assertIn(result.natal_promise_status, ["MIXED", "WEAK", "MODERATE"])
        
        # Timing should be FAVORABLE or MIXED since Saturn is active
        self.assertIn(result.dasha_activation["status"], ["FAVORABLE", "MIXED"])
        
        # Trace equivalents in the canonical schema: factors carry the evidence text
        self.assertTrue(any("Own House" in f.get("reason", "") for f in result.supporting_factors))
        self.assertTrue(any("combust" in f.get("reason", "").lower() for f in result.contradicting_factors))
        self.assertTrue(any("Saturn" in str(f) for f in result.dasha_activation.get("evidence", [])))

if __name__ == '__main__':
    unittest.main()
