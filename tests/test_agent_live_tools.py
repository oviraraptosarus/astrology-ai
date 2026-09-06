import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ai_agent import ALL_TOOLS
from agent_router import SPECIALIST_TOOL_SETS, classify_intent

print(f"Total Agent Tools: {len(ALL_TOOLS)}")
for t in ALL_TOOLS:
    print(f" - Tool: {t.name:<32} | Description: {t.description[:65]}...")

queries = [
    "Is tomorrow a good day for signing a contract in Hyderabad?",
    "When will I get a promotion in my career?",
    "Is $65k a good entry price for Bitcoin?",
    "Check our marriage compatibility",
    "Why is my company facing legal trouble and hostile attacks?"
]

print("\nIntent Classification Test:")
for q in queries:
    intent = classify_intent(q, has_existing_chart=True)
    print(f" Query: '{q}' -> Intent: {intent}")
