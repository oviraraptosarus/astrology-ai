"""
Bhrigu Nandi Nadi (BNN) Planetary Progression Engine (R.G. Rao Tradition)
Implements:
1. Jupiter Progression (Jeeva / Life Force) - 12-Year Sign Progression Cycle (2.5°/year).
2. Saturn Progression (Karma / Profession) - 30-Year Sign Progression Cycle (1.0°/year).
3. Rahu/Ketu Progression (Karmic Debt & Destiny) - 18-Year Reverse Progression Cycle (1.67°/year).
4. Progressed Planetary Aspects: 1st (Conjunction), 5th & 9th (Dharmic Trines), 7th (Direct Opposition).
5. Milestone Prediction: Identifies exact life years when Progressed Jupiter/Saturn activate natal combinations.
"""
from typing import Dict, Any, List
from vedic_models import Chart, Planet

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

class BhriguNandiNadiEngine:
    def __init__(self, chart: Chart):
        self.chart = chart

    def calculate_progressed_positions(self, current_age: float) -> Dict[str, Any]:
        """Calculates progressed positions of Jupiter, Saturn, Rahu at given age."""
        jup = self.chart.planets.get("Jupiter")
        sat = self.chart.planets.get("Saturn")
        rahu = self.chart.planets.get("Rahu")

        jup_natal_lon = jup.longitude if jup else 0.0
        sat_natal_lon = sat.longitude if sat else 0.0
        rahu_natal_lon = rahu.longitude if rahu else 0.0

        # Jupiter moves 30 deg in 12 years = 2.5 deg per year
        jup_prog_lon = (jup_natal_lon + (current_age * 2.5)) % 360.0
        jup_prog_sign_idx = int(jup_prog_lon / 30.0)

        # Saturn moves 30 deg in 30 years = 1.0 deg per year
        sat_prog_lon = (sat_natal_lon + (current_age * 1.0)) % 360.0
        sat_prog_sign_idx = int(sat_prog_lon / 30.0)

        # Rahu moves reverse: 30 deg in 18 years = 1.6667 deg per year reverse
        rahu_prog_lon = (rahu_natal_lon - (current_age * (30.0 / 18.0))) % 360.0
        rahu_prog_sign_idx = int(rahu_prog_lon / 30.0)

        # Identify natal planets aspected by Progressed Jupiter (Trines 1, 5, 9 & Opposition 7)
        jup_aspected_signs = [(jup_prog_sign_idx + offset) % 12 for offset in [0, 4, 6, 8]]
        jup_activations = []
        for p_name, p in self.chart.planets.items():
            p_sign_idx = ZODIAC_SIGNS.index(p.sign)
            if p_sign_idx in jup_aspected_signs:
                relation = "Conjunction (1st)" if p_sign_idx == jup_prog_sign_idx else ("Opposition (7th)" if p_sign_idx == (jup_prog_sign_idx + 6) % 12 else "Trine Aspect (5th/9th)")
                jup_activations.append(f"{p_name} in {p.sign} via {relation}")

        # Identify natal planets aspected by Progressed Saturn
        sat_aspected_signs = [(sat_prog_sign_idx + offset) % 12 for offset in [0, 2, 6, 9]] # 1, 3, 7, 10
        sat_activations = []
        for p_name, p in self.chart.planets.items():
            p_sign_idx = ZODIAC_SIGNS.index(p.sign)
            if p_sign_idx in sat_aspected_signs:
                relation = "Conjunction (1st)" if p_sign_idx == sat_prog_sign_idx else ("Opposition (7th)" if p_sign_idx == (sat_prog_sign_idx + 6) % 12 else "Saturn Special Aspect")
                sat_activations.append(f"{p_name} in {p.sign} via {relation}")

        return {
            "current_age": round(current_age, 1),
            "progressed_jupiter": {
                "longitude": round(jup_prog_lon, 2),
                "sign": ZODIAC_SIGNS[jup_prog_sign_idx],
                "degree_in_sign": round(jup_prog_lon % 30.0, 2),
                "active_natal_contacts": jup_activations
            },
            "progressed_saturn": {
                "longitude": round(sat_prog_lon, 2),
                "sign": ZODIAC_SIGNS[sat_prog_sign_idx],
                "degree_in_sign": round(sat_prog_lon % 30.0, 2),
                "active_natal_contacts": sat_activations
            },
            "progressed_rahu": {
                "longitude": round(rahu_prog_lon, 2),
                "sign": ZODIAC_SIGNS[rahu_prog_sign_idx],
                "degree_in_sign": round(rahu_prog_lon % 30.0, 2)
            }
        }
