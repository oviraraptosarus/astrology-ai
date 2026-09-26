import sys
import json
sys.path.insert(0, r"E:\ASTROLOGY AI")

from advanced_avasthas import AdvancedAvasthaEngine
import astrology_engine

chart_obj, chart_dict = astrology_engine.calculate_chart_with_object(
    year=2008, month=4, day=5,
    hour=6, minute=15,
    lat=50.3480, lon=18.9328,
    tz_name='Europe/Warsaw'
)

avastha_eng = AdvancedAvasthaEngine(chart_obj)

print("=== PLANETARY POSITIONS ===")
for name, p in chart_obj.planets.items():
    s = getattr(p, 'speed', 0.0)
    r = getattr(p, 'retrograde', False)
    c = getattr(p, 'combust', False)
    print(f"  {p.name:7s}: sign={p.sign:12s} deg={p.degree:7.4f}° house={p.house:2d} nak={p.nakshatra:18s} speed={s:7.4f} retro={r} combust={c}")

print("\n=== BALAADI AVASTHAS ===")
for name, p in chart_obj.planets.items():
    print(f"  {name:7s}: {avastha_eng.calculate_balaadi_avastha(p)}")

print("\n=== DEEPTADI AVASTHAS ===")
for name, p in chart_obj.planets.items():
    print(f"  {name:7s}: {avastha_eng.calculate_deeptadi_avastha(p)}")

print("\n=== JAGRADADI AVASTHAS ===")
for name, p in chart_obj.planets.items():
    print(f"  {name:7s}: {avastha_eng.calculate_jagradadi_avastha(p)}")

print("\n=== LAJJITADI AVASTHAS ===")
for item in avastha_eng.evaluate_lajjitadi_avasthas():
    print(f"  {item}")

print("\n=== YOGAS IN CHART ===")
for y in chart_dict.get("yogas", []):
    print(f"  - {y.get('name')}: {y.get('description')}")

print("\n=== SHADBALA ===")
for p_name, sb in chart_dict.get("shadbala", {}).items():
    print(f"  {p_name:7s}: total={sb.get('total_points', 0):.2f}, ishta={sb.get('ishta_phala', 0):.2f}, kashta={sb.get('kashta_phala', 0):.2f}")
