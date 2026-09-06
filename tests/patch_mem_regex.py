import sys, os, re

mem_path = "E:/ASTROLOGY AI/user_memory_engine.py"
with open(mem_path, "r", encoding="utf-8") as f:
    code = f.read()

old_correction_logic = """        if "married" in stmt_lower:
            if "already married" in stmt_lower or "married in" in stmt_lower or "married on" in stmt_lower:
                profile.marital_status = "married"
                extracted["marital_status"] = "married"
            elif "not married" in stmt_lower or "single" in stmt_lower or "unmarried" in stmt_lower:
                profile.marital_status = "single"
                extracted["marital_status"] = "single"

        if "business" in stmt_lower or "startup" in stmt_lower or "company" in stmt_lower:
            profile.career_type = "business_owner"
            extracted["career_type"] = "business_owner"

        if "kid" in stmt_lower or "child" in stmt_lower:
            if "no kids" in stmt_lower or "don't have child" in stmt_lower or "no children" in stmt_lower:
                profile.has_children = False
                extracted["has_children"] = False
            elif "have kids" in stmt_lower or "have a son" in stmt_lower or "have a daughter" in stmt_lower:
                profile.has_children = True
                extracted["has_children"] = True"""

new_correction_logic = """        # Flexible Regex Extraction
        if re.search(r'\\b(married|wife|husband|wedding)\\b', stmt_lower):
            if re.search(r'\\b(already married|married in|married on|married since|got married)\\b', stmt_lower):
                profile.marital_status = "married"
                extracted["marital_status"] = "married"
            elif re.search(r'\\b(not married|single|unmarried|bachelor)\\b', stmt_lower):
                profile.marital_status = "single"
                extracted["marital_status"] = "single"

        if re.search(r'\\b(business|startup|company|firm|enterprise|founder|owner|actor|artist|director|freelancer)\\b', stmt_lower):
            profile.career_type = "business_owner" if not re.search(r'\\b(student|college)\\b', stmt_lower) else "student"
            extracted["career_type"] = profile.career_type

        if re.search(r'\\b(kid|kids|child|children|son|daughter)\\b', stmt_lower):
            if re.search(r'\\b(no kids|don\'t have|no child|no children|without kids)\\b', stmt_lower):
                profile.has_children = False
                extracted["has_children"] = False
            else:
                profile.has_children = True
                extracted["has_children"] = True"""

code = code.replace(old_correction_logic, new_correction_logic)
with open(mem_path, "w", encoding="utf-8") as f:
    f.write(code)

print("user_memory_engine.py regex matcher updated.")
