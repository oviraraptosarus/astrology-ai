import re

with open('tajaka_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# First block: find_solar_return_epoch
old_1 = """    def find_solar_return_epoch(natal_sun_longitude: float, target_year: int, birth_dt_utc: datetime) -> float:
        \"\"\"
        Numerically solves for the exact Julian Day when the transiting Sun
        crosses the exact natal Sun longitude in the target year.
        \"\"\"
        swe.set_sid_mode(Config.ayanamsha_swe_id())
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED

        # Estimate JD near birthday in target year
        est_dt = datetime(target_year, birth_dt_utc.month, birth_dt_utc.day, birth_dt_utc.hour, birth_dt_utc.minute, tzinfo=pytz.utc)"""

new_1 = """    def find_solar_return_epoch(natal_sun_longitude: float, target_year: int, birth_dt_utc: datetime) -> float:
        \"\"\"
        Numerically solves for the exact Julian Day when the transiting Sun
        crosses the exact natal Sun longitude in the target year.
        \"\"\"
        from astronomy_core import ephemeris_lock
        ephemeris_lock.acquire()
        try:
            swe.set_sid_mode(Config.ayanamsha_swe_id())
            flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
    
            # Estimate JD near birthday in target year
            est_dt = datetime(target_year, birth_dt_utc.month, birth_dt_utc.day, birth_dt_utc.hour, birth_dt_utc.minute, tzinfo=pytz.utc)"""

if old_1 in content:
    content = content.replace(old_1, new_1)

old_1b = """            if abs(diff) < 0.0001:  # within 0.36 arcseconds
                return jd

            jd += step

        return best_jd"""

new_1b = """            if abs(diff) < 0.0001:  # within 0.36 arcseconds
                return jd

            jd += step

        return best_jd
        finally:
            ephemeris_lock.release()"""

if old_1b in content:
    content = content.replace(old_1b, new_1b)

# Second block: calculate_varshaphala
old_2 = """        # 2. Varsha Lagna (Ascendant at Solar Return Epoch)
        try:
            res_houses = swe.houses_ex(return_jd, lat, lon, b'O', flags)
        except Exception:
            res_houses = swe.houses_ex(return_jd, lat, lon, b'E', flags)

        varsha_asc_lon = res_houses[1][0]
        v_asc_sign_idx = int(varsha_asc_lon / 30.0)
        v_asc_sign = ZODIAC_SIGNS[v_asc_sign_idx]

        # 3. Planetary positions at Solar Return Epoch
        planets_data = {}
        for p_name, p_id in SWE_PLANETS.items():
            res, _ = swe.calc_ut(return_jd, p_id, flags)"""

new_2 = """        # 2. Varsha Lagna (Ascendant at Solar Return Epoch)
        from astronomy_core import ephemeris_lock
        with ephemeris_lock:
            swe.set_sid_mode(Config.ayanamsha_swe_id())
            try:
                res_houses = swe.houses_ex(return_jd, lat, lon, b'O', flags)
            except Exception:
                res_houses = swe.houses_ex(return_jd, lat, lon, b'E', flags)
    
            varsha_asc_lon = res_houses[1][0]
            v_asc_sign_idx = int(varsha_asc_lon / 30.0)
            v_asc_sign = ZODIAC_SIGNS[v_asc_sign_idx]
    
            # 3. Planetary positions at Solar Return Epoch
            planets_data = {}
            for p_name, p_id in SWE_PLANETS.items():
                res, _ = swe.calc_ut(return_jd, p_id, flags)"""

# In calculate_varshaphala, it sets sid_mode early:
old_2_pre = """    def calculate_varshaphala(chart: Chart, birth_dt_utc: datetime, target_year: int, lat: float, lon: float) -> Dict[str, Any]:
        \"\"\"
        Calculates complete Annual Varshaphala Chart, Muntha, Sahams, and Tajaka Yogas.
        \"\"\"
        swe.set_sid_mode(Config.ayanamsha_swe_id())
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED"""

new_2_pre = """    def calculate_varshaphala(chart: Chart, birth_dt_utc: datetime, target_year: int, lat: float, lon: float) -> Dict[str, Any]:
        \"\"\"
        Calculates complete Annual Varshaphala Chart, Muntha, Sahams, and Tajaka Yogas.
        \"\"\"
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED"""

if old_2 in content:
    content = content.replace(old_2, new_2)
if old_2_pre in content:
    content = content.replace(old_2_pre, new_2_pre)

with open('tajaka_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("tajaka patched.")
