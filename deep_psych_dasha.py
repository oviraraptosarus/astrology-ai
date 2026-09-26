import sys, os, json, datetime
import swisseph as swe

sys.path.insert(0, r"E:\ASTROLOGY AI")

from astrology_engine import calculate_chart_with_object
from dasha_engine import DashaEngine
from dosha_engine import DoshaEngine

# B (her): 2008-04-05 06:15 CEST, Bytom Poland (50.348N, 18.916E)
c, _ = calculate_chart_with_object(2008, 4, 5, 6, 15, 50.348, 18.916, "Europe/Warsaw")

ZODIAC = ['Aries','Taurus','Gemini','Cancer','Leo','Virgo','Libra','Scorpio','Sagittarius','Capricorn','Aquarius','Pisces']

# Dasha timeline
print("=== VIMSHOTTARI DASHA TIMELINE ===")
deng = DashaEngine()
birth_utc = datetime.datetime(2008, 4, 5, 4, 15, 0)
moon_lon = c.planets['Moon'].degree + ZODIAC.index(c.planets['Moon'].sign) * 30
timeline = deng.calculate_vimshottari_timeline(birth_utc, moon_lon)

for md in timeline:
    print(f"\nMD: {md['lord']:8s} {md['start'][:10]} to {md['end'][:10]}")
    for ad in md.get("sub_periods", []):
        print(f"   AD: {ad['lord']:8s} ({ad['start'][:10]} to {ad['end'][:10]})")
        for pd in ad.get("sub_periods", []):
            pass  # skip PD for brevity

curr = deng.get_current_dasha(timeline, datetime.datetime(2026, 9, 13))
print(f"\nCurrent (Sep 2026): MD={curr['mahadasha']}, AD={curr['antardasha']}, PD={curr['pratyantardasha']}")

# Doshas
print("\n=== DOSHAS ===")
de = DoshaEngine(c)
doshas = de.evaluate_all(datetime.datetime(2026, 9, 13, 12, 0))
print(json.dumps(doshas, indent=2, default=str))

# Additional info from chart object
print("\n=== ASHTAKAVARGA FROM CHART OBJECT ===")
sav = c.sarvashtakavarga
if sav:
    print("Sarvashtakavarga:", json.dumps(sav, indent=2, default=str))
bav = c.bhinna_ashtakavarga
if bav:
    print("Bhinna:", json.dumps(bav, indent=2, default=str))

print("\n=== BUILT-IN CURRENT DASHA FROM CHART ===")
print(json.dumps(c.current_dasha, indent=2, default=str))

print("\n=== COMBUSTION / PLANETARY WAR ===")
for p, obj in c.planets.items():
    if hasattr(obj, 'combustion') and obj.combustion.get('status'):
        print(f"  {p}: COMBUST (sun distance: {obj.combustion.get('sun_distance')}°)")
    if hasattr(obj, 'planetary_war') and obj.planetary_war.get('in_war'):
        print(f"  {p}: IN WAR with {obj.planetary_war.get('with_planet')}, winner={obj.planetary_war.get('is_winner')}")

print("\n=== DISPOSITOR CHAINS ===")
for p, obj in c.planets.items():
    print(f"  {p}: dispositor={obj.dispositor}, chain={getattr(obj, 'dispositor_chain', '')}, parivartana={obj.is_parivartana}, vargottama={obj.is_vargottama}")

print("\n=== CONJUNCTIONS & ASPECTS ===")
for p, obj in c.planets.items():
    print(f"  {p}: conjunct={obj.conjunct_with}, aspects_houses={obj.aspects_houses}, aspected_by={obj.aspected_by}")

print("\n=== FUNCTIONAL ROLES & FRIENDSHIPS ===")
for p, obj in c.planets.items():
    print(f"  {p}: role={obj.functional_role}, owns_houses={obj.owns_houses}, detailed_roles={obj.detailed_functional_roles}, compound_friends={obj.compound_friendships}")
