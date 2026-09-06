import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
import json
from rectification_engine import RectificationEngine
from kp_engine import KPEngine

# Person: DOB recorded as 7:15 AM, May 6, 1975, Mandapeta, East Godavari, AP
# Mandapeta coords: 16.8667 N, 81.9333 E, IST
LAT  = 16.8667
LON  = 81.9333
TZ   = "Asia/Kolkata"

# Recorded birth time
recorded = datetime(1975, 5, 6, 7, 15)

# Real life events (actual, verifiable)
events = [
    {"date": "01-01-1995", "type": "career_job"},        # Started business (approx Jan 95)
    {"date": "21-11-2001", "type": "marriage"},           # Married exactly
    {"date": "29-04-2026", "type": "property_purchase"},  # Moved into own house
]

print("=" * 60)
print("PERSON : Mandapeta, East Godavari, AP")
print("RECORDED : 7:15 AM, 6 May 1975")
print("COORDS   : %.4f N, %.4f E" % (LAT, LON))
print("=" * 60)
print()

# 1. Show the KP chart at the recorded time first
kp = KPEngine.calculate_kp_chart(1975, 5, 6, 7, 15, LAT, LON, TZ)
print("KP CHART @ 7:15 AM (RECORDED TIME)")
print("Lagna (1st cusp):", kp["cusps"][0]["sign"], "%.2f°" % kp["cusps"][0]["degree"])
print("Lagna Star Lord :", kp["cusps"][0]["star_lord"])
print("Lagna Sub Lord  :", kp["cusps"][0]["sub_lord"])
print("House Cusps:")
for c in kp["cusps"]:
    print(f"  H{c['house']:2d}: {c['sign']:12s} {c['degree']:6.2f}° | SL={c['star_lord']:8s} SUB={c['sub_lord']}")
print()

# 2. Run rectification
print("RUNNING RECTIFICATION ENGINE (+-120 min, 4-min steps)...")
result = RectificationEngine.rectify(
    birth_datetime=recorded,
    birth_lat=LAT, birth_lon=LON,
    events=events,
    timezone_str=TZ,
    search_minutes=120,
    step_minutes=4,
    include_double_transit=False
)

print()
print("=" * 60)
print("RECTIFICATION RESULT")
print("=" * 60)
print("Recorded     :", result["original_birth_time"])
print("Rectified    :", result["rectified_birth_time"])
print("Shift        :", result["shift_minutes"], "minutes")
print("Best Score   :", result["best_score"])
print("Peak Sharpn  :", result.get("peak_sharpness"))
print("Confidence   :", result["confidence"], "%")
print("Candidates   :", result["candidate_count"])
print("Debug error  :", result.get("debug_error"))
print()
print("-- Per-Event Scores (at rectified time) --")
for ev in (result["event_scores"] or []):
    print(f"  {ev['date']} ({ev['event_type']:20s}): CSL={ev['csl_score']} DASHA={ev['dasha_score']} LAGNA={ev['lagna_score']} TOTAL={ev['total']}")
    print(f"    Dasha: {ev['dasha']['mahadasha']} / {ev['dasha']['antardasha']} / {ev['dasha']['pratyantardasha']}")

print()
print("-- Score Curve (shift -> score) --")
# Print only the top 10 by score to see where the peak is
curve = sorted(result["score_curve"], key=lambda x: x["score"], reverse=True)[:10]
for c in curve:
    bar = "#" * int(c["score"] * 40)
    print(f"  {c['shift_minutes']:+4d} min : {c['score']:.4f}  {bar}")

# Show rectified KP chart
shift = result["shift_minutes"]
rdt = recorded.replace(hour=7, minute=15) 
from datetime import timedelta
rdt2 = rdt + timedelta(minutes=shift)
print()
print("=" * 60)
print(f"RECTIFIED CHART @ {rdt2.strftime('%H:%M')}")
kp2 = KPEngine.calculate_kp_chart(rdt2.year, rdt2.month, rdt2.day, rdt2.hour, rdt2.minute, LAT, LON, TZ)
print("Lagna (1st cusp):", kp2["cusps"][0]["sign"], "%.2f°" % kp2["cusps"][0]["degree"])
print("Lagna Star Lord :", kp2["cusps"][0]["star_lord"])
print("Lagna Sub Lord  :", kp2["cusps"][0]["sub_lord"])
