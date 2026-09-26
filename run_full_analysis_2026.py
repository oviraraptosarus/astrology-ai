import os, sys, json
from datetime import datetime
import pytz

from astrology_engine import calculate_chart_with_object, calculate_nakshatra, ZODIAC_SIGNS
from dasha_engine import DashaEngine
from yogini_dasha_engine import YoginiDashaEngine
from jaimini_chara_dasha_engine import JaiminiCharaDashaEngine
from jaimini_engine import JaiminiEngine
from tajika_engine import TajikaVarshaphalaEngine
from forward_timing_scanner import ForwardTimingScanner
from sade_sati_engine import SadeSatiEngine
from gochara_vedha_engine import GocharaVedhaEngine
from ashtakavarga_kakshya_engine import AshtakavargaKakshyaEngine
from ashtakavarga_engine import AshtakavargaEngine
from sensitive_points import SensitivePointsEngine
from longevity_engine import LongevityEngine
from bhrigu_nandi_nadi_engine import BhriguNandiNadiEngine
from sarvatobhadra_chakra_engine import SarvatobhadraChakraEngine
from navatara_chakra_engine import NavataraChakraEngine
from medical_astrology_engine import MedicalAstrologyEngine
from cancellations import CancellationEngine
from advanced_avasthas import AdvancedAvasthaEngine
from wealth_lagnas_engine import WealthLagnasEngine
from strength_engine import StrengthEngine
from yogas import evaluate_all_yogas

year, month, day = 2008, 8, 1
hour, minute = 18, 25
lat, lon = 16.85, 82.02
tz_name = "Asia/Kolkata"

print("==================================================")
print("1. NATAL CHART BASE")
print("==================================================")
chart, chart_dict = calculate_chart_with_object(year, month, day, hour, minute, lat=lat, lon=lon, tz_name=tz_name)
print(f"Ascendant: {chart.ascendant_sign} {chart.ascendant_degree:.4f}° (Makara / Capricorn Lagna)")
for p_name, p in chart.planets.items():
    p_lon = (ZODIAC_SIGNS.index(p.sign) * 30.0) + p.degree
    nak_name, pada, nak_lord = calculate_nakshatra(p_lon)
    print(f"  {p.name:8s}: {p.sign:12s} {p.degree:7.4f}° (Abs: {p_lon:7.3f}°) | House {p.house:2d} | Chalit {p.chalit_house:2d} | Retro: {p.retrograde} | Nak: {nak_name} Pada {pada} (Lord: {nak_lord})")

print("\n--- CHARA KARAKAS ---")
karakas = JaiminiEngine.calculate_chara_karakas(chart)
for k, v in karakas.items():
    print(f"  {k}: {v}")

print("\n--- SENSITIVE POINTS ---")
sens_eng = SensitivePointsEngine(chart)
sens = sens_eng.calculate_all()
for k, v in sens.items():
    print(f"  {k}: {v}")

print("\n--- WEALTH LAGNAS ---")
wealth_eng = WealthLagnasEngine(chart)
wl = wealth_eng.calculate_special_lagnas()
for k, v in wl.items():
    print(f"  {k}: {v}")

print("\n--- ASHTAKAVARGA SAV ---")
# calculate_ashtakavarga is static or returns SAV
ashtakavarga = AshtakavargaEngine.calculate_ashtakavarga(chart)
print(f"SAV points: {ashtakavarga.get('sav', {})}")

print("\n--- SHADBALA ---")
shadbala = StrengthEngine.calculate_shadbala(chart)
for p_name, p_sb in shadbala.items():
    print(f"  {p_name:8s}: Total {p_sb.get('total_shadbala', 0):.2f} Rupas ({p_sb.get('total_virupas', 0):.1f} Virupas) | Ratio: {p_sb.get('strength_ratio', 0):.2f}")

print("\n==================================================")
print("2. VIMSHOTTARI DASHA 2026")
print("==================================================")
dasha_eng = DashaEngine(chart)
timeline = dasha_eng.calculate_vimshottari_timeline(depth=4)

print("All Vimshottari periods active during 2026:")
for entry in timeline:
    s_dt = entry['start_date'] if isinstance(entry['start_date'], datetime) else datetime.fromisoformat(str(entry['start_date']))
    e_dt = entry['end_date'] if isinstance(entry['end_date'], datetime) else datetime.fromisoformat(str(entry['end_date']))
    if s_dt < datetime(2027, 1, 1, tzinfo=s_dt.tzinfo if s_dt.tzinfo else pytz.UTC) and e_dt > datetime(2026, 1, 1, tzinfo=e_dt.tzinfo if e_dt.tzinfo else pytz.UTC):
        print(f"  {entry['dasha_path']:30s} | {s_dt.strftime('%Y-%m-%d')} -> {e_dt.strftime('%Y-%m-%d')}")

print("\n==================================================")
print("3. YOGINI DASHA 2026")
print("==================================================")
# static class
yog_timeline = YoginiDashaEngine.calculate_yogini_timeline(chart, years=36)
for y in yog_timeline:
    s_dt = y['start_date'] if isinstance(y['start_date'], datetime) else datetime.fromisoformat(str(y['start_date']))
    e_dt = y['end_date'] if isinstance(y['end_date'], datetime) else datetime.fromisoformat(str(y['end_date']))
    if s_dt < datetime(2027, 1, 1, tzinfo=s_dt.tzinfo if s_dt.tzinfo else pytz.UTC) and e_dt > datetime(2026, 1, 1, tzinfo=e_dt.tzinfo if e_dt.tzinfo else pytz.UTC):
        print(f"  Yogini: {y['major_yogini']}-{y.get('sub_yogini', '')} | {s_dt.strftime('%Y-%m-%d')} -> {e_dt.strftime('%Y-%m-%d')}")

