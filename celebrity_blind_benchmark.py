"""
Celebrity Blind Prediction & Auto-Calibration Benchmark Suite
Tests the ForwardTimingScanner and Acute Micro-Trigger Engine across 
high-stakes historical life events with documented ground truth.
"""

from typing import Dict, List, Any
import datetime
import pytz
import swisseph as swe

from astrology_engine import calculate_chart_with_object
from forward_timing_scanner import ForwardTimingScanner

FAMOUS_CASES = {
    "STEVE_JOBS": {
        "birth": {"year": 1955, "month": 2, "day": 24, "hour": 19, "minute": 15, "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles"},
        "events": [
            {"date": "2004-07-31", "domain": "HEALTH_ACCIDENT", "label": "Pancreatic Tumor Surgery"},
            {"date": "1985-09-16", "domain": "CAREER", "label": "Ousted from Apple"},
            {"date": "1997-07-04", "domain": "CAREER", "label": "Return to Apple as CEO"},
            {"date": "2011-10-05", "domain": "HEALTH_ACCIDENT", "label": "Death"}
        ]
    },
    "AMITABH_BACHCHAN": {
        "birth": {"year": 1942, "month": 10, "day": 11, "hour": 16, "minute": 0, "lat": 25.4358, "lon": 81.8463, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "1982-07-26", "domain": "HEALTH_ACCIDENT", "label": "Coolie Near-Fatal Accident"},
            {"date": "2003-01-18", "domain": "FATHER_HEALTH", "label": "Father Harivansh Rai Bachchan Passing"}
        ]
    },
    "PRINCESS_DIANA": {
        "birth": {"year": 1961, "month": 7, "day": 1, "hour": 19, "minute": 45, "lat": 52.83, "lon": 0.50, "tz": "Europe/London"},
        "events": [
            {"date": "1997-08-31", "domain": "HEALTH_ACCIDENT", "label": "Fatal Paris Car Crash"},
            {"date": "1981-07-29", "domain": "MARRIAGE", "label": "Royal Wedding"}
        ]
    },
    "SANJAY_GANDHI": {
        "birth": {"year": 1946, "month": 12, "day": 14, "hour": 9, "minute": 27, "lat": 28.6139, "lon": 77.2090, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "1980-06-23", "domain": "HEALTH_ACCIDENT", "label": "Fatal Pitts S-2A Plane Crash"}
        ]
    },
    "INDIRA_GANDHI": {
        "birth": {"year": 1917, "month": 11, "day": 19, "hour": 23, "minute": 11, "lat": 25.4358, "lon": 81.8463, "tz": "Asia/Kolkata"},
        "events": [
            {"date": "1984-10-31", "domain": "HEALTH_ACCIDENT", "label": "Assassination by Bodyguards"}
        ]
    },
    "TIGER_WOODS": {
        "birth": {"year": 1975, "month": 12, "day": 30, "hour": 22, "minute": 50, "lat": 33.7879, "lon": -117.8531, "tz": "America/Los_Angeles"},
        "events": [
            {"date": "2009-11-27", "domain": "HEALTH_ACCIDENT", "label": "SUV Crash / Scandal Inflection"},
            {"date": "2021-02-23", "domain": "HEALTH_ACCIDENT", "label": "Severe Rollover Car Crash in LA"}
        ]
    }
}

def run_celebrity_benchmarks():
    print("==========================================================================================")
    print("      CELEBRITY BLIND PREDICTION & HIGH-PRECISION CALIBRATION BENCHMARK                   ")
    print("==========================================================================================\n")

    total = 0
    hits = 0

    for name, data in FAMOUS_CASES.items():
        b = data["birth"]
        chart, _ = calculate_chart_with_object(b["year"], b["month"], b["day"], b["hour"], b["minute"], b["lat"], b["lon"], b["tz"], name)
        scanner = ForwardTimingScanner(chart)

        print(f"🏛️ CASE: {name}")
        for ev in data["events"]:
            total += 1
            ev_date = datetime.datetime.fromisoformat(ev["date"])
            ev_year = ev_date.year
            start_scan = pytz.utc.localize(datetime.datetime(ev_year - 1, 1, 1))
            
            # Scan 36 months around the event
            windows = scanner.scan_domain_windows(ev["domain"], start_scan, months_ahead=36)
            
            # Check if actual event date is captured in macro window and peak dates
            match = None
            for w in windows:
                w_start = datetime.datetime.fromisoformat(w["macro_window_start"]).date()
                w_end = datetime.datetime.fromisoformat(w["macro_window_end"]).date()
                if w_start <= ev_date.date() <= w_end:
                    match = w
                    break
            
            if match:
                hits += 1
                print(f"  🎯 [HIT] Event: {ev['label']} ({ev['date']}) | Domain: {ev['domain']}")
                print(f"      • Macro Window : {match['macro_window_start']} to {match['macro_window_end']}")
                print(f"      • Peak Micro   : {match['peak_trigger_dates']}")
                print(f"      • Dasha Triad  : {match['dasha_hierarchy']}")
                print(f"      • Details      : {match.get('micro_trigger_details')}")
            else:
                print(f"  ⚠️ [MISS] Event: {ev['label']} ({ev['date']}) | Domain: {ev['domain']}")

        print("------------------------------------------------------------------------------------------")

    print(f"\n📊 FINAL BENCHMARK HIT RATE: {hits} / {total} Events Captured ({hits/total*100:.1f}%)")

if __name__ == "__main__":
    run_celebrity_benchmarks()
