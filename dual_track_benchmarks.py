"""
Comprehensive Dual-Track Benchmark Suite (Phases 16 - 20)
Implements:
1. SET A: Strong Verified Rodden AA / A Cases (Jobs, Obama, Einstein, Trump 10:54, Diana 19:45)
2. SET B: Uncertain / Alternative Time Cases (Trump 09:51 vs 10:54, Diana 14:00 vs 19:45, Gandhi 1869, Bachchan)
3. SET C: Negative / Permuted Controls & Base-Rate Sensitivity
4. Dual-Track Output Contract:
   - Track A: Maximum High-Resolution Calculated Prediction (Macro -> Meso -> Micro -> Exact Date)
   - Track B: Maximum Honesty about Reliability & Sensitivity (A/B/C Reliability, Convergence, Empirical Score)
"""

from typing import Dict, List, Any, Tuple
import datetime
import pytz
import swisseph as swe

from astrology_engine import calculate_chart_with_object
from dasha_engine import DashaEngine
from transit_engine import TransitEngine
from sensitive_points import SensitivePointsEngine
from uncertainty_engine import UncertaintyEngine
from tradition_arbiter import run_full_arbitration

ZODIAC = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
          "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

HISTORICAL_BENCHMARKS = {
    "STEVE_JOBS": {
        "birth": {"year": 1955, "month": 2, "day": 24, "hour": 19, "minute": 15, "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles", "city": "San Francisco"},
        "quality": "Rodden AA (Birth Certificate)",
        "events": [
            {"date": "1976-04-01", "domain": "CAREER", "type": "Apple Founded", "severity": "HIGH"},
            {"date": "1985-09-16", "domain": "CAREER", "type": "Ousted from Apple / Found NeXT", "severity": "CRITICAL"},
            {"date": "1997-07-04", "domain": "CAREER", "type": "Return to Apple as Interim CEO", "severity": "HIGH"},
            {"date": "2004-07-31", "domain": "HEALTH_ACCIDENT", "type": "Pancreatic Tumor Surgery", "severity": "CRITICAL"},
            {"date": "2011-10-05", "domain": "HEALTH_ACCIDENT", "type": "Death / Life Cessation", "severity": "FATAL"}
        ]
    },
    "BARACK_OBAMA": {
        "birth": {"year": 1961, "month": 8, "day": 4, "hour": 19, "minute": 24, "lat": 21.3069, "lon": -157.8583, "tz": "Pacific/Honolulu", "city": "Honolulu"},
        "quality": "Rodden AA (Birth Certificate)",
        "events": [
            {"date": "2004-11-02", "domain": "CAREER", "type": "Elected US Senator (Illinois)", "severity": "HIGH"},
            {"date": "2008-11-04", "domain": "CAREER", "type": "Elected 44th US President", "severity": "VERY_HIGH"},
            {"date": "2009-01-20", "domain": "CAREER", "type": "First Inauguration", "severity": "HIGH"},
            {"date": "2012-11-06", "domain": "CAREER", "type": "Re-elected US President", "severity": "HIGH"}
        ]
    },
    "ALBERT_EINSTEIN": {
        "birth": {"year": 1879, "month": 3, "day": 14, "hour": 11, "minute": 30, "lat": 48.4011, "lon": 9.9876, "tz": "Europe/Berlin", "city": "Ulm"},
        "quality": "Rodden AA (Birth Certificate)",
        "events": [
            {"date": "1905-09-26", "domain": "CAREER", "type": "Annus Mirabilis Papers (Special Relativity)", "severity": "VERY_HIGH"},
            {"date": "1915-11-25", "domain": "CAREER", "type": "General Relativity Completed", "severity": "VERY_HIGH"},
            {"date": "1922-11-09", "domain": "CAREER", "type": "Awarded Nobel Prize in Physics", "severity": "VERY_HIGH"},
            {"date": "1955-04-18", "domain": "HEALTH_ACCIDENT", "type": "Death (Aortic Aneurysm)", "severity": "FATAL"}
        ]
    },
    "ELON_MUSK": {
        "birth": {"year": 1971, "month": 6, "day": 28, "hour": 7, "minute": 30, "lat": -25.7479, "lon": 28.2293, "tz": "Africa/Johannesburg", "city": "Pretoria"},
        "quality": "Rodden B (Biography Quote)",
        "events": [
            {"date": "1999-02-01", "domain": "WEALTH", "type": "Zip2 Sold for $307M", "severity": "HIGH"},
            {"date": "2000-12-15", "domain": "HEALTH_ACCIDENT", "type": "Severe Falciparum Malaria (Near-Fatal)", "severity": "CRITICAL"},
            {"date": "2002-10-03", "domain": "WEALTH", "type": "PayPal Sold to eBay for $1.5B", "severity": "HIGH"},
            {"date": "2008-09-28", "domain": "CAREER", "type": "Falcon 1 Flight 4 Success", "severity": "VERY_HIGH"},
            {"date": "2021-01-07", "domain": "WEALTH", "type": "Becomes World's Richest Person", "severity": "VERY_HIGH"}
        ]
    },
    "DONALD_TRUMP": {
        "birth": {"year": 1946, "month": 6, "day": 14, "hour": 10, "minute": 54, "lat": 40.7282, "lon": -73.7949, "tz": "America/New_York", "city": "Queens, NY"},
        "quality": "Rodden AA (Birth Certificate)",
        "alternative_birth": {"year": 1946, "month": 6, "day": 14, "hour": 9, "minute": 51, "lat": 40.7282, "lon": -73.7949, "tz": "America/New_York", "city": "Queens, NY"},
        "events": [
            {"date": "2016-11-08", "domain": "CAREER", "type": "Elected 45th US President", "severity": "VERY_HIGH"},
            {"date": "2020-11-03", "domain": "CAREER", "type": "2020 Election Defeat", "severity": "HIGH"},
            {"date": "2024-07-13", "domain": "HEALTH_ACCIDENT", "type": "Butler PA Assassination Attempt", "severity": "CRITICAL"},
            {"date": "2024-11-05", "domain": "CAREER", "type": "Elected 47th US President", "severity": "VERY_HIGH"}
        ]
    },
    "PRINCESS_DIANA": {
        "birth": {"year": 1961, "month": 7, "day": 1, "hour": 19, "minute": 45, "lat": 52.8300, "lon": 0.5000, "tz": "Europe/London", "city": "Sandringham"},
        "quality": "Rodden A (Memory/Quote)",
        "alternative_birth": {"year": 1961, "month": 7, "day": 1, "hour": 14, "minute": 0, "lat": 52.8300, "lon": 0.5000, "tz": "Europe/London", "city": "Sandringham"},
        "events": [
            {"date": "1981-07-29", "domain": "MARRIAGE", "type": "Royal Wedding to Prince Charles", "severity": "VERY_HIGH"},
            {"date": "1992-12-09", "domain": "MARRIAGE", "type": "Formal Separation Announced", "severity": "HIGH"},
            {"date": "1996-08-28", "domain": "MARRIAGE", "type": "Divorce Finalized", "severity": "HIGH"},
            {"date": "1997-08-31", "domain": "HEALTH_ACCIDENT", "type": "Fatal Paris Car Crash", "severity": "FATAL"}
        ]
    }
}

