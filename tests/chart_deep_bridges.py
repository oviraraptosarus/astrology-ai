import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from astrology_engine import calculate_chart_with_object

lat, lon = 16.8667, 81.9333
chart, payload = calculate_chart_with_object(1975, 5, 6, 7, 15, lat, lon, "Asia/Kolkata", 0)

print("--- FULL PLANETARY STATUS ---")
for name, p in chart.planets.items():
    print(f"{name:10s}: Sign={p.sign:12s} House={p.house:2d} Owns={p.owns_houses} Dig={p.dignity:10s} DigBala={getattr(p, 'dig_bala', 0):.2f}")

print("\n--- ALL HOUSES & OCCUPANTS ---")
house_occupants = {i: [] for i in range(1, 13)}
for name, p in chart.planets.items():
    if name != "Ascendant":
        house_occupants[p.house].append(name)

for h in range(1, 13):
    lord = next((p.name for p in chart.planets.values() if h in p.owns_houses), "Unknown")
    occ = ", ".join(house_occupants[h]) if house_occupants[h] else "Empty"
    print(f"House {h:2d}: Sign={chart.houses[h-1].sign:12s} Lord={lord:8s} Occupants=[{occ}]")
