import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from astrology_engine import calculate_chart_with_object
from dasha_engine import DashaEngine
from longevity_engine import LongevityEngine

lat, lon = 25.4358, 81.8463
chart, payload = calculate_chart_with_object(1942, 10, 11, 16, 0, lat, lon, "Asia/Kolkata", 0)

dasha = payload.get("Current_Dasha", {})
print("Current Dasha:", dasha)

marakas = LongevityEngine.identify_marakas(chart)
print("Identified Marakas for Aquarius Lagna:", marakas)
