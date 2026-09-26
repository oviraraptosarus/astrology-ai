"""
Dual-Track Comprehensive Mortality & Lifespan Audit
Computes:
1. Track 1: Natural Lifespan Mathematical Ceiling (Pindayu & Amshayu from BPHS 43-45)
2. Track 2: Acute Premature Trauma & Crisis Windows (Apamrityu / Sub-Degree Collisions <= 1.2° orb across all ages)
3. Track 3: Final Convergence Terminal Window (Dasha Maraka x Transit Collision)
"""

import datetime, pytz
from astrology_engine import calculate_chart_with_object
from forward_timing_scanner import ForwardTimingScanner
from pindayu_engine import ParashariAyurdayaEngine

FAMILY_CHARTS = {
    "YOU (2008-08-01)": {
        "birth": {"year": 2008, "month": 8, "day": 1, "hour": 18, "minute": 25, "lat": 16.8186, "lon": 82.0641, "tz": "Asia/Kolkata"},
        "relation": "User (Self)",
        "scan_start_year": 2026,
        "scan_years": 85
    },
    "HER (2008-04-05)": {
        "birth": {"year": 2008, "month": 4, "day": 5, "hour": 6, "minute": 15, "lat": 50.348, "lon": 18.916, "tz": "Europe/Warsaw"},
        "relation": "Partner (Poland)",
        "scan_start_year": 2026,
        "scan_years": 85
    },
    "FATHER (1975-05-06)": {
        "birth": {"year": 1975, "month": 5, "day": 6, "hour": 7, "minute": 15, "lat": 16.8667, "lon": 81.9333, "tz": "Asia/Kolkata"},
        "relation": "Father",
        "scan_start_year": 2026,
        "scan_years": 50
    },
    "MOTHER (1980-10-01)": {
        "birth": {"year": 1980, "month": 10, "day": 1, "hour": 20, "minute": 25, "lat": 16.8667, "lon": 81.9333, "tz": "Asia/Kolkata"},
        "relation": "Mother",
        "scan_start_year": 2026,
        "scan_years": 50
    },
    "BROTHER (2003-06-05)": {
        "birth": {"year": 2003, "month": 6, "day": 5, "hour": 17, "minute": 45, "lat": 17.6868, "lon": 83.2185, "tz": "Asia/Kolkata"},
        "relation": "Brother (Dubai)",
        "scan_start_year": 2026,
        "scan_years": 75
    }
}

def run_mortality_audit():
    print("=" * 100)
    print("      DUAL-TRACK COMPREHENSIVE MORTALITY & LIFESPAN AUDIT                                 ")
    print("==========================================================================================\n")

    for name, data in FAMILY_CHARTS.items():
        b = data["birth"]
        chart, _ = calculate_chart_with_object(b["year"], b["month"], b["day"], b["hour"], b["minute"], b["lat"], b["lon"], b["tz"], name=name)
        
        # 1. Parashari Mathematical Ceiling
        ayur = ParashariAyurdayaEngine.evaluate_tri_ayurdaya(chart)
        pind = ayur["pindayu_result"]["total_longevity_years"]
        amsh = ayur["amshayu_result"]["total_longevity_years"]

        # 2. Forward Timing Scan for Acute Physical Trauma & Natural Cessation
        scanner = ForwardTimingScanner(chart)
        start_dt = pytz.utc.localize(datetime.datetime(data["scan_start_year"], 1, 1))
        
        trauma_windows = scanner.scan_domain_windows("HEALTH_ACUTE_SURGICAL_INTERVENTION", start_dt, months_ahead=data["scan_years"]*12)
        cessation_windows = scanner.scan_domain_windows("HEALTH_NATURAL_LIFESPAN_CESSATION", start_dt, months_ahead=data["scan_years"]*12)

        # Filter for acute micro-trigger collisions
        acute_trauma = [w for w in trauma_windows if w.get("exact_peak_date") and ("Mars" in w.get("micro_trigger_details", "") or "Saturn" in w.get("micro_trigger_details", "") or "Rahu" in w.get("micro_trigger_details", ""))]
        acute_cessation = [w for w in cessation_windows if w.get("exact_peak_date")]

        print(f"🏛️ {name} [{data['relation']}]")
        print(f"   • Ascendant (Lagna)    : {chart.ascendant_sign} at {chart.ascendant_degree:.2f}°")
        print(f"   • Parashari Amshayu    : {amsh} Years ({int(amsh)}y {int((amsh%1)*12)}m)")
        print(f"   • Parashari Pindayu    : {pind} Years ({int(pind)}y {int((pind%1)*12)}m)")
        print(f"   • Primary Life Span Cap: Age {int(amsh)} to {min(105, int(pind))}")
        
        print("\n   ⚠️ [EARLY APAMRITYU / ACUTE TRAUMA FRICTION WINDOWS (Before Age 65)]:")
        early_acute = [w for w in acute_trauma if int(w["macro_window_start"][:4]) - b["year"] < 65][:3]
        if not early_acute:
            print("      None — No fatal sub-degree collision spikes found in early/middle life.")
        for w in early_acute:
            age_at_event = int(w["macro_window_start"][:4]) - b["year"]
            print(f"      • Macro: {w['macro_window_start']} to {w['macro_window_end']} (Age ~{age_at_event})")
            print(f"        Exact Peak Day : {w['exact_peak_date']} (± Window: {w['peak_trigger_dates']})")
            print(f"        Dasha Triad    : {w['dasha_hierarchy']}")
            print(f"        Mechanism      : {w['micro_trigger_details']}")

        print("\n   ☠️ [PRIMARY TERMINAL / NATURAL LIFESPAN EXIT WINDOWS]:")
        terminal_candidates = [w for w in acute_cessation + acute_trauma if int(w["macro_window_start"][:4]) - b["year"] >= min(60, int(amsh)-5)]
        terminal_candidates.sort(key=lambda w: (w.get("model_score", 0)), reverse=True)
        for w in terminal_candidates[:3]:
            age_at_event = int(w["macro_window_start"][:4]) - b["year"]
            print(f"      • Macro Window   : {w['macro_window_start']} to {w['macro_window_end']} (Age ~{age_at_event})")
            print(f"        ★ EXACT PEAK   : {w['exact_peak_date']} (± Window: {w['peak_trigger_dates']})")
            print(f"        Model Score    : {w['model_score']} [Orb: {w.get('min_orb_arcmin')} arcmin]")
            print(f"        Dasha Triad    : {w['dasha_hierarchy']}")
            print(f"        Micro Catalyst : {w['micro_trigger_details']}")
        print("-" * 100 + "\n")

if __name__ == "__main__":
    run_mortality_audit()
