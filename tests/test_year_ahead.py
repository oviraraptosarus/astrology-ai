import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from datetime import datetime
from astrology_engine import calculate_full_chart
from event_analysis import EventPredictionEngine
from deterministic_formatter import format_fallback_response

from vedic_models import Chart

print("Running Year Ahead End-To-End Test")

# Sample chart
chart_dict = calculate_full_chart(
    year=1990, month=5, day=15, 
    hour=14, minute=30, 
    lat=34.0522, lon=-118.2437
)

chart = Chart.from_dict(chart_dict.get("Basic_Chart", {}))
chart.current_dasha = chart_dict.get("Current_Dasha", {})
chart.current_transits = chart_dict.get("Live_Transits_Gochar", {})

engine = EventPredictionEngine(chart)

print("\n--- Testing Target Period: NOW ---")
analysis_now = engine.analyze_event("What does the next year hold for me?", datetime.now())

# Because of the changes, this returns a YearAheadAnalysis object
response_now = format_fallback_response(analysis_now.to_dict())

print(response_now)

print("\n--- Testing Target Period: +5 Years ---")
from datetime import timedelta
future_date = datetime.now() + timedelta(days=365*5)
analysis_future = engine.analyze_event("What does the next year hold for me?", future_date)

timing_now = analysis_now.timing
timing_future = analysis_future.timing

print(f"Timing Now: {timing_now}")
print(f"Timing Future: {timing_future}")

if timing_now != timing_future:
    print("\n[SUCCESS]: The deterministic responses are different when the year changes.")
else:
    print("\n[FAILURE]: The responses are identical despite a 5-year difference.")
    import sys
    sys.exit(1)
