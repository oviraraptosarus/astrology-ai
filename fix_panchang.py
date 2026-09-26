import os

with open('panchangam_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
in_lock_block = False

for line in lines:
    if line.strip() == "from astronomy_core import ephemeris_lock":
        new_lines.append(line)
        continue
    if line.strip() == "ephemeris_lock.acquire()":
        new_lines.append("        with ephemeris_lock:\n")
        in_lock_block = True
        continue
    if line.strip() == "try:" and in_lock_block and "swe.set_sid_mode" in lines[lines.index(line)+1]:
        # This is the injected try we want to skip
        continue
    if line.strip() == "finally:":
        # This is the injected finally we want to skip
        in_lock_block = False
        continue
    if line.strip() == "ephemeris_lock.release()":
        continue
        
    if in_lock_block:
        new_lines.append("    " + line)
    else:
        new_lines.append(line)

with open('panchangam_engine.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("panchangam fixed")
