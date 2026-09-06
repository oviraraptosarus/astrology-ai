
import sys, os
sys.path.insert(0, "E:/ASTROLOGY AI")
from user_memory_engine import ContextMemoryEngine, UserContextProfile

engine = ContextMemoryEngine("test_memory.db")
profile = engine.get_or_create_profile("test_user_1", "1990-01-01")

engine.record_user_correction("test_user_1", "I just got divorced after 5 years of being married. I'm taking time to be single.", profile)

print("Status:", profile.marital_status)

engine.record_user_correction("test_user_1", "I don't have children anymore after the accident.", profile)
print("Children:", profile.has_children)

os.remove("test_memory.db")
