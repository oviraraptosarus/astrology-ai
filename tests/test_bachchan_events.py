import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from rectification_engine import RectificationEngine
from event_analysis import EventPredictionEngine
from astrology_engine import calculate_chart_with_object

lat, lon = 25.4358, 81.8463
events = [
    {"type": "marriage", "date": "03-06-1973"},
    {"type": "accident_surgery", "date": "02-08-1982"},
    {"type": "promotion", "date": "03-07-2000"}
]

print("=== RUNNING RECTIFICATION ON AMITABH BACHCHAN'S RECORDED TIME (16:00 IST) ===")
rect_res = RectificationEngine.rectify(
    birth_datetime=datetime(1942, 10, 11, 16, 0),
    birth_lat=lat, birth_lon=lon,
    events=events, timezone_str="Asia/Kolkata",
    search_minutes=60, step_minutes=4,
    include_double_transit=True
)

print(f"Recorded Time : 16:00 IST")
rect_time_str = rect_res.get('rectified_birth_time', rect_res.get('rectified_time', 'N/A'))
print(f"Rectified Time: {rect_time_str} (Shift: {rect_res.get('shift_minutes')} min)")
print(f"Score         : {rect_res.get('best_score')}")
print(f"Confidence    : {rect_res.get('confidence')}")

print("\nTop Candidates:")
curve_data = rect_res.get('score_curve', rect_res.get('curve', []))
for c in sorted(curve_data, key=lambda x: x.get('score', 0), reverse=True)[:5]:
    print(f"  Shift {c.get('shift_minutes', 0):+3d} min -> Score: {c.get('score', 0):.4f}")

# Now let's evaluate the life event activations on his chart
chart, payload = calculate_chart_with_object(1942, 10, 11, 16, 0, lat, lon, "Asia/Kolkata", 0)
engine = EventPredictionEngine(chart)

print("\n=== PREDICTIVE EVENT TIMING ACCURACY ON ACTUAL HISTORICAL DATES ===")

# 1. 1982 Coolie Accident
res_acc = engine.analyze_event("Will there be any accident or surgery?", datetime(1982, 8, 2))
print("\n1. 1982 Coolie Accident (02-08-1982):")
print(f"   Domain: {res_acc.domain}")
print(f"   Natal Promise: {res_acc.natal_promise['status']}")
print(f"   Activated Houses: {res_acc.timing['activated_natal_houses']}")
print(f"   Activated Lords : {res_acc.timing['activated_natal_lords']}")

# 2. 1973 Marriage to Jaya Bhaduri
res_mar = engine.analyze_event("Marriage timing with partner", datetime(1973, 6, 3))
print("\n2. 1973 Marriage (03-06-1973):")
print(f"   Domain: {res_mar.domain}")
print(f"   Natal Promise: {res_mar.natal_promise['status']}")
print(f"   Activated Houses: {res_mar.timing['activated_natal_houses']}")

# 3. 2000 Career Resurgence (KBC)
res_car = engine.analyze_event("Career promotion and status elevation", datetime(2000, 7, 3))
print("\n3. 2000 KBC Resurgence (03-07-2000):")
print(f"   Domain: {res_car.domain}")
print(f"   Natal Promise: {res_car.natal_promise['status']}")
print(f"   Activated Houses: {res_car.timing['activated_natal_houses']}")
