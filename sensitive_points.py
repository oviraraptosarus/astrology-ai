"""
Sensitive Points & Critical Diagnostic Degrees Engine
Implements:
1. 22nd Drekkana (Kharesh / 8th house in D3)
2. 64th Navamsha (Khara Navamsha / 4th from Moon & Lagna in D9)
3. Mrityu Bhaga (Exact fatal degrees for 9 Grahas + Lagna per Saravali/Jataka Parijata)
4. Gandanta Zones (Revati-Ashwini, Ashlesha-Magha, Jyeshtha-Mula at Lagna/Moon/Tithi level)
5. Pushkara Navamsha & Pushkara Bhaga (Auspicious wealth/protection degrees)
6. Bhrigu Bindu (Rahu-Moon Midpoint)
7. Indu Lagna (Wealth Ascendant)
"""

from typing import Dict, List, Any, Optional
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

# Ray values (Kalas) for Indu Lagna calculation according to classical text
INDU_LAGNA_RAYS = {
    "Sun": 30,
    "Moon": 16,
    "Mars": 6,
    "Mercury": 8,
    "Jupiter": 10,
    "Venus": 12,
    "Saturn": 1
}

# Mrityu Bhaga (Fatal Degrees in integer degrees 1-30 for each sign 0-11)
MRITYU_BHAGA_TABLE = {
    "Sun": [20, 9, 12, 6, 8, 24, 16, 17, 22, 2, 3, 23],
    "Moon": [26, 12, 13, 25, 24, 11, 26, 14, 13, 25, 5, 12],
    "Mars": [19, 28, 25, 23, 29, 28, 14, 21, 2, 15, 11, 6],
    "Mercury": [15, 14, 13, 12, 8, 18, 20, 10, 21, 22, 7, 5],
    "Jupiter": [19, 29, 12, 27, 6, 4, 13, 10, 17, 11, 15, 28],
    "Venus": [28, 15, 11, 17, 10, 13, 4, 6, 27, 12, 29, 19],
    "Saturn": [10, 4, 7, 9, 12, 16, 3, 18, 28, 14, 13, 15],
    "Rahu": [14, 13, 12, 11, 24, 23, 24, 11, 10, 20, 18, 8],
    "Ketu": [8, 18, 20, 10, 21, 22, 7, 5, 14, 13, 12, 11],
    "Ascendant": [1, 9, 22, 22, 25, 2, 4, 23, 18, 20, 24, 10]
}

PUSHKARA_BHAGA_TABLE = {
    0: 21, 1: 14, 2: 18, 3: 8, 4: 19, 5: 9,
    6: 24, 7: 11, 8: 23, 9: 14, 10: 19, 11: 9
}

PUSHKARA_NAVAMSHA_RANGES = {
    0: [(20.0, 23.3333, "Libra"), (26.6667, 30.0, "Sagittarius")],
    4: [(20.0, 23.3333, "Libra"), (26.6667, 30.0, "Sagittarius")],
    8: [(20.0, 23.3333, "Libra"), (26.6667, 30.0, "Sagittarius")],
    1: [(6.6667, 10.0, "Pisces"), (13.3333, 16.6667, "Taurus")],
    5: [(6.6667, 10.0, "Pisces"), (13.3333, 16.6667, "Taurus")],
    9: [(6.6667, 10.0, "Pisces"), (13.3333, 16.6667, "Taurus")],
    2: [(16.6667, 20.0, "Pisces"), (23.3333, 26.6667, "Taurus")],
    6: [(16.6667, 20.0, "Pisces"), (23.3333, 26.6667, "Taurus")],
    10: [(16.6667, 20.0, "Pisces"), (23.3333, 26.6667, "Taurus")],
    3: [(0.0, 3.3333, "Cancer"), (6.6667, 10.0, "Virgo")],
    7: [(0.0, 3.3333, "Cancer"), (6.6667, 10.0, "Virgo")],
    11: [(0.0, 3.3333, "Cancer"), (6.6667, 10.0, "Virgo")]
}

