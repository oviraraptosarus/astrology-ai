import json
from typing import Dict, List, Any
from vedic_models import Chart
from evidence_engine import Evidence, EvidenceStrength

class ConvergenceEngine:
    """
    Evaluates evidence across multiple methodologies (e.g., Parashari vs Jaimini)
    to mechanically detect convergences (agreements) or contradictions.
    """
    
    @staticmethod
    def evaluate(domain: str, evidence_list: List[Dict]) -> Dict[str, Any]:
        """
        Groups evidence by polarity and root source (e.g. planet) 
        to calculate a convergence score that resists redundant "SAME FACT REPEATED" inflation.
        """
        supporting = [e for e in evidence_list if e.get("polarity") == "supporting"]
        contradicting = [e for e in evidence_list if e.get("polarity") == "contradicting"]
        
        def extract_root(evidence: Dict) -> str:
            # Find the primary planet driving the rule. Evidence dicts expose the
            # planet across reason/subject/id/conditions_satisfied (schema varies by
            # source engine), so scan all of them, not just conditions_satisfied
            # (which is empty for house/aspect evidence and previously collapsed
            # every item into a single "GENERAL" root, destroying independence).
            haystack = " ".join(str(evidence.get(k, "")) for k in
                                ("reason", "subject", "id", "source_rule")) + " " + \
                       " ".join(evidence.get("conditions_satisfied", []) or [])
            for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
                if p in haystack:
                    return p
            # Fall back to a house/subject key so distinct houses stay independent
            subj = str(evidence.get("subject") or evidence.get("id") or "GENERAL")
            return subj or "GENERAL"

        def score_mapper(strength_val) -> float:
            # Evidence carries its weight under "strength" (enum or string like
            # "STRONG"); older paths used "confidence". Accept both. Reading the
            # wrong key silently defaulted EVERY item to MODERATE=3.0, erasing all
            # strength differentiation.
            if hasattr(strength_val, "name"):
                strength_val = strength_val.name
            mapping = {"VERY_STRONG": 5.0, "STRONG": 4.0, "MODERATE": 3.0, "WEAK": 2.0, "VERY_WEAK": 1.0}
            return mapping.get(str(strength_val).upper().replace(" ", "_"), 3.0)

        # Calculate scores with diminishing returns for SAME FACT REPEATED
        def calculate_diminished_score(evidence_group: List[Dict]) -> float:
            root_map: Dict[str, List[float]] = {}
            for e in evidence_group:
                root = extract_root(e)
                # Prefer "strength" (the real key on domain evidence); fall back to
                # "confidence" for legacy evidence dicts. Never silently default.
                weight = e.get("strength")
                if weight is None:
                    weight = e.get("confidence", "MODERATE")
                score = score_mapper(weight)
                if root not in root_map:
                    root_map[root] = []
                root_map[root].append(score)
            
            total = 0.0
            for root, scores in root_map.items():
                scores.sort(reverse=True)
                # First piece of evidence is full strength (TRUE INDEPENDENT CONFIRMATION)
                # Subsequent evidence from same root is diminished (SAME FACT REPEATED)
                for i, s in enumerate(scores):
                    total += s / (2 ** i) 
            return total

        sup_score = calculate_diminished_score(supporting)
        con_score = calculate_diminished_score(contradicting)
        
        total_score = sup_score + con_score
        if total_score == 0:
            return {
                "status": "NO_DATA",
                "convergence_ratio": 0.0,
                "supporting_score": 0.0,
                "contradicting_score": 0.0,
                "summary": "No significant evidence found for this domain."
            }
            
        ratio = sup_score / total_score
        
        if ratio > 0.8:
            status = "STRONG_CONVERGENCE_POSITIVE"
            summary = "Multiple independent indicators strongly agree on a positive outcome."
        elif ratio > 0.6:
            status = "WEAK_CONVERGENCE_POSITIVE"
            summary = "Most indicators lean positive, but some friction or dependency exists."
        elif ratio < 0.2:
            status = "STRONG_CONVERGENCE_NEGATIVE"
            summary = "Multiple independent indicators strongly agree on a challenging/negative outcome."
        elif ratio < 0.4:
            status = "WEAK_CONVERGENCE_NEGATIVE"
            summary = "Most indicators lean negative, but some protective factors exist."
        else:
            status = "CONTRADICTION"
            summary = "Significant contradictions exist. The outcome will likely be mixed or delayed."
            
        return {
            "status": status,
            "convergence_ratio": round(ratio, 2),
            "supporting_score": round(sup_score, 2),
            "contradicting_score": round(con_score, 2),
            "summary": summary
        }
