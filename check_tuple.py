import sys
import json
sys.path.insert(0, r"E:\ASTROLOGY AI")
import astrology_engine

res = astrology_engine.calculate_chart_with_object(
    year=2008, month=4, day=5,
    hour=6, minute=15,
    lat=50.3480, lon=18.9328,
    tz_name='Europe/Warsaw'
)
print("Type of res:", type(res), "len:", len(res) if isinstance(res, (tuple, list)) else "N/A")
for idx, item in enumerate(res):
    print(f"Item {idx}: type={type(item)}")
