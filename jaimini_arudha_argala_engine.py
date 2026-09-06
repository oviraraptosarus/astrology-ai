"""
Jaimini Arudha Pada (A1-A12) & Argala/Virodhargala Engine (Pt. Sanjay Rath Method)
Implements:
1. Calculation of all 12 Arudha Padas (A1 to A12):
   - A1 (Arudha Lagna - Image/Status), A2 (Dhana Pada), A3 (Bhratri Pada),
   - A4 (Matri/Vahana Pada), A5 (Mantra/Putra Pada), A6 (Shatru/Roga Pada),
   - A7 (Dara Pada), A8 (Mrityu Pada), A9 (Bhagya Pada), A10 (Rajya Pada),
   - A11 (Labha Pada), A12 (Upapada Lagna - UL).
   - Standard Jaimini exceptions (If Pada falls in 1st/7th, shift 10 signs).
2. Argala (Intervention) & Virodhargala (Obstruction) Matrix:
   - Primary Argala: Houses 2, 4, 11 from target.
   - Virodhargala: Houses 12, 10, 3 from target.
   - Secondary Argala: 5th house (obstructed by 9th).
"""
from typing import Dict, Any, List
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

PADA_NAMES = {
    1: ("A1 / AL", "Arudha Lagna", "External Personality, Status & Public Maya"),
    2: ("A2", "Dhana Pada", "Perceived Wealth, Savings & Family Reputation"),
    3: ("A3", "Bhratri Pada", "Initiatives, Siblings, Bravery & Media Reach"),
    4: ("A4", "Matri / Vahana Pada", "Vehicles, Properties, Mother & Domestic Assets"),
    5: ("A5", "Mantra / Putra Pada", "Intellect, Creative Output, Progeny & Followers"),
    6: ("A6", "Shatru / Roga Pada", "Litigation, Debts, Enemies & Physical Vulnerabilities"),
    7: ("A7", "Dara Pada", "Business Partnerships, Clients & Social Transactions"),
    8: ("A8", "Mrityu Pada", "Sudden Transformations, Hidden Crises & Scandal Vulnerability"),
    9: ("A9", "Bhagya Pada", "Spiritual Fortunes, Dharma, Guru & Higher Learning"),
    10: ("A10", "Rajya Pada", "Career Recognition, Authority, Executive Post & Karma"),
    11: ("A11", "Labha Pada", "Cash Flow, Material Income Streams & Associates"),
    12: ("A12 / UL", "Upapada Lagna", "Marriage Longevity, Spouse Profile & Commitment")
}

class JaiminiArudhaArgalaEngine:
    def __init__(self, chart: Chart):
        self.chart = chart
        self.lagna_sign_idx = ZODIAC_SIGNS.index(chart.ascendant_sign) if hasattr(chart, "ascendant_sign") and chart.ascendant_sign in ZODIAC_SIGNS else int(chart.ascendant.longitude / 30)

    def calculate_all_padas(self) -> Dict[str, Any]:
        """Calculates all 12 Arudha Padas (A1 to A12)."""
        padas = {}
        for h in range(1, 13):
            house_sign_idx = (self.lagna_sign_idx + h - 1) % 12
            lord = SIGN_LORDS[ZODIAC_SIGNS[house_sign_idx]]
            lord_p = self.chart.planets.get(lord)
            lord_sign_idx = ZODIAC_SIGNS.index(lord_p.sign) if lord_p else house_sign_idx

            dist = (lord_sign_idx - house_sign_idx) % 12
            pada_idx = (lord_sign_idx + dist) % 12

            # Classical Jaimini Exception: If pada falls in 1st or 7th from the house, jump 10 signs forward (add 9 to 0-index)
            if pada_idx == house_sign_idx or pada_idx == (house_sign_idx + 6) % 12:
                pada_idx = (pada_idx + 9) % 12

            pada_sign = ZODIAC_SIGNS[pada_idx]
            tag, label, desc = PADA_NAMES[h]
            planets_in_pada = [pname for pname, p in self.chart.planets.items() if p.sign == pada_sign]

            padas[f"House_{h}_{tag.replace(' / ', '_')}"] = {
                "house": h,
                "pada_code": tag,
                "pada_name": label,
                "pada_sign": pada_sign,
                "planets_present": planets_in_pada,
                "significance": desc
            }
        return padas

    def evaluate_argala_on_house(self, target_house: int) -> Dict[str, Any]:
        """Evaluates Argala (Intervention) and Virodhargala (Obstruction) on any house."""
        target_sign_idx = (self.lagna_sign_idx + target_house - 1) % 12
        
        argala_pairs = [
            (2, 12, "Primary Dhana Argala (Wealth/Family Intervention)"),
            (4, 10, "Primary Sukha Argala (Asset/Comfort Intervention)"),
            (11, 3, "Primary Labha Argala (Gains/Desire Intervention)"),
            (5, 9, "Secondary Putra/Mantra Argala (Intellect/Progeny Intervention)")
        ]

        active_argalas = []
        for a_off, v_off, label in argala_pairs:
            a_sign = ZODIAC_SIGNS[(target_sign_idx + a_off - 1) % 12]
            v_sign = ZODIAC_SIGNS[(target_sign_idx + v_off - 1) % 12]

            a_planets = [pname for pname, p in self.chart.planets.items() if p.sign == a_sign]
            v_planets = [pname for pname, p in self.chart.planets.items() if p.sign == v_sign]

            if len(a_planets) > 0:
                is_obstructed = len(v_planets) >= len(a_planets)
                status = "OBSTRUCTED (Virodhargala Active)" if is_obstructed else "UNOBSTRUCTED (Full Intervention Strength)"
                active_argalas.append({
                    "argala_type": label,
                    "argala_house": f"House {a_off} from Target ({a_sign})",
                    "argala_planets": a_planets,
                    "virodhargala_house": f"House {v_off} from Target ({v_sign})",
                    "virodhargala_planets": v_planets,
                    "status": status
                })

        return {
            "target_house": target_house,
            "target_sign": ZODIAC_SIGNS[target_sign_idx],
            "argalas": active_argalas
        }
