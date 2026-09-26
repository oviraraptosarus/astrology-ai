import sys, os
sys.path.insert(0, r"E:/ASTROLOGY AI")
import datetime
import swisseph as swe
from astrology_engine import calculate_chart_with_object
from dasha_engine import DashaEngine
from varga_engine import VargaEngine
from forward_timing_scanner import ZODIAC_SIGNS

B_BIRTH = (2008, 4, 5, 6, 15, 50.348, 18.916, "Europe/Warsaw")
chart_b, payload_b = calculate_chart_with_object(*B_BIRTH, name="Her")

print("=== PLANETARY DETAILED POSITIONS ===")
for p, obj in chart_b.planets.items():
    sign_idx = ZODIAC_SIGNS.index(obj.sign)
    abs_lon = sign_idx * 30.0 + obj.degree
    d9 = VargaEngine.calc_d9_navamsha(obj.sign, obj.degree)
    d3 = VargaEngine.calc_d3_drekkana(obj.sign, obj.degree)
    d7 = VargaEngine.calc_d7_saptamsha(obj.sign, obj.degree)
    d10 = VargaEngine.calc_d10_dasamsha(obj.sign, obj.degree)
    d12 = VargaEngine.calc_d12_dwadashamsha(obj.sign, obj.degree)
    d30 = VargaEngine.calc_d30_trimshamsha(obj.sign, obj.degree)
    d60 = VargaEngine.calc_d60_shashtiamsha(obj.sign, obj.degree)
    print(f"{p:8s}: {obj.sign:11s} {obj.degree:7.4f}° (Abs:{abs_lon:7.4f}°) | Nak: {obj.nakshatra:18s} | House: {obj.house} | D9:{d9:11s} | D30:{d30:11s} | D60:{d60:11s}")

asc_sign_idx = ZODIAC_SIGNS.index(chart_b.ascendant_sign)
asc_abs_lon = asc_sign_idx * 30.0 + chart_b.ascendant_degree
asc_d9 = VargaEngine.calc_d9_navamsha(chart_b.ascendant_sign, chart_b.ascendant_degree)
asc_d30 = VargaEngine.calc_d30_trimshamsha(chart_b.ascendant_sign, chart_b.ascendant_degree)
asc_d60 = VargaEngine.calc_d60_shashtiamsha(chart_b.ascendant_sign, chart_b.ascendant_degree)
print(f"{'Lagna':8s}: {chart_b.ascendant_sign:11s} {chart_b.ascendant_degree:7.4f}° (Abs:{asc_abs_lon:7.4f}°) | D9:{asc_d9:11s} | D30:{asc_d30:11s} | D60:{asc_d60:11s}")

print("\n=== TIMELINE (VIMSHOTTARI) ===")
moon_lon = ZODIAC_SIGNS.index(chart_b.planets['Moon'].sign) * 30.0 + chart_b.planets['Moon'].degree
dt_utc = datetime.datetime(2008, 4, 5, 4, 15, tzinfo=datetime.timezone.utc) # CEST is UTC+2
timeline = DashaEngine.calculate_vimshottari_timeline(dt_utc, moon_lon, num_levels=3)
for md in timeline:
    print(f"MD: {md['lord']} [{md['start'][:10]} to {md['end'][:10]}]")
    for ad in md.get('sub_periods', []):
        if any(y in ad['start'] or y in ad['end'] for y in ["2023", "2024", "2025", "2026", "2027", "2028", "2029", "2030"]):
            print(f"   AD: {md['lord']}-{ad['lord']} [{ad['start'][:10]} to {ad['end'][:10]}]")
            for pd in ad.get('sub_periods', []):
                if any(y in pd['start'] or y in pd['end'] for y in ["2025", "2026", "2027"]):
                    print(f"      PD: {md['lord']}-{ad['lord']}-{pd['lord']} [{pd['start'][:10]} to {pd['end'][:10]}]")

