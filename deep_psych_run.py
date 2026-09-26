import sys, os, json, datetime
import swisseph as swe

sys.path.insert(0, r"E:\ASTROLOGY AI")

from config import Config
from astrology_engine import calculate_chart_with_object
from dasha_engine import DashaEngine
from varga_engine import VargaEngine
from jaimini_engine import JaiminiEngine
from advanced_avasthas import AdvancedAvasthaEngine
from strength_engine import StrengthEngine
from sensitive_points import SensitivePointsEngine
from upagrahas import UpagrahaEngine
from panchangam_engine import PanchangamEngine
from yogas import evaluate_all_yogas
from ashtakavarga_engine import AshtakavargaEngine
from sade_sati_engine import SadeSatiEngine
from dosha_engine import DoshaEngine

# B (her): 2008-04-05 06:15 CEST, Bytom Poland (50.348N, 18.916E)
B_BIRTH = (2008, 4, 5, 6, 15, 50.348, 18.916, "Europe/Warsaw")

chart, payload = calculate_chart_with_object(*B_BIRTH, name="Her")

print("==================================================")
print("             NATAL CORE POSITIONS (D1)            ")
print("==================================================")
print(f"Lagna (Ascendant): {chart.ascendant_sign} {chart.ascendant_degree:.4f}°")
for p, obj in chart.planets.items():
    print(f"{p:8s}: {obj.sign:12s} {obj.degree:7.4f}° | House: {obj.house:2d} (KP/Chalit: {obj.chalit_house}) | Nak: {obj.nakshatra:18s} P{obj.nakshatra_pada} (Lord: {obj.nakshatra_lord}) | Ret: {str(obj.retrograde):5s} | Dignity: {obj.dignity}")

print("\n==================================================")
print("              PANCHANGAM AT BIRTH                 ")
print("==================================================")
try:
    pe = PanchangamEngine()
    dt = datetime.datetime(2008, 4, 5, 6, 15)
    panch = pe.calculate_full_panchang(dt, 50.348, 18.916, tz_name="Europe/Warsaw")
    for k, v in panch.items():
        print(f"  {k}: {v}")
except Exception as e:
    print(f"Panchangam error: {e}")

print("\n==================================================")
print("              CHARA KARAKAS (JAIMINI 8)           ")
print("==================================================")
try:
    j_karakas = JaiminiEngine.calculate_chara_karakas(chart, use_8_karakas=True)
    for k, v in j_karakas.items():
        p_obj = chart.planets[v]
        print(f"  {k:5s} : {v:8s} ({p_obj.sign} {p_obj.degree:.4f}° - Nak: {p_obj.nakshatra} P{p_obj.nakshatra_pada})")
except Exception as e:
    print(f"Jaimini karakas error: {e}")

print("\n==================================================")
print("                   ARUDHA PADAS                   ")
print("==================================================")
try:
    arudhas = JaiminiEngine.calculate_all_arudhas(chart)
    for k, v in arudhas.items():
        print(f"  {k:5s}: {v}")
except Exception as e:
    print(f"Arudhas error: {e}")

print("\n==================================================")
print("              VARGA PLACEMENTS (ALL KEY VARGAS)   ")
print("==================================================")
for p, obj in chart.planets.items():
    v = obj.vargas
    print(f"{p:8s} -> D9:{str(v.get('D9','')):12s} D60:{str(v.get('D60','')):12s} D30:{str(v.get('D30','')):12s} D10:{str(v.get('D10','')):12s} D7:{str(v.get('D7','')):12s} D12:{str(v.get('D12','')):12s} D27:{str(v.get('D27','')):12s} D2:{str(v.get('D2','')):12s} D3:{str(v.get('D3','')):12s}")

asc_v = VargaEngine.calculate_all_vargas(chart.ascendant_sign, chart.ascendant_degree)
print(f"Lagna    -> D9:{str(asc_v.get('D9','')):12s} D60:{str(asc_v.get('D60','')):12s} D30:{str(asc_v.get('D30','')):12s} D10:{str(asc_v.get('D10','')):12s} D7:{str(asc_v.get('D7','')):12s} D12:{str(asc_v.get('D12','')):12s}")

print("\n==================================================")
print("               ADVANCED AVASTHAS                  ")
print("==================================================")
try:
    aae = AdvancedAvasthaEngine(chart)
    all_av = aae.combine_all()
    for p, av in all_av.get("planets", {}).items():
        print(f"{p:8s}: Balaadi={av.get('balaadi')}, Jagradadi={av.get('jagradadi')}, Deeptadi={av.get('deeptadi')}, Lajjitadi={av.get('lajjitadi')}")
