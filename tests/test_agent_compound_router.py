import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from agent_router import classify_intent, get_specialist_tools, SPECIALIST_TOOL_SETS

print("=" * 75)
print("TEST: PHASE 14 MULTI-DOMAIN COMPOUND INTENT ROUTING")
print("=" * 75)

# 1. Single Intent Queries
assert classify_intent("Calculate my birth chart for 1990-01-15") == "BIRTH_CHART"
assert classify_intent("Are we compatible for marriage?") == "COMPATIBILITY"
assert classify_intent("When will I get married and what is the best muhurta?") == "TIMING"
assert classify_intent("How is my current Sade Sati transit affecting me?") == "TRANSIT"
print("✓ Single intent queries accurately routed to specialist domains.")

# 2. Compound Multi-Domain Queries
q1 = "Are we compatible, and when will we get married next year?"
i1 = classify_intent(q1)
print(f"Query: '{q1}' -> Classified Intent: {i1}")
assert i1 == "COMPOUND", f"Expected COMPOUND, got {i1}"

q2 = "Show my natal chart and tell me how my Sade Sati transit affects my career timing."
i2 = classify_intent(q2)
print(f"Query: '{q2}' -> Classified Intent: {i2}")
assert i2 == "COMPOUND", f"Expected COMPOUND, got {i2}"

# 3. Toolset Preservation Verification
compound_tools = SPECIALIST_TOOL_SETS["COMPOUND"]
print(f"\nCompound Specialist Tool Count: {len(compound_tools)}")
assert "check_compatibility" in compound_tools
assert "scan_forward_event_timing" in compound_tools
assert "get_birth_chart" in compound_tools
assert "retrieve_astrological_insights" in compound_tools
print("✓ Compound specialist tools preserve full multi-domain execution without dropping tools.")

print("\n" + "=" * 75)
print(">>> ALL AGENT ROUTER COMPOUND INTENT TESTS PASSED (100% OK) <<<")
print("=" * 75)
