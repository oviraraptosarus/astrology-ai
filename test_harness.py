import json
from astrology_engine import calculate_full_chart, get_semantic_view

class ExpertTestHarness:
    def __init__(self):
        self.cases = []
        
    def add_case(self, name: str, year: int, month: int, day: int, hour: int, minute: int, lat: float, lon: float, domain: str, expected_outcome: str):
        self.cases.append({
            "name": name,
            "birth_data": (year, month, day, hour, minute, lat, lon),
            "domain": domain,
            "expected_outcome": expected_outcome
        })
        
    def run_all(self):
        results = []
        for case in self.cases:
            print(f"\nEvaluating Case: {case['name']} - Domain: {case['domain']}")
            chart_dict = calculate_full_chart(*case['birth_data'])
            semantic_view_json = get_semantic_view(chart_dict, case['domain'])
            
            packet = {
                "case_name": case['name'],
                "expected_outcome": case['expected_outcome'],
                "engine_reasoning": json.loads(semantic_view_json)
            }
            results.append(packet)
            
            # Print a brief summary
            confidence = packet['engine_reasoning'].get('confidence', 'UNKNOWN')
            timing = packet['engine_reasoning'].get('timing_status', 'UNKNOWN')
            print(f"  Confidence: {confidence}")
            print(f"  Timing Status: {timing}")
            print(f"  Support Count: {len(packet['engine_reasoning'].get('supporting_indications', []))}")
            print(f"  Contradiction Count: {len(packet['engine_reasoning'].get('contradicting_indications', []))}")
            
        return results

if __name__ == '__main__':
    harness = ExpertTestHarness()
    # Steve Jobs
    harness.add_case("Steve Jobs", 1955, 2, 24, 19, 15, 37.7749, -122.4194, "business", "Billionaire tech founder")
    
    all_results = harness.run_all()
    with open("harness_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    print("\nAll cases evaluated. Results saved to harness_results.json")
