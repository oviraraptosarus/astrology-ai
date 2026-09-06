
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from astrology_engine import calculate_chart_with_object
from strength_engine import StrengthEngine

chart, _ = calculate_chart_with_object(1980, 1, 1, 12, 0, 0, 0, "UTC", "Test")

mercury = chart.planets["Mercury"]
sun = chart.planets["Sun"]

print(f"Sun Longitude: {sun.degree + (chart.get_sign_index(sun.sign) * 30):.2f}")
print(f"Mercury Longitude: {mercury.degree + (chart.get_sign_index(mercury.sign) * 30):.2f}")
print(f"Mercury Cheshta Bala: {mercury.shadbala['cheshta_bala']} Virupas")
print("Expected max for Cheshta Bala is 60 Virupas.")
