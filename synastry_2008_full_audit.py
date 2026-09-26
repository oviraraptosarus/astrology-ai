"""
FULL SYNASTRY AUDIT: the two 2008 charts (unconstrained mode)
  A (him): 2008-08-01 18:25 IST, Ramachandrapuram AP (16.8186N, 82.0641E)
  B (her): 2008-04-05 06:15 CEST, Bytom Poland (50.348N, 18.916E)
Computes EVERY layer from raw ephemeris: natal + Ashtakoota (real tables,
not the scaffold) + Kuja dosha + cross-chart overlays + tight cross
conjunctions + D9 soul layer + Chara Karakas + Upapada + dasha overlay +
double-transit marriage-window verification + progeny link + verdict.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import datetime, pytz
import swisseph as swe
from config import Config
from astrology_engine import calculate_chart_with_object
from dasha_engine import DashaEngine
from forward_timing_scanner import ZODIAC_SIGNS

A_BIRTH = (2008, 8, 1, 18, 25, 16.8186, 82.0641, "Asia/Kolkata")
B_BIRTH = (2008, 4, 5, 6, 15, 50.348, 18.916, "Europe/Warsaw")

NAKS = ["Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra","Punarvasu","Pushya",
        "Ashlesha","Magha","Purva Phalguni","Uttara Phalguni","Hasta","Chitra","Swati",
        "Vishakha","Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha","Shravana",
        "Dhanishta","Shatabhisha","Purva Bhadrapada","Uttara Bhadrapada","Revati"]
YONI = {"Ashwini":"Horse","Bharani":"Elephant","Krittika":"Sheep","Rohini":"Serpent",
        "Mrigashira":"Serpent","Ardra":"Dog","Punarvasu":"Cat","Pushya":"Sheep",
        "Ashlesha":"Cat","Magha":"Rat","Purva Phalguni":"Rat","Uttara Phalguni":"Cow",
        "Hasta":"Buffalo","Chitra":"Tiger","Swati":"Buffalo","Vishakha":"Tiger",
        "Anuradha":"Deer","Jyeshtha":"Deer","Mula":"Dog","Purva Ashadha":"Monkey",
        "Uttara Ashadha":"Mongoose","Shravana":"Monkey","Dhanishta":"Lion",
        "Shatabhisha":"Horse","Purva Bhadrapada":"Lion","Uttara Bhadrapada":"Cow","Revati":"Elephant"}
YONI_ENEMY = {frozenset(p) for p in [("Horse","Buffalo"),("Elephant","Lion"),("Sheep","Monkey"),
                                     ("Serpent","Mongoose"),("Dog","Deer"),("Cat","Rat"),("Cow","Tiger")]}
YONI_FRIEND = {frozenset(p) for p in [("Horse","Elephant"),("Horse","Sheep"),("Elephant","Monkey"),
                                      ("Sheep","Serpent"),("Dog","Serpent"),("Cow","Sheep"),
                                      ("Buffalo","Sheep"),("Tiger","Lion"),("Monkey","Sheep"),
                                      ("Deer","Sheep"),("Mongoose","Serpent")]}
VARNA = {"Aries":"Kshatriya","Leo":"Kshatriya","Sagittarius":"Kshatriya",
         "Taurus":"Vaishya","Virgo":"Vaishya","Capricorn":"Vaishya",
         "Gemini":"Shudra","Libra":"Shudra","Aquarius":"Shudra",
         "Cancer":"Brahmin","Scorpio":"Brahmin","Pisces":"Brahmin"}
VASHYA_GROUP = {"Cancer":"Jalachara","Pisces":"Jalachara","Capricorn":"Jalachara","Scorpio":"Keeta",
                "Aries":"Chatushpada","Taurus":"Chatushpada","Leo":"Vanachara","Sagittarius":"Manava (biped)",
                "Gemini":"Manava","Libra":"Manava","Aquarius":"Manava","Virgo":"Manava"}
GANA = {}
for n in ["Ashwini","Mrigashira","Punarvasu","Pushya","Hasta","Swati","Anuradha","Shravana","Revati"]:
    GANA[n] = "Deva"
for n in ["Bharani","Rohini","Ardra","Purva Phalguni","Uttara Phalguni","Purva Ashadha","Uttara Ashadha","Purva Bhadrapada","Uttara Bhadrapada"]:
    GANA[n] = "Manushya"
for n in ["Krittika","Ashlesha","Magha","Chitra","Vishakha","Jyeshtha","Mula","Dhanishta","Shatabhisha"]:
    GANA[n] = "Rakshasa"
NADI = [n % 3 for n in range(27)]  # 0=Adi,1=Madhya,2=Antya (Ashwini=Adi cycle)
FRIENDS = {"Sun":{"Moon","Mars","Jupiter"},"Moon":{"Sun","Mercury"},
           "Mars":{"Sun","Moon","Jupiter"},"Mercury":{"Sun","Venus"},
           "Jupiter":{"Sun","Moon","Mars"},"Venus":{"Mercury","Saturn"},
           "Saturn":{"Mercury","Venus"}}
ENEMIES = {"Sun":{"Venus","Saturn"},"Mars":{"Mercury"},"Mercury":{"Moon"},
           "Venus":{"Sun","Moon"},"Saturn":{"Sun","Moon","Mars"}}
PLANETS = ["Sun","Moon","Mars","Mercury","Jupiter","Venus","Saturn"]


def chart_of(birth):
    chart, payload = calculate_chart_with_object(*birth, name="X")
    lons = {}
    for p in PLANETS + ["Rahu", "Ketu"]:
        po = chart.planets[p]
        lons[p] = (ZODIAC_SIGNS.index(po.sign) * 30.0 + po.degree) % 360.0
    asc_lon = (ZODIAC_SIGNS.index(chart.ascendant_sign) * 30.0 + chart.ascendant_degree) % 360.0
    return chart, payload, lons, asc_lon


def nak_of(lon):
    return int(lon / (360 / 27))


def d9_sign(lon):
    """Engine-validated navamsha (element-based start: Fire=0, Earth=9(Cap), Air=6(Lib), Water=3(Can))."""
    from varga_engine import VargaEngine
    sign = ZODIAC_SIGNS[int(lon // 30)]
    return VargaEngine.get_sign_index(VargaEngine.calc_d9_navamsha(sign, lon % 30))


def arudha_of(house_sign_idx, lons):
    """Engine-validated Jaimini arudha (Pt. Sanjay Rath method with 1/7 exception)."""
    lord = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun",
            "Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter",
            "Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}[ZODIAC_SIGNS[house_sign_idx]]
    lord_idx = int(lons[lord] // 30)
    dist = (lord_idx - house_sign_idx) % 12
    arudha = (lord_idx + dist) % 12
    if arudha == house_sign_idx or (arudha - house_sign_idx) % 12 == 6:
        arudha = (arudha + 9) % 12
    return arudha


def ashtakoota(b_moon_lon, g_moon_lon):
    b_nak, g_nak = nak_of(b_moon_lon), nak_of(g_moon_lon)
    b_rashi, g_rashi = int(b_moon_lon // 30), int(g_moon_lon // 30)
    b_sign, g_sign = ZODIAC_SIGNS[b_rashi], ZODIAC_SIGNS[g_rashi]
    R = []

    # 1 Varna (1)
    v_b, v_g = VARNA[b_sign], VARNA[g_sign]
    rank = {"Shudra":1,"Vaishya":2,"Kshatriya":3,"Brahmin":4}
    varna_pts = 1 if rank[v_b] >= rank[v_g] else 0
    R.append(("Varna", varna_pts, 1, f"{v_b} vs {v_g}"))

    # 2 Vashya (2)
    vb, vg = VASHYA_GROUP[b_sign], VASHYA_GROUP[g_sign]
    vash = 2 if vb == vg else (1 if vb in ("Jalachara","Manava") and vg in ("Jalachara","Manava") else 0)
    R.append(("Vashya", vash, 2, f"{vb} vs {vg}"))

    # 3 Tara (3)
    t1 = ((g_nak - b_nak) % 27) + 1
    t2 = ((b_nak - g_nak) % 27) + 1
    bad = {3,5,7}  # Vipat, Pratyari, Vadha
    tara_pts = 3 if (t1 % 9 or 9) not in bad and (t2 % 9 or 9) not in bad else \
               (1.5 if (t1 % 9 or 9) not in bad or (t2 % 9 or 9) not in bad else 0)
    R.append(("Tara", tara_pts, 3, f"counts {t1}/{t2} -> tara {(t1%9 or 9)},{(t2%9 or 9)}"))

    # 4 Yoni (4)
    yb, yg = YONI[NAKS[b_nak]], YONI[NAKS[g_nak]]
    if yb == yg: yoni = 4
    elif frozenset((yb,yg)) in YONI_ENEMY: yoni = 1
    elif frozenset((yb,yg)) in YONI_FRIEND: yoni = 3
    else: yoni = 2
    R.append(("Yoni", yoni, 4, f"{yb} vs {yg}"))

    # 5 Graha Maitri (5)
    lb = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun",
          "Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter",
          "Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}[b_sign]
    lg = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon","Leo":"Sun",
          "Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars","Sagittarius":"Jupiter",
          "Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}[g_sign]
    def rel(x, y):  # x's attitude to y
        if y in FRIENDS.get(x, set()): return "F"
        if y in ENEMIES.get(x, set()): return "E"
        return "N"
    r1, r2 = rel(lb, lg), rel(lg, lb)
    gm = 5 if (r1=="F" and r2=="F") else 4 if "F" in (r1,r2) and "E" not in (r1,r2) \
         else 3 if r1==r2=="N" else 1 if "E" in (r1,r2) and "N" in (r1,r2) else 0
    R.append(("Graha Maitri", gm, 5, f"lords {lb}/{lg}, attitudes {r1}/{r2}"))

    # 6 Gana (6)
    gb, gg = GANA[NAKS[b_nak]], GANA[NAKS[g_nak]]
    gana = 6 if gb==gg else 5 if (gb=="Deva" and gg=="Manushya") else \
           1 if (gb=="Deva" and gg=="Rakshasa") else 0
    R.append(("Gana", gana, 6, f"{gb} vs {gg}"))

    # 7 Bhakoot (7)
    # Classical Bhakoot dosha: girl's Moon 2/12, 6/8, or 5/9 from boy's Moon.
    # In terms of d = (g - b) % 12 (d=0 same sign, d=1 girl is 2nd from boy):
    #   2/12 dosha -> d in (1, 11); 6/8 dosha -> d in (5, 7); 5/9 dosha -> d in (4, 8)
    # Exception: 5/9 trine dosha is cancelled when the Moon-sign lords are the
    # same planet or mutual friends.
    d = (g_rashi - b_rashi) % 12
    pos = d if d != 0 else 12  # positional count (girl is (d+1)th from boy; keep d for set tests
    if d in (1, 11, 5, 7):
        bhak = 0
    elif d in (4, 8):  # 5/9 trine
        trine_cancelled = (lb == lg) or (rel(lb, lg) == "F" and rel(lg, lb) == "F")
        bhak = 7 if trine_cancelled else 0
    else:
        bhak = 7
    R.append(("Bhakoot", bhak, 7, f"{b_sign}->{g_sign} girl is {(d if d else 12)+1}th from boy; "
                                   f"{'5/9 trine, lords friends -> dosha cancelled' if d in (4,8) and bhak==7 else ('dosha' if bhak==0 else 'no dosha')}"))

    # 8 Nadi (8)
    nadi = 8 if NADI[b_nak] != NADI[g_nak] else 0
    nadi_names = ["Adi", "Madhya", "Antya"]
    R.append(("Nadi", nadi, 8, f"{nadi_names[NADI[b_nak]]} vs {nadi_names[NADI[g_nak]]}"))

    # Supplemental South-Indian kootas (printed, not scored)
    supp = []
    # Rajju (5-cycle: Pada,Kati,Nabhi,Kantha,Shiro repeating from Ashwini)
    rajju_cycle = ["Pada (feet)", "Kati (waist)", "Nabhi (navel)", "Kantha (neck)", "Shiro (head)"]
    rb, rg = rajju_cycle[b_nak % 5], rajju_cycle[g_nak % 5]
    supp.append(("Rajju", f"{rb} vs {rg} -> {'DOSHA (same rajju)' if rb==rg else 'CLEAN (different rajjus)'}"))
    # Vedha (piercing pairs)
    vedha_pairs = {("Ashlesha","Purva Bhadrapada"),("Ashwini","Jyeshtha"),("Bharani","Anuradha"),
                   ("Krittika","Vishakha"),("Rohini","Swati"),("Mrigashira","Dhanishta"),
                   ("Ardra","Shravana"),("Punarvasu","Uttara Ashadha"),("Pushya","Purva Ashadha")}
    bn, gn = NAKS[b_nak], NAKS[g_nak]
    supp.append(("Vedha", f"{bn} x {gn} -> {'DOSHA (piercing pair)' if (bn,gn) in vedha_pairs or (gn,bn) in vedha_pairs else 'CLEAN (no piercing)'}"))
    # Mahendra (progeny blessing: 4/7/10/13/16/19/22/25th from boy's nak)
    mdist = ((g_nak - b_nak) % 27) + 1
    supp.append(("Mahendra", f"girl's nak is {mdist}th from boy's -> {'BLESSED' if mdist in (4,7,10,13,16,19,22,25) else 'not present (no Mahendra blessing)'}"))
    # Stree-Dirgha (boy's nak counted from girl's should exceed 13)
    sdist = ((b_nak - g_nak) % 27) + 1
    supp.append(("Stree-Dirgha", f"boy's nak is {sdist}th from girl's -> {'satisfied (>13)' if sdist > 13 else 'NOT satisfied (<=13)'}"))

    total = sum(p for _,p,_,_ in R)
    return total, R, b_nak, g_nak, supp


def cross_report(a_lons, a_asc, b_lons, b_asc, name_a="HIM", name_b="HER"):
    print("\n=== CROSS-CHART OVERLAYS (whole-sign) ===")
    a_asc_i, b_asc_i = int(a_asc // 30), int(b_asc // 30)
    for p, lon in a_lons.items():
        h_from_b = ((int(lon // 30) - b_asc_i) % 12) + 1
        print(f"  {name_a} {p:8s} {ZODIAC_SIGNS[int(lon//30)]:12s} -> {name_B if False else 'HER'} house {h_from_b}")
    print()
    for p, lon in b_lons.items():
        h_from_a = ((int(lon // 30) - a_asc_i) % 12) + 1
        print(f"  {name_B if False else 'HER'} {p:8s} {ZODIAC_SIGNS[int(lon//30)]:12s} -> HIS house {h_from_a}")

    print("\n=== TIGHT CROSS-CHART CONJUNCTIONS (<8 deg orb) ===")
    for pa, la in a_lons.items():
        for pb, lb_ in b_lons.items():
            d = abs((la - lb_ + 180) % 360 - 180)
            if d <= 8:
                print(f"  HIS {pa:8s} @ {la%30:6.2f} {ZODIAC_SIGNS[int(la//30)]}  x  HER {pb:8s} @ {lb_%30:6.2f} {ZODIAC_SIGNS[int(lb_//30)]}  orb {d:.2f}°")


def transit_check(year, month, day, planet):
    swe.set_sid_mode(Config.ayanamsha_swe_id())
    jd = swe.julday(year, month, day, 12.0)
    res, _ = swe.calc_ut(jd, {"Jupiter": swe.JUPITER, "Saturn": swe.SATURN}[planet], swe.FLG_SIDEREAL)
    lon = res[0] % 360.0
    return lon, int(lon // 30)


def dasha_at(birth_dt_utc, moon_lon, when_utc):
    tl = DashaEngine.calculate_vimshottari_timeline(birth_dt_utc, moon_lon, num_levels=3)
    cur = DashaEngine.get_current_dasha(tl, when_utc)
    return cur


def main():
    A, A_payload, A_lons, A_asc = chart_of(A_BIRTH)
    B, B_payload, B_lons, B_asc = chart_of(B_BIRTH)

    print("=" * 100)
    print("FULL SYNASTRY AUDIT — HIM (2008-08-01) x HER (2008-04-05) — Lahiri sidereal")
    print("=" * 100)

    print("\n=== NATAL CORES ===")
    for nm, ch, lons, asc in (("HIM", A, A_lons, A_asc), ("HER", B, B_lons, B_asc)):
        print(f"  {nm}: Lagna {ch.ascendant_sign} {ch.ascendant_degree:.2f}° | Moon {ch.planets['Moon'].sign} {ch.planets['Moon'].degree:.2f}° ({NAKS[nak_of(lons['Moon'])]})")
        occ = {}
        for p in PLANETS:
            h = getattr(ch.planets[p], "house", None)
            if h: occ.setdefault(h, []).append(p)
        print(f"       Houses: " + " | ".join(f"H{h}:{','.join(ps)}" for h, ps in sorted(occ.items())))

    # ---- Ashtakoota (real tables) ----
    print("\n=== ASHTAKOOTA GUNA MILAN (real computation) ===")
    total, rows, b_nak, g_nak, supp = ashtakoota(A_lons["Moon"], B_lons["Moon"])
    for name, pts, mx, note in rows:
        print(f"  {name:14s} {pts:>4}/{mx}  ({note})")
    print(f"  TOTAL: {total}/36  ->  {'EXCELLENT (>=25)' if total>=25 else 'GOOD (>=18)' if total>=18 else 'NOT RECOMMENDED (<18)'}")
    print(f"  Moons: HIS {NAKS[b_nak]} / HER {NAKS[g_nak]}")
    print("  --- South-Indian supplemental kootas ---")
    for name, note in supp:
        print(f"  {name:14s} {note}")

    # ---- Kuja dosha both ----
    print("\n=== KUJA DOSHA (Manglik) — both charts ===")
    for nm, ch, lons, asc in (("HIM", A, A_lons, A_asc), ("HER", B, B_lons, B_asc)):
        mars = lons["Mars"]; jup = lons["Jupiter"]
        flags = []
        for src_name, src in (("Lagna", asc), ("Moon", lons["Moon"]), ("Venus", lons["Venus"])):
            pos = ((int(mars // 30) - int(src // 30)) % 12) + 1
            if pos in (1, 2, 4, 7, 8, 12):
                flags.append(f"{pos} from {src_name}")
        # Jupiter aspect cancellation (5,7,9 from Jupiter onto Mars sign)
        jup_sign = int(jup // 30); mars_sign = int(mars // 30)
        aspected = ((mars_sign - jup_sign) % 12) + 1 in (5, 7, 9)
        print(f"  {nm}: Mars dosha positions: {', '.join(flags) if flags else 'NONE'} | "
              f"Jupiter aspect on Mars: {'YES -> dosha cancelled' if aspected and flags else ('no' if not flags else 'NO')}")

    # ---- overlays & tight conjunctions ----
    cross_report(A_lons, A_asc, B_lons, B_asc)

    # ---- D9 soul layer ----
    print("\n=== NAVAMSHA (D9) SOUL LAYER ===")
    a_d9_lagna, b_d9_lagna = d9_sign(A_asc), d9_sign(B_asc)
    print(f"  HIS D9 Lagna: {ZODIAC_SIGNS[a_d9_lagna]} | HER D9 Lagna: {ZODIAC_SIGNS[b_d9_lagna]}")
    print(f"  >>> HER D9 Lagna ({ZODIAC_SIGNS[b_d9_lagna]}) vs HIS D1 Lagna ({A.ascendant_sign}): "
          f"{'EXACT MATCH — soul-level recognition' if ZODIAC_SIGNS[b_d9_lagna]==A.ascendant_sign else 'no match'}")
    print(f"  HIS D9 Lagna ({ZODIAC_SIGNS[a_d9_lagna]}) vs HER D1 Lagna ({B.ascendant_sign}): "
          f"{'match' if ZODIAC_SIGNS[a_d9_lagna]==B.ascendant_sign else 'no direct match'}")
    for nm, lons in (("HIM", A_lons), ("HER", B_lons)):
        print(f"  {nm} D9: Moon {ZODIAC_SIGNS[d9_sign(lons['Moon'])]}, Venus {ZODIAC_SIGNS[d9_sign(lons['Venus'])]}, "
              f"Mars {ZODIAC_SIGNS[d9_sign(lons['Mars'])]}, Jupiter {ZODIAC_SIGNS[d9_sign(lons['Jupiter'])]}")
    va, vb = d9_sign(A_lons["Venus"]), d9_sign(B_lons["Venus"])
    print(f"  D9 Venus pair: HIS {ZODIAC_SIGNS[va]} x HER {ZODIAC_SIGNS[vb]} -> "
          f"{'FIRE TRINE (soul-level romantic resonance)' if (va - vb) % 12 in (4, 8) and va % 4 == vb % 4 else 'check: ' + str((va - vb) % 12)}")

    # ---- Chara Karakas (absolute longitude, engine scheme) ----
    print("\n=== CHARA KARAKAS (absolute-longitude ranking) ===")
    for nm, lons in (("HIM", A_lons), ("HER", B_lons)):
        ranked = sorted(PLANETS, key=lambda p: lons[p], reverse=True)
        roles = ["AK","AmK","BK","MK","PK","GK","DK"]
        karaka = dict(zip(roles, ranked))
        print(f"  {nm}: " + " ".join(f"{r}={p}" for r, p in karaka.items()))

    # ---- Upapada Lagna ----
    print("\n=== UPAPADA LAGNA (Jaimini arudha of 7th) ===")
    for nm, lons, asc in (("HIM", A_lons, A_asc), ("HER", B_lons, B_asc)):
        ul = arudha_of((int(asc // 30) + 6) % 12, lons)
        print(f"  {nm}: UL = {ZODIAC_SIGNS[ul]}")
    ul_a = ZODIAC_SIGNS[arudha_of((int(A_asc // 30) + 6) % 12, A_lons)]
    ul_b = ZODIAC_SIGNS[arudha_of((int(B_asc // 30) + 6) % 12, B_lons)]
    print(f"  UL compatibility: HIS UL {ul_a} / HER UL {ul_b}")

    # ---- Dasha overlay + marriage window verification ----
    print("\n=== VIMSHOTTARI DASHA OVERLAY ===")
    a_birth_utc = pytz.utc.localize(datetime.datetime(2008, 8, 1, 12, 55))
    b_birth_utc = pytz.utc.localize(datetime.datetime(2008, 4, 5, 4, 15))
    for label, when in (("NOW (Sep 2026)", datetime.datetime(2026, 9, 7, 12, 0, tzinfo=pytz.utc)),
                        ("2035-01 (marriage window)", datetime.datetime(2035, 1, 15, 12, 0, tzinfo=pytz.utc)),
                        ("2036-01", datetime.datetime(2036, 1, 15, 12, 0, tzinfo=pytz.utc))):
        ca = dasha_at(a_birth_utc, A_lons["Moon"], when)
        cb = dasha_at(b_birth_utc, B_lons["Moon"], when)
        print(f"  {label}:")
        print(f"    HIM: {ca.get('mahadasha')} -> {ca.get('antardasha')} -> {ca.get('pratyantardasha')}")
        print(f"    HER: {cb.get('mahadasha')} -> {cb.get('antardasha')} -> {cb.get('pratyantardasha')}")

    print("\n=== DOUBLE-TRANSIT MARRIAGE WINDOW VERIFICATION (Jupiter/Saturn raw ephemeris) ===")
    a7 = (int(A_asc // 30) + 6) % 12  # his 7th sign idx (Cancer)
    b5 = (int(B_asc // 30) + 4) % 12  # her 5th sign idx (Cancer)
    b7 = (int(B_asc // 30) + 6) % 12  # her 7th sign idx (Virgo)
    jup_aspects = lambda j: {j, (j+4)%12, (j+6)%12, (j+8)%12}  # sign + 5th,7th,9th aspects
    sat_aspects = lambda s: {s, (s+2)%12, (s+6)%12, (s+9)%12}  # sign + 3rd,7th,10th
    print(f"  HIS 7th sign: {ZODIAC_SIGNS[a7]} | HER 5th: {ZODIAC_SIGNS[b5]} | HER 7th: {ZODIAC_SIGNS[b7]}")
    hits = []
    for y in (2034, 2035, 2036):
        for m in range(1, 13):
            jl, js = transit_check(y, m, 15, "Jupiter")
            sl, ss = transit_check(y, m, 15, "Saturn")
            his_7_dt = a7 in jup_aspects(js) and a7 in sat_aspects(ss)
            her_5_dt = b5 in jup_aspects(js) and b5 in sat_aspects(ss)
            her_7_dt = b7 in jup_aspects(js) and b7 in sat_aspects(ss)
            if his_7_dt or her_5_dt or her_7_dt:
                hits.append((f"{y}-{m:02d}", ZODIAC_SIGNS[js], ZODIAC_SIGNS[ss],
                             his_7_dt, her_5_dt, her_7_dt))
    print(f"  Months where double-transit fires (Jup {ZODIAC_SIGNS[js]} / Sat {ZODIAC_SIGNS[ss]}):")
    for h in hits:
        print(f"    {h[0]}: Jup {h[1]:12s} Sat {h[2]:12s} | HIS-7th:{'✓' if h[3] else '·'} HER-5th:{'✓' if h[4] else '·'} HER-7th:{'✓' if h[5] else '·'}")

    # ---- Sade Sati context ----
    print("\n=== SADE SATI CONTEXT ===")
    a_moon_sign = int(A_lons["Moon"] // 30)
    b_moon_sign = int(B_lons["Moon"] // 30)
    for label, y in (("her (Moon Pisces)", 2026), ("her", 2030), ("her", 2035), ("him (Moon Cancer)", 2027), ("him", 2035), ("him", 2033)):
        sl, ss = transit_check(y, 6, 15, "Saturn")
        for nm, moon_sign in (("HIM", a_moon_sign), ("HER", b_moon_sign)):
            rel = ((ss - moon_sign) % 12)
            phase = "PEAK (over Moon)" if rel == 0 else "rising (12th)" if rel == 11 else "setting (2nd)" if rel == 1 else "-"
            if phase != "-":
                print(f"  {label} {y}: Saturn in {ZODIAC_SIGNS[ss]} -> {nm} Sade Sati {phase}")

    print("\n" + "=" * 100)
    print("AUDIT COMPLETE — verdict synthesized in chat from the layers above.")
    print("=" * 100)


if __name__ == "__main__":
    main()
