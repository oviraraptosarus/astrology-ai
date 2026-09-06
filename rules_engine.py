from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from vedic_models import Chart, Planet

@dataclass
class RuleResult:
    rule_id: str
    name: str
    domain: str
    fired: bool
    polarity: str # 'supporting', 'contradicting', 'modifier', 'neutral'
    evidence_used: List[str]
    conditions_satisfied: List[str]
    conditions_not_satisfied: List[str]
    exceptions_encountered: List[str]
    modifiers: List[str]
    provenance: str
    confidence: str # VERY_STRONG, STRONG, MODERATE, WEAK, INSUFFICIENT
    reason: str
    
    def to_dict(self):
        return {
            "rule_id": self.rule_id,
            "name": self.name,
            "domain": self.domain,
            "fired": self.fired,
            "polarity": self.polarity,
            "evidence_used": self.evidence_used,
            "conditions_satisfied": self.conditions_satisfied,
            "conditions_not_satisfied": self.conditions_not_satisfied,
            "exceptions_encountered": self.exceptions_encountered,
            "modifiers": self.modifiers,
            "provenance": self.provenance,
            "confidence": self.confidence,
            "reason": self.reason
        }

class Rule:
    def __init__(self):
        self.rule_id = ""
        self.name = ""
        self.tradition = ""
        self.domain = ""
        self.polarity = "neutral"
        self.timing_relevance = False
        self.varga_relevance = False
        self.provenance = ""
        self.confidence = "MODERATE"

    def evaluate(self, chart: Chart, **kwargs) -> RuleResult:
        raise NotImplementedError("Rules must implement evaluate()")

class RuleEvaluator:
    def __init__(self, chart: Chart):
        self.chart = chart
        self.rules: List[Rule] = []

    def add_rule(self, rule: Rule):
        self.rules.append(rule)

    def evaluate_all(self, domain: str = "general", **kwargs) -> List[RuleResult]:
        results = []
        for rule in self.rules:
            if rule.domain == domain or rule.domain == "general":
                result = rule.evaluate(self.chart, **kwargs)
                if result:
                    results.append(result)
        return results
