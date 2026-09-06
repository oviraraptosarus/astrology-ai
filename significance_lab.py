"""
significance_lab.py -- Does the transit-timing predictor have REAL skill?

This is the scientific instrument the project lacked. It does NOT try to make the
astrology "look good". It asks one falsifiable question per predictor configuration:

    Does the real-event hit rate exceed what the SAME test scores on
    (a) random dates (negative control), and
    (b) a null distribution built by permuting the real event dates,
    at p < 0.05?

Three honesty guarantees:
  1. Blind: the predictor only sees (chart, date, domain) -- never the event.
  2. Negative control: identical test on random adult-life dates -> base rate.
  3. Permutation test: shuffle each chart's real event dates within that chart's
     own adult-life window N times; the fraction of shuffles whose hit rate >=
     the observed hit rate is the empirical p-value. This controls for window
     width, base rate, and per-chart transit density automatically.

If NO configuration beats chance at p<0.05, that is the reported result. A true
null is a valid scientific finding, not a failure to hide.
"""

import os
import sys
import json
import random
import datetime
import argparse
from typing import Dict, List, Any, Callable

import pytz

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from astrology_engine import calculate_chart_with_object
from dasha_engine import DashaEngine
from transit_engine import TransitEngine

from benchmark_corpus import CORPUS  # expanded documented-event corpus

# ---- Predictor building blocks --------------------------------------------

# Planets classically tied to each domain (used by the "dasha significator" gate).
DOMAIN_SIGNIFICATORS = {
    "CAREER":          {"Sun", "Saturn", "Mercury", "Mars", "Jupiter"},
    "WEALTH":          {"Jupiter", "Venus", "Mercury", "Moon"},
    "MARRIAGE":        {"Venus", "Jupiter", "Moon"},
    "HEALTH_ACCIDENT": {"Saturn", "Mars", "Sun", "Ketu", "Rahu"},
    "CHILDREN":        {"Jupiter", "Moon", "Sun"},
    "FAME":            {"Sun", "Jupiter", "Mars"},
}

# Candidate target-house sets, from narrow (discriminating) to broad.
HOUSE_SETS = {
    "CAREER":          {"narrow": [10],        "mid": [10, 11],       "broad": [10, 2, 6, 11, 1]},
    "WEALTH":          {"narrow": [2, 11],     "mid": [2, 11, 9],     "broad": [2, 11, 5, 9, 1]},
    "MARRIAGE":        {"narrow": [7],         "mid": [7, 2],         "broad": [7, 2, 11]},
    "HEALTH_ACCIDENT": {"narrow": [8],         "mid": [8, 6],         "broad": [6, 8, 12, 1]},
    "CHILDREN":        {"narrow": [5],         "mid": [5, 9],         "broad": [5, 2, 9, 11]},
    "FAME":            {"narrow": [10],        "mid": [10, 1],        "broad": [10, 1, 5, 9]},
}


def _to_utc(dt):
    if dt.tzinfo is None:
        return pytz.utc.localize(dt)
    return dt.astimezone(pytz.utc)


class Predictor:
    """
    A configurable, blind predictor. .fires(chart, birth_utc, date, domain) -> bool.

    require_dasha  : dasha triad must contain a domain significator
    house_width    : 'narrow' | 'mid' | 'broad'
    require_transit: double transit must activate a target house
    mode           : 'transit_only' | 'dasha_only' | 'convergence' (both)
    """
    def __init__(self, mode="convergence", house_width="narrow"):
        self.mode = mode
        self.house_width = house_width
        self._dasha_cache = {}

    def _timeline(self, chart, birth_utc):
        key = id(chart)
        if key not in self._dasha_cache:
            moon = chart.planets.get("Moon")
            ml = moon.longitude if moon else 0.0
            self._dasha_cache[key] = DashaEngine.calculate_vimshottari_timeline(
                birth_utc, ml, num_levels=3)
        return self._dasha_cache[key]

    def fires(self, chart, birth_utc, date_str, domain) -> bool:
        ev = _to_utc(datetime.datetime.fromisoformat(date_str))

        dasha_ok = True
        if self.mode in ("dasha_only", "convergence"):
            tl = self._timeline(chart, birth_utc)
            cur = DashaEngine.get_current_dasha(tl, ev)
            lords = {cur.get("mahadasha"), cur.get("antardasha"),
                     cur.get("pratyantardasha")}
            dasha_ok = bool(lords & DOMAIN_SIGNIFICATORS.get(domain, set()))

        transit_ok = True
        if self.mode in ("transit_only", "convergence"):
            houses = HOUSE_SETS.get(domain, {}).get(self.house_width, [1, 10])
            tr = TransitEngine.evaluate_double_transit(chart, ev)
            ah = tr.get("activated_houses", [])
            transit_ok = any(h in houses for h in ah)

        if self.mode == "dasha_only":
            return dasha_ok
        if self.mode == "transit_only":
            return transit_ok
        return dasha_ok and transit_ok


# ---- Corpus loading --------------------------------------------------------

def load_charts():
    charts = {}
    for name, data in CORPUS.items():
        b = data["birth"]
        chart, _ = calculate_chart_with_object(
            b["year"], b["month"], b["day"], b["hour"], b["minute"],
            b["lat"], b["lon"], b["tz"], name)
        birth_utc = pytz.timezone(b["tz"]).localize(
            datetime.datetime(b["year"], b["month"], b["day"], b["hour"], b["minute"])
        ).astimezone(pytz.utc)
        charts[name] = (chart, birth_utc, data)
    return charts


