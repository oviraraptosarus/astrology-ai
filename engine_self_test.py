"""
engine_self_test.py — Golden-chart + provider regression checks for the Astrology AI engine.

Used by:
  * /api/health/ai  (app.py) — live self-test on the published site
  * pre_publish_check.py — run before every deploy

Pure deterministic checks, ZERO LLM calls. This catches the bugs that the
synthesis models can never see: corrupted dasha seeds (nakshatra wrong),
engine-path disagreements, and decommissioned provider models.
"""
import os
import time
from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()  # safe both standalone and when app.py already loaded it

# ── TTL cache: health endpoints get polled; full chart calc ×2 per call is heavy ──
_cache = {"golden": (0.0, None), "providers": (0.0, None)}
CACHE_TTL_S = 60.0


def _cached(key, ttl, fn, *args):
    ts, val = _cache[key]
    now = time.time()
    if val is not None and now - ts < ttl:
        return val
    val = fn(*args)
    _cache[key] = (now, val)
    return val

# ── Golden charts: locked against JHora + PyJHora reference values ──────────
GOLDEN = [
    {
        "key": "sajal_2006",  # Sajal Kumar Mishra — JHora-verified (Venus/Mercury/Mars PD)
        "year": 2006, "month": 3, "day": 3, "hour": 18, "minute": 20,
        "lat": 17.385, "lon": 78.4867, "tz": "Asia/Kolkata",
        "moon_sign": "Aries", "moon_deg": (7.45, 7.60),
        "nak": "Ashwini", "pada": 3, "lord": "Ketu",
        "md_seq": ["Ketu", "Venus", "Sun", "Moon", "Mars"],
        "check_date": datetime(2026, 9, 6),
        "expect_md": "Venus", "expect_ad": "Mercury", "expect_pd": "Mars",
    },
    {
        "key": "user_2008",  # natal chart — PyJHora-validated (Moon Cancer 17.17, Ashlesha)
        "year": 2008, "month": 8, "day": 1, "hour": 18, "minute": 25,
        "lat": 16.8186, "lon": 82.0641, "tz": "Asia/Kolkata",
        "moon_sign": "Cancer", "moon_deg": (17.10, 17.25),
        "nak": "Ashlesha", "pada": 1, "lord": "Mercury",
        "md_seq": ["Mercury", "Ketu", "Venus", "Sun", "Moon"],
        "check_date": datetime(2026, 9, 6),
        "expect_md": "Ketu", "expect_ad": "Sun", "expect_pd": "Jupiter",  # PD locked: engines agree at golden date
    },
]


def _check_timeline_integrity(tl):
    """Structural invariants independent of any reference values.
    Catches shared-logic corruption (e.g. wrong ayanamsa, broken AD order) that
    both engines would reproduce identically and thus agree on."""
    from dasha_engine import DashaEngine
    lords = DashaEngine.DASHA_LORDS
    checks = []

    def chk(name, ok, detail=""):
        checks.append({"name": name, "ok": bool(ok), "detail": str(detail)})

    if not tl:
        chk("has_mahadashas", False, "empty timeline")
        return checks

    # MDs: no gaps/overlaps, lords follow Vimshottari cyclic order from birth lord
    prev_end = tl[0]["start"]
    md_start_idx = lords.index(tl[0]["lord"]) if tl else 0
    for i, md in enumerate(tl):
        chk(f"md_{i}_no_gap", md["start"] == prev_end, f"{md['start']} vs {prev_end}")
        chk(f"md_{i}_order", md["lord"] == lords[(md_start_idx + i) % 9],
            f"{md['lord']} vs {lords[(md_start_idx + i) % 9]}")
        chk(f"md_{i}_span", md["end"] > md["start"], "end<=start")
        prev_end = md["end"]

    # AD/PD cycles: sub-lords must be a CONTIGUOUS cyclic run in Vimshottari
    # order (the birth MD is fractional, so its AD/PD cycle legitimately starts
    # mid-cycle and has fewer than 9 entries — that is CORRECT, not a bug).
    def _is_cyclic_run(lord_list, start_lord):
        if not lord_list:
            return True
        start = lords.index(start_lord)
        for j, name in enumerate(lord_list):
            if name != lords[(start + j) % 9]:
                return False
        return True

    for mi, md in enumerate(tl):
        ads = md.get("sub_periods", [])
        if not ads:
            continue
        ad_lords = [a["lord"] for a in ads]
        chk(f"md{mi}_ad_cycle", _is_cyclic_run(ad_lords, ad_lords[0]), f"{ad_lords}")
        prev = md["start"]
        for a in ads:
            chk(f"md{mi}_ad_contig", a["start"] == prev, f"{a['start']} vs {prev}")
            prev = a["end"]
            pds = a.get("sub_periods", [])
            if not pds:
                continue
            pd_lords = [p["lord"] for p in pds]
            chk(f"ad_{a['lord']}_pd_cycle", _is_cyclic_run(pd_lords, pd_lords[0]), f"{pd_lords}")
            p_prev = a["start"]
            for p in pds:
                chk(f"ad_{a['lord']}_pd_contig", p["start"] == p_prev, f"{p['start']} vs {p_prev}")
                p_prev = p["end"]

    return checks


