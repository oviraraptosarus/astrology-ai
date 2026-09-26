import sys
sys.path.insert(0, r"E:\ASTROLOGY AI")

import swisseph as swe
from config import Config
from astrology_engine import calculate_chart_with_object, ZODIAC_SIGNS

signs = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio","Sagittarius","Capricorn","Aquarius","Pisces"]

swe.set_sid_mode(Config.ayanamsha_swe_id())

# HIS CHART
chart_h, _ = calculate_chart_with_object(year=2008, month=8, day=1, hour=18, minute=25,
    lat=16.8687, lon=82.0297, tz_name='Asia/Kolkata')
his_natal = {}
for n, p in chart_h.planets.items():
    his_natal[n] = p.degree + 30 * signs.index(p.sign)
his_lagna = chart_h.ascendant_degree + 30 * signs.index(chart_h.ascendant_sign)

# HER CHART (Ania)
chart_a, _ = calculate_chart_with_object(year=2008, month=4, day=5, hour=6, minute=15,
    lat=50.3480, lon=18.9328, tz_name='Europe/Warsaw')
her_natal = {}
for n, p in chart_a.planets.items():
    her_natal[n] = p.degree + 30 * signs.index(p.sign)
her_lagna = chart_a.ascendant_degree + 30 * signs.index(chart_a.ascendant_sign)

print("=== HER NATAL (Ania) ===")
for n in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']:
    print(f"  {n:7s}: {signs[int(her_natal[n]/30)]:12s} {her_natal[n]%30:6.2f}°")
print(f"  LAGNA: {chart_a.ascendant_sign} {chart_a.ascendant_degree:.2f}°")

print("\n=== HIS JAIMINI SPOUSE SIGNATURES ===")
print("  UL (Upapada Lagna): Scorpio")
print("  Darakaraka (DK): Moon in Cancer (Ashlesha nakshatra, lord Mercury)")
print("  DK in D9: Sagittarius")
print("  Rasi 7th house: Cancer (lord Moon)")

def navamsa(lon):
    si = int(lon/30); dis = lon%30; part = int(dis/(30/9)); st = si%3
    start = si if st==0 else (si+8)%12 if st==1 else (si+4)%12
    return (start+part)%12

def drekkana(lon):
    si = int(lon/30); dis = lon%30; dnum = int(dis/10)
    return (si + [0,4,8][dnum]) % 12

print("\n=== CORRELATION MATRIX ===")
checks = []

# 1. Element match: his spouse = Water (Cancer/Scorpio). Her element makeup?
her_water = sum(1 for n in her_natal if signs[int(her_natal[n]/30)] in ['Cancer','Scorpio','Pisces'])
checks.append(("His spouse = WATER archetype (Cancer/Scorpio)", f"Her chart has {her_water}/8 planets in water signs", her_water >= 4))

# 2. Her Lagna element vs his spouse signs
her_lag_el = signs[int(her_lagna/30)]
checks.append(("His spouse is water-sign", f"Her Lagna = {her_lag_el} (water)" , her_lag_el in ['Cancer','Scorpio','Pisces']))

# 3. DK Moon synastry: his DK (Moon in Cancer ~107°) aspects with her planets
moon_dk = his_natal['Moon']
print("\n--- Her planets ASPECTING his DK (Moon in Cancer) ---")
for n in ['Sun','Moon','Mars','Mercury','Jupiter','Venus','Saturn','Rahu','Ketu']:
    diff = abs(her_natal[n] - moon_dk)
    if diff > 180: diff = 360 - diff
    if diff < 10:
        print(f"  {n}: CONJUNCT his DK Moon ({diff:.1f}°)")
        checks.append((f"Her {n} conjunct his DK Moon", f"{diff:.1f}°", True))
    elif 108 < diff < 132:
        print(f"  {n}: TRINE his DK Moon ({diff:.1f}°)")
        checks.append((f"Her {n} trine his DK Moon", f"{diff:.1f}°", True))
    elif 78 < diff < 102:
        print(f"  {n}: SQUARE his DK Moon ({diff:.1f}°)")
        checks.append((f"Her {n} square his DK Moon", f"{diff:.1f}°", False))
    elif 165 < diff < 195:
        print(f"  {n}: OPPOSITE his DK Moon ({diff:.1f}°)")
        checks.append((f"Her {n} opposite his DK Moon", f"{diff:.1f}°", False))
    else:
        print(f"  {n}: no aspect ({diff:.1f}°)")

