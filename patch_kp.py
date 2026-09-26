import re

with open('kp_engine.py', 'r') as f:
    lines = f.readlines()

new_lines = []
in_lock = False
for i, line in enumerate(lines):
    if line.startswith('        swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)'):
        new_lines.append('        with ephemeris_lock:\n')
        new_lines.append('            swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)\n')
        in_lock = True
        continue
    
    if in_lock:
        if line.startswith('    @staticmethod'):
            in_lock = False
            new_lines.append(line)
        elif line.strip() == '':
            new_lines.append(line)
        elif line.startswith('        '):
            new_lines.append('    ' + line) # Add 4 spaces
        else:
            # We reached the end of the method
            in_lock = False
            new_lines.append(line)
    else:
        new_lines.append(line)

with open('kp_engine.py', 'w') as f:
    f.writelines(new_lines)
print("Updated kp_engine.py")
