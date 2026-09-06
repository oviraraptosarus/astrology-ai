import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from datetime import datetime
from kp_engine import KPEngine
from rectification_engine import RectificationEngine

LAT, LON, TZ = 16.8667, 81.9333, "Asia/Kolkata"

# The real rules of KP that the engine missed:
EVENT_RULES = {
    "career_job": {"primary": 10, "supporting": [2, 6, 10, 11]},
    "marriage": {"primary": 7, "supporting": [2, 7, 11]},
    "property_purchase": {"primary": 4, "supporting": [4, 11, 12]}
}

def score_kp_properly(time_to_test):
    kp = KPEngine.calculate_kp_chart(time_to_test.year, time_to_test.month, time_to_test.day, 
                                     time_to_test.hour, time_to_test.minute, LAT, LON, TZ)
    abcd = kp["abcd_significators"]
    
    total = 0
    print(f"\n--- EVALUATING {time_to_test.strftime('%H:%M')} ---")
    for ev, rules in EVENT_RULES.items():
        primary = rules["primary"]
        supporting = rules["supporting"]
        
        csl = kp["cusps"][primary - 1]["sub_lord"]
        
        # Check if CSL signifies supporting houses
        best_score = 0.0
        for h in supporting:
            sig = abcd.get(str(h), {})
            if csl in sig.get("level_a", []): best_score = max(best_score, 1.0)
            elif csl in sig.get("level_b", []): best_score = max(best_score, 0.85)
            elif csl in sig.get("level_c", []): best_score = max(best_score, 0.7)
            elif csl in sig.get("level_d", []): best_score = max(best_score, 0.6)
            
        print(f"Event: {ev:18s} | Primary CSL (H{primary}): {csl:7s} | Max Sig in {supporting}: {best_score}")
        total += best_score
        
    print(f"TOTAL KP SCORE: {total}")

score_kp_properly(datetime(1975, 5, 6, 7, 15))  # Taurus
score_kp_properly(datetime(1975, 5, 6, 8, 59))  # Gemini
