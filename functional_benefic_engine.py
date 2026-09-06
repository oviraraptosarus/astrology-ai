from vedic_models import Chart, Planet
from typing import Dict, List

class FunctionalBeneficEngine:
    """
    Determines the functional nature of planets (Yoga Karaka, Benefic, Malefic, Neutral, Maraka)
    based on the Ascendant (Lagna) sign.
    
    Rules based on Brihat Parashara Hora Sastra (BPHS):
    1. Lords of Trikonas (1, 5, 9) are always functional benefics.
    2. Lords of Trishadayas (3, 6, 11) are functional malefics.
    3. Lords of Kendras (1, 4, 7, 10) lose their natural nature:
       - Natural benefics (Jup, Ven, optionally Mon, Mer) become neutral or malefic (Kendradhipati Dosha).
       - Natural malefics (Sun, Mar, Sat) become neutral or benefic.
    4. Lord of 8th is malefic (unless it also owns 1st, e.g. Aries/Libra ascendants).
    5. Lords of 2nd and 12th are neutral and give results based on their other house ownership or associations.
    6. Planets owning both a Kendra and a Trikona are Yoga Karakas (highest benefics).
    7. Lords of 2nd and 7th are Marakas (death-inflicting or highly challenging).
    """
    
    NATURAL_BENEFICS = ["Jupiter", "Venus", "Moon", "Mercury"]
    NATURAL_MALEFICS = ["Sun", "Mars", "Saturn", "Rahu", "Ketu"]

    @staticmethod
    def calculate_functional_roles(chart: Chart):
        # 1. Identify Badhaka House based on Ascendant
        asc_sign = chart.ascendant_sign
        movable = ["Aries", "Cancer", "Libra", "Capricorn"]
        fixed = ["Taurus", "Leo", "Scorpio", "Aquarius"]
        dual = ["Gemini", "Virgo", "Sagittarius", "Pisces"]
        
        badhaka_house = 11
        if asc_sign in fixed:
            badhaka_house = 9
        elif asc_sign in dual:
            badhaka_house = 7
            
        for p_name, p in chart.planets.items():
            if p_name in ["Rahu", "Ketu", "Ascendant"]:
                continue
                
            owns = p.owns_houses
            if not owns:
                continue
                
            is_trikona = any(h in [1, 5, 9] for h in owns)
            is_kendra = any(h in [1, 4, 7, 10] for h in owns)
            is_trishadaya = any(h in [3, 6, 11] for h in owns)
            is_maraka = any(h in [2, 7] for h in owns)
            is_badhaka = badhaka_house in owns
            is_dusthana = any(h in [6, 8, 12] for h in owns)
            
            roles = []
            
            # Badhaka
            if is_badhaka:
                roles.append("Badhaka")
                
            # Maraka
            if is_maraka:
                roles.append("Maraka")
                
            # Yoga Karaka
            if (1 in owns and len(owns) == 1) or (is_trikona and is_kendra and 1 not in owns):
                roles.append("Yoga Karaka")
                p.functional_role = "Benefic" # Base functional role
            # Ascendant Lord
            elif 1 in owns:
                p.functional_role = "Benefic"
            # Trikona Lord
            elif is_trikona:
                p.functional_role = "Benefic"
            # Trishadaya Lord
            elif is_trishadaya:
                p.functional_role = "Malefic"
            # 8th Lord (except Sun/Moon technically, but functionally malefic)
            elif 8 in owns and not is_trikona:
                p.functional_role = "Malefic"
            # Kendradhipati Dosha
            elif is_kendra and not is_trikona:
                if p_name in FunctionalBeneficEngine.NATURAL_BENEFICS:
                    p.functional_role = "Neutral" # Loses beneficence
                else:
                    p.functional_role = "Neutral" # Loses maleficence
            # 2nd and 12th lords take nature of other house
            elif (2 in owns or 12 in owns) and len(owns) == 2:
                other_house = [h for h in owns if h not in [2, 12]][0]
                if other_house in [1, 5, 9]:
                    p.functional_role = "Benefic"
                elif other_house in [3, 6, 11]:
                    p.functional_role = "Malefic"
                elif other_house == 8:
                    p.functional_role = "Malefic"
                else:
                    p.functional_role = "Neutral"
            else:
                p.functional_role = "Neutral"
                
            # Store granular roles in a new list for the engine to use
            if "Yoga Karaka" in roles:
                p.functional_role = "Yoga Karaka"
                
            p.detailed_functional_roles = roles

    @staticmethod
    def calculate_panchadha_maitri(chart: Chart):
        """
        Calculates Panchadha Maitri (Compound Friendship) by combining 
        Natural Friendship (Naisargika) and Temporal Friendship (Tatkalika).
        """
        # Calculate Natural Friendships
        from condition_engine import ConditionEngine
        ConditionEngine.evaluate_friendships(chart)
        
        for p1_name, p1 in chart.planets.items():
            if p1_name in ["Rahu", "Ketu", "Ascendant"]:
                continue
                
            p1.compound_friendships = {
                "Best_Friends": [],
                "Friends": [],
                "Neutrals": [],
                "Enemies": [],
                "Bitter_Enemies": []
            }
                
            for p2_name, p2 in chart.planets.items():
                if p2_name in ["Rahu", "Ketu", "Ascendant"] or p1_name == p2_name:
                    continue
                    
                # 1. Natural Relationship
                nat_rel = 0
                if p2_name in p1.friendships.get("natural_friends", []):
                    nat_rel = 1
                elif p2_name in p1.friendships.get("natural_enemies", []):
                    nat_rel = -1
                    
                # 2. Temporal Relationship (Tatkalika Maitri)
                # Planets in 2nd, 3rd, 4th, 10th, 11th, 12th from a planet are Temporal Friends (+1)
                # Planets in 1st, 5th, 6th, 7th, 8th, 9th are Temporal Enemies (-1)
                p1_h = p1.house
                p2_h = p2.house
                
                dist = ((p2_h - p1_h) % 12) + 1
                
                temp_rel = -1
                if dist in [2, 3, 4, 10, 11, 12]:
                    temp_rel = 1
                    
                # 3. Compound Relationship
                total = nat_rel + temp_rel
                
                if total == 2:
                    p1.compound_friendships["Best_Friends"].append(p2_name)
                elif total == 1:
                    p1.compound_friendships["Friends"].append(p2_name)
                elif total == 0:
                    p1.compound_friendships["Neutrals"].append(p2_name)
                elif total == -1:
                    p1.compound_friendships["Enemies"].append(p2_name)
                elif total == -2:
                    p1.compound_friendships["Bitter_Enemies"].append(p2_name)
                    
            # 4. Refine Dignity using Compound Friendship
            if p1.dignity == "Neutral Sign" and p1.dispositor:
                dispositor_name = p1.dispositor
                if dispositor_name in p1.compound_friendships["Best_Friends"]:
                    p1.dignity = "Great Friend Sign"
                elif dispositor_name in p1.compound_friendships["Friends"]:
                    p1.dignity = "Friendly Sign"
                elif dispositor_name in p1.compound_friendships["Neutrals"]:
                    p1.dignity = "Neutral Sign"
                elif dispositor_name in p1.compound_friendships["Enemies"]:
                    p1.dignity = "Enemy Sign"
                elif dispositor_name in p1.compound_friendships["Bitter_Enemies"]:
                    p1.dignity = "Great Enemy Sign"
