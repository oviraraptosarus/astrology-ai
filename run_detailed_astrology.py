import sys
import json
sys.path.insert(0, r"E:\ASTROLOGY AI")

from advanced_avasthas import AdvancedAvasthaEngine
from ashtakavarga_engine import AshtakavargaEngine
from bhrigu_nandi_nadi_engine import BhriguNandiNadiEngine
from compatibility_engine import CompatibilityEngine
import astrology_engine

# Calculate chart object
chart_a = astrology_engine.calculate_chart_with_object(
    year=2008, month=4, day=5,
    hour=6, minute=15,
    lat=50.3480, lon=18.9328,
    tz_name='Europe/Warsaw'
)

# Advanced Avasthas
avastha_eng = AdvancedAvasthaEngine(chart_a)
avastha_res = avastha_eng.calculate_all_avasthas()

# Ashtakavarga Engine
av_eng = AshtakavargaEngine(chart_a)
av_res = av_eng.calculate()

# Bhrigu Nandi Nadi
bnn_eng = BhriguNandiNadiEngine(chart_a)
bnn_res = bnn_eng.analyze()

print("=== AVASTHAS RESULTS ===")
for p, data in avastha_res.items():
    print(f"Planet {p}: {data}")

print("\n=== ASHTAKAVARGA REDUCTIONS ===")
print("Trikona / Ekadhipatya:", av_res)

print("\n=== BHRIGU NANDI NADI ===")
print("BNN:", json.dumps(bnn_res, indent=2, default=str))

# Check shadbala from ania_full_chart.json
with open("E:/ASTROLOGY AI/ania_full_chart.json", "r", encoding="utf-8") as f:
    full_c = json.load(f)

print("\n=== YOGAS DETECTED ===")
for y in full_c.get("yogas", []):
    print(f"- {y.get('name')}: {y.get('description', '')[:120]}")

print("\n=== SHADBALA ===")
for p, sb in full_c.get("shadbala", {}).items():
    print(f"- {p}: total={sb.get('total_points')} (rank: {sb.get('rank', '')}), ishta={sb.get('ishta_phala')}, kashta={sb.get('kashta_phala')}")

print("\n=== BHAVA BALA ===")
for h, bb in full_c.get("bhava_bala", {}).items():
    print(f"- House {h}: {bb}")
