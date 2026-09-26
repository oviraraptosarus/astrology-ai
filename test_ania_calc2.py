import sys
import json
import inspect
sys.path.insert(0, r"E:\ASTROLOGY AI")

import astrology_engine

print("calculate_full_chart signature:", inspect.signature(astrology_engine.calculate_full_chart))

# Let's run calculate_full_chart
try:
    chart_data = astrology_engine.calculate_full_chart(
        dob="2008-04-05",
        tob="06:15:00",
        lat=50.3480,
        lon=18.9328,
        tz=2.0
    )
    with open("E:/ASTROLOGY AI/ania_full_chart.json", "w", encoding="utf-8") as f:
        json.dump(chart_data, f, indent=2, default=str)
    print("Full chart successfully dumped to ania_full_chart.json")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
