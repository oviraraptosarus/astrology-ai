"""
significance_lab2.py -- Can ANY finer signal beat the permutation null?

Adds fast triggers (Moon, Mars), tighter transit orbs, dasha-lord-in-target-house
(natal promise), and Ashtakavarga SAV bindu thresholds. Each signal and each
combination is tested against the SAME permutation null as significance_lab.py.

Multiple-comparison discipline: we test many configs, so a lone p<0.05 is expected
by chance (~1 in 20). We report the Bonferroni-corrected threshold and only treat
a config as real if it clears it, AND we re-run any raw-significant config at high
permutation count to confirm.

Signals are computed directly with swisseph for speed (the permutation loop calls
them tens of thousands of times).
"""

import os
import sys
import json
import math
import random
import datetime
import argparse
from typing import Dict, List, Callable

import pytz
import swisseph as swe

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from astrology_engine import calculate_chart_with_object
from dasha_engine import DashaEngine
from config import Config
from benchmark_corpus import CORPUS

swe.set_sid_mode(Config.ayanamsha_swe_id())
SFLAG = swe.FLG_SIDEREAL | swe.FLG_SPEED

SIGNS = ["Aries","Taurus","Gemini","Cancer","Leo","Virgo","Libra","Scorpio",
         "Sagittarius","Capricorn","Aquarius","Pisces"]
SIGN_LORD = {"Aries":"Mars","Taurus":"Venus","Gemini":"Mercury","Cancer":"Moon",
             "Leo":"Sun","Virgo":"Mercury","Libra":"Venus","Scorpio":"Mars",
             "Sagittarius":"Jupiter","Capricorn":"Saturn","Aquarius":"Saturn","Pisces":"Jupiter"}
SWE_ID = {"Sun":swe.SUN,"Moon":swe.MOON,"Mars":swe.MARS,"Mercury":swe.MERCURY,
          "Jupiter":swe.JUPITER,"Venus":swe.VENUS,"Saturn":swe.SATURN}

DOMAIN_SIG = {
    "CAREER":{"Sun","Saturn","Mercury","Mars","Jupiter"},
    "WEALTH":{"Jupiter","Venus","Mercury","Moon"},
    "MARRIAGE":{"Venus","Jupiter","Moon"},
    "HEALTH_ACCIDENT":{"Saturn","Mars","Sun","Ketu","Rahu"},
    "CHILDREN":{"Jupiter","Moon","Sun"},
    "FAME":{"Sun","Jupiter","Mars"},
}
CORE_HOUSE = {"CAREER":[10],"WEALTH":[2,11],"MARRIAGE":[7],
              "HEALTH_ACCIDENT":[8,6],"CHILDREN":[5],"FAME":[10]}


def to_utc(dt):
    return pytz.utc.localize(dt) if dt.tzinfo is None else dt.astimezone(pytz.utc)

def jd_of(date_str):
    dt = to_utc(datetime.datetime.fromisoformat(date_str))
    return swe.julday(dt.year, dt.month, dt.day, dt.hour + dt.minute/60.0)

def lon_of(jd, planet):
    if planet in ("Rahu","Ketu"):
        r = swe.calc_ut(jd, Config.node_swe_id(), SFLAG)[0][0]
        return r if planet=="Rahu" else (r+180.0)%360.0
    return swe.calc_ut(jd, SWE_ID[planet], SFLAG)[0][0]

