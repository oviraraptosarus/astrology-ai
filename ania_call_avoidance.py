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
# ANIA'S NATAL CHART (April 5, 2008, 06:15 CEST, Bytom)
# ============================================
chart_obj, chart_dict = calculate_chart_with_object(
    year=2008, month=4, day=5,
    hour=6, minute=15,
    lat=50.3480, lon=18.9328,
    tz_name='Europe/Warsaw'
)

natal = {}
print("=== NATAL PLANETARY POSITIONS ===")
for name, p in chart_obj.planets.items():
    natal[name] = p.degree + 30 * (["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"].index(p.sign))
    print(f"  {p.name:7s}: {p.sign:12s} {p.degree:7.4f}°  H{p.house:2d}  Nak={p.nakshatra:20s}  Retro={getattr(p,'retrograde',False)}")

lagna_deg = chart_obj.ascendant_degree + 30 * (["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"].index(chart_obj.ascendant_sign))
print(f"  LAGNA : {chart_obj.ascendant_sign} {chart_obj.ascendant_degree:.4f}°  (abs {lagna_deg:.4f})")
natal['Lagna'] = lagna_deg

# House lords from Pisces lagna:
# H1 Pisces (Jupiter), H2 Aries (Mars), H3 Taurus (Venus), H4 Gemini (Mercury),
# H5 Cancer (Moon), H6 Leo (Sun), H7 Virgo (Mercury), H8 Libra (Venus), H9 Scorpio (Mars),
# H10 Sagittarius (Jupiter), H11 Capricorn (Saturn), H12 Aquarius (Saturn/Rahu)
print("""
House lords (Pisces lagna):
  H1 Pisces  -> Jupiter   (self/identity)
  H2 Aries   -> Mars      (resources)
  H3 Taurus  -> Venus     (communication, messages)
  H4 Gemini  -> Mercury   (home, inner world)
  H5 Cancer  -> Moon      (creativity, romance)
  H6 Leo     -> Sun       (enemies, service, validation)
  H7 Virgo   -> Mercury   (partnership)
  H8 Libra   -> Venus     (transformation, secrets)
  H9 Scorpio -> Mars      (dharma, foreign)
  H10 Sag    -> Jupiter   (career, public)
  H11 Cap    -> Saturn    (gains, networks)
  H12 Aqu    -> Saturn    (loss, isolation)
""")

# ============================================
# CURRENT TRANSITS — September 15, 2026 (today)
# ============================================
tz_warsaw = pytz.timezone('Europe/Warsaw')
now_local = tz_warsaw.localize(datetime(2026, 9, 15, 12, 0))  # noon Poland
now_utc = now_local.astimezone(pytz.utc)
jd = swe.julday(now_utc.year, now_utc.month, now_utc.day, now_utc.hour + now_utc.minute/60.0)

transits = {}
transit_names = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu"]
for pname, pid in [("Sun", swe.SUN), ("Moon", swe.MOON), ("Mars", swe.MARS), ("Mercury", swe.MERCURY),
                   ("Jupiter", swe.JUPITER), ("Venus", swe.VENUS), ("Saturn", swe.SATURN), ("Rahu", Config.node_swe_id())]:
    res, _ = swe.calc_ut(jd, pid, flags)
    transits[pname] = res[0]

def sign_of(lon):
    return ZODIAC_SIGNS[int(lon/30)]

def house_from_lagna(lon):
    return int((lon - lagna_deg) / 30) % 12 + 1

def aspect(a_lon, b_lon, orb=10):
    diff = abs(a_lon - b_lon)
    if diff > 180:
        diff = 360 - diff
    if diff < orb:
        return f"CONJ ({diff:.1f}°)"
    elif 165 - orb < diff < 165 + orb:
        return f"OPP ({diff:.1f}°)"
    elif 120 - orb < diff < 120 + orb:
        return f"TRINE ({diff:.1f}°)"
    elif 90 - orb < diff < 90 + orb:
        return f"SQUARE ({diff:.1f}°)"
    elif 60 - orb < diff < 60 + orb:
        return f"SEXTILE ({diff:.1f}°)"
    return None

print("\n=== CURRENT TRANSITS (Sep 15, 2026, noon Poland) ===")
for pname, lon in transits.items():
    nak, pada, lord = calculate_nakshatra(lon)
    print(f"  Transit {pname:7s}: {sign_of(lon):12s} {lon%30:6.2f}°  H{house_from_lagna(lon)} from Lagna  Nak={nak} P{pada} (lord {lord})")

