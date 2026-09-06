import sys, os

mem_path = "E:/ASTROLOGY AI/user_memory_engine.py"
with open(mem_path, "r", encoding="utf-8") as f:
    code = f.read()

if "import re" not in code:
    code = "import re\n" + code
    with open(mem_path, "w", encoding="utf-8") as f:
        f.write(code)

print("import re added.")
