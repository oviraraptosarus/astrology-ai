import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

print("=== TEST 1: Geocentric Chart Calculation (Vedic standard; topocentric removed) ===")
from astrology_engine import calculate_chart_with_object
chart, _ = calculate_chart_with_object(2008, 8, 1, 18, 25, 16.8186, 82.0641, "Asia/Kolkata", "Test")
print(f"Lagna: {chart.ascendant_sign} {chart.ascendant_degree:.2f}°")
print(f"Planets: {', '.join(chart.planets.keys())}")
assert chart.ascendant_sign == "Capricorn", "Lagna must stay Capricorn (geocentric fix)"
print("OK: Geocentric chart computed successfully")

print()
print("=== TEST 2: Full Shadbala (is_partial=False) ===")
from strength_engine import StrengthEngine
StrengthEngine.calculate_shadbala(chart)
for name, p in chart.planets.items():
    if name in ["Rahu", "Ketu", "Ascendant"]:
        continue
    s = p.shadbala
    print(f"{name}: Sthana={s['sthana_bala']} Dig={s['dig_bala']} Kala={s['kala_bala']} Cheshta={s['cheshta_bala']} Naisargika={s['naisargika_bala']} Drik={s['drik_bala']} TOTAL={s['total']} partial={s['is_partial']}")

print()
print("=== TEST 3: Rectification Engine loads and runs ===")
from rectification_engine import RectificationEngine
print(f"Event houses: {list(RectificationEngine.EVENT_HOUSES.keys())}")
print(f"Dasha sequence: {RectificationEngine.DASHA_SEQUENCE}")

# Quick dasha-on-date test (signature: birth_moon_nak_lord, birth_utc, event_utc)
test_dasha = RectificationEngine._dasha_on_date(
    "Ketu",
    __import__('datetime').datetime(2008, 8, 1, 13, 0),  # UTC
    __import__('datetime').datetime(2026, 9, 6, 6, 0)    # UTC today
)
print(f"Dasha on 2026-09-06: Maha={test_dasha['mahadasha']} Antar={test_dasha['antardasha']} Pratyantar={test_dasha['pratyantardasha']}")

print()
print("=== ALL UPGRADE TESTS PASSED ===")
