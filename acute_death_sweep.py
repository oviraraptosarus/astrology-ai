"""
ACUTE SUB-DEGREE DEATH SWEEP (unconstrained) — all corpus charts.
For each chart, sweeps the Jaimini longevity bracket day-by-day for:
  - Transiting SATURN (aspects 0/60/90/180 — graha drishti) over natal
    Sun, Moon, Lagna degree, 8th lord, natal Saturn, natal Mars
  - Transiting MARS (aspects 0/90/150/180) over the same targets
  - Transiting RAHU (conjunction/opposition) over the same targets
  - Saturn/Mars/Rahu INGRESS into the natal 8th house sign
Collisions <= 1.2 deg orb recorded; exact peak refined by ternary search.
Each collision is flagged if it falls inside a double-maraka D-A-P window
(from death_window_analysis.analyze) — the classical dasha x transit convergence.
Empirical scorecard printed for the 4 charts with known death dates.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import datetime, pytz
import swisseph as swe
from config import Config
from astrology_engine import calculate_chart_with_object
from forward_timing_scanner import ZODIAC_SIGNS
from death_window_analysis import CHARTS, analyze, BRACKET_AGES, LORDS, ZOD

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "death_sweep_results.txt")
swe.set_sid_mode(Config.ayanamsha_swe_id())

ASPECTS = {"Saturn": [0.0, 60.0, 90.0, 180.0],
           "Mars":   [0.0, 90.0, 150.0, 180.0],
           "Rahu":   [0.0, 180.0]}
TRANSIT_IDS = {"Saturn": swe.SATURN, "Mars": swe.MARS, "Rahu": Config.node_swe_id()}
ORB_LIMIT = 1.2

def ang_sep(a, b):
    d = abs((a - b) % 360.0)
    return min(d, 360.0 - d)

def planet_lon(pid, dt):
    hour = dt.hour + dt.minute / 60.0 + dt.second / 3600.0
    jd = swe.julday(dt.year, dt.month, dt.day, hour)
    res, _ = swe.calc_ut(jd, pid, swe.FLG_SIDEREAL)
    return res[0] % 360.0

def refine_min(pid, target, aspect, d0, d1):
    """Ternary search for the exact minimum-separation hour in [d0, d1]."""
    import math
    def f(dt):
        return ang_sep(planet_lon(pid, dt), (target + aspect) % 360.0)
    lo, hi = d0, d1
    for _ in range(40):
        t1 = lo + (hi - lo) / 3
        t2 = hi - (hi - lo) / 3
        if f(t1) < f(t2):
            hi = t2
        else:
            lo = t1
    tm = lo + (hi - lo) / 2
    return tm, f(tm)

def sweep_chart(name, info, maraka_windows):
    y, m, d, h, mi, lat, lon, tz = info["b"]
    chart, _ = calculate_chart_with_object(y, m, d, h, mi, lat, lon, tz, name=name)

    def abs_lon(p):
        po = chart.planets[p]
        return (ZODIAC_SIGNS.index(po.sign) * 30.0 + po.degree) % 360.0

    asc_idx = ZOD.index(chart.ascendant_sign)
    h8_sign_idx = (asc_idx + 7) % 12
    h8_lord = LORDS[ZOD[h8_sign_idx]]

    targets = {
        "Sun": abs_lon("Sun"), "Moon": abs_lon("Moon"),
        "Lagna": (asc_idx * 30.0 + chart.ascendant_degree) % 360.0,
        f"8L({h8_lord})": abs_lon(h8_lord),
        "Saturn": abs_lon("Saturn"), "Mars": abs_lon("Mars"),
    }

    birth_year = y
    lo_age, hi_age = BRACKET_AGES[info.get("_bracket", "Deerghayu")] if "_bracket" in info else (66, 105)
    start = datetime.datetime(birth_year + lo_age, 1, 1)
    end = datetime.datetime(birth_year + hi_age + 1, 1, 1)

    collisions = []
    day = start
    one = datetime.timedelta(days=1)
    # track for ingress detection
    prev_sign = {}
    while day < end:
        for t_name, pid in TRANSIT_IDS.items():
            tlon = planet_lon(pid, day)
            tsign = int(tlon // 30)
            # ingress into natal 8th
            if prev_sign.get(t_name) is not None and tsign != prev_sign[t_name]:
                if tsign == h8_sign_idx:
                    collisions.append({"date": day.strftime("%Y-%m-%d"),
                                       "kind": f"{t_name} INGRESS into natal 8th house",
                                       "orb_arcmin": None})
            prev_sign[t_name] = tsign
            if t_name == "Rahu" and tsign != h8_sign_idx and ((tsign - h8_sign_idx) % 12) != 6:
                pass  # rahu only conj/opp handled below via aspects
            for tgt_name, tlon_natal in targets.items():
                for asp in ASPECTS[t_name]:
                    diff = ang_sep(tlon, (tlon_natal + asp) % 360.0)
                    if diff <= ORB_LIMIT:
                        collisions.append({"date": day.strftime("%Y-%m-%d"),
                                           "kind": f"{t_name} {'conj' if asp==0 else ('opp' if asp==180 else f'{int(asp)}°')} {tgt_name}",
                                           "orb_arcmin": round(diff * 60, 1),
                                           "_pid": pid, "_tgt": tlon_natal, "_asp": asp,
                                           "_day": day})
        day += one

    # Deduplicate: keep tightest per (kind, date-window of 5 days)
    collisions.sort(key=lambda c: (c["date"], c["kind"]))
    dedup = []
    for c in collisions:
        if c.get("orb_arcmin") is None:
            dedup.append(c)
            continue
        dup = False
        for e in dedup:
            if e.get("orb_arcmin") is None:
                continue
            if e["kind"] == c["kind"] and abs((datetime.datetime.fromisoformat(e["date"]) - datetime.datetime.fromisoformat(c["date"])).days) <= 5:
                if c["orb_arcmin"] < e["orb_arcmin"]:
                    e.update(c)
                dup = True
                break
        if not dup:
            dedup.append(dict(c))

    # refine top 40 by orb, attach maraka-window convergence
    acute = [c for c in dedup if c.get("orb_arcmin") is not None]
    acute.sort(key=lambda c: c["orb_arcmin"])
    for c in acute[:40]:
        d0 = c["_day"] - datetime.timedelta(days=1)
        d1 = c["_day"] + datetime.timedelta(days=1)
        tm, orb = refine_min(c["_pid"], c["_tgt"], c["_asp"], d0, d1)
        c["exact_peak"] = tm.strftime("%Y-%m-%d")
        c["orb_arcmin_exact"] = round(orb * 60, 1)
        in_win = None
        for w in maraka_windows:
            if w["start"].date() <= tm.date() <= w["end"].date():
                in_win = w["triad"]
                break
        c["maraka_convergence"] = in_win
    ingresses = [c for c in dedup if c.get("orb_arcmin") is None]

    return acute[:40], ingresses, targets, chart

def main():
    lines = []
    def P(s=""):
        print(s)
        lines.append(s)

    P("=" * 104)
    P("ACUTE SUB-DEGREE DEATH SWEEP — Saturn/Mars/Rahu over Sun/Moon/Lagna/8L/Saturn/Mars — all charts")
    P("Aspect sets: Saturn 0/60/90/180 | Mars 0/90/150/180 | Rahu 0/180 | orb <= 1.2 deg | inside Jaimini bracket")
    P("=" * 104)

    dead_checks = []

    for name, info in CHARTS.items():
        try:
            chart, lon_, mar, lords, bracket, ages, results = analyze(name, info)
        except Exception as e:
            P(f"\n### {name}: analyze failed: {e}")
            continue
        info = dict(info)
        info["_bracket"] = bracket
        try:
            acute, ingresses, targets, chart = sweep_chart(name, info, results)
        except Exception as e:
            P(f"\n### {name}: sweep failed: {e}")
            continue

        h2, h7, h8, badh, occ = lords
        P(f"\n{'='*104}")
        P(f"### {name}  |  Bracket {bracket} (age {ages[0]}-{ages[1]})  |  Marakas: {h2}, {h7}")
        P(f"    Natal targets: " + ", ".join(f"{k}={v%30:.1f}°{ZODIAC_SIGNS[int(v//30)][:3]}" for k, v in targets.items()))
        if ingresses:
            P(f"    8th-house ingresses in bracket: " + "; ".join(f"{i['date']} {i['kind']}" for i in ingresses[:8]))
        if not acute:
            P("    No acute collisions (<=1.2°) found in bracket.")
        else:
            P(f"    Top acute collisions ({len(acute)}; sorted by exact orb):")
            for c in acute[:12]:
                conv = f" | MARAKA-DASHA CONVERGENCE: {c['maraka_convergence']}" if c.get("maraka_convergence") else ""
                P(f"      {c['exact_peak']}  {c['kind']:38s} orb {c['orb_arcmin_exact']:>5}'{conv}")

        if "died" in info:
            dd = datetime.date.fromisoformat(info["died"])
            near = [c for c in acute if abs((datetime.date.fromisoformat(c["exact_peak"]) - dd).days) <= 5]
            ing_hit = [i for i in ingresses if abs((datetime.date.fromisoformat(i["date"]) - dd).days) <= 60]
            dead_checks.append((name, dd, near, ing_hit))
            P(f"    ACTUAL DEATH {info['died']}: acute collision within ±5d: "
              f"{'; '.join(c['kind'] + ' @' + c['exact_peak'] for c in near) if near else 'NONE'}"
              f" | 8th-ingress within ±60d: {'YES ' + ing_hit[0]['date'] if ing_hit else 'no'}")

    P("\n" + "=" * 104)
    P("EMPIRICAL SCORECARD — acute layer vs 4 known deaths (±5 days)")
    hits = sum(1 for n, dd, near, ing in dead_checks if near)
    for n, dd, near, ing in dead_checks:
        P(f"  {n:18s} died {dd}  ->  {'HIT: ' + ', '.join(c['kind'] for c in near) if near else 'MISS'}")
    P(f"  ACUTE LAYER: {hits}/{len(dead_checks)}")
    P("=" * 104)

    with open(OUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\n[saved to {OUT}]")

if __name__ == "__main__":
    main()
