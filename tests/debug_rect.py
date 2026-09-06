import sys, os, traceback
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
import pytz

from astrology_engine import calculate_chart_with_object

tz = pytz.timezone("Asia/Kolkata")
candidate_dt = tz.localize(datetime(2008, 8, 1, 18, 25))

print("Calling calculate_chart_with_object directly...")
try:
    cand = calculate_chart_with_object(
        year=candidate_dt.year, month=candidate_dt.month,
        day=candidate_dt.day, hour=candidate_dt.hour,
        minute=candidate_dt.minute, lat=16.8186, lon=82.0641,
        tz_name="Asia/Kolkata"
    )
    print("SUCCESS:", type(cand))
    print("chart:", cand[0].ascendant_sign if isinstance(cand, tuple) else "N/A")
except Exception:
    traceback.print_exc()