class SensitivePointsEngine:
    """Calculates all sensitive, critical, and fortune points for a Vedic chart."""

    def __init__(self, chart: Chart):
        self.chart = chart

    def _get_lagna_lon(self) -> float:
        if hasattr(self.chart, "ascendant") and hasattr(self.chart.ascendant, "longitude"):
            return self.chart.ascendant.longitude
        if hasattr(self.chart, "ascendant_sign") and hasattr(self.chart, "ascendant_degree"):
            sign_idx = ZODIAC_SIGNS.index(self.chart.ascendant_sign) if self.chart.ascendant_sign in ZODIAC_SIGNS else 0
            return (sign_idx * 30.0) + self.chart.ascendant_degree
        return 0.0

    def calculate_all(self) -> Dict[str, Any]:
        return {
            "22nd_drekkana": self.calculate_22nd_drekkana(),
            "64th_navamsha": self.calculate_64th_navamsha(),
            "mrityu_bhagas": self.check_mrityu_bhagas(),
            "gandanta_points": self.check_gandantas(),
            "pushkara_status": self.check_pushkaras(),
            "bhrigu_bindu": self.calculate_bhrigu_bindu(),
            "indu_lagna": self.calculate_indu_lagna()
        }

    def calculate_22nd_drekkana(self) -> Dict[str, Any]:
        lagna_lon = self._get_lagna_lon()
        sign_idx = int(lagna_lon / 30)
        deg_in_sign = lagna_lon % 30
        drekkana_part = int(deg_in_sign / 10)  # 0, 1, or 2

        eighth_sign_idx = (sign_idx + 7) % 12
        if drekkana_part == 0:
            d3_sign_idx = eighth_sign_idx
        elif drekkana_part == 1:
            d3_sign_idx = (eighth_sign_idx + 4) % 12
        else:
            d3_sign_idx = (eighth_sign_idx + 8) % 12

        d3_sign_name = ZODIAC_SIGNS[d3_sign_idx]
        kharesh_lord = SIGN_LORDS[d3_sign_name]

        return {
            "d3_sign": d3_sign_name,
            "kharesh_lord": kharesh_lord,
            "description": f"22nd Drekkana falls in {d3_sign_name} governed by {kharesh_lord}."
        }

    def calculate_64th_navamsha(self) -> Dict[str, Any]:
        results = {}
        lagna_lon = self._get_lagna_lon()
        lagna_d9_lon = (lagna_lon * 9) % 360
        lagna_d9_sign_idx = int(lagna_d9_lon / 30)
        lagna_64th_sign_idx = (lagna_d9_sign_idx + 3) % 12
        results["from_lagna"] = {
            "d9_sign": ZODIAC_SIGNS[lagna_64th_sign_idx],
            "lord": SIGN_LORDS[ZODIAC_SIGNS[lagna_64th_sign_idx]],
            "d1_arc_start_deg": round((lagna_lon + 210.0) % 360, 2)
        }

        moon = self.chart.planets.get("Moon")
        if moon:
            moon_lon = moon.longitude
            moon_d9_lon = (moon_lon * 9) % 360
            moon_d9_sign_idx = int(moon_d9_lon / 30)
            moon_64th_sign_idx = (moon_d9_sign_idx + 3) % 12
            results["from_moon"] = {
                "d9_sign": ZODIAC_SIGNS[moon_64th_sign_idx],
                "lord": SIGN_LORDS[ZODIAC_SIGNS[moon_64th_sign_idx]],
                "d1_arc_start_deg": round((moon_lon + 210.0) % 360, 2)
            }
        return results

    def check_mrityu_bhagas(self) -> List[Dict[str, Any]]:
        afflicted = []
        for p_name, p in self.chart.planets.items():
            if p_name not in MRITYU_BHAGA_TABLE:
                continue
            sign_idx = int(p.longitude / 30)
            deg_in_sign = p.longitude % 30
            mb_deg = MRITYU_BHAGA_TABLE[p_name][sign_idx]
            diff = abs(deg_in_sign - mb_deg)
            if diff <= 1.0:
                afflicted.append({
                    "entity": p_name,
                    "sign": ZODIAC_SIGNS[sign_idx],
                    "degree": round(deg_in_sign, 2),
                    "mrityu_bhaga_degree": mb_deg,
                    "orb_diff": round(diff, 2),
                    "status": "EXACT_MRITYU_BHAGA" if diff <= 0.5 else "NEAR_MRITYU_BHAGA",
                    "severity": "CRITICAL"
                })

        lagna_lon = self._get_lagna_lon()
        sign_idx = int(lagna_lon / 30)
        deg_in_sign = lagna_lon % 30
        mb_deg = MRITYU_BHAGA_TABLE["Ascendant"][sign_idx]
        diff = abs(deg_in_sign - mb_deg)
        if diff <= 1.0:
            afflicted.append({
                "entity": "Ascendant",
                "sign": ZODIAC_SIGNS[sign_idx],
                "degree": round(deg_in_sign, 2),
                "mrityu_bhaga_degree": mb_deg,
                "orb_diff": round(diff, 2),
                "status": "EXACT_MRITYU_BHAGA" if diff <= 0.5 else "NEAR_MRITYU_BHAGA",
                "severity": "CRITICAL"
            })

        return afflicted

    def check_gandantas(self) -> List[Dict[str, Any]]:
        gandanta_knots = [
            (356.6667, 360.0, "Revati (Pisces)", "Abhukta/Junction Gandanta"),
            (0.0, 3.3333, "Ashwini (Aries)", "Ashwini Nakshatra Gandanta"),
            (116.6667, 120.0, "Ashlesha (Cancer)", "Ashlesha Nakshatra Gandanta"),
            (120.0, 123.3333, "Magha (Leo)", "Magha Nakshatra Gandanta"),
            (236.6667, 240.0, "Jyeshtha (Scorpio)", "Jyeshtha Nakshatra Gandanta"),
            (240.0, 243.3333, "Mula (Sagittarius)", "Mula Nakshatra Gandanta")
        ]

        results = []
        for p_name, p in self.chart.planets.items():
            lon = p.longitude % 360
            for start, end, knot_name, desc in gandanta_knots:
                if start <= lon <= end:
                    results.append({
                        "entity": p_name,
                        "longitude": round(lon, 2),
                        "knot": knot_name,
                        "type": desc
                    })

        lagna_lon = self._get_lagna_lon() % 360
        for start, end, knot_name, desc in gandanta_knots:
            if start <= lagna_lon <= end:
                results.append({
                    "entity": "Ascendant",
                    "longitude": round(lagna_lon, 2),
                    "knot": knot_name,
                    "type": f"Lagna Gandanta ({desc})"
                })

        return results

    def check_pushkaras(self) -> Dict[str, Any]:
        pushkara_planets = []
        for p_name, p in self.chart.planets.items():
            sign_idx = int(p.longitude / 30)
            deg_in_sign = p.longitude % 30

            pb_deg = PUSHKARA_BHAGA_TABLE.get(sign_idx)
            is_pb = abs(deg_in_sign - pb_deg) <= 1.0 if pb_deg is not None else False

            ranges = PUSHKARA_NAVAMSHA_RANGES.get(sign_idx, [])
            in_pn = False
            pn_nav_sign = None
            for start, end, nav_sign in ranges:
                if start <= deg_in_sign < end:
                    in_pn = True
                    pn_nav_sign = nav_sign
                    break

            if in_pn or is_pb:
                pushkara_planets.append({
                    "planet": p_name,
                    "sign": ZODIAC_SIGNS[sign_idx],
                    "degree": round(deg_in_sign, 2),
                    "pushkara_navamsha": in_pn,
                    "navamsha_sign": pn_nav_sign,
                    "pushkara_bhaga": is_pb
                })

        return {
            "total_pushkara_planets": len(pushkara_planets),
            "planets": pushkara_planets
        }

    def calculate_bhrigu_bindu(self) -> Dict[str, Any]:
        moon = self.chart.planets.get("Moon")
        rahu = self.chart.planets.get("Rahu")
        if not moon or not rahu:
            return {}

        moon_lon = moon.longitude % 360
        rahu_lon = rahu.longitude % 360

        if moon_lon >= rahu_lon:
            dist = moon_lon - rahu_lon
        else:
            dist = (360.0 - rahu_lon) + moon_lon

        midpoint_lon = (rahu_lon + (dist / 2.0)) % 360
        sign_idx = int(midpoint_lon / 30)
        deg_in_sign = midpoint_lon % 30

        return {
            "longitude": round(midpoint_lon, 2),
            "sign": ZODIAC_SIGNS[sign_idx],
            "degree_in_sign": round(deg_in_sign, 2),
            "sign_lord": SIGN_LORDS[ZODIAC_SIGNS[sign_idx]]
        }

    def calculate_indu_lagna(self) -> Dict[str, Any]:
        lagna_sign_idx = int(self._get_lagna_lon() / 30)
        moon = self.chart.planets.get("Moon")
        if not moon:
            return {}
        moon_sign_idx = int(moon.longitude / 30)

        ninth_from_lagna_sign = ZODIAC_SIGNS[(lagna_sign_idx + 8) % 12]
        ninth_from_lagna_lord = SIGN_LORDS[ninth_from_lagna_sign]

        ninth_from_moon_sign = ZODIAC_SIGNS[(moon_sign_idx + 8) % 12]
        ninth_from_moon_lord = SIGN_LORDS[ninth_from_moon_sign]

        rays_lagna = INDU_LAGNA_RAYS.get(ninth_from_lagna_lord, 0)
        rays_moon = INDU_LAGNA_RAYS.get(ninth_from_moon_lord, 0)
        total_rays = rays_lagna + rays_moon

        remainder = total_rays % 12
        if remainder == 0:
            remainder = 12

        indu_lagna_sign_idx = (moon_sign_idx + remainder - 1) % 12
        indu_lagna_sign = ZODIAC_SIGNS[indu_lagna_sign_idx]

        planets_in_indu = [
            p_name for p_name, p in self.chart.planets.items()
            if int(p.longitude / 30) == indu_lagna_sign_idx
        ]

        return {
            "indu_lagna_sign": indu_lagna_sign,
            "total_rays": total_rays,
            "planets_in_indu_lagna": planets_in_indu,
            "wealth_grade": "EXTRAORDINARY_WEALTH" if any(p in ["Jupiter", "Venus", "Mercury", "Moon"] for p in planets_in_indu) else "STANDARD"
        }
