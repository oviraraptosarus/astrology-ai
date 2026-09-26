import re

with open('panchangam_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the one in __init__
content = re.sub(
    r'    def __init__\(self\):\n        swe\.set_sid_mode\(Config\.ayanamsha_swe_id\(\)\)\n',
    r'    def __init__(self):\n        pass\n',
    content
)

# Replace the beginning of calculate_full_panchang to inject lock
old_start = """        # 1. Sunrise & Sunset for the Day
        # We find the sunrise preceding or on this day with Polar Fallback
        jd_midnight = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 0.0)"""

new_start = """        from astronomy_core import ephemeris_lock
        with ephemeris_lock:
            swe.set_sid_mode(Config.ayanamsha_swe_id())
            # 1. Sunrise & Sunset for the Day
            # We find the sunrise preceding or on this day with Polar Fallback
            jd_midnight = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 0.0)"""

content = content.replace(old_start, new_start)

# Now we have to indent everything inside the with block until the end of the SWE calls.
# Actually, wait. swe.calc_ut happens at line 148, but the whole function calculates stuff based on it.
# Rather than indenting the rest of the 200 lines function, let's just acquire and release the lock around the SWISSEPH calls.
# So instead of `with ephemeris_lock:` wrapping everything, let's do:

# Wait, `ephemeris_lock` is an `RLock`.
# `with ephemeris_lock:` requires block indentation.
# A simpler way to avoid re-indenting 200 lines:

new_start2 = """        from astronomy_core import ephemeris_lock
        ephemeris_lock.acquire()
        try:
            swe.set_sid_mode(Config.ayanamsha_swe_id())
            # 1. Sunrise & Sunset for the Day
            # We find the sunrise preceding or on this day with Polar Fallback
            jd_midnight = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 0.0)"""

content = content.replace(new_start, new_start2)

# Now find where the SWE calls end. Line 149 is `moon_res, _ = swe.calc_ut(jd_now, swe.MOON, flags)`
old_end = """        sun_lon = sun_res[0] % 360.0
        moon_lon = moon_res[0] % 360.0"""

new_end = """        finally:
            ephemeris_lock.release()

        sun_lon = sun_res[0] % 360.0
        moon_lon = moon_res[0] % 360.0"""

content = content.replace(old_end, new_end)

with open('panchangam_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("panchangam_engine.py patched.")