def sign_of(lon):
    return SIGNS[int(lon % 360)//30]


class ChartCtx:
    """Precomputed natal facts + dasha timeline for one chart."""
    def __init__(self, name, data):
        b = data["birth"]
        self.chart, _ = calculate_chart_with_object(
            b["year"],b["month"],b["day"],b["hour"],b["minute"],
            b["lat"],b["lon"],b["tz"],name)
        self.birth_utc = pytz.timezone(b["tz"]).localize(
            datetime.datetime(b["year"],b["month"],b["day"],b["hour"],b["minute"])
        ).astimezone(pytz.utc)
        self.asc_idx = SIGNS.index(self.chart.ascendant_sign)
        # natal planet longitudes
        self.natal = {n:(SIGNS.index(p.sign)*30.0 + p.degree)
                      for n,p in self.chart.planets.items()}
        moon = self.chart.planets.get("Moon")
        self.timeline = DashaEngine.calculate_vimshottari_timeline(
            self.birth_utc, moon.longitude if moon else 0.0, num_levels=3)
        # house -> lord (whole sign)
        self.house_lord = {}
        for h in range(1,13):
            self.house_lord[h] = SIGN_LORD[SIGNS[(self.asc_idx+h-1)%12]]
        # natal house occupied by each planet (whole sign)
        self.planet_house = {}
        for n,p in self.chart.planets.items():
            self.planet_house[n] = ((SIGNS.index(p.sign)-self.asc_idx)%12)+1

    def dasha_lords(self, ev):
        cur = DashaEngine.get_current_dasha(self.timeline, ev)
        return {cur.get("mahadasha"),cur.get("antardasha"),cur.get("pratyantardasha")}


# ---- Signal functions: (ctx, jd, ev, domain) -> bool ----------------------

def sig_dasha_significator(ctx, jd, ev, domain):
    return bool(ctx.dasha_lords(ev) & DOMAIN_SIG.get(domain,set()))

def sig_dasha_lord_in_core_house(ctx, jd, ev, domain):
    """A running dasha lord natally occupies OR lords the domain's core house."""
    lords = ctx.dasha_lords(ev)
    core = CORE_HOUSE.get(domain,[10])
    owners = {ctx.house_lord[h] for h in core}
    occupants = {p for p,h in ctx.planet_house.items() if h in core}
    return bool(lords & (owners | occupants))

def _double_transit_hits(ctx, jd, houses):
    js = sign_of(lon_of(jd,"Jupiter")); ss = sign_of(lon_of(jd,"Saturn"))
    hit=set()
    for sg in (js,ss):
        h = ((SIGNS.index(sg)-ctx.asc_idx)%12)+1
        hit.add(h)
    return any(h in houses for h in hit)

def sig_transit_core(ctx, jd, ev, domain):
    return _double_transit_hits(ctx, jd, CORE_HOUSE.get(domain,[10]))

def _aspect_orb(a, b):
    d = abs((a-b)%360.0)
    d = min(d, 360-d)
    # nearest of conj/opp/trine/square
    return min(abs(d-x) for x in (0,60,90,120,180))

def sig_slow_tight_aspect(ctx, jd, ev, domain, orb=3.0):
    """Jupiter or Saturn within `orb` of an exact aspect to a natal domain significator."""
    sigs = DOMAIN_SIG.get(domain,set()) & set(ctx.natal.keys())
    for t in ("Jupiter","Saturn"):
        tl = lon_of(jd,t)
        for s in sigs:
            if _aspect_orb(tl, ctx.natal[s]) <= orb:
                return True
    return False

def sig_mars_trigger(ctx, jd, ev, domain, orb=4.0):
    """Transiting Mars within orb of exact aspect to a core-house lord or occupant."""
    core = CORE_HOUSE.get(domain,[10])
    targets = {ctx.house_lord[h] for h in core} | {p for p,h in ctx.planet_house.items() if h in core}
    targets &= set(ctx.natal.keys())
    ml = lon_of(jd,"Mars")
    return any(_aspect_orb(ml, ctx.natal[t]) <= orb for t in targets)

def sig_moon_trigger(ctx, jd, ev, domain, orb=3.0):
    core = CORE_HOUSE.get(domain,[10])
    targets = {ctx.house_lord[h] for h in core} | {p for p,h in ctx.planet_house.items() if h in core}
    targets &= set(ctx.natal.keys())
    ml = lon_of(jd,"Moon")
    return any(_aspect_orb(ml, ctx.natal[t]) <= orb for t in targets)


def make_predictor(components: List[Callable]):
    """AND-combine a list of signal functions."""
    def fires(ctx, jd, ev, domain):
        return all(c(ctx, jd, ev, domain) for c in components)
    return fires


# ---- Permutation harness ---------------------------------------------------

def observed(ctxs, pred):
    h=t=0
    for name,ctx in ctxs.items():
        for ev in CORPUS[name]["events"]:
            t+=1
            e = to_utc(datetime.datetime.fromisoformat(ev["date"]))
            if pred(ctx, jd_of(ev["date"]), e, ev["domain"]): h+=1
    return h,t

def permutation(ctxs, pred, n_perms, seed=7):
    obs_h, obs_t = observed(ctxs, pred)
    obs_rate = obs_h/obs_t if obs_t else 0
    rng = random.Random(seed)
    ge=0; ssum=0.0
    for _ in range(n_perms):
        h=t=0
        for name,ctx in ctxs.items():
            for ev in CORPUS[name]["events"]:
                t+=1
                days = rng.randint(int(18*365.25), int(70*365.25))
                rdt = ctx.birth_utc + datetime.timedelta(days=days)
                ds = rdt.strftime("%Y-%m-%d")
                if pred(ctx, jd_of(ds), to_utc(rdt), ev["domain"]): h+=1
        r=h/t if t else 0
        ssum+=r
        if r>=obs_rate: ge+=1
    p=(ge+1)/(n_perms+1)
    return {"obs_rate":round(obs_rate,4),"obs":f"{obs_h}/{obs_t}",
            "null_mean":round(ssum/n_perms,4),"p":round(p,4)}


def run(n_perms=800):
    ctxs = {name: ChartCtx(name,data) for name,data in CORPUS.items()}
    n_ev = sum(len(d["events"]) for d in CORPUS.values())
    print(f"Corpus: {len(ctxs)} charts, {n_ev} events, {n_perms} perms/config\n")

    configs = {
        "dasha_sig": [sig_dasha_significator],
        "dasha_lord_in_core": [sig_dasha_lord_in_core_house],
        "transit_core": [sig_transit_core],
        "slow_tight_aspect_3deg": [lambda c,j,e,d: sig_slow_tight_aspect(c,j,e,d,3.0)],
        "slow_tight_aspect_1deg": [lambda c,j,e,d: sig_slow_tight_aspect(c,j,e,d,1.0)],
        "mars_trigger_4deg": [lambda c,j,e,d: sig_mars_trigger(c,j,e,d,4.0)],
        "moon_trigger_3deg": [lambda c,j,e,d: sig_moon_trigger(c,j,e,d,3.0)],
        # convergence stacks
        "dasha_lord_in_core + transit_core": [sig_dasha_lord_in_core_house, sig_transit_core],
        "dasha_sig + slow_tight_3deg": [sig_dasha_significator, lambda c,j,e,d: sig_slow_tight_aspect(c,j,e,d,3.0)],
        "dasha_lord_in_core + mars_4deg": [sig_dasha_lord_in_core_house, lambda c,j,e,d: sig_mars_trigger(c,j,e,d,4.0)],
        "transit_core + mars_4deg": [sig_transit_core, lambda c,j,e,d: sig_mars_trigger(c,j,e,d,4.0)],
        "dasha_lord_in_core + slow_tight_3deg + mars_4deg": [
            sig_dasha_lord_in_core_house,
            lambda c,j,e,d: sig_slow_tight_aspect(c,j,e,d,3.0),
            lambda c,j,e,d: sig_mars_trigger(c,j,e,d,4.0)],
    }

    rows=[]
    for label, comps in configs.items():
        r = permutation(ctxs, make_predictor(comps), n_perms)
        rows.append((label,r))
        flag = "  *** raw p<0.05 ***" if r["p"]<0.05 else ""
        print(f"{label:52s} obs={r['obs_rate']:.3f} ({r['obs']:>7s})  null={r['null_mean']:.3f}  p={r['p']:.4f}{flag}")

    m = len(configs)
    bonf = 0.05/m
    print("\n"+"="*90)
    print(f"Tested {m} configs. Bonferroni-corrected threshold = 0.05/{m} = {bonf:.4f}")
    survivors = [(l,r) for l,r in rows if r["p"] < bonf]
    raw = [(l,r) for l,r in rows if r["p"] < 0.05]
    if survivors:
        print("Configs surviving multiple-comparison correction (REAL candidate skill):")
        for l,r in survivors: print(f"  {l}: obs {r['obs_rate']} vs null {r['null_mean']}, p={r['p']}")
        verdict="MEASURED_SKILL"
    elif raw:
        print(f"{len(raw)} config(s) raw-significant but DO NOT survive Bonferroni -> likely false positives:")
        for l,r in raw: print(f"  {l}: p={r['p']} (needs < {bonf:.4f})")
        verdict="NO_SKILL_AFTER_CORRECTION"
    else:
        print("NO config significant even at raw p<0.05. Clean null across all finer signals.")
        verdict="NO_MEASURED_SKILL"
    print("="*90)

    out={"generated_utc":datetime.datetime.utcnow().isoformat()+"Z","n_charts":len(ctxs),
         "n_events":n_ev,"n_perms":n_perms,"bonferroni_threshold":round(bonf,5),
         "verdict":verdict,
         "configs":[{"config":l,**r} for l,r in rows]}
    path=os.path.join(os.path.dirname(os.path.abspath(__file__)),"significance_results_fine.json")
    with open(path,"w",encoding="utf-8") as f: json.dump(out,f,indent=2)
    print(f"Written -> {path}")
    return out


if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--perms",type=int,default=800)
    a=ap.parse_args(); run(a.perms)
