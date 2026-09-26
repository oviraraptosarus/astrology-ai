import sys
import json
from datetime import datetime, timedelta
sys.path.insert(0, r"E:\ASTROLOGY AI")

import swisseph as swe
import pytz
from config import Config
from astrology_engine import ZODIAC_SIGNS, NAKSHATRAS, calculate_nakshatra, calculate_chart_with_object

swe.set_sid_mode(Config.ayanamsha_swe_id())
flags = swe.FLG_SIDEREAL | swe.FLG_SPEED

# ============================================
# ANIA'S NATAL CHART
# ============================================
chart_obj, chart_dict = calculate_chart_with_object(
    year=2008, month=4, day=5,
    hour=6, minute=15,
    lat=50.3480, lon=18.9328,
    tz_name='Europe/Warsaw'
)

signs = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]
natal = {}
for name, p in chart_obj.planets.items():
    natal[name] = p.degree + 30 * signs.index(p.sign)
lagna_deg = chart_obj.ascendant_degree + 30 * signs.index(chart_obj.ascendant_sign)

print("=== ANIA NATAL ===")
for name, p in chart_obj.planets.items():
    print(f"  {p.name:7s}: {p.sign:12s} {p.degree:7.4f}° H{p.house:2d} {p.nakshatra}")
print(f"  Lagna: {chart_obj.ascendant_sign} {chart_obj.ascendant_degree:.4f}°")

# Find key analysis points for call avoidance:
# 1. Is there anything ACTUALLY in her chart that creates secrecy, deception, or catfishing?
#    - 8th house concentration (secrets, hidden things)
#    - 12th house Rahu (dissolution, facade)
#    - Mercury affliction (lying/deception capacity)
#    - Venus affliction (fake love / false appearance)
#    - Ketu/Saturn in 6th (self-sabotage)
#    - 7th house condition (actual relationship reality)

print("\n=== HOUSE ANALYSIS ===")
# House contents (whole sign from Pisces lagna)
whole_sign_house = {
    1: [], 2: [], 3: [], 4: [], 5: [], 6: [], 7: [], 8: [], 9: [], 10: [], 11: [], 12: []
}
for name, lon in natal.items():
    h = int((lon - lagna_deg) / 30) % 12 + 1
    whole_sign_house[h].append(name)

for h in range(1, 13):
    occupants = whole_sign_house[h]
    if occupants:
        print(f"  H{h} ({signs[(signs.index(chart_obj.ascendant_sign) + h - 1) % 12]}): {', '.join(occupants)}")

print("\n=== DECEPTION/FAÇADE SIGNALS ===")
# 8th house = secrets, hidden things
h8 = whole_sign_house.get(8, [])
print(f"  H8 (secrets/hidden): {h8 if h8 else 'empty'}")
# 12th house = dissolution, escapism
h12 = whole_sign_house.get(12, [])
print(f"  H12 (dissolution/escapism): {h12 if h12 else 'empty'}")
# 7th house = partnership reality
h7 = whole_sign_house.get(7, [])
print(f"  H7 (partnership): {h7 if h7 else 'empty'}")

# Rahu/Ketu axis
print(f"\n  Rahu: {chart_obj.planets['Rahu'].sign} {chart_obj.planets['Rahu'].degree:.2f}° (H{int((natal['Rahu']-lagna_deg)/30)%12+1})")
print(f"  Ketu: {chart_obj.planets['Ketu'].sign} {chart_obj.planets['Ketu'].degree:.2f}° (H{int((natal['Ketu']-lagna_deg)/30)%12+1})")

# Is Rahu associated with deception? H12 Rahu = escapism, not necessarily deception
print(f"\n  8th lord: {(signs[(signs.index(chart_obj.ascendant_sign)+7)%12])} (Scorpio) -> lord Mars")
print(f"  8th lord placement: Mars in {chart_obj.planets['Mars'].sign} H{chart_obj.planets['Mars'].house} (Gemini H4)")

# D9 analysis for relationship truth
print("\n=== D9 (NAVAMSHA) CHECK — relationship authenticity ===")
# Check if navamsa chart available in chart_dict
if 'navamsa' in chart_dict:
    nav = chart_dict['navamsa']
    print(f"  Navamsa lagna: {nav.get('lagna', 'N/A')}")
else:
    print("  Navamsa data not in chart_dict")

# Let's manually compute Navamsa
print("\n=== MANUAL NAVAMSHA (from natal positions) ===")
def calc_navamsa(lon):
    """Navamsa: Each sign divided into 9 parts of 3°20' each"""
    sign_idx = int(lon / 30)
    deg_in_sign = lon % 30
    nav_part = int(deg_in_sign / (30/9))  # 0-8
    # Navamsa sign = (nav_part + offset) where offset depends on sign parity
    nav_sign_idx = (nav_part + (sign_idx % 3) * 3) % 12  # Simplified - but for movable signs etc.
    return signs[nav_sign_idx]

# More accurate: for fire signs navamsa starts from same sign, earth from next, etc.
def accurate_navamsa(lon):
    sign_idx = int(lon / 30)
    deg_in_sign = lon % 30
    # Each sign is 30°, navamsa is 3°20'
    nav_part = int(deg_in_sign / (30/9))
    # From BPHS: navamsa for movable signs starts at own sign, fixed at 9th, dual at 5th
    sign_type = sign_idx % 3  # 0=movable, 1=fixed, 2=dual
    if sign_type == 0:  # movable (Aries, Cancer, Libra, Capricorn)
        start = sign_idx
    elif sign_type == 1:  # fixed (Taurus, Leo, Scorpio, Aquarius)
        start = (sign_idx + 8) % 12
    else:  # dual (Gemini, Virgo, Sagittarius, Pisces)
        start = (sign_idx + 4) % 12
    nav_sign = (start + nav_part) % 12
    return signs[nav_sign]

