from typing import Dict, List
from vedic_models import Chart, Planet

class ConditionEngine:
    @staticmethod
    def evaluate_all_conditions(chart: Chart):
        ConditionEngine.evaluate_dignity(chart)
        ConditionEngine.evaluate_friendships(chart)
        ConditionEngine.evaluate_combustion(chart)
        ConditionEngine.evaluate_avasthas(chart)
        ConditionEngine.evaluate_planetary_war(chart)

    @staticmethod
    def evaluate_dignity(chart: Chart):
        """
        Formalizes Dignity Hierarchy based on strict degree ranges where applicable.
        """
        # Structure: 
        # Exaltation: (Sign, Exact Degree)
        # Moolatrikona: (Sign, Start Degree, End Degree)
        # Own: List of Signs
        # Debilitation: (Sign, Exact Degree)
        DIGNITY_RULES = {
            "Sun": {"Exalted": ("Aries", 10), "Moolatrikona": ("Leo", 0, 20), "Own": ["Leo"], "Debilitated": ("Libra", 10)},
            "Moon": {"Exalted": ("Taurus", 3), "Moolatrikona": ("Taurus", 3, 30), "Own": ["Cancer"], "Debilitated": ("Scorpio", 3)},
            "Mars": {"Exalted": ("Capricorn", 28), "Moolatrikona": ("Aries", 0, 12), "Own": ["Aries", "Scorpio"], "Debilitated": ("Cancer", 28)},
            "Mercury": {"Exalted": ("Virgo", 15), "Moolatrikona": ("Virgo", 15, 20), "Own": ["Gemini", "Virgo"], "Debilitated": ("Pisces", 15)},
            "Jupiter": {"Exalted": ("Cancer", 5), "Moolatrikona": ("Sagittarius", 0, 10), "Own": ["Sagittarius", "Pisces"], "Debilitated": ("Capricorn", 5)},
            "Venus": {"Exalted": ("Pisces", 27), "Moolatrikona": ("Libra", 0, 15), "Own": ["Taurus", "Libra"], "Debilitated": ("Virgo", 27)},
            "Saturn": {"Exalted": ("Libra", 20), "Moolatrikona": ("Aquarius", 0, 20), "Own": ["Capricorn", "Aquarius"], "Debilitated": ("Aries", 20)},
            # Nodes typically don't have universally agreed degree ranges for exaltation, using signs:
            "Rahu": {"Exalted": ("Taurus", 15), "Moolatrikona": ("Virgo", 0, 30), "Own": [], "Debilitated": ("Scorpio", 15)},
            "Ketu": {"Exalted": ("Scorpio", 15), "Moolatrikona": ("Pisces", 0, 30), "Own": [], "Debilitated": ("Taurus", 15)}
        }

        for p_name, p in chart.planets.items():
            if p_name not in DIGNITY_RULES:
                continue
                
            rules = DIGNITY_RULES[p_name]
            degree_in_sign = p.degree % 30
            
            # Check Exaltation
            ex_sign, ex_deg = rules["Exalted"]
            if p.sign == ex_sign:
                # Standard classical texts say "Deep Exaltation" at exact degree, 
                # but the whole sign is considered Exalted. We'll mark as Exalted.
                p.dignity = "Exalted"
                continue
                
            # Check Debilitation
            deb_sign, deb_deg = rules["Debilitated"]
            if p.sign == deb_sign:
                p.dignity = "Debilitated"
                continue
                
            # Check Moolatrikona
            mt_sign, mt_start, mt_end = rules["Moolatrikona"]
            if p.sign == mt_sign and mt_start <= degree_in_sign <= mt_end:
                p.dignity = "Moolatrikona"
                continue
                
            # Check Own Sign (if not already MT)
            if p.sign in rules["Own"]:
                p.dignity = "Own House"
                continue
                
            p.dignity = "Neutral" # Will be refined by Friendship later

    @staticmethod
    def evaluate_friendships(chart: Chart):
        """
        Naisargika Maitri (Natural Friendship).
        Based on Brihat Parashara Hora Sastra.
        """
        FRIENDSHIP_TABLE = {
            "Sun": {"Friends": ["Moon", "Mars", "Jupiter"], "Enemies": ["Venus", "Saturn"], "Neutrals": ["Mercury"]},
            "Moon": {"Friends": ["Sun", "Mercury"], "Enemies": [], "Neutrals": ["Mars", "Jupiter", "Venus", "Saturn"]},
            "Mars": {"Friends": ["Sun", "Moon", "Jupiter"], "Enemies": ["Mercury"], "Neutrals": ["Venus", "Saturn"]},
            "Mercury": {"Friends": ["Sun", "Venus"], "Enemies": ["Moon"], "Neutrals": ["Mars", "Jupiter", "Saturn"]},
            "Jupiter": {"Friends": ["Sun", "Moon", "Mars"], "Enemies": ["Mercury", "Venus"], "Neutrals": ["Saturn"]},
            "Venus": {"Friends": ["Mercury", "Saturn"], "Enemies": ["Sun", "Moon"], "Neutrals": ["Mars", "Jupiter"]},
            "Saturn": {"Friends": ["Mercury", "Venus"], "Enemies": ["Sun", "Moon", "Mars"], "Neutrals": ["Jupiter"]}
        }

        for p_name, p in chart.planets.items():
            if p_name in FRIENDSHIP_TABLE:
                p.friendships["natural_friends"] = FRIENDSHIP_TABLE[p_name]["Friends"]
                p.friendships["natural_enemies"] = FRIENDSHIP_TABLE[p_name]["Enemies"]
                p.friendships["natural_neutrals"] = FRIENDSHIP_TABLE[p_name]["Neutrals"]

            # Refine dignity based on dispositor friendship (if dignity is Neutral)
            if p.dignity == "Neutral" and p.dispositor and p_name in FRIENDSHIP_TABLE:
                if p.dispositor in p.friendships["natural_friends"]:
                    p.dignity = "Friendly Sign"
                elif p.dispositor in p.friendships["natural_enemies"]:
                    p.dignity = "Enemy Sign"
                else:
                    p.dignity = "Neutral Sign"

    @staticmethod
    def get_absolute_longitude(planet: Planet) -> float:
        ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        try:
            sign_idx = ZODIAC_SIGNS.index(planet.sign)
            return (sign_idx * 30) + (planet.degree % 30)
        except ValueError:
            return planet.degree

    @staticmethod
    def evaluate_combustion(chart: Chart):
        """
        Calculates combustion (Asta) based on absolute angular distance from the Sun.
        """
        from config import Config
        
        if "Sun" not in chart.planets:
            return
            
        sun_lon = chart.planets["Sun"].degree + (chart.get_sign_index(chart.planets["Sun"].sign) * 30)
        
        for p_name, p in chart.planets.items():
            if p_name in ["Sun", "Rahu", "Ketu", "Ascendant"]:
                continue
                
            p_lon = p.degree + (chart.get_sign_index(p.sign) * 30)
            
            dist = abs(sun_lon - p_lon)
            dist = min(dist, 360 - dist)
            
            threshold = Config.get_combustion_threshold(p_name, p.retrograde)
            
            if dist <= threshold:
                p.combustion = {
                    "status": True,
                    "sun_distance": round(dist, 2),
                    "threshold": threshold
                }
            else:
                p.combustion = {
                    "status": False,
                    "sun_distance": round(dist, 2),
                    "threshold": threshold
                }

    @staticmethod
    def evaluate_avasthas(chart: Chart):
        """
        Balaadi Avastha (Infant, Youth, Adult, Old, Dead)
        Depends on whether the sign is Odd (Aries, Gemini...) or Even (Taurus, Cancer...)
        """
        odd_signs = ["Aries", "Gemini", "Leo", "Libra", "Sagittarius", "Aquarius"]
        even_signs = ["Taurus", "Cancer", "Virgo", "Scorpio", "Capricorn", "Pisces"]
        
        for p_name, p in chart.planets.items():
            if p_name in ["Rahu", "Ketu", "Ascendant"]:
                continue
                
            deg = p.degree % 30
            state = ""
            
            if p.sign in odd_signs:
                if 0 <= deg < 6: state = "Bala"
                elif 6 <= deg < 12: state = "Kumara"
                elif 12 <= deg < 18: state = "Yuva"
                elif 18 <= deg < 24: state = "Vriddha"
                elif 24 <= deg <= 30: state = "Mrita"
            elif p.sign in even_signs:
                if 0 <= deg < 6: state = "Mrita"
                elif 6 <= deg < 12: state = "Vriddha"
                elif 12 <= deg < 18: state = "Yuva"
                elif 18 <= deg < 24: state = "Kumara"
                elif 24 <= deg <= 30: state = "Bala"
                
            p.avasthas["balaadi"] = state

    @staticmethod
    def evaluate_planetary_war(chart: Chart):
        """
        Graha Yuddha (Planetary War). Occurs when Mars, Mercury, Jupiter, Venus, or Saturn
        are within 1 degree of each other.
        Venus is generally considered the victor, otherwise the planet with the lower longitude wins.
        """
        true_planets = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]
        
        # Check pairs
        for i in range(len(true_planets)):
            for j in range(i + 1, len(true_planets)):
                p1_name = true_planets[i]
                p2_name = true_planets[j]
                
                if p1_name not in chart.planets or p2_name not in chart.planets:
                    continue
                    
                p1 = chart.planets[p1_name]
                p2 = chart.planets[p2_name]
                
                p1_lon = ConditionEngine.get_absolute_longitude(p1)
                p2_lon = ConditionEngine.get_absolute_longitude(p2)
                
                dist = abs(p1_lon - p2_lon)
                dist = min(dist, 360 - dist)
                
                if dist <= 1.0: # Within 1 degree
                    # Planetary war!
                    p1.planetary_war["in_war"] = True
                    p1.planetary_war["with_planet"] = p2_name
                    p2.planetary_war["in_war"] = True
                    p2.planetary_war["with_planet"] = p1_name
                    
                    if p1_name == "Venus":
                        p1.planetary_war["is_winner"] = True
                    elif p2_name == "Venus":
                        p2.planetary_war["is_winner"] = True
                    else:
                        if p1_lon < p2_lon:
                            p1.planetary_war["is_winner"] = True
                        else:
                            p2.planetary_war["is_winner"] = True

