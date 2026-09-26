import sys
import json
import math
from datetime import datetime, timedelta

sys.path.insert(0, r"E:\ASTROLOGY AI")
sys.path.insert(0, r"E:\ASTROLOGY AI\venv\Lib\site-packages")

import swisseph as swe
import astrology_engine
from vedic_models import Planet

# Set sidereal mode (Lahiri ayanamsa)
swe.set_sid_mode(swe.SIDM_LAHIRI)

# =====================================================
# ANIA'S NATAL CHART
# =====================================================
chart_a, chart_dict_a = astrology_engine.calculate_chart_with_object(
    year=2008, month=4, day=5,
    hour=6, minute=15,
    lat=50.3480, lon=18.9328,
    tz_name='Europe/Warsaw'
)

print("=== ANIA NATAL POSITIONS ===")
for name, p in chart_a.planets.items():
    r = getattr(p, 'retrograde', False)
    print(f"  {p.name:7s}: {p.sign:12s} {p.degree:7.4f}°  H{p.house:2d}  Nak={p.nakshatra:20s}  Retro={r}")

print(f"  Lagna: {chart_a.ascendant_sign} {chart_a.ascendant_degree:.4f}°")

# =====================================================
# TRANSIT POSITIONS FOR TOMORROW EVENING
# September 16, 2026, Wednesday
# Let's check 18:00, 19:00, 20:00, 21:00, 22:00, 23:00 Polish Time (CEST = UTC+2)
# =====================================================

print("\n\n=== TRANSIT SCAN: SEPTEMBER 16, 2026 (EVENING) ===")

for hour in [18, 19, 20, 21, 22, 23]:
    # September 16, 2026, hour:00:00 Polish Time = hour-2 UTC = (hour-2):00:00 UTC
    utc_hour = hour - 2
    
    jd = swe.julday(2026, 9, 16, utc_hour)
    
    # Get Moon position at this JD
    moon_pos = swe.calc_ut(jd, swe.MOON, swe.FLG_SIDEREAL | swe.FLG_SPEED)
    moon_long = moon_pos[0][0]
    moon_speed = moon_pos[0][3]
    
    # Get Sun position
    sun_pos = swe.calc_ut(jd, swe.SUN, swe.FLG_SIDEREAL | swe.FLG_SPEED)
    sun_long = sun_pos[0][0]
    
    # Get Mars position
    mars_pos = swe.calc_ut(jd, swe.MARS, swe.FLG_SIDEREAL | swe.FLG_SPEED)
    mars_long = mars_pos[0][0]
    
    # Get Jupiter position
    jup_pos = swe.calc_ut(jd, swe.JUPITER, swe.FLG_SIDEREAL | swe.FLG_SPEED)
    jup_long = jup_pos[0][0]
    
    # Get Venus position
    ven_pos = swe.calc_ut(jd, swe.VENUS, swe.FLG_SIDEREAL | swe.FLG_SPEED)
    ven_long = ven_pos[0][0]
    
    # Get Saturn position
    sat_pos = swe.calc_ut(jd, swe.SATURN, swe.FLG_SIDEREAL | swe.FLG_SPEED)
    sat_long = sat_pos[0][0]
    
    # Get Mercury position
    merc_pos = swe.calc_ut(jd, swe.MERCURY, swe.FLG_SIDEREAL | swe.FLG_SPEED)
    merc_long = merc_pos[0][0]
    
    # Convert longitudes to signs
    signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
             "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
    
    def long_to_sign(deg):
        idx = int(deg / 30)
        sign_deg = deg - (idx * 30)
        return signs[idx], sign_deg
    
    moon_sign, moon_sd = long_to_sign(moon_long)
    sun_sign, sun_sd = long_to_sign(sun_long)
    mars_sign, mars_sd = long_to_sign(mars_long)
    jup_sign, jup_sd = long_to_sign(jup_long)
    ven_sign, ven_sd = long_to_sign(ven_long)
    sat_sign, sat_sd = long_to_sign(sat_long)
    merc_sign, merc_sd = long_to_sign(merc_long)
    
    # Moon-Saturn distance (for Sade Sati)
    moon_sat_diff = abs(moon_long - sat_long)
    if moon_sat_diff > 180:
        moon_sat_diff = 360 - moon_sat_diff
    
    # Moon-Jupiter aspect (benefic)
    moon_jup_diff = abs(moon_long - jup_long)
    if moon_jup_diff > 180:
        moon_jup_diff = 360 - moon_jup_diff
    
    # Moon-Mars aspect
    moon_mars_diff = abs(moon_long - mars_long)
    if moon_mars_diff > 180:
        moon_mars_diff = 360 - moon_mars_diff
    
    # Moon-Venus aspect
    moon_ven_diff = abs(moon_long - ven_long)
    if moon_ven_diff > 180:
        moon_ven_diff = 360 - moon_ven_diff
    
    # Check aspects (conjunction = <10, opposition = 170-190, trine = 110-130, square = 80-100, sextile = 50-70)
    def aspect_name(diff):
        if diff < 10:
            return "CONJ"
        elif 10 < diff < 15:
            return "near-CONJ"
        elif 165 < diff < 195:
            return "OPP"
        elif 108 < diff < 132:
            return "TRINE"
        elif 78 < diff < 102:
            return "SQUARE"
        elif 48 < diff < 72:
            return "SEXTILE"
        else:
            return f"{diff:.0f}° apart"
    
    print(f"\n--- {hour}:00 Polish Time (Sep 16) ---")
    print(f"  Moon: {moon_sign} {moon_sd:.2f}° (speed: {moon_speed:.4f}°/day)")
    print(f"  Sun:  {sun_sign} {sun_sd:.2f}°")
    print(f"  Mars: {mars_sign} {mars_sd:.2f}°")
    print(f"  Jup:  {jup_sign} {jup_sd:.2f}°")
    print(f"  Ven:  {ven_sign} {ven_sd:.2f}°")
    print(f"  Sat:  {sat_sign} {sat_sd:.2f}°")
    print(f"  Merc: {merc_sign} {merc_sd:.2f}°")
    print(f"  Moon-Saturn distance: {moon_sat_diff:.2f}° ({aspect_name(moon_sat_diff)})")
    print(f"  Moon-Jupiter distance: {moon_jup_diff:.2f}° ({aspect_name(moon_jup_diff)})")
    print(f"  Moon-Mars distance: {moon_mars_diff:.2f}° ({aspect_name(moon_mars_diff)})")
    print(f"  Moon-Venus distance: {moon_ven_diff:.2f}° ({aspect_name(moon_ven_diff)})")
