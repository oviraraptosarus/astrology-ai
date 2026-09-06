import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from astrology_engine import calculate_chart_with_object
from pushkara_engine import PushkaraEngine
from wealth_lagnas_engine import WealthLagnasEngine
from kp_interlinks_engine import KPCuspalInterlinksEngine

print("=" * 70)
print("TEST: TIER 3 ADVANCED MASTER ENGINES (AMITABH BACHCHAN 1942)")
print("=" * 70)
chart_ab, _ = calculate_chart_with_object(1942, 10, 11, 16, 0, 25.4358, 81.8463, "Asia/Kolkata", 0)

# 1. Pushkara
push_eng = PushkaraEngine(chart_ab)
push_res = push_eng.evaluate_all_planets()
print(f"Total Pushkara Blessings : {push_res['total_pushkara_blessings']} -> Rating: {push_res['resilience_rating']}")
for pname, pdata in push_res['evaluations'].items():
    if pdata['is_pushkara_navamsha'] or pdata['is_pushkara_bhaga']:
        print(f"  * {pname} in {pdata['sign']} ({pdata['degree_in_sign']} deg): {pdata['status']}")

# 2. Wealth Lagnas
wealth_eng = WealthLagnasEngine(chart_ab)
special_lagnas = wealth_eng.calculate_special_lagnas()
indu = special_lagnas['indu_lagna']
print(f"\nIndu Lagna Sign          : {indu['indu_lagna_sign']}")
print(f"Indu Lagna Planets       : {indu['planets_in_indu_lagna']}")
print(f"Financial Verdict        : {indu['financial_magnitude_verdict']}")
print(f"Ghatika Lagna (Power)    : {special_lagnas['ghatika_lagna']['sign']}")
print(f"Shree Lagna (Lakshmi)    : {special_lagnas['shree_lagna']['sign']}")

# 3. KP Interlinks
kp_eng = KPCuspalInterlinksEngine(chart_ab)
promises = kp_eng.evaluate_cuspal_promises()
print(f"\nKP Cuspal Interlinks Gating Sample:")
for cname in ['Cusp_10_Career_&_Executive_Status', 'Cusp_7_Marriage_&_Partnership', 'Cusp_2_Wealth_Accumulation']:
    p = promises.get(cname, {})
    print(f"  {p.get('domain_name')}: CSL = {p.get('cusp_sub_lord')} -> Gate: {p.get('gate_status')} ({p.get('astrological_verdict')})")
