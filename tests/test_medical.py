import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from astrology_engine import calculate_chart_with_object
from medical_astrology_engine import MedicalAstrologyEngine

chart_ab, _ = calculate_chart_with_object(1942, 10, 11, 16, 0, 25.4358, 81.8463, "Asia/Kolkata", 0)
med_eng = MedicalAstrologyEngine(chart_ab)
diag = med_eng.diagnose_health_profile()

print("=" * 70)
print("MEDICAL ASTROLOGY DIAGNOSTIC REPORT: AMITABH BACHCHAN")
print("=" * 70)
print(f"Primary Dosha : {diag['primary_ayurvedic_dosha']}")
print(f"Surgical Risk : {diag['surgical_trauma_risk']}")
print("\nSurgical & Acute Trauma Indicators:")
for ind in diag['surgical_indicators']:
    print(f"  - {ind}")

print("\nDusthana Anatomical Zones:")
for d in diag['dusthana_anatomical_vulnerabilities']:
    print(f"  House {d['house']} ({d['sign']}): {d['anatomical_zone']}")
    print(f"    Planets: {d['planets_present']}")
    print(f"    Vulnerabilities: {d['potential_vulnerabilities']}")
