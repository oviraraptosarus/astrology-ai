import sys, os, pytz
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from astrology_engine import calculate_chart_with_object
from tajika_engine import TajikaVarshaphalaEngine

print("Testing High Latitude in Tajika Engine...")
try:
    chart, _ = calculate_chart_with_object(
        1985, 1, 15, 12, 0, 70.0, 20.0, "UTC", "Vulnerable Native"
    )
    res = TajikaVarshaphalaEngine.calculate_annual_chart(chart, 2025, 70.0, 20.0)
    print("SUCCESS")
except Exception as e:
    print(f"FAILED with Exception: {type(e).__name__}: {e}")
