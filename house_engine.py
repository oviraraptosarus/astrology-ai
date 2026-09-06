from vedic_models import Chart, Planet
from typing import Dict, Any, List

class HouseEngine:
    @staticmethod
    def analyze_house(chart: Chart, house_num: int) -> Dict[str, Any]:
        if house_num < 1 or house_num > 12:
            return {"error": "Invalid house number. Must be 1-12."}
            
        # 1. Base Attributes
        # We need the sign of the house. 
        # Whole sign houses: Ascendant sign is house 1.
        zodiac_signs = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
        
        asc_idx = zodiac_signs.index(chart.ascendant_sign)
        house_sign_idx = (asc_idx + house_num - 1) % 12
        house_sign = zodiac_signs[house_sign_idx]
        
        # 2. Find Lord
        lord_name = None
        for p_name, p in chart.planets.items():
            if house_num in p.owns_houses:
                lord_name = p_name
                break
                
        # 3. Find Occupants
        occupants = []
        for p_name, p in chart.planets.items():
            if p.house == house_num:
                occupants.append(p_name)
                
        # 4. Find Aspects to this house
        aspected_by = []
        for p_name, p in chart.planets.items():
            if house_num in p.aspects_houses:
                aspected_by.append(p_name)
                
        # 5. Ashtakavarga Score for this house
        bindus = chart.sarvashtakavarga.get(house_num, 0) if hasattr(chart, 'sarvashtakavarga') else 0
        
        # 6. Structural Classification
        classifications = HouseEngine.get_house_classifications(house_num)
        
        return {
            "house_num": house_num,
            "sign": house_sign,
            "lord": lord_name,
            "occupants": occupants,
            "aspected_by": aspected_by,
            "sarvashtakavarga_bindus": bindus,
            "classifications": classifications
        }

    @staticmethod
    def get_house_classifications(house_num: int) -> List[str]:
        """
        Returns the classical structural classifications for a given house.
        """
        classifications = []
        
        if house_num in [1, 4, 7, 10]:
            classifications.append("Kendra")
        if house_num in [1, 5, 9]:
            classifications.append("Trikona")
        if house_num in [3, 6, 10, 11]:
            classifications.append("Upachaya")
        if house_num in [6, 8, 12]:
            classifications.append("Dusthana")
        if house_num in [2, 7]:
            classifications.append("Maraka")
        if house_num in [2, 5, 8, 11]:
            classifications.append("Panapara")
        if house_num in [3, 6, 9, 12]:
            classifications.append("Apoklima")
            
        return classifications
