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

domains = [
    "CAREER_FOUNDING_ENTERPRISE",
    "CAREER_TECH_PRODUCT_LAUNCH",
    "CAREER_BREAKTHROUGH",
    "WEALTH_LIQUID_WINDFALL",
    "WEALTH_PASSIVE_ROYALTIES_IP",
    "WEALTH_FOREIGN_CURRENCY",
    "WEALTH_SPECULATIVE_GAINS",
    "EDUCATION_UNIVERSITY_GRADUATION",
    "EDUCATION_COLLEGE_DROPOUT_AUTONOMY",
    "EDUCATION_COMPETITIVE_EXAM_TOP_RANK",
    "RELOCATION_PERMANENT_EMIGRATION",
    "OCCULT_DEEP_JYOTISHA_MASTERY",
    "HEALTH_ACUTE_SURGICAL_INTERVENTION"
]

print("================================================================================")
print("             PREDICTIVE CONVERGENCE SCAN (2024 - 2031)")
print("================================================================================")

for dom in domains:
    wins = fts.scan_domain_windows(dom, start_date=datetime(2024, 1, 1), months_ahead=84)
    # filter for score >= 60
    high_wins = [w for w in wins if (w.get('model_score') or 0) >= 60.0]
    print(f"\n>>> DOMAIN: {dom} (Total high-score windows: {len(high_wins)})")
    for w in high_wins:
        print(f"  - [{w['macro_window_start']} to {w['macro_window_end']}] Score: {w['model_score']} | Dasha: {w['dasha_hierarchy']}")
        print(f"    Peak Trigger: {w['peak_trigger_dates']} | Micro: {w['micro_trigger_details']}")
        print(f"    Transits: {'; '.join(w.get('transit_evidence', []))}")
