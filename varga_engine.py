from typing import Dict
from vedic_models import Chart, Planet

class VargaEngine:
    """
    Calculates Divisional Charts (Vargas) mathematically based on longitude.
    """
    
    ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", 
                    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

    @staticmethod
    def get_sign_index(sign: str) -> int:
        return VargaEngine.ZODIAC_SIGNS.index(sign)
        
    @staticmethod
    def get_sign_from_index(idx: int) -> str:
        return VargaEngine.ZODIAC_SIGNS[idx % 12]

    @staticmethod
    def calc_d2_hora(sign: str, degree: float) -> str:
        is_odd = (VargaEngine.get_sign_index(sign) % 2 == 0)
        if is_odd:
            return "Leo" if degree < 15.0 else "Cancer"
        else:
            return "Cancer" if degree < 15.0 else "Leo"

    @staticmethod
    def calc_d3_drekkana(sign: str, degree: float) -> str:
        div3 = int(degree / 10.0)
        if div3 >= 3: div3 = 2 # Handle floating point edge case for exactly 30.0
        base_idx = VargaEngine.get_sign_index(sign)
        offset = [0, 4, 8][div3]
        return VargaEngine.get_sign_from_index(base_idx + offset)

    @staticmethod
    def calc_d4_chaturthamsha(sign: str, degree: float) -> str:
        div4 = int(degree / 7.5)
        if div4 >= 4: div4 = 3
        base_idx = VargaEngine.get_sign_index(sign)
        offset = [0, 3, 6, 9][div4]
        return VargaEngine.get_sign_from_index(base_idx + offset)

    @staticmethod
    def calc_d7_saptamsha(sign: str, degree: float) -> str:
        div7 = int(degree / (30.0 / 7.0))
        if div7 >= 7: div7 = 6
        base_idx = VargaEngine.get_sign_index(sign)
        is_odd = (base_idx % 2 == 0)
        start_idx = base_idx if is_odd else base_idx + 6
        return VargaEngine.get_sign_from_index(start_idx + div7)

    @staticmethod
    def calc_d9_navamsha(sign: str, degree: float) -> str:
        division = int(degree / (30.0 / 9.0))
        if division >= 9: division = 8
        sign_idx = VargaEngine.get_sign_index(sign)
        element_idx = sign_idx % 4 # 0=Fire, 1=Earth, 2=Air, 3=Water
        start_idx = [0, 9, 6, 3][element_idx]
        return VargaEngine.get_sign_from_index(start_idx + division)

    @staticmethod
    def calc_d10_dasamsha(sign: str, degree: float) -> str:
        division = int(degree / 3.0)
        if division >= 10: division = 9
        sign_idx = VargaEngine.get_sign_index(sign)
        is_odd = (sign_idx % 2 == 0)
        start_idx = sign_idx if is_odd else sign_idx + 8
        return VargaEngine.get_sign_from_index(start_idx + division)

    @staticmethod
    def calc_d12_dwadashamsha(sign: str, degree: float) -> str:
        div12 = int(degree / 2.5)
        if div12 >= 12: div12 = 11
        base_idx = VargaEngine.get_sign_index(sign)
        return VargaEngine.get_sign_from_index(base_idx + div12)

    @staticmethod
    def calc_d16_shodashamsha(sign: str, degree: float) -> str:
        div16 = int(degree / 1.875)
        if div16 >= 16: div16 = 15
        base_idx = VargaEngine.get_sign_index(sign)
        modality = base_idx % 3 # 0=Movable, 1=Fixed, 2=Dual
        start_16 = [0, 4, 8][modality]
        return VargaEngine.get_sign_from_index(start_16 + div16)

    @staticmethod
    def calc_d20_vimshamsha(sign: str, degree: float) -> str:
        div20 = int(degree / 1.5)
        if div20 >= 20: div20 = 19
        base_idx = VargaEngine.get_sign_index(sign)
        modality = base_idx % 3 # 0=Movable, 1=Fixed, 2=Dual
        start_20 = [0, 8, 4][modality]
        return VargaEngine.get_sign_from_index(start_20 + div20)

    @staticmethod
    def calc_d24_chaturvimshamsha(sign: str, degree: float) -> str:
        div24 = int(degree / 1.25)
        if div24 >= 24: div24 = 23
        base_idx = VargaEngine.get_sign_index(sign)
        is_odd = (base_idx % 2 == 0)
        start_24 = 4 if is_odd else 3
        return VargaEngine.get_sign_from_index(start_24 + div24)

    @staticmethod
    def calc_d27_saptavimshamsha(sign: str, degree: float) -> str:
        div27 = int(degree / (30.0 / 27.0))
        if div27 >= 27: div27 = 26
        sign_idx = VargaEngine.get_sign_index(sign)
        element_idx = sign_idx % 4 # 0=Fire, 1=Earth, 2=Air, 3=Water
        start_idx = [0, 3, 6, 9][element_idx] # Aries, Cancer, Libra, Capricorn
        return VargaEngine.get_sign_from_index(start_idx + div27)

    @staticmethod
    def calc_d30_trimshamsha(sign: str, degree: float) -> str:
        base_idx = VargaEngine.get_sign_index(sign)
        is_odd = (base_idx % 2 == 0)
        if is_odd:
            if degree < 5: return "Aries"
            elif degree < 10: return "Aquarius"
            elif degree < 18: return "Sagittarius"
            elif degree < 25: return "Gemini"
            else: return "Libra"
        else:
            if degree < 5: return "Taurus"
            elif degree < 12: return "Virgo"
            elif degree < 20: return "Pisces"
            elif degree < 25: return "Capricorn"
            else: return "Scorpio"

    @staticmethod
    def calc_d40_khavedamsha(sign: str, degree: float) -> str:
        div40 = int(degree / 0.75)
        if div40 >= 40: div40 = 39
        base_idx = VargaEngine.get_sign_index(sign)
        is_odd = (base_idx % 2 == 0)
        start_40 = 0 if is_odd else 6 # Aries or Libra
        return VargaEngine.get_sign_from_index(start_40 + div40)

    @staticmethod
    def calc_d45_akshavedamsha(sign: str, degree: float) -> str:
        div45 = int(degree / (30.0 / 45.0))
        if div45 >= 45: div45 = 44
        base_idx = VargaEngine.get_sign_index(sign)
        modality = base_idx % 3 # 0=Movable, 1=Fixed, 2=Dual
        start_45 = [0, 4, 8][modality]
        return VargaEngine.get_sign_from_index(start_45 + div45)

    @staticmethod
    def calc_d60_shashtiamsha(sign: str, degree: float) -> str:
        div60 = int(degree / 0.5)
        if div60 >= 60: div60 = 59
        base_idx = VargaEngine.get_sign_index(sign)
        return VargaEngine.get_sign_from_index(base_idx + div60)

    @staticmethod
    def calculate_all_vargas(planet_sign: str, planet_degree: float) -> Dict[str, str]:
        """
        Returns a dictionary mapping varga names to the calculated sign.
        Calculates all classical 16 Shodashavarga charts.
        """
        return {
            "D1": planet_sign,
            "D2": VargaEngine.calc_d2_hora(planet_sign, planet_degree),
            "D3": VargaEngine.calc_d3_drekkana(planet_sign, planet_degree),
            "D4": VargaEngine.calc_d4_chaturthamsha(planet_sign, planet_degree),
            "D7": VargaEngine.calc_d7_saptamsha(planet_sign, planet_degree),
            "D9": VargaEngine.calc_d9_navamsha(planet_sign, planet_degree),
            "D10": VargaEngine.calc_d10_dasamsha(planet_sign, planet_degree),
            "D12": VargaEngine.calc_d12_dwadashamsha(planet_sign, planet_degree),
            "D16": VargaEngine.calc_d16_shodashamsha(planet_sign, planet_degree),
            "D20": VargaEngine.calc_d20_vimshamsha(planet_sign, planet_degree),
            "D24": VargaEngine.calc_d24_chaturvimshamsha(planet_sign, planet_degree),
            "D27": VargaEngine.calc_d27_saptavimshamsha(planet_sign, planet_degree),
            "D30": VargaEngine.calc_d30_trimshamsha(planet_sign, planet_degree),
            "D40": VargaEngine.calc_d40_khavedamsha(planet_sign, planet_degree),
            "D45": VargaEngine.calc_d45_akshavedamsha(planet_sign, planet_degree),
            "D60": VargaEngine.calc_d60_shashtiamsha(planet_sign, planet_degree)
        }

    @staticmethod
    def assess_dignity(chart: Chart, varga_name: str, planet_names: list[str]) -> Dict[str, str]:
        """
        Evaluates the dignity of the specified planets in a specific Varga (e.g., D9, D10).
        Returns a dictionary mapping planet names to their dignity in that varga.
        """
        dignities = {}
        
        # Borrow the DIGNITY_RULES and FRIENDSHIP_TABLE from ConditionEngine to evaluate dignity in Varga
        # This is a simplified dignity check based purely on the sign in the Varga.
        DIGNITY_RULES = {
            "Sun": {"Exalted": "Aries", "Own": ["Leo"], "Debilitated": "Libra"},
            "Moon": {"Exalted": "Taurus", "Own": ["Cancer"], "Debilitated": "Scorpio"},
            "Mars": {"Exalted": "Capricorn", "Own": ["Aries", "Scorpio"], "Debilitated": "Cancer"},
            "Mercury": {"Exalted": "Virgo", "Own": ["Gemini", "Virgo"], "Debilitated": "Pisces"},
            "Jupiter": {"Exalted": "Cancer", "Own": ["Sagittarius", "Pisces"], "Debilitated": "Capricorn"},
            "Venus": {"Exalted": "Pisces", "Own": ["Taurus", "Libra"], "Debilitated": "Virgo"},
            "Saturn": {"Exalted": "Libra", "Own": ["Capricorn", "Aquarius"], "Debilitated": "Aries"},
            "Rahu": {"Exalted": "Taurus", "Own": [], "Debilitated": "Scorpio"},
            "Ketu": {"Exalted": "Scorpio", "Own": [], "Debilitated": "Taurus"}
        }
        
        FRIENDSHIP_TABLE = {
            "Sun": {"Friends": ["Moon", "Mars", "Jupiter"], "Enemies": ["Venus", "Saturn"]},
            "Moon": {"Friends": ["Sun", "Mercury"], "Enemies": []},
            "Mars": {"Friends": ["Sun", "Moon", "Jupiter"], "Enemies": ["Mercury"]},
            "Mercury": {"Friends": ["Sun", "Venus"], "Enemies": ["Moon"]},
            "Jupiter": {"Friends": ["Sun", "Moon", "Mars"], "Enemies": ["Mercury", "Venus"]},
            "Venus": {"Friends": ["Mercury", "Saturn"], "Enemies": ["Sun", "Moon"]},
            "Saturn": {"Friends": ["Mercury", "Venus"], "Enemies": ["Sun", "Moon", "Mars"]}
        }
        
        for p_name in planet_names:
            planet = chart.planets.get(p_name)
            if not planet or varga_name not in planet.vargas:
                dignities[p_name] = "UNAVAILABLE"
                continue
                
            varga_sign = planet.vargas[varga_name]
            
            if p_name not in DIGNITY_RULES:
                dignities[p_name] = "Neutral"
                continue
                
            rules = DIGNITY_RULES[p_name]
            
            if varga_sign == rules.get("Exalted"):
                dignities[p_name] = "Exalted"
            elif varga_sign == rules.get("Debilitated"):
                dignities[p_name] = "Debilitated"
            elif varga_sign in rules.get("Own", []):
                dignities[p_name] = "Own House"
            else:
                # Check friendship of the lord of the varga_sign
                lord = chart.SIGN_LORDS.get(varga_sign)
                if lord and p_name in FRIENDSHIP_TABLE:
                    if lord in FRIENDSHIP_TABLE[p_name]["Friends"]:
                        dignities[p_name] = "Friendly Sign"
                    elif lord in FRIENDSHIP_TABLE[p_name]["Enemies"]:
                        dignities[p_name] = "Enemy Sign"
                    else:
                        dignities[p_name] = "Neutral Sign"
                else:
                    dignities[p_name] = "Neutral Sign"
                    
        return dignities

    @staticmethod
    def get_varga_reliability(varga_id: str, is_birth_time_precise: bool = False) -> Dict[str, str]:
        """
        Returns metadata about the reliability of a Varga based on the provided birth time precision.
        """
        # Based on VARGA_REGISTRY.json definitions
        sensitivity_map = {
            "D1": "MODERATE", "D2": "LOW", "D3": "MODERATE", "D4": "MODERATE",
            "D7": "MODERATE", "D9": "HIGH", "D10": "HIGH", "D12": "HIGH",
            "D16": "HIGH", "D20": "HIGH", "D24": "EXTREME", "D27": "EXTREME",
            "D30": "EXTREME", "D40": "EXTREME", "D45": "EXTREME", "D60": "EXTREME"
        }
        
        sensitivity = sensitivity_map.get(varga_id.upper(), "UNKNOWN")
        
        if sensitivity == "EXTREME" and not is_birth_time_precise:
            return {
                "varga": varga_id,
                "birth_time_sensitivity": sensitivity,
                "reliability": "LOW",
                "warning": f"{varga_id}_RELIABILITY_WARNING: Extreme birth-time sensitivity. Cannot be trusted without rectification."
            }
        elif sensitivity == "HIGH" and not is_birth_time_precise:
            return {
                "varga": varga_id,
                "birth_time_sensitivity": sensitivity,
                "reliability": "MODERATE",
                "warning": f"{varga_id}_RELIABILITY_WARNING: High sensitivity. Use cautiously."
            }
            
        return {
            "varga": varga_id,
            "birth_time_sensitivity": sensitivity,
            "reliability": "HIGH",
            "warning": None
        }
