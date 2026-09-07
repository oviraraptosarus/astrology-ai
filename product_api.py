"""
product_api.py — Consumer product layer over the deterministic engine.

This is the SINGLE translation boundary between the sophisticated Jyotisha
engine and the simple, calm consumer UI. It turns large internal engine
objects into small, human-readable schemas the PWA frontend renders directly.

Design contract:
  * The browser NEVER recomputes astrology. It renders what this layer returns.
  * Level 1 plain-language insight is always up front.
  * Deeper evidence (Level 2 explanation, Level 3 factors, Level 4 raw judgment)
    is available but never forced on the user.
  * Every accessor uses .get() with safe fallbacks — a partial engine result
    must degrade gracefully, never 500 the product UI.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta

# ── Presentation metadata ────────────────────────────────────────────────────
SIGN_GLYPH = {
    "Aries": "\u2648", "Taurus": "\u2649", "Gemini": "\u264a", "Cancer": "\u264b",
    "Leo": "\u264c", "Virgo": "\u264d", "Libra": "\u264e", "Scorpio": "\u264f",
    "Sagittarius": "\u2650", "Capricorn": "\u2651", "Aquarius": "\u2652", "Pisces": "\u2653",
}
SIGN_ELEMENT = {
    "Aries": "Fire", "Leo": "Fire", "Sagittarius": "Fire",
    "Taurus": "Earth", "Virgo": "Earth", "Capricorn": "Earth",
    "Gemini": "Air", "Libra": "Air", "Aquarius": "Air",
    "Cancer": "Water", "Scorpio": "Water", "Pisces": "Water",
}
SIGN_MODALITY = {
    "Aries": "Cardinal", "Cancer": "Cardinal", "Libra": "Cardinal", "Capricorn": "Cardinal",
    "Taurus": "Fixed", "Leo": "Fixed", "Scorpio": "Fixed", "Aquarius": "Fixed",
    "Gemini": "Mutable", "Virgo": "Mutable", "Sagittarius": "Mutable", "Pisces": "Mutable",
}
SIGN_RULER = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}
PLANET_GLYPH = {
    "Sun": "\u2609", "Moon": "\u263d", "Mars": "\u2642", "Mercury": "\u263f",
    "Jupiter": "\u2643", "Venus": "\u2640", "Saturn": "\u2644",
    "Rahu": "\u260a", "Ketu": "\u260b", "Ascendant": "Asc",
}
PLANET_THEME = {
    "Sun": "identity, confidence, and how you shine",
    "Moon": "emotions, comfort, and your inner world",
    "Mars": "drive, courage, and how you take action",
    "Mercury": "thinking, communication, and skill",
    "Jupiter": "growth, wisdom, and opportunity",
    "Venus": "love, beauty, and what you value",
    "Saturn": "discipline, patience, and long work",
    "Rahu": "ambition, hunger, and the unconventional",
    "Ketu": "detachment, intuition, and letting go",
}
SIGN_PERSONA = {
    "Aries": "direct, energetic, and quick to begin",
    "Taurus": "steady, grounded, and pleasure-loving",
    "Gemini": "curious, quick-witted, and communicative",
    "Cancer": "caring, intuitive, and protective",
    "Leo": "warm, expressive, and proud",
    "Virgo": "precise, practical, and improving",
    "Libra": "balanced, relational, and refined",
    "Scorpio": "intense, private, and transformative",
    "Sagittarius": "optimistic, free, and philosophical",
    "Capricorn": "ambitious, disciplined, and enduring",
    "Aquarius": "independent, inventive, and humane",
    "Pisces": "imaginative, gentle, and boundless",
}
HOUSE_THEME = {
    1: ("Self", "identity, body, and how you meet the world"),
    2: ("Wealth & Family", "money, speech, food, and close family"),
    3: ("Courage", "siblings, effort, skills, and communication"),
    4: ("Home & Heart", "mother, home, property, and inner peace"),
    5: ("Creativity", "children, romance, intellect, and creativity"),
    6: ("Work & Health", "daily work, health, debts, and rivals"),
    7: ("Partnership", "marriage, partners, and one-to-one relationships"),
    8: ("Transformation", "depth, change, shared resources, and the hidden"),
    9: ("Fortune", "luck, beliefs, teachers, and long journeys"),
    10: ("Career", "career, status, reputation, and public life"),
    11: ("Gains", "income, networks, hopes, and fulfilment"),
    12: ("Release", "solitude, foreign lands, rest, and letting go"),
}
DOMAINS = [
    ("career", "Career", "Work, status & purpose"),
    ("marriage", "Relationships", "Love, marriage & partnership"),
    ("wealth", "Wealth", "Money, income & assets"),
    ("health", "Health", "Vitality & wellbeing"),
]
MONTHS = ["", "January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]

_PROMISE_TONE = {
    "VERY STRONG": ("strong", "A genuinely strong area of your life."),
    "STRONG": ("strong", "A well-supported area of your life."),
    "MODERATE": ("mixed", "A mixed area — real potential, with some friction."),
    "PROMISING": ("mixed", "Promising, with a few things to work through."),
    "WEAK": ("tender", "A more tender area that rewards patience."),
    "CHALLENGED": ("tender", "An area that asks for care and effort."),
    "INSUFFICIENT": ("neutral", "Not strongly emphasised in your chart."),
}


# ── small helpers ─────────────────────────────────────────────────────────────
def _sign_meta(sign: str) -> dict:
    return {
        "sign": sign or "",
        "glyph": SIGN_GLYPH.get(sign, ""),
        "element": SIGN_ELEMENT.get(sign, ""),
        "modality": SIGN_MODALITY.get(sign, ""),
        "ruler": SIGN_RULER.get(sign, ""),
    }


def _fmt_degree(deg) -> str:
    try:
        d = float(deg)
    except (TypeError, ValueError):
        return ""
    whole = int(d)
    minutes = int(round((d - whole) * 60))
    if minutes == 60:
        whole, minutes = whole + 1, 0
    return f"{whole}\u00b0{minutes:02d}'"


def _dignity_tone(dignity: str) -> str:
    d = (dignity or "").lower()
    if any(k in d for k in ("exalt", "moolatrikona", "own")):
        return "strong"
    if any(k in d for k in ("debilit", "great enemy", "enemy", "combust")):
        return "challenged"
    return "neutral"


def _dignity_label(dignity: str) -> str:
    d = (dignity or "").strip()
    return d if d else "Neutral"


# ── planet cards ──────────────────────────────────────────────────────────────
def planet_card(name: str, pdata: dict, deep: bool = False) -> dict:
    """Level 1 planet card. `deep=True` adds Level 3 evidence fields."""
    sign = pdata.get("sign", "")
    house = pdata.get("house")
    dignity = pdata.get("dignity", "")
    nak = pdata.get("nakshatra", "")
    theme = PLANET_THEME.get(name, "")
    house_name = HOUSE_THEME.get(house, ("", ""))[0] if house else ""
    tone = _dignity_tone(dignity)

    plain = f"Your {theme}"
    if sign:
        plain = f"{theme.capitalize()} expressed through {SIGN_PERSONA.get(sign, sign)}."

    card = {
        "planet": name,
        "glyph": PLANET_GLYPH.get(name, ""),
        "sign": sign,
        "sign_glyph": SIGN_GLYPH.get(sign, ""),
        "degree": _fmt_degree(pdata.get("degree")),
        "house": house,
        "house_name": house_name,
        "nakshatra": nak,
        "dignity": _dignity_label(dignity),
        "tone": tone,
        "retrograde": bool(pdata.get("retrograde")),
        "theme": theme,
        "plain": plain,
    }
    if deep:
        card["owns_houses"] = pdata.get("owns_houses", [])
        card["aspected_by"] = pdata.get("aspected_by", [])
        card["conjunct_with"] = pdata.get("conjunct_with", [])
        card["nakshatra_pada"] = pdata.get("nakshatra_pada")
        card["dispositor"] = pdata.get("dispositor", "")
    return card


# ── identity ────────────────────────────────────────────────────────────────
def _identity(chart: dict) -> dict:
    basic = chart.get("Basic_Chart", {})
    asc = basic.get("Ascendant", {})
    moon = basic.get("Moon", {})
    sun = basic.get("Sun", {})
    asc_sign = asc.get("sign", "")
    moon_sign = moon.get("sign", "")
    sun_sign = sun.get("sign", "")
    moon_nak = moon.get("nakshatra", "")

    headline_bits = []
    if moon_sign:
        headline_bits.append(SIGN_PERSONA.get(moon_sign, moon_sign))
    summary = ""
    if asc_sign and moon_sign:
        vp = SIGN_PERSONA.get(asc_sign, asc_sign)
        article = "an" if vp and vp[0].lower() in "aeiou" else "a"
        summary = (
            f"You lead with {article} {vp} presence, "
            f"and feel most yourself when your world is {SIGN_PERSONA.get(moon_sign, moon_sign)}."
        )
    return {
        "ascendant": _sign_meta(asc_sign),
        "moon": {**_sign_meta(moon_sign), "nakshatra": moon_nak},
        "sun": _sign_meta(sun_sign),
        "nakshatra": moon_nak,
        "headline": ", ".join(headline_bits).capitalize() if headline_bits else "",
        "summary": summary,
    }


# ── dasha (life period) ───────────────────────────────────────────────────────
def _period_years(start: str, end: str) -> str:
    def yr(s):
        return (s or "").split("-")[0]
    a, b = yr(start), yr(end)
    return f"{a}\u2013{b}" if a and b else ""


def dasha_period(chart: dict) -> dict:
    d = chart.get("Current_Dasha", {})
    md = d.get("Mahadasha", "")
    ad = d.get("Antardasha", "")
    pd = d.get("Pratyantardasha", "")
    theme = PLANET_THEME.get(md, "")
    sub_theme = PLANET_THEME.get(ad, "")
    plain = ""
    if md and ad:
        plain = (
            f"You are in a {md} main period, coloured right now by {ad}. "
            f"The season emphasises {theme}, with a current focus on {sub_theme}."
        )
    return {
        "maha": md,
        "maha_glyph": PLANET_GLYPH.get(md, ""),
        "antar": ad,
        "pratyantar": pd,
        "maha_theme": theme,
        "antar_theme": sub_theme,
        "years": _period_years(d.get("Mahadasha_Start"), d.get("Mahadasha_End")),
        "start": d.get("Mahadasha_Start", ""),
        "end": d.get("Mahadasha_End", ""),
        "plain": plain,
        "label": f"{md} \u2192 {ad} \u2192 {pd}" if md else "",
    }


# ── daily insight ─────────────────────────────────────────────────────────────
def daily_insight(chart: dict) -> dict:
    pan = chart.get("Panchanga", {})
    transits = chart.get("Live_Transits_Gochar", {})
    moon_t = transits.get("Moon", {})
    moon_sign_today = moon_t.get("current_sign", "")
    house_from_moon = moon_t.get("house_from_natal_moon")

    # Plain daily read from where the transiting Moon sits relative to natal Moon.
    house_focus = HOUSE_THEME.get(house_from_moon, ("", "the day's rhythm"))
    plain = ""
    if moon_sign_today and house_focus[0]:
        plain = (
            f"Today the Moon moves through {moon_sign_today}, lighting up "
            f"{house_focus[0].lower()} — {house_focus[1]}. A good day to attend to that."
        )
    elif moon_sign_today:
        plain = f"Today the Moon moves through {moon_sign_today}. Follow its calm, steady rhythm."

    return {
        "date_label": _pretty_today(),
        "tithi": pan.get("Tithi", ""),
        "vara": pan.get("Vara", ""),
        "nakshatra": pan.get("Nakshatra", ""),
        "yoga": pan.get("Yoga", ""),
        "karana": pan.get("Karana", ""),
        "moon_sign_today": moon_sign_today,
        "moon_glyph": SIGN_GLYPH.get(moon_sign_today, ""),
        "focus": house_focus[0],
        "plain": plain,
    }


# ── transits (right now) ──────────────────────────────────────────────────────
_MAJOR = ["Saturn", "Jupiter", "Rahu", "Ketu", "Mars"]


def transit_highlights(chart: dict, limit: int = 4) -> list:
    transits = chart.get("Live_Transits_Gochar", {})
    out = []
    for p in _MAJOR:
        t = transits.get(p)
        if not t:
            continue
        sign = t.get("current_sign", "")
        hfm = t.get("house_from_natal_moon")
        theme = PLANET_THEME.get(p, "")
        hname = HOUSE_THEME.get(hfm, ("", ""))
        plain = ""
        if sign and hname[0]:
            plain = f"{p} is transiting {sign}, active in your {hname[0].lower()} zone ({hname[1]})."
        elif sign:
            plain = f"{p} is transiting {sign}."
        out.append({
            "planet": p,
            "glyph": PLANET_GLYPH.get(p, ""),
            "sign": sign,
            "sign_glyph": SIGN_GLYPH.get(sign, ""),
            "house_from_moon": hfm,
            "focus": hname[0],
            "retrograde": bool(t.get("is_retrograde_today")),
            "theme": theme,
            "plain": plain,
        })
        if len(out) >= limit:
            break
    return out


# ── yogas (notable patterns) ──────────────────────────────────────────────────
def notable_yogas(chart: dict, limit: int = 6) -> list:
    yogas = chart.get("Yogas_Found", []) or []
    fired = [y for y in yogas if y.get("fired", True)]
    ranked = sorted(fired, key=lambda y: {"HIGH": 0, "MODERATE": 1, "LOW": 2}.get(str(y.get("confidence", "")).upper(), 3))
    out = []
    for y in ranked[:limit]:
        pol = str(y.get("polarity", "")).lower()
        tone = "strong" if "benef" in pol or "positive" in pol or pol == "supporting" else (
            "challenged" if "malef" in pol or "negative" in pol or pol == "contradicting" else "neutral")
        out.append({
            "name": y.get("name", ""),
            "domain": y.get("domain", ""),
            "tone": tone,
            "confidence": str(y.get("confidence", "")).title(),
            "reason": y.get("reason", ""),
        })
    return out


# ── chart summary (My Chart screen) ───────────────────────────────────────────
def chart_summary(chart: dict) -> dict:
    basic = chart.get("Basic_Chart", {})
    planets = []
    for name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
        p = basic.get(name)
        if p:
            planets.append(planet_card(name, p))

    asc_sign = basic.get("Ascendant", {}).get("sign", "")
    houses = []
    # Build houses from Ascendant sign (whole-sign): house N holds a sign.
    zodiac = list(SIGN_GLYPH.keys())
    if asc_sign in zodiac:
        start = zodiac.index(asc_sign)
        # occupants per house
        occ = {}
        for name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]:
            p = basic.get(name, {})
            h = p.get("house")
            if h:
                occ.setdefault(h, []).append({"planet": name, "glyph": PLANET_GLYPH.get(name, "")})
        for i in range(12):
            hnum = i + 1
            sign = zodiac[(start + i) % 12]
            theme = HOUSE_THEME.get(hnum, ("", ""))
            houses.append({
                "house": hnum,
                "sign": sign,
                "sign_glyph": SIGN_GLYPH.get(sign, ""),
                "name": theme[0],
                "theme": theme[1],
                "occupants": occ.get(hnum, []),
            })

    return {
        "identity": _identity(chart),
        "dasha": dasha_period(chart),
        "planets": planets,
        "houses": houses,
        "yogas": notable_yogas(chart, limit=8),
        "divisional": {
            "navamsha": chart.get("Navamsha_D9", {}),
            "dasamsha": chart.get("Dasamsha_D10", {}),
        },
        "numerology": _numerology_brief(chart),
    }


def _numerology_brief(chart: dict) -> dict:
    n = chart.get("Numerology", {})
    moolank = n.get("moolank", {})
    bhagyank = n.get("bhagyank", {})
    return {
        "moolank": moolank.get("single"),
        "moolank_ruler": moolank.get("ruler", ""),
        "bhagyank": bhagyank.get("single"),
        "bhagyank_ruler": bhagyank.get("ruler", ""),
        "harmony": n.get("core_harmony", ""),
    }


# ── home overview (Home screen) ───────────────────────────────────────────────
def home_overview(chart: dict, display_name: str = "") -> dict:
    hour = datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"
    first = (display_name or "").strip().split(" ")[0] if display_name else ""

    ident = _identity(chart)
    daily = daily_insight(chart)
    dasha = dasha_period(chart)
    transits = transit_highlights(chart, limit=3)

    return {
        "greeting": greeting,
        "name": first,
        "date_label": _pretty_today(),
        "identity": ident,
        "today": {
            "headline": "Today",
            "plain": daily["plain"],
            "nakshatra": daily["nakshatra"],
            "tithi": daily["tithi"],
            "moon_sign_today": daily["moon_sign_today"],
            "moon_glyph": daily["moon_glyph"],
        },
        "right_now": {
            "headline": "Right now",
            "period": dasha["label"],
            "plain": dasha["plain"],
            "transits": transits,
        },
    }


def _supports_dash() -> bool:
    try:
        datetime.now().strftime("%-d")
        return True
    except ValueError:
        return False


def _pretty_today() -> str:
    """Cross-platform 'Monday, September 7' (no %-d, which fails on Windows)."""
    now = datetime.now()
    return f"{now.strftime('%A, %B')} {now.day}"


# ── domain forecast (Forecast screen) — layered L1..L4 ────────────────────────
def _layered_domain(sv: dict, domain_label: str) -> dict:
    status = str(sv.get("natal_promise_status", "")).upper()
    tone, l1_desc = _PROMISE_TONE.get(status, ("neutral", "An area worth understanding in your chart."))

    supporting = sv.get("supporting_factors", []) or []
    contradicting = sv.get("contradicting_factors", []) or []

    def _plainify(factors, kind):
        out = []
        for f in factors[:4]:
            out.append({
                "text": f.get("reason", ""),
                "strength": str(f.get("strength", "")).title(),
                "kind": kind,
            })
        return out

    windows = []
    for w in (sv.get("timing_windows", []) or [])[:4]:
        windows.append(_friendly_window(w))

    return {
        "status": status.title() if status else "",
        "tone": tone,
        "level1": {"headline": domain_label, "plain": l1_desc},
        "level2": {
            "supports": _plainify(supporting, "support"),
            "challenges": _plainify(contradicting, "challenge"),
        },
        "level3": {
            "supporting_factors": [
                {"reason": f.get("reason", ""), "rule": f.get("source_rule", ""), "strength": str(f.get("strength", "")).title()}
                for f in supporting[:8]
            ],
            "contradicting_factors": [
                {"reason": f.get("reason", ""), "rule": f.get("source_rule", ""), "strength": str(f.get("strength", "")).title()}
                for f in contradicting[:8]
            ],
        },
        "level4": {
            "final_judgment": sv.get("final_judgment", ""),
            "primary_significators": sv.get("primary_significators", []),
        },
        "windows": windows,
    }


def _friendly_window(w: dict) -> dict:
    """Normalise a timing window from either the semantic view or the forward scanner."""
    start = w.get("start_date") or w.get("macro_window_start") or ""
    end = w.get("end_date") or w.get("macro_window_end") or ""
    conf = str(w.get("confidence", "")).split(" ")[0].title()
    label = w.get("event_label", "")
    reason = w.get("reason") or w.get("micro_trigger_details", "")
    peak = w.get("peak_trigger_dates", "")
    return {
        "start": _friendly_date(start),
        "end": _friendly_date(end),
        "start_raw": start,
        "end_raw": end,
        "confidence": conf,
        "label": label,
        "peak": peak,
        "reason": reason,
    }


def _friendly_date(s: str) -> str:
    try:
        dt = datetime.strptime(str(s)[:10], "%Y-%m-%d")
        return f"{MONTHS[dt.month]} {dt.year}"
    except (ValueError, IndexError):
        return str(s)


def domain_forecast(get_semantic_view, chart: dict, domain: str) -> dict:
    label = dict((d[0], d[1]) for d in DOMAINS).get(domain, domain.title())
    try:
        sv = json.loads(get_semantic_view(chart, domain))
    except Exception:
        sv = {}
    return {"domain": domain, "label": label, **_layered_domain(sv, label)}


def forecast_overview(get_semantic_view, chart: dict) -> dict:
    """Compact status across the core life domains + the current period."""
    cards = []
    for key, label, sub in DOMAINS:
        try:
            sv = json.loads(get_semantic_view(chart, key))
            status = str(sv.get("natal_promise_status", "")).upper()
            tone, plain = _PROMISE_TONE.get(status, ("neutral", ""))
            nxt = (sv.get("timing_windows", []) or [])
            nxt_label = _friendly_window(nxt[0])["start"] if nxt else ""
        except Exception:
            status, tone, plain, nxt_label = "", "neutral", "", ""
        cards.append({
            "domain": key, "label": label, "sub": sub,
            "status": status.title() if status else "",
            "tone": tone, "plain": plain, "next_window": nxt_label,
        })
    return {"period": dasha_period(chart), "domains": cards}


# ── compatibility (Relationships screen) ──────────────────────────────────────
def compatibility_summary(compat: dict, person_label: str, relation: str = "partner") -> dict:
    raw = str(compat.get("total_score", "0/36"))
    try:
        got = float(raw.split("/")[0])
        total = float(raw.split("/")[1]) if "/" in raw else 36.0
    except (ValueError, IndexError):
        got, total = 0.0, 36.0
    pct = round((got / total) * 100) if total else 0

    if pct >= 83:
        band, plain = "Excellent", "A naturally harmonious match with strong foundations."
    elif pct >= 69:
        band, plain = "Strong", "A solid, workable match with real compatibility."
    elif pct >= 50:
        band, plain = "Moderate", "A mixed match — good in places, with areas to nurture."
    else:
        band, plain = "Tender", "A more challenging match that asks for conscious effort."

    breakdown = []
    for line in compat.get("breakdown", []) or []:
        title, _, desc = str(line).partition(":")
        tone = "challenged" if ("dosha" in title.lower() or "friction" in desc.lower() or "misunderstand" in desc.lower()) else "strong"
        breakdown.append({"koota": title.strip(), "note": desc.strip(), "tone": tone})

    return {
        "person": person_label,
        "relation": relation,
        "score": got,
        "total": total,
        "percent": pct,
        "band": band,
        "plain": plain,
        "is_compatible": bool(compat.get("is_compatible")),
        "breakdown": breakdown,
    }


# ── calendar / sky ────────────────────────────────────────────────────────────
def calendar_view(chart: dict) -> dict:
    pan = chart.get("Panchanga", {})
    full = pan.get("Drik_Panchang_Full", {}) or {}
    daily = daily_insight(chart)
    transits = transit_highlights(chart, limit=6)

    # Auspicious / inauspicious windows if the deep panchang provides them.
    auspicious = full.get("auspicious_periods", {}) or {}
    inauspicious = full.get("inauspicious_periods", {}) or {}

    def _windows(d):
        out = []
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, dict) and (v.get("start") or v.get("end")):
                    out.append({"name": str(k).replace("_", " ").title(),
                                "start": v.get("start", ""), "end": v.get("end", "")})
                elif isinstance(v, str):
                    out.append({"name": str(k).replace("_", " ").title(), "start": v, "end": ""})
        return out

    return {
        "today": daily,
        "transits": transits,
        "auspicious": _windows(auspicious),
        "inauspicious": _windows(inauspicious),
    }
