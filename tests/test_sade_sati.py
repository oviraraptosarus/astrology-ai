import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from astrology_engine import calculate_chart_with_object
from sade_sati_engine import SadeSatiEngine

print("=" * 70)
print("TEST: SADE SATI LIFECYCLE ENGINE FOR AMITABH BACHCHAN (MOON IN LIBRA)")
print("=" * 70)
chart_ab, _ = calculate_chart_with_object(1942, 10, 11, 16, 0, 25.4358, 81.8463, "Asia/Kolkata", 0)
sade_engine = SadeSatiEngine(chart_ab)

# Current live status
status_2026 = sade_engine.evaluate_current_status(datetime(2026, 4, 1))
print("Status on April 1, 2026:")
for k, v in status_2026.items():
    print(f"  {k}: {v}")

# Lifetime Timeline
timeline = sade_engine.generate_lifetime_sade_sati_timeline(datetime(1942, 10, 11), scan_years=85)
print(f"\nTotal Critical Shani Transit Phases Found Across Lifetime: {len(timeline)}")
for idx, phase in enumerate(timeline[:8], 1):
    print(f"  [{idx}] {phase['category']} - {phase['phase']}")
    print(f"      Sign: {phase['transit_sign']} | Dates: {phase['start_date']} to {phase['end_date']} ({phase['duration_years']} yrs)")
    print(f"      SAV Bindus: {phase['sav_bindus']} | Impact: {phase['impact']}")
