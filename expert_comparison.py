import json

class ExpertComparisonMode:
    def __init__(self, engine_output: dict, expert_review: dict):
        self.engine = engine_output
        self.expert = expert_review
        
    def generate_comparison(self):
        engine_confidence = self.engine.get("confidence", "UNKNOWN")
        expert_confidence = self.expert.get("confidence", "UNKNOWN")
        
        engine_support = set(self.engine.get("reasoning_trace", {}).get("SUPPORT", []))
        expert_support = set(self.expert.get("reasoning", []))
        
        agreements = engine_support.intersection(expert_support)
        missing_from_engine = expert_support - engine_support
        hallucinated_by_engine = engine_support - expert_support
        
        return {
            "Confidence_Match": engine_confidence == expert_confidence,
            "Agreements": list(agreements),
            "Missing_Factors_in_Engine": list(missing_from_engine),
            "Engine_False_Positives": list(hallucinated_by_engine)
        }

if __name__ == '__main__':
    # Mock test
    mock_engine = {
        "confidence": "STRONG",
        "reasoning_trace": {
            "SUPPORT": ["Gaja Kesari Yoga is technically present. Significance: STRONG."]
        }
    }
    mock_expert = {
        "confidence": "STRONG",
        "reasoning": ["Gaja Kesari Yoga is technically present. Significance: STRONG.", "10th lord is strong in D10"]
    }
    
    comparer = ExpertComparisonMode(mock_engine, mock_expert)
    print(json.dumps(comparer.generate_comparison(), indent=2))
