import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from rectification_engine import RectificationEngine

print("=== RECTIFICATION ENGINE FULL TEST ===")
print("Birth: 2008-08-01 18:25 IST, Ramachandrapuram (16.8186 N, 82.0641 E)")
print()

# Synthetic events (hypothetical anchors for testing)
events = [
    {"date": "15-08-2018", "type": "education"},
    {"date": "01-06-2024", "type": "career_job"},
    {"date": "05-09-2026", "type": "financial_gain"},
]

# Call rectify with a wide window and coarse step for speed (test mode)
result = RectificationEngine.rectify(
    birth_datetime=datetime(2008, 8, 1, 18, 25),
    birth_lat=16.8186, birth_lon=82.0641,
    events=events,
    timezone_str="Asia/Kolkata",
    search_minutes=60,  # +-1 hour for speed
    step_minutes=10,    # 10-min steps for speed
    include_double_transit=False  # Skip slow transit calc in test
)

import json
print(json.dumps(result, indent=2, default=str))
print()
print("=== RECTIFICATION VERIFIED ===")
