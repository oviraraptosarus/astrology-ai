import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from rectification_engine import RectificationEngine

# User's REAL chart: correct birth time = 2008-08-01 18:25 IST
# Simulate the recorded time being WRONG by +40 min
recorded = datetime(2008, 8, 1, 19, 5)
actual   = datetime(2008, 8, 1, 18, 25)

events = [
    {"date": "15-08-2018", "type": "education"},
    {"date": "01-06-2024", "type": "career_job"},
    {"date": "05-09-2026", "type": "financial_gain"},
]

result = RectificationEngine.rectify(
    birth_datetime=recorded,
    birth_lat=16.8186, birth_lon=82.0641,
    events=events,
    timezone_str="Asia/Kolkata",
    search_minutes=120, step_minutes=5,
    include_double_transit=False
)

print("Recorded time (fed to engine):", recorded)
print("Actual correct time:           ", actual)
print()
print("Engine returned rectified time:", result["rectified_birth_time"])
print("Shift found:                   ", result["shift_minutes"], "min  (expected -40)")
print("Best score:                    ", result["best_score"])
print("Peak sharpness:                ", result.get("peak_sharpness"))
print("Confidence:                    ", result["confidence"])
curve = [c["score"] for c in result["score_curve"]]
print("Score range:                   ", round(min(curve),4), "->", round(max(curve),4))
print("Debug error:                   ", result.get("debug_error"))
print()
print("VERDICT:", "RECOVERED" if result["shift_minutes"] == -40 else "MISSED")