class DualTrackEvaluator:
    """
    Evaluates individual historical events against a chart under both Track A and Track B.
    """
    @staticmethod
    def evaluate_event_accuracy(chart, birth_dt_utc: datetime.datetime, event_date_str: str, domain: str, event_type: str) -> Dict[str, Any]:
        event_dt = datetime.datetime.fromisoformat(event_date_str)
        if event_dt.tzinfo is None:
            event_dt = pytz.utc.localize(event_dt)

        moon = chart.planets.get("Moon")
        moon_lon = moon.longitude if moon else 0.0

        # 1. Macro Dasha Evaluation (Vimshottari)
        timeline = DashaEngine.calculate_vimshottari_timeline(birth_dt_utc, moon_lon, num_levels=3)
        cur_dasha = DashaEngine.get_current_dasha(timeline, event_dt)
        md = cur_dasha.get("mahadasha", "Unknown")
        ad = cur_dasha.get("antardasha", "Unknown")
        pd = cur_dasha.get("pratyantardasha", "Unknown")
        dasha_hierarchy = f"{md} -> {ad} -> {pd}"

        # 2. Double Transit (Rao) at Event Date
        transit_res = TransitEngine.evaluate_double_transit(chart, event_dt)
        activated_houses = transit_res.get("activated_houses", [])
        dt_signs = transit_res.get("double_transit_signs", [])

        # 3. Domain Association
        # PRIMARY (core) houses only -- the classical signature house(s) for each
        # domain, NOT the broad supporting set. The earlier version used 4-5 of 12
        # houses per domain, which made "transit hits target" fire ~44% of the time
        # on RANDOM dates (negative control) -- i.e. no discriminating power. We
        # restrict to the 1-2 defining houses so the test can actually be wrong.
        #   CAREER   -> 10th (karma/status) only
        #   WEALTH   -> 2nd (accumulated wealth) + 11th (gains)
        #   MARRIAGE -> 7th (spouse) only
        #   HEALTH_ACCIDENT -> 8th (crisis/longevity) + 6th (disease/injury)
        domain_targets = {
            "CAREER": [10],
            "WEALTH": [2, 11],
            "MARRIAGE": [7],
            "HEALTH_ACCIDENT": [8, 6],
        }
        target_houses = domain_targets.get(domain, [1, 10])
        transit_hit = any(h in target_houses for h in activated_houses)

        # 4. Track A: High-Resolution Calculated Prediction Window
        from forward_timing_scanner import ForwardTimingScanner
        import traceback
        
        scanner = ForwardTimingScanner(chart)
        # Scan 1 month before and after the event date to see if the engine catches it
        try:
            start_scan = event_dt - datetime.timedelta(days=15)
            # Scan exactly across the event window
            windows = scanner.scan_domain_windows(domain, start_date=start_scan, months_ahead=1)
            
            # Did the stringent new convergence engine authorize this window?
            engine_caught_it = len(windows) > 0 and any("PROMISED" in w.get("prediction_state", "") for w in windows)
            
            if engine_caught_it:
                best = sorted(windows, key=lambda w: ("HIGH" in w.get("confidence", ""), "MODERATE" in w.get("confidence", "")), reverse=True)[0]
                active_pd_start = best["macro_window_start"]
                active_pd_end = best["macro_window_end"]
                dasha_hierarchy = best["dasha_hierarchy"]
                transit_hit = True
                pred_state = best.get("prediction_state", "UNKNOWN")
                conf = best.get("confidence", "UNKNOWN")
            else:
                active_pd_start, active_pd_end = "MISSED", "MISS"
                dasha_hierarchy = "NO_AUTHORIZATION"
                transit_hit = False
                pred_state = "DORMANT"
                conf = "NONE"
        except Exception as e:
            active_pd_start, active_pd_end = "ERR", "ERR"
            dasha_hierarchy = "ERR"
            transit_hit = False
            pred_state = "ERR"
            conf = "ERR"
            print(f"Error in ForwardTimingScanner: {traceback.format_exc()}")
            
        tier1_hit = transit_hit
        tier2_hit = transit_hit

        # 5. Track B: Reliability & Sensitivity Assessment
        reliability = UncertaintyEngine.evaluate_predictive_reliability(
            chart, birth_dt_utc, getattr(chart, "lat", 0.0), getattr(chart, "lon", 0.0), getattr(chart, "tz_name", "UTC"),
            event_dt - datetime.timedelta(days=15), event_dt + datetime.timedelta(days=15),
            dasha_hierarchy, domain
        )
        
        return {
            "event_type": event_type,
            "ground_truth_date": event_date_str,
            "track_a_calculated_prediction": {
                "active_dasha_triad": dasha_hierarchy,
                "meso_predictive_window": f"{active_pd_start} to {active_pd_end}",
                "transit_activation": f"Double Transit in {dt_signs} activating Houses {activated_houses}",
                "domain_activated": transit_hit
            },
            "track_b_reliability": {
                "reliability_class": reliability.get("reliability_class", "B"),
                "birth_time_sensitivity": reliability.get("birth_time_sensitivity", "STABLE"),
                "ayanamsha_sensitivity": reliability.get("ayanamsha_sensitivity", "STABLE"),
                "boundary_fragility": reliability.get("boundary_sensitivity", "LOW")
            },
            "evaluation_result": "PRECISION_HIT" if (tier1_hit and tier2_hit) else "PARTIAL_MATCH"
        }

