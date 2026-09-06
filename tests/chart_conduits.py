import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from astrology_engine import calculate_chart_with_object

lat, lon = 16.8667, 81.9333
chart, payload = calculate_chart_with_object(1975, 5, 6, 7, 15, lat, lon, "Asia/Kolkata", 0)

planets = chart.planets

print("=== COMPLETE DISPOSITOR & CONDUIT NETWORK ===")
# Let's map every planet's placement, lordship, and aspect targets
aspect_rules = {
    "Sun": [7],
    "Moon": [7],
    "Mars": [4, 7, 8],
    "Mercury": [7],
    "Jupiter": [5, 7, 9],
    "Venus": [7],
    "Saturn": [3, 7, 10],
    "Rahu": [5, 7, 9],
    "Ketu": [5, 7, 9]
}

for name, p in planets.items():
    if name == "Ascendant": continue
    aspected_houses = [((p.house - 1 + offset) % 12) + 1 for offset in aspect_rules.get(name, [7])]
    print(f"{name:8s} in H{p.house:2d} (Lord of {p.owns_houses}) -> Aspects Houses: {aspected_houses}")
