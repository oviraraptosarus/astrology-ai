import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from rectification_engine import RectificationEngine

LAT  = 16.8667
LON  = 81.9333
TZ   = "Asia/Kolkata"
recorded = datetime(1975, 5, 6, 7, 15)

events = [
    {"date": "01-01-1995", "type": "career_job"},
    {"date": "21-11-2001", "type": "marriage"},
    {"date": "29-04-2026", "type": "property_purchase"},
]

print("Running deep analysis with DOUBLE TRANSITS ENABLED...")
result = RectificationEngine.rectify(
    birth_datetime=recorded,
    birth_lat=LAT, birth_lon=LON,
    events=events,
    timezone_str=TZ,
    search_minutes=120,
    step_minutes=4,
    include_double_transit=True  # Turn on the transit engine!
)

print(f"Recorded     : {result['original_birth_time']}")
print(f"Rectified    : {result['rectified_birth_time']} (Shift: {result['shift_minutes']} min)")
print(f"Best Score   : {result['best_score']:.4f}")
print(f"Confidence   : {result['confidence']:.1f}%\n")

# Let's manually inspect what the engine saw for the recorded time (Shift 0) vs Best Shift
target_shifts = [0, result["shift_minutes"]]
# Also grab the closest peaks to the original time
curve = sorted(result["score_curve"], key=lambda x: abs(x["shift_minutes"]))
print("--- SCORES AROUND RECORDED TIME (7:15 AM) ---")
for c in curve:
    if abs(c["shift_minutes"]) <= 20:
        print(f"  Shift {c['shift_minutes']:+4d} min | Time: {(recorded + __import__('datetime').timedelta(minutes=c['shift_minutes'])).strftime('%H:%M')} | Score = {c['score']:.4f}")
print()

# Now find the absolute best peaks
print("--- TOP 5 CANDIDATES NATIONWIDE ---")
top = sorted(result["score_curve"], key=lambda x: x["score"], reverse=True)[:5]
for c in top:
    print(f"  Shift {c['shift_minutes']:+4d} min | Time: {(recorded + __import__('datetime').timedelta(minutes=c['shift_minutes'])).strftime('%H:%M')} | Score = {c['score']:.4f}")
