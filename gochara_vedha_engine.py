"""
Classical Gochara Vedha & Vipareeta Vedha Engine (Phaladeepika Ch. 26 & Brihat Samhita)
Implements:
1. Classical Benefic Transit Houses from Natal Moon for all 9 Planets.
2. Classical Vedha (Obstruction) House Matrix for each planet.
3. Special Non-Vedha exemptions:
   - Sun and Saturn do NOT cause Vedha to each other (Father & Son).
   - Moon and Mercury do NOT cause Vedha to each other (Father & Son).
4. Real-time Gochara Evaluation:
   - Benefic Transit: UNBLOCKED vs BLOCKED by Vedha.
   - Malefic Transit: HARMFUL vs NEUTRALIZED by Vipareeta Vedha.
"""
from typing import Dict, Any, List, Tuple
from datetime import datetime
import pytz
import swisseph as swe

from vedic_models import Chart, Planet
from config import Config

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# (Benefic House, Obstructing Vedha House) pairs from Natal Moon
GOCHARA_VEDHA_RULES = {
    "Sun": [(3, 9), (6, 12), (10, 4), (11, 5)],
    "Moon": [(1, 5), (3, 9), (6, 12), (7, 2), (10, 4), (11, 8)],
    "Mars": [(3, 12), (6, 9), (11, 5)],
    "Mercury": [(2, 5), (4, 3), (6, 9), (8, 1), (10, 8), (11, 12)],
    "Jupiter": [(2, 12), (5, 4), (7, 3), (9, 10), (11, 8)],
    "Venus": [(1, 8), (2, 7), (3, 1), (4, 10), (5, 9), (8, 5), (9, 11), (11, 6), (12, 3)],
    "Saturn": [(3, 12), (6, 9), (11, 5)],
    "Rahu": [(3, 12), (6, 9), (11, 5)],
    "Ketu": [(3, 12), (6, 9), (11, 5)]
}

SWE_PLANETS_MAP = {
    "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN,
    # Canonical Parashari node model (config-driven; matches astrology_engine).
    "Rahu": Config.node_swe_id(), "Ketu": Config.node_swe_id()
}

class GocharaVedhaEngine:
    def __init__(self, chart: Chart):
        self.chart = chart
        self.moon = chart.planets.get("Moon")
        self.moon_sign_idx = ZODIAC_SIGNS.index(self.moon.sign) if self.moon else 0

    def evaluate_all_transits(self, target_dt: datetime = None) -> Dict[str, Any]:
        """Evaluates Vedha & Vipareeta Vedha for all transiting planets at target_dt."""
        if target_dt is None:
            target_dt = datetime.now(pytz.utc)
        elif target_dt.tzinfo is None:
            target_dt = pytz.utc.localize(target_dt)

        swe.set_sid_mode(Config.ayanamsha_swe_id())
        hour_dec = target_dt.hour + (target_dt.minute / 60.0)
        jd = swe.julday(target_dt.year, target_dt.month, target_dt.day, hour_dec)

        # Get all live planetary positions
        transit_houses = {}
        for pname, pcode in SWE_PLANETS_MAP.items():
            if pname == "Ketu":
                res, _ = swe.calc_ut(jd, Config.node_swe_id(), swe.FLG_SIDEREAL)
                lon = (res[0] + 180.0) % 360.0
            else:
                res, _ = swe.calc_ut(jd, pcode, swe.FLG_SIDEREAL)
                lon = res[0] % 360.0

            sign_idx = int(lon / 30.0)
            h_from_moon = ((sign_idx - self.moon_sign_idx) % 12) + 1
            transit_houses[pname] = {
                "longitude": round(lon, 2),
                "sign": ZODIAC_SIGNS[sign_idx],
                "house_from_moon": h_from_moon
            }

        evaluations = {}
        for pname, rules in GOCHARA_VEDHA_RULES.items():
            t_info = transit_houses[pname]
            curr_h = t_info["house_from_moon"]
            
            # Check if current house is inherently benefic
            benefic_rule = next((r for r in rules if r[0] == curr_h), None)
            
            if benefic_rule:
                # Transiting in benefic house
                vedha_h = benefic_rule[1]
                obstructing_planets = [
                    op for op, odata in transit_houses.items()
                    if odata["house_from_moon"] == vedha_h and op != pname
                    # Classical exemptions
                    and not (pname == "Sun" and op == "Saturn")
                    and not (pname == "Saturn" and op == "Sun")
                    and not (pname == "Moon" and op == "Mercury")
                    and not (pname == "Mercury" and op == "Moon")
                ]

                is_blocked = len(obstructing_planets) > 0
                evaluations[pname] = {
                    "transit_house_from_moon": curr_h,
                    "transit_sign": t_info["sign"],
                    "transit_nature": "BENEFIC_HOUSE",
                    "vedha_house": vedha_h,
                    "obstructing_planets": obstructing_planets,
                    "verdict": f"BLOCKED BY VEDHA (Obstruction from {obstructing_planets} in H{vedha_h})" if is_blocked else "UNBLOCKED & EFFECTIVE (Full Positive Fruit Yielded)"
                }
            else:
                # Transiting in inauspicious house -> Check Vipareeta Vedha
                # Reverse lookup: is this house a Vedha house for someone else?
                vipareeta_rule = next((r for r in rules if r[1] == curr_h), None)
                if vipareeta_rule:
                    partner_h = vipareeta_rule[0]
                    neutralizing_planets = [
                        op for op, odata in transit_houses.items()
                        if odata["house_from_moon"] == partner_h and op != pname
                    ]
                    is_neutralized = len(neutralizing_planets) > 0
                    evaluations[pname] = {
                        "transit_house_from_moon": curr_h,
                        "transit_sign": t_info["sign"],
                        "transit_nature": "INAUSPICIOUS_HOUSE",
                        "vipareeta_neutralizing_house": partner_h,
                        "neutralizing_planets": neutralizing_planets,
                        "verdict": f"NEUTRALIZED BY VIPAREETA VEDHA ({neutralizing_planets} in H{partner_h} cancels harm)" if is_neutralized else "ACTIVE CHALLENGE (Standard Obstruction)"
                    }
                else:
                    evaluations[pname] = {
                        "transit_house_from_moon": curr_h,
                        "transit_sign": t_info["sign"],
                        "transit_nature": "INAUSPICIOUS_HOUSE",
                        "verdict": "STANDARD TRANSIT FRICTION"
                    }

        return {
            "target_date": target_dt.strftime("%Y-%m-%d %H:%M UTC"),
            "natal_moon_sign": ZODIAC_SIGNS[self.moon_sign_idx],
            "transit_evaluations": evaluations
        }
