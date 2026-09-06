import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import datetime
import pytz
import json
from panchangam_engine import PanchangamEngine

pe = PanchangamEngine()
now = datetime.datetime.now(pytz.timezone("Asia/Kolkata"))

# Test for New Delhi (28.6139 N, 77.2090 E)
panchang = pe.calculate_full_panchang(now, lat=28.6139, lon=77.2090, tz_name="Asia/Kolkata")

print("=== DRIK PANCHANGAM OUTPUT ===")
print("Time:", panchang["datetime_local"])
print("Sunrise:", panchang["sun_metrics"]["sunrise"], "| Sunset:", panchang["sun_metrics"]["sunset"])
print("Vara:", panchang["panchanga"]["vara"]["name"], "(Lord:", panchang["panchanga"]["vara"]["lord"] + ")")
print("Tithi:", panchang["panchanga"]["tithi"]["name"], "| Ends at:", panchang["panchanga"]["tithi"]["ends_at"])
print("Nakshatra:", panchang["panchanga"]["nakshatra"]["name"], "(Pada", str(panchang["panchanga"]["nakshatra"]["pada"]) + ") | Ends at:", panchang["panchanga"]["nakshatra"]["ends_at"])
print("Yoga:", panchang["panchanga"]["yoga"]["name"])
print("Karana:", panchang["panchanga"]["karana"]["name"])
print("Active Hora:", panchang["panchanga"]["active_hora"])
print("Rahu Kalam:", panchang["inauspicious_periods"]["rahu_kalam"])
print("Gulika Kalam:", panchang["inauspicious_periods"]["gulika_kalam"])
print("Abhijit Muhurta:", panchang["auspicious_periods"]["abhijit_muhurta"])
print("Brahma Muhurta:", panchang["auspicious_periods"]["brahma_muhurta"])
print("Tithi Shoonya Signs:", panchang["tithi_shoonya_rashis"])
print("\nFirst 3 Day Choghadiyas:")
for c in panchang["choghadiya_day"][:3]:
    print(f" - {c['choghadiya']:<8} ({c['nature']:<12}) : {c['start']} to {c['end']}")
