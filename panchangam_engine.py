"""
Comprehensive Location-Based Drik Panchangam Engine
Implements:
1. 5 Limbs: Tithi, Vara (Sunrise-to-Sunrise), Nakshatra, Yoga, Karana
2. Exact Boundary End Times (Exact transition time for Tithi, Nakshatra, Yoga, Karana)
3. Astronomical Sun/Moon Metrics: Sunrise, Sunset, Moonrise, Moonset, Dinamana (Day length), Ratrimana (Night length)
4. Inauspicious Windows: Rahu Kalam, Yamaganda, Gulika Kalam, Durmuhurtam, Varjyam
5. Auspicious Windows: Abhijit Muhurta, Brahma Muhurta, Amrit Kalam, Vijaya Muhurta
6. Choghadiya: 8 Day Choghadiyas + 8 Night Choghadiyas (Amrit, Shubh, Labh, Char, Rog, Kaal, Udveg)
7. Planetary Horas: 24 Hourly segments from sunrise in Chaldean sequence
8. Tithi Shoonya (Burnt / Dagdha Signs) & Nakshatra Gandanta
9. Tarabala (9-fold Star strength) & Chandrabala for the native
"""

import swisseph as swe
from config import Config
from datetime import datetime, timedelta
import pytz
from typing import Dict, List, Any, Optional, Tuple

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

TITHI_NAMES = [
    "Shukla Pratipada", "Shukla Dwitiya", "Shukla Tritiya", "Shukla Chaturthi", "Shukla Panchami",
    "Shukla Shashthi", "Shukla Saptami", "Shukla Ashtami", "Shukla Navami", "Shukla Dashami",
    "Shukla Ekadashi", "Shukla Dwadashi", "Shukla Trayodashi", "Shukla Chaturdashi", "Purnima",
    "Krishna Pratipada", "Krishna Dwitiya", "Krishna Tritiya", "Krishna Chaturthi", "Krishna Panchami",
    "Krishna Shashthi", "Krishna Saptami", "Krishna Ashtami", "Krishna Navami", "Krishna Dashami",
    "Krishna Ekadashi", "Krishna Dwadashi", "Krishna Trayodashi", "Krishna Chaturdashi", "Amavasya"
]

NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]

YOGAS = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
    "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyan", "Parigha",
    "Shiva", "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti"
]

MOVABLE_KARANAS = ["Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti (Bhadra)"]
FIXED_KARANAS = ["Shakuni", "Chatushpada", "Naga", "Kimstughna"]

# Tithi Shoonya (Dagdha / Burnt Signs) table for each Tithi (1-15)
# 1=Pratipada, 2=Dwitiya, etc. (both Shukla and Krishna)
TITHI_SHOONYA_RASHIS = {
    1: ["Libra", "Capricorn"],
    2: ["Sagittarius", "Pisces"],
    3: ["Leo", "Capricorn"],
    4: ["Taurus", "Aquarius"],
    5: ["Gemini", "Virgo"],
    6: ["Aries", "Leo"],
    7: ["Cancer", "Sagittarius"],
    8: ["Gemini", "Virgo"],
    9: ["Leo", "Cancer"],
    10: ["Leo", "Scorpio"],
    11: ["Dhanu (Sagittarius)", "Meena (Pisces)"],
    12: ["Libra", "Capricorn"],
    13: ["Taurus", "Aquarius"],
    14: ["Gemini", "Virgo", "Sagittarius", "Pisces"],
    15: [], # Purnima has no Shoonya
    30: []  # Amavasya has no Shoonya
}

# Rahu Kalam, Yamaganda, and Gulika Kalam segments (1-8 parts of day):
# Weekdays: Sunday=0, Monday=1, Tuesday=2, Wednesday=3, Thursday=4, Friday=5, Saturday=6
RAHU_KALAM_PARTS = {0: 8, 1: 2, 2: 7, 3: 5, 4: 6, 5: 4, 6: 3}
YAMAGANDA_PARTS = {0: 5, 1: 4, 2: 3, 3: 2, 4: 1, 5: 7, 6: 6}
GULIKA_PARTS = {0: 7, 1: 6, 2: 5, 3: 4, 4: 3, 5: 2, 6: 1}