print("  Navamsa positions:")
for name, lon in natal.items():
    print(f"    {name:7s}: {accurate_navamsa(lon)}")

# 7th lord in navamsa?
print(f"\n  D9 7th house lord sign: 7th from D9 Lagna")

# Check marriage/relationship reality: Venus condition
print("\n=== VENUS CONDITION (authenticity of love/attraction) ===")
venus = chart_obj.planets['Venus']
print(f"  Venus: {venus.sign} {venus.degree:.2f}° H{venus.house}")
print(f"  Venus aspects: check if combust/debilitated")
venus_lon = natal['Venus']
sun_lon = natal['Sun']
merc_lon = natal['Mercury']
ven_sun_dist = abs(venus_lon - sun_lon) % 360
if ven_sun_dist > 180: ven_sun_dist = 360 - ven_sun_dist
print(f"  Venus-Sun distance: {ven_sun_dist:.2f}° (combust if <10)")

print("\n=== 7TH HOUSE LORD CONDITION (partnership truth) ===")
merc = chart_obj.planets['Mercury']
print(f"  7th lord Mercury: {merc.sign} {merc.degree:.2f}° H{merc.house}")
print(f"  Mercury combust: {merc.is_combust if hasattr(merc, 'is_combust') else 'check'}")
print(f"  Mercury debilitated: {'YES - Pisces' if merc.sign == 'Pisces' else 'NO'}")
print(f"  Mercury retrograde: {getattr(merc, 'retrograde', False)}")

# Check if Venus/Mercury/Moon conjunctions create self-deception vs external deception
print("\n=== ASPECT ANALYSIS (relationship honesty) ===")
# Who aspects the 7th house / 7th lord?
# 7th house is Virgo. Virgo lord Mercury in Pisces H1.
# Saturn aspects?
print("  Saturn (Leo, H6) aspects:")
for target, desc in [(360+0, "H12 Sag"), (360+90, "H2 Aries"), (360+150, "H7 Virgo")]:
    pass

# Let's compute Saturn's aspects (3rd, 7th, 10th from itself)
sat_lon = natal['Saturn']
for asp_offset in [60, 120, 180]:
    asp_lon = (sat_lon + asp_offset) % 360
    h = int((asp_lon - lagna_deg) / 360 * 12) + 1
    print(f"  Saturn {asp_offset}° aspect -> {signs[int(asp_lon/30)]} {asp_lon%30:.1f}° (H{h})")

print("\n=== TRANSIT SATURN ASPECTS TODAY (Sep 15, 2026) ===")
tz_warsaw = pytz.timezone('Europe/Warsaw')
now_local = tz_warsaw.localize(datetime(2026, 9, 15, 12, 0))
now_utc = now_local.astimezone(pytz.utc)
jd = swe.julday(now_utc.year, now_utc.month, now_utc.day, now_utc.hour + now_utc.minute/60.0)
res_sat, _ = swe.calc_ut(jd, swe.SATURN, flags)
transit_sat = res_sat[0]
print(f"  Transit Saturn: {signs[int(transit_sat/30)]} {transit_sat%30:.2f}°")
for asp_offset in [60, 120, 180]:
    asp_lon = (transit_sat + asp_offset) % 360
    h = int((asp_lon - lagna_deg) / 360 * 12) + 1
    print(f"    Saturn {asp_offset}° aspect -> {signs[int(asp_lon/30)]} {asp_lon%30:.1f}° (H{h})")

# Transit Saturn to natal planets
print("\n--- Transit Saturn to natal planets (aspects) ---")
for pname, plon in natal.items():
    diff = abs(transit_sat - plon)
    if diff > 180: diff = 360 - diff
    if diff < 10:
        print(f"  Saturn CONJUNCT natal {pname} ({diff:.2f}°)")
    elif 55 < diff < 70:
        print(f"  Saturn SEXTILE natal {pname} ({diff:.2f}°)")
    elif 110 < diff < 130:
        print(f"  Saturn TRINE natal {pname} ({diff:.2f}°)")
    elif 165 < diff < 195:
        print(f"  Saturn OPPOSITE natal {pname} ({diff:.2f}°)")
    elif 80 < diff < 100:
        print(f"  Saturn SQUARE natal {pname} ({diff:.2f}°)")

# Transit Rahu position
res_rahu, _ = swe.calc_ut(jd, Config.node_swe_id(), flags)
transit_rahu = res_rahu[0]
print(f"\n  Transit Rahu: {signs[int(transit_rahu/30)]} {transit_rahu%30:.2f}° (H{int((transit_rahu-lagna_deg)/30)%12+1})")

# What aspects are on her 7th house (Virgo)?
print("\n=== 7TH HOUSE VIRGO — WHO'S TOUCHING IT? ===")
# 7th house cusp = Virgo (150° from Pisces lagna). Actually H7 = Virgo 0-30°
h7_start = (lagna_deg + 180) % 360
print(f"  7th house cusp: {signs[int(h7_start/30)]} {h7_start%30:.2f}°")
for pname, plon in natal.items():
    diff7 = abs(plon - h7_start)
    if diff7 > 180: diff7 = 360 - diff7
    if diff7 < 15:
        print(f"  Natal {pname} near 7th cusp ({diff7:.2f}°)")

# Dasha check
print("\n=== DASHA (current) ===")
print("  Mahadasha: Mercury (7th lord, combust+debilitated in H1)")
print("  Antardasha: Sun (6th lord)")
print("  => Relationship and communication are under maximum stress")