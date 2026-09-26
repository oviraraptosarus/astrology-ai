import datetime
from astrology_engine import calculate_chart_with_object
from dasha_engine import DashaEngine
from config import Config

DASHA_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
DASHA_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]

def ind_vimshottari(moon_lon):
    nak_span = 360.0 / 27.0
    nak_idx = int(moon_lon / nak_span)
    lord_idx = nak_idx % 9
    lord = DASHA_LORDS[lord_idx]
    
    fraction_elapsed = (moon_lon % nak_span) / nak_span
    fraction_left = 1.0 - fraction_elapsed
    
    balance_years = fraction_left * DASHA_YEARS[lord_idx]
    return lord, balance_years

print("--- PART 1 & 3: VIMSHOTTARI 1ST MD BUG ---")
# Birth: 2026-01-01 12:00:00 UTC (Current year, so age is 0)
chart, _ = calculate_chart_with_object(2026, 1, 1, 12, 0, 0, 0, "UTC", "VimshottariTest")
moon_lon = chart.planets["Moon"].degree + (chart.get_sign_index(chart.planets["Moon"].sign) * 30)

ind_lord, ind_bal = ind_vimshottari(moon_lon)
print(f"Independent - Lord: {ind_lord}, Balance: {ind_bal:.4f} years")
print(f"Engine Chart - Lord: {chart.dasha_balance['lord']}, Balance: {chart.dasha_balance['years']:.4f} years")

print(f"\nEngine current dasha at age 0 (should be missing AD/PD if bug exists): {chart.current_dasha}")

# Age 26: 
chart_adult, _ = calculate_chart_with_object(2000, 1, 1, 12, 0, 0, 0, "UTC", "AdultTest")
print(f"Engine current dasha at age 26 (Adult): {chart_adult.current_dasha}")

print("\n--- PART 4: YEAR LENGTH DIVERGENCE (365.25 vs 365.2422) ---")
d1 = 365.25
d2 = 365.2422
print(f"1 year diff: {abs(d1 - d2)} days = {abs(d1 - d2) * 24} hours")
print(f"20 year diff: {abs(d1*20 - d2*20)} days")
print(f"50 year diff: {abs(d1*50 - d2*50)} days")
print(f"80 year diff: {abs(d1*80 - d2*80)} days")
print(f"120 year diff: {abs(d1*120 - d2*120)} days")
