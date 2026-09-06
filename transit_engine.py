from typing import Dict, List, Any
import swisseph as swe
from config import Config
from datetime import datetime
import pytz
from vedic_models import Chart

class TransitEngine:
    """
    Engine for calculating transits (Gochar).
    Specifically implements K.N. Rao's Double Transit (Saturn & Jupiter) logic.
    """
    
    ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
                    
    PLANET_MAP = {
        "Jupiter": swe.JUPITER,
        "Saturn": swe.SATURN
    }
    
    @staticmethod
    def get_current_transit_signs(target_date: datetime) -> Dict[str, str]:
        """
        Gets the signs currently occupied by Saturn and Jupiter.
        """
        # Convert date to Julian Day
        utc_dt = target_date.astimezone(pytz.utc)
        hour_dec = utc_dt.hour + (utc_dt.minute / 60.0) + (utc_dt.second / 3600.0)
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day, hour_dec)
        
        swe.set_sid_mode(Config.ayanamsha_swe_id())
        
        transit_signs = {}
        for p_name, p_id in TransitEngine.PLANET_MAP.items():
            res, _ = swe.calc_ut(jd, p_id, swe.FLG_SWIEPH | swe.FLG_SIDEREAL)
            lon = res[0]
            sign_idx = int(lon / 30.0)
            transit_signs[p_name] = TransitEngine.ZODIAC_SIGNS[sign_idx]
            
        return transit_signs

    @staticmethod
    def get_transit_aspects(planet: str, transit_sign: str) -> List[str]:
        """
        Gets the signs aspected by the transiting planet using Parashari drishti rules.
        """
        sign_idx = TransitEngine.ZODIAC_SIGNS.index(transit_sign)
        aspects = []
        
        if planet == "Jupiter":
            # Jupiter aspects 5th, 7th, 9th from its position
            aspects.append(TransitEngine.ZODIAC_SIGNS[(sign_idx + 4) % 12])
            aspects.append(TransitEngine.ZODIAC_SIGNS[(sign_idx + 6) % 12])
            aspects.append(TransitEngine.ZODIAC_SIGNS[(sign_idx + 8) % 12])
        elif planet == "Saturn":
            # Saturn aspects 3rd, 7th, 10th from its position
            aspects.append(TransitEngine.ZODIAC_SIGNS[(sign_idx + 2) % 12])
            aspects.append(TransitEngine.ZODIAC_SIGNS[(sign_idx + 6) % 12])
            aspects.append(TransitEngine.ZODIAC_SIGNS[(sign_idx + 9) % 12])
            
        return aspects

    @staticmethod
    def evaluate_double_transit(natal_chart: Chart, target_date: datetime) -> Dict[str, Any]:
        """
        Evaluates K.N. Rao's Double Transit rules for a given date.
        Returns a dictionary indicating which houses and natal planets are activated.
        """
        transit_signs = TransitEngine.get_current_transit_signs(target_date)
        
        jup_sign = transit_signs["Jupiter"]
        sat_sign = transit_signs["Saturn"]
        
        # 1. Gather all signs activated by Jupiter (occupying + aspecting)
        jup_activated_signs = set([jup_sign])
        jup_activated_signs.update(TransitEngine.get_transit_aspects("Jupiter", jup_sign))
        
        # 2. Gather all signs activated by Saturn (occupying + aspecting)
        sat_activated_signs = set([sat_sign])
        sat_activated_signs.update(TransitEngine.get_transit_aspects("Saturn", sat_sign))
        
        # 3. Double Transit Signs (Intersection)
        double_transit_signs = jup_activated_signs.intersection(sat_activated_signs)
        
        # 4. Map signs to Natal Houses
        activated_houses = []
        asc_idx = TransitEngine.ZODIAC_SIGNS.index(natal_chart.ascendant_sign)
        
        for sign in double_transit_signs:
            sign_idx = TransitEngine.ZODIAC_SIGNS.index(sign)
            house = ((sign_idx - asc_idx) % 12) + 1
            activated_houses.append(house)
            
        # 5. Check if natal planets are occupying these signs
        activated_natal_planets = []
        for p_name, p in natal_chart.planets.items():
            if p.sign in double_transit_signs:
                activated_natal_planets.append(p_name)
                
        # 6. Check if house lords are activated
        # For example, if Double Transit hits the natal 7th lord, the 7th house matters are activated.
        activated_house_lords = []
        for h in range(1, 13):
            sign_of_house = TransitEngine.ZODIAC_SIGNS[(asc_idx + h - 1) % 12]
            lord_of_house = natal_chart.SIGN_LORDS[sign_of_house]
            if lord_of_house in activated_natal_planets:
                activated_house_lords.append((h, lord_of_house))
                
        return {
            "target_date": target_date.isoformat(),
            "transit_jupiter_sign": jup_sign,
            "transit_saturn_sign": sat_sign,
            "double_transit_signs": list(double_transit_signs),
            "activated_houses": sorted(activated_houses),
            "activated_natal_planets": activated_natal_planets,
            "activated_house_lords": activated_house_lords
        }
