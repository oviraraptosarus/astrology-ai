import re

with open('astrology_engine.py', 'r') as f:
    content = f.read()

# 1. Imports
if 'from astronomy_core import ephemeris_lock' not in content:
    content = content.replace('from varga_engine import VargaEngine', 
                              'from varga_engine import VargaEngine\nfrom astronomy_core import ephemeris_lock\nfrom dasha_engine import DashaEngine')

# 2. Lock & Config
old_block = """    swe.set_sid_mode(Config.ayanamsha_swe_id())
    
    # Setup time
    local_tz = pytz.timezone(tz_name)
    local_dt = local_tz.localize(datetime(year, month, day, hour, minute))
    utc_dt = local_dt.astimezone(pytz.utc)
    
    hour_dec = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
    jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_dec)
    # Topocentric positions were removed: Vedic astrology (JHora/Parashara) uses
    # GEOCENTRIC longitudes. Topocentric parallax shifts the Moon by up to ~1°,
    # corrupting the nakshatra and the entire Vimshottari dasha timeline.
    flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    
    # 1. Base Planets & Relational Graph
    from vedic_models import Chart, Planet
    
    # Ascendant
    # b'O' is Porphyry (equivalent to Sri Pati commonly used in Vedic Bhava Chalit)
    # High-latitude fallback: Equal house ('E') if polar latitudes fail Porphyry
    try:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'O', flags)
    except Exception:
        cusps, ascmc = swe.houses_ex(jd, lat, lon, b'E', flags)"""

new_block = """    with ephemeris_lock:
        swe.set_sid_mode(Config.ayanamsha_swe_id())
        local_tz = pytz.timezone(tz_name)
        local_dt = local_tz.localize(datetime(year, month, day, hour, minute))
        utc_dt = local_dt.astimezone(pytz.utc)
        hour_dec = utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_dec)
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
        from vedic_models import Chart, Planet
        
        hs = b'W' if Config.HOUSE_SYSTEM == "whole_sign" else b'O'
        try:
            cusps, ascmc = swe.houses_ex(jd, lat, lon, hs, flags)
        except Exception:
            cusps, ascmc = swe.houses_ex(jd, lat, lon, b'E', flags)"""

content = content.replace(old_block, new_block)

# 3. Planet loop also needs to be indented to be inside the lock
# Actually, the lock needs to cover up to the end of the `for name, p_id in PLANETS.items():` loop.
# Let's just wrap `swe.calc_ut` in a lock directly for the planet loop, to make it simple.
# Wait, if we closed `with ephemeris_lock` above, we can just wrap the `swe.calc_ut` in the loop.
# Let's fix that.
old_loop = """        res, _ = swe.calc_ut(jd, p_id, flags)"""
new_loop = """        with ephemeris_lock:
            res, _ = swe.calc_ut(jd, p_id, flags)"""
content = content.replace(old_loop, new_loop)

old_ketu = """    ketu_lon = (swe.calc_ut(current_jd, Config.node_swe_id(), flags)[0][0] + 180.0) % 360.0"""
new_ketu = """    with ephemeris_lock:
        ketu_res, _ = swe.calc_ut(current_jd, Config.node_swe_id(), flags)
    ketu_lon = (ketu_res[0] + 180.0) % 360.0"""
content = content.replace(old_ketu, new_ketu)

old_transits = """        res, _ = swe.calc_ut(current_jd, p_id, flags)"""
new_transits = """        with ephemeris_lock:
            res, _ = swe.calc_ut(current_jd, p_id, flags)"""
content = content.replace(old_transits, new_transits)

old_muhurta = """        res_moon, _ = swe.calc_ut(jd, swe.MOON, flags)"""
new_muhurta = """        with ephemeris_lock:
            swe.set_sid_mode(Config.ayanamsha_swe_id())
            res_moon, _ = swe.calc_ut(jd, swe.MOON, flags)"""
content = content.replace(old_muhurta, new_muhurta)

# 4. Remove inline dasha and use DashaEngine
dasha_start = "    # 4. Detailed Dasha (Vimshottari)"
dasha_end = """        "Mahadasha_End": dec_to_ym(birth_dec + md_end_age)\n    }"""
import re
pattern = re.compile(re.escape(dasha_start) + r'.*?' + re.escape(dasha_end), re.DOTALL)

dasha_replacement = """    # 4. Detailed Dasha (Vimshottari) via DashaEngine
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
content = re.sub(pattern, dasha_replacement, content)

with open('astrology_engine.py', 'w') as f:
    f.write(content)
print("Updated astrology_engine.py")
