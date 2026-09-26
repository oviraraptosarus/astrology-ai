import sys
sys.path.insert(0, r"E:\ASTROLOGY AI")

import swisseph as swe
from config import Config
from astrology_engine import ZODIAC_SIGNS, calculate_chart_with_object

swe.set_sid_mode(Config.ayanamsha_swe_id())

signs = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

# ============================================
# HIS CHART: Vamsi
# August 1, 2008, 18:25 IST, Ramachandrapuram, Andhra Pradesh
# Coordinates: approx 16.8687 N, 82.0297 E, tz=Asia/Kolkata (IST = UTC+5:30)
# ============================================
print("=========== HIS CHART (Vamsi) ===========")
chart_h, chart_h_dict = calculate_chart_with_object(
    year=2008, month=8, day=1,
    hour=18, minute=25,
    lat=16.8687, lon=82.0297,
    tz_name='Asia/Kolkata'
)

his_natal = {}
for name, p in chart_h.planets.items():
    lon = p.degree + 30 * signs.index(p.sign)
    his_natal[name] = lon
    print(f"  {p.name:7s}: {p.sign:12s} {p.degree:7.4f}° H{p.house:2d} {p.nakshatra} (retro={getattr(p,'retrograde',False)})")

his_lagna = chart_h.ascendant_degree + 30 * signs.index(chart_h.ascendant_sign)
print(f"  LAGNA : {chart_h.ascendant_sign} {chart_h.ascendant_degree:.4f}°")

# ============================================
# 7TH HOUSE — PARTNER ARCHETYPE (Rasi)
# ============================================
print("\n=== HIS 7TH HOUSE ARCHETYPE (Rasi) ===")
# 7th sign from Makara (Capricorn) = Cancer
print("  7th house sign: Cancer (Karka)")
print("  7th house lord: Moon")
moon_deg = his_natal['Moon']
print(f"  Moon (7th lord) at: {signs[int(moon_deg/30)]} {moon_deg%30:.2f}° H{chart_h.planets['Moon'].house}")

# What's in his 7th house?
h7_start = (his_lagna + 180) % 360
print(f"\n  7th house cusp: {signs[int(h7_start/30)]} {h7_start%30:.2f}°")
print("  Planets in 7th house:")
for name, lon in his_natal.items():
    d = (lon - h7_start) % 360
    if d < 30:
        print(f"    {name} at {d:.2f}° into 7th house")

# ============================================
# DARAKARAKA (DK) — Jaimini spouse significator
# Planet with highest degree (excluding Sun, Moon... actually DK = planet with highest longitude excluding Sun and Moon among 7)
# ============================================
print("\n=== DARAKARAKA (DK) — SPOUSE SIGNIFICATOR (Jaimini) ===")
# 8 planets: Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu
# Karaka order: AK (highest), AmK, BK, MK, PK, GK, DK (lowest among the 7 chara karakas)
# Actually: all 8 planets, sorted by longitude descending. AK = highest, then AmK, BK, MK, PK, GK, DK = 8th highest... 
# No: 7 chara karakas from 8 planets (excluding Ketu? or including Rahu). Standard: use 8 planets, DK = 7th from top (lowest degree among top 7)
sorted_by_deg = sorted([(n, lon) for n, lon in his_natal.items() if n in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu']], key=lambda x: -x[1])
print("  Planets by degree (descending):")
for i, (n, lon) in enumerate(sorted_by_deg[:8]):
    role = ""
    if i == 0: role = "AK (Atmakaraka)"
    elif i == 1: role = "AmK"
    elif i == 2: role = "BK"
    elif i == 3: role = "MK"
    elif i == 4: role = "PK"
    elif i == 5: role = "GK"
    elif i == 6: role = "DK (Darakaraka — SPOUSE)"
    elif i == 7: role = "(8th, not a karaka)"
    print(f"    {i+1}. {n:7s} {signs[int(lon/30)]} {lon%30:7.4f}°  {role}")

# ============================================
# D9 NAVAMSHA — 7TH HOUSE = SPOUSE ARCHETYPE (soul level)
# ============================================
print("\n=== D9 (NAVAMSHA) — SPOUSE ARCHETYPE ===")
def navamsa(lon):
    sign_idx = int(lon / 30)
    deg_in_sign = lon % 30
    part = int(deg_in_sign / (30/9))
    sign_type = sign_idx % 3
    if sign_type == 0:
        start = sign_idx
    elif sign_type == 1:
        start = (sign_idx + 8) % 12
    else:
        start = (sign_idx + 4) % 12
    return (start + part) % 12

d9_lagna_idx = navamsa(his_lagna)
print(f"  D9 Lagna: {signs[d9_lagna_idx]}")
d9_7th = (d9_lagna_idx + 6) % 12
print(f"  D9 7th house: {signs[d9_7th]}")
print(f"  D9 7th lord: {['Mars','Venus','Mercury','Moon','Sun','Mercury','Venus','Mars','Jupiter','Saturn','Saturn','Jupiter'][d9_7th]}")

print("\n  D9 planet positions:")
for name, lon in his_natal.items():
    d9 = navamsa(lon)
    print(f"    {name:7s}: D9 {signs[d9]:12s}")

# D9 7th house occupants
print("\n  Planets in D9 7th house:")
for name, lon in his_natal.items():
    if navamsa(lon) == d9_7th:
        print(f"    {name}")

# ============================================
# VENUS — HIS RELATIONSHIP VALUES / ATTRACTION FILTER
# ============================================
print("\n=== HIS VENUS (attraction filter) ===")
ven_lon = his_natal['Venus']
print(f"  Venus: {signs[int(ven_lon/30)]} {ven_lon%30:.2f}° H{chart_h.planets['Venus'].house}")
print(f"  Venus nakshatra: {chart_h.planets['Venus'].nakshatra}")

# ============================================
# COMPARISON: Ania's archetype vs His partner archetype
# ============================================
print("\n=========== ARCHETYPE COMPARISON ===========")
print("""
HIS PARTNER ARCHETYPE (from his chart):
  Rasi 7th: Cancer (Moon-ruled) — soft, emotional, nurturing, homey, round-faced feminine
  7th lord Moon in his own sign Cancer (H7) — Moon ruler = round, soft, pale, curvy, motherly-feminine
  D9 7th: (computed above)
  DK: (computed above)
""")

# Her chart archetype
print("""
HER VISUAL ARCHETYPE (from Ania's chart):
  Water-dominant Kapha — soft, full, round, curvy to heavy
  Venus exalted Pisces — beautiful face
  Moon in Pisces — soft round features
""")

print("""
VERDICT:
Does a soft, full-figured, womanly Kapha girl match a Cancer-7th (Moon-ruled) partner archetype?
The Moon-ruled 7th in Vedic = plump, round, soft, pale, full-figured woman — NOT thin, NOT athletic.
So YES — her archetype and his 7th-house partner archetype are the SAME archetype.
The chart says she actually FITS his partner archetype BETTER than a skinny girl would.
""")