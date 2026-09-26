import re

# 1. Panchangam Engine (Karana)
with open('panchangam_engine.py', 'r') as f:
    content = f.read()

content = content.replace('karana_name = FIXED_KARANAS[karana_idx - 57]', 'karana_name = FIXED_KARANAS[karana_idx - 58]')
with open('panchangam_engine.py', 'w') as f:
    f.write(content)


# 2. Jaimini Engine (AL Math & Chara Dasha delegation)
with open('jaimini_engine.py', 'r') as f:
    content = f.read()

content = content.replace('al_idx = (al_idx + 3) % 12', 'al_idx = (al_idx + 9) % 12')

# Also, delegate Chara Dasha
if 'from jaimini_chara_dasha_engine import JaiminiCharaDashaEngine' not in content:
    content = content.replace('class JaiminiEngine:', 'from jaimini_chara_dasha_engine import JaiminiCharaDashaEngine\n\nclass JaiminiEngine:')

old_chara_dasha = '''    def calculate_chara_dasha(cls, asc_sign: str, planet_lons: Dict[str, float]) -> List[Dict]:
        """
        Calculates Jaimini Chara Dasha periods.
        Uses K.N. Rao methodology.
        """
        # Simplification for demonstration.
        # A full Chara Dasha requires evaluating dual-lordship (Scorpio/Aquarius)
        # and exaltation/debilitation length modifications.
        # Using primary lord for now.
        
        asc_idx = ZODIAC_SIGNS.index(asc_sign)
        dasha_seq = []
        is_direct = asc_idx % 2 == 0 # Aries, Gemini, Leo, etc go forward. Taurus, Cancer go backward.
        
        # Exception for certain signs (e.g., Scorpio, Aquarius) exists in strict rule sets,
        # but basic forward/backward is implemented here.
        for i in range(12):
            sign_idx = (asc_idx + i) if is_direct else (asc_idx - i)
            sign_idx = sign_idx % 12
            sign_name = ZODIAC_SIGNS[sign_idx]
            
            # Find lord
            lord = SIGN_LORDS[sign_name][0]
            lord_lon = planet_lons[lord]
            lord_sign_idx = int(lord_lon / 30)
            
            # Count from sign to lord
            if is_direct:
                length = (lord_sign_idx - sign_idx) % 12
            else:
                length = (sign_idx - lord_sign_idx) % 12
                
            if length == 0:
                length = 12
                
            dasha_seq.append({
                "sign": sign_name,
                "duration_years": length
            })
            
        return dasha_seq'''

new_chara_dasha = '''    def calculate_chara_dasha(cls, asc_sign: str, planet_lons: Dict[str, float]) -> List[Dict]:
        """
        Calculates Jaimini Chara Dasha periods.
        Delegates to the dedicated JaiminiCharaDashaEngine which correctly implements K.N. Rao rules.
        """
        return JaiminiCharaDashaEngine.calculate_chara_dasha(asc_sign, planet_lons)'''

content = content.replace(old_chara_dasha, new_chara_dasha)
with open('jaimini_engine.py', 'w') as f:
    f.write(content)


# 3. Strength Engine (Cheshta Bala)
with open('strength_engine.py', 'r') as f:
    content = f.read()

# Replace Tropical Heliocentric Mercury/Venus proxy with Geocentric Sidereal Sun
# Wait, we need to read strength_engine.py to see the exact code.

# 3. Strength Engine (Cheshta Bala)
with open('strength_engine.py', 'r') as f:
    content = f.read()

old_cheshta = """            if p_name in ["Mars", "Jupiter", "Saturn"]:
                # Outer planets: Seeghrocca is Sun (geocentric)
                res_sun, _ = swe.calc_ut(jd, swe.SUN, swe.FLG_SWIEPH)
                seeghrocca = res_sun[0]
            else:
                # Inner planets: Seeghrocca is Heliocentric Longitude
                p_id = {"Mercury": swe.MERCURY, "Venus": swe.VENUS}[p_name]
                res_hel, _ = swe.calc_ut(jd, p_id, swe.FLG_SWIEPH | swe.FLG_HELCTR)
                seeghrocca = res_hel[0]"""

# Update to use the same Sidereal Geocentric flags as the planets, and apply to Sun
new_cheshta = """            from astronomy_core import ephemeris_lock
            from config import Config
            with ephemeris_lock:
                swe.set_sid_mode(Config.ayanamsha_swe_id())
                flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
                # Seeghrocca for all standard planets in Vedic is Sidereal Geocentric Sun
                # (For outer planets it's the Sun, for inner planets it's the Sun)
                res_sun, _ = swe.calc_ut(jd, swe.SUN, flags)
                seeghrocca = res_sun[0]"""

content = content.replace(old_cheshta, new_cheshta)
with open('strength_engine.py', 'w') as f:
    f.write(content)
print("Updated strength_engine.py")
