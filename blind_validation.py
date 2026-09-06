import json
import os
from datetime import datetime
from astrology_engine import calculate_full_chart
from event_analysis import EventPredictionEngine

class BlindValidationFramework:
    def __init__(self, dataset_dir="data/cases"):
        self.dataset_dir = dataset_dir
        os.makedirs(self.dataset_dir, exist_ok=True)
        
        self.splits = ["train", "validation", "test"]
        for split in self.splits:
            os.makedirs(os.path.join(self.dataset_dir, split), exist_ok=True)

    def add_case(self, split: str, case_id: str, case_data: dict):
        if split not in self.splits:
            raise ValueError(f"Invalid split {split}")
        file_path = os.path.join(self.dataset_dir, split, f"{case_id}.json")
        with open(file_path, "w") as f:
            json.dump(case_data, f, indent=2)

    def run_blind_evaluation(self, split: str):
        split_dir = os.path.join(self.dataset_dir, split)
        results = []
        
        if not os.path.exists(split_dir):
            return results
            
        for filename in os.listdir(split_dir):
            if not filename.endswith(".json"):
                continue
                
            file_path = os.path.join(split_dir, filename)
            with open(file_path, "r") as f:
                case = json.load(f)
                
            print(f"Running BLIND EVALUATION on {case.get('case_id', filename)}...")
            
            # We evaluate WITHOUT exposing the outcome
            birth_data = case["birth_data"] # year, month, day, hour, minute, lat, lon
            # Handle variable length birth_data tuples gracefully
            chart = calculate_full_chart(*birth_data[:6]) if len(birth_data) == 6 else calculate_full_chart(*birth_data[:7])
            
            engine = EventPredictionEngine(chart)
            # Simulated target date for the event evaluation
            target_date = datetime.utcnow()
            
            analysis = engine.analyze_event(f"Will the native experience success in {case['domain']}?", target_date)
            
            results.append({
                "case_id": case.get("case_id", filename),
                "domain": case["domain"],
                "engine_prediction": analysis.llm_guidance,
                "actual_outcome": case["outcome"] # only appended AT THE END for comparison
            })
            
        return results

if __name__ == '__main__':
    framework = BlindValidationFramework()
    # Add a mock test case (Steve Jobs proxy)
    framework.add_case("test", "case_001", {
        "case_id": "case_001",
        "birth_data": [1955, 2, 24, 19, 15, 37.7749, -122.4194],
        "domain": "CAREER",
        "outcome": "Massive global tech success"
    })
    
    eval_results = framework.run_blind_evaluation("test")
    print(f"Evaluated {len(eval_results)} blind cases.")

