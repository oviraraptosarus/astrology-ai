import sys
import json
import os
sys.path.insert(0, r"E:\ASTROLOGY AI")

import astrology_engine

# Calculate full chart for Ania
# DOB: 2008-04-05, 06:15, Bytom (50.3480 N, 18.9328 E, tz='Europe/Warsaw')
chart_data = astrology_engine.calculate_full_chart(
    year=2008, month=4, day=5,
    hour=6, minute=15,
    lat=50.3480, lon=18.9328,
    tz_name='Europe/Warsaw',
    name='Ania'
)

with open("E:/ASTROLOGY AI/ania_full_chart.json", "w", encoding="utf-8") as f:
    json.dump(chart_data, f, indent=2, default=str)

print("Saved ania_full_chart.json")

# Let's inspect what other modules exist and can be run
modules_to_try = [
    "advanced_avasthas",
    "deep_psych_dasha",
    "deep_psych_audit",
    "ashtakavarga_engine",
    "bhrigu_nandi_nadi_engine",
    "compatibility_engine"
]

results = {}
for mod_name in modules_to_try:
    try:
        mod = __import__(mod_name)
        print(f"Loaded module: {mod_name}")
        results[mod_name] = [attr for attr in dir(mod) if not attr.startswith("__")]
    except Exception as e:
        print(f"Could not load {mod_name}: {e}")

print("Available module attributes:", results)
