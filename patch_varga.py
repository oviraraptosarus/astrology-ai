import re

with open('varga_engine.py', 'r') as f:
    content = f.read()

# Replace all occurrences of int(degree / span) with int((degree / span) + 1e-9)
content = re.sub(r'int\((.*? / .*?)\)', r'int((\1) + 1e-9)', content)

# But wait, there might be other int() calls. Let's make sure it's safe.
# Actually, the best way is to only target the known varga boundary logic.
# A regex like: `int\(degree / ` is safer.
# Let's revert and do that.
with open('varga_engine.py', 'w') as f:
    f.write(content)
print("Updated varga_engine.py")
