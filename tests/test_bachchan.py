import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from astrology_engine import calculate_chart_with_object
from rectification_engine import RectificationEngine
from event_analysis import EventPredictionEngine
from user_memory_engine import ContextMemoryEngine

# Amitabh Bachchan: Oct 11, 1942, 16:00 IST, Allahabad (25.4358 N, 81.8463 E)
lat, lon = 25.4358, 81.8463
chart, payload = calculate_chart_with_object(1942, 10, 11, 16, 0, lat, lon, "Asia/Kolkata", 0)

print("=== AMITABH BACHCHAN NATAL CHART ===")
asc = payload['Basic_Chart']['Ascendant']
print(f"Lagna (Ascendant): {asc['sign']} at {asc['degree']:.2f} deg ({asc['nakshatra']})")

print("\nPlanetary Placements:")
for p_name, p_data in payload['Basic_Chart'].items():
    if p_name in ['sarvashtakavarga', 'bhava_bala', 'Ascendant']: continue
    print(f"  {p_name:10s} : {p_data['sign']:12s} in House {p_data['house']:2d} | Dignity: {p_data['dignity']}")

print("\nCanonical Yogas:")
for y in payload['Yogas_Found'][:6]:
    print(f"  - {y.get('name') or y.get('yoga_name')}")
