import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from astrology_engine import calculate_chart_with_object
from jaimini_arudha_argala_engine import JaiminiArudhaArgalaEngine
from navatara_chakra_engine import NavataraChakraEngine
from gochara_vedha_engine import GocharaVedhaEngine

print("=" * 70)
print("TEST: TIER 4 ADVANCED MASTER ENGINES (MANDAPETA 1975 CHART)")
print("=" * 70)
chart_m, _ = calculate_chart_with_object(1975, 5, 6, 7, 15, 16.8667, 81.9333, "Asia/Kolkata", 0)

# 1. Arudha & Argala
arudha_eng = JaiminiArudhaArgalaEngine(chart_m)
padas = arudha_eng.calculate_all_padas()
print(f"Calculated {len(padas)} Arudha Padas:")
for k, v in list(padas.items())[:4]:
    print(f"  {v['pada_code']} ({v['pada_name']}): {v['pada_sign']} -> {v['significance']}")

argala_10 = arudha_eng.evaluate_argala_on_house(10)
print(f"\nArgala Interventions on 10th House (Career): {len(argala_10['argalas'])} active")

# 2. Navatara
nava_eng = NavataraChakraEngine(chart_m)
transit_tara = nava_eng.evaluate_transit_moon_tara(datetime.now())
print(f"\nLive Moon Tara Bala: {transit_tara['tara_details']['tara_name']} ({transit_tara['tara_details']['nature']}) -> {transit_tara['action_timing_verdict']}")

# 3. Gochara Vedha
vedha_eng = GocharaVedhaEngine(chart_m)
vedha_res = vedha_eng.evaluate_all_transits(datetime.now())
print(f"\nLive Gochara Vedha Status:")
for pname in ['Jupiter', 'Saturn', 'Mars']:
    v = vedha_res['transit_evaluations'][pname]
    print(f"  {pname} in H{v['transit_house_from_moon']} ({v['transit_sign']}): {v['verdict']}")
