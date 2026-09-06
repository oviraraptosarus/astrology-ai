import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from astrology_engine import calculate_chart_with_object

lat, lon = 16.8667, 81.9333

for h, m in [(7, 7), (7, 15), (7, 39)]:
    c, p = calculate_chart_with_object(1975, 5, 6, h, m, lat, lon, "Asia/Kolkata", 0)
    asc = p['Basic_Chart']['Ascendant']
    print(f"{h:02d}:{m:02d} -> Lagna: {asc['sign']} at {asc['degree']:.2f} deg | Nakshatra: {asc['nakshatra']}")
