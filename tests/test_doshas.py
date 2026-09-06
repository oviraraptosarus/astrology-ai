import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from astrology_engine import calculate_chart_with_object
from dosha_engine import DoshaEngine
from yogas import evaluate_all_yogas

chart, _ = calculate_chart_with_object(
    year=2008,
    month=8,
    day=1,
    hour=18,
    minute=25,
    lat=16.8186,
    lon=82.0641,
    tz_name='Asia/Kolkata',
    name='User Test'
)

print('=== 9. DOSHAS (SADE SATI & MANGLIK) ===')
de = DoshaEngine(chart)
import datetime, pytz
dosha_res = de.evaluate_all(target_date=datetime.datetime.now(pytz.utc))
print("Sade Sati Phase:", dosha_res["sade_sati"]["phase"])
print("Is Manglik:", dosha_res["kuja_dosha"]["is_manglik"])
print("Kuja Dosha Cancellations:", dosha_res["kuja_dosha"].get("cancellations", []))

print('\n=== 10. CLASSICAL YOGAS ===')
y_res = evaluate_all_yogas(chart)
for r in y_res:
    print(f" - {r['name']} Yoga (Fired: {r['fired']}) | {r['reason']}")
    for ex in r.get("exceptions_encountered", []):
         print(f"    * Exception: {ex}")
