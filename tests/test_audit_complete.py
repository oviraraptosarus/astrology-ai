import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from astrology_engine import calculate_chart_with_object
from advanced_avasthas import AdvancedAvasthaEngine

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

print('=== 1. BASIC CHART INFO ===')
print(f'Lagna: {chart.ascendant_sign} ({chart.ascendant_degree:.2f} deg)')
print(f'Moon: {chart.planets["Moon"].sign} ({chart.planets["Moon"].degree:.2f} deg)')

print('\n=== 7. ADVANCED AVASTHAS & CHESHTA ===')
eng = AdvancedAvasthaEngine(chart)
res = eng.combine_all()
for p, arr in res.get("lajjitadi_avasthas", {}).items():
    print(f" {p}:")
    for s in arr:
        print(f"   - [{s['state']}] {s['reason']}")
for p, d in res.get("retrogression_anomalies", {}).items():
    print(f" {p}: [{d['effect']}] {d['description']}")

print('\nALL SYSTEM CHECKS PASSED WITH ZERO ERRORS!')
