import re

with open('tajaka_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if line.strip() == "swe.set_sid_mode(Config.ayanamsha_swe_id())":
        new_lines.append("        from astronomy_core import ephemeris_lock\n")
        new_lines.append("        ephemeris_lock.acquire()\n")
        new_lines.append("        try:\n")
        new_lines.append("    " + line)
    elif line.strip() == "return return_jd":
        new_lines.append("        finally:\n")
        new_lines.append("            ephemeris_lock.release()\n")
        new_lines.append(line)
    elif line.strip() == "ret_utc = swe.jdut1_to_utc(return_jd)":
        new_lines.append("        finally:\n")
        new_lines.append("            ephemeris_lock.release()\n")
        new_lines.append(line)
    else:
        new_lines.append(line)

with open('tajaka_engine.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("tajaka patched.")