def run_golden_checks():
    """Compute both golden charts and verify every locked value.
    Cached 60s (health endpoints get polled; full chart calc ×2 is heavy).
    Returns {chart_key: {ok: bool, checks: [{name, ok, detail}]}}."""
    return _cached("golden", CACHE_TTL_S, _run_golden_checks_uncached)


def _run_golden_checks_uncached():
    from astrology_engine import calculate_chart_with_object
    from dasha_engine import DashaEngine

    results = {}
    for g in GOLDEN:
        checks = []
        def chk(name, ok, detail=""):
            checks.append({"name": name, "ok": bool(ok), "detail": str(detail)})

        try:
            chart_obj, chart_dict = calculate_chart_with_object(
                g["year"], g["month"], g["day"], g["hour"], g["minute"],
                g["lat"], g["lon"], g["tz"])

            moon = chart_obj.planets["Moon"]
            moon_lon = chart_obj.get_sign_index(moon.sign) * 30 + moon.degree

            # Stable natal facts
            chk("moon_sign", moon.sign == g["moon_sign"], f"{moon.sign} (want {g['moon_sign']})")
            chk("moon_degree", g["moon_deg"][0] <= moon.degree <= g["moon_deg"][1],
                f"{moon.degree:.2f} (want {g['moon_deg']})")
            chk("nakshatra", moon.nakshatra == g["nak"], f"{moon.nakshatra} (want {g['nak']})")
            chk("pada", moon.nakshatra_pada == g["pada"], f"{moon.nakshatra_pada} (want {g['pada']})")
            chk("nak_lord", moon.nakshatra_lord == g["lord"], f"{moon.nakshatra_lord} (want {g['lord']})")

            # Mahadasha sequence (DashaEngine timeline from birth)
            utc = pytz.timezone(g["tz"]).localize(
                datetime(g["year"], g["month"], g["day"], g["hour"], g["minute"])
            ).astimezone(pytz.utc).replace(tzinfo=None)
            tl = DashaEngine.calculate_vimshottari_timeline(utc, moon_lon, num_levels=3)
            seq = [m["lord"] for m in tl[:5]]
            chk("md_seq", seq == g["md_seq"], f"{seq} (want {g['md_seq']})")

            # Structural integrity: cyclic order, contiguity, 9 sub-periods each.
            # Independent of reference values — catches shared-logic corruption.
            for ic in _check_timeline_integrity(tl):
                if not ic["ok"]:
                    checks.append(ic)

            # Current dasha at the FIXED golden date (deterministic, never drifts)
            de = DashaEngine.get_current_dasha(tl, g["check_date"])
            chk("md", de["mahadasha"] == g["expect_md"],
                f"{de['mahadasha']} (want {g['expect_md']})")
            chk("ad", de["antardasha"] == g["expect_ad"],
                f"{de['antardasha']} (want {g['expect_ad']})")
            if g.get("expect_pd"):
                chk("pd", de["pratyantardasha"] == g["expect_pd"],
                    f"{de['pratyantardasha']} (want {g['expect_pd']})")

            # Cross-engine consistency TODAY (inline astrology_engine vs DashaEngine).
            # Catches the earlier Ketu-Venus vs Ketu-Sun disagreement class of bug.
            ae = chart_dict.get("Current_Dasha", {})
            today = datetime.now(pytz.utc)
            de_today = DashaEngine.get_current_dasha(tl, today.replace(tzinfo=None))
            chk("engines_agree_md", de_today["mahadasha"] == ae.get("Mahadasha"),
                f"dasha_engine={de_today['mahadasha']} astrology_engine={ae.get('Mahadasha')}")
            chk("engines_agree_ad", de_today["antardasha"] == ae.get("Antardasha"),
                f"dasha_engine={de_today['antardasha']} astrology_engine={ae.get('Antardasha')}")
            if de_today["pratyantardasha"] or ae.get("Pratyantardasha"):
                chk("engines_agree_pd", de_today["pratyantardasha"] == ae.get("Pratyantardasha"),
                    f"dasha_engine={de_today['pratyantardasha']} astrology_engine={ae.get('Pratyantardasha')}")

        except Exception as e:
            chk("exception", False, f"{type(e).__name__}: {e}")

        results[g["key"]] = {"ok": all(c["ok"] for c in checks), "checks": checks}
    return results