# 4. UL (Scorpio) correlations: her D3 lagna (body), her Mars, her D9
her_d3_lag = drekkana(her_lagna)
checks.append(("His UL = Scorpio (spouse body)", f"Her D3 (body) Lagna = {signs[her_d3_lag]}", her_d3_lag == 7))
print(f"\n  Her D3 Lagna: {signs[her_d3_lag]} (his UL is Scorpio) -> {'MATCH' if her_d3_lag==7 else 'no'}")

# 5. Her Mars (passion/spouse in her own chart) = ? His UL Scorpio lord = Mars
her_mars = her_natal['Mars']
her_mars_nak_lord = None
nakshatras = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]
nak_idx = int(her_mars/(360/27))
checks.append(("His UL lord = Mars (Scorpio)", f"Her Mars in {signs[int(her_mars/30)]} ({nakshatras[nak_idx]})", signs[int(her_mars/30)]=='Gemini'))
print(f"  Her Mars: {signs[int(her_mars/30)]} {her_mars%30:.2f}° ({nakshatras[nak_idx]})")

# 6. DK in D9 Sagittarius correlation: her Jupiter (Sagittarius) / her D9 lagna?
her_d9_lag = navamsa(her_lagna)
print(f"  Her D9 Lagna: {signs[her_d9_lag]}")
her_jup = her_natal['Jupiter']
print(f"  Her Jupiter: {signs[int(her_jup/30)]} {her_jup%30:.2f}° (his DK-in-D9 = Sagittarius)")
checks.append(("His DK-in-D9 = Sagittarius", f"Her Jupiter in {signs[int(her_jup/30)]}", signs[int(her_jup/30)]=='Sagittarius'))

# 7. Ashlesha (his DK nakshatra) correlation — her Mercury?
def nak_info(lon):
    idx = int(lon/(360/27))
    return nakshatras[idx], idx%9
her_merc_nak, her_merc_lord = nak_info(her_natal['Mercury'])
print(f"  Her Mercury nakshatra: {her_merc_nak} (lord index {her_merc_lord})")
checks.append(("His DK nakshatra = Ashlesha (Mercury)", f"Her Mercury in {her_merc_nak}", her_merc_nak=='Ashlesha'))

# 8. Her Venus — his Venus attraction (Leo/Magha = queen type)
her_ven = her_natal['Venus']
print(f"  Her Venus: {signs[int(her_ven/30)]} {her_ven%30:.2f}° Exalted")
print(f"  His Venus: {signs[int(his_natal['Venus']/30)]} {his_natal['Venus']%30:.2f}° (Magha - regal/queen filter)")
ven_diff = abs(her_ven - his_natal['Venus'])
if ven_diff > 180: ven_diff = 360 - ven_diff
print(f"  Venus-Venus distance: {ven_diff:.1f}°")

# 9. Her 7th house (Virgo) lord Mercury = his UL sign Scorpio's lord? Mercury rules her 7th...
# Correlate differently: his spouse = emotional water; her 7th lord Mercury debilitated Pisces = water.

# SCORE
print("\n\n=== SCORECARD ===")
score = 0
total = 0
for desc, evidence, match in checks:
    total += 1
    if match: score += 1
    print(f"  [{'✓' if match else '✗'}] {desc} | {evidence}")
print(f"\n  MATCH SCORE: {score}/{total}")

print("\n=== FINAL VERDICT (computed, not vibes) ===")