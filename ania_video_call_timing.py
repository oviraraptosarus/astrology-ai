import sys
sys.path.insert(0, r"E:\ASTROLOGY AI")

# Since find_muhurta only searches for waxing moon + auspicious nakshatra,
# I'll do a more thorough timing scan that matches HER chart for the video call
# Specifically: transit Moon position in relation to her natal Moon, Venus, Mercury,
# and her Sade Sati phase.

import swisseph as swe
from datetime import datetime, timedelta
import pytz
from config import Config
from astrology_engine import ZODIAC_SIGNS, NAKSHATRAS, calculate_nakshatra

swe.set_sid_mode(Config.ayanamsha_swe_id())
flags = swe.FLG_SIDEREAL | swe.FLG_SPEED

# Ania's natal positions (from previous run)
natal = {
    'Sun': 21.78,      # Pisces
    'Moon': 8.31,      # Pisces
    'Mars': 18.63,     # Gemini
    'Mercury': 10.51,  # Pisces
    'Jupiter': 26.60,  # Sagittarius
    'Venus': 4.72,     # Pisces
    'Saturn': 8.38,    # Leo retro
    'Rahu': 2.78,      # Aquarius
    'Ketu': 2.78,      # Leo
}
natal_lagna = 20.78  # Pisces

# Scan every 30 min from Sep 16 17:00 to Sep 17 02:00 Polish Time (CEST = UTC+2)
print("=== DETAILED TRANSIT SCAN: Sep 16-17, 2026 (Polish Time) ===\n")
print("(Moon sign, nakshatra, aspects to natal planets, and Sade Sati status)")

tz_warsaw = pytz.timezone('Europe/Warsaw')

for dt_local in [tz_warsaw.localize(datetime(2026, 9, 16, 17, 0)) + timedelta(minutes=30 * i) for i in range(19)]:
    dt_utc = dt_local.astimezone(pytz.utc)
    hour_dec = dt_utc.hour + dt_utc.minute / 60.0
    jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_dec)
    
    # Transit positions
    res_moon, _ = swe.calc_ut(jd, swe.MOON, flags)
    moon_lon = res_moon[0]
    
    res_sun, _ = swe.calc_ut(jd, swe.SUN, flags)
    sun_lon = res_sun[0]
    
    res_mars, _ = swe.calc_ut(jd, swe.MARS, flags)
    mars_lon = res_mars[0]
    
    res_jup, _ = swe.calc_ut(jd, swe.JUPITER, flags)
    jup_lon = res_jup[0]
    
    res_ven, _ = swe.calc_ut(jd, swe.VENUS, flags)
    ven_lon = res_ven[0]
    
    res_merc, _ = swe.calc_ut(jd, swe.MERCURY, flags)
    merc_lon = res_merc[0]
    
    res_sat, _ = swe.calc_ut(jd, swe.SATURN, flags)
    sat_lon = res_sat[0]
    
    # Sign
    def sign_name(lon):
        return ZODIAC_SIGNS[int(lon / 30)]
    
    moon_sign = sign_name(moon_lon)
    sat_sign = sign_name(sat_lon)
    ven_sign = sign_name(ven_lon)
    sun_sign = sign_name(sun_lon)
    
    # Moon nakshatra
    nak_name, nak_pada, nak_lord = calculate_nakshatra(moon_lon)
    
    # Aspects: Moon to natal planets
    aspects = []
    for pname, plon in natal.items():
        diff = abs(moon_lon - plon)
        if diff > 180:
            diff = 360 - diff
        if diff < 10:
            aspects.append(f"Moon CONJ natal {pname}")
        elif 165 < diff < 195:
            aspects.append(f"Moon OPP natal {pname}")
        elif 108 < diff < 132:
            aspects.append(f"Moon TRINE natal {pname}")
        elif 78 < diff < 102:
            aspects.append(f"Moon SQUARE natal {pname}")
    
    # Sade Sati check: transit Saturn sign vs natal Moon sign (Pisces)
    # Saturn in Pisces = Peak Sade Sati (Phase 2)
    sade_sati = "PEAK SADE SATI (Saturn in Pisces over natal Moon/Lagna)"
    
    # Moon's house from natal Lagna
    moon_house_from_lagna = int((moon_lon - natal_lagna) / 30) % 12 + 1
    
    # Transit Venus in relation to natal Lagna / 7th house
    ven_house_from_lagna = int((ven_lon - natal_lagna) / 30) % 12 + 1
    
    # Transit Jupiter in relation to natal Lagna
    jup_house_from_lagna = int((jup_lon - natal_lagna) / 30) % 12 + 1
    
    # Moon-Mars aspect (transit)
    mm_diff = abs(moon_lon - mars_lon)
    if mm_diff > 180:
        mm_diff = 360 - mm_diff
    
    # Moon-Jupiter aspect (transit)
    mj_diff = abs(moon_lon - jup_lon)
    if mj_diff > 180:
        mj_diff = 360 - mj_diff
    
    # Moon-Venus aspect (transit)
    mv_diff = abs(moon_lon - ven_lon)
    if mv_diff > 180:
        mv_diff = 360 - mv_diff
    
    m_house_detail = ""
    if moon_house_from_lagna in [1, 4, 7, 10]:
        m_house_detail = f"Moon in KENDRA (H{moon_house_from_lagna} from Lagna) - strong activation"
    elif moon_house_from_lagna in [3, 6, 11]:
        m_house_detail = f"Moon in TRISHADAYA (H{moon_house_from_lagna}) - slightly challenging"
    else:
        m_house_detail = f"Moon in H{moon_house_from_lagna} from Lagna"
    
    print(f"{dt_local.strftime('%Y-%m-%d %H:%M')} | Moon: {moon_sign} {moon_lon%30:.2f}° | Nak: {nak_name} P{nak_pada} | {m_house_detail} | "
          f"Sat: {sat_sign} | Ven: {ven_sign} (H{ven_house_from_lagna} from Lag) | Jup: (H{jup_house_from_lagna} from Lag)")
    for a in aspects:
        print(f"      {a}")
    if 60 < mm_diff < 70 or 108 < mm_diff < 132:
        print(f"      Transit Moon-Mars: {mm_diff:.1f}° (supportive)")
    if 100 < mj_diff < 130:
        print(f"      Transit Moon-Jupiter: {mj_diff:.1f}° (protective)")
    if 50 < mv_diff < 70 or 108 < mv_diff < 132:
        print(f"      Transit Moon-Venus: {mv_diff:.1f}° (affectionate)")