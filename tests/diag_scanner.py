import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
import pytz
from astrology_engine import calculate_chart_with_object
from forward_timing_scanner import ForwardTimingScanner, DOMAIN_HOUSE_MAP

chart, payload = calculate_chart_with_object(1975, 5, 6, 7, 15, 16.8667, 81.9333, "Asia/Kolkata", 0)
scanner = ForwardTimingScanner(chart)
print("Lagna Sign Index:", scanner.lagna_sign_idx)

config = DOMAIN_HOUSE_MAP["BUSINESS"]
target_houses = config["houses"]
target_karakas = config["karakas"]
target_lords = []
for h in target_houses:
    sign_idx = (scanner.lagna_sign_idx + h - 1) % 12
    from forward_timing_scanner import SIGN_LORDS, ZODIAC_SIGNS
    lord = SIGN_LORDS[ZODIAC_SIGNS[sign_idx]]
    target_lords.append(lord)

print("Target Houses:", target_houses)
print("Target Lords:", target_lords)
print("Target Significators:", set(target_lords + target_karakas))

dt = pytz.utc.localize(datetime(2026, 4, 1))
res = scanner._check_transits_at_date(dt, target_houses, target_lords)
print("Double Transit check at 2026-04-01:", res)