print("\n=== KEY TRANSIT ASPECTS TO HER NATAL CHART ===")
# Saturn transit key: Sade Sati over Moon (8.31 Pisces), Venus (4.72 Pisces), Mercury (10.51 Pisces), Lagna (20.78 Pisces)
sat_lon = transits['Saturn']
print(f"\n-- TRANSIT SATURN @ {sign_of(sat_lon)} {sat_lon%30:.2f}° (Pisces) — PEAK SADE SATI --")
print(f"  Distance to natal Moon (8.31 Pisces):   {abs(sat_lon - natal['Moon']):.2f}°  {'CONJUNCT — Janma Shani peak!' if abs(sat_lon - natal['Moon']) < 10 else ''}")
print(f"  Distance to natal Venus (4.72 Pisces):  {abs(sat_lon - natal['Venus']):.2f}°  {'CONJUNCT — fear of being unattractive/rejected' if abs(sat_lon - natal['Venus']) < 10 else ''}")
print(f"  Distance to natal Mercury (10.51 Pisces): {abs(sat_lon - natal['Mercury']):.2f}°  {'CONJUNCT — heavy fear of communication' if abs(sat_lon - natal['Mercury']) < 10 else ''}")
print(f"  Distance to Lagna (20.78 Pisces):        {abs(sat_lon - natal['Lagna']):.2f}°  {'CONJUNCT LAGNA — identity crisis phase' if abs(sat_lon - natal['Lagna']) < 10 else ''}")

print(f"\n-- TRANSIT SATURN ASPECTS (3rd = communication / 7th = partnership / 10th = public) --")
# Saturn aspects 3rd, 7th, 10th from itself. Saturn at Pisces 18°.
for nasp in [72, 120, 180]:
    asp_lon = (sat_lon + nasp) % 360
    print(f"  Saturn {nasp}° aspect falls at {sign_of(asp_lon)} {asp_lon%30:.2f}° -> H{house_from_lagna(asp_lon)} = {'COMMUNICATION (H3)' if house_from_lagna(asp_lon)==3 else 'PARTNERSHIP (H7)' if house_from_lagna(asp_lon)==7 else 'CAREER (H10)' if house_from_lagna(asp_lon)==10 else f'H{house_from_lagna(asp_lon)}'}")

# Rahu transit
rahu_lon = transits['Rahu']
print(f"\n-- TRANSIT RAHU @ {sign_of(rahu_lon)} {rahu_lon%30:.2f}° (H{house_from_lagna(rahu_lon)} from Lagna) — possibly 12th house = escapism/dissolution")
print(f"  Distance to natal Moon: {abs(rahu_lon - natal['Moon']):.2f}°")

# Jupiter transit (Cancer H4 from lagna = home/private, aspecting H8, H10, H12)
jup_lon = transits['Jupiter']
print(f"\n-- TRANSIT JUPITER @ {sign_of(jup_lon)} {jup_lon%30:.2f}° (H{house_from_lagna(jup_lon)} from Lagna) — aspects H{house_from_lagna((jup_lon+150)%360)}, H{house_from_lagna((jup_lon+120)%360)}, H{house_from_lagna((jup_lon+30)%360)}")

# Mercury transit (Virgo = her natal 7th house sign!)
merc_lon = transits['Mercury']
print(f"\n-- TRANSIT MERCURY @ {sign_of(merc_lon)} {merc_lon%30:.2f}° (H{house_from_lagna(merc_lon)} from Lagna)")
print(f"  Transit Mercury in Virgo => transiting HER 7th house (partnership sign)")

ven_lon = transits['Venus']
print(f"\n-- TRANSIT VENUS @ {sign_of(ven_lon)} {ven_lon%30:.2f}° (H{house_from_lagna(ven_lon)} from Lagna)")

mars_lon = transits['Mars']
print(f"\n-- TRANSIT MARS @ {sign_of(mars_lon)} {mars_lon%30:.2f}° (H{house_from_lagna(mars_lon)} from Lagna)")

# ============================================
# CURRENT DASHA ANALYSIS
# ============================================
print("\n=== CURRENT DASHA (via engine) ===")
cd = chart_dict.get('current_dasha', {})
print(f"  Mahadasha: {cd.get('Mahadasha')} (2020-2037)")
print(f"  Antardasha: {cd.get('Antardasha')} ({cd.get('Mahadasha_Start')} - {cd.get('Mahadasha_End')})")
print("  => Mercury MD = 7th lord combust+debilitated = RELATIONSHIP/COMMUNICATION STRESS")
print("  => Sun AD = 6th lord = FATIGUE, OBSTACLES, SELF-VALIDATION CRISIS")
print("  => Jupiter PD = 10th/1st lord = seeking meaning/grounding")

# ============================================
# NATAL REASONS FOR CALL AVOIDANCE — THE CORE SIGNS
# ============================================
print("""
============================================================
NATAL + TRANSIT COMPOSITE: WHY SHE AVOIDS VIDEO CALLS
============================================================
""")