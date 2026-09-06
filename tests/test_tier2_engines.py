import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from astrology_engine import calculate_chart_with_object
from ashtakavarga_kakshya_engine import AshtakavargaKakshyaEngine
from kundali_milan_synastry_engine import KundaliMilanSynastryEngine

print("=" * 70)
print("TEST 1: ASHTAKAVARGA KAKSHYA 3.5-DAY TRANSIT WINDOWS (MANDAPETA 1975 CHART)")
print("=" * 70)
chart_m, payload_m = calculate_chart_with_object(1975, 5, 6, 7, 15, 16.8667, 81.9333, "Asia/Kolkata", 0)
kakshya_eng = AshtakavargaKakshyaEngine(chart_m)

windows_jup = kakshya_eng.scan_kakshya_windows("Jupiter", datetime(2026, 6, 1), duration_days=30)
print(f"\nJupiter Transit Kakshya Windows (June 2026):")
for w in windows_jup[:4]:
    print(f"  [{w['start_date']} to {w['end_date']}] Jupiter in {w['sign']} ({w['kakshya_lord']} Kakshya) -> {w['status']}")

print("\n" + "=" * 70)
print("TEST 2: KUNDALI MILAN & SYNASTRY (AMITABH & JAYA BACHCHAN)")
print("=" * 70)
# Amitabh: Oct 11, 1942, 16:00, Allahabad (Moon in Libra)
chart_ab, _ = calculate_chart_with_object(1942, 10, 11, 16, 0, 25.4358, 81.8463, "Asia/Kolkata", 0)
# Jaya Bhaduri: Apr 9, 1948, 23:45, Jabalpur (Moon in Aries)
chart_jb, _ = calculate_chart_with_object(1948, 4, 9, 23, 45, 23.1815, 79.9864, "Asia/Kolkata", 0)

ab_moon = chart_ab.planets["Moon"].longitude
jb_moon = chart_jb.planets["Moon"].longitude

milan_res = KundaliMilanSynastryEngine.calculate_ashta_koota(ab_moon, jb_moon)
print(f"Total Guna Milan Score : {milan_res['total_guna_score']} / {milan_res['max_score']}")
print(f"Match Recommendation   : {milan_res['recommendation']}")
print(f"Nadi Score             : {milan_res['breakdown']['nadi']['points']}/8 - {milan_res['breakdown']['nadi']['verdict']}")
print(f"Bhakoot Score          : {milan_res['breakdown']['bhakoot']['points']}/7 - {milan_res['breakdown']['bhakoot']['verdict']}")

kuja_ab = KundaliMilanSynastryEngine.evaluate_kuja_dosha(chart_ab)
print(f"\nAmitabh Kuja Dosha Status: {kuja_ab['status']}")

fertility = KundaliMilanSynastryEngine.calculate_beeja_kshetra_sphuta(chart_ab, chart_jb)
print(f"Beeja Sphuta (Male)      : {fertility['beeja_sphuta_male']['sign']} ({fertility['beeja_sphuta_male']['vitality_status']})")
print(f"Kshetra Sphuta (Female)   : {fertility['kshetra_sphuta_female']['sign']} ({fertility['kshetra_sphuta_female']['fertility_status']})")
