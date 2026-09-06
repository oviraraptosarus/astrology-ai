"""
Krishnamurti Paddhati (KP) System Engine
Implements Placidus Cusps, 249 Sub-Lords, 4-Fold ABCD Significators,
Cuspal Sub-Lord (CSL) House Linkages, and 1-249 Horary Charts.
"""

from datetime import datetime
import pytz
import swisseph as swe
from typing import Dict, List, Any, Optional
from vedic_models import Chart
from config import Config

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

VIMSHOTTARI_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIMSHOTTARI_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]
TOTAL_YEARS = 120.0

PLANET_SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

SWE_PLANETS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
    "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE
}

class KPEngine:
    """
    Complete Krishnamurti Paddhati (KP) Astronomical & Astrological Engine.
    """

    @staticmethod
    def calculate_kp_lords(longitude: float) -> Dict[str, str]:
        """
        Calculates Sign Lord, Star Lord, Sub Lord, and Sub-Sub Lord for any longitude (0-360 deg).
        """
        lon = longitude % 360.0
        sign_idx = int(lon / 30.0)
        sign = ZODIAC_SIGNS[sign_idx]
        sign_lord = PLANET_SIGN_LORDS[sign]

        # Star Lord (Nakshatra)
        nak_span = 360.0 / 27.0  # 13.3333 degrees (800 minutes)
        nak_idx = int(lon / nak_span)
        star_lord = VIMSHOTTARI_LORDS[nak_idx % 9]
        nak_name = NAKSHATRAS[nak_idx]

        # Sub Lord
        fraction_in_nak = lon % nak_span
        degrees_per_year = nak_span / TOTAL_YEARS
        
        sl_idx = nak_idx % 9
        accumulated_degrees = 0.0
        sub_lord = ""
        sub_lord_start_deg = 0.0
        sub_lord_span_deg = 0.0

        for _ in range(9):
            sl_span = VIMSHOTTARI_YEARS[sl_idx] * degrees_per_year
            if fraction_in_nak < (accumulated_degrees + sl_span):
                sub_lord = VIMSHOTTARI_LORDS[sl_idx]
                sub_lord_start_deg = accumulated_degrees
                sub_lord_span_deg = sl_span
                break
            accumulated_degrees += sl_span
            sl_idx = (sl_idx + 1) % 9

        if not sub_lord:
            sub_lord = VIMSHOTTARI_LORDS[sl_idx]
            sub_lord_span_deg = VIMSHOTTARI_YEARS[sl_idx] * degrees_per_year

        # Sub-Sub Lord (SSL)
        fraction_in_sl = fraction_in_nak - sub_lord_start_deg
        ssl_idx = VIMSHOTTARI_LORDS.index(sub_lord)
        ssl_deg_per_year = sub_lord_span_deg / TOTAL_YEARS
        ssl_accum = 0.0
        sub_sub_lord = ""

        for _ in range(9):
            ssl_span = VIMSHOTTARI_YEARS[ssl_idx] * ssl_deg_per_year
            if fraction_in_sl <= (ssl_accum + ssl_span):
                sub_sub_lord = VIMSHOTTARI_LORDS[ssl_idx]
                break
            ssl_accum += ssl_span
            ssl_idx = (ssl_idx + 1) % 9

        if not sub_sub_lord:
            sub_sub_lord = sub_lord

        return {
            "sign": sign,
            "sign_lord": sign_lord,
            "nakshatra": nak_name,
            "star_lord": star_lord,
            "sub_lord": sub_lord,
            "sub_sub_lord": sub_sub_lord
        }

    @staticmethod
    def calculate_kp_chart(year: int, month: int, day: int, hour: int, minute: int,
                           lat: float, lon: float, tz_name: str = "UTC") -> Dict[str, Any]:
        """
        Calculates complete KP Chart: Placidus Cusps, Planet Longitudes, Lords, and ABCD Matrix.
        """
        local_tz = pytz.timezone(tz_name)
        dt_local = local_tz.localize(datetime(year, month, day, hour, minute))
        dt_utc = dt_local.astimezone(pytz.utc)

        hour_dec = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0)
        jd = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_dec)

        # KP Krishnamurti Ayanamsa (save/restore global sid mode to avoid leaking
        # into other engines that expect Lahiri)
        # KP uses the Krishnamurti ayanamsha, which differs from the system-wide
        # Lahiri base by ~0.9 deg. This build of pyswisseph (2.10.x) exposes
        # set_sid_mode but NOT any get_sid_mode, so the prior mode integer cannot
        # be read back. Lahiri is this system's single canonical base mode, so we
        # restore to Lahiri. The critical guarantee is the try/finally: an
        # exception anywhere in the KP computation must NOT leave the global
        # sidereal mode stuck on Krishnamurti and silently corrupt every
        # subsequent Lahiri chart in the same process.
        _restore_mode = Config.ayanamsha_swe_id()
        swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
        try:
            flags = swe.FLG_SIDEREAL | swe.FLG_SPEED

            # 1. Placidus House Cusps (KP Standard) with Polar / High-Latitude Fallback
            # KP strictly uses Placidus. If Placidus fails (Arctic/Antarctic circles),
            # the standard KP fallback is Porphyry (b'O') because it preserves the MC.
            # Very rarely, Porphyry can also have issues, so we fallback to Equal (b'E').
            try:
                res_houses = swe.houses_ex(jd, lat, lon, b'P', flags)
            except Exception:
                try:
                    res_houses = swe.houses_ex(jd, lat, lon, b'O', flags)
                except Exception:
                    res_houses = swe.houses_ex(jd, lat, lon, b'E', flags)
            raw_cusps = res_houses[0]  # tuple 1-12
            cusp_data = []

            for h in range(1, 13):
                c_lon = raw_cusps[h - 1]
                lords = KPEngine.calculate_kp_lords(c_lon)
                cusp_data.append({
                    "house": h,
                    "longitude": round(c_lon, 4),
                    "sign": lords["sign"],
                    "degree": round(c_lon % 30.0, 4),
                    "sign_lord": lords["sign_lord"],
                    "star_lord": lords["star_lord"],
                    "sub_lord": lords["sub_lord"],
                    "sub_sub_lord": lords["sub_sub_lord"]
                })

            # 2. Planet Positions & Lords
            planet_data = {}
            for name, p_id in SWE_PLANETS.items():
                res, _ = swe.calc_ut(jd, p_id, flags)
                p_lon = res[0]
                speed = res[3]
                lords = KPEngine.calculate_kp_lords(p_lon)

                # Find Placidus house occupied
                occ_house = 12
                for h in range(1, 13):
                    c_start = raw_cusps[h - 1]
                    c_next = raw_cusps[0] if h == 12 else raw_cusps[h]

                    # Handle circular wrap-around
                    if c_start < c_next:
                        if c_start <= p_lon < c_next:
                            occ_house = h
                            break
                    else:
                        if p_lon >= c_start or p_lon < c_next:
                            occ_house = h
                            break

                planet_data[name] = {
                    "longitude": round(p_lon, 4),
                    "sign": lords["sign"],
                    "degree": round(p_lon % 30.0, 4),
                    "speed": round(speed, 5),
                    "retrograde": speed < 0 if name not in ["Sun", "Moon", "Rahu"] else False,
                    "placidus_house": occ_house,
                    "sign_lord": lords["sign_lord"],
                    "star_lord": lords["star_lord"],
                    "sub_lord": lords["sub_lord"],
                    "sub_sub_lord": lords["sub_sub_lord"]
                }

            # Ketu
            rahu_lon = planet_data["Rahu"]["longitude"]
            ketu_lon = (rahu_lon + 180.0) % 360.0
            k_lords = KPEngine.calculate_kp_lords(ketu_lon)

            occ_house = 12
            for h in range(1, 13):
                c_start = raw_cusps[h - 1]
                c_next = raw_cusps[0] if h == 12 else raw_cusps[h]
                if c_start < c_next:
                    if c_start <= ketu_lon < c_next:
                        occ_house = h
                        break
                else:
                    if ketu_lon >= c_start or ketu_lon < c_next:
                        occ_house = h
                        break

            planet_data["Ketu"] = {
                "longitude": round(ketu_lon, 4),
                "sign": k_lords["sign"],
                "degree": round(ketu_lon % 30.0, 4),
                "speed": planet_data["Rahu"]["speed"],
                "retrograde": True,
                "placidus_house": occ_house,
                "sign_lord": k_lords["sign_lord"],
                "star_lord": k_lords["star_lord"],
                "sub_lord": k_lords["sub_lord"],
                "sub_sub_lord": k_lords["sub_sub_lord"]
            }

            # 3. Compute 4-Fold ABCD Significator Matrix
            abcd_matrix = KPEngine._compute_abcd_matrix(cusp_data, planet_data)

            # 4. Cuspal Sub-Lord Analysis (Promises for 12 Houses)
            csl_analysis = KPEngine._evaluate_csl_promises(cusp_data, planet_data, abcd_matrix)

            return {
                "cusps": cusp_data,
                "planets": planet_data,
                "abcd_significators": abcd_matrix,
                "csl_analysis": csl_analysis
            }
        finally:
            # Always restore Lahiri (the system base), even on exception.
            swe.set_sid_mode(_restore_mode)

    @staticmethod
    def _compute_abcd_matrix(cusps: List[Dict], planets: Dict[str, Dict]) -> Dict[str, Any]:
        """
        Builds the standard KP 4-fold significator table:
        Level A: Planet in Star of Occupant of House X
        Level B: Occupant of House X
        Level C: Planet in Star of Lord of House X
        Level D: Lord of House X
        """
        matrix = {}
        for h in range(1, 13):
            cusp = cusps[h - 1]
            sign_lord = cusp["sign_lord"]

            occupants = [p_name for p_name, p in planets.items() if p["placidus_house"] == h]
            
            # Level A: Planets in star of occupants
            level_a = []
            for occ in occupants:
                for p_name, p in planets.items():
                    if p["star_lord"] == occ and p_name not in level_a:
                        level_a.append(p_name)

            # Level B: Occupants
            level_b = list(occupants)

            # Level C: Planets in star of house lord
            level_c = [p_name for p_name, p in planets.items() if p["star_lord"] == sign_lord]

            # Level D: House Lord
            level_d = [sign_lord]

            matrix[str(h)] = {
                "house": h,
                "level_a": level_a,  # Strongest
                "level_b": level_b,
                "level_c": level_c,
                "level_d": level_d,
                "all_significators": list(dict.fromkeys(level_a + level_b + level_c + level_d))
            }

        return matrix

    @staticmethod
    def _evaluate_csl_promises(cusps: List[Dict], planets: Dict[str, Dict], abcd_matrix: Dict) -> Dict[str, Any]:
        """
        Evaluates prime house Cuspal Sub-Lord promises (Career: 2,6,10,11; Marriage: 2,7,11; Wealth: 2,11).
        """
        promises = {}

        # 7th CSL (Marriage / Partnerships)
        csl_7 = cusps[6]["sub_lord"]
        csl_7_star = planets.get(csl_7, {}).get("star_lord", "")
        # Find which houses CSL 7 and its star lord signify
        sig_houses = []
        for h_str, h_data in abcd_matrix.items():
            if csl_7_star in h_data["all_significators"] or csl_7 in h_data["all_significators"]:
                sig_houses.append(int(h_str))
        
        is_marriage_favorable = any(h in sig_houses for h in [2, 7, 11]) and not (all(h in [1, 6, 10] for h in sig_houses) and not any(h in [2, 7, 11] for h in sig_houses))
        promises["marriage_7th_csl"] = {
            "sub_lord": csl_7,
            "star_lord": csl_7_star,
            "signified_houses": sorted(sig_houses),
            "status": "PROMISED_FAVORABLE" if is_marriage_favorable else "FRICTION_OR_DELAY"
        }

        # 10th CSL (Career / Profession / Status)
        csl_10 = cusps[9]["sub_lord"]
        csl_10_star = planets.get(csl_10, {}).get("star_lord", "")
        sig_houses_10 = []
        for h_str, h_data in abcd_matrix.items():
            if csl_10_star in h_data["all_significators"] or csl_10 in h_data["all_significators"]:
                sig_houses_10.append(int(h_str))

        is_career_favorable = any(h in sig_houses_10 for h in [2, 6, 10, 11])
        promises["career_10th_csl"] = {
            "sub_lord": csl_10,
            "star_lord": csl_10_star,
            "signified_houses": sorted(sig_houses_10),
            "status": "STRONG_CAREER_PROMISE" if is_career_favorable else "CHALLENGING_CAREER_PATH"
        }

        # 2nd CSL (Financial Assets & Wealth)
        csl_2 = cusps[1]["sub_lord"]
        csl_2_star = planets.get(csl_2, {}).get("star_lord", "")
        sig_houses_2 = []
        for h_str, h_data in abcd_matrix.items():
            if csl_2_star in h_data["all_significators"] or csl_2 in h_data["all_significators"]:
                sig_houses_2.append(int(h_str))

        promises["wealth_2nd_csl"] = {
            "sub_lord": csl_2,
            "star_lord": csl_2_star,
            "signified_houses": sorted(sig_houses_2),
            "status": "WEALTH_ACCUMULATION_CONFIRMED" if any(h in sig_houses_2 for h in [2, 6, 11]) else "MIXED_GAINS"
        }

        return promises