except Exception as e:
    print(f"Avasthas error: {e}")

print("\n==================================================")
print("            SENSITIVE POINTS & PUSHKARA           ")
print("==================================================")
try:
    spe = SensitivePointsEngine(chart)
    sens_all = spe.calculate_all()
    print("22nd Drekkana:", sens_all.get('twenty_second_drekkana'))
    print("64th Navamsha:", sens_all.get('sixty_fourth_navamsha'))
    print("Bhrigu Bindu:", sens_all.get('bhrigu_bindu'))
    print("Indu Lagna:", sens_all.get('indu_lagna'))
    print("Pushkara Navamsha / Bhaga:", sens_all.get('pushkara_points'))
    print("Mrityu Bhaga:", sens_all.get('mrityu_bhaga_violations'))
    print("Gandanta:", sens_all.get('gandantas'))
except Exception as e:
    print(f"Sensitive points error: {e}")

print("\n==================================================")
print("               UPAGRAHAS & APRAKASH               ")
print("==================================================")
try:
    upe = UpagrahaEngine(chart)
    jd_utc = swe.julday(2008, 4, 5, 4.25)
    upag_all = upe.calculate_all(jd_utc, 50.348, 18.916, is_night=False, weekday=5)
    for k, v in upag_all.items():
        print(f"  {k:15s}: {v}")
except Exception as e:
    print(f"Upagrahas error: {e}")

print("\n==================================================")
print("                   SHADBALA                       ")
print("==================================================")
try:
    for p, obj in chart.planets.items():
        if p in ['Rahu', 'Ketu']: continue
        sb = obj.shadbala
        print(f"  {p:8s}: Total Rupas={sb.get('total', 0)/60.0:.2f} ({sb.get('total', 0):.2f} virupas), Sthana={sb.get('sthana_bala')}, Dig={sb.get('dig_bala')}, Kala={sb.get('kala_bala')}, Cheshta={sb.get('cheshta_bala')}, Drik={sb.get('drik_bala')}")
except Exception as e:
    print(f"Shadbala error: {e}")

print("\n==================================================")
print("                 ASHTAKAVARGA                     ")
print("==================================================")
try:
    ave = AshtakavargaEngine()
    av_res = ave.calculate_ashtakavarga(chart)
    sav = av_res.get('sarvashtakavarga', {})
    print("SAV Points per sign:")
    for s, pts in sav.items():
        print(f"  {s:12s}: {pts}")
    print("\nBAV Points per planet per sign:")
    bav = av_res.get('bhinnashtakavarga', {})
    for p, row in bav.items():
        print(f"  {p:8s}: {row}")
except Exception as e:
    print(f"Ashtakavarga error: {e}")

print("\n==================================================")
print("                     YOGAS                        ")
print("==================================================")
try:
    y_list = evaluate_all_yogas(chart)
    for y in y_list:
        name = y.rule_name if hasattr(y, 'rule_name') else (y.get('name') if isinstance(y, dict) else str(y))
        active = y.is_active if hasattr(y, 'is_active') else True
        if active:
            desc = y.description if hasattr(y, 'description') else ""
            print(f"  - {name}: {desc}")
except Exception as e:
    print(f"Yogas error: {e}")

print("\n==================================================")
print("                 DOSHA EVALUATION                 ")
print("==================================================")
try:
    de_dosha = DoshaEngine()
    doshas = de_dosha.evaluate_all(chart)
    for d_name, d_val in doshas.items():
        print(f"  {d_name:20s}: {d_val}")
except Exception as e:
    print(f"Dosha error: {e}")

print("\n==================================================")
print("               VIMSHOTTARI DASHA TIMELINE         ")
print("==================================================")
try:
    de = DashaEngine()
    d_tree = de.calculate_vimshottari_dasha(chart)
    curr = de.get_dasha_at_date(d_tree, datetime.date(2026, 9, 13))
    print("Current (Sep 2026):", curr)
    for md in d_tree:
        print(f"\nMD: {md['planet']} from {md['start_date']} to {md['end_date']}")
        for ad in md.get('antardashas', []):
            print(f"   AD: {ad['planet']:8s} ({ad['start_date']} to {ad['end_date']})")
except Exception as e:
    print(f"Dasha error: {e}")
