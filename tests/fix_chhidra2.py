import sys, os

lon_path = "E:/ASTROLOGY AI/longevity_engine.py"
with open(lon_path, "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    'chhidra = sp.calculate_64th_navamsha_from_moon().get("lord", "Unknown")',
    'chhidra = sp.calculate_64th_navamsha().get("from_moon", {}).get("lord", "Unknown") if isinstance(sp.calculate_64th_navamsha().get("from_moon"), dict) else sp.calculate_64th_navamsha().get("lord", "Unknown")'
)

with open(lon_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Fixed.")
