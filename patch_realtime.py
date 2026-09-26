import re

with open('realtime_engine.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace get_live_planets with the locked + centralized version
old_planets = """    @staticmethod
    def get_live_planets(jd: float) -> Dict[str, Dict[str, Any]]:
        swe.set_sid_mode(Config.ayanamsha_swe_id())
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
        planets_data = {}

        for name, p_id in SWE_PLANETS.items():
            res, _ = swe.calc_ut(jd, p_id, flags)
            lon = res[0]
            speed = res[3]
            sign_idx = int(lon / 30.0)
            sign = ZODIAC_SIGNS[sign_idx]
            deg = lon % 30.0

            nak_span = 360.0 / 27.0
            nak_idx = int(lon / nak_span)
            nak_name = NAKSHATRAS[nak_idx]
            star_lord = NAKSHATRA_LORDS[nak_idx % 9]

            is_stationary = abs(speed) < 0.005
            is_retrograde = speed < 0 if name not in ["Sun", "Moon", "Rahu"] else False

            planets_data[name] = {
                "longitude": lon,
                "sign": sign,
                "degree": round(deg, 4),
                "speed": round(speed, 5),
                "retrograde": is_retrograde,
                "stationary": is_stationary,
                "nakshatra": nak_name,
                "star_lord": star_lord,
                "sign_lord": PLANET_SIGN_LORDS[sign]
            }

        # Ketu (always opposite Rahu)
        rahu_lon = planets_data["Rahu"]["longitude"]
        ketu_lon = (rahu_lon + 180.0) % 360.0
        k_sign_idx = int(ketu_lon / 30.0)
        k_sign = ZODIAC_SIGNS[k_sign_idx]
        k_nak_idx = int(ketu_lon / (360.0 / 27.0))

        planets_data["Ketu"] = {
            "longitude": ketu_lon,
            "sign": k_sign,
            "degree": round(ketu_lon % 30.0, 4),
            "speed": planets_data["Rahu"]["speed"],
            "retrograde": True,
            "stationary": planets_data["Rahu"]["stationary"],
            "nakshatra": NAKSHATRAS[k_nak_idx],
            "star_lord": NAKSHATRA_LORDS[k_nak_idx % 9],
            "sign_lord": PLANET_SIGN_LORDS[k_sign]
        }

        return planets_data"""

new_planets = """    @staticmethod
    def get_live_planets(jd: float) -> Dict[str, Dict[str, Any]]:
        from astronomy_core import ephemeris_lock, AstronomyCore, NAKSHATRAS as CORE_NAK, DASHA_LORDS
        with ephemeris_lock:
            swe.set_sid_mode(Config.ayanamsha_swe_id())
            flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
            planets_data = {}
    
            for name, p_id in SWE_PLANETS.items():
                res, _ = swe.calc_ut(jd, p_id, flags)
                lon = res[0]
                speed = res[3]
                sign_idx = int(lon / 30.0)
                sign = ZODIAC_SIGNS[sign_idx]
                deg = lon % 30.0
    
                nak_idx, _, _ = AstronomyCore.calculate_nakshatra(lon)
                nak_name = CORE_NAK[nak_idx]
                star_lord = DASHA_LORDS[nak_idx % 9]
    
                is_stationary = abs(speed) < 0.005
                is_retrograde = speed < 0 if name not in ["Sun", "Moon", "Rahu"] else False
    
                planets_data[name] = {
                    "longitude": lon,
                    "sign": sign,
                    "degree": round(deg, 4),
                    "speed": round(speed, 5),
                    "retrograde": is_retrograde,
                    "stationary": is_stationary,
                    "nakshatra": nak_name,
                    "star_lord": star_lord,
                    "sign_lord": PLANET_SIGN_LORDS[sign]
                }
    
            # Ketu (always opposite Rahu)
            rahu_lon = planets_data["Rahu"]["longitude"]
            ketu_lon = (rahu_lon + 180.0) % 360.0
            k_sign_idx = int(ketu_lon / 30.0)
            k_sign = ZODIAC_SIGNS[k_sign_idx]
            k_nak_idx, _, _ = AstronomyCore.calculate_nakshatra(ketu_lon)
    
            planets_data["Ketu"] = {
                "longitude": ketu_lon,
                "sign": k_sign,
                "degree": round(ketu_lon % 30.0, 4),
                "speed": planets_data["Rahu"]["speed"],
                "retrograde": True,
                "stationary": planets_data["Rahu"]["stationary"],
                "nakshatra": CORE_NAK[k_nak_idx],
                "star_lord": DASHA_LORDS[k_nak_idx % 9],
                "sign_lord": PLANET_SIGN_LORDS[k_sign]
            }
    
        return planets_data"""

if old_planets in content:
    content = content.replace(old_planets, new_planets)
else:
    print("Could not find get_live_planets chunk!")

old_asc = """    @staticmethod
    def get_live_ascendant(jd: float, lat: float, lon: float) -> Dict[str, Any]:
        swe.set_sid_mode(Config.ayanamsha_swe_id())
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
        try:
            _, ascmc = swe.houses_ex(jd, lat, lon, b'O', flags)
        except Exception:
            _, ascmc = swe.houses_ex(jd, lat, lon, b'E', flags)"""

new_asc = """    @staticmethod
    def get_live_ascendant(jd: float, lat: float, lon: float) -> Dict[str, Any]:
        from astronomy_core import ephemeris_lock
        with ephemeris_lock:
            swe.set_sid_mode(Config.ayanamsha_swe_id())
            flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
            try:
                _, ascmc = swe.houses_ex(jd, lat, lon, b'O', flags)
            except Exception:
                _, ascmc = swe.houses_ex(jd, lat, lon, b'E', flags)"""

if old_asc in content:
    content = content.replace(old_asc, new_asc)
else:
    print("Could not find get_live_ascendant chunk!")

with open('realtime_engine.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("realtime_engine.py patched.")
