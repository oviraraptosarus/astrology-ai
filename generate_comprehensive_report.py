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

out = {}

chart, chart_dict = calculate_chart_with_object(year, month, day, hour, minute, lat=lat, lon=lon, tz_name=tz_name)

# 1. Base Chart & Planets
planets_data = {}
for p_name, p in chart.planets.items():
    p_lon = (ZODIAC_SIGNS.index(p.sign) * 30.0) + p.degree
    nak_name, pada, nak_lord = calculate_nakshatra(p_lon)
    planets_data[p_name] = {
        "sign": p.sign,
        "degree": p.degree,
        "longitude": p_lon,
        "house": p.house,
        "chalit_house": p.chalit_house,
        "retrograde": p.retrograde,
        "nakshatra": nak_name,
        "pada": pada,
        "nak_lord": nak_lord
    }

out["lagna"] = {"sign": chart.ascendant_sign, "degree": chart.ascendant_degree}
out["planets"] = planets_data

# Chara Karakas
out["chara_karakas"] = JaiminiEngine.calculate_chara_karakas(chart)

# Sensitive points
sens_eng = SensitivePointsEngine(chart)
out["sensitive_points"] = sens_eng.calculate_all()

# Special Wealth Lagnas
wealth_eng = WealthLagnasEngine(chart)
out["wealth_lagnas"] = wealth_eng.calculate_special_lagnas()

# Ashtakavarga
AshtakavargaEngine.calculate_ashtakavarga(chart)
out["sarvashtakavarga"] = chart.sarvashtakavarga
out["bhinna_ashtakavarga"] = chart.bhinna_ashtakavarga

# Shadbala
out["shadbala"] = StrengthEngine.calculate_shadbala(chart)

# Vimshottari Timeline
moon_lon = (ZODIAC_SIGNS.index(chart.planets['Moon'].sign) * 30.0) + chart.planets['Moon'].degree
timeline_tree = DashaEngine.calculate_vimshottari_timeline(chart.birth_time, moon_lon, num_levels=3)

# Flatten timeline tree
def flatten_dasha(tree, prefix=""):
    flat = []
    for item in tree:
        path = f"{prefix}/{item['lord']}" if prefix else item['lord']
        flat.append({
            "path": path,
            "level": item['level'],
            "start": item['start'],
            "end": item['end']
        })
        if 'sub_periods' in item and item['sub_periods']:
            flat.extend(flatten_dasha(item['sub_periods'], path))
    return flat

timeline = flatten_dasha(timeline_tree)
v_2026 = []
for entry in timeline:
    s_dt = entry['start'] if isinstance(entry['start'], datetime) else datetime.fromisoformat(str(entry['start']))
    e_dt = entry['end'] if isinstance(entry['end'], datetime) else datetime.fromisoformat(str(entry['end']))
    if s_dt.year <= 2026 and e_dt.year >= 2026:
        v_2026.append({
            "path": entry['path'],
            "level": entry['level'],
            "start": s_dt.strftime('%Y-%m-%d %H:%M'),
            "end": e_dt.strftime('%Y-%m-%d %H:%M')
        })
out["vimshottari_2026"] = v_2026

# Yogini Dasha
yog_timeline = YoginiDashaEngine.calculate_yogini_timeline(chart.birth_time, moon_lon, cycles=3)
y_2026 = []
for y in yog_timeline:
    s_dt = y['start'] if isinstance(y['start'], datetime) else datetime.fromisoformat(str(y['start']))
    e_dt = y['end'] if isinstance(y['end'], datetime) else datetime.fromisoformat(str(y['end']))
    if s_dt.year <= 2026 and e_dt.year >= 2026:
        y_2026.append({
            "major": y['yogini'],
            "start": s_dt.strftime('%Y-%m-%d'),
            "end": e_dt.strftime('%Y-%m-%d')
        })
out["yogini_2026"] = y_2026

# Jaimini Chara Dasha
out["chara_dasha_timeline"] = JaiminiCharaDashaEngine.calculate_chara_dasha_timeline(chart, chart.birth_time, cycles=2)

# Tajika Varshaphala (2025-2026 and 2026-2027)
varsha_2025 = TajikaVarshaphalaEngine.calculate_annual_chart(chart, target_year=2025, lat=lat, lon=lon)
varsha_2026 = TajikaVarshaphalaEngine.calculate_annual_chart(chart, target_year=2026, lat=lat, lon=lon)
out["varshaphala_2025_2026"] = varsha_2025
out["varshaphala_2026_2027"] = varsha_2026

# Sade Sati
ss_eng = SadeSatiEngine(chart)
out["sade_sati_status_mid2026"] = ss_eng.evaluate_current_status(target_date=datetime(2026, 6, 1))
out["sade_sati_lifecycle"] = ss_eng.generate_lifetime_sade_sati_timeline(chart.birth_time)

# Forward Timing Scanner
scanner = ForwardTimingScanner(chart)
domains = [
    "CAREER", "BUSINESS", "WEALTH", "RELATIONSHIP", "MARRIAGE",
    "HEALTH", "ACCIDENT_TRAUMA", "LITIGATION", "RELOCATION", "EDUCATION", "SPIRITUALITY"
]
out["forward_windows_2026"] = {}
start_dt = datetime(2026, 1, 1, tzinfo=pytz.UTC)
for d in domains:
    try:
        windows = scanner.scan_domain_windows(d, start_date=start_dt, months_ahead=12)
        out["forward_windows_2026"][d] = windows
    except Exception as e:
        out["forward_windows_2026"][d] = f"Error: {e}"

# Medical
med_eng = MedicalAstrologyEngine(chart)
out["medical_profile"] = med_eng.diagnose_health_profile()

# Longevity
out["jaimini_3_pairs"] = LongevityEngine.calculate_jaimini_3_pairs(chart)

# BNN Progressions
bnn_eng = BhriguNandiNadiEngine(chart)
out["bnn_age_18"] = bnn_eng.calculate_progressed_positions(current_age=18.0)

# Yogas
yogas_eval = evaluate_all_yogas(chart)
out["yogas"] = [{"name": y.name, "effect": y.effects, "description": getattr(y, 'description', '')} for y in yogas_eval if getattr(y, 'fired', False)]

# Cancellations
canc_eng = CancellationEngine(chart)
out["cancellations"] = canc_eng.evaluate_all_cancellations()

# Lajjitadi Avasthas
av_state_eng = AdvancedAvasthaEngine(chart)
out["avasthas"] = av_state_eng.combine_all()

# Sarvatobhadra Chakra for key dates in 2026
sbc_eng = SarvatobhadraChakraEngine(chart)
out["sbc_2026_01"] = sbc_eng.evaluate_transit_vedha(target_dt=datetime(2026, 1, 15, tzinfo=pytz.UTC))
out["sbc_2026_06"] = sbc_eng.evaluate_transit_vedha(target_dt=datetime(2026, 6, 15, tzinfo=pytz.UTC))
out["sbc_2026_09"] = sbc_eng.evaluate_transit_vedha(target_dt=datetime(2026, 9, 15, tzinfo=pytz.UTC))

with open("full_2026_data.json", "w", encoding="utf-8") as f:
    json.dump(out, f, indent=2, default=str)

print("SUCCESS: full_2026_data.json created with size:", os.path.getsize("full_2026_data.json"))
