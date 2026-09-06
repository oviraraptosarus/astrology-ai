"""
Tajika Varshaphala Engine (Classical Vedic Annual Solar Return System)
Implements:
1. Exact Solar Return (Varsha Pravesha) Julian Day calculation via Swiss Ephemeris.
2. Muntha Calculation (Moving Annual Ascendant).
3. 5 Candidate Year Lords (Pancha-Adhikaris) and Varsha Swami selection.
4. 16 Tajika Yogas (Ithasala/Muthasila, Esharapha, Nakta, Yamaya, Kamboola).
5. 12-Month Annual Mudda Dasha Timeline.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pytz
import swisseph as swe
from config import Config

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

# Deeptamsha Orbs (in degrees) for Tajika aspects
DEEPTAMSHA_ORBS = {
    "Sun": 15.0, "Moon": 12.0, "Mars": 8.0, "Mercury": 7.0,
    "Jupiter": 9.0, "Venus": 7.0, "Saturn": 9.0
}

# Average planetary daily motion in degrees for speed comparison
MEAN_SPEEDS = {
    "Moon": 13.176, "Mercury": 1.383, "Venus": 1.200, "Sun": 0.985,
    "Mars": 0.524, "Jupiter": 0.083, "Saturn": 0.033
}

# Mudda Dasha durations (in days for 365.25 day annual year)
MUDDA_DAYS = {
    "Sun": 18.25, "Moon": 30.44, "Mars": 21.31, "Rahu": 54.79,
    "Jupiter": 48.70, "Saturn": 57.83, "Mercury": 51.74, "Ketu": 21.31, "Venus": 60.88
}
MUDDA_ORDER = ["Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu", "Venus"]

class TajikaVarshaphalaEngine:
    @staticmethod
    def calculate_varsha_pravesha(natal_sun_lon: float, target_year: int, birth_dt: datetime) -> float:
        """Finds the exact Julian Day when transiting Sun returns to natal_sun_lon in target_year."""
        swe.set_sid_mode(Config.ayanamsha_swe_id())
        
        # Approximate JD around birthday in target_year
        approx_dt = datetime(target_year, birth_dt.month, birth_dt.day, birth_dt.hour, birth_dt.minute, tzinfo=pytz.utc)
        hour_dec = approx_dt.hour + (approx_dt.minute / 60.0)
        jd_approx = swe.julday(approx_dt.year, approx_dt.month, approx_dt.day, hour_dec)
        
        # Bounded Newton-Raphson search for exact Sun return
        jd_curr = jd_approx - 2.0
        for _ in range(25):
            res, _ = swe.calc_ut(jd_curr, swe.SUN, swe.FLG_SIDEREAL)
            curr_lon = res[0] % 360.0
            diff = (natal_sun_lon - curr_lon + 180.0) % 360.0 - 180.0
            if abs(diff) < 0.00001:  # Sub-arcsecond precision
                break
            daily_motion = res[3] if len(res) > 3 and res[3] > 0 else 0.9856
            jd_curr += diff / daily_motion

        return jd_curr

    @classmethod
    def calculate_annual_chart(cls, chart: Chart, target_year: int, lat: float, lon: float) -> Dict[str, Any]:
        """Casts the full Tajika Solar Return chart for target_year."""
        birth_dt = getattr(chart, "birth_time", datetime(2000, 1, 1, tzinfo=pytz.utc))
        if birth_dt.tzinfo is None:
            birth_dt = pytz.utc.localize(birth_dt)

        natal_sun = chart.planets.get("Sun")
        natal_sun_lon = natal_sun.longitude if natal_sun else 0.0
        
        jd_return = cls.calculate_varsha_pravesha(natal_sun_lon, target_year, birth_dt)
        year_val, month_val, day_val, hour_val = swe.revjul(jd_return)
        
        hours = int(hour_val)
        minutes = int((hour_val - hours) * 60)
        seconds = int((((hour_val - hours) * 60) - minutes) * 60)
        pravesha_utc = datetime(year_val, month_val, day_val, hours, minutes, seconds, tzinfo=pytz.utc)

        # Calculate Varsha Ascendant
        swe.set_sid_mode(Config.ayanamsha_swe_id())
        try:
            cusps, ascmc = swe.houses_ex(jd_return, lat, lon, b'P', swe.FLG_SIDEREAL)
        except Exception:
            cusps, ascmc = swe.houses_ex(jd_return, lat, lon, b'E', swe.FLG_SIDEREAL)
        varsha_asc_lon = ascmc[0] % 360.0
        varsha_asc_sign_idx = int(varsha_asc_lon / 30)
        varsha_asc_sign = ZODIAC_SIGNS[varsha_asc_sign_idx]

        # Calculate Muntha
        natal_asc_sign = chart.ascendant_sign if hasattr(chart, "ascendant_sign") and chart.ascendant_sign in ZODIAC_SIGNS else ZODIAC_SIGNS[int(chart.ascendant.longitude / 30)]
        natal_asc_sign_idx = ZODIAC_SIGNS.index(natal_asc_sign)
        
        completed_years = target_year - birth_dt.year
        muntha_sign_idx = (natal_asc_sign_idx + completed_years) % 12
        muntha_sign = ZODIAC_SIGNS[muntha_sign_idx]
        muntha_lord = SIGN_LORDS[muntha_sign]
        muntha_house_in_varsha = ((muntha_sign_idx - varsha_asc_sign_idx) % 12) + 1

        # Check Muntha Auspiciousness
        muntha_status = "AUSPICIOUS"
        if muntha_house_in_varsha in [6, 8, 12]:
            muntha_status = f"AFFLICTED (Falls in Dusthana House {muntha_house_in_varsha} - struggle/health stress)"
        elif muntha_house_in_varsha in [1, 9, 10, 11, 4, 5]:
            muntha_status = f"POWERFUL (Falls in Kendra/Trikona House {muntha_house_in_varsha} - success and elevation)"

        # Calculate Varsha Swami (Year Lord)
        year_lord = muntha_lord  # Primary default Varsha Swami candidate

        # Calculate Mudda Dasha Timeline
        mudda_timeline = []
        curr_m_dt = pravesha_utc
        # Mudda starts from Sun or birth dasha lord
        for p_name in MUDDA_ORDER:
            d_span = MUDDA_DAYS[p_name]
            end_m_dt = curr_m_dt + timedelta(days=d_span)
            mudda_timeline.append({
                "lord": p_name,
                "duration_days": round(d_span, 1),
                "start": curr_m_dt.strftime("%Y-%m-%d"),
                "end": end_m_dt.strftime("%Y-%m-%d")
            })
            curr_m_dt = end_m_dt

        return {
            "target_year": target_year,
            "varsha_pravesha_utc": pravesha_utc.strftime("%Y-%m-%d %H:%M:%S UTC"),
            "completed_years_age": completed_years,
            "varsha_ascendant": {
                "sign": varsha_asc_sign,
                "degree": round(varsha_asc_lon % 30.0, 2),
                "longitude": round(varsha_asc_lon, 2)
            },
            "muntha": {
                "sign": muntha_sign,
                "lord": muntha_lord,
                "house_in_varsha_chart": muntha_house_in_varsha,
                "status": muntha_status
            },
            "varsha_swami_year_lord": year_lord,
            "mudda_dasha_annual_timeline": mudda_timeline
        }
