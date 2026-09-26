import re

with open('astrology_engine.py', 'r') as f:
    lines = f.readlines()

new_lines = []
in_calc = False
for i, line in enumerate(lines):
    # 1. Imports
    if line.startswith('from varga_engine import VargaEngine'):
        new_lines.append('from varga_engine import VargaEngine\n')
        new_lines.append('from astronomy_core import ephemeris_lock\n')
        new_lines.append('from dasha_engine import DashaEngine\n')
        continue
    
    # 2. Function start
    if line.startswith('def calculate_chart_with_object('):
        in_calc = True
        new_lines.append(line)
        continue
    
    if in_calc:
        if line.strip() == 'swe.set_sid_mode(Config.ayanamsha_swe_id())':
            new_lines.append('    with ephemeris_lock:\n')
            new_lines.append('        swe.set_sid_mode(Config.ayanamsha_swe_id())\n')
        elif line.startswith('    # --- Integration of Numerology'):
            in_calc = False
            new_lines.append(line)
        elif line.startswith('    try:') and 'swe.houses_ex' in lines[i+1]:
            new_lines.append('        hs = b\'W\' if Config.HOUSE_SYSTEM == "whole_sign" else b\'O\'\n')
            new_lines.append('        ' + line.strip() + '\n')
        elif 'b\'O\'' in line and 'swe.houses_ex' in line:
            new_lines.append('            cusps, ascmc = swe.houses_ex(jd, lat, lon, hs, flags)\n')
        elif line.strip() == '' or line.startswith('    #') and not line.startswith('    # 4. Detailed Dasha'):
            new_lines.append('    ' + line)
        else:
            if line.startswith('    '):
                # We need to skip the inline dasha calculation
                if line.startswith('    # 4. Detailed Dasha (Vimshottari)'):
                    # We inject our code and then skip lines until the end of dashas
                    dasha_replacement = """        # 4. Detailed Dasha (Vimshottari) via DashaEngine
        moon_lon = planet_lons["Moon"]
        timeline = DashaEngine.calculate_vimshottari_timeline(utc_dt, moon_lon, num_levels=3)
        curr_dasha_full = DashaEngine.get_current_dasha(timeline, datetime.now(pytz.utc))
        
        # Format dashas for backwards compatibility
        dashas = {
            "Mahadasha": curr_dasha_full.get("MD", {}).get("lord", ""),
            "Antardasha": curr_dasha_full.get("AD", {}).get("lord", ""),
            "Pratyantardasha": curr_dasha_full.get("PD", {}).get("lord", ""),
            "Mahadasha_Start": curr_dasha_full.get("MD", {}).get("start_date", utc_dt).strftime("%Y-%m"),
            "Mahadasha_End": curr_dasha_full.get("MD", {}).get("end_date", utc_dt).strftime("%Y-%m")
        }\n"""
                    new_lines.append(dasha_replacement)
                    # Skip logic
                    skip = True
                    continue
                if locals().get('skip', False):
                    if line.startswith('    }'):
                        skip = False
                    continue
                
                # Normal line to indent
                new_lines.append('    ' + line)
            else:
                new_lines.append(line)
    else:
        # Also fix find_muhurta lock
        if line.strip() == 'swe.set_sid_mode(Config.ayanamsha_swe_id())' and 'def find_muhurta' in ''.join(lines[i-5:i]):
            new_lines.append('    with ephemeris_lock:\n')
            new_lines.append('        ' + line.strip() + '\n')
        elif line.startswith('    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED') and 'def find_muhurta' in ''.join(lines[i-6:i+2]):
            new_lines.append('        ' + line.strip() + '\n')
        elif line.startswith('    for i in range(30):') and 'def find_muhurta' in ''.join(lines[i-15:i]):
            # Indent the loop
            new_lines.append('        ' + line.strip() + '\n')
            # I will just write a custom block for find_muhurta instead of doing it line by line
            pass
        else:
            new_lines.append(line)

with open('astrology_engine.py', 'w') as f:
    f.writelines(new_lines)
print("Updated astrology_engine.py")
