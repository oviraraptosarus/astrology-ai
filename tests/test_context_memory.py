import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from user_memory_engine import ContextMemoryEngine

mem = ContextMemoryEngine()

print("--- SCENARIO A: 18-Year Old Student ---")
prof_18 = mem.get_or_create_profile(user_id="user_student_18", birth_date_str="2008-08-01")
mem.record_user_correction("user_student_18", "I am an 18 year old student in college", prof_18)

cal_7h = mem.calibrate_domain_prediction("MARRIAGE", {}, prof_18)
print(f"Age: {prof_18.current_age} | Status: {prof_18.career_type}")
print(f"Raw Request: MARRIAGE -> Calibrated: {cal_7h['calibrated_archetype']}")
print(f"Guidance: {cal_7h['guidance_note']}")

print("\n--- SCENARIO B: 51-Year Old Married Business Owner (May 6, 1975) ---")
prof_mature = mem.get_or_create_profile(user_id="user_owner_1975", birth_date_str="1975-05-06")
mem.record_user_correction("user_owner_1975", "I am already married since 2001 and run my own business", prof_mature)

cal_7h_b = mem.calibrate_domain_prediction("MARRIAGE", {}, prof_mature)
cal_10h_b = mem.calibrate_domain_prediction("CAREER", {}, prof_mature)

print(f"Age: {prof_mature.current_age} | Status: {prof_mature.marital_status} | Career: {prof_mature.career_type}")
print(f"Raw Request: MARRIAGE -> Calibrated: {cal_7h_b['calibrated_archetype']}")
print(f"Guidance: {cal_7h_b['guidance_note']}")
print(f"Raw Request: CAREER   -> Calibrated: {cal_10h_b['calibrated_archetype']}")
print(f"Guidance: {cal_10h_b['guidance_note']}")