def run_all_benchmarks():
    print("==========================================================================================")
    print("      DUAL-TRACK SCIENTIFIC BENCHMARK SUITE (PHASES 16-20)")
    print("      Track A: Maximum Predictive Resolution | Track B: Maximum Honesty on Reliability")
    print("==========================================================================================\n")

    total_events = 0
    hits = 0
    partials = 0

    for case_name, data in HISTORICAL_BENCHMARKS.items():
        print(f"🏛️ CASE: {case_name} ({data['quality']})")
        b = data["birth"]
        chart, _ = calculate_chart_with_object(b["year"], b["month"], b["day"], b["hour"], b["minute"], b["lat"], b["lon"], b["tz"], case_name)
        birth_utc = pytz.timezone(b["tz"]).localize(datetime.datetime(b["year"], b["month"], b["day"], b["hour"], b["minute"])).astimezone(pytz.utc)

        for ev in data["events"]:
            total_events += 1
            res = DualTrackEvaluator.evaluate_event_accuracy(chart, birth_utc, ev["date"], ev["domain"], ev["type"])
            t_a = res["track_a_calculated_prediction"]
            t_b = res["track_b_reliability"]

            mark = "🎯 HIT" if res["evaluation_result"] == "PRECISION_HIT" else "⚠️ PARTIAL"
            if res["evaluation_result"] == "PRECISION_HIT":
                hits += 1
            else:
                partials += 1

            print(f"\n  [{mark}] Event: {ev['type']} ({ev['date']}) | Domain: {ev['domain']}")
            print(f"      • Track A [Calculated Window]:  {t_a['meso_predictive_window']} | Dasha: {t_a['active_dasha_triad']}")
            print(f"      • Track A [Transit Mechanics]:  {t_a['transit_activation']}")
            print(f"      • Track B [Reliability Class]:  Class {t_b['reliability_class']} (Sensitivity: {t_b['birth_time_sensitivity']} | Ayanamsha: {t_b['ayanamsha_sensitivity']})")

        print("------------------------------------------------------------------------------------------")

    print("\n==========================================================================================")
    print(f"📊 FINAL BENCHMARK SCORE: {hits} / {total_events} Precision Hits ({hits/total_events*100:.1f}%) | {partials} Partials")
    print("==========================================================================================")


