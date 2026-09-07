"""
Universal Forward Predictive Timing Scanner Engine
==================================================
Generates candidate event windows for ANY input chart by combining:
1. Node-specification house & karaka configuration (70-Node Ontology + aliases)
2. 3-Tier Vimshottari D-A-P Macro Clock
3. K.N. Rao Jupiter & Saturn Double Transit Intermediate Clock
4. Acute Fast-Transit Micro Triggers (continuous-time minimum-separation solve)
5. Ashtakavarga SAV & BAV Defense Shield Scoring

HONESTY CONTRACT (read before using output):
- `model_score` is an UNCALIBRATED internal strength score (orb tightness x
  convergence). It is NOT an empirical probability of any event, and must
  never be presented as one.
- `exact_peak_date` is the continuous-time minimum-separation date for the
  detected transit collision, computed by golden-section minimization. It is
  an astronomical fact about the transit, NOT a prediction that the event
  occurs on that day.
- Unknown/unsupported node names raise NodeDispatchError. There is NO silent
  fallback to Career.
- `empirical_benchmark_performance` is looked up from measured results or
  reported as UNMEASURED. It is never hardcoded.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import pytz
import swisseph as swe
from config import Config

from vedic_models import Chart, Planet
from dasha_engine import DashaEngine
from ashtakavarga_engine import AshtakavargaEngine
from sensitive_points import SensitivePointsEngine

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

from seventy_node_ontology import SEVENTY_LIFE_NODES, SeventyNodeOntology


class NodeDispatchError(ValueError):
    """Raised when an unknown/unsupported node name is requested.
    The scanner must NEVER silently substitute another domain."""


# Standard Domain House Map built directly from the 70-Node Unified Taxonomy:
DOMAIN_HOUSE_MAP = {}
for k, v in SEVENTY_LIFE_NODES.items():
    DOMAIN_HOUSE_MAP[k] = {
        "houses": v["houses"],
        "karakas": v["karakas"],
        "event_label": v["label"]
    }

# Legacy consultation-name aliases. These map old broad domain names onto
# 70-node specifications so existing callers keep working. An alias resolves
# to a real node; anything NOT in this table raises NodeDispatchError.
ALIASES = {
    "CAREER": "CAREER_BREAKTHROUGH",
    "BUSINESS": "CAREER_FOUNDING_ENTERPRISE",
    "WEALTH": "WEALTH_LIQUID_WINDFALL",
    "PROPERTY": "PROPERTY_LAND_ACQUISITION",
    "MARRIAGE": "MARRIAGE_SACRED_UNION",
    "CHILDREN": "PROGENY_FIRST_CHILDBIRTH",
    "HEALTH_ACCIDENT": "HEALTH_ACUTE_SURGICAL_INTERVENTION",
    "LITIGATION": "CAREER_EMPLOYMENT_DISPUTE",
    "RELOCATION": "RELOCATION_PERMANENT_EMIGRATION",
    "SPIRITUALITY": "SPIRITUAL_MANTRA_SIDDHI_INITIATION",
    "FATHER_ACCIDENT": "FATHER_ACUTE_ACCIDENT_TRAUMA",
    "FATHER_HEALTH": "FATHER_NATURAL_LIFESPAN_PASSING",
    "MOTHER_HEALTH": "MOTHER_HEALTH_CRISIS",
    "EDUCATION": "EDUCATION_UNIVERSITY_GRADUATION",
    "FAME": "CAREER_PUBLIC_GOVERNANCE_ELECTION",
    # event_protocols.py ids (domain_engine -> activation_engine path)
    "CAREER_PROMOTION": "CAREER_BREAKTHROUGH",
    "JOB_CHANGE": "CAREER_OUSTER_OR_RESIGNATION",
    "UNEMPLOYMENT": "CAREER_OUSTER_OR_RESIGNATION",
    "MARRIAGE": "MARRIAGE_SACRED_UNION",
    "MARRIAGE_TIMING": "MARRIAGE_SACRED_UNION",
    "MARRIAGE_DELAY": "MARRIAGE_SACRED_UNION",
    "WEALTH_GAIN": "WEALTH_LIQUID_WINDFALL",
    "WEALTH_GENERAL": "WEALTH_STEADY_SAVINGS",
    "FINANCIAL_LOSS": "WEALTH_DEBT_OR_CRISIS",
    "BUSINESS_START": "CAREER_FOUNDING_ENTERPRISE",
    "BUSINESS_TIMING": "CAREER_FOUNDING_ENTERPRISE",
    "EDUCATION_SUCCESS": "EDUCATION_COMPETITIVE_EXAM_TOP_RANK",
    "EDUCATION_GENERAL": "EDUCATION_UNIVERSITY_GRADUATION",
    "RELOCATION_ABROAD": "RELOCATION_PERMANENT_EMIGRATION",
    # methodology_router.identify_domain() output names (event_analysis path)
    "GENERAL": "CAREER_BREAKTHROUGH",  # general outlook: houses 1/9/10/11 overlap
    "GENERAL_TIMING": "CAREER_BREAKTHROUGH",
    "BUSINESS": "CAREER_FOUNDING_ENTERPRISE",
    "CAREER": "CAREER_BREAKTHROUGH",
    "HEALTH": "HEALTH_CHRONIC_PATHOLOGY_DISCOVERY",
    "CHILDREN": "PROGENY_FIRST_CHILDBIRTH",
    "SPIRITUALITY": "SPIRITUAL_MANTRA_SIDDHI_INITIATION",
}
for alias_key, target_node in ALIASES.items():
    if target_node in DOMAIN_HOUSE_MAP:
        DOMAIN_HOUSE_MAP[alias_key] = DOMAIN_HOUSE_MAP[target_node]

# Domain families used for uniform crisis/qualification dispatch (typed, not ad-hoc).
_CRISIS_FAMILIES = {"HEALTH", "ACCIDENT", "SURGERY", "CRASH", "TRAUMA", "LITIGATION",
                    "CRISIS", "PASSING", "DEATH", "ATTACK", "TRANSPLANT", "PATHOLOGY",
                    "ICU", "CARDIAC", "SEVERANCE"}
_CAREER_WEALTH_FAMILIES = {"CAREER", "BUSINESS", "WEALTH", "CAPITAL", "EDUCATION", "FAME",
                           "SOVEREIGN", "TECH", "LIQUID", "EXIT", "GOVERNANCE", "NOBEL"}
_PROGENY_FAMILIES = {"CHILD", "PROGENY", "BIRTH", "SON", "DAUGHTER", "TWIN"}
_MARRIAGE_FAMILIES = {"MARRIAGE", "UNION", "WEDDING", "RELATIONSHIP", "PARTNERSHIP",
                      "ROMANCE", "SPOUSE"}
_PROPERTY_FAMILIES = {"PROPERTY", "REAL_ESTATE", "LAND", "HOUSE_BUILD"}
_PARENT_FAMILIES = {"FATHER", "MOTHER", "PARENTAL"}


def resolve_node(domain: str) -> str:
    """Resolve any accepted node/alias name to its canonical 70-node key.
    Raises NodeDispatchError for unknown names (fail-closed)."""
    upper = (domain or "").strip().upper()
    if not upper:
        raise NodeDispatchError("Empty node name")
    if upper in SEVENTY_LIFE_NODES:
        return upper
    if upper in ALIASES and ALIASES[upper] in SEVENTY_LIFE_NODES:
        return ALIASES[upper]
    raise NodeDispatchError(
        f"Unknown node '{domain}'. Valid nodes: 70-node keys (see seventy_node_ontology.py) "
        f"or legacy aliases {sorted(ALIASES.keys())}"
    )


def add_months(dt: datetime, months: int) -> datetime:
    """Calendar-correct month addition (clamped to end-of-month), preserving tzinfo."""
    month_index = dt.month - 1 + months
    year = dt.year + month_index // 12
    month = month_index % 12 + 1
    import calendar as _calendar
    day = min(dt.day, _calendar.monthrange(year, month)[1])
    return dt.replace(year=year, month=month, day=day)


def _is_crisis_node(node_key: str) -> bool:
    tokens = set(node_key.split("_"))
    return bool(tokens & _CRISIS_FAMILIES) or bool(tokens & _PARENT_FAMILIES)


def _score_from_convergence(confidence: str) -> float:
    """Fallback internal strength score when no micro-trigger was found.
    Coarse convergence-tier mapping — explicitly NOT a probability."""
    if "CRITICAL_HIGH" in confidence:
        return 90.0
    if "HIGH" in confidence:
        return 75.0
    if "MODERATE" in confidence:
        return 55.0
    return 35.0


def _score_from_orb(orb_deg: float, hi: float = 96.0, lo: float = 70.0) -> float:
    """Internal strength score from orbital tightness.
    Linear in orb over [0, 1.5deg]; explicitly NOT an empirical probability."""
    orb = max(0.0, min(1.5, orb_deg))
    return round(lo + (hi - lo) * (1.0 - orb / 1.5), 1)

class ForwardTimingScanner:
    def __init__(self, chart: Chart):
        self.chart = chart
        self.sensitive_engine = SensitivePointsEngine(chart)
        self.sensitive_points = self.sensitive_engine.calculate_all()

        if hasattr(chart, "ascendant_sign") and chart.ascendant_sign in ZODIAC_SIGNS:
            self.lagna_sign_idx = ZODIAC_SIGNS.index(chart.ascendant_sign)
        elif hasattr(chart, "ascendant") and hasattr(chart.ascendant, "longitude"):
            self.lagna_sign_idx = int(chart.ascendant.longitude / 30)
        else:
            self.lagna_sign_idx = 0

        AshtakavargaEngine.calculate_ashtakavarga(chart)
        self.sav_table = getattr(chart, "sarvashtakavarga", {})

    def scan_domain_windows(self, domain: str, start_date: datetime, months_ahead: int = 24) -> List[Dict[str, Any]]:
        # Fail-closed node dispatch: unknown nodes raise instead of falling back to CAREER.
        canonical_node = resolve_node(domain)
        domain_upper = canonical_node  # canonical 70-node key from here on
        config = DOMAIN_HOUSE_MAP[canonical_node]
        target_houses = config["houses"]
        target_karakas = config["karakas"]
        event_label = config["event_label"]

        target_lords = []
        for h in target_houses:
            sign_idx = (self.lagna_sign_idx + h - 1) % 12
            lord = SIGN_LORDS[ZODIAC_SIGNS[sign_idx]]
            target_lords.append(lord)

        target_occupants = [
            p_name for p_name, p_obj in self.chart.planets.items()
            if hasattr(p_obj, "house") and p_obj.house in target_houses
        ]

        target_significators = set(target_lords + target_karakas + target_occupants)

        # Generate Dasha timeline
        birth_utc = getattr(self.chart, "birth_time", datetime(2000, 1, 1, tzinfo=pytz.utc))
        if not isinstance(birth_utc, datetime):
            birth_utc = datetime(2000, 1, 1, tzinfo=pytz.utc)
        if birth_utc.tzinfo is None:
            birth_utc = pytz.utc.localize(birth_utc)

        moon = self.chart.planets.get("Moon")
        moon_lon = moon.longitude if moon else 0.0
        dasha_timeline = DashaEngine.calculate_vimshottari_timeline(birth_utc, moon_lon, num_levels=3)

        if start_date.tzinfo is None:
            start_date = pytz.utc.localize(start_date)
        # Calendar-correct month arithmetic (30.5-day months drift across boundaries).
        end_date = add_months(start_date, months_ahead)
        qualifying_windows = []

        def _to_utc(s: str) -> datetime:
            dt = datetime.fromisoformat(s)
            return pytz.utc.localize(dt) if dt.tzinfo is None else dt.astimezone(pytz.utc)

        flat_entries = []
        for md_node in dasha_timeline:
            md_name = md_node["lord"]
            md_start = _to_utc(md_node["start"])
            md_end = _to_utc(md_node["end"])

            sub_ads = md_node.get("sub_periods", [])
            if not sub_ads:
                flat_entries.append({"md": md_name, "ad": md_name, "pd": md_name, "start": md_start, "end": md_end})
            else:
                for ad_node in sub_ads:
                    ad_name = ad_node["lord"]
                    ad_start = _to_utc(ad_node["start"])
                    ad_end = _to_utc(ad_node["end"])

                    sub_pds = ad_node.get("sub_periods", [])
                    if not sub_pds:
                        flat_entries.append({"md": md_name, "ad": ad_name, "pd": md_name, "start": ad_start, "end": ad_end})
                    else:
                        for pd_node in sub_pds:
                            pd_name = pd_node["lord"]
                            pd_start = _to_utc(pd_node["start"])
                            pd_end = _to_utc(pd_node["end"])
                            flat_entries.append({"md": md_name, "ad": ad_name, "pd": pd_name, "start": pd_start, "end": pd_end})

        for entry in flat_entries:
            d_start = entry["start"]
            d_end = entry["end"]

            if d_end < start_date or d_start > end_date:
                continue

            md = entry["md"]
            ad = entry["ad"]
            pd = entry["pd"]

            dasha_activated = False
            reasons = []

            # Record Dasha Authorizations
            if md in target_significators:
                dasha_activated = True
                reasons.append(f"Mahadasha lord {md} signifies domain")
            if ad in target_significators:
                dasha_activated = True
                reasons.append(f"Antardasha lord {ad} activates event house")
            if pd in target_significators:
                dasha_activated = True
                reasons.append(f"Pratyantardasha lord {pd} triggers manifestation")

            # Must have at least SOME dasha authorization
            if not dasha_activated:
                continue

            window_mid = d_start + (d_end - d_start) / 2

            # Sample transits across the window (start, mid, and end) to catch planetary sign ingresses
            sample_dates = [d_start, window_mid, max(d_start, d_end - timedelta(days=2))]
            best_dt_result = None
            for s_date in sample_dates:
                res = self._check_transits_at_date(s_date, target_houses, target_lords)
                if not best_dt_result:
                    best_dt_result = res
                elif res["double_transit_active"] and not best_dt_result["double_transit_active"]:
                    best_dt_result = res
                elif len(res["activated_houses"]) > len(best_dt_result["activated_houses"]) and not best_dt_result["double_transit_active"]:
                    best_dt_result = res

            dt_result = best_dt_result or self._check_transits_at_date(window_mid, target_houses, target_lords)

            # Check for acute sub-degree Micro-Triggers (Mars/Saturn/Rahu exact degree collisions)
            micro_trigger = self._find_micro_trigger(d_start, d_end, domain_upper)

            # Qualification Rule (uniform across ALL 70 nodes):
            # 1. Full Double Transit (exact target-house hit or domain double active), OR
            # 2. Crisis-family node with an acute sub-degree micro-trigger, OR
            # 3. Major Life Domain Primary Activation (any target house activated while a
            #    D-A-P lord is aligned with the node's significators.
            is_crisis_domain = _is_crisis_node(domain_upper)
            single_primary_hit = (len(dt_result["activated_houses"]) > 0 and (md in target_significators or ad in target_significators or pd in target_significators))

            qualifies = dt_result["double_transit_active"] or (is_crisis_domain and micro_trigger.get("found")) or single_primary_hit

            if qualifies:
                # Modulators
                sav_support = dt_result["kakshya_favorable"]

                # Hierarchical Confidence Assessment (Convergence)
                if micro_trigger.get("found") and dt_result["double_transit_active"]:
                    confidence = "CRITICAL_HIGH (FULL_CONVERGENCE)"
                    state = "PROMISED_AND_TRIGGERED"
                elif dt_result["double_transit_active"] and sav_support:
                    confidence = "HIGH (FULL_CONVERGENCE)"
                    state = "PROMISED_AND_TRIGGERED"
                elif micro_trigger.get("found"):
                    confidence = "HIGH (ACUTE_MICRO_COLLISION)"
                    state = "ACUTE_EVENT_TRIGGERED"
                elif sav_support:
                    confidence = "MODERATE (PARTIAL_CONVERGENCE_NO_MICROTRIGGER)"
                    state = "PROMISED_BUT_DIFFUSE"
                else:
                    confidence = "LOW (WEAK_SUPPORT)"
                    state = "ACTIVATED_BUT_OBSTRUCTED"

                dasha_hierarchy_str = f"{md} -> {ad} -> {pd}"

                # Calculate Uncertainty/Reliability via UncertaintyEngine
                reliability = {}
                try:
                    from uncertainty_engine import UncertaintyEngine
                    reliability = UncertaintyEngine.evaluate_predictive_reliability(
                        self.chart, birth_utc, getattr(self.chart, "lat", 0.0), getattr(self.chart, "lon", 0.0), getattr(self.chart, "tz_name", "UTC"),
                        d_start, d_end, dasha_hierarchy_str, domain_upper
                    )
                except Exception as e:
                    reliability = {"error": str(e)}

                qualifying_windows.append({
                    "event_type": domain_upper,
                    "node_id": SEVENTY_LIFE_NODES[domain_upper]["node_id"],
                    "event_label": event_label,
                    "macro_window_start": max(d_start, start_date).strftime("%Y-%m-%d"),
                    "macro_window_end": min(d_end, end_date).strftime("%Y-%m-%d"),
                    # Continuous-time minimum-separation date (astronomical fact, not an event claim)
                    "exact_peak_date": micro_trigger.get("exact_peak_date"),
                    "peak_trigger_dates": micro_trigger.get("peak_dates", f"{window_mid.strftime('%Y-%m-%d')} (Diffuse window bound)"),
                    # UNCALIBRATED internal strength score (orb tightness x convergence).
                    # NOT an empirical event probability — see HONESTY CONTRACT in module docstring.
                    "model_score": micro_trigger.get("model_score", _score_from_convergence(confidence)),
                    "model_score_semantics": "UNCALIBRATED_STRENGTH_SCORE_NOT_PROBABILITY",
                    "min_orb_arcmin": micro_trigger.get("min_orb_arcmin"),
                    "prediction_state": state,
                    "confidence": confidence,
                    "dasha_hierarchy": dasha_hierarchy_str,
                    "dasha_evidence": reasons,
                    "transit_evidence": dt_result["reasons"],
                    "activated_houses": dt_result["activated_houses"],
                    "micro_trigger_details": micro_trigger.get("details", "No acute catalyst found; general energetic window"),
                    "reliability_metrics": reliability
                })

        # Sort by confidence level
        def confidence_rank(w):
            conf = w["confidence"]
            if "HIGH" in conf: return 3
            if "MODERATE" in conf: return 2
            return 1

        qualifying_windows.sort(key=confidence_rank, reverse=True)
        return qualifying_windows

    def _check_transits_at_date(self, dt: datetime, target_houses: List[int], target_lords: List[str]) -> Dict[str, Any]:
        if dt.tzinfo is None:
            dt = pytz.utc.localize(dt)
        hour_dec = dt.hour + (dt.minute / 60.0) + (dt.second / 3600.0)
        jd = swe.julday(dt.year, dt.month, dt.day, hour_dec)
        swe.set_sid_mode(Config.ayanamsha_swe_id())

        jup_res, _ = swe.calc_ut(jd, swe.JUPITER, swe.FLG_SIDEREAL)
        sat_res, _ = swe.calc_ut(jd, swe.SATURN, swe.FLG_SIDEREAL)

        jup_lon = jup_res[0] % 360.0
        sat_lon = sat_res[0] % 360.0

        jup_sign_idx = int(jup_lon / 30)
        sat_sign_idx = int(sat_lon / 30)

        jup_house = ((jup_sign_idx - self.lagna_sign_idx) % 12) + 1
        sat_house = ((sat_sign_idx - self.lagna_sign_idx) % 12) + 1

        jup_aspected_houses = [((jup_house - 1 + offset - 1) % 12) + 1 for offset in [1, 5, 7, 9]]
        sat_aspected_houses = [((sat_house - 1 + offset - 1) % 12) + 1 for offset in [1, 3, 7, 10]]

        # Classical K.N. Rao Double Transit Evaluation
        # 1. Exact Single-House Convergence (both aspecting the exact same target house)
        exact_common = list(set(jup_aspected_houses).intersection(set(sat_aspected_houses)))
        exact_target = [h for h in exact_common if h in target_houses]

        # 2. Domain-Level Activation (Jupiter touching one domain house/lord AND Saturn touching one domain house/lord)
        jup_domain_hits = [h for h in jup_aspected_houses if h in target_houses]
        sat_domain_hits = [h for h in sat_aspected_houses if h in target_houses]
        domain_double_active = (len(jup_domain_hits) > 0 and len(sat_domain_hits) > 0)

        jup_sav = self.sav_table.get(ZODIAC_SIGNS[jup_sign_idx], 28)
        reasons = []

        double_transit_active = (len(exact_target) > 0) or domain_double_active
        activated_target_houses = list(set(exact_target + jup_domain_hits + sat_domain_hits))

        if len(exact_target) > 0:
            reasons.append(f"Exact K.N. Rao Double Transit: Jupiter (H{jup_house}) & Saturn (H{sat_house}) jointly aspect House(s) {exact_target}")
        elif domain_double_active:
            reasons.append(f"Domain Double Transit: Jupiter activates H{jup_domain_hits} while Saturn activates H{sat_domain_hits}")

        if jup_sav >= 28:
            reasons.append(f"Transit occurs in strong Ashtakavarga sign {ZODIAC_SIGNS[jup_sign_idx]} ({jup_sav} bindus)")

        return {
            "double_transit_active": double_transit_active,
            "activated_houses": activated_target_houses,
            "kakshya_favorable": jup_sav >= 28,
            "reasons": reasons
        }

    def _planet_lon(self, planet_swe_id: int, dt: datetime) -> float:
        """Sidereal absolute longitude of a planet at a given UTC datetime (continuous time)."""
        hour_dec = dt.hour + (dt.minute / 60.0) + (dt.second / 3600.0) + (dt.microsecond / 3.6e9)
        jd = swe.julday(dt.year, dt.month, dt.day, hour_dec)
        swe.set_sid_mode(Config.ayanamsha_swe_id())
        res, _ = swe.calc_ut(jd, planet_swe_id, swe.FLG_SIDEREAL)
        return res[0] % 360.0

    def _build_track(self, planet_swe_id: int, start_dt: datetime, end_dt: datetime) -> List[datetime]:
        """Coarse shared longitude grid for a planet over the window.
        Step is kept <= 3 days so that even a fast Mars minimum basin (~4-6 days
        wide) cannot fall entirely between samples."""
        total_days = max(1, (end_dt - start_dt).days)
        step_days = 3 if total_days > 540 else (2 if total_days > 180 else 1)
        step = timedelta(days=step_days)
        grid = []
        cur = start_dt
        while cur <= end_dt:
            grid.append(cur)
            cur += step
        if not grid:
            grid.append(start_dt)
        return grid

    def _min_separation_on_grid(self, planet_swe_id: int, target_lon: float,
                                grid: List[datetime], orb_limit: float) -> Optional[Dict[str, Any]]:
        """
        Continuous-time minimum angular separation between a transiting planet and a
        natal longitude. Phase 1: coarse scan over the shared grid (cached longitudes).
        Phase 2: golden-section refinement ONLY when the coarse minimum is promising
        (within orb_limit + coarse-step slack). Returns None when the collision cannot
        be within orb.
        """
        # Phase 1: coarse scan with cached longitudes
        cache = getattr(self, "_track_cache", None)
        best_val, best_dt = 999.0, grid[0]
        for dt in grid:
            lon = cache[(planet_swe_id, dt)] if cache and (planet_swe_id, dt) in cache else self._planet_lon(planet_swe_id, dt)
            d = abs((lon - target_lon) % 360.0)
            d = min(d, 360.0 - d)
            if d < best_val:
                best_val, best_dt = d, dt
        # Coarse-step error slack: refine only if the true minimum could be within orb
        grid_step_days = (grid[1] - grid[0]).days if len(grid) > 1 else 1
        if best_val > orb_limit + 0.3 * grid_step_days:
            return None

        # Phase 2: golden-section refinement around the best coarse sample
        def sep(dt: datetime) -> float:
            lon = self._planet_lon(planet_swe_id, dt)
            d = abs((lon - target_lon) % 360.0)
            return min(d, 360.0 - d)

        gr = (5 ** 0.5 - 1) / 2
        lo, hi = grid[0], grid[-1]
        bracket = timedelta(days=grid_step_days + 2)
        a = max(lo, best_dt - bracket)
        b = min(hi, best_dt + bracket)
        for _ in range(36):
            c = b - gr * (b - a)
            d = a + gr * (b - a)
            if sep(c) < sep(d):
                b = d
            else:
                a = c
        t_min = a + (b - a) / 2
        return {"min_sep_deg": sep(t_min), "peak_utc": t_min}

    def _find_micro_trigger(self, start_dt: datetime, end_dt: datetime, domain: str) -> Dict[str, Any]:
        """
        Acute micro-triggers inside the macro window: exact sub-degree collisions of
        transiting Mars/Saturn (and Rahu where relevant) against natal sensitive
        longitudes. Peak instants are solved by continuous-time golden-section
        minimization (NOT day sampling), so `exact_peak_date` is the true
        minimum-separation date.

        NOTE: `model_score` returned here is an UNCALIBRATED strength score derived
        from orbital tightness. It is NOT an empirical event probability.
        """
        window_days = (end_dt - start_dt).days
        if window_days <= 0:
            return {"found": False}

        # Precompute natal absolute longitudes
        natal_lons = {}
        for p_name, p_obj in self.chart.planets.items():
            if hasattr(p_obj, "sign") and p_obj.sign in ZODIAC_SIGNS:
                s_idx = ZODIAC_SIGNS.index(p_obj.sign)
                natal_lons[p_name] = (s_idx * 30.0) + p_obj.degree

        best_hit = None
        min_orb = 999.0

        domain_upper = (domain or "").upper()
        tokens = set(domain_upper.split("_"))
        is_father_domain = bool(tokens & _PARENT_FAMILIES) and bool(tokens & _CRISIS_FAMILIES.union({"HONOR"}))
        is_health_accident = bool(tokens & _CRISIS_FAMILIES)
        is_career_wealth = bool(tokens & _CAREER_WEALTH_FAMILIES)
        is_progeny = bool(tokens & _PROGENY_FAMILIES)
        is_marriage = bool(tokens & _MARRIAGE_FAMILIES)
        is_property = bool(tokens & _PROPERTY_FAMILIES)

        lagna_lon = (self.lagna_sign_idx * 30.0) + (getattr(self.chart, "ascendant_degree", 15.0)
                                                     if hasattr(self.chart, "ascendant_degree") else 15.0)

        # Shared coarse tracks per planet (computed once, reused across all targets)
        self._track_cache = {}
        planet_tracks = {}
        for pid in (swe.MARS, swe.SATURN, swe.JUPITER, swe.VENUS):
            grid = self._build_track(pid, start_dt, end_dt)
            planet_tracks[pid] = grid
            for dt in grid:
                self._track_cache[(pid, dt)] = self._planet_lon(pid, dt)

        def _record(planet_id: int, planet_name: str, target_lon: float, target_label: str,
                    theme: str, orb_limit: float = 1.5, half_width_days: int = 2):
            """Solve continuous-time minimum separation and record if within orb limit."""
            nonlocal best_hit, min_orb
            res = self._min_separation_on_grid(planet_id, target_lon, planet_tracks[planet_id], orb_limit)
            if res is None:
                return
            orb = res["min_sep_deg"]
            if orb <= orb_limit and orb < min_orb:
                min_orb = orb
                peak = res["peak_utc"]
                score = _score_from_orb(orb)
                best_hit = {
                    "found": True,
                    "exact_peak_date": peak.strftime("%Y-%m-%d"),
                    "exact_peak_utc": peak.strftime("%Y-%m-%d %H:%M UTC"),
                    "peak_dates": f"{(peak - timedelta(days=half_width_days)).strftime('%Y-%m-%d')} to {(peak + timedelta(days=half_width_days)).strftime('%Y-%m-%d')}",
                    "model_score": score,
                    "min_orb_arcmin": round(orb * 60.0, 2),
                    "details": (f"Transiting {planet_name} reaches exact minimum separation "
                                f"({orb*60:.1f}' arcmin) over {target_label} on {peak.strftime('%Y-%m-%d')}: "
                                f"{theme} [model_score={score} — UNCALIBRATED, not an event probability]")
                }

        # 1. Parent / Father-accident micro-triggers (Mars over natal Mars; Saturn over natal Sun)
        if is_father_domain:
            if "Mars" in natal_lons:
                _record(swe.MARS, "Mars", natal_lons["Mars"], "Natal Mars (Automotive/Machine Trauma Axis)",
                        "acute collision on the paternal trauma axis")
            if "Sun" in natal_lons:
                _record(swe.SATURN, "Saturn", natal_lons["Sun"], "Natal Sun (Father Karaka Eclipse)",
                        "paternal vitality eclipse", orb_limit=1.5, half_width_days=3)

        # 2. Health / accident / surgery / trauma family
        elif is_health_accident:
            # Saturn in 8th crushing natal planets (evaluated at window mid for house placement)
            mid = start_dt + (end_dt - start_dt) / 2
            sat_lon_mid = self._planet_lon(swe.SATURN, mid)
            sat_house_mid = ((int(sat_lon_mid / 30) - self.lagna_sign_idx) % 12) + 1
            if sat_house_mid == 8:
                for p_target in ["Sun", "Mars", "Moon", "Mercury"]:
                    if p_target in natal_lons:
                        _record(swe.SATURN, "Saturn", natal_lons[p_target], f"Natal {p_target} (8th-house severe crisis axis)",
                                "severe physical crisis", orb_limit=2.0, half_width_days=3)
            if "Mars" in natal_lons:
                _record(swe.MARS, "Mars", natal_lons["Mars"], "Natal Mars (Physical Trauma / Surgery Trigger)",
                        "acute bodily trauma trigger")
            # Mars exact aspect to Lagna degree (conjunction/trine/square/opposition)
            for asp in (0.0, 60.0, 90.0, 120.0, 180.0):
                _record(swe.MARS, "Mars", (lagna_lon + asp) % 360.0, f"Ascendant degree (aspect {asp:.0f}° axis)",
                        "bodily impact on the Ascendant", orb_limit=1.0)

        # 3. Career / business / wealth / education / fame family
        elif is_career_wealth:
            if "Mars" in natal_lons:
                _record(swe.MARS, "Mars", natal_lons["Mars"], "Natal Mars (executive drive / technical deployment)",
                        "executive action catalyst")
            if "Jupiter" in natal_lons:
                _record(swe.JUPITER, "Jupiter", natal_lons["Jupiter"], "Natal Jupiter (status elevation axis)",
                        "status breakthrough catalyst")

        # 4. Progeny family
        elif is_progeny:
            if "Jupiter" in natal_lons:
                _record(swe.JUPITER, "Jupiter", natal_lons["Jupiter"], "Natal Jupiter (Progeny/5th-lord grace)",
                        "progeny milestone catalyst")
            if "Mars" in natal_lons:
                _record(swe.MARS, "Mars", natal_lons["Mars"], "Natal Mars (energy for conception window)",
                        "progeny energy catalyst")

        # 5. Marriage / partnership family
        elif is_marriage:
            if "Venus" in natal_lons:
                _record(swe.VENUS, "Venus", natal_lons["Venus"], "Natal Venus (7th-house union karaka)",
                        "union formation catalyst")
            if "Jupiter" in natal_lons:
                _record(swe.JUPITER, "Jupiter", natal_lons["Jupiter"], "Natal Jupiter (11th-house social gain)",
                        "partnership blessing catalyst")

        # 6. Property family
        elif is_property:
            if "Mars" in natal_lons:
                _record(swe.MARS, "Mars", natal_lons["Mars"], "Natal Mars (Bhumi Karaka / land axis)",
                        "real-estate acquisition catalyst")
            if "Saturn" in natal_lons:
                _record(swe.SATURN, "Saturn", natal_lons["Saturn"], "Natal Saturn (permanent structure axis)",
                        "construction/permanence catalyst")

        if best_hit:
            return best_hit

        return {"found": False}
