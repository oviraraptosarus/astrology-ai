"""
Real-Time Planetary Correlation & Live Timing Engine
Computes live sky transits, KP 5 Ruling Planets, Chaldean Planetary Horas,
Gochara Vedha Obstructions, and Tight Transit-to-Natal Catalytic Aspects.
"""

import math
from datetime import datetime
import pytz
import swisseph as swe
from typing import Dict, List, Any, Tuple
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

NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

PLANET_SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

# Chaldean Order of Planetary Horas
CHALDEAN_ORDER = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

WEEKDAY_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Gochara Favorable Houses from Natal Moon and their Counter-Vedha Houses
# Format: planet: {favorable_house: counter_vedha_house}
VEDHA_PAIRS = {
    "Sun": {3: 9, 6: 12, 10: 4, 11: 5},
    "Moon": {1: 5, 3: 9, 6: 12, 7: 2, 10: 4, 11: 8},
    "Mars": {3: 12, 6: 9, 11: 5},
    "Mercury": {2: 5, 4: 3, 6: 9, 8: 1, 10: 7, 11: 12},
    "Jupiter": {2: 12, 5: 4, 7: 3, 9: 10, 11: 8},
    "Venus": {1: 8, 2: 7, 3: 1, 4: 10, 5: 9, 8: 5, 9: 11, 11: 6, 12: 3},
    "Saturn": {3: 12, 6: 9, 11: 5},
    "Rahu": {3: 12, 6: 9, 11: 5},
    "Ketu": {3: 12, 6: 9, 11: 5}
}

# Exempted Pita-Putra pairs (No Vedha between Sun and Saturn, nor between Moon and Mercury)
EXEMPTED_VEDHA_PAIRS = {
    ("Sun", "Saturn"), ("Saturn", "Sun"),
    ("Moon", "Mercury"), ("Mercury", "Moon")
}

SWE_PLANETS = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
    "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
    "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": Config.node_swe_id()
}