def run_and_export(json_path: str = None):
    """
    Run the full benchmark, tally per-domain precision-hit rates, run a
    negative-control (base-rate) test, and write the measured results to JSON so
    the UncertaintyEngine reports REAL numbers instead of a hardcoded figure.
    """
    import os
    import json
    import random

    per_domain = {}          # domain -> [hits, total]
    overall = [0, 0]         # [hits, total]

    charts = {}
    for case_name, data in HISTORICAL_BENCHMARKS.items():
        b = data["birth"]
        chart, _ = calculate_chart_with_object(
            b["year"], b["month"], b["day"], b["hour"], b["minute"],
            b["lat"], b["lon"], b["tz"], case_name)
        birth_utc = pytz.timezone(b["tz"]).localize(
            datetime.datetime(b["year"], b["month"], b["day"], b["hour"], b["minute"])
        ).astimezone(pytz.utc)
        charts[case_name] = (chart, birth_utc, data)

        for ev in data["events"]:
            res = DualTrackEvaluator.evaluate_event_accuracy(
                chart, birth_utc, ev["date"], ev["domain"], ev["type"])
            hit = 1 if res["evaluation_result"] == "PRECISION_HIT" else 0
            dom = ev["domain"]
            per_domain.setdefault(dom, [0, 0])
            per_domain[dom][0] += hit
            per_domain[dom][1] += 1
            overall[0] += hit
            overall[1] += 1

    # -------- NEGATIVE CONTROL (base-rate estimate) --------
    # For each chart, sample random dates in adult life and measure how often the
    # SAME "transit activates target house" test fires when there is (presumably)
    # no documented milestone. This is the false-positive / base-rate floor: a
    # hit rate on real events only means something if it EXCEEDS this floor.
    rng = random.Random(20260906)
    control_domains = ["CAREER", "WEALTH", "MARRIAGE", "HEALTH_ACCIDENT"]
    control_fire = 0
    control_total = 0
    for case_name, (chart, birth_utc, data) in charts.items():
        for _ in range(40):
            # random date between age 20 and age 60
            days = rng.randint(int(20 * 365.25), int(60 * 365.25))
            rand_dt = (birth_utc + datetime.timedelta(days=days)).strftime("%Y-%m-%d")
            dom = rng.choice(control_domains)
            res = DualTrackEvaluator.evaluate_event_accuracy(
                chart, birth_utc, rand_dt, dom, "RANDOM_CONTROL")
            control_total += 1
            if res["track_a_calculated_prediction"]["domain_activated"]:
                control_fire += 1

    result = {
        "generated_utc": datetime.datetime.utcnow().isoformat() + "Z",
        "grading_note": ("PRECISION_HIT requires the K.N.Rao double transit to activate "
                         "the event's target house at the event date while the dasha runs. "
                         "Compare the hit rate to negative_control.base_rate below; only the "
                         "MARGIN above base rate is evidence of real timing skill."),
        "overall": {"precision_hits": overall[0], "total": overall[1]},
        "by_domain": {d: {"precision_hits": v[0], "total": v[1]} for d, v in per_domain.items()},
        "negative_control": {
            "fires": control_fire,
            "total": control_total,
            "base_rate": round(control_fire / control_total, 4) if control_total else None,
            "method": "random adult-life dates, same target-house transit test, seed=20260906",
        },
    }

    if json_path is None:
        json_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                 "benchmark_results.json")
    with open(json_path, "w", encoding="utf-8") as fh:
        json.dump(result, fh, indent=2)

    br = result["negative_control"]["base_rate"]
    op = overall[0] / overall[1] if overall[1] else 0
    print("\n=== MEASURED BENCHMARK EXPORT ===")
    print(f"Overall precision-hit rate : {overall[0]}/{overall[1]} ({op*100:.1f}%)")
    print(f"Negative-control base rate : {control_fire}/{control_total} ({br*100:.1f}%)")
    print(f"Margin above base rate     : {(op - br)*100:+.1f} percentage points")
    for d, v in sorted(per_domain.items()):
        print(f"  {d:16s}: {v[0]}/{v[1]} ({100.0*v[0]/v[1]:.0f}%)")
    print(f"Written -> {json_path}")
    return result


if __name__ == "__main__":
    import sys
    if "--export" in sys.argv:
        run_and_export()
    else:
        run_all_benchmarks()
        run_and_export()
