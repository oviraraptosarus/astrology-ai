import os, sys, json
from datetime import datetime
import pytz

from astrology_engine import calculate_chart_with_object, ZODIAC_SIGNS
from forward_timing_scanner import ForwardTimingScanner
from sade_sati_engine import SadeSatiEngine
from gochara_vedha_engine import GocharaVedhaEngine
from sarvatobhadra_chakra_engine import SarvatobhadraChakraEngine

chart, _ = calculate_chart_with_object(2008, 8, 1, 18, 25, lat=16.85, lon=82.02, tz_name="Asia/Kolkata")
scanner = ForwardTimingScanner(chart)
sbc_eng = SarvatobhadraChakraEngine(chart)

print("\n--- FORWARD TIMING SCANNER (PROBLEMS/SETBACKS 2026) ---")
problem_domains = ["LITIGATION", "HEALTH", "ACCIDENT_TRAUMA", "CAREER_EMPLOYMENT_DISPUTE"]
for d in problem_domains:
    try:
        windows = scanner.scan_domain_windows(d, start_date=datetime(2026, 1, 1, tzinfo=pytz.UTC), months_ahead=12)
        print(f"\nDOMAIN: {d}")
        for w in sorted(windows, key=lambda x: x.get("model_score", 0), reverse=True):
            if w.get("model_score", 0) >= 50:
                print(f"  {w.get('macro_window_start')} to {w.get('macro_window_end')} | Score: {w.get('model_score')} | Peak: {w.get('exact_peak_date')} | Type: {w.get('event_type')} | Confidence: {w.get('confidence')}")
    except Exception as e:
        print(f"Error on {d}: {e}")

print("\n--- SARVATOBHADRA CHAKRA VEDHAS (2026 CRITICAL MONTHS) ---")
for month in [1, 4, 7, 10]:
    dt = datetime(2026, month, 15, tzinfo=pytz.UTC)
    sbc = sbc_eng.evaluate_transit_vedha(target_dt=dt)
    critical_hits = []
    for tp, tdata in sbc.items():
        if not isinstance(tdata, dict): continue
        if tdata.get("is_malefic") and tdata.get("strikes_sensitive_nak"):
            critical_hits.append(f"{tdata.get('transiting_planet')} striking {tdata.get('struck_special_nakshatra')}")
    if critical_hits:
        print(f"  {dt.strftime('%b %Y')}: {', '.join(critical_hits)}")