class RealtimeEngine:
    """
    Computes live astronomical snapshots, KP Ruling Planets, Horas, and Vedha.
    """

    @staticmethod
    def get_julian_day(dt_utc: datetime) -> float:
        hour_dec = dt_utc.hour + (dt_utc.minute / 60.0) + (dt_utc.second / 3600.0)
        return swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, hour_dec)

    @staticmethod
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

        return planets_data

    @staticmethod
    def get_live_ascendant(jd: float, lat: float, lon: float) -> Dict[str, Any]:
        swe.set_sid_mode(Config.ayanamsha_swe_id())
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
        try:
            _, ascmc = swe.houses_ex(jd, lat, lon, b'O', flags)
        except Exception:
            _, ascmc = swe.houses_ex(jd, lat, lon, b'E', flags)
        asc_lon = ascmc[0]
        sign_idx = int(asc_lon / 30.0)
        sign = ZODIAC_SIGNS[sign_idx]
        deg = asc_lon % 30.0

        nak_span = 360.0 / 27.0
        nak_idx = int(asc_lon / nak_span)
        nak_name = NAKSHATRAS[nak_idx]
        star_lord = NAKSHATRA_LORDS[nak_idx % 9]

        return {
            "longitude": asc_lon,
            "sign": sign,
            "degree": round(deg, 4),
            "sign_lord": PLANET_SIGN_LORDS[sign],
            "nakshatra": nak_name,
            "star_lord": star_lord
        }

    @staticmethod
    def get_kp_ruling_planets(jd: float, lat: float, lon: float, dt_local: datetime) -> Dict[str, str]:
        """
        Calculates the instantaneous 5 KP Ruling Planets (RP):
        1. Ascendant Star Lord
        2. Ascendant Sign Lord
        3. Moon Star Lord
        4. Moon Sign Lord
        5. Day Lord (Vara Lord from Sunrise)
        """
        asc_info = RealtimeEngine.get_live_ascendant(jd, lat, lon)
        planets = RealtimeEngine.get_live_planets(jd)
        moon_info = planets["Moon"]

        # Day Lord (0 = Sunday in weekday calculations)
        weekday_idx = (dt_local.weekday() + 1) % 7
        day_lord = WEEKDAY_LORDS[weekday_idx]

        return {
            "ascendant_star_lord": asc_info["star_lord"],
            "ascendant_sign_lord": asc_info["sign_lord"],
            "moon_star_lord": moon_info["star_lord"],
            "moon_sign_lord": moon_info["sign_lord"],
            "day_lord": day_lord,
            "ruling_planets_ordered": [
                asc_info["star_lord"], asc_info["sign_lord"],
                moon_info["star_lord"], moon_info["sign_lord"],
                day_lord
            ]
        }

    @staticmethod
    def get_planetary_hora(dt_local: datetime, lat: float, lon: float) -> Dict[str, Any]:
        """
        Calculates the active Planetary Hora in the ancient Chaldean sequence.
        """
        weekday_idx = (dt_local.weekday() + 1) % 7
        day_lord = WEEKDAY_LORDS[weekday_idx]
        day_lord_idx = CHALDEAN_ORDER.index(day_lord)

        # Approximate hora by hour from 6:00 AM standard sunrise (or solar sunrise)
        hour_from_sunrise = (dt_local.hour - 6) % 24
        hora_idx = (day_lord_idx + hour_from_sunrise) % 7
        active_hora = CHALDEAN_ORDER[hora_idx]

        return {
            "day_lord": day_lord,
            "active_hora": active_hora,
            "hora_sequence": [CHALDEAN_ORDER[(day_lord_idx + i) % 7] for i in range(24)]
        }

    @staticmethod
    def check_gochara_vedha(natal_moon_sign: str, live_planets: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Checks whether favorable Gochara transits are obstructed by Vedha.
        """
        natal_moon_idx = ZODIAC_SIGNS.index(natal_moon_sign)
        vedha_reports = []

        # Find houses occupied by all transiting planets relative to natal Moon
        transiting_houses = {}
        for p_name, p_data in live_planets.items():
            t_sign_idx = ZODIAC_SIGNS.index(p_data["sign"])
            house_from_moon = ((t_sign_idx - natal_moon_idx) % 12) + 1
            transiting_houses[p_name] = house_from_moon

        for p_name, p_data in live_planets.items():
            t_house = transiting_houses[p_name]
            favorable_pairs = VEDHA_PAIRS.get(p_name, {})

            if t_house in favorable_pairs:
                counter_house = favorable_pairs[t_house]
                # Check if any planet is occupying the counter-vedha house
                obstructing_planets = [
                    obs_p for obs_p, h in transiting_houses.items()
                    if h == counter_house and obs_p != p_name and (p_name, obs_p) not in EXEMPTED_VEDHA_PAIRS
                ]

                is_obstructed = len(obstructing_planets) > 0
                vedha_reports.append({
                    "planet": p_name,
                    "transiting_house": t_house,
                    "is_favorable": True,
                    "counter_vedha_house": counter_house,
                    "is_obstructed": is_obstructed,
                    "obstructed_by": obstructing_planets,
                    "effective_status": "BLOCKED_BY_VEDHA" if is_obstructed else "UNOBSTRUCTED_FAVORABLE"
                })

        return vedha_reports

    @staticmethod
    def check_tight_catalytic_aspects(natal_chart: Chart, live_planets: Dict[str, Dict[str, Any]], orb: float = 1.0) -> List[Dict[str, Any]]:
        """
        Detects exact catalytic aspects (Conjunction, Opposition, Square, Trine within <= 1.0 deg orb).
        """
        catalysts = []

        for t_name, t_data in live_planets.items():
            t_lon = t_data["longitude"]

            for n_name, n_planet in natal_chart.planets.items():
                if n_name == "Ascendant":
                    continue
                # Calculate absolute longitude for natal planet
                n_sign_idx = ZODIAC_SIGNS.index(n_planet.sign)
                n_lon = (n_sign_idx * 30.0) + n_planet.degree

                diff = abs(t_lon - n_lon) % 360.0
                if diff > 180.0:
                    diff = 360.0 - diff

                aspect_type = None
                if abs(diff - 0.0) <= orb:
                    aspect_type = "EXACT_CONJUNCTION"
                elif abs(diff - 180.0) <= orb:
                    aspect_type = "EXACT_OPPOSITION"
                elif abs(diff - 90.0) <= orb:
                    aspect_type = "EXACT_SQUARE"
                elif abs(diff - 120.0) <= orb:
                    aspect_type = "EXACT_TRINE"

                if aspect_type:
                    catalysts.append({
                        "transiting_planet": t_name,
                        "natal_planet": n_name,
                        "aspect_type": aspect_type,
                        "orb_degrees": round(abs(diff - (0.0 if aspect_type=="EXACT_CONJUNCTION" else 180.0 if aspect_type=="EXACT_OPPOSITION" else 90.0 if aspect_type=="EXACT_SQUARE" else 120.0)), 3),
                        "transit_sign": t_data["sign"],
                        "natal_sign": n_planet.sign
                    })

        return catalysts

    @staticmethod
    def get_realtime_correlation_snapshot(natal_chart: Chart, lat: float, lon: float, tz_name: str = "Asia/Kolkata") -> Dict[str, Any]:
        """
        Generates the full real-time correlation snapshot (Live Sky, KP RPs, Horas, Vedha, Catalysts).
        """
        local_tz = pytz.timezone(tz_name)
        now_local = datetime.now(local_tz)
        now_utc = now_local.astimezone(pytz.utc)
        jd = RealtimeEngine.get_julian_day(now_utc)

        live_planets = RealtimeEngine.get_live_planets(jd)
        live_asc = RealtimeEngine.get_live_ascendant(jd, lat, lon)
        kp_rps = RealtimeEngine.get_kp_ruling_planets(jd, lat, lon, now_local)
        hora_info = RealtimeEngine.get_planetary_hora(now_local, lat, lon)
        
        natal_moon_sign = natal_chart.planets.get("Moon", {}).sign if hasattr(natal_chart, "planets") else "Aries"
        vedha_reports = RealtimeEngine.check_gochara_vedha(natal_moon_sign, live_planets)
        catalytic_aspects = RealtimeEngine.check_tight_catalytic_aspects(natal_chart, live_planets, orb=1.2)

        return {
            "timestamp_local": now_local.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "timestamp_utc": now_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "live_ascendant": live_asc,
            "live_planets": live_planets,
            "kp_ruling_planets": kp_rps,
            "planetary_hora": hora_info,
            "gochara_vedha": vedha_reports,
            "catalytic_aspects": catalytic_aspects
        }
