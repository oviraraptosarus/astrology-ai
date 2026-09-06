import sys, os

mem_path = "E:/ASTROLOGY AI/user_memory_engine.py"
with open(mem_path, "r", encoding="utf-8") as f:
    code = f.read()

code = code.replace(
    r"if re.search(r'\b(no kids|don't have|no child|no children|without kids)\b', stmt_lower):",
    r'if re.search(r"\b(no kids|don\'t have|no child|no children|without kids)\b", stmt_lower):'
)

with open(mem_path, "w", encoding="utf-8") as f:
    f.write(code)

print("Quote syntax fixed.")
