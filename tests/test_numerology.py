import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from astrology_engine import calculate_chart_with_object
from numerology_engine import NumerologyEngine

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

print('=== 8. ANK JYOTISH NUMEROLOGY ===')
rep = NumerologyEngine.generate_full_profile(day=1, month=8, year=2008, name="Rahul Sharma")
print("Moolank:", rep['moolank'])
print("Bhagyank:", rep['bhagyank'])
print("Core Harmony:", rep['core_harmony'])
print("Namank:", rep['namank'])
print("Name Harmony:", rep['name_harmony'])
print("Katapayadi:", rep['katapayadi_nama'])
