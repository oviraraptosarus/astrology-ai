from typing import Dict, Any

class CompatibilityEngine:
    """
    Engine for Ashtakoota Guna Milan (Compatibility Matching).
    Uses the Moon Nakshatra and Pada of the Bride and Groom.
    """
    
    # 27 Nakshatras
    NAKSHATRAS = [
        "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", 
        "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", 
        "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", 
        "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", 
        "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
    ]
    
    # Mapping for Varna (1 point): Work/Ego Compatibility
    # Based on Moon Sign (simplified to Nakshatra groups here for architectural scaffold)
    # Actually based on Rashi: Water (Brahmin), Fire (Kshatriya), Earth (Vaishya), Air (Shudra)
    
    # Mapping for Gana (6 points): Temperament
    # Deva (Divine), Manushya (Human), Rakshasa (Demon)
    GANA_MAPPING = {
        "Deva": ["Ashwini", "Mrigashira", "Punarvasu", "Pushya", "Hasta", "Swati", "Anuradha", "Shravana", "Revati"],
        "Manushya": ["Bharani", "Rohini", "Ardra", "Purva Phalguni", "Uttara Phalguni", "Purva Ashadha", "Uttara Ashadha", "Purva Bhadrapada", "Uttara Bhadrapada"],
        "Rakshasa": ["Krittika", "Ashlesha", "Magha", "Chitra", "Vishakha", "Jyeshtha", "Mula", "Dhanishta", "Shatabhisha"]
    }

    @staticmethod
    def get_gana(nakshatra: str) -> str:
        for gana, naks in CompatibilityEngine.GANA_MAPPING.items():
            if nakshatra in naks:
                return gana
        return "Deva" # Fallback

    @staticmethod
    def calculate_gana_koota(boy_nak: str, girl_nak: str) -> float:
        boy_gana = CompatibilityEngine.get_gana(boy_nak)
        girl_gana = CompatibilityEngine.get_gana(girl_nak)
        
        if boy_gana == girl_gana:
            return 6.0
        elif boy_gana == "Deva" and girl_gana == "Manushya":
            return 6.0
        elif boy_gana == "Manushya" and girl_gana == "Deva":
            return 5.0
        elif girl_gana == "Rakshasa" and boy_gana == "Deva":
            return 1.0
        elif boy_gana == "Rakshasa" and girl_gana == "Deva":
            return 0.0
        elif girl_gana == "Rakshasa" and boy_gana == "Manushya":
            return 0.0
        elif boy_gana == "Rakshasa" and girl_gana == "Manushya":
            return 0.0
        return 0.0

    @staticmethod
    def evaluate_compatibility(boy_nakshatra: str, boy_pada: int, girl_nakshatra: str, girl_pada: int) -> Dict[str, Any]:
        """
        Calculates the 36-point Ashtakoota match.
        Currently implements Gana Koota as the scaffolding example.
        """
        # Full implementation would calculate all 8 Kootas:
        # Varna (1), Vashya (2), Tara (3), Yoni (4), Graha Maitri (5), Gana (6), Bhakoot (7), Nadi (8)
        
        gana_score = CompatibilityEngine.calculate_gana_koota(boy_nakshatra, girl_nakshatra)
        
        # Simulating the rest for structural completeness
        total_score = gana_score + 20.0 # Dummy baseline
        
        status = "POOR"
        if total_score >= 18:
            status = "ACCEPTABLE"
        if total_score >= 25:
            status = "GOOD"
        if total_score >= 30:
            status = "EXCELLENT"
            
        return {
            "boy_nakshatra": boy_nakshatra,
            "girl_nakshatra": girl_nakshatra,
            "scores": {
                "varna": 1.0,
                "vashya": 2.0,
                "tara": 3.0,
                "yoni": 4.0,
                "graha_maitri": 5.0,
                "gana": gana_score,
                "bhakoot": 7.0,
                "nadi": 8.0,
            },
            "total_score": total_score,
            "out_of": 36.0,
            "status": status,
            "dosha_present": "Nadi Dosha" if total_score < 18 else "None" # Example
        }
