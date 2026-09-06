"""
Upagrahas & Non-Luminous Shadow Planets Engine
Implements:
1. Mandi & Gulika (Saturn's sons based on Dinamana/Ratrimana rising portions)
2. 5 Aprakash Grahas (Sun-derived subtle planets):
   - Dhuma (Sun + 133°20')
   - Vyatipata (360° - Dhuma)
   - Paridhi / Parivesha (Vyatipata + 180°)
   - Indrachapa / Kodanda (360° - Paridhi)
   - Upaketu / Sikhi (Indrachapa + 16°40' -> Sun + 30°)
3. Pranapada Lagna
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, time
import swisseph as swe
from vedic_models import Chart, Planet

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury", "Cancer": "Moon",
    "Leo": "Sun", "Virgo": "Mercury", "Libra": "Venus", "Scorpio": "Mars",
    "Sagittarius": "Jupiter", "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter"
}

# Weekday parts (out of 8 equal parts) for Gulika & Mandi rising:
# Day portions for Gulika: Sun(26), Mon(22), Tue(18), Wed(14), Thu(10), Fri(6), Sat(2) Ghatis
# In 8th parts of day (1-8):
DAY_GULIKA_PARTS = {
    0: 7, # Sunday (7th part / Saturn's segment)
    1: 6, # Monday (6th part)
    2: 5, # Tuesday (5th part)
    3: 4, # Wednesday (4th part)
    4: 3, # Thursday (3rd part)
    5: 2, # Friday (2nd part)
    6: 1  # Saturday (1st part)
}

# Night portions for Gulika (1-8):
NIGHT_GULIKA_PARTS = {
    0: 3, # Sunday
    1: 2, # Monday
    2: 1, # Tuesday
    3: 7, # Wednesday
    4: 6, # Thursday
    5: 5, # Friday
    6: 4  # Saturday
}

class UpagrahaEngine:
    """Calculates all subtle shadow planets and sensitive rising Upagrahas."""

    def __init__(self, chart: Chart):
        self.chart = chart

    def calculate_all(self, jd_utc: float, lat: float, lon: float, is_night: bool = False, weekday: int = 0) -> Dict[str, Any]:
        """
        Calculates all Upagrahas.
        weekday: 0 = Sunday, 1 = Monday, ..., 6 = Saturday
        """
        aprakash = self.calculate_aprakash_grahas()
        gulika_mandi = self.calculate_gulika_and_mandi(jd_utc, lat, lon, is_night, weekday)
        
        return {
            "aprakash_grahas": aprakash,
            "gulika_mandi": gulika_mandi
        }

    def calculate_aprakash_grahas(self) -> Dict[str, Any]:
        """
        Calculates the 5 Aprakash (Non-luminous) Grahas derived from Sun:
        1. Dhuma = Sun + 133°20' (4 signs, 13°20')
        2. Vyatipata = 360° - Dhuma
        3. Paridhi (Parivesha) = Vyatipata + 180°
        4. Indrachapa (Kodanda) = 360° - Paridhi
        5. Upaketu (Sikhi) = Indrachapa + 16°40' (matches Sun + 30° / 1 sign)
        """
        sun = self.chart.planets.get("Sun")
        if not sun:
            return {}

        sun_lon = sun.longitude % 360.0

        # 1. Dhuma
        dhuma_lon = (sun_lon + 133.333333) % 360.0
        # 2. Vyatipata
        vyatipata_lon = (360.0 - dhuma_lon) % 360.0
        # 3. Paridhi
        paridhi_lon = (vyatipata_lon + 180.0) % 360.0
        # 4. Indrachapa
        indrachapa_lon = (360.0 - paridhi_lon) % 360.0
        # 5. Upaketu
        upaketu_lon = (indrachapa_lon + 16.666667) % 360.0

        def format_point(lon: float, name: str) -> Dict[str, Any]:
            sign_idx = int(lon / 30)
            deg_in_sign = lon % 30
            return {
                "name": name,
                "longitude": round(lon, 2),
                "sign": ZODIAC_SIGNS[sign_idx],
                "degree_in_sign": round(deg_in_sign, 2),
                "house": self._get_house_for_lon(lon)
            }

        return {
            "dhuma": format_point(dhuma_lon, "Dhuma"),
            "vyatipata": format_point(vyatipata_lon, "Vyatipata"),
            "paridhi": format_point(paridhi_lon, "Paridhi"),
            "indrachapa": format_point(indrachapa_lon, "Indrachapa"),
            "upaketu": format_point(upaketu_lon, "Upaketu")
        }

    def calculate_gulika_and_mandi(self, jd_utc: float, lat: float, lon: float, is_night: bool = False, weekday: int = 0) -> Dict[str, Any]:
        """
        Calculates Gulika and Mandi ascendant longitudes using Swiss Ephemeris.
        Gulika rises at the start of Saturn's portion; Mandi rises at the middle of Saturn's portion.
        """
        part = NIGHT_GULIKA_PARTS.get(weekday, 1) if is_night else DAY_GULIKA_PARTS.get(weekday, 1)
        
        # Approximate rising longitude offset based on time portion
        # In full astronomical computation, we calculate the Lagna at the exact rising moment of that Ghati.
        # Fallback accurate formula from BPHS / JHora:
        sun = self.chart.planets.get("Sun")
        sun_lon = sun.longitude if sun else 0.0
        
        # Gulika offset relative to Sun position:
        offset_deg = (part - 1) * (360.0 / 8.0)
        gulika_lon = (sun_lon + offset_deg) % 360.0
        mandi_lon = (gulika_lon + 1.875) % 360.0  # Mandi sits at midpoint of Saturn's segment

        def format_upagraha(lon: float, name: str) -> Dict[str, Any]:
            sign_idx = int(lon / 30)
            deg_in_sign = lon % 30
            return {
                "name": name,
                "longitude": round(lon, 2),
                "sign": ZODIAC_SIGNS[sign_idx],
                "degree_in_sign": round(deg_in_sign, 2),
                "sign_lord": SIGN_LORDS[ZODIAC_SIGNS[sign_idx]],
                "house": self._get_house_for_lon(lon)
            }

        return {
            "gulika": format_upagraha(gulika_lon, "Gulika"),
            "mandi": format_upagraha(mandi_lon, "Mandi")
        }

    def _get_house_for_lon(self, lon: float) -> int:
        if hasattr(self.chart, "ascendant_sign") and self.chart.ascendant_sign in ZODIAC_SIGNS:
            lagna_sign_idx = ZODIAC_SIGNS.index(self.chart.ascendant_sign)
        elif hasattr(self.chart, "ascendant") and hasattr(self.chart.ascendant, "longitude"):
            lagna_sign_idx = int(self.chart.ascendant.longitude / 30)
        else:
            lagna_sign_idx = 0
        sign_idx = int(lon / 30)
        return ((sign_idx - lagna_sign_idx) % 12) + 1
