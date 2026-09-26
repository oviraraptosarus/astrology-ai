import re

with open('tajika_engine.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
for i, line in enumerate(lines):
    if line.strip() == "swe.set_sid_mode(Config.ayanamsha_swe_id())":
        new_lines.append("        from astronomy_core import ephemeris_lock\n")
        new_lines.append("        ephemeris_lock.acquire()\n")
        new_lines.append("        try:\n")
        new_lines.append("    " + line)
    elif line.strip() == "year_val, month_val, day_val, hour_val = swe.revjul(jd_return)":
        new_lines.append("        finally:\n")
        new_lines.append("            ephemeris_lock.release()\n")
        new_lines.append(line)
    elif line.strip() == "cusps, ascmc = swe.houses_ex(jd_return, lat, lon, b'E', swe.FLG_SIDEREAL)":
        new_lines.append(line)
        new_lines.append("        finally:\n")
        new_lines.append("            ephemeris_lock.release()\n")
    else:
        new_lines.append(line)

with open('tajika_engine.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
print("tajika patched.")
