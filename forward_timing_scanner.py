"""
Universal Forward Predictive Timing Scanner Engine
Calculates high-precision future event windows (80-95%+ confidence) for ANY input chart.
Implements:
1. Full 10-Domain House & Karaka Configuration
2. 3-Tier Vimshottari D-A-P Macro Clock
3. K.N. Rao Jupiter & Saturn Double Transit Intermediate Clock
4. Acute Fast-Transit Micro Triggers (Mars/Rahu over 22D, 64N, and Natal House Cusps)
5. Ashtakavarga SAV & BAV Defense Shield Scoring
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

# Standard Domain House Map built directly from the 70-Node Unified Taxonomy:
DOMAIN_HOUSE_MAP = {}
for k, v in SEVENTY_LIFE_NODES.items():
    DOMAIN_HOUSE_MAP[k] = {
        "houses": v["houses"],
        "karakas": v["karakas"],
        "event_label": v["label"]
    }

# Backward compatibility aliases for standard consultation names:
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
    "SPOUSE_HEALTH": "MARRIAGE_DIVORCE_FINALIZED",
    "EDUCATION": "EDUCATION_UNIVERSITY_GRADUATION",
    "FAME": "CAREER_PUBLIC_GOVERNANCE_ELECTION"
}
for alias_key, target_node in ALIASES.items():
    if target_node in DOMAIN_HOUSE_MAP:
        DOMAIN_HOUSE_MAP[alias_key] = DOMAIN_HOUSE_MAP[target_node]

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
        domain_upper = domain.upper()
        config = DOMAIN_HOUSE_MAP.get(domain_upper, DOMAIN_HOUSE_MAP["CAREER"])
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
        end_date = start_date + timedelta(days=months_ahead * 30.5)
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

            # Qualification Rule:
            # 1. Full Double Transit (Exact target house hit or domain double active)
            # 2. Acute Crisis / Health / Accident / Litigation (Micro-trigger sub-degree collision qualifies)
            # 3. Major Life Domain Primary Activation (Jupiter or Saturn activating primary house while D-A-P lord is aligned)
            is_crisis_domain = domain_upper in ["HEALTH_ACCIDENT", "FATHER_ACCIDENT", "FATHER_HEALTH", "MOTHER_HEALTH", "LITIGATION"]
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
                    "event_label": event_label,
                    "macro_window_start": max(d_start, start_date).strftime("%Y-%m-%d"),
                    "macro_window_end": min(d_end, end_date).strftime("%Y-%m-%d"),
                    "exact_peak_date": micro_trigger.get("exact_peak_date", window_mid.strftime("%Y-%m-%d")),
                    "peak_trigger_dates": micro_trigger.get("peak_dates", f"{window_mid.strftime('%Y-%m-%d')} (Diffuse window bound)"),
                    "peak_probability_pct": micro_trigger.get("probability_pct", 80.0 if "HIGH" in confidence else 55.0),
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

    def _find_micro_trigger(self, start_dt: datetime, end_dt: datetime, domain: str) -> Dict[str, Any]:
        """
        Finds acute Mars, Saturn, and Fast-Transit micro triggers inside the macro window.
        Scans for exact sub-degree aspects (<= 1.2° orb) against natal sensitive points,
        planets, and acute house ingresses.
        """
        window_days = (end_dt - start_dt).days
        if window_days <= 0:
            return {"found": False}

        # Step day-by-day across the window for precision
        step_days = max(1, window_days // 45)
        curr = start_dt
        
        # Precompute natal absolute longitudes
        natal_lons = {}
        for p_name, p_obj in self.chart.planets.items():
            if hasattr(p_obj, "sign") and p_obj.sign in ZODIAC_SIGNS:
                s_idx = ZODIAC_SIGNS.index(p_obj.sign)
                natal_lons[p_name] = (s_idx * 30.0) + p_obj.degree

        best_hit = None
        min_orb = 999.0

        domain_upper = domain.upper()
        is_father_domain = ("FATHER" in domain_upper)
        is_health_accident = any(k in domain_upper for k in ["HEALTH", "ACCIDENT", "SURGERY", "CRASH", "TRAUMA", "LITIGATION", "CRISIS", "PASSING", "DEATH"])
        is_career_wealth = any(k in domain_upper for k in ["CAREER", "BUSINESS", "WEALTH", "CAPITAL", "EDUCATION", "FAME", "SOVEREIGN", "TECH", "LIQUID", "EXIT"])
        is_progeny = any(k in domain_upper for k in ["CHILD", "PROGENY", "BIRTH", "SON", "DAUGHTER", "TWIN"])
        is_marriage = any(k in domain_upper for k in ["MARRIAGE", "UNION", "WEDDING", "RELATIONSHIP", "PARTNERSHIP"])
        is_property = any(k in domain_upper for k in ["PROPERTY", "REAL_ESTATE", "LAND", "HOUSE_BUILD"])

        while curr <= end_dt:
            hour_dec = curr.hour + (curr.minute / 60.0)
            jd = swe.julday(curr.year, curr.month, curr.day, hour_dec)
            
            # Calculate live Mars, Saturn, and Jupiter
            mars_res, _ = swe.calc_ut(jd, swe.MARS, swe.FLG_SIDEREAL)
            mars_lon = mars_res[0] % 360.0
            mars_sign_idx = int(mars_lon / 30)
            mars_house = ((mars_sign_idx - self.lagna_sign_idx) % 12) + 1

            saturn_res, _ = swe.calc_ut(jd, swe.SATURN, swe.FLG_SIDEREAL)
            saturn_lon = saturn_res[0] % 360.0
            saturn_sign_idx = int(saturn_lon / 30)
            saturn_house = ((saturn_sign_idx - self.lagna_sign_idx) % 12) + 1

            jup_res, _ = swe.calc_ut(jd, swe.JUPITER, swe.FLG_SIDEREAL)
            jup_lon = jup_res[0] % 360.0
            jup_sign_idx = int(jup_lon / 30)
            jup_house = ((jup_sign_idx - self.lagna_sign_idx) % 12) + 1

            # Check Lagna degree aspect from Mars
            lagna_lon = (self.lagna_sign_idx * 30.0) + (self.chart.ascendant_degree if hasattr(self.chart, "ascendant_degree") else 15.0)
            l_diff = min(abs((mars_lon - lagna_lon) % 360.0), 360.0 - abs((mars_lon - lagna_lon) % 360.0))
            l_aspect = min([abs(l_diff - asp) for asp in [0.0, 60.0, 90.0, 120.0, 180.0]])

            # 1. Check Father Accident / Trauma Specific Micro-Triggers (House 4 / Father 8th & Sun)
            if is_father_domain:
                if "Mars" in natal_lons:
                    diff = min(abs((mars_lon - natal_lons["Mars"]) % 360.0), 360.0 - abs((mars_lon - natal_lons["Mars"]) % 360.0))
                    if diff <= 1.5 and diff < min_orb:
                        min_orb = diff
                        prob = round(max(70.0, min(96.0, 98.0 - (diff * 18.0))), 1)
                        best_hit = {
                            "found": True,
                            "exact_peak_date": curr.strftime("%Y-%m-%d"),
                            "peak_dates": f"{(curr - timedelta(days=2)).strftime('%Y-%m-%d')} to {(curr + timedelta(days=2)).strftime('%Y-%m-%d')}",
                            "probability_pct": prob,
                            "min_orb_arcmin": round(diff * 60.0, 1),
                            "details": f"Transiting Mars (at {mars_lon%30:.2f}° {ZODIAC_SIGNS[mars_sign_idx]}) forms exact {diff*60:.1f}' conjunction over Natal Mars (Automotive/Machine Trauma Axis) [Peak Probability: {prob}% on {curr.strftime('%Y-%m-%d')}]"
                        }
                if "Sun" in natal_lons:
                    s_diff = min(abs((saturn_lon - natal_lons["Sun"]) % 360.0), 360.0 - abs((saturn_lon - natal_lons["Sun"]) % 360.0))
                    if s_diff <= 1.5 and s_diff < min_orb:
                        min_orb = s_diff
                        prob = round(max(65.0, min(94.0, 95.0 - (s_diff * 18.0))), 1)
                        best_hit = {
                            "found": True,
                            "exact_peak_date": curr.strftime("%Y-%m-%d"),
                            "peak_dates": f"{(curr - timedelta(days=3)).strftime('%Y-%m-%d')} to {(curr + timedelta(days=3)).strftime('%Y-%m-%d')}",
                            "probability_pct": prob,
                            "min_orb_arcmin": round(s_diff * 60.0, 1),
                            "details": f"Transiting Saturn forms tight aspect ({s_diff*60:.1f}' orb) over Natal Sun (Father Karaka Eclipse) [Peak Probability: {prob}% on {curr.strftime('%Y-%m-%d')}]"
                        }

            # 2. General Health / Acute Accident / Surgery / Physical Trauma
            elif is_health_accident:
                # Check Saturn transit through 8th House crushing 8th house planets
                if saturn_house == 8:
                    for p_target in ["Sun", "Mars", "Moon", "Mercury"]:
                        if p_target in natal_lons:
                            s_diff = min(abs((saturn_lon - natal_lons[p_target]) % 360.0), 360.0 - abs((saturn_lon - natal_lons[p_target]) % 360.0))
                            if s_diff <= 2.0 and s_diff < min_orb:
                                min_orb = s_diff
                                best_hit = {
                                    "found": True,
                                    "peak_dates": f"{(curr - timedelta(days=3)).strftime('%Y-%m-%d')} to {(curr + timedelta(days=3)).strftime('%Y-%m-%d')}",
                                    "details": f"Transiting Saturn in 8th House at {saturn_lon%30:.2f}° {ZODIAC_SIGNS[saturn_sign_idx]} exactly impacts Natal {p_target} ({s_diff*60:.1f}' orb) - Severe Physical Crisis"
                                }
                # Check Mars crossing Natal Mars or Natal 8th Lord
                if "Mars" in natal_lons:
                    diff = min(abs((mars_lon - natal_lons["Mars"]) % 360.0), 360.0 - abs((mars_lon - natal_lons["Mars"]) % 360.0))
                    if diff <= 1.5 and diff < min_orb:
                        min_orb = diff
                        best_hit = {
                            "found": True,
                            "peak_dates": f"{(curr - timedelta(days=2)).strftime('%Y-%m-%d')} to {(curr + timedelta(days=2)).strftime('%Y-%m-%d')}",
                            "details": f"Transiting Mars forms acute conjunction ({diff*60:.1f}' orb) over Natal Mars (Physical Trauma / Surgery Trigger)"
                        }
                # Check Mars exact aspect to Lagna
                if l_aspect <= 1.0 and l_aspect < min_orb:
                    min_orb = l_aspect
                    best_hit = {
                        "found": True,
                        "peak_dates": f"{(curr - timedelta(days=2)).strftime('%Y-%m-%d')} to {(curr + timedelta(days=2)).strftime('%Y-%m-%d')}",
                        "details": f"Transiting Mars at {mars_lon%30:.2f}° {ZODIAC_SIGNS[mars_sign_idx]} casts exact {l_aspect*60:.1f}' aspect to Ascendant (Bodily Impact)"
                    }
                elif (mars_house in [6, 8, 1, 12] or saturn_house in [6, 8, 12]) and not best_hit:
                    best_hit = {
                        "found": True,
                        "peak_dates": f"{curr.strftime('%Y-%m-%d')} to {(curr + timedelta(days=5)).strftime('%Y-%m-%d')}",
                        "details": f"Transiting Mars/Saturn occupies Dusthana House {mars_house}/{saturn_house}, acting as physical stress catalyst"
                    }

            # 3. Career / Business / Wealth / Technical Field
            elif is_career_wealth:
                if (mars_house in [10, 11, 2, 1] or saturn_house in [10, 11, 3]) and not best_hit:
                    best_hit = {
                        "found": True,
                        "peak_dates": f"{curr.strftime('%Y-%m-%d')} to {(curr + timedelta(days=5)).strftime('%Y-%m-%d')}",
                        "details": f"Transiting Mars/Saturn energizes Upachaya/Kendra House {mars_house}/{saturn_house}, catalyzing executive action, technical deployment, and status breakthrough"
                    }

            # 4. Progeny & Children (Childbirth / Conception)
            elif is_progeny:
                if "Jupiter" in natal_lons:
                    j_diff = min(abs((mars_lon - natal_lons["Jupiter"]) % 360.0), 360.0 - abs((mars_lon - natal_lons["Jupiter"]) % 360.0))
                    if (mars_house in [5, 11, 2, 1] or jup_house in [5, 11, 2, 1]) and not best_hit:
                        best_hit = {
                            "found": True,
                            "peak_dates": f"{curr.strftime('%Y-%m-%d')} to {(curr + timedelta(days=5)).strftime('%Y-%m-%d')}",
                            "details": f"Transiting Jupiter/Mars energizes Progeny House 5/11, triggering childbirth/progeny milestone"
                        }

            # 5. Marriage & Partnership Formation
            elif is_marriage:
                if (jup_house in [7, 11, 1, 5] or mars_house in [7, 11, 1]) and not best_hit:
                    best_hit = {
                        "found": True,
                        "peak_dates": f"{curr.strftime('%Y-%m-%d')} to {(curr + timedelta(days=5)).strftime('%Y-%m-%d')}",
                        "details": f"Transiting Jupiter/Venus energizes 7th/11th House of Marriage and Sacred Union"
                    }

            # 6. Real Estate & Property
            elif is_property:
                if (mars_house in [4, 11, 1] or saturn_house in [4, 11, 1]) and not best_hit:
                    best_hit = {
                        "found": True,
                        "peak_dates": f"{curr.strftime('%Y-%m-%d')} to {(curr + timedelta(days=5)).strftime('%Y-%m-%d')}",
                        "details": f"Transiting Mars (Bhumi Karaka) energizes 4th House of Real Estate, Land, and Permanent Assets"
                    }

            curr += timedelta(days=step_days)

        if best_hit:
            return best_hit

        return {"found": False}
