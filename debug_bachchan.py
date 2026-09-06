
import sys
sys.path.insert(0, "E:/ASTROLOGY AI")

from datetime import datetime
import pytz
from astrology_engine import calculate_chart_with_object
from event_analysis import EventPredictionEngine

chart_ab, _ = calculate_chart_with_object(
    1942, 10, 11, 16, 0, 25.4358, 81.8463, "Asia/Kolkata", "Amitabh Bachchan"
)
engine = EventPredictionEngine(chart_ab)
res = engine.analyze_event("Will I achieve massive fame and career success as a public figure?", datetime(1975, 6, 1, tzinfo=pytz.utc))

print("=== Bachchan Career Analysis Debug ===")
print("Domain:", res.domain)
print("Natal Promise Status:", res.natal_promise["status"])
print("Supporting Evidence count:", len(res.natal_promise["supporting_evidence"]))
for e in res.natal_promise["supporting_evidence"]:
    print("  SUPPORT:", e.get("subject"), "|", e.get("source_rule"), "|", e.get("reason","")[:80])
print("Contradicting Evidence count:", len(res.natal_promise["contradicting_evidence"]))
for e in res.natal_promise["contradicting_evidence"]:
    print("  CONTRA:", e.get("subject"), "|", e.get("source_rule"), "|", e.get("reason","")[:80])
print("Timing Status:", res.activation["timing_status"])
print("Convergence:", res.convergence)
print("LLM Guidance:", res.llm_guidance)