# ── Provider model probes: catch decommissioned/renamed models ──────────────
DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"          # llama-3.3-70b-versatile was removed by Groq
DEFAULT_OPENROUTER_MODEL = "liquid/lfm-2.5-2.6b:free"


def _probe_openai_compatible(url, key, configured_model):
    """GET {url}/models; verify the configured model still exists."""
    import requests
    try:
        r = requests.get(f"{url}/models",
                         headers={"Authorization": f"Bearer {key}"},
                         timeout=6)
        if r.status_code != 200:
            return f"DOWN (HTTP {r.status_code})"
        ids = [m.get("id") for m in r.json().get("data", [])]
        if configured_model not in ids:
            return f"UP — MODEL MISSING: '{configured_model}' not in provider list"
        return "UP"
    except Exception as e:
        return f"DOWN ({type(e).__name__})"


def _probe_google(api_key, configured_model):
    """Gemini REST models list: verify the configured model still exists."""
    import requests
    try:
        r = requests.get(
            "https://generativelanguage.googleapis.com/v1beta/models",
            params={"key": api_key}, timeout=6)
        if r.status_code != 200:
            return f"DOWN (HTTP {r.status_code})"
        ids = [m.get("name", "").replace("models/", "") for m in r.json().get("models", [])]
        if configured_model not in ids:
            return f"UP — MODEL MISSING: '{configured_model}' not in Gemini list"
        return "UP"
    except Exception as e:
        return f"DOWN ({type(e).__name__})"


def probe_providers():
    """Live provider checks (cached 60s). Returns {provider: status}."""
    return _cached("providers", CACHE_TTL_S, _probe_providers_uncached)


def _probe_providers_uncached():
    """Live provider checks. Returns {provider: status}."""
    import requests
    health = {}

    key = os.getenv("GROQ_API_KEY")
    health["Groq"] = (_probe_openai_compatible("https://api.groq.com/openai/v1", key,
                                               os.getenv("GROQ_MODEL", DEFAULT_GROQ_MODEL))
                      if key else "NOT_CONFIGURED")

    key = os.getenv("OPENROUTER_API_KEY")
    health["OpenRouter"] = (_probe_openai_compatible("https://openrouter.ai/api/v1", key,
                                                     DEFAULT_OPENROUTER_MODEL)
                            if key else "NOT_CONFIGURED")

    key = os.getenv("GOOGLE_API_KEY")
    gemini_model = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    health["Google"] = (_probe_google(key, gemini_model) if key else "NOT_CONFIGURED")

    try:
        r = requests.get("http://localhost:20128/v1/models", timeout=1.0)
        health["OmniRoute"] = "UP" if r.status_code == 200 else "DOWN"
    except Exception:
        health["OmniRoute"] = "DOWN"

    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=1.0)
        health["Ollama"] = "UP" if r.status_code == 200 else "DOWN"
    except Exception:
        health["Ollama"] = "DOWN"

    return health
