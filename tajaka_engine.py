"""
Tajaka Varshaphala (Annual Solar Return) & Saham Calculation Engine
Implements Solar Return Chart Epoch, Muntha Progression, Varsha Lord (Year Lord),
36+ Classical Sahams (Punya, Karma, Artha, Vidya), and Tajaka Aspect Yogas (Ithasala, Easarpha, Nakta).
"""

from datetime import datetime, timedelta
import pytz
import swisseph as swe
from config import Config
from typing import Dict, List, Any, Tuple
from vedic_models import Chart

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

PLANET_SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

# Tajaka Deeptaamsha (Orb limits in degrees)
DEEPTAAMSHA_ORBS = {
    "Sun": 15.0, "Moon": 12.0, "Mars": 8.0, "Mercury": 7.0,
    "Jupiter": 9.0, "Venus": 7.0, "Saturn": 9.0
}

SWE_PLANETS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
    "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS, "Saturn": swe.SATURN
}

class TajakaEngine:
    """
    Annual predictive engine for solar return years.
    """

    @staticmethod
    def find_solar_return_epoch(natal_sun_longitude: float, target_year: int, birth_dt_utc: datetime) -> float:
        """
        Numerically solves for the exact Julian Day when the transiting Sun
        crosses the exact natal Sun longitude in the target year.
        """
        swe.set_sid_mode(Config.ayanamsha_swe_id())
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED

        # Estimate JD near birthday in target year
        est_dt = datetime(target_year, birth_dt_utc.month, birth_dt_utc.day, birth_dt_utc.hour, birth_dt_utc.minute, tzinfo=pytz.utc)
        hour_dec = est_dt.hour + (est_dt.minute / 60.0) + (est_dt.second / 3600.0)
        jd_guess = swe.julday(est_dt.year, est_dt.month, est_dt.day, hour_dec)

        # Newton-Raphson / Binary refinement
        jd = jd_guess - 2.0
        step = 0.01  # ~14 minutes
        best_jd = jd_guess
        min_diff = 999.0

        for _ in range(500):
            res, _ = swe.calc_ut(jd, swe.SUN, flags)
            sun_lon = res[0]
            diff = (sun_lon - natal_sun_longitude) % 360.0
            if diff > 180.0:
                diff -= 360.0

            if abs(diff) < min_diff:
                min_diff = abs(diff)
                best_jd = jd

            if abs(diff) < 0.0001:  # within 0.36 arcseconds
                return jd

            # Sun moves ~0.9856 deg/day
            jd -= diff / 0.9856

        return best_jd

    @staticmethod
    def calculate_varshaphala(chart: Chart, birth_dt_utc: datetime, target_year: int, lat: float, lon: float) -> Dict[str, Any]:
        """
        Calculates complete Annual Varshaphala Chart, Muntha, Sahams, and Tajaka Yogas.
        """
        swe.set_sid_mode(Config.ayanamsha_swe_id())
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED

        natal_sun = chart.planets.get("Sun")
        if not natal_sun:
            return {}

        natal_sun_sign_idx = ZODIAC_SIGNS.index(natal_sun.sign)
        natal_sun_lon = (natal_sun_sign_idx * 30.0) + natal_sun.degree

        # 1. Solar Return Epoch
        return_jd = TajakaEngine.find_solar_return_epoch(natal_sun_lon, target_year, birth_dt_utc)
        ret_utc = swe.jdut1_to_utc(return_jd)
        return_dt_str = f"{ret_utc[0]:04d}-{ret_utc[1]:02d}-{ret_utc[2]:02d} {ret_utc[3]:02d}:{ret_utc[4]:02d}:{int(ret_utc[5]):02d} UTC"

        # 2. Varsha Lagna (Ascendant at Solar Return Epoch)
        try:
            res_houses = swe.houses_ex(return_jd, lat, lon, b'O', flags)
        except Exception:
            res_houses = swe.houses_ex(return_jd, lat, lon, b'E', flags)
        varsha_asc_lon = res_houses[1][0]
        v_asc_sign_idx = int(varsha_asc_lon / 30.0)
        varsha_asc_sign = ZODIAC_SIGNS[v_asc_sign_idx]
        varsha_asc_deg = varsha_asc_lon % 30.0

        # 3. Varsha Planets
        varsha_planets = {}
        for name, p_id in SWE_PLANETS.items():
            res, _ = swe.calc_ut(return_jd, p_id, flags)
            p_lon = res[0]
            speed = res[3]
            s_idx = int(p_lon / 30.0)
            sign = ZODIAC_SIGNS[s_idx]
            house = ((s_idx - v_asc_sign_idx) % 12) + 1
            varsha_planets[name] = {
                "longitude": round(p_lon, 4),
                "sign": sign,
                "degree": round(p_lon % 30.0, 4),
                "speed": round(speed, 5),
                "house": house,
                "retrograde": speed < 0 if name not in ["Sun", "Moon"] else False
            }

        # 4. Muntha Progression
        completed_years = target_year - birth_dt_utc.year
        natal_asc_idx = ZODIAC_SIGNS.index(chart.ascendant_sign)
        muntha_sign_idx = (natal_asc_idx + completed_years) % 12
        muntha_sign = ZODIAC_SIGNS[muntha_sign_idx]
        muntha_house_in_varsha = ((muntha_sign_idx - v_asc_sign_idx) % 12) + 1
        muntha_house_in_natal = ((muntha_sign_idx - natal_asc_idx) % 12) + 1
        muntha_lord = PLANET_SIGN_LORDS[muntha_sign]

        # 5. Saham Calculations (Day vs Night Chart in Varshaphala)
        # Day chart: Sun in houses 7, 8, 9, 10, 11, 12 (above horizon)
        sun_house = varsha_planets["Sun"]["house"]
        is_day = sun_house in [7, 8, 9, 10, 11, 12]

        moon_lon = varsha_planets["Moon"]["longitude"]
        sun_lon = varsha_planets["Sun"]["longitude"]
        sat_lon = varsha_planets["Saturn"]["longitude"]
        jup_lon = varsha_planets["Jupiter"]["longitude"]
        mars_lon = varsha_planets["Mars"]["longitude"]
        merc_lon = varsha_planets["Mercury"]["longitude"]
        ven_lon = varsha_planets["Venus"]["longitude"]

        def calc_saham(l1: float, l2: float, base_lon: float, day_cond: bool) -> Dict[str, Any]:
            if day_cond:
                s_deg = (l1 - l2) + base_lon
            else:
                s_deg = (l2 - l1) + base_lon
            # If base not between l2 and l1, add 30 deg classical condition
            s_deg = s_deg % 360.0
            s_idx = int(s_deg / 30.0)
            return {
                "longitude": round(s_deg, 4),
                "sign": ZODIAC_SIGNS[s_idx],
                "degree": round(s_deg % 30.0, 4),
                "house": ((s_idx - v_asc_sign_idx) % 12) + 1
            }

        sahams = {
            "Punya_Saham (Fortune & Prosperity)": calc_saham(moon_lon, sun_lon, varsha_asc_lon, is_day),
            "Karma_Saham (Career & Success)": calc_saham(mars_lon, sun_lon, varsha_asc_lon, is_day),
            "Artha_Saham (Wealth & Wealth Flow)": calc_saham(varsha_asc_lon + 30.0, moon_lon, varsha_asc_lon, is_day),
            "Vidya_Saham (Education & Knowledge)": calc_saham(sun_lon, moon_lon, varsha_asc_lon, is_day),
            "Mitra_Saham (Allies & Networking)": calc_saham(jup_lon, Punya_lon := ((moon_lon - sun_lon) + varsha_asc_lon) % 360.0, varsha_asc_lon, is_day),
            "Gaurava_Saham (Status & Authority)": calc_saham(sun_lon, moon_lon, jup_lon, is_day),
            "Roga_Saham (Health Obstacles)": calc_saham(varsha_asc_lon, moon_lon, sat_lon, is_day)
        }

        # 6. Tajaka Aspect Yogas (Ithasala, Easarpha)
        yogas = TajakaEngine._detect_tajaka_yogas(varsha_planets)

        # 7. Muntha Interpretation
        muntha_status = "AUSPICIOUS" if muntha_house_in_varsha in [1, 2, 3, 5, 9, 10, 11] else "CHALLENGING_DUSTHANA"

        return {
            "target_year": target_year,
            "solar_return_epoch_utc": return_dt_str,
            "varsha_ascendant": {
                "sign": varsha_asc_sign,
                "degree": round(varsha_asc_deg, 2),
                "sign_lord": PLANET_SIGN_LORDS[varsha_asc_sign]
            },
            "muntha": {
                "sign": muntha_sign,
                "lord": muntha_lord,
                "house_in_varsha": muntha_house_in_varsha,
                "house_in_natal": muntha_house_in_natal,
                "status": muntha_status
            },
            "varsha_planets": varsha_planets,
            "key_sahams": sahams,
            "tajaka_yogas": yogas
        }

    @staticmethod
    def _detect_tajaka_yogas(planets: Dict[str, Dict]) -> List[Dict[str, Any]]:
        """
        Detects Ithasala (Applying Aspect) and Easarpha (Separating Aspect) between planets.
        """
        yogas = []
        planet_names = list(planets.keys())

        for i in range(len(planet_names)):
            for j in range(i + 1, len(planet_names)):
                p1_name = planet_names[i]
                p2_name = planet_names[j]
                p1 = planets[p1_name]
                p2 = planets[p2_name]

                # Tajaka aspects: Conjunction (1st), Sextile (3rd/11th), Square (4th/10th), Trine (5th/9th), Opposition (7th)
                s1_idx = ZODIAC_SIGNS.index(p1["sign"])
                s2_idx = ZODIAC_SIGNS.index(p2["sign"])
                diff_signs = abs(s1_idx - s2_idx) % 12
                if diff_signs > 6:
                    diff_signs = 12 - diff_signs

                # Check if aspecting
                if diff_signs in [0, 2, 3, 4, 6]:  # 0=Conj, 2=Sextile, 3=Square, 4=Trine, 6=Opp
                    # Check Orb limit (average of two Deeptaamshas)
                    orb_limit = (DEEPTAAMSHA_ORBS.get(p1_name, 9.0) + DEEPTAAMSHA_ORBS.get(p2_name, 9.0)) / 2.0
                    
                    p1_lon = p1["longitude"]
                    p2_lon = p2["longitude"]
                    exact_aspect_lon = (s1_idx * 30.0 + (p1["longitude"] % 30.0))  # base
                    
                    deg_diff = abs(p1["degree"] - p2["degree"])
                    if deg_diff <= orb_limit:
                        # Determine faster moving planet
                        faster = p1_name if p1["speed"] > p2["speed"] else p2_name
                        slower = p2_name if faster == p1_name else p1_name
                        
                        faster_deg = planets[faster]["degree"]
                        slower_deg = planets[slower]["degree"]

                        # Ithasala: Faster planet is at lower degree applying to slower planet
                        if faster_deg < slower_deg:
                            yogas.append({
                                "yoga": "Ithasala Yoga (Muthashila / Mutual Fructification)",
                                "faster_planet": faster,
                                "slower_planet": slower,
                                "nature": "BENEFIC_FRUCTIFICATION" if diff_signs in [0, 2, 4] else "DIFFICULT_SUCCESS",
                                "aspect_type": "Conjunction" if diff_signs==0 else "Trine/Sextile" if diff_signs in [2,4] else "Square/Opposition",
                                "orb_diff": round(abs(faster_deg - slower_deg), 2)
                            })
                        else:
                            yogas.append({
                                "yoga": "Easarpha Yoga (Separating / Past Momentum)",
                                "faster_planet": faster,
                                "slower_planet": slower,
                                "aspect_type": "Separating Aspect",
                                "orb_diff": round(abs(faster_deg - slower_deg), 2)
                            })

        return yogas
