"""
C.S. Patel Ashtakavarga Kakshya Timing Engine
Implements:
1. Division of each 30-degree sign into 8 Kakshyas (3°45' each).
2. Kakshya Order: Saturn (0°-3°45'), Jupiter (3°45'-7°30'), Mars (7°30'-11°15'), 
   Sun (11°15'-15°00'), Venus (15°00'-18°45'), Mercury (18°45'-22°30'), 
   Moon (22°30'-26°15'), Lagna (26°15'-30°00').
3. Prashtarashtakavarga (PAV) Bindu Contribution Matrix (56 x 12 grid).
4. Real-time transit evaluation: Active Kakshya Bindu (1 = Event Manifests, 0 = Blocked/Fruitless).
5. 3.5-day window generator for any transiting planet.
"""
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import pytz
import swisseph as swe
from config import Config

from vedic_models import Chart, Planet
from ashtakavarga_engine import AshtakavargaEngine

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

KAKSHYA_LORDS = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Lagna"]
KAKSHYA_SPAN = 30.0 / 8.0  # 3.75 degrees = 3°45'

# Classical Ashtakavarga Benefic Contribution Rules (From BPHS & C.S. Patel)
# For each planet, the houses from itself, Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Lagna that give 1 bindu
ASHTAKAVARGA_RULES = {
    "Sun": {
        "Sun": [1, 2, 4, 7, 8, 9, 10, 11], "Moon": [3, 6, 10, 11], "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 10, 11, 12], "Jupiter": [5, 6, 9, 11], "Venus": [6, 7, 12],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11], "Lagna": [3, 4, 6, 10, 11, 12]
    },
    "Moon": {
        "Sun": [3, 6, 7, 8, 10, 11], "Moon": [1, 3, 6, 7, 10, 11], "Mars": [2, 3, 5, 6, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11], "Jupiter": [1, 4, 7, 8, 10, 11, 12], "Venus": [3, 4, 5, 7, 9, 10, 11],
        "Saturn": [3, 5, 6, 11], "Lagna": [3, 6, 10, 11]
    },
    "Mars": {
        "Sun": [3, 5, 6, 10, 11], "Moon": [3, 6, 11], "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 11], "Jupiter": [6, 10, 11, 12], "Venus": [6, 8, 11, 12],
        "Saturn": [1, 4, 7, 8, 9, 10, 11], "Lagna": [1, 3, 6, 10, 11]
    },
    "Mercury": {
        "Sun": [5, 6, 9, 11, 12], "Moon": [2, 4, 6, 8, 10, 11], "Mars": [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12], "Jupiter": [6, 8, 11, 12], "Venus": [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn": [1, 2, 4, 7, 8, 9, 10, 11], "Lagna": [1, 2, 4, 6, 8, 10, 11]
    },
    "Jupiter": {
        "Sun": [1, 2, 3, 4, 7, 8, 9, 10, 11], "Moon": [2, 5, 7, 9, 11], "Mars": [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11], "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11], "Venus": [2, 5, 6, 9, 10, 11],
        "Saturn": [3, 5, 6, 12], "Lagna": [1, 2, 4, 5, 6, 7, 9, 10, 11]
    },
    "Venus": {
        "Sun": [8, 11, 12], "Moon": [1, 2, 3, 4, 5, 8, 9, 11, 12], "Mars": [3, 5, 6, 9, 11, 12],
        "Mercury": [3, 5, 6, 9, 11], "Jupiter": [5, 8, 9, 10, 11], "Venus": [1, 2, 3, 4, 5, 8, 9, 10, 11],
        "Saturn": [3, 4, 5, 8, 9, 10, 11], "Lagna": [1, 2, 3, 4, 5, 8, 9, 11]
    },
    "Saturn": {
        "Sun": [1, 2, 4, 7, 8, 10, 11], "Moon": [3, 6, 11], "Mars": [3, 5, 6, 10, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12], "Jupiter": [5, 6, 11, 12], "Venus": [6, 11, 12],
        "Saturn": [3, 5, 6, 11], "Lagna": [1, 3, 4, 6, 10, 11]
    }
}

class AshtakavargaKakshyaEngine:
    def __init__(self, chart: Chart):
        self.chart = chart
        self.pav_tables = self._generate_prashtarashtakavarga()

    def _generate_prashtarashtakavarga(self) -> Dict[str, List[List[int]]]:
        """Generates 8x12 Prashtarashtakavarga (PAV) matrix for each planet."""
        lagna_sign_idx = ZODIAC_SIGNS.index(self.chart.ascendant_sign) if hasattr(self.chart, "ascendant_sign") and self.chart.ascendant_sign in ZODIAC_SIGNS else int(self.chart.ascendant.longitude / 30)
        
        planet_signs = {}
        for p_name in ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
            p = self.chart.planets.get(p_name)
            planet_signs[p_name] = ZODIAC_SIGNS.index(p.sign) if p else 0
        planet_signs["Lagna"] = lagna_sign_idx

        pav = {}
        for target_p, rules in ASHTAKAVARGA_RULES.items():
            # 8 rows (contributors: Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon, Lagna), 12 columns (signs)
            grid = [[0 for _ in range(12)] for _ in range(8)]
            for row_idx, contributor in enumerate(KAKSHYA_LORDS):
                contrib_sign = planet_signs[contributor]
                benefic_houses = rules.get(contributor, [])
                for h in benefic_houses:
                    sign_col = (contrib_sign + h - 1) % 12
                    grid[row_idx][sign_col] = 1
            pav[target_p] = grid
        return pav

    def get_kakshya_info(self, planet_name: str, longitude: float) -> Dict[str, Any]:
        """Determines the active Kakshya Lord and bindu status for a given transit degree."""
        sign_idx = int(longitude / 30.0)
        deg_in_sign = longitude % 30.0
        kakshya_idx = int(deg_in_sign / KAKSHYA_SPAN)
        kakshya_idx = min(7, max(0, kakshya_idx))

        kakshya_lord = KAKSHYA_LORDS[kakshya_idx]
        deg_start = kakshya_idx * KAKSHYA_SPAN
        deg_end = (kakshya_idx + 1) * KAKSHYA_SPAN

        # Check PAV bindu
        has_bindu = False
        if planet_name in self.pav_tables:
            has_bindu = (self.pav_tables[planet_name][kakshya_idx][sign_idx] == 1)

        status = "FRUITFUL (1 Bindu Contributed)" if has_bindu else "UNFRUITFUL / BARREN (0 Bindus - Efforts Blocked)"

        return {
            "planet": planet_name,
            "sign": ZODIAC_SIGNS[sign_idx],
            "degree_in_sign": round(deg_in_sign, 2),
            "kakshya_index": kakshya_idx + 1,
            "kakshya_lord": kakshya_lord,
            "kakshya_span": f"{deg_start:.2f}° to {deg_end:.2f}°",
            "has_bindu": has_bindu,
            "status": status
        }

    def scan_kakshya_windows(self, planet_name: str, start_dt: datetime, duration_days: int = 30) -> List[Dict[str, Any]]:
        """Scans daily transits to produce exact 3.5-day Kakshya manifestation windows."""
        swe_map = {
            "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
            "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN
        }
        if planet_name not in swe_map:
            return []

        swe.set_sid_mode(Config.ayanamsha_swe_id())
        windows = []
        curr_dt = start_dt
        end_dt = start_dt + timedelta(days=duration_days)

        prev_kakshya = None
        window_start = curr_dt

        while curr_dt <= end_dt:
            hour_dec = curr_dt.hour + (curr_dt.minute / 60.0)
            jd = swe.julday(curr_dt.year, curr_dt.month, curr_dt.day, hour_dec)
            res, _ = swe.calc_ut(jd, swe_map[planet_name], swe.FLG_SIDEREAL)
            lon = res[0] % 360.0
            
            info = self.get_kakshya_info(planet_name, lon)
            k_key = (info["sign"], info["kakshya_index"], info["has_bindu"])

            if prev_kakshya is None:
                prev_kakshya = k_key
                window_start = curr_dt

            if k_key != prev_kakshya:
                windows.append({
                    "planet": planet_name,
                    "sign": prev_kakshya[0],
                    "kakshya_lord": KAKSHYA_LORDS[prev_kakshya[1] - 1],
                    "has_bindu": prev_kakshya[2],
                    "status": "FRUITFUL (Active Event Window)" if prev_kakshya[2] else "BARREN (Blocked Window)",
                    "start_date": window_start.strftime("%Y-%m-%d"),
                    "end_date": curr_dt.strftime("%Y-%m-%d")
                })
                prev_kakshya = k_key
                window_start = curr_dt

            curr_dt += timedelta(days=1)

        return windows
