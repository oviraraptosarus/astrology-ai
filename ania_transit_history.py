import sys
import json
from datetime import datetime, timedelta
sys.path.insert(0, r"E:\ASTROLOGY AI")

import swisseph as swe
import pytz
from config import Config
from astrology_engine import ZODIAC_SIGNS, NAKSHATRAS, calculate_nakshatra

swe.set_sid_mode(Config.ayanamsha_swe_id())
flags = swe.FLG_SIDEREAL | swe.FLG_SPEED

signs = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

# Ania natal: April 5, 2008, 06:15 AM, Bytom, Poland (Europe/Warsaw, UTC+2)
natal = {
    'Sun': 21.78 + 30*11,      # Pisces 21.78
    'Moon': 8.31 + 30*11,      # Pisces 8.31
    'Mars': 18.63 + 30*2,      # Gemini 18.63
    'Mercury': 10.51 + 30*11,  # Pisces 10.51
    'Jupiter': 26.60 + 30*8,   # Sagittarius 26.60
    'Venus': 4.72 + 30*11,     # Pisces 4.72
    'Saturn': 8.38 + 30*4,     # Leo 8.38
    'Rahu': 2.78 + 30*10,      # Aquarius 2.78
    'Ketu': 2.78 + 30*4,       # Leo 2.78
}
lagna = 20.78 + 30*11  # Pisces 20.78

def sign_of(lon):
    return signs[int(lon/30)]

def house_from_lagna(lon):
    return int((lon - lagna) / 30) % 12 + 1

def diff_from_lagna(lon):
    d = (lon - lagna) % 360
    return d

# ============================================
# SATURN TRANSIT HISTORY — THE BIG ONE
# Since Saturn takes ~29.5 years to circle,
# check whether Saturn has been transiting her Pisces stellium
# during the past few years (2024-2026), which would explain
# prolonged avoidance, depression, withdrawal.
# ============================================
print("=== SATURN TRANSIT HISTORY 2022-2027 (her Sade Sati + Pisces transit) ===\n")
print("Saturn entered Pisces ~March 2025 (from Aquarius). Let's track its path.")

tz_warsaw = pytz.timezone('Europe/Warsaw')

# Scan Saturn monthly from Jan 2023 to Dec 2027
print("Month | Saturn Sign | House | Distance to natal Moon | Distance to natal Lagna | Status")
for year in range(2023, 2028):
    for month in range(1, 13):
        try:
            dt_local = tz_warsaw.localize(datetime(year, month, 15, 12, 0))
            dt_utc = dt_local.astimezone(pytz.utc)
            jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60.0)
            res_sat, _ = swe.calc_ut(jd, swe.SATURN, flags)
            sat_lon = res_sat[0]
            
            sat_sign = sign_of(sat_lon)
            sat_house = house_from_lagna(sat_lon)
            
            # Distances to her key natal points
            moon_dist = abs(sat_lon - natal['Moon'])
            if moon_dist > 180: moon_dist = 360 - moon_dist
            lag_dist = abs(sat_lon - lagna)
            if lag_dist > 180: lag_dist = 360 - lag_dist
            ven_dist = abs(sat_lon - natal['Venus'])
            if ven_dist > 180: ven_dist = 360 - ven_dist
            merc_dist = abs(sat_lon - natal['Mercury'])
            if merc_dist > 180: merc_dist = 360 - merc_dist
            
            # Status
            status = ""
            if sat_sign == "Pisces":
                status = "PISCCES TRANSIT"
            if moon_dist < 10:
                status += " | ON MOON (peak sade sati)"
            if lag_dist < 10:
                status += " | ON LAGNA"
            if ven_dist < 10:
                status += " | ON VENUS"
            if merc_dist < 10:
                status += " | ON MERCURY"
            
            # Only print important periods (Pisces transit or near her points)
            if sat_sign in ["Aquarius", "Pisces"] or status:
                print(f"{year}-{month:02d} | {sat_sign:12s} | H{sat_house:2d} | Moon: {moon_dist:5.1f}° | Lag: {lag_dist:5.1f}° | Ven: {ven_dist:5.1f}° | Merc: {merc_dist:5.1f}° | {status}")
        except Exception as e:
            print(f"Error at {year}-{month}: {e}")

print("\n\n=== JUPITER TRANSIT HISTORY (expansive/optimism planet) ===\n")
# Jupiter in Cancer (summer 2025-2026) aspects her 7th house?
for year in range(2024, 2028):
    for month in range(1, 13, 2):
        try:
            dt_local = tz_warsaw.localize(datetime(year, month, 15, 12, 0))
            dt_utc = dt_local.astimezone(pytz.utc)
            jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60.0)
            res_jup, _ = swe.calc_ut(jd, swe.JUPITER, flags)
            jup_lon = res_jup[0]
            jup_sign = sign_of(jup_lon)
            jup_house = house_from_lagna(jup_lon)
            print(f"{year}-{month:02d} | Jupiter {jup_sign:12s} H{jup_house}")
        except Exception as e:
            pass

print("\n\n=== TRANSIT RAHU — long-running escapism facadse ===\n")
# Rahu has a ~18-year cycle, moves backwards ~19°/year
# Check current Rahu (2024-2027) and where it's been
for year in range(2024, 2028):
    for month in [3, 6, 9, 12]:
        try:
            dt_local = tz_warsaw.localize(datetime(year, month, 15, 12, 0))
            dt_utc = dt_local.astimezone(pytz.utc)
            jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60.0)
            res_rahu, _ = swe.calc_ut(jd, Config.node_swe_id(), flags)
            rahu_lon = res_rahu[0]
            rahu_sign = sign_of(rahu_lon)
            rahu_house = house_from_lagna(rahu_lon)
            print(f"{year}-{month:02d} | Rahu {rahu_sign:12s} H{rahu_house}")
        except Exception as e:
            pass

print("\n\n=== CURRENT MOON TRANSIT (today Sep 15, 2026) ===")
dt_local = tz_warsaw.localize(datetime(2026, 9, 15, 20, 0))  # evening Poland
dt_utc = dt_local.astimezone(pytz.utc)
jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute/60.0)
res_moon, _ = swe.calc_ut(jd, swe.MOON, flags)
moon_lon = res_moon[0]
moon_sign = sign_of(moon_lon)
moon_house = house_from_lagna(moon_lon)
nak, pada, lord = calculate_nakshatra(moon_lon)
print(f"Transit Moon: {moon_sign} {moon_lon%30:.2f}° H{moon_house} | Nak: {nak} P{pada} (lord {lord})")

# Check moon to natal aspects
print("\nTransit Moon aspects to her natal chart:")
for pname, plon in natal.items():
    diff = abs(moon_lon - plon)
    if diff > 180: diff = 360 - diff
    if diff < 10:
        print(f"  Moon CONJUNCT natal {pname} ({diff:.2f}°)")
    elif 165 < diff < 195:
        print(f"  Moon OPPOSITE natal {pname} ({diff:.2f}°)")
    elif 108 < diff < 132:
        print(f"  Moon TRINE natal {pname} ({diff:.2f}°)")
    elif 78 < diff < 102:
        print(f"  Moon SQUARE natal {pname} ({diff:.2f}°)")