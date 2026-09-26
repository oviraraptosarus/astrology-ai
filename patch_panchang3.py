import re

with open('panchangam_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

content = re.sub(
    r'    def __init__\(self\):\n        swe\.set_sid_mode\(Config\.ayanamsha_swe_id\(\)\)\n',
    r'    def __init__(self):\n        pass\n',
    content
)

old_block = """        jd_now = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_dec)

        # 1. Sunrise & Sunset for the Day"""

new_block = """        jd_now = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_dec)

        from astronomy_core import ephemeris_lock
        ephemeris_lock.acquire()
        swe.set_sid_mode(Config.ayanamsha_swe_id())
        
        # 1. Sunrise & Sunset for the Day"""

content = content.replace(old_block, new_block)

old_end = """        sun_lon = sun_res[0] % 360.0
        moon_lon = moon_res[0] % 360.0"""

new_end = """        ephemeris_lock.release()

        sun_lon = sun_res[0] % 360.0
        moon_lon = moon_res[0] % 360.0"""

content = content.replace(old_end, new_end)

with open('panchangam_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("panchangam patched cleanly")
