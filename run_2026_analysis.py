import os, sys, json
from datetime import datetime

# Import engines
from astrology_engine import calculate_chart_with_object, calculate_vargas, calculate_aspects
from dasha_engine import DashaEngine
from yogini_dasha_engine import YoginiDashaEngine
from jaimini_chara_dasha_engine import JaiminiCharaDashaEngine
from tajika_engine import TajikaEngine
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
from advanced_avasthas import AdvancedAvasthasEngine
from wealth_lagnas_engine import WealthLagnasEngine

# Birth Details: 2008-08-01 18:25 IST, Ramachandrapuram, AP (16.85, 82.02)
year = 2008
month = 8
day = 1
hour = 18
minute = 25
lat = 16.85
lon = 82.02
tz_name = "Asia/Kolkata"

print("--- CALCULATING BASE CHART ---")
chart = calculate_chart_with_object(year, month, day, hour, minute, lat=lat, lon=lon, tz_name=tz_name)
print(f"Lagna: {chart.ascendant_sign} {chart.ascendant_degree:.2f}°")
for p in chart.planets:
    print(f"{p.name}: {p.sign} {p.degree:.2f}° (House {p.house}, Retro: {p.is_retrograde})")

print("\n--- DASHA ENGINE 2026 ---")
dasha_eng = DashaEngine(chart)
dashas_2026 = dasha_eng.calculate_vimshottari(start_year=2026, years=2)
# Or find current dasha tree
print("Dasha structure for 2026:")
current_d = dasha_eng.get_dasha_at_date(datetime(2026, 1, 1))
print("Jan 1 2026:", current_d)
mid_d = dasha_eng.get_dasha_at_date(datetime(2026, 6, 1))
print("Jun 1 2026:", mid_d)
sep_d = dasha_eng.get_dasha_at_date(datetime(2026, 9, 15))
print("Sep 15 2026:", sep_d)
dec_d = dasha_eng.get_dasha_at_date(datetime(2026, 12, 1))
print("Dec 1 2026:", dec_d)

print("\n--- FORWARD TIMING SCANNER 2026 ---")
scanner = ForwardTimingScanner(chart)
domains = ["CAREER", "BUSINESS", "WEALTH", "RELATIONSHIP", "HEALTH", "LITIGATION", "RELOCATION", "EDUCATION", "SPIRITUALITY"]
for d in domains:
    try:
        windows = scanner.scan_domain_windows(d, start_year=2026, years=1)
        print(f"\nDomain: {d} (Found {len(windows)} windows)")
        for w in windows[:5]:
            print(f"  Window: {w.get('start_date')} to {w.get('end_date')} | Score: {w.get('score')} | Prob: {w.get('probability')}% | Peak: {w.get('peak_date')} | Details: {w.get('description', '')[:100]}")
    except Exception as e:
        print(f"Error scanning {d}: {e}")

