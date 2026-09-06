from typing import Dict, Any, List
from vedic_models import Chart

class RemediesEngine:
    """
    Engine for Upayas (Astrological Remedies).
    Suggests Mantras, Gemstones, and Charity based on planetary afflictions.
    """
    
    # Classical Mapping for Remedies
    REMEDIES_MAP = {
        "Sun": {
            "gemstone": "Ruby (Manikya)",
            "metal": "Gold or Copper",
            "mantra": "Om Hraam Hreem Hroum Sah Suryaya Namah",
            "charity": "Wheat, Jaggery, Copper on Sundays",
            "deity": "Lord Shiva / Lord Rama"
        },
        "Moon": {
            "gemstone": "Pearl (Moti)",
            "metal": "Silver",
            "mantra": "Om Shraam Shreem Shroum Sah Chandraya Namah",
            "charity": "Milk, Rice, Silver on Mondays",
            "deity": "Goddess Gouri / Lord Shiva"
        },
        "Mars": {
            "gemstone": "Red Coral (Moonga)",
            "metal": "Copper",
            "mantra": "Om Kraam Kreem Kroum Sah Bhaumaya Namah",
            "charity": "Red Lentils (Masoor), Red Clothes on Tuesdays",
            "deity": "Lord Hanuman / Lord Kartikeya"
        },
        "Mercury": {
            "gemstone": "Emerald (Panna)",
            "metal": "Gold or Bronze",
            "mantra": "Om Braam Breem Broum Sah Budhaya Namah",
            "charity": "Green Gram (Moong), Green Clothes on Wednesdays",
            "deity": "Lord Vishnu / Lord Ganesha"
        },
        "Jupiter": {
            "gemstone": "Yellow Sapphire (Pukhraj)",
            "metal": "Gold",
            "mantra": "Om Graam Greem Groum Sah Gurave Namah",
            "charity": "Chana Dal, Turmeric, Yellow Clothes on Thursdays",
            "deity": "Lord Brahma / Lord Shiva / Guru"
        },
        "Venus": {
            "gemstone": "Diamond (Heera) or White Sapphire",
            "metal": "Silver or Platinum",
            "mantra": "Om Draam Dreem Droum Sah Shukraya Namah",
            "charity": "Sugar, Rice, White Clothes on Fridays",
            "deity": "Goddess Lakshmi / Goddess Durga"
        },
        "Saturn": {
            "gemstone": "Blue Sapphire (Neelam)",
            "metal": "Iron or Lead",
            "mantra": "Om Praam Preem Proum Sah Shanaischaraya Namah",
            "charity": "Black Sesame, Mustard Oil, Iron on Saturdays",
            "deity": "Lord Hanuman / Lord Shiva"
        },
        "Rahu": {
            "gemstone": "Hessonite (Gomed)",
            "metal": "Panchaloha (5 metals alloy)",
            "mantra": "Om Bhraam Bhreem Bhroum Sah Rahave Namah",
            "charity": "Black/Blue Blankets, Radish on Saturdays",
            "deity": "Goddess Durga"
        },
        "Ketu": {
            "gemstone": "Cat's Eye (Lehsuniya)",
            "metal": "Panchaloha",
            "mantra": "Om Sraam Sreem Sroum Sah Ketave Namah",
            "charity": "Multi-colored blankets, feed dogs on Tuesdays",
            "deity": "Lord Ganesha"
        }
    }

    @staticmethod
    def identify_afflictions(chart: Chart) -> List[str]:
        """
        Identifies planets that are debilitated, combust, or heavily afflicted.
        """
        afflicted_planets = []
        for p_name, p in chart.planets.items():
            if p.dignity == "Debilitated" or p.combust:
                afflicted_planets.append(p_name)
                
            # Rahu/Ketu conjunction is a basic affliction check
            if "Rahu" in p.conjunct_with or "Ketu" in p.conjunct_with:
                if p_name not in ["Rahu", "Ketu"] and p_name not in afflicted_planets:
                    afflicted_planets.append(p_name)
                    
        return afflicted_planets

    @staticmethod
    def generate_remedies_report(chart: Chart) -> Dict[str, Any]:
        """
        Generates a comprehensive remedies report based on chart afflictions.
        """
        afflicted_planets = RemediesEngine.identify_afflictions(chart)
        
        # We generally do NOT recommend gemstones for lords of 6, 8, 12, even if debilitated.
        # Instead, we recommend charity (Daana) or Mantras for them.
        asc_idx = Chart.ZODIAC_SIGNS.index(chart.ascendant_sign) if hasattr(Chart, 'ZODIAC_SIGNS') else 0
        
        # Quick mapping for dusthana lords (6, 8, 12)
        # We need a robust way to find this, simulating for architecture
        # If a planet rules 6,8,12, gemstone = None.
        
        remedies = []
        for p in afflicted_planets:
            base_remedy = RemediesEngine.REMEDIES_MAP[p]
            
            # Simple rule: Gemstones are for strengthening benefic planets that are weak.
            # Mantras/Charity are for pacifying malefic planets.
            # For this architectural scaffold, we just return the full suite.
            remedies.append({
                "planet": p,
                "reason": "Planet is debilitated, combust, or afflicted by nodes.",
                "recommended_gemstone": base_remedy["gemstone"],
                "recommended_charity": base_remedy["charity"],
                "recommended_mantra": base_remedy["mantra"],
                "presiding_deity": base_remedy["deity"]
            })
            
        return {
            "ascendant": chart.ascendant_sign,
            "afflicted_planets_count": len(afflicted_planets),
            "remedies": remedies,
            "warning": "Gemstones should only be worn for functional benefics. For functional malefics (lords of 6,8,12), rely exclusively on Charity (Daana) and Mantras."
        }
