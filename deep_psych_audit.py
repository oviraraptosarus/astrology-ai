import sys, os
sys.path.insert(0, r"E:/ASTROLOGY AI")
import datetime
import swisseph as swe
from astrology_engine import calculate_chart_with_object
from forward_timing_scanner import ZODIAC_SIGNS

B_BIRTH = (2008, 4, 5, 6, 15, 50.348, 18.916, "Europe/Warsaw")
chart_b, payload_b = calculate_chart_with_object(*B_BIRTH, name="Her")

A_BIRTH = (2008, 8, 1, 18, 25, 16.8186, 82.0641, "Asia/Kolkata")
chart_a, payload_a = calculate_chart_with_object(*A_BIRTH, name="Him")

print("=== HER PLANETARY METRICS ===")
for p, obj in chart_b.planets.items():
    pada = int((obj.degree % (30.0 / 9.0)) / (30.0 / 36.0)) + 1 # rough or standard pada calculation
    abs_lon = ZODIAC_SIGNS.index(obj.sign) * 30.0 + obj.degree
    nak_idx = int(abs_lon / (360.0 / 27.0))
    pada_exact = int((abs_lon % (360.0 / 27.0)) / (360.0 / 108.0)) + 1
    print(f"{p:8s}: {obj.sign:11s} {obj.degree:7.4f}° | Nak: {obj.nakshatra:18s} (Pada {pada_exact}) | House: {obj.house}")

print("\n=== HIS PLANETARY METRICS ===")
for p, obj in chart_a.planets.items():
    abs_lon = ZODIAC_SIGNS.index(obj.sign) * 30.0 + obj.degree
    pada_exact = int((abs_lon % (360.0 / 27.0)) / (360.0 / 108.0)) + 1
    print(f"{p:8s}: {obj.sign:11s} {obj.degree:7.4f}° | Nak: {obj.nakshatra:18s} (Pada {pada_exact}) | House: {obj.house}")

print(f"\nHer Lagna: {chart_b.ascendant_sign} {chart_b.ascendant_degree:.4f}°")
print(f"His Lagna: {chart_a.ascendant_sign} {chart_a.ascendant_degree:.4f}°")

