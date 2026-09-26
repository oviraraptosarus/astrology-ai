import sys
sys.path.insert(0, r"E:\ASTROLOGY AI")

import swisseph as swe
from config import Config
from astrology_engine import calculate_chart_with_object, ZODIAC_SIGNS

signs = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

swe.set_sid_mode(Config.ayanamsha_swe_id())

# HIS CHART: Aug 1, 2008, 18:25 IST, Ramachandrapuram (16.8687 N, 82.0297 E)
chart_h, chart_h_dict = calculate_chart_with_object(
    year=2008, month=8, day=1,
    hour=18, minute=25,
    lat=16.8687, lon=82.0297,
    tz_name='Asia/Kolkata'
)

his_natal = {}
for name, p in chart_h.planets.items():
    his_natal[name] = p.degree + 30 * signs.index(p.sign)

lagna_deg = chart_h.ascendant_degree + 30 * signs.index(chart_h.ascendant_sign)
print(f"Lagna: {chart_h.ascendant_sign} {chart_h.ascendant_degree:.2f}°")

def sign_of(lon):
    return signs[int(lon/30)]

def calc_upapada(lagna_lon, planets_lon):
    """Upapada Lagna (UL): 12th from lagna, count lord's sign distance from 12th, add same to lord's sign."""
    h12_sign_idx = (int(lagna_lon/30) + 11) % 12  # 12th sign from lagna
    h12_sign = signs[h12_sign_idx]
    # Lord of 12th sign
    lords = {'Aries':'Mars','Taurus':'Venus','Gemini':'Mercury','Cancer':'Moon','Leo':'Sun',
             'Virgo':'Mercury','Libra':'Venus','Scorpio':'Mars','Sagittarius':'Jupiter','Capricorn':'Saturn',
             'Aquarius':'Saturn','Pisces':'Jupiter'}
    h12_lord = lords[h12_sign]
    lord_sign_idx = int(planets_lon[h12_lord] / 30)
    # Count from 12th sign to lord's sign (1-based)
    distance = (lord_sign_idx - h12_sign_idx) % 12
    if distance == 0: distance = 12
    # Go that many signs from lord's sign
    ul_sign_idx = (lord_sign_idx + distance - 1) % 12
    return signs[ul_sign_idx], h12_sign, h12_lord, distance

ul_sign, h12_sig, h12_lord, dist = calc_upapada(lagna_deg, his_natal)
print(f"12th house sign: {h12_sig} (lord {h12_lord})")
print(f"12th lord {h12_lord} in {sign_of(his_natal[h12_lord])}, distance from 12th = {dist}")
print(f"\n>>> UPAPADA LAGNA (UL / A7) = {ul_sign} <<<")

# Arudha Lagna
def calc_arudha(lagna_lon):
    """AL: count from lagna lord's sign to lagna, same distance from lord's sign."""
    lords = {'Aries':'Mars','Taurus':'Venus','Gemini':'Mercury','Cancer':'Moon','Leo':'Sun',
             'Virgo':'Mercury','Libra':'Venus','Scorpio':'Mars','Sagittarius':'Jupiter','Capricorn':'Saturn',
             'Aquarius':'Saturn','Pisces':'Jupiter'}
    lagna_sign_idx = int(lagna_lon / 30)
    lagna_sign = signs[lagna_sign_idx]
    lagna_lord = lords[lagna_sign]
    lord_sign_idx = int(his_natal[lagna_lord] / 30)
    # Count from lord sign to lagna sign
    dist = (lagna_sign_idx - lord_sign_idx) % 12
    if dist == 0: dist = 12
    al_sign_idx = (lord_sign_idx + dist - 1) % 12
    return signs[al_sign_idx], lagna_lord

al_sign, lagna_lord = calc_arudha(lagna_deg)
print(f"Lagna lord: {lagna_lord} in {sign_of(his_natal[lagna_lord])}")
print(f">>> ARUDHA LAGNA (AL) = {al_sign} <<<")

# Chara karakas (Jaimini)
print("\n=== CHARA KARAKAS ===")
karakas = sorted([(n, his_natal[n]) for n in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu']], key=lambda x: -x[1])
names = ['AK (Atmakaraka)', 'AmK', 'BK', 'MK', 'PK', 'GK', 'DK (Darakaraka)']
for i, (n, lon) in enumerate(karakas[:7]):
    print(f"  {n:7s} {sign_of(lon):12s} {lon%30:6.2f}° = {names[i]}")

dk = karakas[6][0]
dk_sign = sign_of(karakas[6][1])
dk_nakshatra_lord = None
print(f"\nDK = {dk} in {dk_sign}")

# DK's nakshatra to determine spouse archetype (Jaimini dictates)
nakshatras = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]
dk_lon = karakas[6][1]
nak_idx = int(dk_lon / (360/27))
print(f"DK nakshatra: {nakshatras[nak_idx]} (lord = {['Ketu','Venus','Sun','Moon','Mars','Rahu','Jupiter','Saturn','Mercury'][nak_idx % 9]})")

# UL sign -> spouse family/looks; the sign in UL is what he'll get
print(f"""
=== JAIMINI READING ===""")

# UL sign interpretation
ul_idx = signs.index(ul_sign)
print(f"UPAPADA in {ul_sign}:")
if ul_sign in ['Cancer','Scorpio','Pisces']:
    print(f"  -> WATER sign = soft, emotional, round-faced, nurturing, home-oriented spouse")
elif ul_sign in ['Taurus','Virgo','Capricorn']:
    print(f"  -> EARTH sign = practical, grounded, sensual, good-looking, materially stable")
elif ul_sign in ['Aries','Leo','Sagittarius']:
    print(f"  -> FIRE sign = fiery, proud, passionate, dramatic, distinctive looks")
else:
    print(f"  -> AIR sign = intellectual, communicative, lean/lithe, social")

print(f"AL in {al_sign}:")
if ul_idx == al_idx_placeholder if False else True:
    pass

# spouse from DK sign
print(f"DK ({dk}) in {dk_sign}: " + 
      ("Moon-ruled soft, round, curvy, pale." if dk_sign=='Cancer' else 
       "Venus-ruled beautiful, artistic, sensual." if dk_sign in ['Taurus','Libra'] else
       "Jupiter-ruled noble, fair, dignified." if dk_sign in ['Sagittarius','Pisces'] else
       "Mars-ruled feisty, athletic, passionate." if dk_sign in ['Aries','Scorpio'] else
       "Saturn-ruled lean, practical, mature." if dk_sign in ['Capricorn','Aquarius'] else
       "Sun-ruled proud, regal, striking." if dk_sign=='Leo' else
       "Mercury-ruled youthful, slim, clever." if dk_sign in ['Gemini','Virgo'] else "?"))

# Jaimini navamsa karaka for spouse appearance: DK in D9
def navamsa(lon):
    si = int(lon/30); dis = lon%30; part = int(dis/(30/9)); st = si%3
    start = si if st==0 else (si+8)%12 if st==1 else (si+4)%12
    return (start+part)%12

dk_d9 = navamsa(karakas[6][1])
print(f"DK in D9: {signs[dk_d9]} — spouse's deeper nature/appearance at soul level")