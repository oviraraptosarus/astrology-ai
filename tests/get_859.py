import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from astrology_engine import calculate_chart_with_object
import json

chart, chart_dict = calculate_chart_with_object(1975, 5, 6, 8, 59, 16.8667, 81.9333, "Asia/Kolkata", "GeminiPerson")

print("ASCENDANT:", chart.ascendant_sign, chart.ascendant_degree)
planets = chart.planets
for p in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
    if p in planets:
        obj = planets[p]
        print(f"{p:7s}: {obj.sign:12s} (House {obj.house}) - Dignity: {obj.dignity}")
