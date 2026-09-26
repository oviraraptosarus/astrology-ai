import sys
import os
sys.path.insert(0, "E:/ASTROLOGY AI")
from datetime import datetime
import json
from astrology_engine import calculate_chart_with_object
from forward_timing_scanner import ForwardTimingScanner

chart, chart_dict = calculate_chart_with_object(2008, 8, 1, 18, 25, 16.8185549, 82.0641497, tz_name='Asia/Kolkata')
chart.birth_time = datetime(2008, 8, 1, 12, 55)

fts = ForwardTimingScanner(chart)

domains_to_scan = [
    "EDUCATION_UNIVERSITY_GRADUATION",
    "EDUCATION_COLLEGE_DROPOUT_AUTONOMY",
    "EDUCATION_COMPETITIVE_EXAM_TOP_RANK",
    "CAREER_BREAKTHROUGH",
    "CAREER_FOUNDING_ENTERPRISE",
    "CAREER_TECH_PRODUCT_LAUNCH",
    "WEALTH_LIQUID_WINDFALL",
    "WEALTH_PASSIVE_ROYALTIES_IP",
    "WEALTH_FOREIGN_CURRENCY",
    "RELOCATION_PERMANENT_EMIGRATION",
    "OCCULT_DEEP_JYOTISHA_MASTERY",
    "HEALTH_ACUTE_SURGICAL_INTERVENTION"
]

results = {}
for dom in domains_to_scan:
    try:
        windows = fts.scan_domain_windows(dom, start_date=datetime(2024, 1, 1), months_ahead=84) # 7 years: 2024-2031
        results[dom] = windows
    except Exception as e:
        results[dom] = f"ERROR: {e}"

for dom, wins in results.items():
    print(f"\n==================================================")
    print(f" DOMAIN: {dom}")
    print(f"==================================================")
    if isinstance(wins, list):
        if not wins:
            print("  No high-probability convergence windows found.")
        for w in wins:
            print(f"  Window: {w.get('window_start')} -> {w.get('window_end')} | Score: {w.get('total_score')} | Quality: {w.get('window_quality')}")
            print(f"    Dasha Triad: {w.get('dasha_triad')}")
            print(f"    Transits: Jup={w.get('jupiter_transit_sign')} | Sat={w.get('saturn_transit_sign')}")
            print(f"    Drivers: {w.get('drivers')}")
            if w.get('acute_micro_triggers'):
                print(f"    Micro Triggers: {w.get('acute_micro_triggers')}")
    else:
        print(f"  {wins}")
