import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from boundary_fragility_engine import BoundaryFragilityEngine
from astrology_engine import calculate_nakshatra
from varga_engine import VargaEngine
from kp_engine import KPEngine

print("=" * 80)
print("PHASE 3: ADVERSARIAL DISCRETE-MATH BOUNDARY & PERTURBATION TEST SUITE")
print("=" * 80)

# Jitter offsets in degrees: 1", 10", 30", 1', 3', 5'
JITTER_OFFSETS = [
    (1.0 / 3600.0, "1 arcsecond"),
    (10.0 / 3600.0, "10 arcseconds"),
    (30.0 / 3600.0, "30 arcseconds"),
    (1.0 / 60.0, "1 arcminute"),
    (3.0 / 60.0, "3 arcminutes"),
    (5.0 / 60.0, "5 arcminutes")
]

# 1. Test Sign Boundary (Aries 0.0° / Pisces 30.0°)
print("\n[1. SIGN BOUNDARY TEST (Aries/Pisces Cusp at 0.0° / 360.0°)]")
for deg_off, label in JITTER_OFFSETS:
    # Left side (Pisces 29°59'...)
    left_lon = 360.0 - deg_off
    res_left = BoundaryFragilityEngine.evaluate_longitude_fragility(left_lon)
    
    # Right side (Aries 0°00'...)
    right_lon = 0.0 + deg_off
    res_right = BoundaryFragilityEngine.evaluate_longitude_fragility(right_lon)
    
    print(f"  Offset ±{label:<14} -> Left ({left_lon:8.5f}°): {res_left['fragility_status']} | Right ({right_lon:8.5f}°): {res_right['fragility_status']}")
    if deg_off <= (1.0 / 60.0):
        assert res_left['fragility_status'] == "HIGHLY_SENSITIVE_TO_INPUT_PRECISION"
        assert res_right['fragility_status'] == "HIGHLY_SENSITIVE_TO_INPUT_PRECISION"
print("  ✓ Sign boundary sensitivity correctly classified as HIGHLY_SENSITIVE under 1 arcmin.")

# 2. Test Nakshatra Boundary (Ashwini/Bharani at 13°20' = 13.333333°)
print("\n[2. NAKSHATRA BOUNDARY TEST (Ashwini / Bharani Cusp at 13°20')]")
nak_boundary = 360.0 / 27.0 # 13.333333333333334
for deg_off, label in JITTER_OFFSETS:
    left_lon = nak_boundary - deg_off
    nak_l, pada_l, lord_l = calculate_nakshatra(left_lon)
    
    right_lon = nak_boundary + deg_off
    nak_r, pada_r, lord_r = calculate_nakshatra(right_lon)
    
    res_l = BoundaryFragilityEngine.evaluate_longitude_fragility(left_lon)
    print(f"  Offset ±{label:<14} -> Left: {nak_l} P{pada_l} ({lord_l}) | Right: {nak_r} P{pada_r} ({lord_r}) | Fragility: {res_l['fragility_status']}")
    assert nak_l == "Ashwini" and pada_l == 4
    assert nak_r == "Bharani" and pada_r == 1
print("  ✓ Nakshatra & Pada boundary accurately transitions and flags fragility.")

# 3. Test Navamsha / Pada Boundary (3°20' = 3.333333°)
print("\n[3. NAVAMSHA BOUNDARY TEST (3°20' Varga Cusp)]")
nav_boundary = 360.0 / 108.0 # 3.3333333333333335
d9_left = VargaEngine.calc_d9_navamsha("Aries", nav_boundary - (1.0 / 3600.0))
d9_right = VargaEngine.calc_d9_navamsha("Aries", nav_boundary + (1.0 / 3600.0))
print(f"  At 3°20' ± 1 arcsecond -> Left Navamsha: {d9_left} | Right Navamsha: {d9_right}")
assert d9_left == "Aries" and d9_right == "Taurus"
print("  ✓ Navamsha flips cleanly at exact mathematical boundary.")

# 4. Test KP Sub-Lord Boundary
print("\n[4. KP SUB-LORD BOUNDARY TEST]")
# In Ashwini (0° - 13°20'), Ketu sub-lord ends at (7/120)*13.333333 = 0.7777777778° (0°46'40")
kp_sl_boundary = (7.0 / 120.0) * (360.0 / 27.0)
kp_l = KPEngine.calculate_kp_lords(kp_sl_boundary - (1.0 / 3600.0))
kp_r = KPEngine.calculate_kp_lords(kp_sl_boundary + (1.0 / 3600.0))
print(f"  At Ketu/Venus Sub-Lord Cusp (0°46'40\") ± 1 arcsecond -> Left: Sub={kp_l['sub_lord']} | Right: Sub={kp_r['sub_lord']}")
assert kp_l['sub_lord'] == "Ketu" and kp_r['sub_lord'] == "Venus"
print("  ✓ KP Sub-Lord boundary shifts deterministically without numerical drift.")

# 5. Test Gandanta Detection (Junction of Water/Fire)
print("\n[5. GANDANTA DETECTION TEST (Cancer-Leo Junction at 120°)]")
g_lon = 119.85 # 119°51' (9 arcmin before 120° Leo)
res_g = BoundaryFragilityEngine.evaluate_longitude_fragility(g_lon)
print(f"  Longitude {g_lon}° -> Is Gandanta: {res_g['is_gandanta']} | Details: {res_g['gandanta_details']}")
assert res_g['is_gandanta'] is True

print("\n" + "=" * 80)
print(">>> ALL ADVERSARIAL DISCRETE-MATH BOUNDARY TESTS PASSED (100% OK) <<<")
print("=" * 80)
