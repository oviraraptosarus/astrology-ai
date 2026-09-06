import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
import json
from astrology_engine import calculate_chart_with_object, get_semantic_view
from synthesis_engine import SynthesisEngine
from remedy_engine import RemedyEngine
from panchangam_engine import PanchangamEngine
from event_analysis import EventPredictionEngine
import pytz

# Birth: Aug 1, 2008, 18:25 IST, Ramachandrapuram
chart, chart_dict = calculate_chart_with_object(2008, 8, 1, 18, 25, 16.8186, 82.0641, "Asia/Kolkata", "Native")

print("==================================================")
print("1. EVENT PREDICTION ENGINE OUTPUT (Career Timing in 2027):")
print("==================================================")
ea_engine = EventPredictionEngine(chart)
analysis_res = ea_engine.analyze_event("When will I get a major job promotion?", datetime(2027, 6, 1))
res_dict = analysis_res.to_dict()
print(json.dumps(res_dict, indent=2))

print("\n==================================================")
print("2. SYNTHESIS ENGINE EVIDENCE & DOMAIN PROTOCOL:")
print("==================================================")
# Current API: DomainEngine.analyze_domain -> SynthesisEngine.synthesize
from domain_engine import DomainEngine
from rules_engine import RuleEvaluator
from activation_engine import ActivationEngine
rule_eval = RuleEvaluator(chart)
domain_engine = DomainEngine(chart, rule_eval)
domain_analysis = domain_engine.analyze_domain("CAREER")
activation_profile = ActivationEngine(chart).assess_activation(
    "career", domain_analysis.relevant_planets, domain_analysis.relevant_houses)
career_synth = SynthesisEngine(chart).synthesize(domain_analysis, activation_profile)
print(json.dumps(career_synth.to_dict(), indent=2, default=str))
