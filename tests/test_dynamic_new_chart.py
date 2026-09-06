import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from astrology_engine import calculate_chart_with_object
from event_analysis import EventPredictionEngine

# Test an entirely new chart: Oct 24, 1992, 18:45 IST, New Delhi (28.6139 N, 77.2090 E)
lat, lon = 28.6139, 77.2090
new_chart, payload = calculate_chart_with_object(1992, 10, 24, 18, 45, lat, lon, "Asia/Kolkata", 0)

print("=== NEW CHART PROCESSED DYNAMICALLY ===")
asc = payload['Basic_Chart']['Ascendant']
print(f"1. Ascendant Calculated: {asc['sign']} at {asc['degree']:.2f} deg ({asc['nakshatra']})")

print("\n2. Planetary Dignities & Placements:")
for p_name, p_data in payload['Basic_Chart'].items():
    if p_name in ['sarvashtakavarga', 'bhava_bala', 'Ascendant']: continue
    print(f"   {p_name:10s} : {p_data['sign']:12s} in House {p_data['house']:2d} | Dignity: {p_data['dignity']}")

print("\n3. Yogas Automatically Detected:")
for y in payload['Yogas_Found'][:5]:
    print(f"   - {y.get('name') or y.get('yoga_name')}")

engine = EventPredictionEngine(new_chart)
res_career = engine.analyze_event("How will my career and business be?", datetime.now())
print(f"\n4. Dynamic Domain Evaluation (Career/Business):")
print(f"   Natal Promise Status: {res_career.natal_promise['status']}")
print(f"   Supporting Evidence Count: {len(res_career.natal_promise['supporting_evidence'])}")
print(f"   Timing Window Status: {res_career.activation['timing_status']}")
print(f"   Transits Activating Houses: {res_career.timing['activated_natal_houses']}")
