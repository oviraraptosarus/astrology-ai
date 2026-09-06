import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from astrology_engine import calculate_chart_with_object
from event_analysis import EventPredictionEngine

lat, lon = 16.8667, 81.9333
chart, payload = calculate_chart_with_object(1975, 5, 6, 7, 15, lat, lon, "Asia/Kolkata", 0)
engine = EventPredictionEngine(chart)

now = datetime.now()

print("==================================================")
print("1. MARRIAGE / WIFE")
res_m = engine.analyze_event("How is my relationship with my wife?", now)
print("Domain:", res_m.domain)
print("Natal Promise Confidence:", res_m.natal_promise["status"])
print("Convergence:", res_m.convergence)
print("LLM Guidance:", res_m.llm_guidance)
print("Supporting Evidence:", [e.get("reason", e) if isinstance(e, dict) else e for e in res_m.natal_promise["supporting_evidence"]])
print("Contradicting Evidence:", [e.get("reason", e) if isinstance(e, dict) else e for e in res_m.natal_promise["contradicting_evidence"]])

print("\n==================================================")
print("2. BUSINESS / CAREER")
res_b = engine.analyze_event("How will my business progress?", now)
print("Domain:", res_b.domain)
print("Natal Promise Confidence:", res_b.natal_promise["status"])
print("Convergence:", res_b.convergence)
print("LLM Guidance:", res_b.llm_guidance)
print("Supporting Evidence:", [e.get("reason", e) if isinstance(e, dict) else e for e in res_b.natal_promise["supporting_evidence"]])
print("Contradicting Evidence:", [e.get("reason", e) if isinstance(e, dict) else e for e in res_b.natal_promise["contradicting_evidence"]])

print("\n==================================================")
print("3. CHILDREN")
res_c = engine.analyze_event("How is my relationship with children?", now)
print("Domain:", res_c.domain)
print("Natal Promise Confidence:", res_c.natal_promise["status"])
print("Convergence:", res_c.convergence)
print("LLM Guidance:", res_c.llm_guidance)
print("Supporting Evidence:", [e.get("reason", e) if isinstance(e, dict) else e for e in res_c.natal_promise["supporting_evidence"]])
print("Contradicting Evidence:", [e.get("reason", e) if isinstance(e, dict) else e for e in res_c.natal_promise["contradicting_evidence"]])
