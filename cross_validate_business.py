import sys, os
sys.path.insert(0, "E:/ASTROLOGY AI")
from datetime import datetime
import json
from astrology_engine import calculate_chart_with_object
from dasha_engine import DashaEngine
from jaimini_chara_dasha_engine import JaiminiCharaDashaEngine
from yogini_dasha_engine import YoginiDashaEngine
from forward_timing_scanner import ForwardTimingScanner
from kp_engine import KPEngine
from varga_engine import VargaEngine

chart, chart_dict = calculate_chart_with_object(2008, 8, 1, 18, 25, 16.8185549, 82.0641497, tz_name='Asia/Kolkata')
chart.birth_time = datetime(2008, 8, 1, 12, 55)

moon_p = chart.planets['Moon']
ZODIAC = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']
moon_abs = ZODIAC.index(moon_p.sign)*30 + moon_p.degree

print("=== 1. VIMSHOTTARI (Dasha Engine) ===")
tl = DashaEngine.calculate_vimshottari_timeline(datetime(2008,8,1,12,55), moon_abs)
for md in tl:
    st = md['start'][:10]; en = md['end'][:10]
    if "2025" in st or "2026" in st or "2027" in st:
        print(f"MD {md['lord']:7s} {st} -> {en}")
        for ad in md.get('sub_periods',[]):
            ast = ad['start'][:10]; aen = ad['end'][:10]
            if any(y in ast or y in aen for y in ["2025","2026","2027"]):
                print(f"  AD {ad['lord']:7s} {ast} -> {aen}")

print("\n=== 2. JAIMINI CHARA DASHA ===")
jcd = JaiminiCharaDashaEngine.calculate_chara_dasha_timeline(chart, datetime(2008,8,1,12,55))
for cd in jcd:
    st = str(cd.get('start',''))[:10]; en = str(cd.get('end',''))[:10]
    if any(y in st or y in en for y in ["2025","2026","2027","2028"]):
        print(f"Sign {cd.get('sign'):12s} {st} -> {en} | Planets: {cd.get('planets')} | Activations: {cd.get('special_activations')}")

print("\n=== 3. YOGINI DASHA ===")
yd = YoginiDashaEngine.calculate_yogini_timeline(datetime(2008,8,1,12,55), moon_abs)
for y in yd:
    st = str(y.get('start',''))[:10]; en = str(y.get('end',''))[:10]
    if any(yr in st or yr in en for yr in ["2025","2026","2027","2028","2029","2030"]):
        print(f"Yogini {y.get('yogini'):10s} Lord:{y.get('lord'):7s} {st} -> {en} | {y.get('impact_archetype','')}")

print("\n=== 4. KP CROSS-VALIDATION (Business-relevant cusps) ===")
kp = KPEngine.calculate_kp_chart(2008,8,1,18,25,16.8185549,82.0641497,'Asia/Kolkata')
# 10th cusp (career/business) and 2nd cusp (wealth) and 11th cusp (gains)
for h in [2,10,11]:
    for c in kp.get('cusps',[]):
        if c.get('house')==h:
            print(f"House {h}: {c['sign']} {c['degree']:.2f}° | SignLord:{c['sign_lord']} StarLord:{c['star_lord']} SubLord:{c['sub_lord']} SubSub:{c['sub_sub_lord']}")

print("\n=== 5. DIVISIONAL D10 (Business) + D2 (wealth) + D9 (spouse/partnership) ===")
for name, fn in [("D10",VargaEngine.calc_d10_dasamsha),("D2",VargaEngine.calc_d2_hora),("D9",VargaEngine.calc_d9_navamsha)]:
    asc = fn(chart.ascendant_sign, chart.ascendant_degree)
    print(f"\n{name}: Asc={asc}")
    for p,pl in chart.planets.items():
        ps = fn(pl.sign, pl.degree)
        print(f"  {p:7s}: {ps}")
