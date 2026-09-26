import sys
import os
sys.path.insert(0, "E:/ASTROLOGY AI")
from datetime import datetime
import json
from astrology_engine import calculate_chart_with_object
from dasha_engine import DashaEngine
from varga_engine import VargaEngine
from jaimini_engine import JaiminiEngine
from kp_engine import KPEngine
from wealth_lagnas_engine import WealthLagnasEngine
from sensitive_points import SensitivePointsEngine
from ashtakavarga_engine import AshtakavargaEngine
from jaimini_chara_dasha_engine import JaiminiCharaDashaEngine
from yogini_dasha_engine import YoginiDashaEngine
# from tajika_engine import TajakaEngine
# from realtime_engine import RealtimeEngine

ZODIAC = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

chart, chart_dict = calculate_chart_with_object(2008, 8, 1, 18, 25, 16.8185549, 82.0641497, tz_name='Asia/Kolkata')

print("=== 1. NATAL D1 POSITIONS ===")
print(f"Ascendant: {chart.ascendant_sign} {chart.ascendant_degree:.4f}°")
for p, pl in chart.planets.items():
    retro = getattr(pl, 'is_retrograde', False)
    combust = getattr(pl, 'is_combust', False)
    print(f"{p:7s}: {pl.sign:11s} {pl.degree:7.4f}° | House {pl.house:2d} | Nak: {pl.nakshatra:14s} P{pl.nakshatra_pada} | Lord: {pl.nakshatra_lord} | Retro: {retro} | Combust: {combust}")

print("\n=== 2. DIVISIONAL CHARTS (VARGAS) ===")
# Let's inspect D9, D10, D24, D2, D4, D7, D60
for v_name, v_func in [
    ("D9 Navamsha", VargaEngine.calc_d9_navamsha),
    ("D10 Dasamsha", VargaEngine.calc_d10_dasamsha),
    ("D24 Chaturvimshamsha", VargaEngine.calc_d24_chaturvimshamsha),
    ("D2 Hora", VargaEngine.calc_d2_hora),
    ("D4 Chaturthamsha", VargaEngine.calc_d4_chaturthamsha),
    ("D7 Saptamsha", VargaEngine.calc_d7_saptamsha),
    ("D60 Shashtiamsha", VargaEngine.calc_d60_shashtiamsha)
]:
    print(f"\n--- {v_name} ---")
    asc_sign = v_func(chart.ascendant_sign, chart.ascendant_degree)
    print(f" Ascendant: {asc_sign}")
    for p, pl in chart.planets.items():
        psign = v_func(pl.sign, pl.degree)
        print(f"  {p:7s}: {psign:11s}")

print("\n=== 3. ASHTAKAVARGA ===")
AshtakavargaEngine.calculate_ashtakavarga(chart)
print(f"SAV total: {sum(chart.sarvashtakavarga.values())}")
for h, bindus in chart.sarvashtakavarga.items():
    sign = ZODIAC[(ZODIAC.index(chart.ascendant_sign) + h - 1) % 12]
    print(f" House {h:2d} ({sign:11s}): {bindus} bindus")

print("\n=== 4. CHARA KARAKAS (7 Scheme) ===")
ck = JaiminiEngine.calculate_chara_karakas(chart)
for k, v in ck.items():
    print(f" {k}: {v}")

print("\n=== 5. SPECIAL WEALTH LAGNAS ===")
wle = WealthLagnasEngine(chart)
special_lags = wle.calculate_special_lagnas()
print(json.dumps(special_lags, indent=2))

print("\n=== 6. SENSITIVE POINTS ===")
spe = SensitivePointsEngine(chart)
sp = spe.calculate_all()
print(json.dumps(sp, indent=2))

print("\n=== 7. VIMSHOTTARI DASHA TIMELINE ===")
moon_p = chart.planets['Moon']
moon_abs_lon = ZODIAC.index(moon_p.sign) * 30.0 + moon_p.degree
tl = DashaEngine.calculate_vimshottari_timeline(datetime(2008, 8, 1, 12, 55), moon_abs_lon)
for md in tl:
    print(f"MD: {md['lord']:7s} | {md['start'][:10]} -> {md['end'][:10]}")
    if md['lord'] in ['Mercury', 'Ketu', 'Venus']:
        for ad in md.get('sub_periods', []):
            print(f"   AD: {ad['lord']:7s} | {ad['start'][:10]} -> {ad['end'][:10]}")
            for pd in ad.get('sub_periods', []):
                st = pd['start'][:10]
                en = pd['end'][:10]
                if any(yr in st or yr in en for yr in ["2024", "2025", "2026", "2027", "2028"]):
                    print(f"      PD: {pd['lord']:7s} | {st} -> {en}")

print("\n=== 8. KP SYSTEM ANALYSIS ===")
kp_res = KPEngine.calculate_kp_chart(2008, 8, 1, 18, 25, 16.8185549, 82.0641497, 'Asia/Kolkata')
print("KP Cusps:")
for c in kp_res.get('cusps', []):
    print(f" Cusp {c['house']:2d}: {c['sign']:11s} {c['degree']:7.2f}° | SignLord: {c['sign_lord']:7s} | StarLord: {c['star_lord']:7s} | SubLord: {c['sub_lord']:7s} | SubSub: {c['sub_sub_lord']}")

print("\nKP Planets:")
for p, data in kp_res.get('planets', {}).items():
    print(f" {p:7s}: {data['sign']:11s} {data['degree']:7.2f}° | PlacidusH: {data.get('placidus_house', 0):2d} | StarLord: {data['star_lord']:7s} | SubLord: {data['sub_lord']:7s}")

print("\nKP ABCD Significators:")
for p, sigs in kp_res.get('abcd_significators', {}).items():
    print(f" Planet {p:7s}: {sigs}")

print("\nKP CSL Analysis:")
for h, csl in kp_res.get('csl_analysis', {}).items():
    print(f" House {h}: {csl}")

print("\n=== 9. YOGINI DASHA ===")
yd = YoginiDashaEngine.calculate_yogini_timeline(datetime(2008, 8, 1, 12, 55), moon_abs_lon)
for y in yd:
    st = str(y.get('start', ''))[:10]
    en = str(y.get('end', ''))[:10]
    if any(yr in st or yr in en for yr in ["2024", "2025", "2026", "2027", "2028", "2029", "2030", "2031"]):
        print(f" Yogini: {y.get('yogini'):10s} (Lord: {y.get('lord'):7s}) | {st} -> {en}")

print("\n=== 10. JAIMINI CHARA DASHA ===")
jcd = JaiminiCharaDashaEngine.calculate_chara_dasha_timeline(chart)
for cd in jcd:
    st = str(cd.get('start', ''))[:10]
    en = str(cd.get('end', ''))[:10]
    if any(yr in st or yr in en for yr in ["2020", "2022", "2024", "2025", "2026", "2027", "2028", "2029", "2030", "2031"]):
        print(f" Chara Dasha: {cd.get('sign'):12s} | {st} -> {en}")
