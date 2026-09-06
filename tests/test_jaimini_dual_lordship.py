import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from astrology_engine import calculate_chart_with_object
from jaimini_chara_dasha_engine import JaiminiCharaDashaEngine

print("=" * 70)
print("TEST: JAIMINI DUAL-LORDSHIP RESOLUTION (SCORPIO & AQUARIUS)")
print("=" * 70)

chart_user, _ = calculate_chart_with_object(2008, 8, 1, 18, 25, 16.8186, 82.0641, "Asia/Kolkata", "User")

# Scorpio lord test
scorpio_lord, scorpio_p = JaiminiCharaDashaEngine.resolve_jaimini_lord("Scorpio", chart_user)
print(f"Scorpio Co-Lord Selection: {scorpio_lord} (in {scorpio_p.sign} with {len(scorpio_p.conjunct_with)} planets)")
assert scorpio_lord == "Ketu", "Ketu should be chosen over Mars due to more conjunctions (3 vs 2)"

# Aquarius lord test
aquarius_lord, aquarius_p = JaiminiCharaDashaEngine.resolve_jaimini_lord("Aquarius", chart_user)
print(f"Aquarius Co-Lord Selection: {aquarius_lord} (in {aquarius_p.sign} with {len(aquarius_p.conjunct_with)} planets)")
assert aquarius_lord == "Saturn", "Saturn should be chosen over Rahu due to more conjunctions (2 vs 0)"

# Calculate sign dasha years
scorpio_years = JaiminiCharaDashaEngine.calculate_sign_dasha_years("Scorpio", chart_user)
aquarius_years = JaiminiCharaDashaEngine.calculate_sign_dasha_years("Aquarius", chart_user)

print(f"Scorpio Dasha Duration: {scorpio_years} years (Calculated from Ketu in Cancer)")
print(f"Aquarius Dasha Duration: {aquarius_years} years (Calculated from Saturn in Leo)")

assert scorpio_years == 8, f"Expected 8 years, got {scorpio_years}"
assert aquarius_years == 6, f"Expected 6 years, got {aquarius_years}"
print("\n✓ Jaimini Dual-Lordship resolution accurately calculates dasha years according to classical rules.")
