import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from astrology_engine import calculate_chart_with_object
from forward_timing_scanner import ForwardTimingScanner

def scan_chart_demo(name: str, y, m, d, h, mn, lat, lon, tz, scan_domains, start_dt, months):
    print("=" * 70)
    print(f"CHART: {name} ({y:04d}-{m:02d}-{d:02d} {h:02d}:{mn:02d} {tz})")
    print("=" * 70)
    chart, payload = calculate_chart_with_object(y, m, d, h, mn, lat, lon, tz, 0)
    asc = payload['Basic_Chart']['Ascendant']
    print(f"Computed Lagna : {asc['sign']} at {asc['degree']:.2f} deg ({asc['nakshatra']})")
    
    scanner = ForwardTimingScanner(chart)
    for dom in scan_domains:
        windows = scanner.scan_domain_windows(dom, start_date=start_dt, months_ahead=months)
        print(f"\n--- DOMAIN: {dom} ({len(windows)} qualified windows found) ---")
        for idx, w in enumerate(windows[:2], 1):
            print(f"  [{idx}] Status : {w.get('prediction_state', 'UNKNOWN')} ({w['confidence']})")
            print(f"      Event Label : {w['event_label']}")
            print(f"      Macro Window: {w['macro_window_start']} to {w['macro_window_end']}")
            print(f"      Peak Dates  : {w['peak_trigger_dates']}")
            print(f"      Dasha Triad : {w['dasha_hierarchy']}")
            print(f"      Micro Detail: {w['micro_trigger_details']}")

# 1. User Chart (May 6, 1975) -> Forward 2026-2028
scan_chart_demo(
    "User Chart", 1975, 5, 6, 7, 15, 16.8667, 81.9333, "Asia/Kolkata",
    ["BUSINESS", "WEALTH", "HEALTH_ACCIDENT"], datetime(2026, 1, 1), 24
)

# 2. Arbitrary Young Client (Aug 15, 1998, Bangalore) -> Forward 2026-2028
scan_chart_demo(
    "New Client Chart", 1998, 8, 15, 14, 30, 12.9716, 77.5946, "Asia/Kolkata",
    ["CAREER", "MARRIAGE"], datetime(2026, 1, 1), 24
)
