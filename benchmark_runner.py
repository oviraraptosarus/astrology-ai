"""
Real-world Astronomical & Astrological Benchmark Test Runner (Phase 16, 17, 18, 19).
Runs BLIND analysis against historical individuals, calculates scores for
Event Domain Match, Timing Match, and False Positives.
"""

from typing import Dict, List, Any
import json
from datetime import datetime
import pytz

from astrology_engine import calculate_chart_with_object
from forward_timing_scanner import ForwardTimingScanner
from uncertainty_engine import UncertaintyEngine

BENCHMARK_CASES = {
    "STEVE_JOBS": {
        "birth_data": {
            "year": 1955, "month": 2, "day": 24, "hour": 19, "minute": 15,
            "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles", "city": "San Francisco"
        },
        "quality": "Rodden AA",
        "ground_truth_events": [
            {"date": "1985-09-16", "domain": "CAREER", "event": "Resigned from Apple / Found NeXT", "severity": "HIGH"},
            {"date": "1997-07-04", "domain": "CAREER", "event": "Return to Apple as interim CEO", "severity": "HIGH"},
            {"date": "2006-01-24", "domain": "WEALTH", "event": "Sale of Pixar to Disney ($7.4B)", "severity": "HIGH"},
            {"date": "2004-07-31", "domain": "HEALTH_ACCIDENT", "event": "Pancreatic cancer surgery", "severity": "CRITICAL"},
            {"date": "2011-10-05", "domain": "HEALTH_ACCIDENT", "event": "Death", "severity": "FATAL"}
        ]
    },
    "ELON_MUSK": {
        "birth_data": {
            "year": 1971, "month": 6, "day": 28, "hour": 7, "minute": 30,
            "lat": -25.7479, "lon": 28.2293, "tz": "Africa/Johannesburg", "city": "Pretoria"
        },
        "quality": "Rodden B",
        "ground_truth_events": [
            {"date": "2002-10-03", "domain": "WEALTH", "event": "PayPal sold to eBay ($1.5B)", "severity": "HIGH"},
            {"date": "2008-09-28", "domain": "CAREER", "event": "SpaceX Falcon 1 Flight 4 success (Saved company)", "severity": "HIGH"},
            {"date": "2000-12-15", "domain": "HEALTH_ACCIDENT", "event": "Severe falciparum malaria (Near-fatal)", "severity": "CRITICAL"}
        ]
    }
}

class BenchmarkRunner:
    @staticmethod
    def run_case_blind(case_name: str, test_domain: str, start_year: int, scan_years: int = 10) -> Dict[str, Any]:
        """Runs the ForwardTimingScanner BLIND across the requested domain."""
        case = BENCHMARK_CASES[case_name]
        bd = case["birth_data"]
        
        # 1. Calculate Core Astronomy
        chart, _ = calculate_chart_with_object(
            bd["year"], bd["month"], bd["day"], bd["hour"], bd["minute"],
            bd["lat"], bd["lon"], bd["tz"], name=case_name
        )
        
        # 2. Setup Scanner
        scanner = ForwardTimingScanner(chart)
        start_dt = pytz.utc.localize(datetime(start_year, 1, 1))
        
        # 3. Predict Blind
        predicted_windows = scanner.scan_domain_windows(test_domain, start_dt, months_ahead=scan_years*12)
        
        return {
            "case": case_name,
            "domain_tested": test_domain,
            "blind_predictions": predicted_windows
        }
        
    @staticmethod
    def grade_predictions(case_name: str, domain: str, blind_predictions: List[Dict]) -> Dict[str, Any]:
        case = BENCHMARK_CASES[case_name]
        truths = [t for t in case["ground_truth_events"] if t["domain"] == domain]
        
        results = []
        for truth in truths:
            truth_dt = datetime.fromisoformat(truth["date"])
            match_found = False
            for p in blind_predictions:
                p_start = datetime.fromisoformat(p["macro_window_start"])
                p_end = datetime.fromisoformat(p["macro_window_end"])
                # Evaluate Window Overlap
                if p_start <= truth_dt <= p_end:
                    match_found = True
                    results.append({
                        "event": truth["event"],
                        "actual_date": truth["date"],
                        "status": "HIT",
                        "predicted_window": f"{p['macro_window_start']} to {p['macro_window_end']}",
                        "reliability_class": p.get("reliability_metrics", {}).get("reliability_class", "UNKNOWN"),
                        "sensitivity": p.get("reliability_metrics", {}).get("birth_time_sensitivity", "UNKNOWN")
                    })
                    break
            if not match_found:
                results.append({
                    "event": truth["event"],
                    "actual_date": truth["date"],
                    "status": "MISS (False Negative)"
                })
                
        # Calculate False Positives (Predicted windows that hit nothing)
        matched_predictions = [r["predicted_window"] for r in results if r["status"] == "HIT"]
        false_positives = [p for p in blind_predictions if f"{p['macro_window_start']} to {p['macro_window_end']}" not in matched_predictions]
        
        return {
            "total_ground_truth": len(truths),
            "hits": sum(1 for r in results if r["status"] == "HIT"),
            "misses": sum(1 for r in results if "MISS" in r["status"]),
            "false_positives": len(false_positives),
            "details": results
        }

if __name__ == "__main__":
    print("=== DUAL-TRACK BLIND BENCHMARK TESTING ===")
    
    for case_id in ["STEVE_JOBS", "ELON_MUSK"]:
        for dom, sy, ty in [("CAREER", 1980, 25), ("WEALTH", 1995, 20), ("HEALTH_ACCIDENT", 1995, 20)]:
            print(f"\\nEvaluating {case_id} | Domain: {dom} | Window: {sy}-{sy+ty}")
            
            # Step 1: Blind Generation
            blind = BenchmarkRunner.run_case_blind(case_id, dom, sy, ty)
            
            # Step 2: Scoring 
            score = BenchmarkRunner.grade_predictions(case_id, dom, blind["blind_predictions"])
            print(f"  Accuracy Score: {score['hits']}/{score['total_ground_truth']} Hits | False Positives: {score['false_positives']}")
            for entry in score["details"]:
                print(f"    - Event: {entry['event']} ({entry['actual_date']}) -> {entry['status']}")
                if entry["status"] == "HIT":
                    print(f"      (Predicted: [ {entry['predicted_window']} ] | Class: {entry.get('reliability_class')} | Sensitivity: {entry.get('sensitivity')})")