print("\n==================================================")
print("4. JAIMINI CHARA DASHA 2026")
print("==================================================")
chara_eng = JaiminiCharaDashaEngine(chart)
chara_timeline = chara_eng.calculate_chara_dasha_timeline(years=40)
for c in chara_timeline:
    s_dt = c.get('start_date')
    e_dt = c.get('end_date')
    # we can print them all, it's fine
    print(f"  Sign Dasha: {c.get('sign')} | {s_dt} -> {e_dt} | Duration: {c.get('duration_years')} yrs")

print("\n==================================================")
print("5. TAJIKA VARSHAPHALA (2025-2026 and 2026-2027)")
print("==================================================")
varsha_2025 = TajikaVarshaphalaEngine.calculate_annual_chart(chart, target_year=2025, lat=lat, lon=lon)
print(f"Varshaphala 2025-2026 (Age 17->18, till Aug 2026):")
print(f"  Varsha Pravesha: {varsha_2025.get('varsha_pravesha_utc')}")
print(f"  Muntha Sign: {varsha_2025.get('muntha_sign')} (House {varsha_2025.get('muntha_house')})")
print(f"  Year Lord (Varsheshwara): {varsha_2025.get('varsheshwara')}")
print(f"  Mudda Dasha:")
for m in varsha_2025.get('mudda_dasha', []):
    print(f"    {m.get('planet')}: {m.get('start_date')} -> {m.get('end_date')}")

varsha_2026 = TajikaVarshaphalaEngine.calculate_annual_chart(chart, target_year=2026, lat=lat, lon=lon)
print(f"\nVarshaphala 2026-2027 (Age 18->19, from Aug 1, 2026):")
print(f"  Varsha Pravesha: {varsha_2026.get('varsha_pravesha_utc')}")
print(f"  Muntha Sign: {varsha_2026.get('muntha_sign')} (House {varsha_2026.get('muntha_house')})")
print(f"  Year Lord (Varsheshwara): {varsha_2026.get('varsheshwara')}")
print(f"  Mudda Dasha:")
for m in varsha_2026.get('mudda_dasha', []):
    print(f"    {m.get('planet')}: {m.get('start_date')} -> {m.get('end_date')}")

print("\n==================================================")
print("6. SADE SATI & SATURN TRANSIT 2026")
print("==================================================")
ss_eng = SadeSatiEngine(chart)
ss_status = ss_eng.evaluate_current_status(target_date=datetime(2026, 6, 1))
print(f"Sade Sati status at 2026-06-01: {ss_status}")
ss_lifecycle = ss_eng.generate_lifetime_sade_sati_timeline()
print("Sade Sati Lifecycle summary overall:")
for cycle in ss_lifecycle:
    print(f"  {cycle}")

print("\n==================================================")
print("7. FORWARD TIMING SCANNER: ALL DOMAINS 2026")
print("==================================================")
scanner = ForwardTimingScanner(chart)
domains = [
    "CAREER", "BUSINESS", "WEALTH", "RELATIONSHIP", "HEALTH", "ACCIDENT_TRAUMA", "EDUCATION"
]
for d in domains:
    try:
        windows = scanner.scan_domain_windows(d, start_year=2026, years=1)
        print(f"\n>>> DOMAIN: {d} (Total Windows: {len(windows)})")
        for w in windows:
            print(f"  [{w.get('start_date')} -> {w.get('end_date')}] | Score: {w.get('score')} | Prob: {w.get('probability')}% | Peak: {w.get('peak_date')}")
            print(f"    Trigger: {w.get('trigger_type')} | Dasha: {w.get('dasha_triad')} | Kakshya: {w.get('kakshya_bindus')}")
            print(f"    Desc: {w.get('description')}")
    except Exception as e:
        print(f"  Error on {d}: {e}")

print("\n==================================================")
print("8. MEDICAL ASTROLOGY & ACUTE HEALTH")
print("==================================================")
med_eng = MedicalAstrologyEngine(chart)
med = med_eng.diagnose_health_profile()
print(f"Medical profile: {json.dumps(med, indent=2, default=str)}")

print("\n==================================================")
print("9. LONGEVITY & MARAKA/BADHAKA")
print("==================================================")
pairs = LongevityEngine.calculate_jaimini_3_pairs(chart)
# span = LongevityEngine.calculate_jaimini_longevity_span(chart)
# marakas = LongevityEngine.identify_marakas(chart)
print(f"Jaimini 3 Pairs: {pairs}")
# print(f"Longevity Span: {span}")
# print(f"Maraka/Badhaka: {marakas}")

print("\n==================================================")
print("10. BHRIGU NANDI NADI 2026")
print("==================================================")
bnn_eng = BhriguNandiNadiEngine(chart)
bnn_pos = bnn_eng.calculate_progressed_positions(current_age=18.0)
print(f"BNN Progressed Positions at Age 18 (2026): {bnn_pos}")

print("\n==================================================")
print("11. YOGAS & CANCELLATIONS")
print("==================================================")
yogas_eval = evaluate_all_yogas(chart)
for y in yogas_eval:
    if getattr(y, 'fired', False):
        print(f"  Yoga: {y.name} | Effect: {y.effects}")

canc_eng = CancellationEngine(chart)
cancs = canc_eng.evaluate_all_cancellations()
for pl, c_info in cancs.items():
    print(f"  {pl}: {c_info}")

print("\n==================================================")
print("12. LAJJITADI AVASTHAS")
print("==================================================")
av_state_eng = AdvancedAvasthaEngine(chart)
avasthas = av_state_eng.combine_all()
for pl, av in avasthas.items():
    print(f"  {pl}: {av}")
