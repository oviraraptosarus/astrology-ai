"""
Bhrigu Nandi Nadi (BNN) Astrology Engine
Implements Directional Trines (1-5-9), 2-12 & 7th Linkages,
Jeeva Karaka (Jupiter), Karma Karaka (Saturn), and Transit Activations.
"""

from typing import Dict, List, Any, Optional
from vedic_models import Chart, Planet

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# 4 Elements / Directions in BNN
DIRECTION_ELEMENTS = {
    "FIRE_EAST": ["Aries", "Leo", "Sagittarius"],
    "EARTH_SOUTH": ["Taurus", "Virgo", "Capricorn"],
    "AIR_WEST": ["Gemini", "Libra", "Aquarius"],
    "WATER_NORTH": ["Cancer", "Scorpio", "Pisces"]
}

SIGN_TO_DIRECTION = {}
for direction, signs in DIRECTION_ELEMENTS.items():
    for s in signs:
        SIGN_TO_DIRECTION[s] = direction

# Natural Karakas in BNN
BNN_KARAKAS = {
    "Jupiter": "Jeeva Karaka (Self / Life Force / Longevity)",
    "Saturn": "Karma Karaka (Profession / Duty / Work)",
    "Sun": "Pitru / Atma Karaka (Father / Authority / Soul)",
    "Moon": "Matru / Mano Karaka (Mother / Mind / Travel)",
    "Mars": "Bhatru / Shakti Karaka (Brothers / Technical Energy / Vitality)",
    "Mercury": "Buddhi / Vyapara Karaka (Intellect / Trade / Business / Speech)",
    "Venus": "Kalatra / Dhana Karaka (Spouse / Wealth / Luxury / Arts)",
    "Rahu": "Maya / Pithru Karma Karaka (Foreign / Illusion / Material Surges)",
    "Ketu": "Moksha / Gnana Karaka (Detachment / Occult / Roots / Spirit)"
}

class NadiEngine:
    """
    Evaluates chart according to classical Bhrigu Nandi Nadi (BNN) principles.
    """

    @staticmethod
    def calculate_directional_clusters(chart: Chart) -> Dict[str, List[Dict[str, Any]]]:
        """
        Groups planets into the 4 BNN Directional Trines (1-5-9 mutual conjunctions).
        """
        clusters = {
            "FIRE_EAST": [],
            "EARTH_SOUTH": [],
            "AIR_WEST": [],
            "WATER_NORTH": []
        }

        for name, planet in chart.planets.items():
            if name == "Ascendant":
                continue
            direction = SIGN_TO_DIRECTION.get(planet.sign, "FIRE_EAST")
            clusters[direction].append({
                "planet": name,
                "sign": planet.sign,
                "degree": planet.degree,
                "retrograde": planet.retrograde,
                "karaka": BNN_KARAKAS.get(name, "")
            })

        # Sort each cluster by longitude within direction
        for dir_name in clusters:
            clusters[dir_name].sort(key=lambda x: x["degree"])

        return clusters

    @staticmethod
    def get_planet_bnn_links(chart: Chart, planet_name: str) -> Dict[str, Any]:
        """
        Computes 1-5-9 (trines), 2nd house (support/future), 12th house (past/roots), and 7th house (opposition/cooperation) linkages for a planet.
        """
        planet = chart.planets.get(planet_name)
        if not planet:
            return {}

        sign_idx = ZODIAC_SIGNS.index(planet.sign)
        direction = SIGN_TO_DIRECTION[planet.sign]

        # 1. Trines (1-5-9) -> Same Direction
        trine_planets = []
        for name, p in chart.planets.items():
            if name in [planet_name, "Ascendant"]:
                continue
            if SIGN_TO_DIRECTION[p.sign] == direction:
                trine_planets.append(name)

        # 2. 2nd House from Planet (Front / Direct Support)
        second_sign = ZODIAC_SIGNS[(sign_idx + 1) % 12]
        second_planets = [name for name, p in chart.planets.items() if p.sign == second_sign and name != "Ascendant"]

        # 3. 12th House from Planet (Behind / Root / Past karma)
        twelfth_sign = ZODIAC_SIGNS[(sign_idx - 1) % 12]
        twelfth_planets = [name for name, p in chart.planets.items() if p.sign == twelfth_sign and name != "Ascendant"]

        # 4. 7th House from Planet (Direct Aspect)
        seventh_sign = ZODIAC_SIGNS[(sign_idx + 6) % 12]
        seventh_planets = [name for name, p in chart.planets.items() if p.sign == seventh_sign and name != "Ascendant"]

        return {
            "subject": planet_name,
            "sign": planet.sign,
            "direction": direction,
            "trinal_conjunctions_1_5_9": trine_planets,
            "front_support_2nd": second_planets,
            "rear_linkage_12th": twelfth_planets,
            "opposite_aspect_7th": seventh_planets,
            "composite_bnn_combination": [planet_name] + trine_planets + second_planets + seventh_planets
        }

    @staticmethod
    def evaluate_jeeva_and_karma(chart: Chart) -> Dict[str, Any]:
        """
        Evaluates the core BNN Jeeva (Self) and Karma (Career) axes.
        """
        jeeva_links = NadiEngine.get_planet_bnn_links(chart, "Jupiter")
        karma_links = NadiEngine.get_planet_bnn_links(chart, "Saturn")

        # Interpret Karma (Saturn)
        karma_combo = karma_links.get("composite_bnn_combination", [])
        career_insights = []
        if "Sun" in karma_combo:
            career_insights.append("Saturn + Sun: Government, authority, executive leadership, or father-related enterprise.")
        if "Moon" in karma_combo:
            career_insights.append("Saturn + Moon: Frequent travel, food, liquid products, nursing, hospitality, or fluctuating work environment.")
        if "Mars" in karma_combo:
            career_insights.append("Saturn + Mars: Engineering, heavy machinery, technical fields, construction, surgery, or high physical drive.")
        if "Mercury" in karma_combo:
            career_insights.append("Saturn + Mercury: Business, trade, accounting, IT, software engineering, consulting, or commerce.")
        if "Jupiter" in karma_combo:
            career_insights.append("Saturn + Jupiter (Dharma-Karma Yoga): Advisory, teaching, law, finance, mentorship, or high organizational status.")
        if "Venus" in karma_combo:
            career_insights.append("Saturn + Venus: Financial assets, luxury goods, arts, media, real estate, architecture, or hospitality.")
        if "Rahu" in karma_combo:
            career_insights.append("Saturn + Rahu: High-tech, AI, foreign multinational corporations, electronics, shadow industries, or sudden massive scaling.")
        if "Ketu" in karma_combo:
            career_insights.append("Saturn + Ketu: Software coding/algorithms, research, medical diagnostic, legal drafting, or advisory behind-the-scenes.")

        # Interpret Jeeva (Jupiter)
        jeeva_combo = jeeva_links.get("composite_bnn_combination", [])
        life_insights = []
        if "Ketu" in jeeva_combo:
            life_insights.append("Jupiter + Ketu: Strong spiritual detachment, intuitive depth, esoteric knowledge, or ancestral blessings.")
        if "Rahu" in jeeva_combo:
            life_insights.append("Jupiter + Rahu: Unconventional life trajectory, strong worldly desires, foreign connections, or revolutionary ideas.")
        if "Mars" in jeeva_combo:
            life_insights.append("Jupiter + Mars: Energetic, bold, decisive, courageous, and righteous disposition.")

        return {
            "jeeva_karaka": jeeva_links,
            "karma_karaka": karma_links,
            "bnn_career_patterns": career_insights,
            "bnn_life_patterns": life_insights
        }
