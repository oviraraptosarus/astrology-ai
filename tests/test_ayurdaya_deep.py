import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from astrology_engine import calculate_chart_with_object
from longevity_engine import LongevityEngine

lat, lon = 25.4358, 81.8463
chart, payload = calculate_chart_with_object(1942, 10, 11, 16, 0, lat, lon, "Asia/Kolkata", 0)

print("=== JAIMINI 3-PAIR AYURDAYA CALCULATION ===")
span = LongevityEngine.calculate_jaimini_longevity_span(chart)
print(f"Longevity Category : {span['bracket']}")
print(f"Classical Span     : {span['estimated_range']}")
print("Pair Breakdown     :")
for k, v in span['pair_evaluations'].items():
    print(f"  - {k:25s}: {v}")

print("\n=== COMPLETE 4-TIER MARAKA & VULNERABILITY MATRIX ===")
marakas = LongevityEngine.identify_marakas(chart)
for k, v in marakas.items():
    print(f"  {k:30s}: {v}")
