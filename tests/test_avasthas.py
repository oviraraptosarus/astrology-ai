import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from astrology_engine import calculate_chart_with_object
from advanced_avasthas import AdvancedAvasthaEngine

# Test with User's Birth Details: Aug 1 2008, 18:25 IST, Ramachandrapuram (16.8186 N, 82.0641 E)
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

eng = AdvancedAvasthaEngine(chart)
res = eng.combine_all()
print("LAJJITADI:")
print(res['lajjitadi_avasthas'])
print("RETROGRESSION:")
print(res['retrogression_anomalies'])
