import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from astrology_engine import calculate_chart_with_object
from event_analysis import EventPredictionEngine
from methodology_router import MethodologyRouter

lat, lon = 16.8667, 81.9333
chart, payload = calculate_chart_with_object(1975, 5, 6, 7, 15, lat, lon, "Asia/Kolkata", 0)

# Check all domains available in router
print("Available Domains in System:")
for d, kws in MethodologyRouter.DOMAINS.items():
    print(f"  - {d:15s} : {kws[:4]}...")

# Check Dispositor Links / Cross-Domain Bridges
print("\n--- CROSS-DOMAIN RIPPLE BRIDGES FOR TAURUS LAGNA (7:15 AM) ---")
planets = chart.planets

# 1. Career (10H) <-> Marriage (7H)
mars = planets.get("Mars")
print(f"Bridge 1: Marriage <-> Career: 7th Lord Mars sits in House {mars.house} with Moon (3rd Lord).")
print("  => Spousal relationship and independent career are functionally tied together.")

# 2. Wealth (2H) <-> Real Estate (4H) <-> Self (1H)
saturn = planets.get("Saturn")
venus = planets.get("Venus")
merc = planets.get("Mercury")
print(f"Bridge 2: Wealth <-> Real Estate <-> Self: Lagna Lord Venus & Yogakaraka Saturn (9L/10L) sit in House {venus.house} (Gemini).")
print(f"  => 2nd Lord Mercury sits in House {merc.house} (Taurus Lagna). Mutual reception/exchange energy.")
print("  => Career and reputation generate direct wealth accumulation that gets locked into physical assets.")

# 3. Children (5H) <-> Gains (11H)
jup = planets.get("Jupiter")
print(f"Bridge 3: Children <-> Gains: Karaka Jupiter in House {jup.house} (Pisces - Own Sign) aspects 5th House of Children directly.")
print("  => High intelligence, strong moral lineage, and children act as long-term wealth anchors.")
