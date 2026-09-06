from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime

# Import engines
from vedic_models import Chart
from methodology_router import MethodologyRouter
from domain_engine import DomainEngine
from rules_engine import RuleEvaluator
from dasha_engine import DashaEngine
from transit_engine import TransitEngine
from synthesis_engine import SynthesisEngine
from activation_engine import ActivationProfile

@dataclass
class EventAnalysisResult:
    """The final payload that is passed to the LLM for synthesis."""
    question: str
    domain: str
    methodology_route: Dict[str, Any]
    natal_promise: Dict[str, Any]
    activation: Dict[str, Any]
    timing: Dict[str, Any]
    convergence: str
    llm_guidance: str
    
    def to_dict(self):
        return {
            "question": self.question,
            "domain": self.domain,
            "methodology_route": self.methodology_route,
            "natal_promise": self.natal_promise,
            "activation": self.activation,
            "timing": self.timing,
            "convergence": self.convergence,
            "llm_guidance": self.llm_guidance
        }

class EventPredictionEngine:
    """
    Executes the ultimate predictive pipeline:
    QUESTION -> DOMAIN -> METHODOLOGY -> NATAL PROMISE -> ACTIVATION -> TIMING -> CONVERGENCE -> LLM GUIDANCE
    """
    
    def __init__(self, chart: Chart):
        self.chart = chart
        self.rule_evaluator = RuleEvaluator(chart)
        self.domain_engine = DomainEngine(chart, self.rule_evaluator)
        self.synthesis_engine = SynthesisEngine(chart)
        
    def analyze_event(self, question: str, target_date: datetime) -> EventAnalysisResult:
        # 1. QUESTION & DOMAIN & METHODOLOGY
        # (Router identifies Domain and constructs the Methodology Route)
        route = MethodologyRouter.route_question(question)
        domain = route["domain"]
        primary_method = route["primary_methodology"]
        
        # 2. NATAL PROMISE (D1 + Varga + Yogas)
        # We delegate this to the domain engine which uses the RuleEvaluator
        promise_analysis = self.domain_engine.analyze_domain(domain)
        natal_promise = {
            "status": promise_analysis.confidence,
            "supporting_evidence": promise_analysis.supporting_evidence,
            "contradicting_evidence": promise_analysis.contradicting_evidence,
            "vargas_checked": route["required_vargas"]
        }
        
        # 3. ACTIVATION (Dasha & Timing)
        from activation_engine import ActivationEngine
        activation_engine = ActivationEngine(self.chart)
        activation_profile = activation_engine.assess_activation(
            domain, promise_analysis.relevant_planets, promise_analysis.relevant_houses
        )
        
        activation = {
            "dasha_system": route["required_dashas"][0] if route.get("required_dashas") else "VIMSHOTTARI",
            "dasha_evidence": [e.to_dict() for e in activation_profile.dasha_evidence],
            "transit_evidence": [e.to_dict() for e in activation_profile.transit_evidence],
            "timing_status": activation_profile.timing_status,
            "timing_windows": [w.to_dict() for w in activation_profile.timing_windows]
        }
        
        # 4. TIMING (Transits)
        transit_results = TransitEngine.evaluate_double_transit(self.chart, target_date)
        timing = {
            "transit_system": "DOUBLE_TRANSIT_RAO",
            "double_transit_signs": transit_results["double_transit_signs"],
            "activated_natal_houses": transit_results["activated_houses"],
            "activated_natal_lords": transit_results["activated_house_lords"]
        }
        
        # 5. CONVERGENCE (Method A vs B)
        synthesis_result = self.synthesis_engine.synthesize(promise_analysis, activation_profile, question, str(target_date.date()))
        convergence_status = synthesis_result.methodology_convergence
        
        # 6. LLM GUIDANCE
        llm_guidance = (
            f"The natal promise is {promise_analysis.confidence}. Timing activation status is {activation_profile.timing_status}. "
            f"Methodology convergence is {convergence_status}. Transits are activating houses {timing['activated_natal_houses']}."
        )
        
        return EventAnalysisResult(
            question=question,
            domain=domain,
            methodology_route=route,
            natal_promise=natal_promise,
            activation=activation,
            timing=timing,
            convergence=convergence_status,
            llm_guidance=llm_guidance
        )
