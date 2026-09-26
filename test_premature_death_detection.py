"""
Apamrityu / Premature Death Blind Historical Verification
Tests the upgraded forward timing scanner on premature fatal events:
1. Princess Diana: Fatal Car Crash (1997-08-31) [Age 36]
2. Steve Jobs: Pancreatic Neuroendocrine Tumor Passing (2011-10-05) [Age 56]
3. Sanjay Gandhi: Aerobatic Plane Crash (1980-06-23) [Age 33]
4. Indira Gandhi: Assassination (1984-10-31) [Age 66]
"""

import datetime, pytz
from astrology_engine import calculate_chart_with_object
from forward_timing_scanner import ForwardTimingScanner

PREMATURE_DEATH_CASES = [
    {
        "name": "PRINCESS_DIANA",
        "birth": {"year": 1961, "month": 7, "day": 1, "hour": 19, "minute": 45, "lat": 52.83, "lon": 0.50, "tz": "Europe/London"},
        "event": {"date": "1997-08-31", "domain": "HEALTH_AUTOMOTIVE_CAR_CRASH", "label": "Fatal Paris Car Crash (Age 36)"}
    },
    {
        "name": "STEVE_JOBS",
        "birth": {"year": 1955, "month": 2, "day": 24, "hour": 19, "minute": 15, "lat": 37.7749, "lon": -122.4194, "tz": "America/Los_Angeles"},
        "event": {"date": "2011-10-05", "domain": "HEALTH_NATURAL_LIFESPAN_CESSATION", "label": "Passing from Pancreatic Cancer (Age 56)"}
    },
    {
        "name": "SANJAY_GANDHI",
        "birth": {"year": 1946, "month": 12, "day": 14, "hour": 9, "minute": 27, "lat": 28.6139, "lon": 77.2090, "tz": "Asia/Kolkata"},
        "event": {"date": "1980-06-23", "domain": "HEALTH_AVIATION_PLANE_CRASH", "label": "Pitts S-2A Fatal Plane Crash (Age 33)"}
    },
    {
        "name": "INDIRA_GANDHI",
        "birth": {"year": 1917, "month": 11, "day": 19, "hour": 23, "minute": 11, "lat": 25.4358, "lon": 81.8463, "tz": "Asia/Kolkata"},
        "event": {"date": "1984-10-31", "domain": "HEALTH_VIOLENT_ATTACK_ASSASSINATION", "label": "Fatal Assassination (Age 66)"}
    }
]

def test_premature_death_detection():
    print("=" * 95)
    print("PREMATURE DEATH / APAMRITYU EVENT DETECTION TEST")
    print("=" * 95)

    hits = 0
    total = len(PREMATURE_DEATH_CASES)

    for item in PREMATURE_DEATH_CASES:
        name = item["name"]
        b = item["birth"]
        ev = item["event"]
        ev_date = datetime.datetime.fromisoformat(ev["date"])

        chart, _ = calculate_chart_with_object(b["year"], b["month"], b["day"], b["hour"], b["minute"], b["lat"], b["lon"], b["tz"], name=name)
        scanner = ForwardTimingScanner(chart)

        # Scan 36 months around the event
        start_scan = pytz.utc.localize(datetime.datetime(ev_date.year - 1, 1, 1))
        windows = scanner.scan_domain_windows(ev["domain"], start_scan, months_ahead=36)

        match = None
        for w in windows:
            w_start = datetime.datetime.fromisoformat(w["macro_window_start"]).date()
            w_end = datetime.datetime.fromisoformat(w["macro_window_end"]).date()
            if w_start <= ev_date.date() <= w_end:
                match = w
                break

        if match:
            hits += 1
            print(f"\n🎯 [CAPTURED] {name:18s} | {ev['label']}")
            print(f"     • Macro Dasha Window : {match['macro_window_start']} to {match['macro_window_end']}")
            print(f"     • Peak Trigger Dates : {match['peak_trigger_dates']}")
            print(f"     • Dasha Hierarchy    : {match['dasha_hierarchy']}")
            print(f"     • Micro Details      : {match.get('micro_trigger_details')}")
        else:
            print(f"\n⚠️ [MISSED] {name:18s} | {ev['label']}")

    print("\n" + "=" * 95)
    print(f"📊 APAMRITYU DETECTION RESULT: {hits} / {total} Premature Events Captured ({hits/total*100:.1f}%)")
    print("=" * 95)

if __name__ == "__main__":
    test_premature_death_detection()
