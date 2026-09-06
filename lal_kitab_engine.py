from typing import Dict, Any, List
from vedic_models import Chart, Planet

class LalKitabEngine:
    """
    Engine for Lal Kitab calculations.
    The core principle of Lal Kitab is the 'Teva' or fixed house chart,
    where the Ascendant is ALWAYS considered as Aries (House 1), regardless of the actual birth ascendant.
    """
    
    ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

    @staticmethod
    def generate_lal_kitab_teva(chart: Chart) -> Dict[str, Any]:
        """
        Converts a standard natal chart into a Lal Kitab Teva.
        In Lal Kitab, the signs are essentially ignored. The houses act as the signs.
        House 1 = Aries, House 2 = Taurus, etc.
        """
        asc_idx = LalKitabEngine.ZODIAC_SIGNS.index(chart.ascendant_sign)
        
        teva_houses = {h: [] for h in range(1, 13)}
        
        for p_name, p in chart.planets.items():
            # Find the distance of the planet's sign from the Ascendant's sign
            planet_sign_idx = LalKitabEngine.ZODIAC_SIGNS.index(p.sign)
            house = ((planet_sign_idx - asc_idx) % 12) + 1
            
            # In Lal Kitab, the house IS the sign.
            # So if a planet is in House 1, it is treated as being in Aries.
            lk_sign = LalKitabEngine.ZODIAC_SIGNS[house - 1]
            
            teva_houses[house].append({
                "planet": p_name,
                "natal_sign": p.sign,
                "lal_kitab_sign": lk_sign, # The fixed sign of the house
                "retrograde": p.retrograde
            })
            
        return {
            "original_ascendant": chart.ascendant_sign,
            "lal_kitab_ascendant": "Aries (Fixed)",
            "houses": teva_houses
        }

    @staticmethod
    def evaluate_blind_planets(teva: Dict[str, Any]) -> List[str]:
        """
        In Lal Kitab, if the 10th house is empty and the 4th house has planets,
        or vice versa depending on specific rules, a planet may become 'blind' or inactive.
        (Simplified rule for scaffolding).
        """
        # House 10 is the house of Karma/Action (Capricorn in LK)
        house_10_empty = len(teva["houses"][10]) == 0
        
        blind_planets = []
        if house_10_empty:
            # Planets in House 4 (Cancer in LK) become blind (ineffective) if House 10 is empty
            for p in teva["houses"][4]:
                blind_planets.append(p["planet"])
                
        return blind_planets
