import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from astrology_engine import calculate_chart_with_object
from jaimini_chara_dasha_engine import JaiminiCharaDashaEngine
from tajika_engine import TajikaVarshaphalaEngine

print("=" * 70)
print("TEST 1: AMITABH BACHCHAN (1942) - 1982 COOLIE ACCIDENT ANNUAL ANALYSIS")
print("=" * 70)
chart_ab, payload_ab = calculate_chart_with_object(1942, 10, 11, 16, 0, 25.4358, 81.8463, "Asia/Kolkata", 0)

# Chara Dasha
karakas = JaiminiCharaDashaEngine.calculate_chara_karakas(chart_ab)
print("Chara Karakas:")
for k, v in karakas.items():
    print(f"  {k} ({v['planet']}): {v['sign']} {v['degree_in_sign']:.2f} deg - {v['description']}")

arudhas = JaiminiCharaDashaEngine.calculate_arudhas(chart_ab)
print(f"\nArudha Lagna (AL): {arudhas['Arudha_Lagna']}, Upapada Lagna (UL): {arudhas['Upapada_Lagna']}")

# Varshaphala for 1981-1982 (Age 39 - accident occurred Aug 2, 1982)
annual_ab = TajikaVarshaphalaEngine.calculate_annual_chart(chart_ab, target_year=1981, lat=25.4358, lon=81.8463)
print(f"\n1981-1982 Solar Return Pravesha: {annual_ab['varsha_pravesha_utc']}")
print(f"Annual Ascendant: {annual_ab['varsha_ascendant']['sign']} at {annual_ab['varsha_ascendant']['degree']} deg")
print(f"Muntha Sign     : {annual_ab['muntha']['sign']} (Lord: {annual_ab['muntha']['lord']})")
print(f"Muntha Location : House {annual_ab['muntha']['house_in_varsha_chart']} in Annual Chart -> Status: {annual_ab['muntha']['status']}")
print(f"Varsha Swami    : {annual_ab['varsha_swami_year_lord']}")

print("\n" + "=" * 70)
print("TEST 2: MANDAPETA TAURUS CHART (1975) - 2026 ANNUAL SOLAR RETURN")
print("=" * 70)
chart_m, payload_m = calculate_chart_with_object(1975, 5, 6, 7, 15, 16.8667, 81.9333, "Asia/Kolkata", 0)
annual_m = TajikaVarshaphalaEngine.calculate_annual_chart(chart_m, target_year=2026, lat=16.8667, lon=81.9333)
print(f"2026 Solar Return Pravesha: {annual_m['varsha_pravesha_utc']}")
print(f"Annual Ascendant: {annual_m['varsha_ascendant']['sign']} at {annual_m['varsha_ascendant']['degree']} deg")
print(f"Muntha Sign     : {annual_m['muntha']['sign']} (Lord: {annual_m['muntha']['lord']})")
print(f"Muntha Location : House {annual_m['muntha']['house_in_varsha_chart']} in Annual Chart -> Status: {annual_m['muntha']['status']}")
print(f"Varsha Swami    : {annual_m['varsha_swami_year_lord']}")
