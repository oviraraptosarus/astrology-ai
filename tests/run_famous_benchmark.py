import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from astrology_engine import calculate_chart_with_object
from rectification_engine import RectificationEngine
from user_memory_engine import ContextMemoryEngine
from event_analysis import EventPredictionEngine

lat, lon = 25.4358, 81.8463 # Allahabad, India
chart, payload = calculate_chart_with_object(1942, 10, 11, 16, 0, lat, lon, "Asia/Kolkata", 0)

print("=================================================================")
print("BENCHMARK CHART: AMITABH BACHCHAN (Oct 11, 1942, 16:00 IST)")
print("=================================================================")

# 1. Chart Baseline
asc = payload['Basic_Chart']['Ascendant']
print(f"Lagna Sign  : {asc['sign']} at {asc['degree']:.2f} deg ({asc['nakshatra']})")
print(f"8th House   : Virgo (Sun, Mars, Mercury-Exalted, Venus-Debilitated)")
print(f"6th House   : Cancer (Jupiter-Exalted)")
print(f"4th House   : Taurus (Saturn)")

# 2. Historical Life Events Verification
events = [
    {"type": "marriage", "date": "03-06-1973", "desc": "Marriage to Jaya Bhaduri"},
    {"type": "accident_surgery", "date": "02-08-1982", "desc": "Coolie Near-Fatal Accident & Surgery"},
    {"type": "promotion", "date": "03-07-2000", "desc": "Kaun Banega Crorepati Star Resurgence"}
]

rect = RectificationEngine.rectify(
    birth_datetime=datetime(1942, 10, 11, 16, 0),
    birth_lat=lat, birth_lon=lon,
    events=events, timezone_str="Asia/Kolkata",
    search_minutes=40, step_minutes=4
)

print("\n--- 1. EVENT RECTIFICATION & RETRODICTIVE SCORING ---")
print(f"Overall Confidence : {rect['confidence']}%")
print(f"Best Match Score   : {rect['best_score']}")
for ev in rect['event_scores']:
    print(f"  * Event: {ev['event_type']:18s} ({ev['date']}) | Dasha: {ev['dasha']['mahadasha']}-{ev['dasha']['antardasha']}-{ev['dasha']['pratyantardasha']} | Score: {ev['total']*100:.1f}%")

# 3. Context Memory Calibration
mem = ContextMemoryEngine()
prof = mem.get_or_create_profile("bachchan_1942", "1942-10-11")
mem.record_user_correction("bachchan_1942", "I am an actor, married since 1973, have 2 children", prof)

print("\n--- 2. CONTEXT MEMORY CALIBRATION TEST ---")
cal_mar = mem.calibrate_domain_prediction("MARRIAGE", {}, prof)
cal_car = mem.calibrate_domain_prediction("CAREER", {}, prof)
print(f"Age: {prof.current_age} | Marital: {prof.marital_status} | Career: {prof.career_type}")
print(f"  Marriage Query Calibrated -> {cal_mar['calibrated_archetype']}")
print(f"  Career Query Calibrated   -> {cal_car['calibrated_archetype']}")
