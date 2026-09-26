import sys
import json

# Add project root
sys.path.insert(0, r"E:\ASTROLOGY AI")

try:
    import astrology_engine
    print("astrology_engine imported successfully")
except Exception as e:
    print(f"Error importing astrology_engine: {e}")
    sys.exit(1)

# Ania's birth details:
# April 5, 2008, 06:15:00 am, Bytom, Poland (18.9667 E, 50.3500 N, timezone UTC+2)
# Let's check available functions in astrology_engine
print("Engine functions/classes:", [attr for attr in dir(astrology_engine) if not attr.startswith("__")][:30])

# Let's run a chart calculation if standard interface exists
try:
    # Let's see what signature calculate_chart or similar has
    if hasattr(astrology_engine, "calculate_chart"):
        chart = astrology_engine.calculate_chart(
            year=2008, month=4, day=5,
            hour=6, minute=15, second=0,
            lat=50.3480, lon=18.9328,
            tz_offset=2.0
        )
        print("Chart calculated successfully!")
        print("Planets/Lagna summary:")
        for k, v in chart.items():
            if isinstance(v, (dict, list, str, int, float)):
                print(f"  {k}: {str(v)[:150]}")
except Exception as e:
    print(f"Error calculating chart: {e}")