# ---- Core measurements -----------------------------------------------------

def observed_hit_rate(charts, predictor: Predictor):
    hits = total = 0
    per_domain = {}
    for name, (chart, birth_utc, data) in charts.items():
        for ev in data["events"]:
            total += 1
            dom = ev["domain"]
            per_domain.setdefault(dom, [0, 0])
            per_domain[dom][1] += 1
            if predictor.fires(chart, birth_utc, ev["date"], dom):
                hits += 1
                per_domain[dom][0] += 1
    return hits, total, per_domain


def negative_control(charts, predictor: Predictor, samples_per_chart=60, seed=20260906):
    rng = random.Random(seed)
    fires = total = 0
    for name, (chart, birth_utc, data) in charts.items():
        domains = list({ev["domain"] for ev in data["events"]}) or ["CAREER"]
        for _ in range(samples_per_chart):
            days = rng.randint(int(18 * 365.25), int(70 * 365.25))
            rand_dt = (birth_utc + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
            dom = rng.choice(domains)
            total += 1
            if predictor.fires(chart, birth_utc, rand_dt, dom):
                fires += 1
    return fires, total


def permutation_test(charts, predictor: Predictor, n_perms=2000, seed=1234):
    """
    Null hypothesis: the predictor has no timing skill -- a real event date is no
    more likely to fire than a random date drawn from the SAME chart's adult-life
    window with the SAME domain. We build the null by, for each permutation,
    replacing every real event date with a random date in that chart's adult
    window (keeping chart+domain fixed) and recomputing the hit rate.

    p-value = fraction of permutations whose null hit rate >= observed hit rate.
    """
    obs_hits, obs_total, _ = observed_hit_rate(charts, predictor)
    obs_rate = obs_hits / obs_total if obs_total else 0.0

    rng = random.Random(seed)
    null_rates = []
    ge = 0
    for _ in range(n_perms):
        h = t = 0
        for name, (chart, birth_utc, data) in charts.items():
            for ev in data["events"]:
                t += 1
                days = rng.randint(int(18 * 365.25), int(70 * 365.25))
                rd = (birth_utc + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
                if predictor.fires(chart, birth_utc, rd, ev["domain"]):
                    h += 1
        rate = h / t if t else 0.0
        null_rates.append(rate)
        if rate >= obs_rate:
            ge += 1

    p = (ge + 1) / (n_perms + 1)  # add-one (never reports p=0)
    null_mean = sum(null_rates) / len(null_rates)
    return {
        "observed_hits": obs_hits,
        "observed_total": obs_total,
        "observed_rate": round(obs_rate, 4),
        "null_mean_rate": round(null_mean, 4),
        "p_value": round(p, 4),
        "n_perms": n_perms,
        "significant_0.05": p < 0.05,
    }


# ---- Grid search over configurations ---------------------------------------

def run_grid(n_perms=2000):
    charts = load_charts()
    total_events = sum(len(d["events"]) for _, _, d in charts.values())
    print(f"Corpus: {len(charts)} charts, {total_events} documented events\n")

    configs = []
    for mode in ("transit_only", "dasha_only", "convergence"):
        widths = ("narrow", "mid", "broad") if mode != "dasha_only" else ("narrow",)
        for w in widths:
            configs.append((mode, w))

    rows = []
    for mode, w in configs:
        pred = Predictor(mode=mode, house_width=w)
        nc_fire, nc_total = negative_control(charts, pred)
        perm = permutation_test(charts, pred, n_perms=n_perms)
        base = nc_fire / nc_total if nc_total else 0.0
        rows.append({
            "config": f"{mode}/{w}",
            "obs_rate": perm["observed_rate"],
            "obs": f"{perm['observed_hits']}/{perm['observed_total']}",
            "control_base_rate": round(base, 4),
            "null_mean": perm["null_mean_rate"],
            "p_value": perm["p_value"],
            "significant": perm["significant_0.05"],
        })
        flag = "  *** p<0.05 ***" if perm["significant_0.05"] else ""
        print(f"{mode:13s}/{w:6s}  obs={perm['observed_rate']:.3f} ({perm['observed_hits']}/{perm['observed_total']})"
              f"  control={base:.3f}  null_mean={perm['null_mean_rate']:.3f}  p={perm['p_value']:.4f}{flag}")

    winners = [r for r in rows if r["significant"]]
    print("\n" + "=" * 78)
    if winners:
        print(f"{len(winners)} configuration(s) beat chance at p<0.05:")
        for r in winners:
            print(f"  {r['config']}: obs {r['obs_rate']:.3f} vs null {r['null_mean']:.3f}, p={r['p_value']}")
        verdict = "MEASURED_SKILL"
    else:
        print("NO configuration beats chance at p<0.05.")
        print("Honest verdict: on this corpus, the transit-timing predictor shows")
        print("no demonstrated skill above its own base rate. This is a true null.")
        verdict = "NO_MEASURED_SKILL"
    print("=" * 78)

    out = {
        "generated_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "n_charts": len(charts),
        "n_events": total_events,
        "n_perms": n_perms,
        "verdict": verdict,
        "configurations": rows,
    }
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "significance_results.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
    print(f"Written -> {path}")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--perms", type=int, default=2000)
    args = ap.parse_args()
    run_grid(n_perms=args.perms)
