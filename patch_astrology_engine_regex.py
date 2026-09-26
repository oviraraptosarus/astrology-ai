import re

with open('astrology_engine.py', 'r') as f:
    content = f.read()

# 1. Imports
if 'from astronomy_core import ephemeris_lock' not in content:
    content = content.replace('from varga_engine import VargaEngine', 
                              'from varga_engine import VargaEngine\nfrom astronomy_core import ephemeris_lock\nfrom dasha_engine import DashaEngine')

# 2. Lock & Config
# Wrap everything from `swe.set_sid_mode(Config.ayanamsha_swe_id())` to `chart.current_transits = live_transits` in the lock!
# Actually, the remedy engine doesn't need the lock, but it doesn't hurt.
# Let's just indent everything.
start_str = "    swe.set_sid_mode(Config.ayanamsha_swe_id())"
end_str = "    # --- Integration of Numerology and Western Astrology ---"

import string
idx1 = content.find(start_str)
idx2 = content.find(end_str)

if idx1 != -1 and idx2 != -1:
    block = content[idx1:idx2]
    # indent the block
    indented_block = "\n".join("    " + line if line.strip() else line for line in block.split("\n"))
    indented_block = "    with ephemeris_lock:\n" + indented_block[4:] # replace the first indentation with the with statement
    
    # House config fix
    indented_block = indented_block.replace("        try:\n            cusps, ascmc = swe.houses_ex(jd, lat, lon, b'O', flags)", "        hs = b'W' if Config.HOUSE_SYSTEM == \"whole_sign\" else b'O'\n        try:\n            cusps, ascmc = swe.houses_ex(jd, lat, lon, hs, flags)")
    
    # Dasha fix
    dasha_start = "        # 4. Detailed Dasha (Vimshottari)"
    dasha_end = """            "Mahadasha_End": dec_to_ym(birth_dec + md_end_age)\n        }"""
    pattern = re.compile(re.escape(dasha_start) + r'.*?' + re.escape(dasha_end), re.DOTALL)

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
        }"""
    indented_block = re.sub(pattern, dasha_replacement, indented_block)

    content = content[:idx1] + indented_block + content[idx2:]

    # Also update remedy call for dashas
    content = content.replace('r_engine.generate_dasha_remedies(curr_dasha, antardasha)', 'r_engine.generate_dasha_remedies(dashas.get("Mahadasha", ""), dashas.get("Antardasha", ""))')

# 3. Muhurta lock
muhurta_pattern = re.compile(r'def find_muhurta\(start_year, start_month, start_day, lat, lon\):\s+from datetime import timedelta\s+swe.set_sid_mode\(Config.ayanamsha_swe_id\(\)\)\s+flags = swe.FLG_SIDEREAL \| swe.FLG_SPEED\s+start_dt = datetime\(start_year, start_month, start_day\)\s+best_dates = \[\]\s+# Scan next 30 days\s+for i in range\(30\):\s+check_dt = start_dt \+ timedelta\(days=i\)\s+jd = swe.julday\(check_dt.year, check_dt.month, check_dt.day, 12.0\)\s+res_moon, _ = swe.calc_ut\(jd, swe.MOON, flags\)', re.DOTALL)

new_muhurta = """def find_muhurta(start_year, start_month, start_day, lat, lon):
    from datetime import timedelta
    start_dt = datetime(start_year, start_month, start_day)
    best_dates = []
    
    with ephemeris_lock:
        swe.set_sid_mode(Config.ayanamsha_swe_id())
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
        
        # Scan next 30 days
        for i in range(30):
            check_dt = start_dt + timedelta(days=i)
            jd = swe.julday(check_dt.year, check_dt.month, check_dt.day, 12.0)
            
            res_moon, _ = swe.calc_ut(jd, swe.MOON, flags)"""

content = re.sub(muhurta_pattern, new_muhurta, content)

with open('astrology_engine.py', 'w') as f:
    f.write(content)
print("Updated astrology_engine.py")
