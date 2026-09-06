from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class EventAnalysis:
    """The canonical event analysis schema produced by the Synthesis Engine."""
    event: str
    domain: str
    event_id: str
    question: str
    time_horizon: str
    primary_significators: List[str]
    secondary_significators: List[str]
    natal_promise_status: str
    supporting_factors: List[Dict]
    contradicting_factors: List[Dict]
    cancellations: List[Dict]
    varga_confirmation: Dict[str, str]
    dasha_activation: Dict[str, Any]
    transit_activation: Dict[str, Any]
    primary_methodology: str
    secondary_methodology: List[str]
    methodology_convergence: str
    methodology_disagreement_details: List[str]
    missing_evidence: List[str]
    final_judgment: str
    timing_windows: List[Dict] = field(default_factory=list)
    sensitive_points: Dict[str, Any] = field(default_factory=dict)
    avasthas: Dict[str, Any] = field(default_factory=dict)
    doshas: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self):
        return {
            "event": self.event,
            "domain": self.domain,
            "event_id": self.event_id,
            "question": self.question,
            "time_horizon": self.time_horizon,
            "primary_significators": self.primary_significators,
            "secondary_significators": self.secondary_significators,
            "natal_promise_status": self.natal_promise_status,
            "supporting_factors": self.supporting_factors,
            "contradicting_factors": self.contradicting_factors,
            "cancellations": self.cancellations,
            "varga_confirmation": self.varga_confirmation,
            "dasha_activation": self.dasha_activation,
            "transit_activation": self.transit_activation,
            "primary_methodology": self.primary_methodology,
            "secondary_methodology": self.secondary_methodology,
            "methodology_convergence": self.methodology_convergence,
            "methodology_disagreement_details": self.methodology_disagreement_details,
            "missing_evidence": self.missing_evidence,
            "final_judgment": self.final_judgment,
            "timing_windows": self.timing_windows,
            "sensitive_points": self.sensitive_points,
            "avasthas": self.avasthas,
            "doshas": self.doshas
        }

@dataclass
class YearAheadAnalysis:
    """The reasoning pack for a general year-ahead query."""
    target_period_start: str
    target_period_end: str
    major_themes: List[str]
    active_dasha: List[Dict]
    dasha_transitions: List[Dict]
    major_transits: List[Dict]
    important_yogas: List[Dict]
    supporting_evidence: List[Dict]
    contradicting_evidence: List[Dict]
    timing_windows: List[Dict]
    
    def to_dict(self):
        return {
            "target_period_start": self.target_period_start,
            "target_period_end": self.target_period_end,
            "major_themes": self.major_themes,
            "active_dasha": self.active_dasha,
            "dasha_transitions": self.dasha_transitions,
            "major_transits": self.major_transits,
            "important_yogas": self.important_yogas,
            "supporting_evidence": self.supporting_evidence,
            "contradicting_evidence": self.contradicting_evidence,
            "timing_windows": self.timing_windows,
            "domain": "general_timing", # for compatibility
            "time_horizon": "12_MONTHS"
        }