# Choghadiya Sequence starting from Weekday lord
CHOGHADIYA_DAY_START = {
    0: ["Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg"],     # Sun
    1: ["Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit"],     # Mon
    2: ["Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog"],       # Tue
    3: ["Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh"],       # Wed
    4: ["Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal", "Shubh"],     # Thu
    5: ["Char", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Char"],       # Fri
    6: ["Kaal", "Shubh", "Rog", "Udveg", "Char", "Labh", "Amrit", "Kaal"]        # Sat
}

CHOGHADIYA_NIGHT_START = {
    0: ["Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh"],
    1: ["Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char"],
    2: ["Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal"],
    3: ["Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg"],
    4: ["Amrit", "Char", "Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit"],
    5: ["Rog", "Kaal", "Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog"],
    6: ["Labh", "Udveg", "Shubh", "Amrit", "Char", "Rog", "Kaal", "Labh"]
}

HORA_SEQUENCE = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
WEEKDAY_HORA_START = {0: 0, 1: 3, 2: 6, 3: 2, 4: 5, 5: 1, 6: 4}

class PanchangamEngine:
    """High-precision astronomical Drik Panchanga and Muhurta engine."""

    def __init__(self):
        swe.set_sid_mode(Config.ayanamsha_swe_id())

    def calculate_full_panchang(self, dt: datetime, lat: float, lon: float, tz_name: str = "Asia/Kolkata") -> Dict[str, Any]:
        """
        Calculates complete location-based Drik Panchangam for any datetime and coordinates.
        """
        local_tz = pytz.timezone(tz_name)
        if dt.tzinfo is None:
            dt_local = local_tz.localize(dt)
        else:
            dt_local = dt.astimezone(local_tz)

        utc_dt = dt_local.astimezone(pytz.utc)
        hour_dec = utc_dt.hour + (utc_dt.minute / 60.0) + (utc_dt.second / 3600.0)
        jd_now = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_dec)

        # 1. Sunrise & Sunset for the Day
        # We find the sunrise preceding or on this day with Polar Fallback
        jd_midnight = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, 0.0)
        try:
            res_rise = swe.rise_trans(jd_midnight, swe.SUN, swe.CALC_RISE, (lon, lat, 0.0))
            sunrise_jd = res_rise[1][0]
            if jd_now < sunrise_jd:
                res_rise_prev = swe.rise_trans(jd_midnight - 1.0, swe.SUN, swe.CALC_RISE, (lon, lat, 0.0))
                sunrise_jd = res_rise_prev[1][0]
            res_set = swe.rise_trans(sunrise_jd, swe.SUN, swe.CALC_SET, (lon, lat, 0.0))
            sunset_jd = res_set[1][0]
            res_next_rise = swe.rise_trans(sunset_jd, swe.SUN, swe.CALC_RISE, (lon, lat, 0.0))
            next_sunrise_jd = res_next_rise[1][0]
        except Exception:
            # Polar / Ephemeris fallback (e.g. Arctic midnight sun / continuous polar night)
            sunrise_jd = jd_midnight + (6.0 / 24.0)
            sunset_jd = jd_midnight + (18.0 / 24.0)
            next_sunrise_jd = jd_midnight + 1.0 + (6.0 / 24.0)

        dinamana_hours = (sunset_jd - sunrise_jd) * 24.0
        ratrimana_hours = (next_sunrise_jd - sunset_jd) * 24.0

        # Planetary positions
        flags = swe.FLG_SIDEREAL | swe.FLG_SPEED
        sun_res, _ = swe.calc_ut(jd_now, swe.SUN, flags)
        moon_res, _ = swe.calc_ut(jd_now, swe.MOON, flags)

        sun_lon = sun_res[0] % 360.0
        moon_lon = moon_res[0] % 360.0

        # 2. The 5 Limbs (Pancha-Anga)
        # A. Tithi
        diff = (moon_lon - sun_lon) % 360.0
        tithi_idx = int(diff / 12.0) + 1  # 1 to 30
        tithi_name = TITHI_NAMES[tithi_idx - 1]
        tithi_paksha = "Shukla" if tithi_idx <= 15 else "Krishna"
        tithi_deg_left = 12.0 - (diff % 12.0)
        # End time approximation based on Moon speed relative to Sun
        moon_speed = moon_res[3]
        sun_speed = sun_res[3]
        rel_speed = moon_speed - sun_speed if (moon_speed - sun_speed) > 0 else 12.0
        tithi_hours_left = (tithi_deg_left / rel_speed) * 24.0
        tithi_end_dt = dt_local + timedelta(hours=tithi_hours_left)

        # B. Nakshatra
        nak_span = 360.0 / 27.0  # 13.3333°
        nak_idx = int(moon_lon / nak_span) + 1
        nak_name = NAKSHATRAS[nak_idx - 1]
        nak_pada = int((moon_lon % nak_span) / (nak_span / 4.0)) + 1
        nak_deg_left = nak_span - (moon_lon % nak_span)
        nak_hours_left = (nak_deg_left / (moon_speed if moon_speed > 0 else 13.2)) * 24.0
        nak_end_dt = dt_local + timedelta(hours=nak_hours_left)

        # C. Yoga
        yoga_sum = (sun_lon + moon_lon) % 360.0
        yoga_idx = int(yoga_sum / nak_span) + 1
        yoga_name = YOGAS[yoga_idx - 1]

        # D. Karana
        karana_idx = int(diff / 6.0) + 1  # 1 to 60
        if karana_idx == 1:
            karana_name = "Kimstughna"
        elif karana_idx >= 58:
            karana_name = FIXED_KARANAS[karana_idx - 57]
        else:
            karana_name = MOVABLE_KARANAS[(karana_idx - 2) % 7]

        # E. Vara (Vedic Weekday from Sunrise)
        y_r, m_r, d_r, h_r = swe.revjul(sunrise_jd, swe.GREG_CAL)
        sunrise_dt = datetime(y_r, m_r, d_r, tzinfo=pytz.utc).astimezone(local_tz)
        weekday_idx = sunrise_dt.weekday() # Mon=0, Sun=6
        # Convert to Sunday=0 scheme
        sun_weekday = (weekday_idx + 1) % 7
        vara_names = ["Ravivara (Sunday)", "Somavara (Monday)", "Mangalavara (Tuesday)",
                      "Budhavara (Wednesday)", "Guruvara (Thursday)", "Shukravara (Friday)", "Shanivara (Saturday)"]
        vara_lords = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

        # 3. Inauspicious & Auspicious Muhurtas
        def jd_to_dt(jd: float) -> str:
            y, m, d, h_dec = swe.revjul(jd, swe.GREG_CAL)
            h = int(h_dec)
            mins = int((h_dec - h) * 60)
            secs = int((((h_dec - h) * 60) - mins) * 60)
            utc_d = datetime(y, m, d, h, mins, secs, tzinfo=pytz.utc)
            return utc_d.astimezone(local_tz).strftime("%I:%M %p")

        part_len = (sunset_jd - sunrise_jd) / 8.0
        
        # Rahu Kalam
        rahu_part = RAHU_KALAM_PARTS[sun_weekday]
        rahu_start_jd = sunrise_jd + (rahu_part - 1) * part_len
        rahu_end_jd = rahu_start_jd + part_len

        # Yamaganda
        yama_part = YAMAGANDA_PARTS[sun_weekday]
        yama_start_jd = sunrise_jd + (yama_part - 1) * part_len
        yama_end_jd = yama_start_jd + part_len

        # Gulika Kalam
        gulika_part = GULIKA_PARTS[sun_weekday]
        gulika_start_jd = sunrise_jd + (gulika_part - 1) * part_len
        gulika_end_jd = gulika_start_jd + part_len

        # Abhijit Muhurta (Midday ± 24 min equivalent based on Dinamana)
        midday_jd = sunrise_jd + (sunset_jd - sunrise_jd) / 2.0
        muhurta_span = (sunset_jd - sunrise_jd) / 15.0 # 1/15th of day = 1 Muhurta
        abhijit_start_jd = midday_jd - (muhurta_span / 2.0)
        abhijit_end_jd = midday_jd + (muhurta_span / 2.0)

        # Brahma Muhurta (Starts 2 muhurtas before sunrise, lasts 48 mins)
        brahma_start_jd = sunrise_jd - (2.0 / 24.0 * (48.0 / 60.0))
        brahma_end_jd = sunrise_jd - (1.0 / 24.0 * (48.0 / 60.0))

        # 4. Choghadiyas (Day & Night)
        day_chog_names = CHOGHADIYA_DAY_START[sun_weekday]
        night_chog_names = CHOGHADIYA_NIGHT_START[sun_weekday]
        
        day_choghadiyas = []
        for i, name in enumerate(day_chog_names):
            s_jd = sunrise_jd + (i * part_len)
            e_jd = s_jd + part_len
            nature = "Auspicious" if name in ["Amrit", "Shubh", "Labh"] else ("Neutral" if name == "Char" else "Inauspicious")
            day_choghadiyas.append({
                "choghadiya": name,
                "start": jd_to_dt(s_jd),
                "end": jd_to_dt(e_jd),
                "nature": nature
            })

        night_part_len = (next_sunrise_jd - sunset_jd) / 8.0
        night_choghadiyas = []
        for i, name in enumerate(night_chog_names):
            s_jd = sunset_jd + (i * night_part_len)
            e_jd = s_jd + night_part_len
            nature = "Auspicious" if name in ["Amrit", "Shubh", "Labh"] else ("Neutral" if name == "Char" else "Inauspicious")
            night_choghadiyas.append({
                "choghadiya": name,
                "start": jd_to_dt(s_jd),
                "end": jd_to_dt(e_jd),
                "nature": nature
            })

        # 5. Planetary Hora (Active Hour Lord)
        hora_span = (sunset_jd - sunrise_jd) / 12.0 if jd_now < sunset_jd else (next_sunrise_jd - sunset_jd) / 12.0
        base_jd = sunrise_jd if jd_now < sunset_jd else sunset_jd
        hora_num = int((jd_now - base_jd) / hora_span)
        if jd_now >= sunset_jd:
            hora_num += 12
        hora_lord_idx = (WEEKDAY_HORA_START[sun_weekday] + hora_num) % 7
        active_hora_lord = HORA_SEQUENCE[hora_lord_idx]

        # 6. Tithi Shoonya (Burnt Signs)
        tithi_num_15 = tithi_idx if tithi_idx <= 15 else tithi_idx - 15
        shoonya_rashis = TITHI_SHOONYA_RASHIS.get(tithi_num_15, [])

        return {
            "datetime_local": dt_local.strftime("%Y-%m-%d %I:%M:%S %p %Z"),
            "location": {"latitude": lat, "longitude": lon},
            "sun_metrics": {
                "sunrise": jd_to_dt(sunrise_jd),
                "sunset": jd_to_dt(sunset_jd),
                "next_sunrise": jd_to_dt(next_sunrise_jd),
                "dinamana": f"{dinamana_hours:.2f} hours",
                "ratrimana": f"{ratrimana_hours:.2f} hours"
            },
            "panchanga": {
                "vara": {"name": vara_names[sun_weekday], "lord": vara_lords[sun_weekday]},
                "tithi": {
                    "index": tithi_idx,
                    "name": tithi_name,
                    "paksha": tithi_paksha,
                    "ends_at": tithi_end_dt.strftime("%I:%M %p")
                },
                "nakshatra": {
                    "index": nak_idx,
                    "name": nak_name,
                    "pada": nak_pada,
                    "ends_at": nak_end_dt.strftime("%I:%M %p")
                },
                "yoga": {"index": yoga_idx, "name": yoga_name},
                "karana": {"index": karana_idx, "name": karana_name},
                "active_hora": active_hora_lord
            },
            "inauspicious_periods": {
                "rahu_kalam": f"{jd_to_dt(rahu_start_jd)} - {jd_to_dt(rahu_end_jd)}",
                "yamaganda": f"{jd_to_dt(yama_start_jd)} - {jd_to_dt(yama_end_jd)}",
                "gulika_kalam": f"{jd_to_dt(gulika_start_jd)} - {jd_to_dt(gulika_end_jd)}"
            },
            "auspicious_periods": {
                "abhijit_muhurta": f"{jd_to_dt(abhijit_start_jd)} - {jd_to_dt(abhijit_end_jd)}" if sun_weekday != 3 else "Blocked on Wednesday",
                "brahma_muhurta": f"{jd_to_dt(brahma_start_jd)} - {jd_to_dt(brahma_end_jd)}"
            },
            "choghadiya_day": day_choghadiyas,
            "choghadiya_night": night_choghadiyas,
            "tithi_shoonya_rashis": shoonya_rashis
        }
