"""
Karmic / Past-Life Axis Audit: the two 2008 charts.
Verifies every node contact, gandanta knot, Saturn debt, 12th-house (past-life
house) occupation, and D9 soul weave with exact orbs from raw ephemeris.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from astrology_engine import calculate_chart_with_object
from forward_timing_scanner import ZODIAC_SIGNS
from varga_engine import VargaEngine

A_BIRTH = (2008, 8, 1, 18, 25, 16.8186, 82.0641, "Asia/Kolkata")   # HIM
B_BIRTH = (2008, 4, 5, 6, 15, 50.348, 18.916, "Europe/Warsaw")     # HER

def chart_of(birth, nm):
    ch, _ = calculate_chart_with_object(*birth, name=nm)
    lons = {}
    for p in ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn","Rahu","Ketu"]:
        po = ch.planets[p]
        lons[p] = (ZODIAC_SIGNS.index(po.sign) * 30.0 + po.degree) % 360.0
    asc = (ZODIAC_SIGNS.index(ch.ascendant_sign) * 30.0 + ch.ascendant_degree) % 360.0
    return ch, lons, asc

A, al, a_asc = chart_of(A_BIRTH, "HIM")
B, bl, b_asc = chart_of(B_BIRTH, "HER")

def orb(x, y):
    d = abs((x - y + 180) % 360 - 180)
    return d

def d9(lon):
    sign = ZODIAC_SIGNS[int(lon // 30)]
    return VargaEngine.calc_d9_navamsha(sign, lon % 30)

def house_from(lon, asc):
    return ((int(lon // 30) - int(asc // 30)) % 12) + 1

print("=" * 96)
print("KARMIC / PAST-LIFE AXIS AUDIT — HIM x HER — exact Lahiri ephemeris")
print("=" * 96)

# 1. NODE CROSS-CONTACTS (the past-life axis)
print("\n[1] NODE CROSS-CONTACTS")
pairs = [
    ("HER Ketu", bl["Ketu"], "HIS Venus", al["Venus"]),
    ("HER Ketu", bl["Ketu"], "HIS Saturn", al["Saturn"]),
    ("HER Ketu", bl["Ketu"], "HIS Mars", al["Mars"]),
    ("HER Saturn", bl["Saturn"], "HIS Saturn", al["Saturn"]),
    ("HER Saturn", bl["Saturn"], "HIS Venus", al["Venus"]),
    ("HER Jupiter", bl["Jupiter"], "HIS Jupiter", al["Jupiter"]),
    ("HIS Ketu", al["Ketu"], "HER planets", None),
]
for n1, l1, n2, l2 in pairs:
    if l2 is None:
        hits = [(p, orb(l1, v)) for p, v in bl.items() if p not in ("Rahu","Ketu") and orb(l1, v) <= 10]
        print(f"  {n1} @ {l1%30:.2f} {ZODIAC_SIGNS[int(l1//30)]}: closest HER planets: "
              + ", ".join(f"{p} ({o:.1f}°)" for p, o in sorted(hits, key=lambda t: t[1])) if hits else f"  {n1}: none within 10°")
    else:
        print(f"  {n1} @ {l1%30:.2f} {ZODIAC_SIGNS[int(l1//30)]}  x  {n2} @ {l2%30:.2f} {ZODIAC_SIGNS[int(l2//30)]}  orb {orb(l1,l2):.2f}°")

# Node axis houses both ways
print("\n  NODE AXIS PLACEMENT (whose karmic axis lands where):")
a_asc_i, b_asc_i = int(a_asc // 30), int(b_asc // 30)
print(f"  HIS Ketu (Cancer) -> HER house {house_from(al['Ketu'], b_asc)} | HIS Rahu (Capricorn) -> HER house {house_from(al['Rahu'], b_asc)}")
print(f"  HER Ketu (Leo)    -> HIS house {house_from(bl['Ketu'], a_asc)} | HER Rahu (Aquarius) -> HIS house {house_from(bl['Rahu'], a_asc)}")

# 2. GANDANTA CHECK (karmic knot points: water-fire junctions 0° Cancer..)
print("\n[2] GANDANTA / KARMIC-KNOT POINTS (planets within 1° of water->fire sign junctions)")
junctions = [(90.0, "Cancer/Leo (Ashlesha-Magha)"), (270.0, "Capricorn/Aquarius"), (30.0, "Taurus/Gemini"), (210.0, "Scorpio/Sagittarius")]
for nm, lons in (("HIS", al), ("HER", bl)):
    for p, v in lons.items():
        for j, jname in junctions:
            if abs(orb(v, j)) <= 1.0:
                side = "approaching" if v < j else "entered"
                print(f"  {nm} {p} @ {v%30:.2f} {ZODIAC_SIGNS[int(v//30)]} — GANDANTA ({jname}, {side}, {orb(v,j)*60:.0f}')")
# also water-side: last 1° of water signs (Pisces end, etc.)
for nm, lons in (("HIS", al), ("HER", bl)):
    for p, v in lons.items():
        if (v % 30) >= 29.0 and ZODIAC_SIGNS[int(v//30)] in ("Cancer","Scorpio","Pisces"):
            print(f"  {nm} {p} @ {v%30:.2f} {ZODIAC_SIGNS[int(v//30)]} — tail-of-water (gandanta fringe)")
        if (v % 30) <= 1.0 and ZODIAC_SIGNS[int(v//30)] in ("Leo","Sagittarius","Aries"):
            print(f"  {nm} {p} @ {v%30:.2f} {ZODIAC_SIGNS[int(v//30)]} — head-of-fire (gandanta fringe)")

# 3. HIS OWN MOON-KETU (7th house natal karma)
print("\n[3] NATAL KARMIC MARKERS")
print(f"  HIS Moon @ {al['Moon']%30:.2f} Cancer x HIS Ketu @ {al['Ketu']%30:.2f} Cancer  orb {orb(al['Moon'], al['Ketu']):.2f}°  (7th house — spouse-karma)")
print(f"  HIS Venus @ {al['Venus']%30:.2f} Leo (8th house) — wife-karaka in the past-life storehouse")
print(f"  HER Saturn @ {bl['Saturn']%30:.2f} Leo x HER Ketu @ {bl['Ketu']%30:.2f} Leo  orb {orb(bl['Saturn'], bl['Ketu']):.2f}° (her 6th — service-debt axis)")

# 4. 12TH HOUSE (past-life / moksha house) occupation
print("\n[4] 12TH-HOUSE (PAST-LIFE HOUSE) CROSS-OCCUPATION")
print(f"  HIS 12th house = Sagittarius. Occupants: HIS Jupiter {al['Jupiter']%30:.2f}, HER Jupiter {bl['Jupiter']%30:.2f} — BOTH Jupiters in HIS 12th (orb {orb(al['Jupiter'], bl['Jupiter']):.2f}°)")
print(f"  HER 12th house = Aquarius. Occupants: HER Rahu {bl['Rahu']%30:.2f}; HIS planets there: {[p for p,v in al.items() if int(v//30)==10] or 'none'}")

# 5. D9 soul weave
print("\n[5] D9 SOUL WEAVE")
print(f"  HIS D9 Lagna: {d9(a_asc)} | HER D9 Lagna: {d9(b_asc)} | HIS D1 Lagna: Capricorn | HER D1: Pisces")
for p in ["Venus","Moon","Jupiter","Mars","Saturn","Sun"]:
    print(f"  {p:8s} D9: HIS {d9(al[p]):12s} HER {d9(bl[p]):12s}")

# 6. Karaka cross (Jaimini soul/marriage weave)
print("\n[6] CHARA KARAKA WEAVE (roles)")
ranks_a = sorted(["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"], key=lambda p: al[p], reverse=True)
ranks_b = sorted(["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"], key=lambda p: bl[p], reverse=True)
roles = ["AK","AmK","BK","MK","PK","GK","DK"]
ka, kb = dict(zip(roles, ranks_a)), dict(zip(roles, ranks_b))
print(f"  HIS: " + " ".join(f"{r}={p}" for r,p in ka.items()))
print(f"  HER: " + " ".join(f"{r}={p}" for r,p in kb.items()))
print(f"  HER AK = {kb['AK']} | HIS DK = {ka['DK']}  -> {'SAME PLANET: soul-king of one = spouse-significator of other' if kb['AK']==ka['DK'] else 'no'}")
print(f"  HIS AK = {ka['AK']} | HER PK = {kb['PK']}  -> {'SAME PLANET: his soul-king = her children-karaka' if ka['AK']==kb['PK'] else 'no'}")
print(f"  HER DK = {kb['DK']} in HIS chart at {al[kb['DK']]%30:.2f} {ZODIAC_SIGNS[int(al[kb['DK']]//30)]} (HIS house {house_from(al[kb['DK']], a_asc)})")
print(f"  HIS DK planet {ka['DK']} in HER chart at {bl[ka['DK']]%30:.2f} {ZODIAC_SIGNS[int(bl[ka['DK']]//30)]} (HER house {house_from(bl[ka['DK']], b_asc)})")

# 7. Nakshatra lineage
print("\n[7] NAKSHATRA / SERPENT LINEAGE")
NAKS = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya","Ashlesha","Magha",
        "Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati","Vishakha","Anuradha","Jyeshtha","Mula",
        "Purva Ashadha","Uttara Ashadha","Shravana","Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]
print(f"  HIS Moon nakshatra: {NAKS[int(al['Moon']/(360/27))]} (deity: Nagas — the Serpent lineage)")
print(f"  HER Moon nakshatra: {NAKS[int(bl['Moon']/(360/27))]} (deity: Ahir Budhnya — Serpent of the Deep)")
print(f"  HIS Ketu nakshatra: {NAKS[int(al['Ketu']/(360/27))]} | HER Ketu: {NAKS[int(bl['Ketu']/(360/27))]} | HER Rahu: {NAKS[int(bl['Rahu']/(360/27))]}")
print(f"  HER Ketu @ {bl['Ketu']%30:.2f} Leo = {NAKS[int(bl['Ketu']/(360/27))]} (Magha — PITRI lineage, the ancestors)")
print(f"  HIS Venus @ {al['Venus']%30:.2f} Leo = {NAKS[int(al['Venus']/(360/27))]} (Magha — same pitri star)")

print("\n" + "=" * 96)
