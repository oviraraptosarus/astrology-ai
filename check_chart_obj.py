import sys
sys.path.insert(0, r"E:\ASTROLOGY AI")
import astrology_engine

chart_obj, chart_dict = astrology_engine.calculate_chart_with_object(
    year=2008, month=4, day=5,
    hour=6, minute=15,
    lat=50.3480, lon=18.9328,
    tz_name='Europe/Warsaw'
)
print("chart_obj attributes:", dir(chart_obj))
print("chart_obj.planets type:", type(chart_obj.planets))
if isinstance(chart_obj.planets, dict):
    print("dict keys:", list(chart_obj.planets.keys()))
    for k, v in list(chart_obj.planets.items())[:2]:
        print(f"  {k}: {type(v)} {v}")
elif isinstance(chart_obj.planets, list):
    print("list len:", len(chart_obj.planets), "items:", chart_obj.planets[:3])
