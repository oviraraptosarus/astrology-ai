"""
Uncertainty & Reliability Calibration Engine (Track B)
Calculates Birth-Time Sensitivity, Ayanamsha Sensitivity, and Model Reliability 
for any high-resolution predictive window.
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import pytz
import swisseph as swe
from config import Config

from astrology_engine import calculate_chart_with_object
from dasha_engine import DashaEngine
from varga_engine import VargaEngine

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

class UncertaintyEngine:
    @staticmethod
    def evaluate_predictive_reliability(
        base_chart, 
        base_birth_time_utc: datetime, 
        lat: float, lon: float, tz_name: str,
        predicted_start_utc: datetime,
        predicted_end_utc: datetime,
        dasha_hierarchy: str,
        domain: str
    ) -> Dict[str, Any]:
        """
        Evaluates the robustness of a specific prediction window against input perturbations.
        """
        results = {
            "birth_time_sensitivity": "STABLE",
            "dasha_origin_shift_days": 0.0,
            "dasha_triad_stable_under_5min": True,
            "ayanamsha_sensitivity": "STABLE",
            "boundary_sensitivity": "LOW",
            # Empirical performance is NOT hardcoded. It is looked up from the
            # actual measured blind-benchmark results for this domain if the
            # results file exists; otherwise it is reported as UNMEASURED.
            "empirical_benchmark_performance": UncertaintyEngine._lookup_benchmark(domain),
            "reliability_class": "A"
        }

        if base_birth_time_utc.tzinfo is None:
            base_birth_time_utc = pytz.utc.localize(base_birth_time_utc)

        # 1. Birth Time Sensitivity (±5 minutes shift)
        # Shift birth time backwards by 5 minutes
        dt_minus_5 = base_birth_time_utc - timedelta(minutes=5)
        # We need the moon's exact longitude 5 minutes ago to see dasha shift
        jd_minus_5 = swe.julday(dt_minus_5.year, dt_minus_5.month, dt_minus_5.day, dt_minus_5.hour + dt_minus_5.minute/60.0)
        swe.set_sid_mode(Config.ayanamsha_swe_id())
        moon_res_minus, _ = swe.calc_ut(jd_minus_5, swe.MOON, swe.FLG_SIDEREAL | swe.FLG_SPEED)
        moon_lon_minus = moon_res_minus[0]

        timeline_minus = DashaEngine.calculate_vimshottari_timeline(dt_minus_5, moon_lon_minus, num_levels=3)
        
        # Check if the generated dasha hierarchy exists at the predicted_start_utc in the shifted setup
        cur_minus = DashaEngine.get_current_dasha(timeline_minus, predicted_start_utc)
        shifted_hierarchy_minus = f"{cur_minus.get('mahadasha')} -> {cur_minus.get('antardasha')} -> {cur_minus.get('pratyantardasha')}"
        
        # A +-5 min birth-time change rigidly translates the whole Vimshottari
        # sequence by a fixed "origin shift". The origin shift scales with how
        # fast the Moon is moving at birth: shift = (moon_delta_deg / 13.3333) *
        # 120 years. Near perigee the Moon can move ~0.05 deg in 5 min (=> ~160
        # days of origin shift); near apogee ~0.002 deg (=> ~7 days).
        #
        # BUT the raw origin-shift magnitude is NOT the right reliability signal:
        # what matters is whether the actual Dasha triad ACTIVE AT THE EVENT DATE
        # flips under that shift. We already recomputed the shifted triad above
        # (shifted_hierarchy_minus); use it directly instead of a crude day count.
        moon_delta = abs(moon_lon_minus - base_chart.planets["Moon"].longitude)
        origin_shift_days = (moon_delta / 13.333333333333334) * 120 * 365.25
        results["dasha_origin_shift_days"] = round(origin_shift_days, 1)

        base_triad = dasha_hierarchy.replace(" ", "")
        shifted_triad = shifted_hierarchy_minus.replace(" ", "")
        triad_stable = (base_triad == shifted_triad)
        results["dasha_triad_stable_under_5min"] = triad_stable

        if not triad_stable:
            # The active period changed under a plausible birth-time error: the
            # micro-timing genuinely cannot be trusted at this resolution.
            results["birth_time_sensitivity"] = "HIGHLY_SENSITIVE_TO_INPUT_PRECISION"
            results["reliability_class"] = "C"
        elif origin_shift_days > (predicted_end_utc - predicted_start_utc).days / 2:
            # Triad holds but the sequence translates by more than half the
            # quoted window: the day-level edge of the window is soft.
            results["birth_time_sensitivity"] = "BORDERLINE"
            if results["reliability_class"] == "A":
                results["reliability_class"] = "B"
        else:
            results["birth_time_sensitivity"] = "STABLE"

        # 2. Cusp Boundary Sensitivity (Does the planet swap houses if Equal House is used?)
        # Base chart has 'house' from Porphyry. We check Equal House.
        boundary_flags = []
        asc_idx = ZODIAC_SIGNS.index(base_chart.ascendant_sign)
        for pname, p in base_chart.planets.items():
            equal_house = ((ZODIAC_SIGNS.index(p.sign) - asc_idx) % 12) + 1
            if hasattr(p, "chalit_house") and p.chalit_house != equal_house:
                boundary_flags.append(pname)
                
        if len(boundary_flags) >= 2:
            results["boundary_sensitivity"] = "HIGH"
            results["reliability_class"] = max(results["reliability_class"], "B")
        elif len(boundary_flags) == 1:
            results["boundary_sensitivity"] = "MODERATE"

        # 3. Discrete Mathematical Boundary Fragility Audit (Sign, Nakshatra, Pada, KP Sub-Lord, Gandanta)
        try:
            from boundary_fragility_engine import BoundaryFragilityEngine
            fragility_report = BoundaryFragilityEngine.evaluate_chart_fragility(base_chart)
            results["chart_boundary_fragility"] = fragility_report["chart_boundary_fragility_rating"]
            results["fragile_planets_count"] = fragility_report["fragile_entities_count"]
            if fragility_report["gandanta_entities"]:
                results["gandanta_afflictions"] = [g["entity"] + ": " + g["details"] for g in fragility_report["gandanta_entities"]]
            if fragility_report["chart_boundary_fragility_rating"] == "HIGHLY_SENSITIVE":
                results["reliability_class"] = "C"
            elif fragility_report["chart_boundary_fragility_rating"] == "BORDERLINE":
                results["reliability_class"] = max(results["reliability_class"], "B")
        except Exception as e:
            results["boundary_fragility_error"] = str(e)

        # 4. Ayanamsha Sensitivity (Any planet shifting signs within 1.1 degrees?)
        # Raman vs Lahiri difference is approx 1.1 - 1.2 degrees.
        ayanamsha_shifts = []
        for pname, p in base_chart.planets.items():
            if p.degree < 1.2 or p.degree > 28.8:
                ayanamsha_shifts.append(pname)
                
        if ayanamsha_shifts:
            results["ayanamsha_sensitivity"] = f"BORDERLINE ({', '.join(ayanamsha_shifts)} on Sandhi edges)"
            results["reliability_class"] = max(results["reliability_class"], "B")

        # Compile final reliability wrapper
        return results

    # Cache for the measured benchmark table (loaded once per process).
    _BENCHMARK_CACHE = None

    @staticmethod
    def _lookup_benchmark(domain: str) -> str:
        """
        Return the ACTUAL measured benchmark performance for this domain, read
        from benchmark_results.json. Never fabricates a number; if no measurement
        exists, says so. Reports BOTH layers explicitly:
        - Window containment (vs its 82.5% random-date base rate — near-uninformative)
        - Acute exact-day sub-degree peaks (only layer with demonstrated selectivity)
        """
        import os
        import json
        if UncertaintyEngine._BENCHMARK_CACHE is None:
            path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "benchmark_results.json")
            try:
                with open(path, "r", encoding="utf-8") as fh:
                    UncertaintyEngine._BENCHMARK_CACHE = json.load(fh)
            except Exception:
                UncertaintyEngine._BENCHMARK_CACHE = {}
        table = UncertaintyEngine._BENCHMARK_CACHE or {}

        parts = []

        # Layer 1: precision (double-transit + dasha at event date)
        by_domain = table.get("by_domain", {})
        d = by_domain.get((domain or "").upper())
        overall = table.get("overall", {})
        nc = table.get("negative_control", {})
        base = nc.get("base_rate")
        if d and d.get("total"):
            parts.append(f"{d['precision_hits']}/{d['total']} "
                         f"({100.0*d['precision_hits']/d['total']:.0f}%) precision hits on documented '{domain}' events")
        elif overall and overall.get("total"):
            parts.append(f"{overall['precision_hits']}/{overall['total']} "
                         f"({100.0*overall['precision_hits']/overall['total']:.0f}%) precision hits across all domains "
                         f"(domain '{domain}' not separately measured)")
        if base is not None:
            parts.append(f"negative-control base rate {base*100:.0f}% (only the margin above this is skill)")

        # Layer 2: window containment (explicitly labelled near-uninformative)
        wc = table.get("window_containment", {})
        wnc = wc.get("negative_control", {})
        if wnc.get("base_rate") is not None:
            parts.append(f"macro-window containment base rate {wnc['base_rate']*100:.0f}% on random dates — containment alone is NOT predictive")

        # Layer 3: acute exact-day evidence
        acute = table.get("acute_exact_layer", {})
        if acute:
            n_cases = len(acute.get("verified_cases", []))
            parts.append(f"acute exact-day sub-degree peak: {n_cases} verified case(s) total (no established rate)")

        sig = table.get("significance_tests", {})
        if sig.get("verdict"):
            parts.append(f"significance testing verdict: {sig['verdict']} for macro timing")

        if not parts:
            return "UNMEASURED (no blind-benchmark data for this domain)"
        return "; ".join(parts) + ". model_score is an UNCALIBRATED strength score, not a probability."

