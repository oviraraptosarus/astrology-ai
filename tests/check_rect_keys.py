import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from rectification_engine import RectificationEngine

lat, lon = 25.4358, 81.8463
events = [
    {"type": "marriage", "date": "03-06-1973"},
    {"type": "accident_surgery", "date": "02-08-1982"},
    {"type": "promotion", "date": "03-07-2000"}
]

rect_res = RectificationEngine.rectify(
    birth_datetime=datetime(1942, 10, 11, 16, 0),
    birth_lat=lat, birth_lon=lon,
    events=events, timezone_str="Asia/Kolkata",
    search_minutes=60, step_minutes=4
)
print("Keys:", rect_res.keys())
for k, v in rect_res.items():
    if k != 'curve':
        print(f"  {k}: {v}")
