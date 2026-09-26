import sys
sys.path.insert(0, r"E:\ASTROLOGY AI")

import swisseph as swe
from config import Config
from astrology_engine import ZODIAC_SIGNS

swe.set_sid_mode(Config.ayanamsha_swe_id())

signs = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

# Ania's natal positions (from engine, verified)
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

# ============================================
# DREKKANA (D3) — THE CHART OF PHYSICAL BODY / CONSTITUTION
# Classic rule: Drekkana = 1/3 of a sign (10° each)
# Fire signs start from fire sign itself, earth from 9th, air from 5th (in sign)
# Actually standard: for every sign, first drekkana = own sign, second = 5th from it, third = 9th from it
# ============================================
def drekkana(lon):
    sign_idx = int(lon / 30)
    deg_in_sign = lon % 30
    drekkana_num = int(deg_in_sign / 10)  # 0,1,2
    # Drekkana sign: 1st = own, 2nd = 5th from own, 3rd = 9th from own
    offsets = [0, 4, 8]
    drek_sign = (sign_idx + offsets[drekkana_num]) % 12
    return signs[drek_sign], drekkana_num + 1

print("=== DREKKANA (D3) — PHYSICAL CONSTITUTION/APPEARANCE CHART ===")
print("(D3 rules physical body: build, flesh, weight, health)\n")
d3_planets = {}
for pname, plon in natal.items():
    d3_sign, dnum = drekkana(plon)
    d3_planets[pname] = (d3_sign, plon % 30)
    print(f"  {pname:7s}: D3 {d3_sign:12s} (Drekkana {dnum})")

d3_lagna, _ = drekkana(lagna)
print(f"  LAGNA : D3 {d3_lagna}")

print("\n=== BODY TYPE RULES (Parashari classic) ===")
print("""
RULE 1 — ELEMENT/PRAKRITI (natural constitution):
  • Watery signs (Cancer, Scorpio, Pisces)  = Kapha: soft, fleshy, curvy, full figure
  • Earthy (Taurus, Virgo, Capricorn)        = sturdy, well-proportioned, solid
  • Fiery (Aries, Leo, Sagittarius)          = medium, athletic, lean-muscular
  • Airy (Gemini, Libra, Aquarius)           = thin, lean, slender, wiry
""")

# Count planets by element
elements = {'Fire': 0, 'Earth': 0, 'Air': 0, 'Water': 0}
sign_element = {
    'Aries':'Fire','Leo':'Fire','Sagittarius':'Fire',
    'Taurus':'Earth','Virgo':'Earth','Capricorn':'Earth',
    'Gemini':'Air','Libra':'Air','Aquarius':'Air',
    'Cancer':'Water','Scorpio':'Water','Pisces':'Water'
}
print("=== NATAL CHART ELEMENT DISTRIBUTION ===")
for pname, plon in natal.items():
    s = signs[int(plon/30)]
    elements[sign_element[s]] += 1
    print(f"  {pname:7s}: {s} ({sign_element[s]})")
print(f"\n  TOTALS: {elements}")
print(f"  => WATER DOMINANCE: {elements['Water']} of 9 bodies in water signs")

print("\n=== BODY TYPE VERDICT FROM NATAL CHART ===")
water_count = elements['Water']
if water_count >= 4:
    verdict = "FULL / SOFT / CURVY body type (Kapha-dominant) — fleshy, rounded, womanly build"
elif water_count >= 2:
    verdict = "SOFT-LEAN hybrid — some fleshiness but not heavy"
else:
    verdict = "LEANER type"
print(f"  {verdict}")

print("\n=== D3 (DREKKANA) BODY-RULER ANALYSIS ===")
# In D3, the strongest ruler of body = planets in water signs again + the D3 lagna
d3_water = 0
for pname, (d3s, dnum) in d3_planets.items():
    if sign_element[d3s] == 'Water':
        d3_water += 1
print(f"  D3 planets in water signs: {d3_water} of 9")
print(f"  D3 Lagana: {d3_lagna} ({sign_element[d3_lagna]})")
if sign_element[d3_lagna] == 'Water':
    print("  => D3 Lagna in water = fleshier constitution confirmed")

print("\n=== THE DIRECT ANSWER ===")
print(f"""
  Natal: {water_count}/9 planets in WATER signs (incl. Sun, Moon, Venus, Mercury — all 4 in Pisces)
  D3:    {d3_water}/9 in water; D3 lagna in {d3_lagna} ({sign_element[d3_lagna]})

  By the classical rules, this is a KAPHA (water)-dominant chart:
  -> soft, rounded, fuller, curvy, womanly body
  -> NOT skinny, NOT athletic-lean
  -> flesh distributes gently (hips, thighs, bust, soft face)
  -> if she gains weight, it shows as soft fullness, not hard bulk
  -> the "fat" question: she is likely FULLER-FIGURED / curvy, but the chart
     describes proportioned softness more than clinical obesity.
""")

print("=== HONEST CAVEATS ===")
print("""
1. This is archetype, not BMI. Classical astrology gives body TYPE, not pounds.
2. It presumes the birth data is REAL (April 5, 2008, 06:15, Bytom).
3. Lifestyle (gym, walking, sports) can shift any archetype leaner.
   Her own messages mention gym and driving lessons.
4. The chart says 'curvy/soft' — a real girl with this chart + body insecurity
   is EXACTLY the girl who hides from video calls.
""")